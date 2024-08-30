```markdown
# Python Scripts Collection

This repository contains a diverse collection of Python scripts for various tasks,
including image and video processing, system monitoring, network analysis, quantum 
computing demonstrations, calendar management with Microsoft Graph API, and more.

## Contents

### Image Processing
- **captureImage.py**: This script captures an image from the default camera and
  saves it to the specified output directory with a unique filename based on the
  current date and time.
- **compress_image_to_small_size.py**: This script provides a graphical user
  interface for compressing JPEG images, allowing users to compress either a
  single image file or all images in a folder with adjustable compression
  quality, input/output path selection, and real-time quality adjustment
  display.
- **convert_image_to_doc.py**: This script provides a graphical user interface
  that allows users to convert image files to text documents using Google Cloud
  Vision API's optical character recognition (OCR) capabilities, with the
  extracted text formatted right-to-left and saved as a Microsoft Word document.
- **convert_svg_to_diffrent_images_format.py**: This script provides a graphical
  user interface for converting SVG files to raster image formats like PNG, JPG,
  and BMP, allowing users to select an input SVG file, choose an output format
  and location, set the desired resolution, and perform the conversion.
- **extract_text_from_image_regular.py**: This script provides a graphical user
  interface (GUI) application that allows users to extract text from images
  using the Google Cloud Vision API, and save the extracted text as either a TXT
  or CSV file.
- **extract_text_from_image_tables.py**: This script provides a graphical user
  interface (GUI) application that allows users to extract text from images
  using the Google Cloud Vision API, process the extracted text to separate
  names and IDs, and save the processed data as either a TXT or CSV file.
- **watermar_detection.py**: This script provides a graphical user interface for
  detecting watermarks in images and videos using a YOLOv5 model, allowing users
  to load custom models, process individual files, and save the output with
  detected watermarks highlighted.
- **inpainting.py**: This script implements a graphical user interface (GUI)
  application that utilizes machine learning models for detecting and removing
  watermarks from images and videos.
- **image_mover.py**: This script creates a graphical user interface (GUI)
  application using PyQt5 that allows users to move image files from a source
  directory to a destination directory.
- **train_watermark_yolov5.py**: This script sets up and runs the training
  process for the YOLOv5 object detection model, allowing for customization
  through command-line arguments and predefined hyperparameters.
- **mnist_cuda.py**: This script trains a convolutional neural network model on
  the MNIST handwritten digit dataset using PyTorch for image classification
  tasks.
- **organize_dataset.py**: The script organizes a dataset by splitting it into
  training and validation sets, creating the necessary directory structure, and
  copying the image files and corresponding label files into their respective
  training and validation directories within the destination folder.
- **matrix_multiplication_comparison.py**: This script compares the performance
  of applying Gaussian blur to an image using CPU and GPU (if available), by
  measuring and displaying the execution times and memory usage for both
  methods.
- **sort_cpu_gpu_comparison.py**: This script compares the performance of sorting
  algorithms on CPU and GPU by generating random data, sorting it using NumPy for
  CPU and PyTorch for GPU, measuring the time taken for each method, and reporting
  the average times and speedup achieved by GPU sorting over CPU sorting.

### Video Processing
- **convert_mp4_codec_and_resolution_for_tv.py**: This script creates a
  graphical user interface (GUI) application that allows users to convert video
  files using FFmpeg, with options to select the source video, destination
  folder, video codec, and output resolution, while displaying the conversion
  progress.
- **convert_youtube_to_download_multiple_movies_and_music.py**: This script
  provides a graphical user interface for downloading and converting YouTube
  videos to MP3 or MP4 format, allowing batch processing, custom save locations,
  and multithreaded operations.
- **create_movie_clip_from_images_and_sound.py**: This script creates a video
  slideshow from a directory of images with a repeating background sound.
- **extract_frames_from_video.py**: This script provides a graphical user
  interface for extracting frames from multiple video files, allowing users to
  select videos, choose an output folder, and specify extraction parameters such
  as extracting every N frames or a maximum number of frames per video.
- **get_clip_resolution.py**: This script loads a video file named "output2.mp4"
  using the moviepy library and prints its resolution (width and height).
- **video_encoding_comparison.py**: This script compares the performance of CPU
  and GPU video encoding using FFmpeg by measuring the encoding time for both
  methods, calculating the average encoding times, and providing a comparison of
  the performance between CPU and GPU.

### System Utilities
- **anthropic_claude_chat.py**: The ClaudeChat application provides a graphical
  user interface for interacting with the Anthropic Claude AI model, allowing
  users to have conversations, upload and analyze files, and manage conversation
  history.
- **anthropic_claude_chat_for_linux.py**: The ClaudeChat application provides a
  graphical user interface for interacting with the Claude AI model from
  Anthropic, allowing users to have conversations, upload files for analysis,
  and manage conversation history.
- **disk-space-alert-service.py**: This script implements a Windows service that
  monitors disk space on local drives and sends email alerts when available
  space falls below a configured threshold.
- **disksizeinfo.py**: This script retrieves and displays the available free
  space on the C: and D: drives, as well as the CPU usage statistics for each
  CPU core, including user, system, and idle percentages.
- **convert_audio_to_text.py**: This script provides a graphical user interface
  that allows users to convert audio files (in .m4a format) to text using the
  Google Cloud Speech-to-Text API, with options to choose the save location for
  the output text file, enable automatic punctuation and profanity filtering,
  and support for the Hebrew language.
- **get_hostname_nbtstat.py**: This script performs a network scan on the local
  network to gather information about active devices, including their IP
  addresses, hostnames, MAC addresses, and device types, and writes the
  collected data to a file named 'network_scan_results.txt'.
- **system_discovery.py**: This script collects and displays various system
  information such as the operating system, machine architecture, hostname, IP
  address, CPU cores, and total RAM by utilizing the platform, socket, and
  psutil modules.
- **get_calendar_events.py**: This script authenticates a user with Microsoft
  Graph API using MSAL, retrieves the user's calendars and their events for the
  next 365 days, and displays information about the calendars and events.
- **get_calendar_events_for_everyone.py**: This script authenticates the user
  using Microsoft Graph API, retrieves their calendar events for the next 7
  days, and prints the subject, start time, and end time for each event.
- **get_calendar_permissions.py**: This script retrieves calendars and their
  permissions for a user from the Microsoft Graph API using Azure AD
  authentication, and it prints the calendar names, IDs, and permission details
  for each calendar.
- **GraphServiceClient.py**: This script retrieves a Microsoft user's calendar
  information, including upcoming holidays and all-day events for the next year,
  by authenticating with the Microsoft Graph API and fetching the necessary
  data.
- **network_analyzer.py**: This script provides a graphical user interface for
  real-time network traffic monitoring and detection of suspicious activities
  such as port scans, large data transfers, and excessive DNS queries, utilizing
  the Scapy library for packet capture and analysis and PyQt5 for the GUI.
- **network_monitor.py**: This script captures and analyzes network traffic on
  specified network interfaces to detect

Copyright (c) [2024] [Eran Gross]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.