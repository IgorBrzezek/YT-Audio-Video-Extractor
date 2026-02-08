===============================================================================
YouTube Audio & Video Extractor (v1.20)
===============================================================================

Author: Igor Brzezek (igor.brzezek@gmail.com)
GitHub: https://github.com/IgorBrzezek/yt-audio-download
Release Date: 08.02.2026
License: MIT License

--- DESCRIPTION ---

A robust Python-based command-line utility for extracting high-quality audio
(MP3) or video (MP4) from YouTube. Version 1.20 introduces yt-dlp management
tools, improved temporary file handling, single-line progress display, and
comprehensive bug fixes. Features enhanced reliability, cleaner progress
output, and full English language support.

--- REQUIREMENTS ---

1. Python 3.x
2. yt-dlp (Main engine - ensure it is updated: yt-dlp -U or use --dlupg)
3. FFmpeg & FFprobe (Required for audio conversion and merging)
4. colorama (Optional: provides terminal colors for progress tracking)

--- KEY FEATURES IN v1.20 ---

* YT-DLP MANAGEMENT: Built-in commands to check (--dlver), compare (--dlchk),
  and update (--dlupg) yt-dlp directly from the script.
* SINGLE-LINE PROGRESS: Unified format showing file number, download progress,
  conversion progress, and summary all on one clean line.
* IMPROVED TEMP FILE HANDLING: All temporary files use 'ytextr_tmp_' prefix
  and are automatically cleaned up at startup and during operation.
* LANGUAGE STANDARDIZATION: Complete English language support throughout
  code, comments, and user messages.
* FIXED OVERWRITE BUG: Interactive overwrite prompt now properly deletes
  existing files before re-downloading.
* EXTENDED AUDIO FORMATS: Options for high-quality stereo MP3 (-mp3slow)
  and space-saving mono MP3 (-mono).
* EXTENDED VIDEO FORMATS: Specific options for 1080p (-mp41080) and
  480p (-mp4480) video downloads.
* ENHANCED OUTPUT MODES: --compact for cleaner list view, --summarize for
  detailed post-download reports, and --title to display titles.
* IMPROVED CONCURRENCY & RELIABILITY: Specify FFmpeg threads (-t/--threads)
  and enable automatic retries (-ret/--retries).
* INTERACTIVE OVERWRITE: Prompt ([y/N/a/q]) for handling existing files
  with full control (overwrite, skip, overwrite all, or quit).
* ANTI-BLOCKING: Support for browser cookies, custom User-Agent spoofing,
  and Android client emulation.
* ERROR LOGGING: Records failed URLs into 'ytextractor.err' for review.
* ABORT PROTECTION: Clean exit handling (Ctrl+C) that kills background
  processes and removes partial files instantly.

--- COMMAND LINE OPTIONS ---

HELP
  -h, --short-help      Show short help message.
  --help                Show extensive categorized help and examples.

INPUT & OUTPUT
  urls                  YouTube URLs (Always wrap in double quotes).
  --list [FILE]         Path to a text file containing one URL per line.
  --skip                Skip existing files without asking.
  --overwrite           Overwrite existing files without asking.
  -o [NAME]             Manually specify the output filename.
  -dst [DIR]            Destination directory for saved files.

FORMAT (Audio)
  -mp3high              MP3 stereo VBR 192kbps (default quality).
  -mp3fast              MP3 stereo VBR 128kbps (fast compression).
  -mp3slow              MP3 stereo VBR 196kbps (high quality).
  -mono                 MP3 mono VBR 96kbps (space saving).

FORMAT (Video)
  -mp4fast              MP4 video 720p (fastest way).
  -mp41080              MP4 video 1080p or best available.
  -mp4480               MP4 video 480p or best available.

ANTI-BLOCKING
  --cookies [BROWSER]   Use cookies from Chrome, Firefox, etc.
  -r, --limit-rate [RATE] Limit download speed (e.g., 50K, 2.1M).
  --add-header          Add UA header.
  --add-android         Use android client spoofing.

OUTPUT MODE
  --pb                  Show progress bar (if supported).
  --min                 Download with minimal, single-line progress updates.
  -b, --batch           Run a batch job from a file silently.
  --compact             Compact view for the --list option.
  -sum, --summarize     Show a summary after all downloads (for --list).
  --title               Show title of each downloaded item (for --list).
  --showname X          Show X chars of title in minimal mode.

UTILITIES
  --color               Enable colored output.
  --log                 Log yt-dlp output to file.
  --debug               Show debug information.
  --verbose             Verbose output.
  -t, --threads         Number of threads for compression (default: 1).
  -ret, --retries       Number of retries for a failed download (default: 1).

YT-DLP MANAGEMENT
  --dlver               Show current yt-dlp version.
  --dlchk               Check latest yt-dlp version available online.
  --dlupg               Update yt-dlp to latest version (OS-specific).

--- USAGE EXAMPLES ---

0. Main download as MP3 (high quality, stereo):
   python yt_avextractor.py -mp3slow --color "https://www.youtube.com/watch?v=VIDEO_ID"

1. Download audio from a list with compact view, summary, and titles:
   python yt_avextractor.py --list music.txt --compact --summarize --title --color

2. Fast video download (720p) using browser cookies:
   python yt_avextractor.py -mp4fast --cookies chrome "https://www.youtube.com/watch?v=VIDEO_ID"

3. Download 1080p video with 4 FFmpeg threads:
   python yt_avextractor.py -mp41080 -t 4 --color "https://www.youtube.com/watch?v=VIDEO_ID"

4. Download mono MP3 (space saving) with retries:
   python yt_avextractor.py -mono -ret 3 "https://www.youtube.com/watch?v=VIDEO_ID"

5. Download from a list, skipping existing files without asking:
   python yt_avextractor.py --list downloads.txt --skip --color

--- TROUBLESHOOTING ---

If a download fails:
* Check 'ytextractor.err' for the URL and the specific failure reason.
* Use --log to generate a technical report of the communication with YouTube.
* Ensure yt-dlp is updated to the latest version.

===============================================================================
