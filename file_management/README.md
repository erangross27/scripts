# Directory Scripts Documentation


## Available Scripts


### compress_pdf_file.py

**Path:** `file_management\compress_pdf_file.py`

**Description:**
PDF Compressor

This script provides a graphical user interface for compressing PDF files using Ghostscript.
It allows users to select input and output files, and displays a progress bar during compression.

Features:
- File selection for input and output PDFs
- Progress bar to show compression status
- Multithreaded compression to keep the GUI responsive
- Estimated time calculation based on file size
- Error handling for common issues (e.g., missing Ghostscript)

Dependencies:
- subprocess
- tkinter
- os
- threading
- time

Note: This script requires Ghostscript to be installed and accessible in the system PATH.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.1 KB
- Lines of code: 111 (of 137 total)

**Functions:**
- `compress_pdf`: Compress pdf based on input file path, output file path, power
- `estimate_time`: Estimate time based on file size
- `update_progress`: Updates progress based on process, input file, output file, progress bar, compress button
- `select_file`: Select file based on entry, save
- `compress_file`: Compress file
- `main`: Main

**Dependencies:**
- tkinter

### numbering_pdf.py

**Path:** `file_management\numbering_pdf.py`

**Description:**
PDF Page Numberer

This script provides a graphical user interface for adding page numbers to PDF documents.
It allows users to open a PDF file, customize the appearance and position of page numbers,
preview the changes, and save the numbered PDF.

Features:
- Open and preview PDF files
- Customize page number position (left, center, right)
- Set page number color
- Adjust footer offset
- Set starting page number
- Change font size
- Adjust horizontal and vertical offsets
- Preview changes in real-time
- Process and save the numbered PDF

Dependencies:
- PyQt5: For creating the graphical user interface
- PyMuPDF (fitz): For PDF manipulation

Usage:
Run the script and use the GUI to open a PDF, adjust settings, and save the numbered PDF.

Note: This script requires PyQt5 and PyMuPDF to be installed.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 12.1 KB
- Lines of code: 238 (of 323 total)

**Classes:**
- `ColorIndicator`: Represents a color indicator
  - Methods:
    - `__init__`: Special method __init__
    - `setColor`: Setcolor based on color
    - `paintEvent`: Paintevent based on event
- `PDFNumberer`: Represents a p d f numberer
  - Methods:
    - `__init__`: Special method __init__
    - `initUI`: Initui
    - `select_color`: Select color
    - `open_pdf`: Open pdf
    - `update_preview`: Updates preview
    - `process_pdf`: Process pdf

**Dependencies:**
- PyQt5
- fitz