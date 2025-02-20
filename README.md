# Scripts Directory Documentation

This repository contains various Python scripts organized by functionality.

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

**Dependencies:**
- subprocess
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

**Dependencies:**
- PyQt5
- fitz

### breast_cancer_detector.py

**Path:** `healthcare\breast_cancer_detector.py`

**Description:**
No description available

**Dependencies:**
- joblib
- numpy
- pandas
- sklearn

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

**Dependencies:**
- torch
- train
- utils
- yaml

### cuda_matrix_multiplication.py

**Path:** `miscellaneous\cuda_matrix_multiplication.py`

**Description:**
No description available

**Dependencies:**
- numpy
- pycuda

### cuda_vector_add.py

**Path:** `miscellaneous\cuda_vector_add.py`

**Description:**
No description available

**Dependencies:**
- numpy
- pycuda

### discover_gpu_memory.py

**Path:** `miscellaneous\discover_gpu_memory.py`

**Description:**
No description available

**Dependencies:**
- wmi

### discover_monitor_information.py

**Path:** `miscellaneous\discover_monitor_information.py`

**Description:**
No description available

**Dependencies:**
- subprocess
- wmi

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

**Dependencies:**
- pkgutil
- platform

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
No description available

**Dependencies:**
- shutil

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

**Dependencies:**
- GPUtil
- numpy
- psutil
- torch

### remove_versions_from_requirements.py

**Path:** `miscellaneous\remove_versions_from_requirements.py`

**Description:**
No description available

**Dependencies:**

### setup_env.py

**Path:** `miscellaneous\setup_env.py`

**Description:**
No description available

**Dependencies:**
- ctypes
- winreg

### setup_requirements.py

**Path:** `miscellaneous\setup_requirements.py`

**Description:**
No description available

**Dependencies:**

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

**Dependencies:**
- anthropic
- psycopg2
- subprocess

### __init__.py

**Path:** `network monitor\__init__.py`

**Description:**
No description available

### anomaly_detector.py

**Path:** `network monitor\anomaly_detector.py`

**Description:**
No description available

**Dependencies:**
- feature_extractor
- numpy

### __init__.py

**Path:** `network monitor\config\__init__.py`

**Description:**
No description available

**Dependencies:**
- feature_config
- whitelist_config

### feature_config.py

**Path:** `network monitor\config\feature_config.py`

**Description:**
No description available

### whitelist_config.py

**Path:** `network monitor\config\whitelist_config.py`

**Description:**
No description available

**Dependencies:**
- ipaddress

### feature_extractor.py

**Path:** `network monitor\feature_extractor.py`

**Description:**
No description available

**Dependencies:**
- config
- pandas
- scapy

### interface_manager.py

**Path:** `network monitor\interface_manager.py`

**Description:**
No description available

**Dependencies:**
- bidi
- netifaces
- psutil
- subprocess
- wmi

### logger_setup.py

**Path:** `network monitor\logger_setup.py`

**Description:**
No description available

**Dependencies:**

### __init__.py

**Path:** `network monitor\models\__init__.py`

**Description:**
No description available

**Dependencies:**
- persistent_anomaly_detector

### persistent_anomaly_detector.py

**Path:** `network monitor\models\persistent_anomaly_detector.py`

**Description:**
No description available

**Dependencies:**
- joblib
- pandas
- sklearn

### network_monitor.py

**Path:** `network monitor\network_monitor.py`

**Description:**
No description available

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
No description available

**Dependencies:**
- ipaddress
- scapy

### packet_capture.py

**Path:** `network monitor\packet_capture.py`

**Description:**
No description available

**Dependencies:**
- queue
- scapy
- tqdm

### __init__.py

**Path:** `network monitor\utils\__init__.py`

**Description:**
No description available

**Dependencies:**
- network_utils
- packet_utils

### network_utils.py

**Path:** `network monitor\utils\network_utils.py`

**Description:**
No description available

**Dependencies:**

### packet_utils.py

