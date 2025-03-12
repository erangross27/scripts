"""
This script handles setup requirements.
"""

# This script generates a requirements.txt file by analyzing Python imports in a directory

# Import required standard library modules
import os
import ast
import sys
from pathlib import Path
import argparse

def extract_imports(file_path):
    """Extract import statements from a Python file"""
    # Try to parse the Python file and handle any syntax errors
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                tree = ast.parse(file.read())
            except (SyntaxError, ValueError) as e:
                import warnings
                warnings.warn(f"Could not parse {file_path}: {e}", SyntaxWarning)
                return set()
    except (IOError, OSError) as e:
        import warnings
        warnings.warn(f"Could not read {file_path}: {e}", RuntimeWarning)
        return set()

    # Store found imports in a set
    imports = set()
    # Walk through the AST to find Import and ImportFrom nodes
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            # Handle relative imports (from . import module)
            if node.module is not None:
                imports.add(node.module.split('.')[0])
            # Add imported names for relative imports without module
            else:
                for name in node.names:
                    imports.add(name.name.split('.')[0])
    return imports

# Common Python standard library modules to exclude from requirements
stdlib_list = ['abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections',
              'contextlib', 'copy', 'csv', 'datetime', 'decimal', 'enum',
              'functools', 'glob', 'hashlib', 'hmac', 'io', 'itertools', 'json',
              'logging', 'math', 'multiprocessing', 'os', 'pathlib', 'pickle',
              'random', 're', 'socket', 'sqlite3', 'string', 'sys', 'threading',
              'time', 'typing', 'uuid', 'warnings', 'xml', 'zipfile']

def find_requirements(directory):
    """Find all Python files and extract their requirements"""
    # Initialize sets and counters
    requirements = set()
    file_count = 0

    print(f"Scanning directory: {directory}")

    # Recursively walk through directory to find .py files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                print(f"Processing: {file_path}")
                file_imports = extract_imports(file_path)
                requirements.update(file_imports)
                file_count += 1

    # Remove standard library modules from requirements
    stdlib_modules = set(stdlib_list)
    requirements = {req for req in requirements if req not in stdlib_modules}

    print(f"\nProcessed {file_count} Python files")
    return requirements

def generate_requirements_txt(requirements, output_file='requirements.txt'):
    """Generate requirements.txt file"""
    # Write sorted requirements to file
    with open(output_file, 'w') as f:
        for req in sorted(requirements):
            f.write(f'{req}\n')

if __name__ == '__main__':
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Generate requirements.txt from Python files')
    parser.add_argument('--dir', type=str, default=os.getcwd(),
                      help='Directory to scan (default: current directory)')
    args = parser.parse_args()

    # Use the specified directory or default to current directory
    scan_dir = args.dir

    # Verify directory exists
    if not os.path.exists(scan_dir):
        print(f"Error: Directory {scan_dir} does not exist!")
        sys.exit(1)

    # Find all requirements
    all_requirements = find_requirements(scan_dir)

    # Generate requirements.txt in the scanned directory
    output_file = os.path.join(scan_dir, 'requirements.txt')
    generate_requirements_txt(all_requirements, output_file)

    # Print summary
    print(f"\nGenerated {output_file} with {len(all_requirements)} packages:")
    print('\n'.join(sorted(all_requirements)))
