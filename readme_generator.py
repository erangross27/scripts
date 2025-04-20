# readme_generator.py
import os
import sys
import time
import argparse
import datetime
import ast
import nbformat
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Set

# Standard library modules to exclude from dependency listing
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
    'xml', 'zipfile', 'zlib', 'tokenize', 'token'
}

class ScriptAnalyzer:
    def __init__(self, base_dir: Path, exclude_dirs: List[str] = None, verbose: bool = False):
        self.base_dir = base_dir
        self.exclude_dirs = exclude_dirs or []
        self.verbose = verbose
        self.scripts: Dict[str, Dict[str, Any]] = {}
        self.total_files = 0
        self.analyzed_count = 0

    def extract_docstring(self, file_path: Path) -> str:
        """Extract the module-level docstring from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            return ast.get_docstring(tree) or "No documentation"
        except Exception as e:
            if self.verbose:
                print(f"Error extracting docstring from {file_path}: {str(e)}")
            return "No documentation"

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extract imported modules from a Python file."""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except Exception as e:
            if self.verbose:
                print(f"Error extracting imports from {file_path}: {str(e)}")
        return imports

    def extract_functions_and_classes(self, file_path: Path) -> Dict[str, Any]:
        """Extract top-level functions and classes with their docstrings."""
        functions_and_classes = {'functions': [], 'classes': []}
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                tree = ast.parse(content)

                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.FunctionDef):
                        doc = ast.get_docstring(node) or "No documentation"
                        functions_and_classes['functions'].append({
                            'name': node.name,
                            'docstring': doc,
                            'line_number': node.lineno
                        })
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
            if self.verbose:
                print(f"Error parsing functions/classes in {file_path}: {str(e)}")
            return {'functions': [], 'classes': []}

    def get_file_stats(self, file_path: Path) -> Dict[str, Any]:
        """Get file statistics: size, last modified, lines, code lines."""
        stats = {}
        try:
            size = file_path.stat().st_size
            mod_time = file_path.stat().st_mtime
            last_modified = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            stats = {
                'size': size,
                'last_modified': last_modified,
                'total_lines': total_lines,
                'code_lines': code_lines
            }
        except Exception as e:
            if self.verbose:
                print(f"Error getting stats for {file_path}: {str(e)}")
            stats = {
                'size': 0,
                'last_modified': 'Unknown',
                'total_lines': 0,
                'code_lines': 0
            }
        return stats

    def process_notebook(self, file_path: Path) -> Dict[str, Any]:
        """Process Jupyter Notebook (.ipynb) files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                notebook = nbformat.read(f, as_version=4)

            description = "No description available"
            for cell in notebook.cells:
                if cell.cell_type == 'markdown':
                    # Take the first line of the markdown cell as description
                    description = cell.source.split('\n', 1)[0].strip('# ').strip()
                    break

            code_cells = sum(1 for cell in notebook.cells if cell.cell_type == 'code')
            markdown_cells = sum(1 for cell in notebook.cells if cell.cell_type == 'markdown')

            # Extract imports from code cells
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
                        continue

            return {
                'description': description,
                'code_cells': code_cells,
                'markdown_cells': markdown_cells,
                'requirements': imports
            }

        except Exception as e:
            if self.verbose:
                print(f"Error processing notebook {file_path}: {str(e)}")
            return {
                'description': f"Error: {str(e)}",
                'code_cells': 0,
                'markdown_cells': 0,
                'requirements': set()
            }

    def update_file_docstrings(self, file_path: Path) -> bool:
        """Placeholder for updating missing docstrings in a Python file."""
        # Implement or integrate a real updater as needed
        # For now, assume no update is performed
        return False

    def analyze_file(self, file_path: Path, relative_path: Path) -> Dict[str, Any]:
        """Analyze a single file, return structured data."""
        result = {'path': str(relative_path)}
        if str(file_path).endswith('.py'):
            was_updated = self.update_file_docstrings(file_path)
            result['description'] = self.extract_docstring(file_path)
            result['requirements'] = self.extract_imports(file_path)
            result.update(self.extract_functions_and_classes(file_path))
            result['stats'] = self.get_file_stats(file_path)
            result['type'] = 'python'
            result['was_updated'] = was_updated
        elif str(file_path).endswith('.ipynb'):
            notebook_data = self.process_notebook(file_path)
            result['description'] = notebook_data['description']
            result['requirements'] = notebook_data['requirements']
            result['code_cells'] = notebook_data['code_cells']
            result['markdown_cells'] = notebook_data['markdown_cells']
            result['stats'] = self.get_file_stats(file_path)
            result['type'] = 'notebook'
            result['was_updated'] = False
        else:
            # Unknown file type
            result['description'] = "Unknown file type"
            result['requirements'] = set()
            result['stats'] = {}
            result['type'] = 'unknown'
            result['was_updated'] = False

        # Progress output
        self.analyzed_count += 1
        if self.total_files > 0:
            progress = (self.analyzed_count / self.total_files) * 100
            sys.stdout.write(f"\rAnalyzing files: {self.analyzed_count}/{self.total_files} ({progress:.1f}%)")
            sys.stdout.flush()

        return result

    def should_exclude(self, path: Path) -> bool:
        """Determine if a directory should be excluded."""
        return any(excluded in path.parts for excluded in self.exclude_dirs)

    def analyze_scripts(self):
        """Walk directory and analyze all Python and notebook files."""
        # Count total files
        self.total_files = 0
        for root, _, files in os.walk(self.base_dir):
            root_path = Path(root)
            if self.should_exclude(root_path):
                continue
            for file in files:
                if file.endswith('.py') or file.endswith('.ipynb'):
                    self.total_files += 1
        print(f"Found {self.total_files} files to analyze.")

        self.analyzed_count = 0
        # Analyze in parallel
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = []
            for root, _, files in os.walk(self.base_dir):
                root_path = Path(root)
                if self.should_exclude(root_path):
                    continue
                for file in files:
                    if file.endswith('.py') or file.endswith('.ipynb'):
                        file_path = root_path / file
                        relative_path = file_path.relative_to(self.base_dir)
                        futures.append(executor.submit(self.analyze_file, file_path, relative_path))

            # Collect results
            for future in futures:
                result = future.result()
                self.scripts[result['path']] = result
        print(f"\nAnalyzed {self.analyzed_count} files.")

    def generate_readme_content(self, scripts_list: List[Dict], is_root: bool = False) -> str:
        """Generate Markdown content for README files."""
        content = []

        # Header and introduction
        if is_root:
            content.extend([
                "# Scripts Directory Documentation\n",
                "This repository contains various Python scripts and Jupyter notebooks organized by functionality.\n",
                "## Table of Contents\n"
            ])
            # Organize scripts by directory
            scripts_by_dir: Dict[str, List[Dict]] = {}
            for script_info in self.scripts.values():
                dir_name = os.path.dirname(script_info['path']) or 'Root'
                scripts_by_dir.setdefault(dir_name, []).append(script_info)

            for dir_name in sorted(scripts_by_dir.keys()):
                clean_name = dir_name.replace('\\', '/')
                if clean_name == 'Root':
                    content.append(f"- [Root Scripts](#root-scripts)")
                else:
                    anchor = clean_name.lower().replace('/', '-')
                    content.append(f"- [{clean_name}](#{anchor})")

            content.append("\n## Root Scripts\n")
        else:
            # Subdirectory README header
            content.extend([
                "# Directory Scripts Documentation\n",
                "\n## Available Scripts\n"
            ])

        for script in sorted(scripts_list, key=lambda x: x['path']):
            script_name = os.path.basename(script['path'])
            content.extend([
                f"\n### {script_name}",
                f"\n**Path:** `{script['path']}`",
                f"\n**Description:**\n{script['description']}\n",
            ])

            # File stats
            stats = script.get('stats', {})
            if stats:
                size_kb = stats.get('size', 0) / 1024
                last_mod = stats.get('last_modified', 'Unknown')
                code_lines = stats.get('code_lines', 0)
                total_lines = stats.get('total_lines', 0)
                content.extend([
                    "\n**File Info:**",
                    f"- Last modified: {last_mod}",
                    f"- Size: {size_kb:.1f} KB",
                    f"- Lines of code: {code_lines} (of {total_lines} total)",
                ])

            # Notebook info
            if script.get('type') == 'notebook':
                content.extend([
                    "\n**Notebook Info:**",
                    f"- Code cells: {script.get('code_cells', 0)}",
                    f"- Markdown cells: {script.get('markdown_cells', 0)}",
                ])

            # Functions
            functions = script.get('functions', [])
            if functions:
                content.append("\n**Functions:**")
                for func in sorted(functions, key=lambda x: x['line_number']):
                    summary = func['docstring'].split('.')[0]
                    content.append(f"- `{func['name']}`: {summary}")

            # Classes
            classes = script.get('classes', [])
            if classes:
                content.append("\n**Classes:**")
                for cls in sorted(classes, key=lambda x: x['line_number']):
                    cls_summary = cls['docstring'].split('.')[0]
                    content.append(f"- `{cls['name']}`: {cls_summary}")
                    if cls['methods']:
                        content.append("  - Methods:")
                        for method in sorted(cls['methods'], key=lambda x: x['line_number']):
                            method_summary = method['docstring'].split('.')[0]
                            content.append(f"    - `{method['name']}`: {method_summary}")

            # Requirements (dependencies)
            requirements = script.get('requirements', set())
            non_stdlib_reqs = [req for req in sorted(requirements) if req not in stdlib_modules]
            if non_stdlib_reqs:
                content.append("\n**Dependencies:**")
                for req in non_stdlib_reqs:
                    content.append(f"- {req}")

        return '\n'.join(content)

    def generate_readme(self):
        """Generate README.md files for root and subdirectories."""
        start_time = time.time()
        # Group scripts by directory
        scripts_by_dir: Dict[str, List[Dict]] = {}
        for script in self.scripts.values():
            dir_name = os.path.dirname(script['path']) or 'Root'
            scripts_by_dir.setdefault(dir_name, []).append(script)

        # Generate root README
        print("Generating main README.md...")
        root_content = self.generate_readme_content(list(self.scripts.values()), is_root=True)
        root_path = self.base_dir / 'README.md'
        with open(root_path, 'w', encoding='utf-8') as f:
            f.write(root_content)
        print(f"Generated {root_path}")

        # Generate READMEs for subdirectories
        for dir_name, scripts in scripts_by_dir.items():
            if dir_name != 'Root':
                print(f"Generating README for {dir_name}...")
                dir_path = self.base_dir / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                readme_path = dir_path / 'README.md'
                content = self.generate_readme_content(scripts)
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Generated {readme_path}")

        elapsed = time.time() - start_time
        print(f"Documentation generation completed in {elapsed:.2f} seconds.")

# Utility functions for argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description="Generate and update documentation for Python scripts")
    parser.add_argument("directory", nargs="?", default=".", help="Directory containing scripts")
    parser.add_argument("-e", "--exclude", nargs="+", default=None, help="Directories to exclude")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--update-only", action="store_true", help="Only update docstrings")
    parser.add_argument("--readme-only", action="store_true", help="Only generate READMEs")
    parser.add_argument("--skip-notebooks", action="store_true", help="Skip .ipynb files")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    base_dir = Path(args.directory).resolve()
    print(f"Analyzing Python files in: {base_dir}")
    exclude_dirs = ["venv", "__pycache__", ".git", ".github", ".vscode", "build", "dist", "node_modules"]
    if args.exclude:
        exclude_dirs.extend(args.exclude)

    analyzer = ScriptAnalyzer(base_dir, exclude_dirs, verbose=args.verbose)

    if not args.readme_only:
        analyzer.analyze_scripts()

    if not args.update_only:
        analyzer.generate_readme()