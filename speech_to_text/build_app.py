import os
import base64
import sys
import shutil

def build_executable():
    # Create build directory
    build_dir = os.path.join('scripts', 'speech_to_text', 'build_output')
    os.makedirs(build_dir, exist_ok=True)
    
    # Change to build directory
    original_dir = os.getcwd()
    os.chdir(build_dir)

    try:
        # Get API key from environment
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("Error: OPENAI_API_KEY not found in environment variables")
            sys.exit(1)

        # Encode the API key
        encoded_key = base64.b64encode(api_key.encode()).decode()

        # Use proper path handling for source script
        script_path = os.path.join(original_dir, 'scripts', 'speech_to_text', 'transcription_app.py')

        # Read your main script
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: Could not find script at {script_path}")
            print("Current working directory:", os.getcwd())
            sys.exit(1)

        # Replace the placeholder with the encoded key
        content = content.replace('ENCODED_KEY_PLACEHOLDER', encoded_key)

        # Write to a temporary file in build directory
        temp_script = 'temp_script.py'
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(content)

        # Copy FFmpeg files to build directory
        ffmpeg_source_dir = os.path.join(original_dir, 'scripts', 'speech_to_text')
        for file in ['ffmpeg.exe', 'ffprobe.exe']:
            source_file = os.path.join(ffmpeg_source_dir, file)
            if os.path.exists(source_file):
                shutil.copy2(source_file, file)
            else:
                print(f"Error: {file} not found in {ffmpeg_source_dir}")
                sys.exit(1)

        # Create spec file content
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
        'pydub',
        'pydub.audio_segment',
        'openai',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets'
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
    name='AudioTranscriber',
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
        spec_file = 'AudioTranscriber.spec'
        with open(spec_file, 'w') as f:
            f.write(spec_content)

        # Build with PyInstaller using the spec file
        os.system(f'pyinstaller {spec_file}')

        # Move the final executable to a more accessible location
        dist_dir = os.path.join(original_dir, 'scripts', 'speech_to_text', 'release')
        os.makedirs(dist_dir, exist_ok=True)
        
        exe_path = os.path.join('dist', 'AudioTranscriber.exe')
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, os.path.join(dist_dir, 'AudioTranscriber.exe'))
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