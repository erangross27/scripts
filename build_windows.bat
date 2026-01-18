@echo off
echo ===================================================
echo      PDF Compressor - Windows Build Script
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in your PATH.
    pause
    exit /b
)

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install PyQt6 pyinstaller

echo.
echo ===================================================
echo Ghostscript Bundling Options
echo ===================================================
echo 1. Bundle Ghostscript (Makes EXE portable, but larger)
echo    [ACTION REQUIRED] Copy your 'gs' folder (e.g., C:\Program Files\gs\gs10.02.1)
echo    into this directory and rename it to 'ghostscript'.
echo.
echo 2. Do Not Bundle (Requires Ghostscript installed on target machine)
echo.

set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    if not exist "ghostscript" (
        echo.
        echo Error: 'ghostscript' folder not found in current directory.
        echo Please copy your Ghostscript installation here and rename it to 'ghostscript'.
        echo Expected structure: .\ghostscript\bin\gswin64c.exe
        pause
        exit /b
    )
    echo.
    echo Building with bundled Ghostscript...
    pyinstaller --noconsole --onefile --name "PDFCompressor_Portable" ^
                --add-data "ghostscript;ghostscript" ^
                file_management\compress_pdf_qt.py
) else (
    echo.
    echo Building Light Version (System Ghostscript required)...
    pyinstaller --noconsole --onefile --name "PDFCompressor_Light" ^
                file_management\compress_pdf_qt.py
)

echo.
echo ===================================================
echo Build Complete!
echo Executable is located in the 'dist' folder.
echo ===================================================
pause
