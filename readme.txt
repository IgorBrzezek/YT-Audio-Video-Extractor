===========================================
  YouTube Audio & Video Extractor (v1.15)
============================================

Author: Igor Brzezek (igor.brzezek@gmail.com)
GitHub: https://github.com/IgorBrzezek
Version: 1.13


-------------------
1. DESCRIPTION
-------------------

This is a command-line Python script for downloading content from YouTube. It acts as a powerful and user-friendly wrapper for the 'yt-dlp' and 'ffmpeg' tools.

Its primary purpose is to either:
  a) Extract the highest quality audio, convert it to MP3, and save it.
  b) Download the full video (with audio) in the best quality available and save it as an MP4.

The script is designed to be robust, handling single links or large batches of links from a file. It includes essential features to bypass common YouTube download errors, throttling, and restrictions, such as using your browser's cookies. It offers different output modes, from detailed progress bars to a minimal single-line status or completely silent operation for batch jobs.


-------------------
2. REQUIREMENTS
-------------------

Before running this script, you MUST have the following installed and accessible from your system's command line (i.e., added to your system's PATH).

  1. Python 3:
     - The script is written in Python 3.
     - You will also need the 'colorama' library:
       pip install colorama

  2. yt-dlp:
     - This is the core download engine.
     - Get it here: https://github.com/yt-dlp/yt-dlp
     - **CRITICAL:** YouTube changes its site often. You MUST keep yt-dlp updated.
       Run this command frequently:
       yt-dlp -U

  3. ffmpeg & ffprobe:
     - These are required for all audio extraction and MP4 merging.
     - Get them here: https://ffmpeg.org/download.html
     - The script will fail if it cannot call 'ffmpeg' and 'ffprobe' from the terminal.


-------------------
3. USAGE
-------------------

Basic command-line syntax:

  # For one or more URLs
  python yt_extractor.py [OPTIONS] "URL_1" "URL_2" ...

  # For batch processing from a file
  python yt_extractor.py --list "my_links.txt" [OPTIONS]


**IMPORTANT:** Always enclose your URLs in double quotes (" "). This prevents the command line from misinterpreting special characters like '&' (which is common in YouTube playlist URLs).


-------------------
4. DETAILED OPTIONS
-------------------

Here is a breakdown of every available command-line option, grouped by category.

