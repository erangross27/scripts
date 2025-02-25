# Directory Scripts Documentation

## Available Scripts


### build_app.py

**Path:** `video_processing\youtube_downloader\build_app.py`

**Description:**
This script handles build app.

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 3.6 KB
- Lines of code: 102 (of 134 total)

**Functions:**
- `build_executable`: Build executable

### youtube_downloader.py

**Path:** `video_processing\youtube_downloader\youtube_downloader.py`

**Description:**
This script downloads content related to youtube.

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 9.6 KB
- Lines of code: 231 (of 281 total)

**Functions:**
- `main`: Main

**Classes:**
- `DownloaderThread`: Represents a downloader thread
  - Methods:
    - `__init__`: Special method __init__
    - `progress_hook`: Progress hook based on d
    - `run`: Run
- `YouTubeDownloader`: Represents a you tube downloader
  - Methods:
    - `__init__`: Special method __init__
    - `initUI`: Initui
    - `browse_location`: Browse location
    - `start_download`: Start download
    - `update_progress`: Updates progress based on percentage, status text
    - `download_finished`: Download finished based on success, message

**Dependencies:**
- PyQt5
- yt_dlp