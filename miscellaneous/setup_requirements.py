"""
This script handles setup requirements.
"""

import os
import ast
import re
from pathlib import Path

def extract_imports(file_path):
    """Extract import statements from a Python file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
        except:
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
    """Find all Python files and extract their requirements"""
    requirements = set()
    
    # Walk through all directories
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                file_imports = extract_imports(file_path)
                requirements.update(file_imports)
    
    # Filter out standard library modules
    stdlib_modules = set(stdlib_list)
    requirements = {req for req in requirements if req not in stdlib_modules}
    
    return requirements

def generate_requirements_txt(requirements, output_file='requirements.txt'):
    """Generate requirements.txt file"""
    with open(output_file, 'w') as f:
        for req in sorted(requirements):
            f.write(f'{req}\n')

# List of Python standard library modules
stdlib_list = ['abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 
              'contextlib', 'copy', 'csv', 'datetime', 'decimal', 'enum',
              'functools', 'glob', 'hashlib', 'hmac', 'io', 'itertools', 'json',
              'logging', 'math', 'multiprocessing', 'os', 'pathlib', 'pickle',
              'random', 're', 'socket', 'sqlite3', 'string', 'sys', 'threading',
              'time', 'typing', 'uuid', 'warnings', 'xml', 'zipfile']

if __name__ == '__main__':
    # Get the current directory
    current_dir = os.getcwd()
    
    # Find all requirements
    all_requirements = find_requirements(current_dir)
    
    # Generate requirements.txt
    generate_requirements_txt(all_requirements)
    
    print(f"Generated requirements.txt with {len(all_requirements)} packages:")
    print('\n'.join(sorted(all_requirements)))
