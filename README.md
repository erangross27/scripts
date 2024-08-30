```markdown
# Python Scripts Collection

This repository contains a diverse collection of Python scripts for various tasks, including image and video processing, system monitoring, network analysis, quantum computing demonstrations, calendar management with Microsoft Graph API, and more.

## Contents

### Image Processing
- **captureImage.py**: This script captures an image from the default camera and saves it to the specified output directory with a unique filename based on the current date and time.
- **compress_image_to_small_size.py**: This script provides a graphical user interface for compressing JPEG images, allowing users to compress either a single image file or all images in a folder with adjustable compression quality, input/output path selection, and real-time quality adjustment display.
- **convert_image_to_doc.py**: This script provides a graphical user interface that allows users to convert image files to text documents using Google Cloud Vision API's optical character recognition (OCR) capabilities, with the extracted text formatted right-to-left and saved as a Microsoft Word document.
- **convert_svg_to_diffrent_images_format.py**: This script provides a graphical user interface for converting SVG files to raster image formats like PNG, JPG, and BMP, allowing users to select an input SVG file, choose an output format and location, set the desired resolution, and perform the conversion.
- **extract_text_from_image_regular.py**: This script provides a graphical user interface (GUI) application that allows users to extract text from images using the Google Cloud Vision API, and save the extracted text as either a TXT or CSV file.
- **extract_text_from_image_tables.py**: This script provides a graphical user interface (GUI) application that allows users to extract text from images using the Google Cloud Vision API, process the extracted text to separate names and IDs, and save the processed data as either a TXT or CSV file.
- **watermar_detection.py**: This script provides a graphical user interface for detecting watermarks in images and videos using a YOLOv5 model, allowing users to load custom models, process individual files, and save the output with detected watermarks highlighted.
- **inpainting.py**: This script implements a graphical user interface (GUI) application that utilizes machine learning models for detecting and removing watermarks from images and videos.
- **image_mover.py**: This script creates a graphical user interface (GUI) application using PyQt5 that allows users to move image files from a source directory to a destination directory.

### Video Processing
- **convert_mp4_codec_and_resolution_for_tv.py**: This script creates a graphical user interface (GUI) application that allows users to convert video files using FFmpeg, with options to select the source video, destination folder, video codec, and output resolution, while displaying the conversion progress.
- **convert_youtube_to_download_multiple_movies_and_music.py**: This script provides a graphical user interface for downloading and converting YouTube videos to MP3 or MP4 format, allowing batch processing, custom save locations, and multithreaded operations.
- **create_movie_clip_from_images_and_sound.py**: This script creates a video slideshow from a directory of images with a repeating background sound.
- **extract_frames_from_video.py**: This script provides a graphical user interface for extracting frames from multiple video files, allowing users to select videos, choose an output folder, and specify extraction parameters such as extracting every N frames or a maximum number of frames per video.
- **get_clip_resolution.py**: This script loads a video file named "output2.mp4" using the moviepy library and prints its resolution (width and height).

### System Utilities
- **anthropic_claude_chat.py**: The ClaudeChat application provides a graphical user interface for interacting with the Anthropic Claude AI model, allowing users to have conversations, upload and analyze files, and manage conversation history.
- **anthropic_claude_chat_for_linux.py**: The ClaudeChat application provides a graphical user interface for interacting with the Claude AI model from Anthropic, allowing users to have conversations, upload files for analysis, and manage conversation history.
- **disk-space-alert-service.py**: This script implements a Windows service that monitors disk space on local drives and sends email alerts when available space falls below a configured threshold.
- **disksizeinfo.py**: This script retrieves and displays the available free space on the