# Directory Scripts Documentation

## Available Scripts


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