**Path:** `network monitor\utils\packet_utils.py`

**Description:**
No description available

**Dependencies:**
- ipaddress
- scapy

### whitelist_manager.py

**Path:** `network monitor\whitelist_manager.py`

**Description:**
No description available

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

**Dependencies:**
- qiskit
- qiskit_ibm_runtime

### readme_generator.py

**Path:** `readme_generator.py`

**Description:**
No description available

**Dependencies:**

### setup_requirements.py

**Path:** `setup_requirements.py`

**Description:**
No description available

**Dependencies:**

### build_app.py

**Path:** `speech_to_text\build_app.py`

**Description:**
No description available

**Dependencies:**
- shutil

### transcription_app.py

**Path:** `speech_to_text\transcription_app.py`

**Description:**
No description available

**Dependencies:**
- PyQt5
- openai
- pydub

### ai_security_service.py

**Path:** `system_utilities\ai_security_service.py`

**Description:**
No description available

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
ClaudeChat Application

This application provides a graphical user interface for interacting with the Anthropic Claude AI model. 
It allows users to have conversations with the AI, upload and analyze files, and manage conversation history.

Key features:
- Chat interface with Claude AI
- File upload and analysis (text, PDF, images, Word, Excel)
- Conversation history management
- Code block highlighting and copying
- Multiple Claude model selection

The application uses PyQt5 for the GUI, SQLite for storing conversation history, 
and integrates with various libraries for file handling and API communication.

Main classes:
- ClaudeChat: The main application window and logic
- ConversationHistory: Manages conversation storage and retrieval
- MessageProcessor: Handles asynchronous API calls to Claude
- PythonHighlighter: Provides syntax highlighting for code blocks

Usage:
Run this script to launch the ClaudeChat application. An Anthropic API key is required.

Dependencies:
- PyQt5
- anthropic
- fitz (PyMuPDF)
- Pillow
- win32com

Note: This application is designed to run on Windows due to some Windows-specific features.

**Dependencies:**
- PIL
- PyQt5
- anthropic
- ctypes
- fitz
- httpx
- pyexpat
- pythoncom
- requests
- win32com
- winreg

### anthropic_claude_chat_for_linux.py

**Path:** `system_utilities\anthropic_claude_chat_for_linux.py`

**Description:**
ClaudeChat Application

This application provides a graphical user interface for interacting with the Claude AI model
using the Anthropic API. It allows users to have conversations with the AI, upload files for
analysis, and manage conversation history.

Key features:
- Chat interface for interacting with Claude AI
- File upload and analysis (text, PDF, images)
- Conversation history management
- Code block detection and syntax highlighting
- Multiple Claude model selection

The application uses PyQt5 for the GUI, sqlite3 for local storage of conversation history,
and integrates with the Anthropic API for AI interactions.

Usage:
Run this script to launch the ClaudeChat application. Users will need to provide their
Anthropic API key on first run or if it's not set in the environment variables.

Dependencies:
- PyQt5
- anthropic
- fitz (PyMuPDF)
- Pillow
- requests
- logging

Note: Ensure all required dependencies are installed and the Anthropic API key is available
before running the application.

**Dependencies:**
- PIL
- PyQt5
- anthropic
- ctypes
- fitz
- httpx
- platform
- pyexpat
- requests
- subprocess

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

**Dependencies:**
- cryptography
- dataclasses
- email
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

**Dependencies:**
- psutil

### hour_calculator.py

**Path:** `system_utilities\hour_calculator.py`

**Description:**
No description available

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

**Dependencies:**
- platform
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

**Dependencies:**
- subprocess
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

**Dependencies:**
- GPUtil
- psutil
- subprocess

### build_app.py

**Path:** `video_processing\youtube_downloader\build_app.py`

**Description:**
No description available

**Dependencies:**
- shutil

### youtube_downloader.py

**Path:** `video_processing\youtube_downloader\youtube_downloader.py`

**Description:**
No description available

**Dependencies:**
- PyQt5
- tempfile
- yt_dlp