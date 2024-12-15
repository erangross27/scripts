# Python Scripts Collection

This repository contains a diverse collection of Python scripts for various tasks,
including image and video processing, system monitoring, network analysis, quantum 
computing demonstrations, calendar management with Microsoft Graph API, and more.

## Contents

### Image Processing

- `captureImage.py`: Captures an image from the default camera with a unique filename.
- `compress_image_to_small_size.py`: GUI for compressing JPEG images.
- `convert_image_to_doc.py`: Converts image files to text documents using OCR.
- `convert_svg_to_diffrent_images_format.py`: Converts SVG files to raster image formats.
- `extract_text_from_image_regular.py`: Extracts text from images using Google Cloud Vision API.
- `extract_text_from_image_tables.py`: Extracts and processes text from images with tables.
- `watermar_detection.py`: Detects watermarks in images and videos using YOLOv5.
- `inpainting.py`: Detects and removes watermarks from images and videos.
- `image_mover.py`: GUI for moving image files between directories.
- `organize_dataset.py`: Organizes datasets into training and validation sets.

### Video Processing

- `convert_mp4_codec_and_resolution_for_tv.py`: GUI for converting video files using FFmpeg.
- `convert_youtube_to_download_multiple_movies_and_music.py`: Downloads and converts YouTube videos.
- `create_movie_clip_from_images_and_sound.py`: Creates video slideshows from images with sound.
- `extract_frames_from_video.py`: Extracts frames from multiple video files.
- `get_clip_resolution.py`: Prints the resolution of a video file.
- `video_encoding_comparison.py`: Compares CPU and GPU video encoding performance.

### System Utilities

- `anthropic_claude_chat.py`: GUI for interacting with the Anthropic Claude AI model.
- `anthropic_claude_chat_for_linux.py`: Linux version of the Claude AI chat interface.
- `disk-space-alert-service.py`: Windows service for monitoring disk space.
- `disksizeinfo.py`: Displays disk space and CPU usage information.
- `convert_audio_to_text.py`: Converts audio files to text using Google Cloud Speech-to-Text API.
- `system_discovery.py`: Collects and displays system information.

### Network

- `get_hostname_nbtstat.py`: Performs network scans and gathers device information.
- `network_analyzer.py`: GUI for real-time network traffic monitoring.

### Quantum Computing

- `deutsch_jozsa_algorithm.py`: Demonstrates the Deutsch-Jozsa quantum algorithm.
- `quantum_key_cracking.py`: Simulates quantum key cracking.
- `quantum_rng.py`: Quantum random number generator.

### Calendar

- `get_calendar_events.py`: Retrieves and displays calendar events using Microsoft Graph API.
- `get_calendar_events_for_everyone.py`: Retrieves calendar events for the next 7 days.
- `get_calendar_permissions.py`: Retrieves calendar permissions using Microsoft Graph API.
- `GraphServiceClient.py`: Retrieves calendar information including holidays and all-day events.

### Machine Learning

- `train_watermark_yolov5.py`: Trains YOLOv5 model for watermark detection.
- `mnist_cuda.py`: Trains a CNN on the MNIST dataset using PyTorch.
- `mnist_gpu_comparison.py`: Compares CPU and GPU performance for MNIST training.

### File Management

- `compress_pdf_file.py`: Compresses PDF files.
- `numbering_pdf.py`: Adds page numbers to PDF files.

### Miscellaneous

- `matrix_multiplication_comparison.py`: Compares CPU and GPU performance for matrix operations.
- `sort_cpu_gpu_comparison.py`: Compares CPU and GPU sorting performance.
- `update_readme.py`: Automatically updates README.md with script descriptions.

## Usage

Each script can be run independently. Please refer to the individual script files for specific usage instructions and requirements.

## Requirements

Requirements for running these scripts vary. A `requirements.txt` file is provided in the repository root. To install all dependencies, run:


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
