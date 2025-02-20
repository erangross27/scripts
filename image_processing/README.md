# Directory Scripts Documentation

## Available Scripts


### captureImage.py

**Path:** `image_processing\captureImage.py`

**Description:**
No description available

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

**Dependencies:**
- PyQt5

### convertor.py

**Path:** `image_processing\convertor.py`

**Description:**
No description available

**Dependencies:**
- PIL
- PyQt5

### copy_all_images_from_sub_folders.py

**Path:** `image_processing\copy_all_images_from_sub_folders.py`

**Description:**
No description available

**Dependencies:**
- shutil

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

**Dependencies:**
- google
- tkinter

### image_brightener_gui.py

**Path:** `image_processing\image_brightener_gui.py`

**Description:**
No description available

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

**Dependencies:**
- PyQt5
- shutil

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

**Dependencies:**
- shutil

### shutterstock_gui.py

**Path:** `image_processing\shutterstock_gui.py`

**Description:**
No description available

**Dependencies:**
- PyQt5
- shutterstock_uploader

### shutterstock_uploader.py

**Path:** `image_processing\shutterstock_uploader.py`

**Description:**
No description available

**Dependencies:**
- anthropic
- dotenv
- requests

### test_cuda.py

**Path:** `image_processing\test_cuda.py`

**Description:**
No description available

**Dependencies:**
- torch

### update_meta_data.py

**Path:** `image_processing\update_meta_data.py`

**Description:**
No description available

**Dependencies:**
- PIL
- PyQt5
- anthropic
- piexif
- shlex
- subprocess
- traceback
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

**Dependencies:**
- PIL
- cv2
- numpy
- tkinter
- torch
- tqdm