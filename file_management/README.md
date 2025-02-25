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
- Last modified: 2025-02-18 10:38:35
- Size: 4.7 KB
- Lines of code: 93 (of 119 total)

**Functions:**
- `compress_pdf`: No documentation
- `estimate_time`: No documentation
- `update_progress`: No documentation
- `select_file`: No documentation
- `compress_file`: No documentation
- `main`: No documentation

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
- Last modified: 2025-02-18 10:38:35
- Size: 11.5 KB
- Lines of code: 205 (of 290 total)

**Classes:**
- `ColorIndicator`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `setColor`: No documentation
    - `paintEvent`: No documentation
- `PDFNumberer`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `initUI`: No documentation
    - `select_color`: No documentation
    - `open_pdf`: No documentation
    - `update_preview`: No documentation
    - `process_pdf`: No documentation

**Dependencies:**
- PyQt5
- fitz