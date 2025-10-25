#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=======================================
YouTube Audio & Video Extractor (v1.12)
=======================================

Info:
  Author: Igor Brzezek (igor.brzezek@gmail.com)
  GitHub: https://github.com/IgorBrzezek/yt-audio-download
  Version: 1.13
  Date: 25.10.2025
  
LICENSE:
  MIT License 

DESCRIPTION:
  This script allows users to extract audio tracks from YouTube videos and save them as MP3 files,
  or download the full video as an MP4 file.
  It utilizes the powerful yt-dlp library for downloading and ffmpeg for audio conversion.
  The script is controlled via command-line options, allowing for batch processing,
  different quality settings, and customized output.

  BEST PRACTICE:
  Always enclose URLs in double quotes (" ") when running the script from the command line,
  especially if the URL contains special characters like '&'. This prevents the shell
  from misinterpreting the URL.
  Example: python yt_avextractor.py "https://youtube.com/watch?v=...&list=..."
  
  AND: always first upgrade yt-dlp with command:
  yt-dlp -U

REQUIREMENTS:
  1. Python 3
  2. yt-dlp
  3. ffmpeg & ffprobe
  4. colorama (Python library): pip install colorama
  
LIST FILE:  
    Sample file list exapmple for extraction (for example: list.txt)
    Any URL without quotation marks.

    URL1
    URL2
    URL3

SCRIPT OPTIONS:
  (See --help for a detailed, categorized list of all options)

EXAMPLES:
  # Recommended: Download audio using browser cookies to avoid errors
  python yt_avextractor.py --cookies chrome "YOUTUBE_URL"

  # Download full video (fastest way)
  python yt_avextractor.py -mp4fast "YOUTUBE_URL"

  # Run a batch job from a file silently and get an error code
  python yt_avextractor.py --list "links.txt" -b
  
  # Download a list with minimal, single-line progress updates
  python yt_avextractor.py --list "links.txt" --min
