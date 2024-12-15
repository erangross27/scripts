# YouTube Downloader

A simple desktop application built with PyQt5 that allows you to download YouTube videos as MP4 or extract audio as MP3.

![YouTube Downloader Screenshot](screenshot.png)

## Features

- Download YouTube videos in MP4 format
- Extract audio from YouTube videos in MP3 format
- User-friendly graphical interface
- Progress bar with download speed and ETA
- Customizable save location
- Cross-platform support (Windows, macOS, Linux)

## Prerequisites

Before running the application, make sure you have Python installed and the following dependencies:

```bash
pip install PyQt5 yt-dlp
```

You'll also need FFmpeg installed on your system:
- **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: Install via Homebrew: `brew install ffmpeg`
- **Linux**: Install via package manager: `sudo apt install ffmpeg` (Ubuntu/Debian)

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python youtube_downloader.py
```

2. Paste a YouTube URL into the URL field
3. Choose your save location (defaults to Downloads folder)
4. Select desired format (MP3 or MP4)
5. Click "Download" and wait for the process to complete

## Features in Detail

- **URL Input**: Paste any valid YouTube video URL
- **Save Location**: Choose where to save downloaded files
- **Format Selection**: Choose between:
  - MP4 (Best quality video)
  - MP3 (Audio extracted at 192kbps)
- **Progress Tracking**:
  - Real-time progress bar
  - Download speed display
  - Estimated time remaining
  - Status updates

## Technical Details

- Built with PyQt5 for the GUI
- Uses yt-dlp for downloading YouTube content
- Implements multithreading to prevent GUI freezing
- Includes error handling and user feedback
- Temporary cache management for downloads

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the YouTube download functionality
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework
- [FFmpeg](https://ffmpeg.org/) for media processing capabilities