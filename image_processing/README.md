# Directory Scripts Documentation


## Available Scripts


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