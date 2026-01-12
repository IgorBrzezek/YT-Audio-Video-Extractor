# YouTube Audio & Video Extractor (v1.18)

**Author:** Igor Brzezek (igor.brzezek@gmail.com)
**Version:** 1.18
**GitHub:** https://github.com/IgorBrzezek/yt-audio-download

---

## 1. DESCRIPTION

This is a command-line Python script for downloading content from YouTube. It acts as an advanced and user-friendly wrapper for the `yt-dlp` and `ffmpeg` tools.

Its main purpose is:
a) To extract the highest quality audio, convert it to MP3, and save it.
b) To download the full video (with audio) in the best available quality and save it as an MP4 file.

The script is designed for reliability, handling single links or large batches of links from a file. It includes key features to bypass common YouTube download errors, speed limits, and restrictions, such as using browser cookies. It offers various display modes: from detailed progress, through a minimalist single-line status, to completely silent operation for batch jobs.

Failed or incomplete downloads are logged to `ytextractor.err` for easy review.

---

## 2. CHANGELOG (Recent)

-   **v1.18:** Added `--showname X` to display the first X characters of the video title in minimal mode. The `--skip` logic has been improved to correctly check for the existence of the final output file.
-   **v1.18p6:** Implemented `ytextractor.err` reporting for failed/incomplete downloads and enhanced the end-of-process summary.
-   **v1.18p5:** Fully restored the original categorized `--help` layout and all missing options.

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
`python yt_avextractor_1.18.py [OPTIONS] "URL_1" "URL_2" ...`

### For batch processing from a file
`python yt_avextractor_1.18.py --list "my_links.txt" [OPTIONS]`

**IMPORTANT:** Always enclose URLs in double quotes (`" "`). This prevents the command line from misinterpreting special characters like `&` (common in YouTube playlist URLs).

---

## 5. DETAILED OPTION DESCRIPTION

Below is a description of all available command-line options, grouped by category.

### Help
-   `-h, --short-help`
    Shows a short, one-line summary of options.
-   `--help`
    Shows extensive, categorized help with descriptions for all options.

### Input & Output
-   `urls` (Positional)
    One or more YouTube video URLs. This is ignored if `--list` is used.
-   `-o, --output FILENAME`
    Specifies a custom output filename. **IMPORTANT:** This option ONLY works when downloading a SINGLE URL.
-   `--list FILE`
    Path to a text file containing a list of URLs to process (one URL per line).
-   `--skip`
    Skips downloading a file if the final output file (e.g., `My Video.mp3`) already exists in the destination directory. Useful for resuming interrupted batch jobs.
-   `-dst DIRECTORY`
    Specifies the destination directory for saved files. Defaults to the current directory.
-   `--overwrite`
    Forces overwriting of existing files.

### Format (Choose one)
-   `-mp3high` (Default)
    Downloads the best audio and converts it to a high-quality MP3 (192 kbps).
-   `-mp3fast` or `-mp3128`
    Downloads the best audio and converts it to a standard-quality MP3 (128 kbps). Use this for smaller file sizes.
-   `-mp4fast`
    Downloads the full video. It finds the best available video and audio streams, then combines them into a single `.mp4` file without re-encoding. This is the fastest method for video.

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

---

## 6. EXAMPLES

-   **Example 1: Basic Audio Download (High Quality)**
    Downloads a single song as a high-quality 192kbps MP3.
    ```bash
    python yt_avextractor_1.18.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    ```

-   **Example 2: Full Video Download (Fastest)**
    Downloads the best video and audio, quickly combining them into an MP4 file.
    ```bash
    python yt_avextractor_1.18.py -mp4fast "https://www.youtube.com/watch?v=VIDEO_ID"
    ```

-   **Example 3: Recommended "Safe" Download (Using Cookies)**
    The best method for avoiding most errors (403, age restrictions). Uses Chrome cookies.
    ```bash
    python yt_avextractor_1.18.py --cookies chrome "https://www.youtube.com/watch?v=AGE_RESTRICTED_ID"
    ```

-   **Example 4: Full-Featured Batch Job (Recommended)**
    Processes `lista.txt`, downloads as 128kbps MP3s, uses headers, skips existing files, logs output, and shows minimal, colored progress with the first 20 characters of each title.
    ```bash
    python yt_avextractor_1.18.py -mp3fast --add-header --log info.log --list lista.txt --min --color --skip --showname 20
    ```

-   **Example 5: Batch Processing to a Specific Folder**
    Downloads all URLs from `my_playlist.txt` to the "My Music" folder.
    ```bash
    python yt_avextractor_1.18.py --list "my_playlist.txt" -dst "C:\Users\MyUser\Music"
    ```

---

## 7. TROUBLESHOOTING

-   **"ERROR: ... 403: Forbidden" or "Age-Restricted"**
    *Solution:* Use the `--cookies BROWSER` option. This solves the problem in 99% of cases.

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
