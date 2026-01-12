===============================================================================
YouTube Audio & Video Extractor (v1.18)
===============================================================================

Author: Igor Brzezek (igor.brzezek@gmail.com)
GitHub: https://github.com/IgorBrzezek/yt-audio-download
Release Date: 12.01.2026
License: MIT License

--- DESCRIPTION ---

A robust Python-based command-line utility for extracting high-quality audio 
(MP3) or video (MP4) from YouTube. This version introduces significant 
stability improvements, including advanced signal handling, improved minimal 
UI modes, and detailed error tracking.

--- REQUIREMENTS ---

1. Python 3.x
2. yt-dlp (Main engine - ensure it is updated: yt-dlp -U)
3. FFmpeg & FFprobe (Required for audio conversion and merging)
4. colorama (Optional: provides terminal colors for progress tracking)

--- KEY FEATURES IN v1.18 ---

* SMART PROGRESS: Choose between full progress bars, a single-line minimal mode, 
  or silent batch processing.
* ANTI-BLOCKING: Built-in support for browser cookies, custom User-Agent 
  spoofing (v128 Chrome), and Android client emulation.
* ERROR LOGGING: Failsafe mechanism that records failed URLs into 
  'ytextractor.err' for later review.
* ABORT PROTECTION: Clean exit handling (Ctrl+C) that kills all background 
  processes and removes partial temp files instantly.
* UTF-8 COMPATIBILITY: Native support for special characters and emojis in 
  video titles.

--- COMMAND LINE OPTIONS ---

HELP
  -h, --short-help      Show a one-line options summary.
  --help                Show extensive categorized help and examples.

INPUT & OUTPUT
  urls                  YouTube URLs (Always wrap in double quotes).
  --list [FILE]         Path to a text file containing one URL per line.
  --skip                Skip files if the final output already exists.
  -o [NAME]             Manually specify the output filename.
  -dst [DIR]            Destination directory for saved files.
  --overwrite           Force overwrite of existing files.

FORMATS
  -mp3high              192kbps MP3 extraction (Default).
  -mp3fast / -mp3128    128kbps MP3 extraction for faster processing.
  -mp4fast              Direct video download merged into MP4 format.

OUTPUT MODES
  --min                 Minimalist single-line progress display.
  --showname X          Show only first X characters of title in --min mode.
  -b, --batch           Silent operation for automation scripts.
  --color               Enable ANSI colors for status and progress.

UTILITIES
  --cookies [BROWSER]   Use cookies from Chrome, Firefox, etc..
  -r [RATE]             Limit download speed (e.g., 50K, 2.1M).
  --log [FILE]          Detailed debug logging to a text file.

--- USAGE EXAMPLES ---

0. Main download as MP3 (128 kbps):
   python yt_avextractor.py -mp3fast --add-header --log info.log --min --color --overwrite --showname 20 "Here URL of YT movie do download"

1. If You have list of movies to download: 
   python yt_avextractor.py -mp3fast --add-header --log info.log --min --color --overwrite --showname 20 --list list.txt

2. Download audio from a list with minimal UI and 20-char titles:2
   python yt_avextractor.py --list music.txt --min --showname 20 --color

3. Fast video download using browser cookies to avoid throttling:
   python yt_avextractor.py -mp4fast --cookies chrome "https://youtube.com/..."

4. High-quality MP3 with speed limit:
   python yt_avextractor.py -mp3high -r 1.5M "URL_HERE"
   

--- TROUBLESHOOTING ---

If a download fails:
* Check 'ytextractor.err' for the URL and the specific failure reason.
* Use --log to generate a technical report of the communication with YouTube.
* Ensure yt-dlp is updated to the latest version.

===============================================================================