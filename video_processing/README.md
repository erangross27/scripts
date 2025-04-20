# Directory Scripts Documentation


## Available Scripts


### convert_mp4_codec_and_resolution_for_tv.py

**Path:** `video_processing\convert_mp4_codec_and_resolution_for_tv.py`

**Description:**
Video Converter Application

This script creates a GUI application for converting video files using FFmpeg.
It allows users to select a source video file, choose a destination folder,
and set conversion parameters such as codec and resolution. The application
shows a progress bar during the conversion process.

Features:
- Select source video file and destination folder
- Choose video codec (libx264 or mpeg4)
- Select output resolution (480p, 720p, or 1080p)
- Display conversion progress
- Handle FFmpeg processes and update GUI asynchronously

Dependencies:
- tkinter
- subprocess
- re
- time
- threading
- os
- sys
- FFmpeg (must be accessible in the system PATH or bundled with the application)

Note: This script is designed to work both as a standalone Python script and
when bundled with PyInstaller.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.8 KB
- Lines of code: 114 (of 162 total)

**Functions:**
- `select_source_file`: Select source file
- `select_destination_folder`: Select destination folder
- `get_duration`: Retrieves duration based on file path
- `update_progress_bar`: Updates progress bar based on value
- `convert_video`: Converts video
- `start_conversion`: Start conversion
- `on_closing`: On closing

**Dependencies:**
- tkinter

### create_movie_clip_from_images_and_sound.py

**Path:** `video_processing\create_movie_clip_from_images_and_sound.py`

**Description:**
This script creates a video slideshow from a directory of images with a repeating background sound.

The script performs the following steps:
1. Loads images from a specified directory.
2. Creates a video clip from the images, displaying each for a set duration.
3. Loads a background sound file.
4. Repeats the background sound to match the length of the video.
5. Combines the image sequence with the repeated background sound.
6. Outputs the final video file.

Required libraries:
- os: For file and directory operations.
- cv2: For image loading and processing.
- moviepy.editor: For video and audio manipulation.

Usage:
- Set the 'image_directory' variable to the path of your image folder.
- Set the 'output_video' variable to your desired output video filename.
- Set the 'image_duration' variable to the number of seconds each image should be displayed.
- Set the 'background_sound' variable to the path of your MP3 background sound file.
- Run the script to generate the video.

Note: Ensure all required libraries are installed before running the script.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 2.8 KB
- Lines of code: 43 (of 80 total)

**Dependencies:**
- cv2
- moviepy

### extract_frames_from_video.py

**Path:** `video_processing\extract_frames_from_video.py`

**Description:**
Multi-Video Frame Extractor

This script provides a graphical user interface for extracting frames from multiple video files.
It allows users to select video files, choose an output folder, and specify extraction parameters.
The application uses PyQt5 for the GUI and OpenCV for video processing.

Key features:
- Select multiple video files for frame extraction
- Choose output folder for extracted frames
- Two extraction modes: extract every N frames or extract X frames per video
- Set maximum number of frames to extract per video
- Progress bar and status updates during extraction
- Multithreaded extraction process to keep UI responsive

Classes:
- FrameExtractor: A QThread subclass that handles the frame extraction process
- App: The main application window, inheriting from QWidget

Usage:
Run this script directly to launch the graphical user interface.
Select video files, set extraction parameters, and click "Extract Frames" to begin the process.

Dependencies:
- PyQt5
- OpenCV (cv2)
- sys
- os

Author: [Eran Gross]
Date: [30/08/2024]
Version: 1.0


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 9.1 KB
- Lines of code: 195 (of 258 total)

**Classes:**
- `FrameExtractor`: Represents a frame extractor
  - Methods:
    - `__init__`: Special method __init__
    - `run`: Run
    - `get_frame_count`: Retrieves frame count based on video path
- `App`: Represents a app
  - Methods:
    - `__init__`: Special method __init__
    - `initUI`: Initui
    - `select_videos`: Select videos
    - `select_output`: Select output
    - `extract_frames`: Extract frames
    - `update_progress`: Updates progress based on value
    - `update_status`: Updates status based on status
    - `extraction_finished`: Extraction finished

**Dependencies:**
- PyQt5
- cv2

### get_clip_resolution.py

**Path:** `video_processing\get_clip_resolution.py`

**Description:**
This script demonstrates how to load a video file and retrieve its resolution using the moviepy library.

The script performs the following steps:
1. Imports the VideoFileClip class from moviepy.editor.
2. Loads a video file named "output2.mp4".
3. Prints the resolution (width and height) of the loaded video.

Usage:
    Ensure that the moviepy library is installed and that the video file "output2.mp4" 
    exists in the same directory as this script.

Note:
    This script requires the moviepy library to be installed. You can install it using pip:
    pip install moviepy


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 1.0 KB
- Lines of code: 16 (of 26 total)

**Dependencies:**
- moviepy

### video_encoding_comparison.py

**Path:** `video_processing\video_encoding_comparison.py`

**Description:**
This script compares the performance of CPU and GPU video encoding using FFmpeg.

It provides functions to:
- Print GPU and CPU memory usage
- Encode video using either CPU or GPU
- Run a comparison between CPU and GPU encoding

The script measures encoding time for both CPU and GPU (if available) over multiple runs,
calculates average encoding times, and compares the performance between CPU and GPU.

Dependencies:
- subprocess: For running FFmpeg commands
- time: For measuring encoding time
- os: For file operations
- psutil: For CPU memory usage monitoring
- GPUtil: For GPU memory usage monitoring and GPU availability checking

Usage:
Replace 'input.mp4' with the path to your input video file at the end of the script.
Run the script to perform the encoding comparison.

Note: This script requires FFmpeg to be installed and accessible in the system path.
For GPU encoding, it assumes an NVIDIA GPU with NVENC support.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.1 KB
- Lines of code: 97 (of 128 total)

**Functions:**
- `print_gpu_memory`: Print gpu memory
- `print_cpu_memory`: Print cpu memory
- `encode_video`: Encode video based on input file, output file, use gpu
- `run_comparison`: Run comparison based on input file, runs

**Dependencies:**
- GPUtil
- psutil