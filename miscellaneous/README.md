# Directory Scripts Documentation

## Available Scripts


### cuda_matrix_multiplication.py

**Path:** `miscellaneous\cuda_matrix_multiplication.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 4.0 KB
- Lines of code: 88 (of 133 total)

**Functions:**
- `cpu_matrix_mul`: No documentation
- `gpu_matrix_mul`: No documentation

**Dependencies:**
- numpy
- pycuda

### cuda_vector_add.py

**Path:** `miscellaneous\cuda_vector_add.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 2.2 KB
- Lines of code: 48 (of 81 total)

**Dependencies:**
- numpy
- pycuda

### discover_gpu_memory.py

**Path:** `miscellaneous\discover_gpu_memory.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 1.9 KB
- Lines of code: 29 (of 51 total)

**Functions:**
- `get_intel_gpu_info`: Retrieves and displays information about the Intel GPU installed on the system

**Dependencies:**
- wmi

### discover_monitor_information.py

**Path:** `miscellaneous\discover_monitor_information.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 3.8 KB
- Lines of code: 80 (of 104 total)

**Functions:**
- `get_monitor_info_wmi`: Retrieve monitor information using Windows Management Instrumentation (WMI)
- `get_monitor_info_powershell`: Retrieve monitor information using PowerShell as a fallback method
- `main`: Main function to retrieve and display monitor information

**Dependencies:**
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

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 4.1 KB
- Lines of code: 78 (of 105 total)

**Functions:**
- `get_imports`: No documentation
- `normalize_package_name`: No documentation
- `get_stdlib_modules`: No documentation
- `is_windows_specific`: No documentation
- `get_all_requirements`: No documentation
- `main`: No documentation

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
- Last modified: 2025-02-18 10:38:35
- Size: 4.1 KB
- Lines of code: 90 (of 123 total)

**Functions:**
- `print_gpu_memory`: No documentation
- `print_cpu_memory`: No documentation
- `cpu_gaussian_blur`: No documentation
- `gpu_gaussian_blur`: No documentation
- `run_comparison`: No documentation

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

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 3.0 KB
- Lines of code: 68 (of 81 total)

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
- Last modified: 2025-02-18 10:38:35
- Size: 4.1 KB
- Lines of code: 82 (of 116 total)

**Functions:**
- `print_gpu_memory`: No documentation
- `print_cpu_memory`: No documentation
- `cpu_hash_passwords`: No documentation
- `gpu_hash_passwords`: No documentation
- `run_comparison`: No documentation

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
- Last modified: 2025-02-18 10:38:35
- Size: 4.6 KB
- Lines of code: 101 (of 140 total)

**Functions:**
- `is_prime`: No documentation
- `cpu_find_primes`: No documentation
- `gpu_is_prime`: No documentation
- `gpu_find_primes`: No documentation
- `print_gpu_memory`: No documentation
- `print_cpu_memory`: No documentation
- `run_comparison`: No documentation

**Dependencies:**
- GPUtil
- numpy
- psutil
- torch

### remove_versions_from_requirements.py

**Path:** `miscellaneous\remove_versions_from_requirements.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 2.3 KB
- Lines of code: 34 (of 54 total)

**Functions:**
- `remove_versions`: Remove version specifiers and comments from a requirements file

### setup_env.py

**Path:** `miscellaneous\setup_env.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 6.9 KB
- Lines of code: 141 (of 187 total)

**Functions:**
- `main`: No documentation

**Classes:**
- `EnvironmentManager`: No documentation
  - Methods:
    - `__init__`: No documentation
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
No description available

**File Info:**
- Last modified: 2025-02-20 08:52:01
- Size: 2.4 KB
- Lines of code: 49 (of 67 total)

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
- Last modified: 2025-02-18 10:38:35
- Size: 3.3 KB
- Lines of code: 79 (of 107 total)

**Functions:**
- `cpu_sort`: No documentation
- `gpu_sort`: No documentation
- `print_gpu_memory`: No documentation
- `print_cpu_memory`: No documentation
- `run_comparison`: No documentation

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
- Last modified: 2025-02-18 10:38:35
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