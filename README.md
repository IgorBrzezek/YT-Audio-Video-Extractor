# YouTube Audio & Video Extractor (v1.15)

**Author:** Igor Brzezek (igor.brzezek@gmail.com)
**Version:** 1.15

---

## 1. DESCRIPTION

This is a command-line Python script for downloading content from YouTube. It acts as an advanced and user-friendly wrapper for the `yt-dlp` and `ffmpeg` tools.

Its main purpose is:
a) To extract the highest quality audio, convert it to MP3, and save it.
b) To download the full video (with audio) in the best available quality and save it as an MP4 file.

The script is designed for reliability, handling single links or large batches of links from a file. It includes key features to bypass common YouTube download errors, speed limits, and restrictions, such as using browser cookies. It offers various display modes: from detailed progress bars, through a minimalist single-line status, to completely silent operation for batch jobs.

---

## 2. REQUIREMENTS

Before running the script, you **MUST** have the following tools installed and available from the system's command line (i.e., added to the system's PATH environment variable):

1.  **Python 3:**
    * The script is written in Python 3.
    * You will also need the `colorama` library:
        ```bash
        pip install colorama
        ```

2.  **yt-dlp:**
    * This is the main download engine.
    * Download from here: [https://github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)
    * **CRITICAL:** YouTube frequently changes its site. You MUST keep `yt-dlp` up to date.
        Run this command regularly:
        ```bash
        yt-dlp -U
        ```

3.  **ffmpeg & ffprobe:**
    * These are required for audio extraction and merging MP4 files.
    * Download from here: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
    * The script will fail if it cannot call `ffmpeg` and `ffprobe` from the terminal.

---

## 3. USAGE

Basic command-line syntax:

### For one or more URLs
python yt_extractor.py [OPTIONS] "URL_1" "URL_2" ...

### For batch processing from a file
python yt_extractor.py --list "my_links.txt" [OPTIONS]
IMPORTANT: Always enclose URLs in double quotes (" "). This prevents the command line from misinterpreting special characters like & (common in YouTube playlist URLs).

## 4. DETAILED OPTION DESCRIPTION

Below is a description of all available command-line options, grouped by category.

Help Options
-h, --short-help Shows short, one-line help for the most common commands.

--help Shows full, detailed help (the same as in the script's header).

Input and Output Options
urls (Positional) One or more YouTube video URLs, separated by spaces. This argument is ignored if the --list option is used. Example: python yt_extractor.py "URL1" "URL2"

-o FILENAME, --output FILENAME Specifies a custom output filename. IMPORTANT: This option ONLY works when downloading a SINGLE URL. It will be ignored if you provide multiple URLs or use a list. Example: -o "My File Name.mp3"

--list FILE Path to a text file containing a list of URLs to process. The file should contain one URL per line. DO NOT use quotes around the URLs inside the file. Example: --list "links.txt"

-dst DIRECTORY Specifies the destination directory where all downloaded files will be saved. If not provided, files are saved in the same directory as the script. Example: -dst "C:\My Music\Downloads"

--overwrite Forces overwriting of existing files. Passes the --force-overwrite flag to yt-dlp, ensuring files are re-downloaded and overwritten. This option is automatically enabled when using batch mode (-b).

Format Options (Choose one)
-mp3fast (Default) This is the default mode. It downloads the best available audio stream and uses ffmpeg to convert it to a high-quality VBR (Variable Bitrate) MP3. It provides excellent quality and is very fast.

-mp3128 Downloads the best audio and re-encodes it as a 128 kbps CBR (Constant Bitrate) MP3. Use this option if file size is a major concern.

-mp4fast Downloads the full video. It finds the best available video stream and the best available audio stream, then remuxes (combines) them into a single .mp4 file without re-encoding. The fastest way to download a video file.

Anti-Blocking and Network Options
--cookies BROWSER This is the most effective method for bypassing YouTube errors, "403 Forbidden" errors, age restrictions, and speed throttling. It tells yt-dlp to use cookies from your logged-in browser.

BROWSER can be: chrome, firefox, edge, brave, opera, safari, etc.

For advanced users with multiple browser profiles, you can specify one, e.g., --cookies "firefox:default-release" Example: --cookies chrome

-r RATE, --limit-rate RATE Limits the maximum download speed. Useful to avoid detection or overloading your internet connection. Example: -r 500K (for 500 KB/s), -r 2M (for 2 MB/s)

--add-header Adds a standard browser "User-Agent" header to the download request. Try this option if standard downloading fails. Do not use simultaneously with --add-android.

--add-android Tells yt-dlp to mimic a request from the official YouTube Android app. Often effective in bypassing restrictions. Do not use simultaneously with --add-header.

Display Mode Options (Choose one)
(Default) Normal output mode. Shows necessary messages, download progress ([download] ...%), and conversion progress (Converting to mp3: ...%). Does not show detailed [youtube] or [info] messages.

--pb Similar to the default mode, but tries to show a more detailed yt-dlp progress bar if possible (size, speed, ETA).

--min Minimal mode. Displays only a single, dynamically updated line per file, showing the current status (e.g., Downloading, Converting) and percentage. Ends with a summary line for each file (times, size).

-b, --batch Silent (batch) mode. Generates no console output (logging still works). Automatically enables --overwrite. Ideal for scripts. The script returns an exit code: 0 for full success, or N (N > 0) indicating the number of files that failed.

Utility Options
--color Forces colored output in the terminal (useful if not enabled by default). This option is ignored in --batch and --min modes.

--log [FILENAME] Creates a log file (default: yt-dlp.log) in the script's directory. All output, including errors and debug information (if enabled), will be saved to this file. Example: --log my_download_log.txt

--debug Enables verbose mode. Prints all raw, detailed output from the yt-dlp and ffmpeg commands. Essential for troubleshooting. This option is ignored in --batch and --min modes.

## 5. EXAMPLES

Here are 10 examples covering various scenarios.

Example 1: Basic Audio Download (Default) Downloads a single song as a high-quality MP3 file using default settings.

python yt_extractor.py "[https://www.youtube.com/watch?v=dQw4w9WgXcQ](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
Example 2: Full Video Download (Fastest) Downloads the best video and audio, quickly combining them into an MP4 file.

python yt_extractor.py -mp4fast "[https://www.youtube.com/watch?v=VIDEO_ID_HERE](https://www.youtube.com/watch?v=VIDEO_ID_HERE)"
Example 3: Recommended "Safe" Download (Using Cookies) The best method for avoiding most errors (403, age restrictions). Uses Chrome cookies.

python yt_extractor.py --cookies chrome "[https://www.youtube.com/watch?v=AGE_RESTRICTED_ID](https://www.youtube.com/watch?v=AGE_RESTRICTED_ID)"

Example 4: Batch Processing a List to a Specific Folder Downloads all URLs from "my_playlist.txt" as default MP3 files to the "My Music" folder.

python yt_extractor.py --list "my_playlist.txt" -dst "C:\Users\MyUser\Music"
Example 5: Multiple URLs, Smaller File Size (128kbps MP3) Downloads two specific URLs as smaller 128 kbps MP3 files and places them in the "Podcasts" subfolder.

python yt_extractor.py -mp3128 -dst "./Podcasts" "URL_1" "URL_2"
Example 6: Custom Filename and Forced Overwrite Downloads a single video as an MP4, names it "MyVideo.mp4", and forces an overwrite if it already exists.

python yt_extractor.py -mp4fast -o "MyVideo.mp4" --overwrite "URL_VIDEO"
Example 7: Minimal Progress for a List Downloads all URLs from "links.txt" as default MP3 files, showing only single-line minimal progress updates.

python yt_extractor.py --list "links.txt" --min
Example 8: Silent Batch Job with Logging Downloads URLs from "work_list.txt" completely silently (-b), saving all logs to "work_log.txt". Check the system exit code after completion to see the number of errors.

python yt_extractor.py --list "work_list.txt" -b --log "work_log.txt"

### On Linux/macOS: echo $?

### On Windows: echo %ERRORLEVEL%

Example 9: Alternative Strategy with Rate Limiting If standard download fails, try using an Android client simulation and limit the speed to 1 MB/s to appear less aggressive.

python yt_extractor.py --add-android -r 1M "[https://www.youtube.com/watch?v=STUBBORN_ID](https://www.youtube.com/watch?v=STUBBORN_ID)"
Example 10: Audio Download with Specific Output Name and Debugging Downloads a single audio file, gives it a specific name, enables colors, and shows all detailed debug output from yt-dlp/ffmpeg.

python yt_extractor.py -o "SpecificSong.mp3" --color --debug "URL_SONG"

## 6. TROUBLESHOOTING AND BEST PRACTICES

"ERROR: ... 403: Forbidden" or "Age-Restricted"

Solution: Use the --cookies BROWSER option. This solves the problem in 99% of cases.

The script fails on ALL downloads (even simple ones)

Solution: Your yt-dlp is outdated. YouTube changes its site code, and yt-dlp must be updated to match. Run yt-dlp -U in your command line. Do this regularly.

"ffmpeg: command not found" or "ffprobe: command not found"

Solution: ffmpeg and ffprobe are not in your system's PATH. You need to download them from ffmpeg.org and place them in a directory that is in your PATH, or add their location to your PATH environment variable.

URLs with & (like playlists) cause errors!

Solution: You forgot to enclose the URL in double quotes (" "). INCORRECT: python yt_extractor.py https://...&list=... CORRECT: python yt_extractor.py "https://...&list=..."

The video still won't download, even with cookies.

Solution: Try alternative download strategies: --add-header or --add-android. Use only one at a time.

Overwriting (--overwrite) doesn't seem to work.

Solution: Make sure you are using the --overwrite flag. It passes --force-overwrite to yt-dlp. Check for typos. Batch mode (-b) automatically enables this option.

## 7. LICENSE

MIT License
