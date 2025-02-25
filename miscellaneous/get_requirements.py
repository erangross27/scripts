"""
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
"""

import os
import ast
import sys
import platform
import pkgutil
from collections import defaultdict

# Function to extract import statements from a Python file
def get_imports(file_path):
    """
    Retrieves imports based on file path.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError:
            print(f"Couldn't parse {file_path} due to syntax errors.")
            return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:  # absolute import
                imports.add(node.module.split('.')[0])
    
    return imports

# Function to normalize package names (e.g., 'PIL' to 'Pillow')
def normalize_package_name(package):
    """
    Normalize package name based on package.
    """
    package_mappings = {
        'PIL': 'Pillow',
        'bidi': 'python-bidi',
        'cv2': 'opencv-python',
        # Add more mappings here if needed
    }
    return package_mappings.get(package, package)

# Function to get a list of standard library modules
def get_stdlib_modules():
    """
    Retrieves stdlib modules.
    """
    stdlib_modules = set(sys.builtin_module_names)
    stdlib_modules.update([m.name for m in pkgutil.iter_modules()])
    return stdlib_modules

# Function to check if a package is Windows-specific
def is_windows_specific(package):
    """
    Checks if windows specific based on package.
    """
    windows_specific_modules = {
        'win32', 'winreg', '_win', 'msvcrt', 'nt', 'winsound', 'win32com', 'win32api',
        'win32gui', 'win32con', 'win32event', 'win32evtlog', 'win32file', 'win32security',
        'pywintypes', 'pythoncom', 'winshell', 'servicemanager', 'wmi'
    }
    return package.lower() in windows_specific_modules or any(package.startswith(prefix) for prefix in windows_specific_modules)

# Main function to generate requirements file
def get_all_requirements(output_file):
    """
    Retrieves all requirements based on output file.
    """
    current_dir = os.getcwd()
    all_imports = defaultdict(set)
    is_windows = platform.system() == "Windows"
    stdlib_modules = get_stdlib_modules()

    # Iterate through all Python files in the current directory
    for filename in os.listdir(current_dir):
        if filename.endswith(".py"):
            file_path = os.path.join(current_dir, filename)
            imports = get_imports(file_path)
            for imp in imports:
                # Filter out standard library modules and Windows-specific modules on non-Windows systems
                if imp.lower() not in stdlib_modules and (is_windows or not is_windows_specific(imp)):
                    normalized_imp = normalize_package_name(imp)
                    all_imports[normalized_imp].add(filename)

    # Write the requirements to the output file
    with open(output_file, 'w') as f:
        for imp, files in sorted(all_imports.items()):
            f.write(f"{imp} # Used in: {', '.join(sorted(files))}\n")

    print(f"Requirements have been saved to {output_file}")

# Main entry point of the script
def main():
    """
    Main.
    """
    output_file = "requirements.txt"
    get_all_requirements(output_file)

# Execute the main function if the script is run directly
if __name__ == "__main__":
    main()
