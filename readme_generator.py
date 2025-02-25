#!/usr/bin/env python3
# Script to analyze Python files and generate documentation
# Handles docstring extraction, import analysis, class/function discovery, and README generation

import os
import ast
import re
import sys
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import time
import nbformat

class ScriptAnalyzer:
    def __init__(self, base_dir: str, exclude_dirs: Optional[List[str]] = None):
        # Initialize analyzer with base directory path and exclusion list
        self.base_dir = Path(base_dir)
        self.exclude_dirs = exclude_dirs or ["venv", "__pycache__", ".git", ".github", ".vscode", "build", "dist", "node_modules"]
        self.scripts: Dict[str, Dict] = {}
        self.analyzed_count = 0
        self.total_files = 0

    def extract_docstring(self, file_path: Path) -> str:
        """Parse Python file and extract module-level docstring"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
                docstring = ast.get_docstring(tree)
                return docstring if docstring else "No description available"
        except Exception as e:
            return f"Could not parse file for description: {str(e)}"

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Parse Python file and extract all import statements"""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
                for node in ast.walk(tree):
                    # Handle regular imports
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.add(name.name.split('.')[0])
                    # Handle from imports
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
        except Exception as e:
            print(f"Warning: Error extracting imports from {file_path}: {str(e)}")
        return imports

    def extract_functions_and_classes(self, file_path: Path) -> Dict[str, List[Dict]]:
        """Parse Python file and extract functions and classes with their docstrings"""
        functions_and_classes = {
            'functions': [],
            'classes': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                tree = ast.parse(content)

                # Extract top-level functions
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.FunctionDef):
                        doc = ast.get_docstring(node) or "No documentation"
                        functions_and_classes['functions'].append({
                            'name': node.name,
                            'docstring': doc,
                            'line_number': node.lineno
                        })

                    # Extract classes and their methods
                    elif isinstance(node, ast.ClassDef):
                        class_doc = ast.get_docstring(node) or "No documentation"
                        methods = []

                        for class_node in ast.iter_child_nodes(node):
                            if isinstance(class_node, ast.FunctionDef):
                                method_doc = ast.get_docstring(class_node) or "No documentation"
                                methods.append({
                                    'name': class_node.name,
                                    'docstring': method_doc,
                                    'line_number': class_node.lineno
                                })

                        functions_and_classes['classes'].append({
                            'name': node.name,
                            'docstring': class_doc,
                            'methods': methods,
                            'line_number': node.lineno
                        })

            return functions_and_classes
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
            return functions_and_classes

    def get_file_stats(self, file_path: Path) -> Dict[str, Any]:
        """Get file statistics such as size, lines of code, and last modified date"""
        stats = {}
        try:
            # Get file size
            stats['size'] = file_path.stat().st_size

            # Get last modified date
            mod_time = file_path.stat().st_mtime
            stats['last_modified'] = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')

            # Count lines of code
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.readlines()
                stats['total_lines'] = len(content)

                # Count non-empty, non-comment lines
                code_lines = 0
                for line in content:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        code_lines += 1

                stats['code_lines'] = code_lines

            return stats
        except Exception as e:
            print(f"Error getting file stats for {file_path}: {str(e)}")
            return {
                'size': 0,
                'last_modified': 'Unknown',
                'total_lines': 0,
                'code_lines': 0
            }

    def process_notebook(self, file_path: Path) -> Dict[str, Any]:
        """Process Jupyter notebook (.ipynb) files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                notebook = nbformat.read(file, as_version=4)

                # Extract description from the first markdown cell
                description = "No description available"
                for cell in notebook.cells:
                    if cell.cell_type == 'markdown':
                        description = cell.source.split('\n', 1)[0].strip('# ')
                        break

                # Count code cells and markdown cells
                code_cells = sum(1 for cell in notebook.cells if cell.cell_type == 'code')
                markdown_cells = sum(1 for cell in notebook.cells if cell.cell_type == 'markdown')

                # Extract imports
                imports = set()
                for cell in notebook.cells:
                    if cell.cell_type == 'code':
                        try:
                            tree = ast.parse(cell.source)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Import):
                                    for name in node.names:
                                        imports.add(name.name.split('.')[0])
                                elif isinstance(node, ast.ImportFrom):
                                    if node.module:
                                        imports.add(node.module.split('.')[0])
                        except:
                            pass

                return {
                    'description': description,
                    'code_cells': code_cells,
                    'markdown_cells': markdown_cells,
                    'requirements': imports
                }
        except Exception as e:
            print(f"Error processing notebook {file_path}: {str(e)}")
            return {
                'description': f"Error processing notebook: {str(e)}",
                'code_cells': 0,
                'markdown_cells': 0,
                'requirements': set()
            }

    def analyze_file(self, file_path: Path, relative_path: Path) -> Dict[str, Any]:
        """Analyze a single file and return its data"""
        result = {
            'path': str(relative_path)
        }

        if str(file_path).endswith('.py'):
            # Python file analysis
            result['description'] = self.extract_docstring(file_path)
            result['requirements'] = self.extract_imports(file_path)
            result.update(self.extract_functions_and_classes(file_path))
            result['stats'] = self.get_file_stats(file_path)
            result['type'] = 'python'

        elif str(file_path).endswith('.ipynb'):
            # Jupyter notebook analysis
            notebook_data = self.process_notebook(file_path)
            result['description'] = notebook_data['description']
            result['requirements'] = notebook_data['requirements']
            result['code_cells'] = notebook_data['code_cells']
            result['markdown_cells'] = notebook_data['markdown_cells']
            result['stats'] = self.get_file_stats(file_path)
            result['type'] = 'notebook'

        # Update progress
        self.analyzed_count += 1
        if self.total_files > 0:
            progress = (self.analyzed_count / self.total_files) * 100
            sys.stdout.write(f"\rAnalyzing files: {self.analyzed_count}/{self.total_files} ({progress:.1f}%)")
            sys.stdout.flush()

        return result

    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded based on exclude_dirs"""
        parts = path.parts
        return any(excluded in parts for excluded in self.exclude_dirs)

    def analyze_scripts(self):
        """Walk through directory tree and analyze all Python files and Jupyter notebooks"""
        # Count total files first for progress reporting
        self.total_files = 0
        for root, _, files in os.walk(self.base_dir):
            root_path = Path(root)
            if self.should_exclude(root_path):
                continue

            for file in files:
                if file.endswith(('.py', '.ipynb')):
                    self.total_files += 1

        print(f"Found {self.total_files} files to analyze")
        self.analyzed_count = 0

        # Now analyze all files with parallel processing
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = []

            for root, _, files in os.walk(self.base_dir):
                root_path = Path(root)
                if self.should_exclude(root_path):
                    continue

                for file in files:
                    if file.endswith(('.py', '.ipynb')):
                        file_path = root_path / file
                        relative_path = file_path.relative_to(self.base_dir)
                        futures.append(executor.submit(self.analyze_file, file_path, relative_path))

            # Collect results
            for future in futures:
                result = future.result()
                self.scripts[result['path']] = result

        print(f"\nAnalyzed {self.analyzed_count} files")
    def generate_readme_content(self, scripts_list: List[Dict], is_root: bool = False) -> str:
        """Generate markdown content for README files"""
        content = []

        # Add header content for root README
        if is_root:
            content.extend([
                "# Scripts Directory Documentation",
                "\nThis repository contains various Python scripts and Jupyter notebooks organized by functionality.",
                "\n## Table of Contents\n"
            ])

            # Organize scripts by directory for table of contents
            scripts_by_dir: Dict[str, List[Dict]] = {}
            for script_info in self.scripts.values():
                dir_name = os.path.dirname(script_info['path']) or 'Root'
                if dir_name not in scripts_by_dir:
                    scripts_by_dir[dir_name] = []
                scripts_by_dir[dir_name].append(script_info)

            # Generate directory links for table of contents
            for dir_name in sorted(scripts_by_dir.keys()):
                clean_name = dir_name.replace('\\', '/')
                if clean_name == 'Root':
                    content.append(f"- [Root Scripts](#root-scripts)")
                else:
                    content.append(f"- [{clean_name}](#{clean_name.lower().replace('/', '-')})")

            content.append("\n## Root Scripts\n")
        else:
            # Add header content for subdirectory READMEs
            content.extend([
                "# Directory Scripts Documentation",
                "\n## Available Scripts\n"
            ])

        # Add content for each script
        for script_info in sorted(scripts_list, key=lambda x: x['path']):
            script_name = os.path.basename(script_info['path'])
            content.extend([
                f"\n### {script_name}",
                f"\n**Path:** `{script_info['path']}`",
                f"\n**Description:**\n{script_info['description']}",
            ])

            # Add file statistics
            if 'stats' in script_info:
                stats = script_info['stats']
                content.append("\n**File Info:**")
                content.append(f"- Last modified: {stats['last_modified']}")
                content.append(f"- Size: {stats['size'] / 1024:.1f} KB")
                content.append(f"- Lines of code: {stats['code_lines']} (of {stats['total_lines']} total)")

            # Add Jupyter notebook specific information
            if script_info.get('type') == 'notebook':
                content.append("\n**Notebook Info:**")
                content.append(f"- Code cells: {script_info.get('code_cells', 0)}")
                content.append(f"- Markdown cells: {script_info.get('markdown_cells', 0)}")

            # Add functions information if available
            if 'functions' in script_info and script_info['functions']:
                content.append("\n**Functions:**")
                for func in sorted(script_info['functions'], key=lambda x: x['line_number']):
                    # Take the first sentence of the docstring for concise display
                    doc_summary = func['docstring'].split('.')[0].strip()
                    content.append(f"- `{func['name']}`: {doc_summary}")

            # Add classes information if available
            if 'classes' in script_info and script_info['classes']:
                content.append("\n**Classes:**")
                for cls in sorted(script_info['classes'], key=lambda x: x['line_number']):
                    # Take the first sentence of the docstring for concise display
                    doc_summary = cls['docstring'].split('.')[0].strip()
                    content.append(f"- `{cls['name']}`: {doc_summary}")
                    if cls['methods']:
                        content.append("  - Methods:")
                        for method in sorted(cls['methods'], key=lambda x: x['line_number']):
                            method_doc = method['docstring'].split('.')[0].strip()
                            content.append(f"    - `{method['name']}`: {method_doc}")

            # Add non-standard library dependencies
            if script_info['requirements']:
                non_stdlib_reqs = [req for req in sorted(script_info['requirements']) if req not in stdlib_modules]
                if non_stdlib_reqs:
                    content.append("\n**Dependencies:**")
                    for req in non_stdlib_reqs:
                        content.append(f"- {req}")

        return '\n'.join(content)

    def generate_readme(self):
        """Generate README files for root and subdirectories"""
        start_time = time.time()

        # Group scripts by directory
        scripts_by_dir: Dict[str, List[Dict]] = {}
        for script_info in self.scripts.values():
            dir_name = os.path.dirname(script_info['path']) or 'Root'
            if dir_name not in scripts_by_dir:
                scripts_by_dir[dir_name] = []
            scripts_by_dir[dir_name].append(script_info)

        # Generate main README with all scripts
        print("Generating main README.md...")
        root_readme_content = self.generate_readme_content(list(self.scripts.values()), is_root=True)
        root_readme_path = self.base_dir / 'README.md'
        with open(root_readme_path, 'w', encoding='utf-8') as f:
            f.write(root_readme_content)
        print(f"Generated README.md at {root_readme_path}")

        # Generate README for each subdirectory
        for dir_name, scripts in scripts_by_dir.items():
            if dir_name != 'Root':
                print(f"Generating README for {dir_name}...")
                dir_path = self.base_dir / dir_name
                readme_content = self.generate_readme_content(scripts)
                readme_path = dir_path / 'README.md'
                readme_path.parent.mkdir(parents=True, exist_ok=True)
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                print(f"Generated README.md at {readme_path}")

        elapsed_time = time.time() - start_time
        print(f"Documentation generation completed in {elapsed_time:.2f} seconds")

