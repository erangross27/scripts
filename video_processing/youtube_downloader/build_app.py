"""
This script handles build app.
"""

import os
import sys
import shutil

def build_executable():
    """
    Build executable.
    """
    # Get the directory of the build script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create build directory in the same location as the build script
    build_dir = os.path.join(current_dir, 'build_output')
    os.makedirs(build_dir, exist_ok=True)
    
    # Change to build directory
    original_dir = os.getcwd()
    os.chdir(build_dir)

    try:
        # Use proper path handling for source script
        script_path = os.path.join(current_dir, 'youtube_downloader.py')

        # Copy the script to build directory
        temp_script = 'temp_script.py'
        shutil.copy2(script_path, temp_script)

        # Rest of your spec file content and build process
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{temp_script}'],
    pathex=[],
    binaries=[
        ('ffmpeg.exe', '.'),
        ('ffprobe.exe', '.')
    ],
    datas=[],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'yt_dlp',
        'yt_dlp.utils',
        'yt_dlp.postprocessor',
        'yt_dlp.extractor',
        'yt_dlp.downloader',
        'yt_dlp.cookies'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTubeDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
'''

        # Write spec file
        spec_file = 'YouTubeDownloader.spec'
        with open(spec_file, 'w') as f:
            f.write(spec_content)

        # Verify FFmpeg files exist
        required_files = ['ffmpeg.exe', 'ffprobe.exe']
        for file in required_files:
            source_file = os.path.join(current_dir, file)
            if os.path.exists(source_file):
                shutil.copy2(source_file, file)
            else:
                print(f"Error: {file} not found in {current_dir}")
                sys.exit(1)

        # Build with PyInstaller using the spec file
        os.system(f'pyinstaller {spec_file}')

        # Move the final executable to a release folder
        dist_dir = os.path.join(current_dir, 'release')
        os.makedirs(dist_dir, exist_ok=True)
        
        exe_path = os.path.join('dist', 'YouTubeDownloader.exe')
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, os.path.join(dist_dir, 'YouTubeDownloader.exe'))
            print(f"\nExecutable copied to: {dist_dir}")
        else:
            print("Error: Executable not found in dist directory")

    finally:
        # Change back to original directory
        os.chdir(original_dir)
        
        # Clean up build directory
        if os.path.exists(build_dir):
            try:
                shutil.rmtree(build_dir)
            except Exception as e:
                print(f"Warning: Could not clean up build directory: {e}")

    print("\nBuild complete! Check the 'release' folder for the executable.")

if __name__ == '__main__':
    build_executable()