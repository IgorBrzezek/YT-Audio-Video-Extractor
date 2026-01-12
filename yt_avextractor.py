#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=======================================
YouTube Audio & Video Extractor (v1.18)
=======================================

Info:
  Author: Igor Brzezek (igor.brzezek@gmail.com)
  GitHub: https://github.com/IgorBrzezek/yt-audio-download
  Version: 1.18
  Date: 12.01.2026
  
LICENSE:
  MIT License

CHANGELOG:
v1.18: Added --showname X and fixed --skip logic to check for existing final files.
v1.18p6: Added ytextractor.err reporting for failed/incomplete downloads and enhanced summary.
v1.18p5: Fully restored original categorized --help layout and all missing options.
v1.18p4: Fixed -h to show one-line options summary; restored categorized --help.
"""

import argparse
import subprocess
import sys
import os
import logging
import re
import time
import json
import signal
from pathlib import Path

# Ensure UTF-8 output for special characters in titles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Global state
IS_BATCH_MODE = False
IS_MINIMAL_MODE = False
LAST_DL_LINE = ""
LAST_FULL_LINE = ""
CURRENT_SUBPROCESS = None
current_files_to_cleanup = []
failed_urls = []

try:
    from colorama import init, Fore, Style
except ImportError:
    def init(): pass
    class Colors:
        HEADER, OKBLUE, OKCYAN, OKGREEN, WARNING, FAIL, ENDC, BOLD, UNDERLINE = '', '', '', '', '', '', '', '', ''
        C_DIM, C_YELLOW, C_MAGENTA, C_WHITE = '', '', '', ''
else:
    class Colors:
        HEADER = Fore.MAGENTA; OKBLUE = Fore.BLUE; OKCYAN = Fore.CYAN; OKGREEN = Fore.GREEN
        WARNING = Fore.YELLOW; FAIL = Fore.RED; ENDC = Style.RESET_ALL; BOLD = Style.BRIGHT; UNDERLINE = '\033[4m'
        C_DIM = '\033[2m'; C_YELLOW = Fore.YELLOW; C_MAGENTA = Fore.MAGENTA; C_WHITE = Fore.WHITE

AUTHOR = 'Igor Brzezek'; VERSION = "1.18"; DATE = '12.01.2026'
USER_AGENT_HEADER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, browser: chrome) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

def format_bytes(size_bytes_str):
    try:
        size = float(size_bytes_str)
        if size < 1024: return f"{size:.0f}B"
        elif size < 1024**2: return f"{size/1024:.1f}KiB"
        else: return f"{size/(1024**2):.1f}MiB"
    except: return "0B"

def format_ff_time(time_str):
    if '.' in time_str: return time_str.split('.')[0]
    return time_str

def cprint(text, color="", use_color_flag=False, force_print=False, **kwargs):
    if IS_BATCH_MODE and not force_print: return
    if IS_MINIMAL_MODE and not force_print: return
    if use_color_flag: print(f"{color}{text}{Colors.ENDC}", **kwargs)
    else: print(text, **kwargs)

def color_dl_line(line, use_color=False):
    match = re.search(r'(\d+\.?\d*%) of\s+([\d\.]+\w+)(?: in ([\d:]+))? at\s+([\d\.]+\w+/s)', line)
    if match and use_color:
        p, size, duration, speed = match.groups()
        dur_part = f" in {Colors.OKBLUE}{duration}{Colors.ENDC}" if duration else ""
        return f"Downloading {Colors.BOLD}{p}{Colors.ENDC} of {Colors.C_YELLOW}{size}{Colors.ENDC}{dur_part} at {Colors.C_MAGENTA}{speed}{Colors.ENDC}"
    return line.replace('[download]', 'Downloading')

def terminate_process_tree():
    global CURRENT_SUBPROCESS
    if CURRENT_SUBPROCESS:
        try:
            if sys.platform != "win32":
                os.killpg(os.getpgid(CURRENT_SUBPROCESS.pid), signal.SIGTERM)
            else:
                CURRENT_SUBPROCESS.terminate()
        except: pass
    cleanup_incomplete_files()

def signal_handler(sig, frame):
    sys.stdout.write(f"\n{Colors.FAIL}{Colors.BOLD}ABORTED! Instant exit...{Colors.ENDC}\n")
    sys.stdout.flush()
    terminate_process_tree()
    os._exit(1)

signal.signal(signal.SIGINT, signal_handler)

def create_arg_parser():
    parser = argparse.ArgumentParser(description="YouTube Audio/Video Extractor", add_help=False, formatter_class=argparse.RawTextHelpFormatter)
    
    help_group = parser.add_argument_group('Help')
    help_group.add_argument('-h', '--short-help', action='store_true', help="Show a short help message.")
    help_group.add_argument('--help', action='store_true', help="Show extensive help.")
    
    io_group = parser.add_argument_group('Input & Output')
    io_group.add_argument('urls', nargs='*', help="YouTube URLs.")
    io_group.add_argument('-o', '--output', type=str, help="Output filename.")
    io_group.add_argument('--list', type=str, help="File with URLs.")
    io_group.add_argument('--skip', action='store_true', help="Skip existing files.")
    io_group.add_argument('-dst', type=str, help="Destination dir.")
    io_group.add_argument('--overwrite', action='store_true', help="Overwrite files.")
    
    format_group = parser.add_argument_group('Format')
    f_group = format_group.add_mutually_exclusive_group()
    f_group.add_argument('-mp3high', action='store_true', default=True, help="High quality MP3 (192kbps).")
    f_group.add_argument('-mp3fast', action='store_true', help="Download audio fast (128kbps MP3).")
    f_group.add_argument('-mp3128', action='store_true', help="Equivalent to -mp3fast.")
    f_group.add_argument('-mp4fast', action='store_true', help="Download full video (fastest way).")
    
    ab_group = parser.add_argument_group('Anti-Blocking')
    ab_group.add_argument('--cookies', type=str, help="Browser cookies (e.g. chrome).")
    ab_group.add_argument('-r', '--limit-rate', type=str, help="Limit rate (e.g. 50K or 4.2M).")
    ab_group.add_argument('--add-header', action='store_true', help="Add UA header.")
    ab_group.add_argument('--add-android', action='store_true', help="Use android client spoofing.")
    
    out_group = parser.add_argument_group('Output Mode')
    o_group = out_group.add_mutually_exclusive_group()
    o_group.add_argument('--pb', action='store_true', help="Show progress bar (if supported).")
    o_group.add_argument('--min', action='store_true', help="Download with minimal, single-line progress updates.")
    o_group.add_argument('-b', '--batch', action='store_true', help="Run a batch job from a file silently.")
    out_group.add_argument('--showname', type=int, metavar='X', help="Show X chars of title in minimal mode.")
    
    util_group = parser.add_argument_group('Utilities')
    util_group.add_argument('--color', action='store_true', help="Enable colored output.")
    util_group.add_argument('--log', nargs='?', const='yt-dlp.log', help="Log yt-dlp output to file.")
    util_group.add_argument('--debug', action='store_true', help="Show debug information.")
    util_group.add_argument('--verbose', action='store_true', help="Verbose output.")
    
    return parser

def print_help(parser, detailed=False):
    if not detailed:
        print(f"YouTube Audio/Video Extractor v{VERSION} ({DATE})")
        all_options = []
        for group in parser._action_groups:
            for action in group._group_actions:
                if action.option_strings:
                    all_options.append(action.option_strings[0])
        print(f"Options: {' '.join(all_options)}")
    else:
        print(f"YouTube Audio & Video Extractor (v{VERSION})")
        print(f"Author: {AUTHOR} | Date: {DATE}\n")
        for group in parser._action_groups:
            print(f"{group.title}:")
            for action in group._group_actions:
                opts = ", ".join(action.option_strings)
                print(f"  {opts.ljust(25)} {action.help if action.help else ''}")
            print("")
        print("EXAMPLES:")
        print("  python yt_avextractor.py  -mp3fast --add-header   --log info.log --list lista.txt  --min --color --skip  --showname 20")
        print("  python yt_avextractor.py -mp3fast --add-header --log info.log  --min --color --overwrite  --showname 20 \"Here URL of YT movie do download\"")
        print("  python yt_avextractor.py --cookies chrome \"URL\"")
        print("  python yt_avextractor.py --list \"links.txt\" --min --showname 15")
    sys.exit(0)

def cleanup_incomplete_files():
    for filepath in current_files_to_cleanup:
        if filepath and filepath.exists():
            try: os.remove(filepath)
            except: pass

def run_command(command, args, custom_handler=None):
    global CURRENT_SUBPROCESS
    try:
        if args.debug:
            debug_msg = f"[DEBUG] Command: {' '.join(command)}"
            if args.log: logging.debug(debug_msg)
            sys.stdout.write(f"\r\033[K{Colors.C_DIM}{debug_msg}{Colors.ENDC}\n")

        kwargs = {'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT, 'universal_newlines': True, 'encoding': 'utf-8', 'errors': 'replace', 'bufsize': 1}
        if sys.platform != "win32": kwargs['start_new_session'] = True
        
        CURRENT_SUBPROCESS = subprocess.Popen(command, **kwargs)
        
        for line in iter(CURRENT_SUBPROCESS.stdout.readline, ''):
            clean_line = line.strip()
            if not clean_line: continue
            
            is_progress = ("[download]" in clean_line and "%" in clean_line) or \
                          ("=" in clean_line and any(k in clean_line for k in ["out_time", "progress", "speed", "total_size"]))
            
            if args.log and not is_progress:
                logging.info(clean_line)
            
            if (args.verbose or args.debug) and not is_progress:
                sys.stdout.write(f"\r\033[K{Colors.C_DIM}[DEBUG] {clean_line}{Colors.ENDC}\n")
                sys.stdout.flush()
            
            if custom_handler:
                custom_handler(line, args)
                
        ret = CURRENT_SUBPROCESS.wait()
        CURRENT_SUBPROCESS = None
        return ret == 0
    except Exception as e:
        cprint(f"Error: {e}", Colors.FAIL, args.color, force_print=True); sys.exit(1)

def show_minimal_status(i, total, status_text, color_flag, color_code=None, title="", title_limit=None):
    total_digits = len(str(total))
    file_part = f"File: {str(i).rjust(total_digits)}/{total}"
    
    if title_limit and title:
        short_title = title[:title_limit]
        file_part += f" ({short_title})"

    if color_flag:
        prefix = f"{Colors.BOLD}{Colors.OKBLUE}{file_part}{Colors.ENDC} | "
        content = f"{color_code}{status_text}{Colors.ENDC}" if color_code else status_text
    else:
        prefix = f"{file_part} | "
        content = status_text
    sys.stdout.write(f"\r\033[K{prefix}{content}")
    sys.stdout.flush()
    return prefix

def main():
    parser = create_arg_parser(); args = parser.parse_args()
    global IS_BATCH_MODE, IS_MINIMAL_MODE; IS_BATCH_MODE = args.batch; IS_MINIMAL_MODE = args.min
    if not IS_BATCH_MODE:
        try: init()
        except: pass
    
    if args.log:
        logging.basicConfig(filename=args.log, level=logging.DEBUG if args.debug else logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s', force=True)

    if args.short_help: print_help(parser, detailed=False)
    if args.help: print_help(parser, detailed=True)
    
    urls = []
    if args.list:
        try:
            with open(args.list, 'r', encoding='utf-8') as f: urls = [l.strip() for l in f if l.strip()]
        except: cprint("File not found.", Colors.FAIL, args.color, force_print=True); sys.exit(1)
    else: urls = args.urls
    if not urls: cprint("No URLs provided.", Colors.FAIL, args.color, force_print=True); sys.exit(1)
    
    destination_dir = Path(args.dst) if args.dst else Path.cwd()
    destination_dir.mkdir(parents=True, exist_ok=True)
    cprint(f"Found {len(urls)} file(s).", Colors.HEADER, args.color)
    
    error_count = 0
    for i, url in enumerate(urls, 1):
        global LAST_DL_LINE, LAST_FULL_LINE; LAST_DL_LINE = ""; LAST_FULL_LINE = ""
        
        if args.min:
            show_minimal_status(i, len(urls), "Connecting...", args.color, Colors.HEADER, title_limit=args.showname)
        else:
            cprint(f"\n--- Processing {i}/{len(urls)}: {url} ---", Colors.BOLD, args.color)
            cprint("Connecting to YouTube...", Colors.OKCYAN, args.color)

        try:
            info_cmd = ['yt-dlp', '--no-warnings', '--dump-json', '--no-playlist', url]
            if args.cookies: info_cmd.extend(['--cookies-from-browser', args.cookies])
            if args.add_header: info_cmd.extend(['--user-agent', USER_AGENT_HEADER])
            if args.limit_rate: info_cmd.extend(['--limit-rate', args.limit_rate])
            
            raw_output = subprocess.check_output(info_cmd, stderr=subprocess.DEVNULL)
            video_info = json.loads(raw_output.decode('utf-8', errors='replace'))
            video_title = re.sub(r'[\\/*?:"<>|]', "", video_info.get('title', f"video_{i}"))
        except Exception:
            if args.min: sys.stdout.write(f"\n{Colors.FAIL}Error: Metadata fetch failed.{Colors.ENDC}\n")
            failed_urls.append(f"{url} | REASON: Metadata fetch failed.")
            error_count += 1; continue

        ext = '.mp4' if args.mp4fast else '.mp3'
        final_filepath = destination_dir / (f"{video_title}{ext}" if not args.output else args.output)

        # Fix: Implementation of --skip logic
        if args.skip and final_filepath.exists():
            if args.min:
                show_minimal_status(i, len(urls), f"Skipping: {video_title[:30]}... (Exists)", args.color, Colors.WARNING, title=video_title, title_limit=args.showname)
                sys.stdout.write("\n")
            else:
                cprint(f"Skipping: {final_filepath.name} already exists.", Colors.WARNING, args.color)
            continue

        if args.min:
            for s in range(3, 0, -1):
                show_minimal_status(i, len(urls), f"Starting in {s}s: {video_title[:30]}...", args.color, Colors.HEADER, title=video_title, title_limit=args.showname)
                time.sleep(1)
            show_minimal_status(i, len(urls), "Pre-processing...", args.color, Colors.HEADER, title=video_title, title_limit=args.showname)
        else:
            cprint(f"Title: {video_title}", Colors.OKGREEN, args.color)
            for s in range(3, 0, -1):
                sys.stdout.write(f"\rStarting download in {s}s... "); sys.stdout.flush(); time.sleep(1)
            sys.stdout.write("\r" + " " * 40 + "\r")

        start_time = time.monotonic()
        
        if args.mp4fast:
            cmd = ['yt-dlp', '--no-warnings', '--progress', '--merge-output-format', 'mp4', '-o', str(final_filepath), url]
            if args.overwrite: cmd.append('--force-overwrite')
            if args.add_header: cmd.extend(['--user-agent', USER_AGENT_HEADER])
            if args.limit_rate: cmd.extend(['--limit-rate', args.limit_rate])
            if run_command(cmd, args, lambda line, a: download_progress_handler(line, a, i, len(urls), title=video_title)):
                LAST_FULL_LINE = LAST_DL_LINE
                finish_summary(start_time, args, i, len(urls), title=video_title)
            else: 
                failed_urls.append(f"{url} | REASON: Download failed (Video).")
                error_count += 1
        else:
            temp_path = destination_dir / f"temp_{os.getpid()}_{i}.%(ext)s"
            dl_cmd = ['yt-dlp', '--no-warnings', '--progress', '-f', 'bestaudio', '-o', str(temp_path), url]
            if args.add_header: dl_cmd.extend(['--user-agent', USER_AGENT_HEADER])
            if args.limit_rate: dl_cmd.extend(['--limit-rate', args.limit_rate])
            
            if run_command(dl_cmd, args, lambda line, a: download_progress_handler(line, a, i, len(urls), title=video_title)):
                actual_input = next(destination_dir.glob(f"temp_{os.getpid()}_{i}.*"), None)
                if actual_input:
                    current_files_to_cleanup.append(actual_input)
                    duration = video_info.get('duration', 0)
                    cv_cmd = ['ffmpeg', '-threads', '0', '-i', str(actual_input), '-vn']
                    cv_cmd.extend(['-b:a', '128k'] if (args.mp3fast or args.mp3128) else ['-b:a', '192k'])
                    cv_cmd.extend(['-progress', 'pipe:1', '-y', str(final_filepath)])
                    
                    ff_state = {'total_size': '0', 'out_time': '0:00:00', 'out_time_us': '0', 'last_update': 0}
                    if run_command(cv_cmd, args, lambda line, a: conversion_progress_handler(line, a, duration, i, len(urls), ff_state, title=video_title)):
                        finish_summary(start_time, args, i, len(urls), title=video_title)
                    else: 
                        failed_urls.append(f"{url} | REASON: Conversion to MP3 failed.")
                        error_count += 1
                    try: os.remove(actual_input)
                    except: pass
                else:
                    failed_urls.append(f"{url} | REASON: Downloaded temp file missing.")
                    error_count += 1
            else: 
                failed_urls.append(f"{url} | REASON: Download failed (Audio).")
                error_count += 1

    if failed_urls:
        err_file = Path("ytextractor.err")
        with open(err_file, "w", encoding="utf-8") as f:
            f.write("\n".join(failed_urls))
        cprint(f"\n{len(failed_urls)} file(s) failed or are incomplete.", Colors.FAIL, args.color, force_print=True)
        cprint(f"Details saved to: {err_file.absolute()}", Colors.WARNING, args.color, force_print=True)

    sys.exit(error_count)

def finish_summary(start_time, args, i, total, title=""):
    elapsed = time.monotonic() - start_time
    msg = f"Summary: Completed in {elapsed:.2f}s"
    if args.min:
        color_msg = f"{Colors.OKGREEN}{msg}{Colors.ENDC}" if args.color else msg
        prefix = show_minimal_status(i, total, "", args.color, title=title, title_limit=args.showname)
        sys.stdout.write(f"\r\033[K{prefix}{LAST_FULL_LINE} | {color_msg}\n")
    else:
        cprint(f"\n{msg}", Colors.OKGREEN, args.color)
    sys.stdout.flush()

def download_progress_handler(line, args, i, total, title=""):
    global LAST_DL_LINE
    stripped = line.strip()
    if '[download]' in stripped and '%' in stripped:
        match = re.search(r'(\d+\.?\d*%) of\s+([\d\.]+\w+) at\s+([\d\.]+\w+/s)', stripped)
        if match:
            p, size, speed = match.groups()
            if args.min:
                status = f"Downloading: {Colors.BOLD}{p.rjust(6)}{Colors.ENDC} of {Colors.C_YELLOW}{size.rjust(9)}{Colors.ENDC} at {Colors.C_MAGENTA}{speed.rjust(10)}{Colors.ENDC}" if args.color else f"Downloading: {p.rjust(6)} of {size.rjust(9)} at {speed.rjust(10)}"
                LAST_DL_LINE = status
                show_minimal_status(i, total, LAST_DL_LINE, args.color, title=title, title_limit=args.showname)
            else:
                LAST_DL_LINE = color_dl_line(stripped, args.color)
                sys.stdout.write(f"\r\033[K{LAST_DL_LINE}")
            sys.stdout.flush()

def conversion_progress_handler(line, args, total_duration, i, total, state, title=""):
    global LAST_FULL_LINE, LAST_DL_LINE
    kv = line.strip().split('=')
    if len(kv) == 2: state[kv[0]] = kv[1]
    
    if "out_time_us=" in line:
        now = time.monotonic()
        if args.min and (now - state['last_update'] < 0.1): return
        state['last_update'] = now
        try:
            us = int(state.get('out_time_us', '0'))
            percent = min(100.0, (us / (total_duration * 1_000_000)) * 100) if total_duration > 0 else 0
        except: percent = 0
        size = format_bytes(state.get('total_size', '0'))
        time_str = format_ff_time(state.get('out_time', '0:00:00'))
        
        status = f"Converting: {Colors.BOLD}{percent:.1f}%{Colors.ENDC} ({Colors.C_YELLOW}{size}{Colors.ENDC}, {Colors.OKBLUE}{time_str}{Colors.ENDC})" if args.color else f"Converting: {percent:.1f}% ({size}, {time_str})"
            
        if args.min:
            LAST_FULL_LINE = f"{LAST_DL_LINE} | {status}"
            show_minimal_status(i, total, LAST_FULL_LINE, args.color, title=title, title_limit=args.showname)
        else:
            sys.stdout.write(f"\r\033[K{LAST_DL_LINE} | {status}")
        sys.stdout.flush()

if __name__ == '__main__': main()