"""


import argparse
import subprocess
import sys
import os
import logging
import re
import time
import json
from pathlib import Path

# This global flag will be set by main() after parsing args
IS_BATCH_MODE = False
IS_MINIMAL_MODE = False

# Global state for minimal progress handler
minimal_progress_state = {
    'download_percent': '0%',
    'convert_percent': '0%',
    'status_message': 'Initializing...'
}

try:
    from colorama import init
except ImportError:
    # Handle colorama not being installed
    def init():
        pass # Do nothing if colorama is missing
    class Colors:
        HEADER, OKBLUE, OKCYAN, OKGREEN, WARNING, FAIL, ENDC, BOLD, UNDERLINE = '', '', '', '', '', '', '', '', ''
else:
    # --- ANSI Color Codes ---
    class Colors:
        HEADER, OKBLUE, OKCYAN, OKGREEN, WARNING, FAIL, ENDC, BOLD, UNDERLINE = '', '', '', '', '', '', '', '', ''
        if sys.stdout.isatty():
            HEADER = '\033[95m'; OKBLUE = '\033[94m'; OKCYAN = '\033[96m'; OKGREEN = '\033[92m'
            WARNING = '\033[93m'; FAIL = '\033[91m'; ENDC = '\033[0m'; BOLD = '\033[1m'; UNDERLINE = '\033[4m'


# === AUTHOR =================================================
AUTHOR = 'Igor Brzezek'
AUTHOR_EMAIL = 'igor.brzezek@gmail.com'
AUTHOR_GITHUB = 'github.com/igorbrzezek'
VERSION = 1.13
DATE = '25.10.2025'
# ============================================================

# --- yt-dlp additionals options -----------------------------
# These are passed directly to subprocess, which handles quoting
USER_AGENT_HEADER = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
EXTRACTOR_ARG_ANDROID = "youtube:player_client=android"
# ------------------------------------------------------------

def cprint(text, color="", use_color_flag=False, force_print=False, **kwargs):
    """
    Conditional print function.
    If IS_BATCH_MODE is True, this function does nothing.
    If IS_MINIMAL_MODE is True, this function does nothing UNLESS force_print is True.
    """
    if IS_BATCH_MODE and not force_print:
        return
    if IS_MINIMAL_MODE and not force_print:
        return
    
    # Fallback if colorama wasn't imported
    if 'Colors' not in globals():
        use_color_flag = False
        
    if use_color_flag and not IS_MINIMAL_MODE: # No colors in minimal mode
        print(f"{color}{text}{Colors.ENDC}", **kwargs)
    else:
        print(text, **kwargs)

def create_arg_parser():
    parser = argparse.ArgumentParser(description="A Python script to extract audio or video from YouTube using yt-dlp and ffmpeg.", epilog="Example usage:\n  python yt_avextractor.py --cookies chrome -r 2M \"<YOUTUBE_URL>\"", add_help=False, formatter_class=argparse.RawTextHelpFormatter)

    # --- Help Options ---
    help_group = parser.add_argument_group('Help')
    help_group.add_argument('-h', '--short-help', action='store_true', help="Show a short help message and exit.")
    help_group.add_argument('--help', action='store_true', help="Show this extensive help message and exit.")

    # --- Input/Output Options ---
    io_group = parser.add_argument_group('Input & Output')
    io_group.add_argument('urls', nargs='*', help="One or more YouTube video URLs. This is ignored if --list is used.")
    io_group.add_argument('-o', '--output', type=str, metavar='FILENAME', help="Specify the output filename. Only works for a single URL.")
    io_group.add_argument('--list', type=str, metavar='FILE', help="Path to a text file containing YouTube URLs (one per line).")
    io_group.add_argument('-dst', type=str, metavar='DIRECTORY', help="Destination directory for the output files. Defaults to the current directory.")
    io_group.add_argument('--overwrite', action='store_true', help="Force overwrite of existing files (passes --force-overwrite to yt-dlp).")

    # --- Format Options ---
    format_group = parser.add_argument_group('Format (Choose one)')
    format_exclusive_group = format_group.add_mutually_exclusive_group()
    format_exclusive_group.add_argument('-mp3fast', action='store_true', default=True, help="Extract audio to MP3 (high-quality VBR). (Default)")
    format_exclusive_group.add_argument('-mp3128', action='store_true', help="Convert audio to MP3 (128kbps CBR) for smaller file size.")
    format_exclusive_group.add_argument('-mp4fast', action='store_true', help="Download best video+audio, merge (remux) into an MP4 file.")

    # --- Anti-Blocking Options ---
    ab_group = parser.add_argument_group('Anti-Blocking & Network')
    ab_group.add_argument('--cookies', type=str, metavar='BROWSER', help="Use cookies from a browser (e.g., chrome, firefox) to bypass throttling/login.")
    ab_group.add_argument('-r', '--limit-rate', type=str, metavar='RATE', help="Limit download speed (e.g., 500K, 2M) to avoid being blocked.")
    ab_strategy_group = ab_group.add_mutually_exclusive_group()
    ab_strategy_group.add_argument('--add-header', action='store_true', help="Add a browser User-Agent header. Use if downloading fails.")
    ab_strategy_group.add_argument('--add-android', action='store_true', help="Use Android client extractor args. Use if downloading fails.")
    
    # --- Output Mode Options ---
    output_mode_group = parser.add_argument_group('Output Mode (Choose one)')
    output_exclusive_group = output_mode_group.add_mutually_exclusive_group()
    output_exclusive_group.add_argument('--pb', action='store_true', help="Show full progress bars (Default behavior).")
    output_exclusive_group.add_argument('--min', action='store_true', help="Minimal mode: Show only a single, updating line of progress per file.")
    output_exclusive_group.add_argument('-b', '--batch', action='store_true', help="Silent (batch) mode. No console output, implies --force-overwrite, returns error count.")
    
    # --- Utility Options ---
    util_group = parser.add_argument_group('Utilities')
    util_group.add_argument('--color', action='store_true', help="Display colorful status messages in the terminal (Disabled by --batch/--min).")
    util_group.add_argument('--log', nargs='?', const='yt-dlp.log', default=None, metavar='FILENAME', help="Enable logging to a file.")
    util_group.add_argument('--debug', action='store_true', help="Show all raw output from yt-dlp/ffmpeg (Disabled by --batch/--min).")
    
    return parser

def print_help(parser, detailed=False):
    # This function uses print(), not cprint(), so it's immune to batch/min mode.
    if not detailed:
        print(f"YouTube Audio/Video Extractor v{VERSION} ({DATE})")
        print(f"Author: {AUTHOR} ({AUTHOR_EMAIL})\n")
        print("Usage: python yt_avextractor.py [OPTIONS] [URLS...]\n")
        print("A tool to download YouTube audio or video.\n")
        print("Core Options:")
        print("  -o FILENAME           Specify custom output filename (for single URL).")
        print("  --list FILE           Provide a file with URLs to download.")
        print("  -mp4fast              Download best video+audio into an MP4 file.")
        print("  -dst DIRECTORY        Set output directory.")
        print("  --overwrite           Force overwrite existing files.\n")
        print("Anti-Blocking Options (Recommended):")
        print("  --cookies BROWSER     Use cookies from a browser (e.g., chrome, firefox).")
        print("  -r, --limit-rate RATE Limit download speed (e.g., 500K, 2M).")
        print("  --add-android         Use Android client args. Use if downloading fails.\n")
        print("Output Mode:")
        print("  --pb                  Show full progress bars (Default behavior).")
        print("  --min                 Minimal mode: one updating line of progress per file.")
        print("  -b, --batch           Silent (batch) mode. No console output, returns error count.\n")
        print("Other Options:")
        print("  --color, --log, --debug, -h, --help")
    else:
        parser.print_help()
    sys.exit(0)

def run_command(command, args, custom_handler=None):
    if args.debug and not args.batch and not args.min:
        cprint(f"Executing command: {' '.join(command)}", Colors.OKBLUE, args.color)
    if args.log:
        logging.info(f"Executing: {' '.join(command)}")
    try:
        stderr_pipe = subprocess.STDOUT
        
        # Special handling for ffmpeg to capture both progress (stdout) and errors (stderr)
        if 'ffmpeg' in command and IS_MINIMAL_MODE:
             stderr_pipe = subprocess.PIPE
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=stderr_pipe, universal_newlines=True, encoding='utf-8', errors='replace')
        
        # Read from stdout (and stderr if it's redirected)
        if custom_handler:
            custom_handler(process, args)
        else:
            # Default handler (only used in batch mode, just consumes output)
            for line in iter(process.stdout.readline, ''):
                if args.log: logging.info(line.strip())
        
        process.stdout.close()
        
        # Handle stderr separately if it wasn't redirected
        if stderr_pipe == subprocess.PIPE:
            for line in iter(process.stderr.readline, ''):
                if args.debug and not args.batch and not args.min: print(line, end='')
                if args.log: logging.info(line.strip())
            process.stderr.close()

        return process.wait() == 0
    
    except FileNotFoundError:
        cprint(f"Error: Command '{command[0]}' not found. Please ensure it is installed and in your system's PATH.", Colors.FAIL, args.color, force_print=True)
        if args.log: logging.critical(f"{command[0]} command not found.")
        sys.exit(1) # This is a fatal setup error
    except Exception as e:
        cprint(f"An unexpected error occurred: {e}", Colors.FAIL, args.color, force_print=True)
        if args.log: logging.critical(f"Unexpected error: {e}")
        sys.exit(1) # This is a fatal setup error

def get_file_size_mb(filepath):
    try:
        size_bytes = Path(filepath).stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0

def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    # Set the global flags *before* calling any cprint functions
    global IS_BATCH_MODE, IS_MINIMAL_MODE
    IS_BATCH_MODE = args.batch
    IS_MINIMAL_MODE = args.min

    # Only initialize colorama if not in batch or min mode
    if not IS_BATCH_MODE and not IS_MINIMAL_MODE:
        try:
            init()
        except NameError:
             pass # colorama not found

    if args.short_help: print_help(parser, detailed=False)
    if args.help: print_help(parser, detailed=True)

    error_count = 0
    total_files_processed = 0
    total_download_time = 0.0
    total_size_mb = 0.0

    if args.log:
        logging.basicConfig(filename=args.log, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        cprint(f"Logging enabled. Output will be saved to '{args.log}'", Colors.OKCYAN, args.color)
        logging.info("--- Script started ---")

    urls = []
    if args.list:
        try:
            with open(args.list, 'r') as f: urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            cprint(f"Error: The file '{args.list}' was not found.", Colors.FAIL, args.color, force_print=True)
            if args.log: logging.error(f"File not found: {args.list}")
            sys.exit(1) # Fatal error
    else:
        urls = args.urls
    
    youtube_params = ('list=', 'pp=', 't=', 'si=')
    for url_arg in urls:
        if any(url_arg.startswith(param) for param in youtube_params):
            cprint(f"ERROR: Detected an argument that looks like part of a URL ('{url_arg}').", Colors.FAIL, use_color_flag=True, force_print=True)
            cprint("You probably forgot to enclose the entire URL in quotes.", Colors.WARNING, use_color_flag=True, force_print=True)
            cprint("Correct usage example:", Colors.OKCYAN, use_color_flag=True, force_print=True)
            cprint('  python yt_avextractor.py "https://www.youtube.com/watch?v=...&list=..."', use_color_flag=True, force_print=True)
            sys.exit(1) # Fatal error

    if not urls:
        cprint("Error: No URLs provided. Use arguments or --list option.", Colors.FAIL, args.color, force_print=True)
        if args.log: logging.error("No URLs provided.")
        sys.exit(1) # Fatal error
        
    if args.output and len(urls) > 1:
        cprint("Error: The -o/--output option can only be used when processing a single URL.", Colors.FAIL, args.color, force_print=True)
        if args.log: logging.error("Attempted to use -o/--output with multiple URLs.")
        sys.exit(1) # Fatal error

    destination_dir = Path(args.dst) if args.dst else Path.cwd()
    destination_dir.mkdir(parents=True, exist_ok=True)

    cprint(f"Found {len(urls)} file(s) to process.", Colors.HEADER, args.color)
    if args.log: logging.info(f"Starting processing of {len(urls)} URLs.")

    overall_start_time = time.monotonic()
    total_url_count = len(urls)

    # Set the correct handler based on flags
    download_handler_func = download_progress_handler
    convert_handler_func = conversion_progress_handler
    
    if args.batch:
        download_handler_func = None # No handler, run_command will just consume
        convert_handler_func = None
    elif args.min:
        download_handler_func = minimal_download_progress_handler
        convert_handler_func = minimal_conversion_progress_handler
    # (If no flag or --pb, default handlers remain)


    for i, url in enumerate(urls, 1):
        cprint(f"\n--- Processing file {i}/{total_url_count}: {url} ---", Colors.BOLD, args.color)
        if args.log: logging.info(f"--- Processing {i}/{total_url_count}: {url} ---")
        
        minimal_progress_state.update({'download_percent': '0%', 'convert_percent': '0%', 'status_message': 'Getting title...'})
        if IS_MINIMAL_MODE:
            print(f"[{i}/{total_url_count}] Getting title...                  ", end='\r')

        try:
            get_title_cmd = ['yt-dlp', '--no-warnings', '--encoding', 'utf-8', '--get-filename', '-o', '%(title)s', url]
            if args.batch or args.min: get_title_cmd.append('--quiet')
            if args.cookies: get_title_cmd.extend(['--cookies-from-browser', args.cookies])
            if args.add_header: get_title_cmd.extend(['--add-header', USER_AGENT_HEADER])
            if args.add_android: get_title_cmd.extend(['--extractor-args', EXTRACTOR_ARG_ANDROID])
            
            video_title = subprocess.check_output(get_title_cmd, universal_newlines=True, encoding='utf-8').strip()
        
        except Exception as e:
            cprint(f"Could not get video metadata for URL {url}. Error: {e}", Colors.FAIL, args.color, force_print=True)
            if IS_MINIMAL_MODE:
                print(f"[{i}/{total_url_count}] FAILED: Could not get title. Skipping.    ")
            if args.log: logging.error(f"Failed to get metadata for {url}. Error: {e}")
            error_count += 1
            continue

        if args.mp4fast:
            output_filename = f"{video_title}.mp4"
            if args.output:
                output_filename = args.output if args.output.lower().endswith('.mp4') else f"{args.output}.mp4"
        else:
            output_filename = f"{video_title}.mp3"
            if args.output:
                output_filename = args.output if args.output.lower().endswith('.mp3') else f"{args.output}.mp3"
        
        final_filepath = destination_dir / output_filename

        if final_filepath.exists() and not args.overwrite and not args.batch and not args.min:
            cprint(f"File '{final_filepath.name}' already exists.", Colors.WARNING, use_color_flag=args.color)
            choice = input("Overwrite? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                cprint("Skipping file.", Colors.OKCYAN, use_color_flag=args.color)
                if args.log: logging.info(f"Skipped file (already exists): {final_filepath}")
                continue
        elif final_filepath.exists() and IS_MINIMAL_MODE and not args.overwrite:
             print(f"[{i}/{total_url_count}] SKIPPED: File exists '{final_filepath.name}'. (Use --overwrite)    ")
             continue


        download_start_time = time.monotonic()
        download_success = False
        conversion_success = True
        download_duration = 0.0
        conversion_duration = 0.0
        
        current_dl_handler = None
        if download_handler_func:
            current_dl_handler = lambda p, a: download_handler_func(p, a, i, total_url_count)
        
        if args.mp4fast:
            cprint(f"Step 1: Downloading and merging video to MP4 -> ({final_filepath.name})...", Colors.OKCYAN, args.color)
            minimal_progress_state['status_message'] = 'Downloading MP4...'

            download_command = ['yt-dlp', '--no-warnings']
            if args.batch: download_command.append('--quiet')
            if args.min or args.pb or (not args.min and not args.batch): 
                download_command.append('--progress') 
            
            if args.overwrite or args.batch:
                download_command.append('--force-overwrite')

            download_command.extend(['-f', 'bestvideo+bestaudio/best', '--merge-output-format', 'mp4'])
            download_command.extend(['--no-mtime', '-o', str(final_filepath)])

            if args.color: download_command.extend(['--color', 'always'])
            if args.debug: download_command.append('--verbose')
            if args.cookies: download_command.extend(['--cookies-from-browser', args.cookies])
            if args.limit_rate: download_command.extend(['--limit-rate', args.limit_rate]) 
            if args.add_header: download_command.extend(['--add-header', USER_AGENT_HEADER])
            if args.add_android: download_command.extend(['--extractor-args', EXTRACTOR_ARG_ANDROID])
            
            download_command.append(url)
            
            download_success = run_command(download_command, args, current_dl_handler)
            download_duration = time.monotonic() - download_start_time
            
            if download_success:
                file_size_num = get_file_size_mb(final_filepath)
                file_size_str = f"{file_size_num:.2f} MB"
                cprint(f"\nSuccessfully created: {final_filepath}", Colors.OKGREEN, args.color)
                cprint(f"Total time:      {download_duration:.2f}s", Colors.OKGREEN + Colors.BOLD, args.color)
                if IS_MINIMAL_MODE:
                    print(f"[{i}/{total_url_count}] Done. Time: {download_duration:.2f}s, Size: {file_size_str} -> {final_filepath.name}    ")
                if args.log: logging.info(f"Success (MP4): {final_filepath} (Time: {download_duration:.2f}s, Size: {file_size_str})")
                total_files_processed += 1
                total_download_time += download_duration
                total_size_mb += file_size_num
            else:
                cprint(f"\nDownload failed for {url}.", Colors.FAIL, args.color, force_print=True)
                if IS_MINIMAL_MODE:
                    print(f"[{i}/{total_url_count}] FAILED: Download/Merge failed. Skipping.    ")
                if args.log: logging.error(f"Download/Merge failed for {url}")
                error_count += 1
                if final_filepath.exists():
                    try: os.remove(final_filepath)
                    except OSError as e: cprint(f"Could not remove partial file: {e}", Colors.WARNING, args.color)
            
            continue

        else:
            # --- MP3 Download and Convert Logic ---
            temp_filename_template = f"temp_{os.getpid()}_{i}.%(ext)s"
            temp_filepath_template = destination_dir / temp_filename_template
            
            download_command = ['yt-dlp', '--no-warnings', '-f', 'bestaudio', '--no-mtime', '-o', str(temp_filepath_template)]
            if args.batch: download_command.append('--quiet')
            if args.min or args.pb or (not args.min and not args.batch): 
                download_command.append('--progress')

            if args.overwrite or args.batch:
                download_command.append('--force-overwrite')

            if args.color: download_command.extend(['--color', 'always'])
            if args.debug: download_command.append('--verbose')
            if args.cookies: download_command.extend(['--cookies-from-browser', args.cookies])
            if args.limit_rate: download_command.extend(['--limit-rate', args.limit_rate])
            if args.add_header: download_command.extend(['--add-header', USER_AGENT_HEADER])
            if args.add_android: download_command.extend(['--extractor-args', EXTRACTOR_ARG_ANDROID])
            download_command.append(url)

            cprint("Step 1: Downloading audio track...", Colors.OKCYAN, args.color)
            minimal_progress_state['status_message'] = 'Downloading Audio...'
            
            temp_filepath = None
            try:
                get_filename_cmd = ['yt-dlp', '--no-warnings', '--encoding', 'utf-8', '--get-filename', '-f', 'bestaudio', '-o', str(temp_filepath_template), url]
                if args.batch or args.min: get_filename_cmd.append('--quiet')
                if args.cookies: get_filename_cmd.extend(['--cookies-from-browser', args.cookies])
                if args.add_header: get_filename_cmd.extend(['--add-header', USER_AGENT_HEADER])
                if args.add_android: get_filename_cmd.extend(['--extractor-args', EXTRACTOR_ARG_ANDROID])
                
                temp_filepath_str = subprocess.check_output(get_filename_cmd, universal_newlines=True, encoding='utf-8').strip()
                temp_filepath = Path(temp_filepath_str)
            except Exception as e:
                cprint(f"Could not determine temporary filename. Error: {e}", Colors.FAIL, args.color, force_print=True)
                if IS_MINIMAL_MODE:
                    print(f"[{i}/{total_url_count}] FAILED: Could not get temp filename. Skipping.    ")
                if args.log: logging.error(f"Failed to get temp filename for {url}. Error: {e}")
                error_count += 1
                continue
                
            download_success = run_command(download_command, args, current_dl_handler)
            download_duration = time.monotonic() - download_start_time
            
            if not download_success:
                cprint(f"Download failed for {url}.", Colors.FAIL, args.color, force_print=True)
                if IS_MINIMAL_MODE:
                    print(f"[{i}/{total_url_count}] FAILED: Audio download failed. Skipping.    ")
                if args.log: logging.error(f"Audio download failed for {url}")
                error_count += 1
                if temp_filepath and temp_filepath.exists(): os.remove(temp_filepath)
                continue

            try:
                cprint(f"\nStep 2: Converting to MP3 -> ({final_filepath.name})...", Colors.OKCYAN, args.color)
                minimal_progress_state['status_message'] = 'Converting to MP3...'
                
                conversion_start_time = time.monotonic()
                duration = get_duration(temp_filepath, args)
                
                convert_command = ['ffmpeg', '-i', str(temp_filepath), '-vn']
                if args.batch: convert_command.extend(['-loglevel', 'quiet'])
                if args.min: convert_command.extend(['-loglevel', 'error'])
                
                if args.mp3128:
                    convert_command.extend(['-b:a', '128k'])
                else: 
                    convert_command.extend(['-q:a', '2'])
                
                convert_command.extend(['-progress', 'pipe:1', '-y', str(final_filepath)])

                current_conv_handler = None
                if convert_handler_func:
                    current_conv_handler = lambda p, a: convert_handler_func(p, a, duration, i, total_url_count)

                conversion_success = run_command(convert_command, args, current_conv_handler)
                conversion_duration = time.monotonic() - conversion_start_time

                if conversion_success:
                    file_size_num = get_file_size_mb(final_filepath)
                    file_size_str = f"{file_size_num:.2f} MB"
                    cprint(f"\nSuccessfully created: {final_filepath}", Colors.OKGREEN, args.color)
                    cprint(f"Download time:   {download_duration:.2f}s", Colors.OKGREEN, args.color)
                    cprint(f"Conversion time: {conversion_duration:.2f}s", Colors.OKGREEN, args.color)
                    cprint(f"Total time:      {(download_duration + conversion_duration):.2f}s", Colors.OKGREEN + Colors.BOLD, args.color)
                    if IS_MINIMAL_MODE:
                        print(f"[{i}/{total_url_count}] Done. Download: {download_duration:.1f}s, Convert: {conversion_duration:.1f}s, Size: {file_size_str} -> {final_filepath.name}    ")
                    if args.log: logging.info(f"Success (MP3): {final_filepath} (D: {download_duration:.2f}s, C: {conversion_duration:.2f}s, Size: {file_size_str})")
                    total_files_processed += 1
                    total_download_time += download_duration + conversion_duration
                    total_size_mb += file_size_num
                else:
                    cprint(f"\nConversion failed for {temp_filepath}", Colors.FAIL, args.color, force_print=True)
                    if IS_MINIMAL_MODE:
                         print(f"[{i}/{total_url_count}] FAILED: Conversion failed. Skipping.    ")
                    if args.log: logging.error(f"ffmpeg conversion failed for {url}")
                    error_count += 1
            finally:
                if temp_filepath and temp_filepath.exists(): os.remove(temp_filepath)

    overall_duration = time.monotonic() - overall_start_time
    
    if len(urls) > 1:
        cprint(f"\nAll tasks completed. Total script time: {overall_duration:.2f}s", Colors.OKGREEN + Colors.BOLD, args.color)
    else:
        cprint("\nAll tasks completed.", Colors.OKGREEN + Colors.BOLD, args.color)

    if not IS_BATCH_MODE and total_url_count > 0:
        print(f"\n--- SUMMARY ---")
        print(f"Processed: {total_files_processed} files | Total Time: {total_download_time:.2f}s | Total Size: {total_size_mb:.2f} MB | Errors: {error_count}")

    if args.log:
        logging.info(f"--- SUMMARY: Processed: {total_files_processed}, Time: {total_download_time:.2f}s, Size: {total_size_mb:.2f} MB, Errors: {error_count} ---")
        logging.info(f"--- Script finished with {error_count} errors. Total wall time: {overall_duration:.2f}s ---")

    sys.exit(error_count)


def download_progress_handler(process, args, *extra):
    """ 
    Handler for normal and --pb mode. 
    Shows full yt-dlp output, including percentages.
    """
    # Show ERROR/FATAL (case-insensitive), and essential ops
    keywords_to_show = ('[ExtractAudio]', '[Merger]', 'ERROR', 'FATAL')
    was_last_line_progress = False
    
    for line in iter(process.stdout.readline, ''):
        stripped_line = line.strip()
        if not stripped_line: continue
        if args.log: logging.info(stripped_line)
        if args.debug:
            print(line, end='')
            continue
        
        if stripped_line.startswith('WARNING:'):
            continue
            
        is_progress_line = '[download]' in stripped_line and '%' in stripped_line
        
        # Case-insensitive check for error keywords
        line_upper = stripped_line.upper()
        is_essential_line = any(keyword in line_upper for keyword in keywords_to_show)
        
        if is_progress_line:
            cprint(f"\r{stripped_line}  ", use_color_flag=args.color, end="")
            sys.stdout.flush()
            was_last_line_progress = True
        elif is_essential_line:
            if was_last_line_progress: print() 
            cprint(stripped_line, use_color_flag=args.color)
            sys.stdout.flush()
            was_last_line_progress = False
        elif 'Destination:' in stripped_line or 'Merging formats into' in stripped_line:
            if was_last_line_progress: print()
            cprint(stripped_line, use_color_flag=args.color)
            sys.stdout.flush()
            was_last_line_progress = False
        # Other lines (like [info], [youtube]) are intentionally ignored

def minimal_download_progress_handler(process, args, i, total_url_count):
    """ Handler for --min mode. Parses yt-dlp output for progress. """
    global minimal_progress_state
    i_str = f"{i}/{total_url_count}"
    
    download_regex = re.compile(r'\[download\]\s+([\d\.]+)%')
    merge_regex = re.compile(r'\[Merger\] Merging formats into ".*"')
    
    for line in iter(process.stdout.readline, ''):
        stripped_line = line.strip()
        if not stripped_line: continue
        if args.log: logging.info(stripped_line)
        if args.debug: print(line, end='')
            
        if stripped_line.startswith('WARNING:'):
            continue
        
        dl_match = download_regex.search(stripped_line)
        if dl_match:
            minimal_progress_state['download_percent'] = f"{float(dl_match.group(1)):.0f}%"
            status = minimal_progress_state['status_message']
            dl_pct = minimal_progress_state['download_percent']
            print(f"[{i_str}] {status} {dl_pct}      ", end='\r')
            continue
            
        merge_match = merge_regex.search(stripped_line)
        if merge_match:
            minimal_progress_state['status_message'] = 'Merging MP4...'
            print(f"[{i_str}] Merging MP4... 100%                ", end='\r')
            continue

def get_duration(filepath, args):
    """
    Use JSON output for ffprobe for robust duration fetching.
    """
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(filepath)]
    try:
        duration_str = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.DEVNULL)
        data = json.loads(duration_str)
        if 'format' in data and 'duration' in data['format']:
            return float(data['format']['duration'])
        else:
            cprint(f"ffprobe gave unexpected JSON: {duration_str}", Colors.WARNING, use_color_flag=args.color, force_print=True)
            if args.log: logging.warning(f"ffprobe unexpected JSON for {filepath}: {duration_str}")
            return 0
    except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        cprint(f"Could not get audio duration using ffprobe. Error: {e}", Colors.WARNING, use_color_flag=args.color, force_print=True)
        if args.log: logging.warning(f"ffprobe failed to get duration for {filepath}. Error: {e}")
        return 0

def conversion_progress_handler(process, args, total_duration, *extra):
    """ Handler for normal MP3 conversion progress. """
    if total_duration == 0:
        cprint("Cannot show progress because audio duration is unknown.", use_color_flag=args.color)
        return
    for line in iter(process.stdout.readline, ''):
        if args.debug: print(line, end='')
        if args.log: logging.info(line.strip())
        if "out_time_us=" in line:
            us_str = re.search(r'out_time_us=(\d+)', line)
            if us_str:
                microseconds = int(us_str.group(1))
                percent = (microseconds / (total_duration * 1_000_000)) * 100 if total_duration > 0 else 100
                
                # --- FIX: Split color output ---
                color_percent = Colors.OKGREEN if args.color else ""
                color_text = Colors.OKCYAN if args.color else ""
                color_end = Colors.ENDC if args.color else ""
                
                progress_text = f"\r{color_text}Converting to mp3: {color_percent}{percent:.1f}%{color_end} "
                print(progress_text, end="")
                sys.stdout.flush()

def minimal_conversion_progress_handler(process, args, total_duration, i, total_url_count):
    """ Handler for --min mode MP3 conversion progress. """
    global minimal_progress_state
    i_str = f"{i}/{total_url_count}"

    if total_duration == 0:
        minimal_progress_state['convert_percent'] = '??%'
        print(f"[{i_str}] Converting (??%)...     ", end='\r')
    
    for line in iter(process.stdout.readline, ''):
        if args.log: logging.info(line.strip())
        if args.debug: print(line, end='')
            
        if "out_time_us=" in line:
            us_str = re.search(r'out_time_us=(\d+)', line)
            if us_str and total_duration > 0:
                microseconds = int(us_str.group(1))
                percent = (microseconds / (total_duration * 1_000_000)) * 100
                minimal_progress_state['convert_percent'] = f"{percent:.0f}%"
                
                status = minimal_progress_state['status_message']
                dl_pct = minimal_progress_state['download_percent']
                cv_pct = minimal_progress_state['convert_percent']
                print(f"[{i_str}] {status} {cv_pct} (DL: {dl_pct})      ", end='\r')

if __name__ == '__main__':
    main()