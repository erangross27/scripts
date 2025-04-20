# Directory Scripts Documentation


## Available Scripts


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