=== Help Options ===

  -h, --short-help
    Shows a brief, one-line help message for common commands.

  --help
    Shows the full, detailed help message (the one in the script's header).

=== Input & Output Options ===

  urls (Positional)
    One or more YouTube video URLs, separated by spaces. This argument is
    ignored if the --list option is used.
    Example: python yt_extractor.py "URL1" "URL2"

  -o FILENAME, --output FILENAME
    Specify a custom output filename.
    **IMPORTANT:** This option ONLY works when downloading a SINGLE URL. It will
    be ignored if you provide multiple URLs or use a list.
    Example: -o "My Custom Name.mp3"

  --list FILE
    Path to a text file containing a list of URLs to process. The file
    should have one URL per line. Do NOT use quotes around the URLs
    inside the file.
    Example: --list "links.txt"

  -dst DIRECTORY
    Specifies the destination directory where all downloaded files
    will be saved. If not provided, files are saved in the
    same directory as the script.
    Example: -dst "C:\My Music\Downloads"

  --overwrite
    Force overwrite of existing files. This passes the `--force-overwrite`
    flag to yt-dlp, ensuring files are re-downloaded and overwritten.
    This option is automatically implied when using batch mode (`-b`).

=== Format Options (Choose One) ===

  -mp3fast (Default)
    This is the default mode. It downloads the best available audio
    stream and uses ffmpeg to convert it to a high-quality VBR (Variable
    Bitrate) MP3. Provides excellent quality and is fast.

  -mp3128
    Downloads the best audio and re-encodes it as a 128kbps Constant
    Bitrate (CBR) MP3. Use this if file size is a major concern.

  -mp4fast
    Downloads the full video. It finds the best available video stream
    and the best available audio stream, then *remuxes* (merges) them
    into a single .mp4 file without re-encoding. Fastest way to get the
    video file.

=== Anti-Blocking & Network Options ===

  --cookies BROWSER
    This is the **most effective method** for bypassing YouTube errors,
    "403 Forbidden" errors, age-restrictions, and throttling.
    It tells yt-dlp to use the cookies from your logged-in browser.
    - BROWSER can be: chrome, firefox, edge, brave, opera, safari, etc.
    - For advanced users with multiple browser profiles, you can specify one,
      e.g., --cookies "firefox:default-release"
    Example: --cookies chrome

  -r RATE, --limit-rate RATE
    Limits the maximum download speed. Useful to avoid detection or
    saturating your connection.
    Example: -r 500K (for 500 KB/s), -r 2M (for 2 MB/s)

  --add-header
    Adds a standard browser "User-Agent" header to the download request.
    Try this if standard downloading fails.
    **Do not use this at the same time as --add-android.**

  --add-android
    Tells yt-dlp to mimic a request from the official YouTube Android app.
    Often effective at bypassing restrictions.
    **Do not use this at the same time as --add-header.**

=== Output Mode Options (Choose One) ===

  (Default)
    Normal output mode. Shows essential messages, download progress (`[download] ...%`),
    and conversion progress (`Converting to mp3: ...%`). Does not show
    verbose `[youtube]` or `[info]` messages.

  --pb
    Similar to the default mode but tries to show the more detailed
    yt-dlp progress bar if possible (size, speed, ETA).

  --min
    Minimal mode. Displays only a single, dynamically updating line per file,
    showing the current status (e.g., Downloading, Converting) and percentages.
    Ends with a summary line for each file (times, size).

  -b, --batch
    Silent (batch) mode. Produces *no* output on the console (logging still works).
    Automatically implies `--overwrite`. Ideal for scripting.
    The script returns an exit code: 0 for full success, or N (N > 0) indicating
    the number of files that failed.

=== Utility Options ===

  --color
    Forces colorful output in the terminal (useful if not enabled by default).
    This option is ignored in `--batch` and `--min` modes.

  --log [FILENAME]
    Creates a log file (default: yt-dlp.log) in the script's directory.
    All output, including errors and debug info if enabled, will be written here.
    Example: --log my_download_log.txt

  --debug
    Enables verbose mode. Prints all raw, detailed output from 'yt-dlp'
    and 'ffmpeg' commands. Essential for troubleshooting.
    This option is ignored in `--batch` and `--min` modes.


-------------------
5. EXAMPLES
-------------------

Here are 10 examples, covering various scenarios.

Example 1: Basic Audio Download (Default)
  Downloads a single song as a high-quality MP3 using default settings.

    python yt_extractor.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


Example 2: Download Full Video (Fastest)
  Downloads the best video and audio, merging them into an MP4 file quickly.

    python yt_extractor.py -mp4fast "https://www.youtube.com/watch?v=VIDEO_ID_HERE"


Example 3: Recommended "Safe" Download (Using Cookies)
  Best method to avoid most errors (403, age-restriction). Uses Chrome cookies.

    python yt_extractor.py --cookies chrome "https://www.youtube.com/watch?v=AGE_RESTRICTED_ID"


Example 4: Batch Processing a List to a Specific Folder
  Downloads all URLs from "my_playlist.txt" as default MP3s into the "My Music" folder.

    python yt_extractor.py --list "my_playlist.txt" -dst "C:\Users\MyUser\Music"


Example 5: Multiple URLs, Smaller File Size (128kbps MP3)
  Downloads two specific URLs as smaller 128kbps MP3s into a sub-folder "Podcasts".

    python yt_extractor.py -mp3128 -dst "./Podcasts" "URL_1" "URL_2"


Example 6: Custom Filename and Force Overwrite
  Downloads a single video as MP4, names it "MyVideo.mp4", and forces
  overwriting if it already exists.

    python yt_extractor.py -mp4fast -o "MyVideo.mp4" --overwrite "URL_VIDEO"


Example 7: Minimal Progress for a List
  Downloads all URLs from "links.txt" as default MP3s, showing only the
  single-line minimal progress updates.

    python yt_extractor.py --list "links.txt" --min


Example 8: Silent Batch Job with Logging
  Downloads URLs from "work_list.txt" completely silently (`-b`), saving
  all logs to "work_log.txt". Check the system exit code afterwards for errors.

    python yt_extractor.py --list "work_list.txt" -b --log "work_log.txt"
    # On Linux/macOS: echo $?
    # On Windows: echo %ERRORLEVEL%


Example 9: Alternative Strategy with Rate Limiting
  If a standard download fails, try using the Android client simulation
  and limit the speed to 1MB/s to appear less aggressive.

    python yt_extractor.py --add-android -r 1M "https://www.youtube.com/watch?v=STUBBORN_ID"


Example 10: Download Audio with Specific Output Name and Debugging
  Downloads a single audio file, names it explicitly, enables colors,
  and shows all detailed debug output from yt-dlp/ffmpeg.

    python yt_extractor.py -o "SpecificSong.mp3" --color --debug "URL_SONG"


-------------------
6. TROUBLESHOOTING & BEST PRACTICES
-------------------

  1. **"ERROR: ... 403: Forbidden" or "Age-Restricted"**
     - **Solution:** Use the `--cookies BROWSER` option. This solves this
       problem 99% of the time.

  2. **Script Fails on ALL downloads (even simple ones)**
     - **Solution:** Your 'yt-dlp' is out of date. YouTube changes its
       website code, and yt-dlp must be updated to match.
       Run `yt-dlp -U` from your command line. Do this regularly.

  3. **"ffmpeg: command not found" or "ffprobe: command not found"**
     - **Solution:** 'ffmpeg' and 'ffprobe' are not in your system's PATH.
       Download them from ffmpeg.org and place them in a directory included
       in your PATH, or add their location to your PATH environment variable.

  4. **URLs with '&' (like playlists) cause errors!**
     - **Solution:** You forgot to put the URL in double quotes (" ").
       **WRONG:** python yt_extractor.py https://...&list=...
       **RIGHT:** python yt_extractor.py "https://...&list=..."

  5. **A video still won't download, even with cookies.**
     - **Solution:** Try the alternative download strategies: `--add-header` or
       `--add-android`. Use only one of them at a time.

  6. **Overwrite doesn't seem to work.**
     - **Solution:** Ensure you are using the `--overwrite` flag. It passes
       `--force-overwrite` to yt-dlp. Check for typos. Batch mode (`-b`)
       automatically includes this.


-------------------
7. LICENSE
-------------------

MIT License
