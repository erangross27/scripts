"""Build MP3 Player as a standalone Windows executable using PyInstaller."""

import os
import sys
import shutil


def build_executable():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(current_dir, "build_output")
    os.makedirs(build_dir, exist_ok=True)

    original_dir = os.getcwd()
    os.chdir(build_dir)

    try:
        script_path = os.path.join(current_dir, "mp3_player.py")
        temp_script = "mp3_player.py"
        shutil.copy2(script_path, temp_script)

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{temp_script}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtMultimedia',
        'mutagen',
        'mutagen.mp3',
        'mutagen.id3',
        'mutagen.flac',
        'mutagen.mp4',
        'mutagen.oggvorbis',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MP3Player',
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
    entitlements_file=None,
)
"""

        spec_file = "MP3Player.spec"
        with open(spec_file, "w") as f:
            f.write(spec_content)

        print("Building MP3 Player executable...")
        os.system(f"pyinstaller {spec_file}")

        dist_dir = os.path.join(current_dir, "release")
        os.makedirs(dist_dir, exist_ok=True)

        exe_path = os.path.join("dist", "MP3Player.exe")
        if os.path.exists(exe_path):
            dest = os.path.join(dist_dir, "MP3Player.exe")
            shutil.copy2(exe_path, dest)
            print(f"\nExecutable copied to: {dest}")
        else:
            print("Error: Executable not found in dist directory")

    finally:
        os.chdir(original_dir)
        if os.path.exists(build_dir):
            try:
                shutil.rmtree(build_dir)
            except Exception as e:
                print(f"Warning: Could not clean up build directory: {e}")

    print("\nBuild complete! Check the 'release' folder for MP3Player.exe")


if __name__ == "__main__":
    build_executable()
