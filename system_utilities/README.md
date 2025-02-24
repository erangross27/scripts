# Directory Scripts Documentation

## Available Scripts


### ai_security_service.py

**Path:** `system_utilities\ai_security_service.py`

**Description:**
No description available

**Dependencies:**
- bcrypt
- fastapi
- jwt
- pydantic
- redis
- sqlalchemy
- uvicorn

### anthropic_claude_chat.py

**Path:** `system_utilities\anthropic_claude_chat.py`

**Description:**
ClaudeChat Application

This application provides a graphical user interface for interacting with the Anthropic Claude AI model. 
It allows users to have conversations with the AI, upload and analyze files, and manage conversation history.

Key features:
- Chat interface with Claude AI
- File upload and analysis (text, PDF, images, Word, Excel)
- Conversation history management
- Code block highlighting and copying
- Multiple Claude model selection

The application uses PyQt5 for the GUI, SQLite for storing conversation history, 
and integrates with various libraries for file handling and API communication.

Main classes:
- ClaudeChat: The main application window and logic
- ConversationHistory: Manages conversation storage and retrieval
- MessageProcessor: Handles asynchronous API calls to Claude
- PythonHighlighter: Provides syntax highlighting for code blocks

Usage:
Run this script to launch the ClaudeChat application. An Anthropic API key is required.

Dependencies:
- PyQt5
- anthropic
- fitz (PyMuPDF)
- Pillow
- win32com

Note: This application is designed to run on Windows due to some Windows-specific features.

**Dependencies:**
- PIL
- PyQt5
- anthropic
- ctypes
- fitz
- httpx
- pyexpat
- pythoncom
- requests
- win32com
- winreg

### anthropic_claude_chat_for_linux.py

**Path:** `system_utilities\anthropic_claude_chat_for_linux.py`

**Description:**
ClaudeChat Application

This application provides a graphical user interface for interacting with the Claude AI model
using the Anthropic API. It allows users to have conversations with the AI, upload files for
analysis, and manage conversation history.

Key features:
- Chat interface for interacting with Claude AI
- File upload and analysis (text, PDF, images)
- Conversation history management
- Code block detection and syntax highlighting
- Multiple Claude model selection

The application uses PyQt5 for the GUI, sqlite3 for local storage of conversation history,
and integrates with the Anthropic API for AI interactions.

Usage:
Run this script to launch the ClaudeChat application. Users will need to provide their
Anthropic API key on first run or if it's not set in the environment variables.

Dependencies:
- PyQt5
- anthropic
- fitz (PyMuPDF)
- Pillow
- requests
- logging

Note: Ensure all required dependencies are installed and the Anthropic API key is available
before running the application.

**Dependencies:**
- PIL
- PyQt5
- anthropic
- ctypes
- fitz
- httpx
- platform
- pyexpat
- requests
- subprocess

### convert_audio_to_text.py

**Path:** `system_utilities\convert_audio_to_text.py`

**Description:**
Audio to Text Converter

This script provides a graphical user interface for converting audio files to text using Google Cloud Speech-to-Text API.

Features:
- Browse and select audio files (supports .m4a format)
- Choose save location for the output text file
- Convert audio to text with automatic punctuation and profanity filtering
- Supports Hebrew language (iw-IL)

Dependencies:
- os
- tkinter
- google.cloud.speech
- wave
- audioop
- pydub

Note: Requires a valid Google Cloud credentials file.

Usage:
1. Run the script
2. Use the GUI to select an audio file and save location
3. Enter a filename for the output
4. Click "Convert" to process the audio and generate text

The script handles audio format conversion (m4a to wav) and channel conversion (stereo to mono) automatically.

**Dependencies:**
- audioop
- google
- pydub
- tkinter
- wave

### disk-space-alert-service.py

**Path:** `system_utilities\disk-space-alert-service.py`

**Description:**
Disk Space Alert Service

This script implements a Windows service that monitors disk space on local drives
and sends email alerts when available space falls below a configured threshold.

Features:
- Runs as a Windows service
- Configurable check interval and minimum free space threshold
- Email alerts with customizable SMTP settings
- Encrypted storage of email credentials in Windows Registry
- Logging with rotation to prevent excessive log file growth

Usage:
python script.py [install|start|stop|remove|update|reconfigure]
- install: Install the service and configure email settings
- start: Start the service
- stop: Stop the service
- remove: Remove the service
- update: Update the service configuration
- reconfigure: Reconfigure email settings

Dependencies:
psutil, win32event, win32service, win32serviceutil, servicemanager, winreg, cryptography

Configuration:
Settings are stored in a 'config.json' file in the same directory as the script.
Email credentials are securely stored in the Windows Registry.

Note: This script is designed to run on Windows systems only.

**Dependencies:**
- cryptography
- dataclasses
- email
- getpass
- psutil
- servicemanager
- smtplib
- win32event
- win32service
- win32serviceutil
- winreg

### disksizeinfo.py

**Path:** `system_utilities\disksizeinfo.py`

**Description:**
This script provides information about disk usage and CPU utilization.

It uses the psutil library to gather and display the following information:
1. Free space available on C: and D: drives (in GB)
2. CPU usage statistics for each CPU core (user, system, and idle percentages)

The script first checks disk partitions, focusing on C: and D: drives,
and reports the free space available on each.

Then, it collects CPU usage data for a 1-second interval and displays
the usage percentages for each CPU core.

Requirements:
- psutil library must be installed

Note: This script is designed for Windows systems, as it specifically looks for
C: and D: drives.

**Dependencies:**
- psutil

### hour_calculator.py

**Path:** `system_utilities\hour_calculator.py`

**Description:**
No description available

**Dependencies:**
- PyQt5

### system_discovery.py

**Path:** `system_utilities\system_discovery.py`

**Description:**
This script provides functionality to gather and display system information.

It uses the platform, socket, and psutil modules to collect various details about the system,
including the operating system, machine architecture, hostname, IP address, CPU cores, and total RAM.

The main function, system_discovery(), prints this information to the console.

When run as a standalone script, it automatically executes the system_discovery() function.

Dependencies:
    - platform
    - socket
    - psutil

Usage:
    Run the script directly to see the system information output.
    Alternatively, import the system_discovery function to use it in other scripts.

**Dependencies:**
- platform
- psutil