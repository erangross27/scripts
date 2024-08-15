import os
import ast
import sys
import platform
import pkgutil
from collections import defaultdict

def get_imports(file_path):
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

def normalize_package_name(package):
    package_mappings = {
        'PIL': 'Pillow',
        'bidi': 'python-bidi',
        'cv2': 'opencv-python',
        # Add more mappings here if needed
    }
    return package_mappings.get(package, package)

def get_stdlib_modules():
    stdlib_modules = set(sys.builtin_module_names)
    stdlib_modules.update([m.name for m in pkgutil.iter_modules()])
    return stdlib_modules

def is_windows_specific(package):
    windows_specific_modules = {
        'win32', 'winreg', '_win', 'msvcrt', 'nt', 'winsound', 'win32com', 'win32api',
        'win32gui', 'win32con', 'win32event', 'win32evtlog', 'win32file', 'win32security',
        'pywintypes', 'pythoncom', 'winshell', 'servicemanager', 'wmi'
    }
    return package.lower() in windows_specific_modules or any(package.startswith(prefix) for prefix in windows_specific_modules)


def get_all_requirements(output_file):
    current_dir = os.getcwd()
    all_imports = defaultdict(set)
    is_windows = platform.system() == "Windows"
    stdlib_modules = get_stdlib_modules()

    for filename in os.listdir(current_dir):
        if filename.endswith(".py"):
            file_path = os.path.join(current_dir, filename)
            imports = get_imports(file_path)
            for imp in imports:
                if imp.lower() not in stdlib_modules and (is_windows or not is_windows_specific(imp)):
                    normalized_imp = normalize_package_name(imp)
                    all_imports[normalized_imp].add(filename)

    with open(output_file, 'w') as f:
        for imp, files in sorted(all_imports.items()):
            f.write(f"{imp} # Used in: {', '.join(sorted(files))}\n")

    print(f"Requirements have been saved to {output_file}")

def main():
    output_file = "requirements.txt"
    get_all_requirements(output_file)

if __name__ == "__main__":
    main()
