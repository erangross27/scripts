# Directory Scripts Documentation

## Available Scripts


### captureImage.py

**Path:** `image_processing\captureImage.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 1.5 KB
- Lines of code: 34 (of 50 total)

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
- Last modified: 2025-02-18 10:38:35
- Size: 7.5 KB
- Lines of code: 149 (of 191 total)

**Functions:**
- `compress_image`: No documentation
- `compress_images_in_folder`: No documentation

**Classes:**
- `ImageCompressorGUI`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `initUI`: No documentation
    - `setup_radio_buttons`: No documentation
    - `setup_input_output`: No documentation
    - `setup_quality_slider`: No documentation
    - `setup_compress_button`: No documentation
    - `setup_output_text`: No documentation
    - `clear_paths`: No documentation
    - `browse_input`: No documentation
    - `browse_output`: No documentation
    - `update_quality_label`: No documentation
    - `compress_images`: No documentation

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
- Last modified: 2025-02-18 10:38:35
- Size: 5.0 KB
- Lines of code: 82 (of 125 total)

**Functions:**
- `process_image`: No documentation
- `create_gui`: No documentation

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
- Last modified: 2025-02-18 10:38:35
- Size: 6.1 KB
- Lines of code: 112 (of 151 total)

**Classes:**
- `SVGConverter`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `initUI`: No documentation
    - `create_input_layout`: No documentation
    - `create_resolution_layout`: No documentation
    - `select_input`: No documentation
    - `select_output`: No documentation
    - `update_resolution_from_svg`: No documentation
    - `update_output_suffix`: No documentation
    - `convert_svg`: No documentation

**Dependencies:**
- PyQt5

### convertor.py

**Path:** `image_processing\convertor.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 6.0 KB
- Lines of code: 87 (of 129 total)

**Classes:**
- `ImageConverter`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `select_source`: No documentation
    - `select_destination`: No documentation
    - `update_convert_button`: No documentation
    - `convert_image`: No documentation

**Dependencies:**
- PIL
- PyQt5

### copy_all_images_from_sub_folders.py

**Path:** `image_processing\copy_all_images_from_sub_folders.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-20 08:33:40
- Size: 1.6 KB
- Lines of code: 30 (of 49 total)

**Functions:**
- `main`: No documentation

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
- Last modified: 2025-02-18 10:38:35
- Size: 3.9 KB
- Lines of code: 79 (of 115 total)

**Functions:**
- `extract_text_from_image`: No documentation
- `save_to_file`: No documentation
- `select_image_path`: No documentation
- `convert_and_save`: No documentation
- `main`: No documentation

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
- Last modified: 2025-02-18 10:38:35
- Size: 4.8 KB
- Lines of code: 80 (of 136 total)

**Functions:**
- `extract_text_from_image`: No documentation
- `save_to_file`: No documentation
- `select_image_path`: No documentation
- `convert_and_save`: No documentation
- `main`: No documentation

**Dependencies:**
- google
- tkinter

### image_brightener_gui.py

**Path:** `image_processing\image_brightener_gui.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 5.8 KB
- Lines of code: 124 (of 168 total)

**Functions:**
- `main`: No documentation

**Classes:**
- `ImageBrightener`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `browse_input`: No documentation
    - `browse_output`: No documentation
    - `update_brightness`: No documentation
    - `update_preview`: No documentation
    - `brighten_image`: No documentation
    - `process_image`: No documentation

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
- Last modified: 2025-02-18 10:38:35
- Size: 4.2 KB
- Lines of code: 72 (of 111 total)

**Classes:**
- `ImageMover`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `initUI`: No documentation
    - `selectSourceDir`: No documentation
    - `selectDestDir`: No documentation
    - `moveImages`: No documentation

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
- Last modified: 2025-02-18 10:38:35
- Size: 23.9 KB
- Lines of code: 391 (of 561 total)

**Classes:**
- `WatermarkDetectionApp`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `create_widgets`: No documentation
    - `download_and_load_inpainting_model`: No documentation
    - `inpaint`: No documentation
    - `browse_model`: No documentation
    - `load_watermark_model`: No documentation
    - `browse_input`: No documentation
    - `browse_output`: No documentation
    - `start_processing`: No documentation
    - `process_file`: No documentation
    - `process_image`: No documentation
    - `save_intermediate_frame`: No documentation
    - `process_video`: No documentation
    - `detect_and_mark_watermark`: No documentation
    - `visualize_mask`: No documentation
    - `inpaint_image`: No documentation
    - `resize_and_pad`: No documentation
    - `update_log`: No documentation
- `GUILogHandler`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `emit`: No documentation

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
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 3.3 KB
- Lines of code: 52 (of 75 total)

**Functions:**
- `organize_dataset`: Organize a dataset by splitting it into training and validation sets

### shutterstock_gui.py

**Path:** `image_processing\shutterstock_gui.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 9.1 KB
- Lines of code: 192 (of 244 total)

**Functions:**
- `main`: No documentation

**Classes:**
- `UploaderWorker`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `process_image`: Process a single image with error handling
    - `run`: Main worker thread execution
- `MainWindow`: No documentation
  - Methods:
    - `__init__`: No documentation
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
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 10.1 KB
- Lines of code: 213 (of 263 total)

**Classes:**
- `ShutterstockAutoUploader`: No documentation
  - Methods:
    - `__init__`: No documentation
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
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 0.3 KB
- Lines of code: 8 (of 9 total)

**Dependencies:**
- torch

### update_meta_data.py

**Path:** `image_processing\update_meta_data.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 20.9 KB
- Lines of code: 419 (of 539 total)

**Functions:**
- `main`: No documentation

**Classes:**
- `MetadataWorker`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `run`: No documentation
    - `stop`: No documentation
- `MainWindow`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `initUI`: No documentation
    - `select_folder`: No documentation
    - `start_processing`: No documentation
    - `stop_processing`: No documentation
    - `update_progress`: No documentation
    - `update_log`: No documentation
    - `processing_finished`: No documentation
- `LocalMetadataUpdater`: No documentation
  - Methods:
    - `__init__`: No documentation
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
- Last modified: 2025-02-18 10:38:35
- Size: 10.0 KB
- Lines of code: 180 (of 250 total)

**Classes:**
- `WatermarkDetectionApp`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `create_widgets`: No documentation
    - `browse_model`: No documentation
    - `load_model`: No documentation
    - `browse_input`: No documentation
    - `browse_output`: No documentation
    - `start_processing`: No documentation
    - `process_file`: No documentation
    - `process_image`: No documentation
    - `process_video`: No documentation
    - `detect_watermark`: No documentation
    - `update_log`: No documentation
- `GUILogHandler`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `emit`: No documentation

**Dependencies:**
- PIL
- cv2
- numpy
- tkinter
- torch
- tqdm