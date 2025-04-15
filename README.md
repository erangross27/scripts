# Scripts Directory Documentation

This repository contains various Python scripts and Jupyter notebooks organized by functionality.

## Table of Contents

- [Root Scripts](#root-scripts)
- [file_management](#file_management)
- [healthcare](#healthcare)
- [image_processing](#image_processing)
- [machine_learning](#machine_learning)
- [miscellaneous](#miscellaneous)
- [network monitor](#network monitor)
- [network monitor/config](#network monitor-config)
- [network monitor/models](#network monitor-models)
- [network monitor/utils](#network monitor-utils)
- [quantum_computing](#quantum_computing)
- [speech_to_text](#speech_to_text)
- [system_utilities](#system_utilities)
- [video_processing](#video_processing)
- [video_processing/youtube_downloader](#video_processing-youtube_downloader)

## Root Scripts


### compress_pdf_file.py

**Path:** `file_management\compress_pdf_file.py`

**Description:**
PDF Compressor

This script provides a graphical user interface for compressing PDF files using Ghostscript.
It allows users to select input and output files, and displays a progress bar during compression.

Features:
- File selection for input and output PDFs
- Progress bar to show compression status
- Multithreaded compression to keep the GUI responsive
- Estimated time calculation based on file size
- Error handling for common issues (e.g., missing Ghostscript)

Dependencies:
- subprocess
- tkinter
- os
- threading
- time

Note: This script requires Ghostscript to be installed and accessible in the system PATH.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.1 KB
- Lines of code: 111 (of 137 total)

**Functions:**
- `compress_pdf`: Compress pdf based on input file path, output file path, power
- `estimate_time`: Estimate time based on file size
- `update_progress`: Updates progress based on process, input file, output file, progress bar, compress button
- `select_file`: Select file based on entry, save
- `compress_file`: Compress file
- `main`: Main

**Dependencies:**
- tkinter

### numbering_pdf.py

**Path:** `file_management\numbering_pdf.py`

**Description:**
PDF Page Numberer

This script provides a graphical user interface for adding page numbers to PDF documents.
It allows users to open a PDF file, customize the appearance and position of page numbers,
preview the changes, and save the numbered PDF.

Features:
- Open and preview PDF files
- Customize page number position (left, center, right)
- Set page number color
- Adjust footer offset
- Set starting page number
- Change font size
- Adjust horizontal and vertical offsets
- Preview changes in real-time
- Process and save the numbered PDF

Dependencies:
- PyQt5: For creating the graphical user interface
- PyMuPDF (fitz): For PDF manipulation

Usage:
Run the script and use the GUI to open a PDF, adjust settings, and save the numbered PDF.

Note: This script requires PyQt5 and PyMuPDF to be installed.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 12.1 KB
- Lines of code: 238 (of 323 total)

**Classes:**
- `ColorIndicator`: Represents a color indicator
  - Methods:
    - `__init__`: Special method __init__
    - `setColor`: Setcolor based on color
    - `paintEvent`: Paintevent based on event
- `PDFNumberer`: Represents a p d f numberer
  - Methods:
    - `__init__`: Special method __init__
    - `initUI`: Initui
    - `select_color`: Select color
    - `open_pdf`: Open pdf
    - `update_preview`: Updates preview
    - `process_pdf`: Process pdf

**Dependencies:**
- PyQt5
- fitz

### breast_cancer_detector.py

**Path:** `healthcare\breast_cancer_detector.py`

**Description:**
This script handles breast cancer detector that processes data, performs numerical operations.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.6 KB
- Lines of code: 97 (of 136 total)

**Functions:**
- `main`: Main

**Classes:**
- `BreastCancerDetector`: Represents a breast cancer detector
  - Methods:
    - `__init__`: Special method __init__
    - `load_and_prepare_data`: Load and prepare the breast cancer dataset
    - `train_model`: Train the machine learning model
    - `predict_single_case`: Predict for a single case
    - `save_model`: Save the trained model
    - `load_model`: Load a trained model

**Dependencies:**
- joblib
- numpy
- pandas
- sklearn

### captureImage.py

**Path:** `image_processing\captureImage.py`

**Description:**
This script implements captureImage functionality.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 1.5 KB
- Lines of code: 37 (of 54 total)

**Functions:**
- `capture_image`: Captures an image from the default camera and saves it to the specified output directory

**Dependencies:**
- cv2

### compress_image_to_small_size.py

**Path:** `image_processing\compress_image_to_small_size.py`

**Description:**
Image Compressor GUI Application

This script provides a graphical user interface for compressing JPEG images.
It allows users to compress either a single image file or all images in a folder.
The application uses PyQt5 for the GUI and Pillow for image processing.

Features:
- Compress single JPEG image or all JPEG images in a folder
- Adjustable compression quality (1-100)
- Input and output path selection via file dialogs
- Real-time quality adjustment display
- Compression progress and results displayed in the GUI

Usage:
Run the script to launch the GUI application. Select the input (file or folder),
choose the output location, adjust the quality as needed, and click "Compress"
to start the compression process.

Dependencies:
- os
- sys
- PIL (Pillow)
- PyQt5

Classes:
- ImageCompressorGUI: Main application window and logic

Functions:
- compress_image: Compresses a single image file
- compress_images_in_folder: Compresses all JPEG images in a folder


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 8.4 KB
- Lines of code: 194 (of 236 total)

**Functions:**
- `compress_image`: Compress image based on image path, output path, quality
- `compress_images_in_folder`: Compress images in folder based on folder path, output folder path, quality

**Classes:**
- `ImageCompressorGUI`: Represents a image compressor g u i
  - Methods:
    - `__init__`: Special method __init__
    - `initUI`: Initui
    - `setup_radio_buttons`: Setup radio buttons based on layout
    - `setup_input_output`: Setup input output based on layout
    - `setup_quality_slider`: Setup quality slider based on layout
    - `setup_compress_button`: Setup compress button based on layout
    - `setup_output_text`: Setup output text based on layout
    - `clear_paths`: Clear paths
    - `browse_input`: Browse input
    - `browse_output`: Browse output
    - `update_quality_label`: Updates quality label based on value
    - `compress_images`: Compress images

**Dependencies:**
- PIL
- PyQt5

### convert_image_to_doc.py

**Path:** `image_processing\convert_image_to_doc.py`

**Description:**
This script provides a graphical user interface for converting image files to text documents using Google Cloud Vision API.

The program allows users to select an image file, process it using optical character recognition (OCR),
and save the extracted text as a Microsoft Word document (.docx). The text is formatted right-to-left
to accommodate languages that are written in this direction.

Key features:
1. GUI for easy interaction
2. Image selection via file dialog
3. Progress bar to track conversion progress
4. Automatic formatting of text (right-to-left, right-aligned)
5. Saving output as a Word document

Dependencies:
- google-cloud-vision
- python-docx
- tkinter

Note: This script requires a valid Google Cloud Vision API key (google.json) in the same directory.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.2 KB
- Lines of code: 94 (of 137 total)

**Functions:**
- `process_image`: Process image based on image path, progress var, window, progress bar
- `create_gui`: Creates gui

**Dependencies:**
- docx
- google
- tkinter

### convert_svg_to_diffrent_images_format.py

**Path:** `image_processing\convert_svg_to_diffrent_images_format.py`

**Description:**
SVG Converter

This script provides a graphical user interface (GUI) for converting SVG files to raster image formats
(PNG, JPG, BMP) using PyQt5. The application allows users to select an input SVG file, choose an output
format and location, set the desired resolution, and perform the conversion.

Key features:
- Select input SVG file
- Choose output format (PNG, JPG, BMP)
- Set custom resolution
- Automatically detect and set resolution from input SVG
- Convert SVG to selected raster format

Dependencies:
- PyQt5
- sys
- os

Usage:
Run the script to launch the GUI application. Select an input SVG file, choose the output format and
location, adjust the resolution if needed, and click the "Convert" button to perform the conversion.

Classes:
- SVGConverter: Main application window class that handles the UI and conversion process.

Note: This script must be run in an environment with PyQt5 installed.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 6.7 KB
- Lines of code: 142 (of 181 total)

**Classes:**
- `SVGConverter`: Converts s v g
  - Methods:
    - `__init__`: Special method __init__
    - `initUI`: Initui
    - `create_input_layout`: Creates input layout based on label text
    - `create_resolution_layout`: Creates resolution layout
    - `select_input`: Select input
    - `select_output`: Select output
    - `update_resolution_from_svg`: Updates resolution from svg based on file name
    - `update_output_suffix`: Updates output suffix
    - `convert_svg`: Converts svg

**Dependencies:**
- PyQt5

### convertor.py

**Path:** `image_processing\convertor.py`

**Description:**
This script implements convertor functionality that processes images.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 6.3 KB
- Lines of code: 108 (of 151 total)

**Classes:**
- `ImageConverter`: Converts image
  - Methods:
    - `__init__`: Special method __init__
    - `select_source`: Select source
    - `select_destination`: Select destination
    - `update_convert_button`: Updates convert button
    - `convert_image`: Converts image

**Dependencies:**
- PIL
- PyQt5

### copy_all_images_from_sub_folders.py

**Path:** `image_processing\copy_all_images_from_sub_folders.py`

**Description:**
This script handles copy all images from sub folders.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 1.7 KB
- Lines of code: 36 (of 56 total)

**Functions:**
- `main`: Main

### extract_text_from_image_regular.py

**Path:** `image_processing\extract_text_from_image_regular.py`

**Description:**
This script provides a GUI application for extracting text from images using Google Cloud Vision API.

The application allows users to:
1. Select an image file
2. Extract text from the selected image
3. Save the extracted text as either a TXT or CSV file

Key components:
- extract_text_from_image: Extracts text from an image using Google Cloud Vision API
- save_to_file: Saves extracted text to a file (TXT or CSV)
- select_image_path: Opens a file dialog for selecting an image
- convert_and_save: Extracts text from the selected image and saves it to a file
- main: Sets up the GUI and runs the application

Requirements:
- Google Cloud Vision API credentials (google.json file in the same directory as the script)
- google-cloud-vision library
- tkinter library

Usage:
Run the script to open the GUI. Select an image, choose the output file type (TXT or CSV),
and click 'Convert' to extract and save the text.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.2 KB
- Lines of code: 94 (of 130 total)

**Functions:**
- `extract_text_from_image`: Extract text from image based on image path, delimiter
- `save_to_file`: Save to file based on data, file path, file type
- `select_image_path`: Select image path based on entry
- `convert_and_save`: Converts and save based on entry, file type var
- `main`: Main

**Dependencies:**
- google
- tkinter

### extract_text_from_image_tables.py

**Path:** `image_processing\extract_text_from_image_tables.py`

**Description:**
This script provides a GUI application for extracting text from images using Google Cloud Vision API.

The application allows users to:
1. Select an image file
2. Extract text from the image using Google Cloud Vision API
3. Process the extracted text to separate names and IDs
4. Save the processed data as either a TXT or CSV file

Key components:
- extract_text_from_image: Uses Google Cloud Vision API to extract text from an image
- save_to_file: Saves processed data to either a TXT or CSV file
- select_image_path: Opens a file dialog for image selection
- convert_and_save: Extracts text, processes it, and saves to a file
- main: Sets up the GUI using tkinter

Requirements:
- Google Cloud Vision API credentials (google.json file in the same directory as the script)
- Required Python packages: google-cloud-vision, tkinter

Usage:
Run the script and use the GUI to select an image, choose the output file type,
and convert the image text to a structured format.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.1 KB
- Lines of code: 95 (of 151 total)

**Functions:**
- `extract_text_from_image`: Extract text from image based on image path, delimiter
- `save_to_file`: Save to file based on data, file path, file type
- `select_image_path`: Select image path based on entry
- `convert_and_save`: Converts and save based on entry, file type var
- `main`: Main

**Dependencies:**
- google
- tkinter

### image_brightener_gui.py

**Path:** `image_processing\image_brightener_gui.py`

**Description:**
This script handles image brightener gui that performs numerical operations.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 6.3 KB
- Lines of code: 154 (of 199 total)

**Functions:**
- `main`: Main

**Classes:**
- `ImageBrightener`: Represents a image brightener
  - Methods:
    - `__init__`: Special method __init__
    - `browse_input`: Browse input
    - `browse_output`: Browse output
    - `update_brightness`: Updates brightness
    - `update_preview`: Updates preview
    - `brighten_image`: Brighten image based on img
    - `process_image`: Process image

**Dependencies:**
- PyQt5
- cv2
- numpy

### image_mover.py

**Path:** `image_processing\image_mover.py`

**Description:**
Image Mover Application

This script creates a PyQt5-based GUI application for moving image files from a source directory
to a destination directory. The application allows users to select source and destination 
directories through a graphical interface and then move all image files (with extensions
.jpg, .jpeg, .png, .gif, .bmp) from the source to the destination.

Features:
- Select source and destination directories via GUI
- Move image files between directories
- Handle filename conflicts in the destination directory
- Simple and intuitive user interface

Usage:
Run this script to launch the Image Mover application. Use the buttons to select directories
and initiate the image moving process.

Dependencies:
- PyQt5
- os
- shutil


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.5 KB
- Lines of code: 90 (of 129 total)

**Classes:**
- `ImageMover`: Represents a image mover
  - Methods:
    - `__init__`: Special method __init__
    - `initUI`: Initui
    - `selectSourceDir`: Selectsourcedir
    - `selectDestDir`: Selectdestdir
    - `moveImages`: Moveimages

**Dependencies:**
- PyQt5

### inpainting.py

**Path:** `image_processing\inpainting.py`

**Description:**
Watermark Detection and Inpainting Application

This script implements a graphical user interface (GUI) application for detecting
and removing watermarks from images and videos using machine learning models.

Key Features:
1. YOLOv5 model for watermark detection
2. Stable Diffusion Inpainting model for watermark removal
3. Support for processing both images and videos
4. Real-time progress tracking and logging
5. Intermediate frame saving for video processing

The application allows users to:
- Load a custom YOLOv5 model for watermark detection
- Select input images or videos for processing
- Choose output locations for processed files
- View progress and logs in real-time
- Save intermediate frames during video processing for analysis

Dependencies:
- torch
- cv2
- numpy
- tkinter
- logging
- threading
- diffusers
- PIL

Usage:
Run this script to launch the GUI application. Use the interface to load models,
select input/output files, and process images or videos for watermark removal.

Note: Ensure all required dependencies are installed and CUDA is available
for optimal performance when processing large files or videos.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 25.4 KB
- Lines of code: 457 (of 627 total)

**Classes:**
- `WatermarkDetectionApp`: Represents a watermark detection app
  - Methods:
    - `__init__`: Special method __init__
    - `create_widgets`: Creates widgets
    - `download_and_load_inpainting_model`: Download and load inpainting model
    - `inpaint`: Inpaint based on prompt, image, mask image
    - `browse_model`: Browse model
    - `load_watermark_model`: Load watermark model
    - `browse_input`: Browse input
    - `browse_output`: Browse output
    - `start_processing`: Start processing
    - `process_file`: Process file
    - `process_image`: Process image based on input path, output path
    - `save_intermediate_frame`: Save intermediate frame based on frame, frame number
    - `process_video`: Process video based on input path, output path
    - `detect_and_mark_watermark`: Detect and mark watermark based on img
    - `visualize_mask`: Visualize mask based on img, mask
    - `inpaint_image`: Inpaint image based on img, mask, prompt, negative prompt, num inference steps, guidance scale, strength, seed
    - `resize_and_pad`: Resize and pad based on img, mask, size
    - `update_log`: Updates log based on message
- `GUILogHandler`: Handles g u i log operations
  - Methods:
    - `__init__`: Special method __init__
    - `emit`: Emit based on record

**Dependencies:**
- PIL
- cv2
- diffusers
- huggingface_hub
- numpy
- tkinter
- torch

### organize_dataset.py

**Path:** `image_processing\organize_dataset.py`

**Description:**
This script handles organize dataset.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 3.3 KB
- Lines of code: 55 (of 79 total)

**Functions:**
- `organize_dataset`: Organize a dataset by splitting it into training and validation sets

### shutterstock_gui.py

**Path:** `image_processing\shutterstock_gui.py`

**Description:**
This script handles shutterstock gui.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 9.4 KB
- Lines of code: 210 (of 263 total)

**Functions:**
- `main`: Main

**Classes:**
- `UploaderWorker`: Represents a uploader worker
  - Methods:
    - `__init__`: Special method __init__
    - `process_image`: Process a single image with error handling
    - `run`: Main worker thread execution
- `MainWindow`: Represents a main window
  - Methods:
    - `__init__`: Special method __init__
    - `initUI`: Initialize the user interface
    - `create_widgets`: Create all UI widgets
    - `setup_status_table`: Setup the status table configuration
    - `add_widgets_to_layout`: Add all widgets to the main layout
    - `browse_folder`: Handle folder selection
    - `start_upload`: Start the upload process
    - `connect_worker_signals`: Connect all worker signals to their handlers
    - `toggle_buttons`: Toggle button states
    - `update_progress`: Update progress bar and status message
    - `update_status_table`: Update the status table with new information
    - `refresh_status`: Refresh the status of all uploads
    - `update_status_in_table`: Update a specific row in the status table
    - `log_message`: Add a message to the log display
    - `upload_finished`: Handle upload completion

**Dependencies:**
- PyQt5
- shutterstock_uploader

### shutterstock_uploader.py

**Path:** `image_processing\shutterstock_uploader.py`

**Description:**
This script handles shutterstock uploader that makes HTTP requests.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 10.3 KB
- Lines of code: 222 (of 273 total)

**Classes:**
- `ShutterstockAutoUploader`: Represents a shutterstock auto uploader
  - Methods:
    - `__init__`: Special method __init__
    - `setup_logging`: Setup logging configuration
    - `load_keyword_blacklist`: Load blacklisted keywords
    - `add_delay`: Add delay for rate limiting
    - `encode_image`: Encode image to base64
    - `analyze_image_with_claude`: Analyze image using Claude AI
    - `validate_metadata`: Validate metadata before submission
    - `submit_to_shutterstock`: Submit image and metadata to Shutterstock
    - `handle_api_error`: Handle API errors with specific responses
    - `check_submission_status`: Check the status of a submitted image

**Dependencies:**
- anthropic
- dotenv
- requests

### test_cuda.py

**Path:** `image_processing\test_cuda.py`

**Description:**
This script contains test cases for cuda.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 0.3 KB
- Lines of code: 11 (of 13 total)

**Dependencies:**
- torch

### update_meta_data.py

**Path:** `image_processing\update_meta_data.py`

**Description:**
This script handles update meta data that processes images.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 21.8 KB
- Lines of code: 470 (of 591 total)

**Functions:**
- `main`: Main

**Classes:**
- `MetadataWorker`: Represents a metadata worker
  - Methods:
    - `__init__`: Special method __init__
    - `run`: Run
    - `stop`: Stop
- `MainWindow`: Represents a main window
  - Methods:
    - `__init__`: Special method __init__
    - `initUI`: Initui
    - `select_folder`: Select folder
    - `start_processing`: Start processing
    - `stop_processing`: Stop processing
    - `update_progress`: Updates progress based on value
    - `update_log`: Updates log based on message
    - `processing_finished`: Processing finished
- `LocalMetadataUpdater`: Represents a local metadata updater
  - Methods:
    - `__init__`: Special method __init__
    - `_setup_apis`: Set up API clients
    - `process_folder`: Process all images in the folder
    - `process_single_image`: Process a single image
    - `_resize_image_for_api`: Resize image to meet API requirements while maintaining aspect ratio and size <5MB
    - `_analyze_image`: Analyze image using Anthropic API
    - `_normalize_category`: Try to normalize the category returned by the AI to one from the valid list
    - `_parse_analysis_response`: Parse the AI response into structured metadata
    - `_update_local_metadata`: Update local image EXIF metadata

**Dependencies:**
- PIL
- PyQt5
- anthropic
- piexif
- shlex
- win32file

### update_meta_data_pro.py

**Path:** `image_processing\update_meta_data_pro.py`

**Description:**
This script handles update meta data pro.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 24.6 KB
- Lines of code: 470 (of 607 total)

**Functions:**
- `write_metadata_with_exiftool`: Writes metadata to image file using ExifTool, targeting IPTC and XMP fields for stock agencies
- `refine_description_with_ai`: Uses Anthropic's Claude to refine or generate a description for the image
- `suggest_keywords_with_ai`: Uses Anthropic's Claude to suggest additional relevant keywords based on the description
- `main`: Main
- `run_cli_version`: Run cli version

**Classes:**
- `MetadataEditorGUI`: Represents a metadata editor g u i
  - Methods:
    - `__init__`: Special method __init__
    - `browse_image`: Browse image
    - `load_image_preview`: Load image preview based on image path
    - `load_existing_metadata`: Load existing metadata based on image path
    - `toggle_ai_buttons`: Toggle ai buttons based on checked
    - `refine_description`: Refine description
    - `suggest_keywords`: Suggest keywords
    - `check_input_validity`: Check input validity
    - `save_metadata`: Save metadata

**Dependencies:**
- PyQt5
- anthropic

### watermar_detection.py

**Path:** `image_processing\watermar_detection.py`

**Description:**
Watermark Detection Application

This application provides a graphical user interface for detecting watermarks in images and videos using a YOLOv5 model.

Features:
- Load a custom YOLOv5 model for watermark detection
- Process individual images or video files
- Display processing progress and log information
- Save processed images/videos with detected watermarks highlighted

The application uses PyTorch for the deep learning model, OpenCV for image and video processing,
and Tkinter for the graphical user interface.

Usage:
1. Select a YOLOv5 model file (.pt)
2. Choose an input image or video file
3. Specify an output file location
4. Click "Process File" to start the watermark detection

The application will display progress and log information during processing.
Detected watermarks are highlighted with green rectangles in the output.

Classes:
- WatermarkDetectionApp: Main application class handling the GUI and processing logic
- GUILogHandler: Custom logging handler to update the GUI log display

Note: This application requires PyTorch, OpenCV, and other dependencies to be installed.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 10.9 KB
- Lines of code: 228 (of 298 total)

**Classes:**
- `WatermarkDetectionApp`: Represents a watermark detection app
  - Methods:
    - `__init__`: Special method __init__
    - `create_widgets`: Creates widgets
    - `browse_model`: Browse model
    - `load_model`: Load model
    - `browse_input`: Browse input
    - `browse_output`: Browse output
    - `start_processing`: Start processing
    - `process_file`: Process file
    - `process_image`: Process image based on input path, output path
    - `process_video`: Process video based on input path, output path
    - `detect_watermark`: Detect watermark based on img
    - `update_log`: Updates log based on message
- `GUILogHandler`: Handles g u i log operations
  - Methods:
    - `__init__`: Special method __init__
    - `emit`: Emit based on record

**Dependencies:**
- PIL
- cv2
- numpy
- tkinter
- torch
- tqdm

### mnist_cuda.py

**Path:** `machine_learning\mnist_cuda.py`

**Description:**
MNIST Digit Classification using Convolutional Neural Network

This script implements a Convolutional Neural Network (CNN) to classify handwritten digits
from the MNIST dataset using PyTorch. It includes the following main components:

1. Data loading and preprocessing using torchvision
2. Definition of a CNN architecture (Net class)
3. Training and testing functions
4. Model training loop with performance evaluation

The script uses CUDA if available, otherwise falls back to CPU computation.
It trains the model for 10 epochs and prints training progress, test set accuracy,
and total training time.

Dependencies:
- torch
- torchvision
- time

Usage:
Run the script to train and evaluate the model on the MNIST dataset.
The script will automatically download the dataset if not already present.

Note: Adjust hyperparameters like batch size, learning rate, and number of epochs as needed.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.5 KB
- Lines of code: 110 (of 139 total)

**Functions:**
- `train`: Train based on model, device, train loader, optimizer, epoch
- `test`: Test based on model, device, test loader

**Classes:**
- `Net`: Represents a net
  - Methods:
    - `__init__`: Special method __init__
    - `forward`: Forward based on x

**Dependencies:**
- torch
- torchvision

### mnist_gpu_comparison.py

**Path:** `machine_learning\mnist_gpu_comparison.py`

**Description:**
This script demonstrates the training and testing of a Convolutional Neural Network (CNN) on the MNIST dataset using PyTorch.
It compares the performance of training on CPU versus GPU (if available) and provides metrics on execution time and memory usage.

The script includes the following main components:
1. A simple CNN model definition (Net class)
2. Data loading and preprocessing for the MNIST dataset
3. A training and testing function (train_and_test)
4. Functions to print GPU and CPU memory usage
5. Execution of the training process on both CPU and GPU (if available)
6. Comparison of training times and calculation of GPU speedup over CPU

Requirements:
- PyTorch
- torchvision
- psutil
- GPUtil

The script will automatically use CUDA if available, otherwise it will default to CPU.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 6.1 KB
- Lines of code: 137 (of 174 total)

**Functions:**
- `train_and_test`: Train and test based on device, num epochs
- `print_gpu_memory`: Print gpu memory
- `print_cpu_memory`: Print cpu memory

**Classes:**
- `Net`: Represents a net
  - Methods:
    - `__init__`: Special method __init__
    - `forward`: Forward based on x

**Dependencies:**
- GPUtil
- psutil
- torch
- torchvision

### train_watermark_yolov5.py

**Path:** `machine_learning\train_watermark_yolov5.py`

**Description:**
YOLOv5 Training Script

This script sets up and runs a training process for YOLOv5 object detection model.
It includes the following main components:

1. Importing necessary libraries and YOLOv5 modules
2. Defining hyperparameters for YOLOv5 training
3. Setting up command-line argument parsing for various training options
4. Creating a data.yaml file with dataset information
5. Initializing device and callbacks
6. Running the training process

The script is designed to be run from the command line with various optional arguments
to customize the training process. It uses a pre-defined set of hyperparameters and
allows for further customization through command-line options.

Usage:
    python script_name.py [arguments]

For a full list of available arguments, run:
    python script_name.py --help


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 7.7 KB
- Lines of code: 119 (of 145 total)

**Functions:**
- `main`: Main

**Dependencies:**
- torch
- train
- utils
- yaml

### cuda_matrix_multiplication.py

**Path:** `miscellaneous\cuda_matrix_multiplication.py`

**Description:**
This script handles cuda matrix multiplication that performs numerical operations.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.3 KB
- Lines of code: 97 (of 143 total)

**Functions:**
- `cpu_matrix_mul`: Cpu matrix mul based on a, b
- `gpu_matrix_mul`: Gpu matrix mul based on a, b, a gpu, b gpu, c gpu

**Dependencies:**
- numpy
- pycuda

### cuda_vector_add.py

**Path:** `miscellaneous\cuda_vector_add.py`

**Description:**
This script handles cuda vector add that performs numerical operations.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 2.3 KB
- Lines of code: 51 (of 85 total)

**Dependencies:**
- numpy
- pycuda

### discover_gpu_memory.py

**Path:** `miscellaneous\discover_gpu_memory.py`

**Description:**
This script handles discover gpu memory.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 1.9 KB
- Lines of code: 32 (of 55 total)

**Functions:**
- `get_intel_gpu_info`: Retrieves and displays information about the Intel GPU installed on the system

**Dependencies:**
- wmi

### discover_monitor_information.py

**Path:** `miscellaneous\discover_monitor_information.py`

**Description:**
This script handles discover monitor information.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 3.8 KB
- Lines of code: 83 (of 108 total)

**Functions:**
- `get_monitor_info_wmi`: Retrieve monitor information using Windows Management Instrumentation (WMI)
- `get_monitor_info_powershell`: Retrieve monitor information using PowerShell as a fallback method
- `main`: Main function to retrieve and display monitor information

**Dependencies:**
- wmi

### get_openai_model_list.py

**Path:** `miscellaneous\get_openai_model_list.py`

**Description:**
No documentation


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 2.0 KB
- Lines of code: 39 (of 57 total)

**Functions:**
- `list_openai_models`: Fetches and displays available OpenAI models

**Dependencies:**
- openai

### get_requirements.py

**Path:** `miscellaneous\get_requirements.py`

**Description:**
This script generates a requirements.txt file by analyzing Python files in the current directory.

It extracts import statements from each Python file, normalizes package names, filters out standard
library modules and Windows-specific modules (on non-Windows systems), and creates a requirements
file. Each entry in the requirements file includes the package name and the files that use it.

Functions:
- get_imports: Extracts import statements from a Python file.
- normalize_package_name: Normalizes package names (e.g., 'PIL' to 'Pillow').
- get_stdlib_modules: Returns a list of standard library modules.
- is_windows_specific: Checks if a package is Windows-specific.
- get_all_requirements: Main function to generate the requirements file.
- main: Entry point of the script.

Usage:
Run this script in the directory containing the Python files you want to analyze.
The generated requirements.txt file will be saved in the same directory.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.5 KB
- Lines of code: 96 (of 123 total)

**Functions:**
- `get_imports`: Retrieves imports based on file path
- `normalize_package_name`: Normalize package name based on package
- `get_stdlib_modules`: Retrieves stdlib modules
- `is_windows_specific`: Checks if windows specific based on package
- `get_all_requirements`: Retrieves all requirements based on output file
- `main`: Main

**Dependencies:**
- pkgutil

### matrix_multiplication_comparison.py

**Path:** `miscellaneous\matrix_multiplication_comparison.py`

**Description:**
This script compares the performance of Gaussian blur applied to an image using CPU and GPU.

The script performs the following operations:
1. Loads an image from a specified path.
2. Applies Gaussian blur to the image using both CPU and GPU (if available).
3. Measures and compares the execution time for both methods.
4. Prints memory usage statistics for CPU and GPU (if available).
5. Calculates and displays average execution times and performance speedup.

The comparison is run multiple times (default 3) to get more accurate average timings.

Functions:
- print_gpu_memory(): Prints GPU memory usage if available.
- print_cpu_memory(): Prints CPU memory usage.
- cpu_gaussian_blur(image, kernel_size): Applies Gaussian blur on CPU.
- gpu_gaussian_blur(image, kernel_size): Applies Gaussian blur on GPU.
- run_comparison(image_path, runs): Main function to compare CPU and GPU performance.

Usage:
Set the 'image_path' variable to the path of the image you want to process,
then run the script. The results will be printed to the console.

Requirements:
- numpy
- torch
- torchvision
- Pillow (PIL)
- psutil
- GPUtil

Note: GPU operations require CUDA-capable hardware and appropriate CUDA setup.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.4 KB
- Lines of code: 105 (of 138 total)

**Functions:**
- `print_gpu_memory`: Print gpu memory
- `print_cpu_memory`: Print cpu memory
- `cpu_gaussian_blur`: Cpu gaussian blur based on image, kernel size
- `gpu_gaussian_blur`: Gpu gaussian blur based on image, kernel size
- `run_comparison`: Run comparison based on image path, runs

**Dependencies:**
- GPUtil
- PIL
- numpy
- psutil
- torch
- torchvision

### organize_scripts.py

**Path:** `miscellaneous\organize_scripts.py`

**Description:**
This script handles organize scripts.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 3.1 KB
- Lines of code: 71 (of 85 total)

### password_hashing_comparison.py

**Path:** `miscellaneous\password_hashing_comparison.py`

**Description:**
This script compares the performance of password hashing using CPU and GPU.

It includes functions to:
- Print GPU and CPU memory usage
- Hash passwords using CPU and GPU
- Run a comparison between CPU and GPU hashing performance

The main function, run_comparison(), generates a set of sample passwords and
performs multiple runs of hashing using both CPU and GPU (if available).
It then calculates and prints the average time taken for each method and
compares their performance.

Dependencies:
- hashlib: For SHA-256 hashing
- torch: For GPU operations
- time: For timing the operations
- psutil: For CPU memory usage
- GPUtil: For GPU memory usage

Usage:
Run this script directly to perform the comparison with default parameters.
You can modify the parameters in the run_comparison() function call if needed.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.4 KB
- Lines of code: 97 (of 131 total)

**Functions:**
- `print_gpu_memory`: Print gpu memory
- `print_cpu_memory`: Print cpu memory
- `cpu_hash_passwords`: Cpu hash passwords based on passwords
- `gpu_hash_passwords`: Gpu hash passwords based on passwords
- `run_comparison`: Run comparison based on num passwords, password length, runs

**Dependencies:**
- GPUtil
- psutil
- torch

### prime_cpu_gpu_comparison.py

**Path:** `miscellaneous\prime_cpu_gpu_comparison.py`

**Description:**
This script compares the performance of CPU and GPU for finding prime numbers.

It uses NumPy and PyTorch to generate random numbers and perform calculations.
The script includes functions for prime number checking and finding on both CPU and GPU.
It also monitors and reports CPU and GPU memory usage during the process.

The main function, run_comparison(), performs multiple runs of prime number finding
on both CPU and GPU (if available), and reports the average execution times.

Dependencies:
- numpy
- torch
- time
- psutil
- GPUtil

Usage:
Run the script to perform the CPU-GPU comparison for prime number finding.
The comparison parameters (number size, maximum number, and number of runs)
can be adjusted in the run_comparison() function call at the end of the script.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.0 KB
- Lines of code: 122 (of 161 total)

**Functions:**
- `is_prime`: Checks if prime based on n
- `cpu_find_primes`: Cpu find primes based on numbers
- `gpu_is_prime`: Gpu is prime based on n
- `gpu_find_primes`: Gpu find primes based on numbers
- `print_gpu_memory`: Print gpu memory
- `print_cpu_memory`: Print cpu memory
- `run_comparison`: Run comparison based on size, max num, runs

**Dependencies:**
- GPUtil
- numpy
- psutil
- torch

### remove_versions_from_requirements.py

**Path:** `miscellaneous\remove_versions_from_requirements.py`

**Description:**
This script handles remove versions from requirements.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 2.3 KB
- Lines of code: 37 (of 58 total)

**Functions:**
- `remove_versions`: Remove version specifiers and comments from a requirements file

### setup_env.py

**Path:** `miscellaneous\setup_env.py`

**Description:**
This script handles setup env.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 7.0 KB
- Lines of code: 153 (of 200 total)

**Functions:**
- `main`: Main

**Classes:**
- `EnvironmentManager`: Manages environment
  - Methods:
    - `__init__`: Special method __init__
    - `set_windows_env_variable`: Set Windows environment variable using registry and broadcast change
    - `load_existing_config`: Load existing configuration if available
    - `save_config`: Save configuration to file
    - `get_user_input`: Get user input for required variables
    - `set_environment_variables`: Set all environment variables using the proven method
    - `create_download_folder`: Create the download folder if it doesn't exist

**Dependencies:**
- ctypes
- winreg

### setup_requirements.py

**Path:** `miscellaneous\setup_requirements.py`

**Description:**
This script handles setup requirements.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 2.5 KB
- Lines of code: 52 (of 71 total)

**Functions:**
- `extract_imports`: Extract import statements from a Python file
- `find_requirements`: Find all Python files and extract their requirements
- `generate_requirements_txt`: Generate requirements

### sort_cpu_gpu_comparison.py

**Path:** `miscellaneous\sort_cpu_gpu_comparison.py`

**Description:**
This script compares the performance of CPU and GPU sorting algorithms.

It uses NumPy for CPU sorting and PyTorch for GPU sorting. The script performs the following tasks:
1. Checks for CUDA availability and sets the device accordingly.
2. Prints information about the GPU if available.
3. Defines functions for CPU and GPU sorting.
4. Defines functions to print CPU and GPU memory usage.
5. Runs a comparison between CPU and GPU sorting:
   - Generates random data
   - Sorts the data using both CPU and GPU
   - Measures and reports the time taken for each method
   - Calculates and reports average times and speedup
   
The comparison is run multiple times with a large array to get a reliable performance measure.

Requirements:
- NumPy
- PyTorch
- psutil
- GPUtil

Note: GPU sorting will only be performed if CUDA is available.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 3.5 KB
- Lines of code: 94 (of 122 total)

**Functions:**
- `cpu_sort`: Cpu sort based on arr
- `gpu_sort`: Gpu sort based on arr
- `print_gpu_memory`: Print gpu memory
- `print_cpu_memory`: Print cpu memory
- `run_comparison`: Run comparison based on size, runs

**Dependencies:**
- GPUtil
- numpy
- psutil
- torch

### update_readme.py

**Path:** `miscellaneous\update_readme.py`

**Description:**
This script processes Python files in a directory, extracts their docstrings,
generates brief descriptions using the Anthropic API, and updates a README.md
file with these descriptions. It also manages a PostgreSQL database to track
processed files and avoid unnecessary reprocessing. The script ensures proper
setup of the database and handles the creation of necessary tables. It also
checks for and includes license information in the README.md file.

Key features:
- Processes Python files in the script's directory
- Extracts docstrings from Python files
- Uses Anthropic API to generate brief descriptions of scripts
- Updates README.md with script descriptions and license information
- Manages a PostgreSQL database to track processed files
- Handles database and user creation if they don't exist
- Calculates file hashes to detect changes

Dependencies:
- anthropic
- psycopg2
- hashlib
- subprocess

Environment variables:
- ANTHROPIC_API_KEY: API key for Anthropic
- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT: Database connection parameters

Usage:
Run the script directly to process files and update the README.md.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 10.5 KB
- Lines of code: 238 (of 287 total)

**Functions:**
- `create_db_and_user`: Create the database and user if they don't exist
- `get_db_connection`: Establish and return a connection to the database
- `ensure_db_setup`: Ensure the database, user, and necessary tables are set up
- `get_file_hash`: Calculate and return the MD5 hash of a file
- `is_file_processed`: Check if a file has already been processed by comparing its last modified time and hash
- `update_processed_file`: Update or insert a record for a processed file in the database
- `get_docstring`: Extract the docstring from a Python file
- `get_script_description`: Use Anthropic API to get a description of what the script does
- `get_license_filename`: Find the correct license filename in the directory
- `update_readme_content`: Update the README
- `main`: Main function to process Python files and update the README

**Dependencies:**
- anthropic
- psycopg2

### __init__.py

**Path:** `network monitor\__init__.py`

**Description:**
This script handles   init  .


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 0.0 KB
- Lines of code: 3 (of 4 total)

### anomaly_detector.py

**Path:** `network monitor\anomaly_detector.py`

**Description:**
This script handles anomaly detector that performs numerical operations.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.2 KB
- Lines of code: 76 (of 108 total)

**Classes:**
- `AnomalyDetector`: A class for detecting network traffic anomalies using machine learning
  - Methods:
    - `__init__`: Initialize the AnomalyDetector with a logger
    - `analyze_traffic`: Analyze network traffic for anomalies using machine learning
    - `_generate_anomaly_details`: Generate detailed information about detected anomalies

**Dependencies:**
- feature_extractor
- numpy

### __init__.py

**Path:** `network monitor\config\__init__.py`

**Description:**
This script handles   init  .


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 0.5 KB
- Lines of code: 21 (of 23 total)

**Dependencies:**
- feature_config
- whitelist_config

### feature_config.py

**Path:** `network monitor\config\feature_config.py`

**Description:**
This script handles feature config.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 1.1 KB
- Lines of code: 24 (of 26 total)

### whitelist_config.py

**Path:** `network monitor\config\whitelist_config.py`

**Description:**
This script handles whitelist config.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 1.0 KB
- Lines of code: 31 (of 44 total)

**Dependencies:**
- ipaddress

### feature_extractor.py

**Path:** `network monitor\feature_extractor.py`

**Description:**
This script handles feature extractor that processes data.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.1 KB
- Lines of code: 98 (of 128 total)

**Classes:**
- `FeatureExtractor`: A class for extracting features from network packets for machine learning analysis
  - Methods:
    - `__init__`: Initialize the FeatureExtractor with predefined feature names
    - `extract_features`: Extract features from a list of packets for machine learning analysis
    - `_extract_packet_features`: Extract features from a single packet

**Dependencies:**
- config
- pandas
- scapy

### interface_manager.py

**Path:** `network monitor\interface_manager.py`

**Description:**
This script handles interface manager.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.8 KB
- Lines of code: 101 (of 123 total)

**Classes:**
- `InterfaceManager`: Manages interface
  - Methods:
    - `__init__`: Special method __init__
    - `get_interfaces`: Retrieve a list of active network interfaces along with their IP addresses and netmasks
    - `get_subnet_mask`: Get the subnet mask for a given interface
    - `choose_interface`: Allow user to choose a network interface
    - `setup_interface`: Setup network interface either automatically or based on user choice

**Dependencies:**
- bidi
- netifaces
- psutil
- wmi

### logger_setup.py

**Path:** `network monitor\logger_setup.py`

**Description:**
This script handles logger setup.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 2.4 KB
- Lines of code: 37 (of 63 total)

**Classes:**
- `LoggerSetup`: A class to set up and manage a thread-safe logging system using a queue-based approach
  - Methods:
    - `__init__`: Initialize the logger setup with a queue, logger, and queue listener
    - `_setup_logger`: Configure and return a logger instance with queue handler
    - `_setup_queue_listener`: Set up and return a queue listener with stream handler for console output
    - `get_logger`: Return the configured logger instance
    - `stop_listener`: Stop the queue listener if it exists

### __init__.py

**Path:** `network monitor\models\__init__.py`

**Description:**
This script handles   init  .


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 0.2 KB
- Lines of code: 5 (of 7 total)

**Dependencies:**
- persistent_anomaly_detector

### persistent_anomaly_detector.py

**Path:** `network monitor\models\persistent_anomaly_detector.py`

**Description:**
This script handles persistent anomaly detector that processes data.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 3.1 KB
- Lines of code: 70 (of 84 total)

**Classes:**
- `PersistentAnomalyDetector`: Represents a persistent anomaly detector
  - Methods:
    - `__init__`: Special method __init__
    - `partial_fit`: Partially fit the model with new data
    - `predict`: Make predictions using the fitted model
    - `save_model`: Save the fitted model to a file
    - `load_model`: Load a previously saved model

**Dependencies:**
- joblib
- pandas
- sklearn

### network_monitor.py

**Path:** `network monitor\network_monitor.py`

**Description:**
This script handles network monitor.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 9.4 KB
- Lines of code: 136 (of 180 total)

**Functions:**
- `main`: Entry point of the script - parse arguments and start monitoring

**Classes:**
- `NetworkMonitor`: Main class for monitoring network traffic and detecting anomalies
  - Methods:
    - `__init__`: Special method __init__
    - `check_root_linux`: Check if script is running with root privileges on Linux systems
    - `run`: Main monitoring loop that captures and analyzes network traffic
    - `_log_results`: Log detected suspicious activities and anomalies
    - `_update_false_positives`: Track and handle potential false positive detections

**Dependencies:**
- anomaly_detector
- interface_manager
- logger_setup
- models
- packet_analyzer
- packet_capture

### packet_analyzer.py

**Path:** `network monitor\packet_analyzer.py`

**Description:**
This script handles packet analyzer.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 13.6 KB
- Lines of code: 242 (of 302 total)

**Classes:**
- `PacketAnalyzer`: Represents a packet analyzer
  - Methods:
    - `__init__`: Special method __init__
    - `_is_binary_or_encrypted`: Check if the data appears to be binary or encrypted
    - `_decode_payload`: Try multiple encodings to decode the payload
    - `analyze_traffic`: Analyze network traffic for suspicious activities
    - `_analyze_packets`: Analyze individual packets for suspicious behavior
    - `_check_payload_for_threats`: Check packet payload for potential threats with context
    - `_is_whitelisted`: Check if packet matches any whitelist patterns

**Dependencies:**
- ipaddress
- scapy

### packet_capture.py

**Path:** `network monitor\packet_capture.py`

**Description:**
This script handles packet capture.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 2.8 KB
- Lines of code: 81 (of 95 total)

**Classes:**
- `PacketCapture`: Represents a packet capture
  - Methods:
    - `__init__`: Special method __init__
    - `capture_packets_worker`: Capture packets worker based on interface, count, result queue
    - `capture_packets`: Capture packets based on interface, total count

**Dependencies:**
- scapy
- tqdm

### __init__.py

**Path:** `network monitor\utils\__init__.py`

**Description:**
This script handles   init  .


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 0.3 KB
- Lines of code: 12 (of 14 total)

**Dependencies:**
- network_utils
- packet_utils

### network_utils.py

**Path:** `network monitor\utils\network_utils.py`

**Description:**
This script provides utility functions for networks.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 0.6 KB
- Lines of code: 21 (of 25 total)

**Functions:**
- `resolve_ip`: Resolve an IP address to a hostname
- `is_private_ip`: Check if an IP address is private

### packet_utils.py

**Path:** `network monitor\utils\packet_utils.py`

**Description:**
This script provides utility functions for packets.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 1.0 KB
- Lines of code: 29 (of 33 total)

**Functions:**
- `is_inbound`: Check if a packet is inbound to the local network
- `get_packet_protocol`: Get the protocol of a packet
- `get_packet_ports`: Get source and destination ports of a packet

**Dependencies:**
- ipaddress
- scapy

### whitelist_manager.py

**Path:** `network monitor\whitelist_manager.py`

**Description:**
This script handles whitelist manager.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.6 KB
- Lines of code: 115 (of 134 total)

**Classes:**
- `WhitelistManager`: Manages whitelist
  - Methods:
    - `__init__`: Special method __init__
    - `is_whitelisted`: Check if a packet matches any whitelist rules
    - `is_whitelisted_port`: Check if a port is whitelisted
    - `_check_ip_whitelist`: Check if packet IPs are whitelisted
    - `_check_port_whitelist`: Check if packet ports are whitelisted
    - `_check_protocol_whitelist`: Check if packet protocol is whitelisted
    - `_check_time_based_whitelist`: Check if current time falls within whitelisted time windows
    - `_check_domain_whitelist`: Check if DNS query domain is whitelisted
    - `_check_broadcast_whitelist`: Check if broadcast packet should be whitelisted
    - `_check_multicast_whitelist`: Check if multicast packet should be whitelisted

**Dependencies:**
- config
- ipaddress
- scapy

### deutsch_jozsa_algorithm.py

**Path:** `quantum_computing\deutsch_jozsa_algorithm.py`

**Description:**
Deutsch-Jozsa Algorithm Implementation using IBM Quantum

This script implements the Deutsch-Jozsa algorithm using IBM Quantum's cloud-based quantum computers.
The Deutsch-Jozsa algorithm is designed to determine whether a given function is constant or balanced.

The script performs the following main steps:
1. Sets up the connection to IBM Quantum using an API token.
2. Defines the Deutsch-Jozsa circuit and a balanced oracle.
3. Creates and transpiles the circuit for the selected backend.
4. Runs the circuit on the least busy available quantum computer.
5. Retrieves and processes the results.
6. Visualizes the results using a histogram.

The script requires the IBM_QUANTUM_TOKEN environment variable to be set with a valid API token.

Dependencies:
- qiskit
- qiskit_ibm_runtime
- matplotlib
- os

Note: This script is designed for educational and demonstrative purposes.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 3.9 KB
- Lines of code: 78 (of 127 total)

**Functions:**
- `deutsch_jozsa_circuit`: Create a Deutsch-Jozsa circuit
- `balanced_oracle`: Balanced oracle

**Dependencies:**
- matplotlib
- qiskit
- qiskit_ibm_runtime

### quantum_key_cracking.py

**Path:** `quantum_computing\quantum_key_cracking.py`

**Description:**
Quantum Key Cracking using Grover's Algorithm

This script demonstrates the use of Grover's algorithm to crack a 3-bit secret key
using IBM's Qiskit framework and quantum computing services. It includes the following
main components:

1. Setup of IBM Quantum services using an API token.
2. Implementation of a custom oracle function for the 3-bit key.
3. Implementation of a diffuser function for 3 qubits.
4. Creation of a Grover's algorithm circuit for key cracking.
5. Execution of the quantum circuit on IBM's quantum simulator.
6. Analysis and visualization of the results.

The script uses a more complex oracle implementation to demonstrate a practical
application of Grover's algorithm in cryptography. It also includes error handling
for the API token and provides a detailed explanation of the results.

Requirements:
- Qiskit
- Matplotlib
- IBM Quantum account and API token

Usage:
Set the IBM_QUANTUM_TOKEN environment variable with your API token before running the script.
The secret key is set within the script and can be modified as needed.

Note: This is a demonstration and should not be used for actual cryptographic purposes.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.3 KB
- Lines of code: 95 (of 142 total)

**Functions:**
- `oracle`: Implement a more complex oracle for the given 3-bit key
- `diffuser`: Implement the diffuser for 3 qubits
- `grover_circuit`: Create a Grover's algorithm circuit for cracking a 3-bit key

**Dependencies:**
- matplotlib
- qiskit
- qiskit_ibm_runtime

### quantum_rng.py

**Path:** `quantum_computing\quantum_rng.py`

**Description:**
Quantum Random Number Generator

This script demonstrates the generation of random numbers using a quantum circuit
implemented with IBM Quantum services. It showcases the following functionality:

1. Setting up an IBM Quantum account using an API token.
2. Creating a quantum circuit to generate random numbers.
3. Executing the circuit on the least busy IBM Quantum backend.
4. Retrieving and interpreting the results as random numbers.
5. Providing an explanation of the quantum random number generation process.
6. Suggesting potential cybersecurity applications for the generated random numbers.

The script uses Qiskit and the IBM Quantum Runtime to interact with real quantum hardware.
It generates 4-bit random numbers (0-15) and displays them in both decimal and binary formats.

Requirements:
- IBM Quantum account and API token (set as IBM_QUANTUM_TOKEN environment variable)
- Qiskit and qiskit_ibm_runtime libraries

Note: This script is for educational purposes and demonstrates basic quantum computing concepts.
For production-level cryptographic applications, consult with cryptography experts and use
established cryptographic libraries and protocols.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 3.8 KB
- Lines of code: 58 (of 93 total)

**Functions:**
- `quantum_random_number`: Generate a random number using quantum circuit

**Dependencies:**
- qiskit
- qiskit_ibm_runtime

### readme_generator.py

**Path:** `readme_generator.py`

**Description:**
No documentation


**File Info:**
- Last modified: 2025-04-15 20:47:57
- Size: 18.4 KB
- Lines of code: 350 (of 417 total)

**Functions:**
- `parse_args`: No documentation

**Classes:**
- `ScriptAnalyzer`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `extract_docstring`: Extract the module-level docstring from a Python file
    - `extract_imports`: Extract imported modules from a Python file
    - `extract_functions_and_classes`: Extract top-level functions and classes with their docstrings
    - `get_file_stats`: Get file statistics: size, last modified, lines, code lines
    - `process_notebook`: Process Jupyter Notebook (
    - `update_file_docstrings`: Placeholder for updating missing docstrings in a Python file
    - `analyze_file`: Analyze a single file, return structured data
    - `should_exclude`: Determine if a directory should be excluded
    - `analyze_scripts`: Walk directory and analyze all Python and notebook files
    - `generate_readme_content`: Generate Markdown content for README files
    - `generate_readme`: Generate README

**Dependencies:**
- nbformat

### setup_requirements.py

**Path:** `setup_requirements.py`

**Description:**
This script handles setup requirements.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.3 KB
- Lines of code: 76 (of 111 total)

**Functions:**
- `extract_imports`: Extract import statements from a Python file
- `find_requirements`: Find all Python files and extract their requirements
- `generate_requirements_txt`: Generate requirements

### build_app.py

**Path:** `speech_to_text\build_app.py`

**Description:**
This script handles build app.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.3 KB
- Lines of code: 112 (of 150 total)

**Functions:**
- `build_executable`: Build executable

### transcription_app.py

**Path:** `speech_to_text\transcription_app.py`

**Description:**
This script handles transcription app.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 22.7 KB
- Lines of code: 535 (of 670 total)

**Functions:**
- `get_embedded_api_key`: Retrieves embedded api key
- `main`: Main

**Classes:**
- `ProofreadingDialog`: Represents a proofreading dialog
  - Methods:
    - `__init__`: Special method __init__
- `ProofreadingWorker`: Represents a proofreading worker
  - Methods:
    - `__init__`: Special method __init__
    - `run`: Run
- `TranscriptionWorker`: Represents a transcription worker
  - Methods:
    - `__init__`: Special method __init__
    - `format_transcript`: Format transcript based on text
    - `split_audio`: Split audio based on audio segment, max size mb
    - `run`: Run
- `TranscriptionApp`: Represents a transcription app
  - Methods:
    - `__init__`: Special method __init__
    - `toggle_maximize`: Toggle maximize
    - `copy_text`: Copy text
    - `init_ui`: Init ui
    - `mousePressEvent`: Mousepressevent based on event
    - `mouseMoveEvent`: Mousemoveevent based on event
    - `update_status`: Updates status based on text
    - `browse_file`: Browse file
    - `start_transcription`: Start transcription
    - `start_proofreading`: Start proofreading
    - `proofreading_complete`: Proofreading complete based on corrected text
    - `proofreading_error`: Proofreading error based on error message
    - `update_progress`: Updates progress based on status, value
    - `transcription_complete`: Transcription complete based on transcript
    - `save_transcript`: Save transcript
    - `transcription_error`: Transcription error based on error message

**Dependencies:**
- PyQt5
- openai
- pydub

### ai_security_service.py

**Path:** `system_utilities\ai_security_service.py`

**Description:**
This script handles ai security service.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.7 KB
- Lines of code: 146 (of 194 total)

**Functions:**
- `get_current_user`: Retrieves current user based on token
- `get_db`: Retrieves db
- `cache_response`: Cache response based on expire time

**Classes:**
- `User`: Represents a user
- `UserCreate`: Represents a user create
- `UserResponse`: Represents a user response

**Dependencies:**
- bcrypt
- fastapi
- jwt
- pydantic
- redis
- sqlalchemy
- uvicorn

### anthropic_claude_chat.py

**Path:** `system_utilities\anthropic_claude_chat.py`

**Description:**
No documentation


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 87.4 KB
- Lines of code: 1318 (of 1918 total)

### anthropic_claude_chat_for_linux.py

**Path:** `system_utilities\anthropic_claude_chat_for_linux.py`

**Description:**
No documentation


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 88.8 KB
- Lines of code: 1341 (of 1975 total)

### convert_audio_to_text.py

**Path:** `system_utilities\convert_audio_to_text.py`

**Description:**
Audio to Text Converter

This script provides a graphical user interface for converting audio files to text using Google Cloud Speech-to-Text API.

Features:
- Browse and select audio files (supports .m4a format)
- Choose save location for the output text file
- Convert audio to text with automatic punctuation and profanity filtering
- Supports Hebrew language (iw-IL)

Dependencies:
- os
- tkinter
- google.cloud.speech
- wave
- audioop
- pydub

Note: Requires a valid Google Cloud credentials file.

Usage:
1. Run the script
2. Use the GUI to select an audio file and save location
3. Enter a filename for the output
4. Click "Convert" to process the audio and generate text

The script handles audio format conversion (m4a to wav) and channel conversion (stereo to mono) automatically.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.0 KB
- Lines of code: 111 (of 156 total)

**Functions:**
- `browse_audio_file`: Browse audio file based on label
- `browse_save_location`: Browse save location based on label
- `convert_m4a_to_wav`: Converts m4a to wav based on audio file path
- `convert_stereo_to_mono`: Converts stereo to mono based on audio file path
- `convert_audio_to_text`: Converts audio to text based on audio file path, save location, filename
- `main`: Main

**Dependencies:**
- audioop
- google
- pydub
- tkinter
- wave

### disk-space-alert-service.py

**Path:** `system_utilities\disk-space-alert-service.py`

**Description:**
Disk Space Alert Service

This script implements a Windows service that monitors disk space on local drives
and sends email alerts when available space falls below a configured threshold.

Features:
- Runs as a Windows service
- Configurable check interval and minimum free space threshold
- Email alerts with customizable SMTP settings
- Encrypted storage of email credentials in Windows Registry
- Logging with rotation to prevent excessive log file growth

Usage:
python script.py [install|start|stop|remove|update|reconfigure]
- install: Install the service and configure email settings
- start: Start the service
- stop: Stop the service
- remove: Remove the service
- update: Update the service configuration
- reconfigure: Reconfigure email settings

Dependencies:
psutil, win32event, win32service, win32serviceutil, servicemanager, winreg, cryptography

Configuration:
Settings are stored in a 'config.json' file in the same directory as the script.
Email credentials are securely stored in the Windows Registry.

Note: This script is designed to run on Windows systems only.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 12.2 KB
- Lines of code: 267 (of 335 total)

**Functions:**
- `check_dependencies`: Check dependencies
- `check_module`: Check module based on module
- `load_config`: Load config
- `main`: Main

**Classes:**
- `Config`: Represents a config
- `DiskSpaceAlertService`: Provides disk space alert functionality
  - Methods:
    - `__init__`: Special method __init__
    - `SvcStop`: Svcstop
    - `SvcDoRun`: Svcdorun
    - `main`: Main
    - `check_disk_space`: Check disk space
    - `get_disks`: Retrieves disks
    - `send_alert`: Send alert based on disk
    - `get_email_credentials`: Retrieves email credentials
    - `configure_email`: Configure email

**Dependencies:**
- cryptography
- dataclasses
- getpass
- psutil
- servicemanager
- smtplib
- win32event
- win32service
- win32serviceutil
- winreg

### disksizeinfo.py

**Path:** `system_utilities\disksizeinfo.py`

**Description:**
This script provides information about disk usage and CPU utilization.

It uses the psutil library to gather and display the following information:
1. Free space available on C: and D: drives (in GB)
2. CPU usage statistics for each CPU core (user, system, and idle percentages)

The script first checks disk partitions, focusing on C: and D: drives,
and reports the free space available on each.

Then, it collects CPU usage data for a 1-second interval and displays
the usage percentages for each CPU core.

Requirements:
- psutil library must be installed

Note: This script is designed for Windows systems, as it specifically looks for
C: and D: drives.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 1.4 KB
- Lines of code: 23 (of 36 total)

**Dependencies:**
- psutil

### hour_calculator.py

**Path:** `system_utilities\hour_calculator.py`

**Description:**
This script handles hour calculator.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 10.1 KB
- Lines of code: 229 (of 291 total)

**Functions:**
- `parse_time`: Convert a string 'hours:minutes' or 'hours' into total minutes as a float
- `format_hours`: Converts total minutes into 'hours:minutes' string, with rounding to nearest minute
- `evaluate_expression`: Given a list of tokens in the form [time_in_minutes, operator, time_in_minutes, operator, 
- `main`: Main

**Classes:**
- `TimeCalculator`: Represents a time calculator
  - Methods:
    - `__init__`: Special method __init__
    - `on_button_clicked`: On button clicked
    - `clear_all`: Reset everything
    - `process_operator`: 1
    - `process_equals`: 1
    - `update_expression_display`: Updates the expression display with the newly entered time or operator
    - `show_error`: Show error based on message

**Dependencies:**
- PyQt5

### system_discovery.py

**Path:** `system_utilities\system_discovery.py`

**Description:**
This script provides functionality to gather and display system information.

It uses the platform, socket, and psutil modules to collect various details about the system,
including the operating system, machine architecture, hostname, IP address, CPU cores, and total RAM.

The main function, system_discovery(), prints this information to the console.

When run as a standalone script, it automatically executes the system_discovery() function.

Dependencies:
    - platform
    - socket
    - psutil

Usage:
    Run the script directly to see the system information output.
    Alternatively, import the system_discovery function to use it in other scripts.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 1.8 KB
- Lines of code: 28 (of 50 total)

**Functions:**
- `system_discovery`: Function to gather and print system information

**Dependencies:**
- psutil

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

### build_app.py

**Path:** `video_processing\youtube_downloader\build_app.py`

**Description:**
This script handles build app.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 3.6 KB
- Lines of code: 102 (of 134 total)

**Functions:**
- `build_executable`: Build executable

### youtube_downloader.py

**Path:** `video_processing\youtube_downloader\youtube_downloader.py`

**Description:**
This script downloads content related to youtube.


**File Info:**
- Last modified: 2025-04-15 20:20:08
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