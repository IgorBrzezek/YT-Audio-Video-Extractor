# YouTube Audio & Video Extractor (v1.19)

**Author:** Igor Brzezek (igor.brzezek@gmail.com)
**Version:** 1.19
**GitHub:** https://github.com/IgorBrzezek/yt-audio-download

---

## 1. DESCRIPTION

This is a robust command-line Python script for downloading and extracting audio or video content from YouTube. It serves as an advanced and user-friendly wrapper for the `yt-dlp` and `ffmpeg` tools, designed to provide comprehensive control over your downloads.

Its main purpose is:
a) To extract high-quality audio, convert it to various MP3 formats (stereo and mono), and save it.
b) To download the full video (with audio) in various resolutions (720p, 1080p, 480p) and save it as an MP4 file.

The script is engineered for reliability and flexibility, supporting single links or large batches of links from a file. It incorporates key features to circumvent common YouTube download errors, speed limits, and regional restrictions, often leveraging browser cookies. It provides diverse output modes, from detailed progress bars, through a minimalist single-line status, to a compact view for batch lists, and completely silent operation for automation. New interactive overwrite prompts provide granular control over existing files, and improved retry mechanisms enhance download stability.

Failed or incomplete downloads are meticulously logged to `ytextractor.err` for easy review.

---

## 2. CHANGELOG (v1.19)

### Version 1.19 (2026-01-21)

#### New Features

*   **Extended Audio Formats:**
    *   Added `-mp3slow` option for high-quality MP3 (VBR 196kbps).
    *   Added `-mono` option for space-saving mono MP3 (VBR 96kbps).
*   **Extended Video Formats:**
    *   Introduced `-mp41080` for 1080p video downloads.
    *   Introduced `-mp4480` for 480p video downloads.
*   **Enhanced Output Modes:**
    *   Added `--compact` mode for a compact view when using `--list`.
    *   Implemented `--summarize` to display a comprehensive summary after all batch downloads are completed.
    *   Added `--title` option to show the title of each downloaded item when using `--list`.
*   **Improved Concurrency & Reliability:**
    *   Added `-t/--threads` option to specify the number of threads for FFmpeg compression.
    *   Implemented `-ret/--retries` option to allow automatic retries for failed downloads.
*   **Interactive Overwrite Prompt:** Introduced an interactive prompt (`[y/N/a/q]`) to handle existing files, allowing users to choose to overwrite, skip, overwrite all, or quit.
*   **Global State Management:** Refactored global variables to better manage download and conversion progress, including:
    *   `IS_COMPACT_MODE`: New flag to control compact output.
    *   `VIDEO_PROGRESS`, `AUDIO_PROGRESS`: Separate variables for tracking video and audio download/conversion progress, improving clarity for merged formats.
    *   `OVERWRITE_ALL`: New flag to apply overwrite decision across all files in batch mode.
    *   `SUMMARY_DATA`: Collects detailed information (size, time, speeds) for post-download summaries.
    *   `current_file_download_speed_bps`, `current_file_compress_speed_bps`: Track real-time speeds per file for summary statistics.
*   **Progress Reporting:**
    *   `show_minimal_status` now intelligently adapts its output for the new `--compact` mode.
    *   `download_progress_handler` and `conversion_progress_handler` were updated to handle video/audio stream distinctions and update new global progress variables more accurately.
*   **Speed and Size Calculation:**
    *   New utility functions `speed_to_bytes_per_second` and `size_to_bytes` were added for more robust and accurate calculation of download/compression speeds and file sizes across various formats (yt-dlp and FFmpeg outputs).
*   **Argument Parsing:**
    *   Help message descriptions for `-h` and `--help` were swapped for better clarity.
    *   Grouped format options into 'Format (Audio)' and 'Format (Video)' for better organization.
*   **FFmpeg Audio Quality Control:** Switched to using `-q:a` (VBR quality) for MP3 encoding instead of `-b:a` (CBR bitrate), allowing for more flexible and higher quality audio outputs.
*   **Dynamic Video Format Selection:** Implemented dynamic selection of yt-dlp video formats based on `-mp4fast`, `-mp41080`, and `-mp4480` options.
*   **Error Reporting:** Improved error reporting context, especially with the introduction of retries.

#### Bug Fixes

*   Fixed an issue where the `--skip` and `--overwrite` options might not behave as expected in all scenarios by integrating the new interactive overwrite logic and making their behavior more explicit ("without asking").

#### Refactoring

*   **Code Structure:** Introduced `DownloadState` class to encapsulate stream-specific download state, improving modularity and reducing global state reliance for complex download scenarios.
*   **`run_command` Function:** Modified to accept additional keyword arguments for custom handlers, making it more flexible.

