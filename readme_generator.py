import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

class ScriptAnalyzer:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.scripts: Dict[str, Dict] = {}
        
    def extract_docstring(self, file_path: Path) -> str:
        """Extract the module docstring from a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
                docstring = ast.get_docstring(tree)
                return docstring if docstring else "No description available"
        except Exception:
            return "Could not parse file for description"

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extract import statements from a Python file"""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.add(name.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
        except Exception:
            pass
        return imports

    def analyze_scripts(self):
        """Analyze all Python scripts in the directory structure"""
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.base_dir)
                    
                    self.scripts[str(relative_path)] = {
                        'path': str(relative_path),
                        'description': self.extract_docstring(file_path),
                        'requirements': self.extract_imports(file_path)
                    }

    def generate_readme_content(self, scripts_list: List[Dict], is_root: bool = False) -> str:
        """Generate README content for a specific directory"""
        content = []
        
        if is_root:
            content.extend([
                "# Scripts Directory Documentation",
                "\nThis repository contains various Python scripts organized by functionality.",
                "\n## Table of Contents\n"
            ])

            # Group scripts by directory for TOC
            scripts_by_dir: Dict[str, List[Dict]] = {}
            for script_info in self.scripts.values():
                dir_name = os.path.dirname(script_info['path']) or 'Root'
                if dir_name not in scripts_by_dir:
                    scripts_by_dir[dir_name] = []
                scripts_by_dir[dir_name].append(script_info)

            # Generate Table of Contents
            for dir_name in sorted(scripts_by_dir.keys()):
                clean_name = dir_name.replace('\\', '/')
                if clean_name == 'Root':
                    content.append(f"- [Root Scripts](#root-scripts)")
                else:
                    content.append(f"- [{clean_name}](#{clean_name.lower().replace('/', '-')})")

            content.append("\n## Root Scripts\n")
        else:
            content.extend([
                "# Directory Scripts Documentation",
                "\n## Available Scripts\n"
            ])

        for script_info in sorted(scripts_list, key=lambda x: x['path']):
            script_name = os.path.basename(script_info['path'])
            content.extend([
                f"\n### {script_name}",
                f"\n**Path:** `{script_info['path']}`",
                f"\n**Description:**\n{script_info['description']}",
            ])
            
            if script_info['requirements']:
                content.append("\n**Dependencies:**")
                for req in sorted(script_info['requirements']):
                    if req not in stdlib_modules:
                        content.append(f"- {req}")

        return '\n'.join(content)

    def generate_readme(self):
        """Generate README.md files in root and subdirectories"""
        # Group scripts by directory
        scripts_by_dir: Dict[str, List[Dict]] = {}
        for script_info in self.scripts.values():
            dir_name = os.path.dirname(script_info['path']) or 'Root'
            if dir_name not in scripts_by_dir:
                scripts_by_dir[dir_name] = []
            scripts_by_dir[dir_name].append(script_info)

        # Generate README for root directory with all scripts
        root_readme_content = self.generate_readme_content(list(self.scripts.values()), is_root=True)
        root_readme_path = self.base_dir / 'README.md'
        with open(root_readme_path, 'w', encoding='utf-8') as f:
            f.write(root_readme_content)
        print(f"Generated README.md at {root_readme_path}")

        # Generate README for each subdirectory
        for dir_name, scripts in scripts_by_dir.items():
            if dir_name != 'Root':
                dir_path = self.base_dir / dir_name
                readme_content = self.generate_readme_content(scripts)
                readme_path = dir_path / 'README.md'
                readme_path.parent.mkdir(parents=True, exist_ok=True)
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                print(f"Generated README.md at {readme_path}")

# List of Python standard library modules
stdlib_modules = {
    'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 
    'contextlib', 'copy', 'csv', 'datetime', 'decimal', 'enum',
    'functools', 'glob', 'hashlib', 'hmac', 'io', 'itertools', 'json',
    'logging', 'math', 'multiprocessing', 'os', 'pathlib', 'pickle',
    'random', 're', 'socket', 'sqlite3', 'string', 'sys', 'threading',
    'time', 'typing', 'uuid', 'warnings', 'xml', 'zipfile'
}

if __name__ == '__main__':
    scripts_dir = "C:/Users/EranGross/scripts"
    analyzer = ScriptAnalyzer(scripts_dir)
    analyzer.analyze_scripts()
    analyzer.generate_readme()