# Common Python standard library modules to exclude from dependencies list
stdlib_modules = {
    'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections',
    'concurrent', 'contextlib', 'copy', 'csv', 'datetime', 'decimal',
    'email', 'enum', 'functools', 'getopt', 'glob', 'hashlib', 'hmac',
    'html', 'http', 'importlib', 'inspect', 'io', 'itertools', 'json',
    'logging', 'math', 'multiprocessing', 'operator', 'os', 'pathlib',
    'pickle', 'platform', 'pprint', 'queue', 'random', 're', 'secrets',
    'shutil', 'signal', 'socket', 'sqlite3', 'statistics', 'string',
    'subprocess', 'sys', 'tempfile', 'threading', 'time', 'traceback',
    'types', 'typing', 'unittest', 'urllib', 'uuid', 'warnings', 'weakref',
    'xml', 'zipfile', 'zlib'
}

def parse_args():
    parser = argparse.ArgumentParser(description="Generate README documentation for Python scripts")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory containing Python scripts (default: current directory)")
    parser.add_argument("-e", "--exclude", nargs="+", default=None,
                        help="Directories to exclude (in addition to defaults)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    # Resolve the directory path
    scripts_dir = Path(args.directory).resolve()
    print(f"Analyzing Python files in: {scripts_dir}")

    # Initialize exclude directories
    exclude_dirs = ["venv", "__pycache__", ".git", ".github", ".vscode", "build", "dist", "node_modules"]
    if args.exclude:
        exclude_dirs.extend(args.exclude)

    # Initialize and run the analyzer
    analyzer = ScriptAnalyzer(scripts_dir, exclude_dirs)
    analyzer.analyze_scripts()
    analyzer.generate_readme()