---

## 3. REQUIREMENTS

Before running the script, you **MUST** have the following tools installed and available from the system's command line (i.e., added to the system's PATH environment variable):

1.  **Python 3:**
    *   The script is written in Python 3.
    *   You will also need the `colorama` library:
        ```bash
        pip install colorama
        ```

2.  **yt-dlp:**
    *   This is the main download engine.
    *   Download from here: [https://github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)
    *   **CRITICAL:** YouTube frequently changes its site. You MUST keep `yt-dlp` up to date.
        Run this command regularly:
        ```bash
        yt-dlp -U
        ```

3.  **ffmpeg & ffprobe:**
    *   These are required for audio extraction and merging MP4 files.
    *   Download from here: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
    *   The script will fail if it cannot call `ffmpeg` and `ffprobe` from the terminal.

---

## 4. USAGE

Basic command-line syntax:

### For one or more URLs
`python yt_avextractor.py [OPTIONS] "URL_1" "URL_2" ...`

### For batch processing from a file
`python yt_avextractor.py --list "my_links.txt" [OPTIONS]`

**IMPORTANT:** Always enclose URLs in double quotes (`" "`). This prevents the command line from misinterpreting special characters like `&` (common in YouTube playlist URLs).

---

## 5. DETAILED OPTION DESCRIPTION

Below is a description of all available command-line options, grouped by category.

### Help
-   `-h, --short-help`
    Shows a short, one-line summary of options. (This was previously `--help`).
-   `--help`
    Shows extensive, categorized help with descriptions for all options and examples. (This was previously `-h, --short-help`).

### Input & Output
-   `urls` (Positional)
    One or more YouTube video URLs. This is ignored if `--list` is used.
-   `-o, --output FILENAME`
    Specifies a custom output filename. **IMPORTANT:** This option ONLY works when downloading a SINGLE URL.
-   `--list FILE`
    Path to a text file containing a list of URLs to process (one URL per line).
-   `--skip`
    Skips downloading a file if the final output already exists **without asking**. In interactive mode, this implies choosing 's' (skip) for all existing files.
-   `-dst DIRECTORY`
    Specifies the destination directory for saved files. Defaults to the current directory.
-   `--overwrite`
    Forces overwriting of existing files **without asking**. In interactive mode, this implies choosing 'y' (yes) for all existing files.

### Format (Audio)
-   `-mp3high` (Default)
    Downloads the best audio and converts it to a high-quality MP3 (VBR 192kbps).
-   `-mp3fast`
    Downloads the best audio and converts it to a standard-quality MP3 (VBR 128kbps) for faster processing.
-   `-mp3slow`
    Downloads the best audio and converts it to a high-quality MP3 (VBR 196kbps) for enhanced audio fidelity.
-   `-mono`
    Downloads the best audio and converts it to a space-saving mono MP3 (VBR 96kbps).

### Format (Video)
-   `-mp4fast`
    Downloads the full video (720p or best available up to 720p). It finds the best available video and audio streams, then combines them into a single `.mp4` file without re-encoding. This is the fastest method for video.
-   `-mp41080`
    Downloads the full video (1080p or best available up to 1080p).
-   `-mp4480`
    Downloads the full video (480p or best available up to 480p).

### Anti-Blocking
-   `--cookies BROWSER`
    The most effective method for bypassing YouTube errors (e.g., "403 Forbidden"), age restrictions, and speed throttling. Uses cookies from your browser. `BROWSER` can be: `chrome`, `firefox`, `edge`, `brave`, `opera`, etc.
-   `-r, --limit-rate RATE`
    Limits the maximum download speed. Examples: `500K` (500 KB/s), `4.2M` (4.2 MB/s).
-   `--add-header`
    Adds a standard browser "User-Agent" header to the download request. Try this if standard downloading fails.
-   `--add-android`
    Mimics a request from the official YouTube Android app. Often effective in bypassing restrictions.

### Output Mode
-   `--pb`
    Shows a detailed progress bar from `yt-dlp` (if supported).
-   `--min`
    Minimal mode. Displays a single, dynamically updated line per file, showing progress.
-   `-b, --batch`
    Silent (batch) mode. Generates no console output. Ideal for scripts.
-   `--compact`
    Compact view for `--list` option. Shows concise progress updates in a single line, ideal for monitoring many downloads.
-   `-sum, --summarize`
    Displays a comprehensive summary of all downloads (total size, time, average speeds) after all batch downloads are completed (for `--list`).
-   `--title`
    Shows the title of each downloaded item when using `--list` option.
-   `--showname X`
    In minimal (`--min`) mode, shows the first `X` characters of the video title for context.

### Utilities
-   `--color`
    Enables colored terminal output for better readability.
-   `--log [FILENAME]`
    Creates a log file (default: `yt-dlp.log`). All `yt-dlp` output is saved to this file.
-   `--debug`
    Shows all raw, detailed output from `yt-dlp` and `ffmpeg`. Essential for troubleshooting.
-   `--verbose`
    Enables verbose output.
-   `-t, --threads`
    Specifies the number of threads for FFmpeg compression (default: 1). Useful for speeding up audio conversions on multi-core processors.
-   `-ret, --retries`
    Number of retries for a failed download (default: 1). Increases robustness against transient network issues.

---

## 6. EXAMPLES

-   **Example 1: Basic Audio Download (High Quality Stereo)**
    Downloads a single song as a high-quality 196kbps VBR stereo MP3.
    ```bash
    python yt_avextractor.py -mp3slow --color "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    ```

-   **Example 2: Download Audio from a List with Compact View, Summary, and Titles**
    Processes `music.txt`, showing concise updates per file, a final summary, and each item's title.
    ```bash
    python yt_avextractor.py --list music.txt --compact --summarize --title --color
    ```

-   **Example 3: Fast Video Download (720p) using Browser Cookies**
    Downloads the best video and audio up to 720p, quickly combining them into an MP4 file, using Chrome cookies to bypass restrictions.
    ```bash
    python yt_avextractor.py -mp4fast --cookies chrome "https://www.youtube.com/watch?v=VIDEO_ID"
    ```

-   **Example 4: Download 1080p Video with 4 FFmpeg Threads**
    Downloads the best video and audio up to 1080p, utilizing 4 CPU threads for any post-processing by FFmpeg.
    ```bash
    python yt_avextractor.py -mp41080 -t 4 --color "https://www.youtube.com/watch?v=VIDEO_ID"
    ```

-   **Example 5: Download Mono MP3 (Space Saving) with Retries**
    Converts audio to a space-saving mono MP3 format, and attempts up to 3 retries if the download initially fails.
    ```bash
    python yt_avextractor.py -mono -ret 3 "https://www.youtube.com/watch?v=VIDEO_ID"
    ```

-   **Example 6: Download from a List, Skipping Existing Files without Asking**
    Processes `downloads.txt`, and will automatically skip any files that already exist in the destination folder.
    ```bash
    python yt_avextractor.py --list downloads.txt --skip --color
    ```

-   **Example 7: Interactive Overwrite Prompt for a Single File**
    When the output file already exists, the script will ask `Output file already exists. Overwrite? [y/N/a/q]:`.
    ```bash
    python yt_avextractor.py -mp3high "https://www.youtube.com/watch?v=VIDEO_ID"
    ```
    *   `y` (yes): Overwrite the current file.
    *   `N` (no): Skip the current file (default).
    *   `a` (all): Overwrite all subsequent existing files in batch mode.
    *   `q` (quit): Exit the script.

---

## 7. TROUBLESHOOTING

-   **"ERROR: ... 403: Forbidden" or "Age-Restricted"**
    *Solution:* Use the `--cookies BROWSER` option. This solves the problem in 99% of cases.

-   **Script pauses and asks `Output file already exists. Overwrite? [y/N/a/q]:`**
    *Solution:* This is the new interactive overwrite prompt.
        *   `y` to overwrite the current file.
        *   `N` to skip the current file.
        *   `a` to overwrite all subsequent existing files in batch mode.
        *   `q` to quit the script.
    *To avoid this prompt entirely, use `--skip` (to skip all existing) or `--overwrite` (to overwrite all existing) options in advance.*

-   **Script fails on ALL downloads**
    *Solution:* Your `yt-dlp` is outdated. Run `yt-dlp -U` in your terminal to update it. Do this regularly.

-   **"ffmpeg: command not found"**
    *Solution:* `ffmpeg` is not in your system's PATH. Download it from [ffmpeg.org](https://ffmpeg.org/download.html) and add its location to your PATH environment variable.

-   **Download failed for some files in a batch**
    *Solution:* Check the `ytextractor.err` file in the script's directory. It will contain a list of all failed URLs and the reason for failure.

-   **URLs with `&` (like playlists) cause errors**
    *Solution:* You forgot to enclose the URL in double quotes (`" "`).

-   **Still won't download, even with cookies**
    *Solution:* Try alternative download strategies: `--add-header` or `--add-android`. Use only one at a time.

---

## 8. LICENSE

MIT License
