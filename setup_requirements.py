import os
import ast
import sys
from pathlib import Path
import argparse

# Define core, optional, and allowed packages
CORE_PACKAGES = {
    'PyQt6', 'yt-dlp', 'requests', 'tqdm', 'pydub', 'pandas', 'numpy', 'psutil',
    'moviepy', 'matplotlib', 'scikit-learn', 'opencv-python', 'Pillow', 'PyYAML'
}

OPTIONAL_PACKAGES = {
    'redis', 'psycopg2', 'pymongo', 'qiskit', 'qiskit-ibm-runtime',
    'fastapi', 'uvicorn', 'torch', 'torchvision', 'diffusers',
    'python-docx', 'pymupdf', 'cryptography', 'bcrypt', 'pyjwt', 'pywin32',
    'bottle', 'pydantic', 'anthropic', 'openai', 'python-dotenv', 'piexif',
    'gputil', 'pycuda', 'wmi', 'sqlalchemy', 'scapy', 'netifaces',
    'huggingface-hub', 'httpx'
}

ALLOWED_PACKAGES = CORE_PACKAGES | OPTIONAL_PACKAGES

# Version specifications for certain packages
VERSION_MAP = {
    'bottle': '>=0.12.20',
    'pydantic': '>=2.10,<3.0'
}

# Mapping from imported module names to package names
MODULE_TO_PACKAGE = {
    'cv2': 'opencv-python',
    'PIL': 'Pillow',
    'sklearn': 'scikit-learn',
    'yaml': 'PyYAML',
    'PyQt6': 'PyQt6',
    'fitz': 'pymupdf',
    'scapy': 'scapy',
    'anthropic': 'anthropic',
    'openai': 'openai',
    'dotenv': 'python-dotenv',
    'netifaces': 'netifaces',
    'GPUtil': 'gputil',
    'huggingface_hub': 'huggingface-hub',
    'httpx': 'httpx',
    'jwt': 'pyjwt',
    'docx': 'python-docx',
}

# Common Python standard library modules to exclude
stdlib_list = ['abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections',
               'contextlib', 'copy', 'csv', 'datetime', 'decimal', 'enum',
               'functools', 'glob', 'hashlib', 'hmac', 'io', 'itertools', 'json',
               'logging', 'math', 'multiprocessing', 'os', 'pathlib', 'pickle',
               'random', 're', 'socket', 'sqlite3', 'string', 'sys', 'threading',
               'time', 'typing', 'uuid', 'warnings', 'xml', 'zipfile']

def extract_imports(file_path):
    """Extract import statements from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                tree = ast.parse(file.read())
            except (SyntaxError, ValueError) as e:
                print(f"Warning: Could not parse {file_path}: {e}")
                return set()
    except (IOError, OSError) as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def find_requirements(directory):
    """Find all Python files and determine requirements."""
    all_imports = set()
    file_count = 0

    print(f"Scanning directory: {directory}")

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                print(f"Processing: {file_path}")
                file_imports = extract_imports(file_path)
                all_imports.update(file_imports)
                file_count += 1

    # Map module names to package names
    mapped_packages = {MODULE_TO_PACKAGE.get(imp, imp) for imp in all_imports}

    # Remove standard library modules
    stdlib_modules = set(stdlib_list)
    external_packages = {pkg for pkg in mapped_packages if pkg not in stdlib_modules}

    # Determine used optional packages
    used_optional = external_packages & OPTIONAL_PACKAGES

    # Requirements include all core packages and used optional packages
    requirements = CORE_PACKAGES | used_optional

    # Warn about unknown packages
    unknown_packages = external_packages - ALLOWED_PACKAGES
    if unknown_packages:
        print("\nWarning: The following imported packages are not in the allowed list:")
        for pkg in sorted(unknown_packages):
            print(f" - {pkg}")

    print(f"\nProcessed {file_count} Python files")
    return requirements

def generate_requirements_txt(requirements, output_file='requirements.txt'):
    """Generate requirements.txt file with sections."""
    with open(output_file, 'w') as f:
        f.write("# Core packages\n")
        for pkg in sorted(CORE_PACKAGES):
            if pkg in VERSION_MAP:
                f.write(f"{pkg}{VERSION_MAP[pkg]}\n")
            else:
                f.write(f"{pkg}\n")
        optional_used = requirements - CORE_PACKAGES
        if optional_used:
            f.write("\n# Optional packages\n")
            for pkg in sorted(optional_used):
                if pkg in VERSION_MAP:
                    f.write(f"{pkg}{VERSION_MAP[pkg]}\n")
                else:
                    f.write(f"{pkg}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate requirements.txt from Python files')
    parser.add_argument('--dir', type=str, default=os.getcwd(),
                        help='Directory to scan (default: current directory)')
    args = parser.parse_args()

    scan_dir = args.dir

    if not os.path.exists(scan_dir):
        print(f"Error: Directory {scan_dir} does not exist!")
        sys.exit(1)

    all_requirements = find_requirements(scan_dir)

    output_file = os.path.join(scan_dir, 'requirements.txt')
    generate_requirements_txt(all_requirements, output_file)

    print(f"\nGenerated {output_file} with {len(all_requirements)} packages:")
    print('\n'.join(sorted(all_requirements)))