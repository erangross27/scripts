# Directory Scripts Documentation

## Available Scripts


### ai_security_service.py

**Path:** `system_utilities\ai_security_service.py`

**Description:**
This script handles ai security service.

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 5.7 KB
- Lines of code: 146 (of 194 total)

**Functions:**
- `get_current_user`: Retrieves current user based on token
- `get_db`: Retrieves db
- `cache_response`: Cache response based on expire time

**Classes:**
- `User`: Represents a user
- `UserCreate`: Represents a user create
- `UserResponse`: Represents a user response

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
Could not parse file for description

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 87.4 KB
- Lines of code: 1318 (of 1918 total)

### anthropic_claude_chat_for_linux.py

**Path:** `system_utilities\anthropic_claude_chat_for_linux.py`

**Description:**
Could not parse file for description

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 88.8 KB
- Lines of code: 1341 (of 1975 total)

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

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 5.0 KB
- Lines of code: 111 (of 156 total)

**Functions:**
- `browse_audio_file`: Browse audio file based on label
- `browse_save_location`: Browse save location based on label
- `convert_m4a_to_wav`: Converts m4a to wav based on audio file path
- `convert_stereo_to_mono`: Converts stereo to mono based on audio file path
- `convert_audio_to_text`: Converts audio to text based on audio file path, save location, filename
- `main`: Main

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

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 12.2 KB
- Lines of code: 267 (of 335 total)

**Functions:**
- `check_dependencies`: Check dependencies
- `check_module`: Check module based on module
- `load_config`: Load config
- `main`: Main

**Classes:**
- `Config`: Represents a config
- `DiskSpaceAlertService`: Provides disk space alert functionality
  - Methods:
    - `__init__`: Special method __init__
    - `SvcStop`: Svcstop
    - `SvcDoRun`: Svcdorun
    - `main`: Main
    - `check_disk_space`: Check disk space
    - `get_disks`: Retrieves disks
    - `send_alert`: Send alert based on disk
    - `get_email_credentials`: Retrieves email credentials
    - `configure_email`: Configure email

**Dependencies:**
- cryptography
- dataclasses
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

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 1.4 KB
- Lines of code: 23 (of 36 total)

**Dependencies:**
- psutil

### hour_calculator.py

**Path:** `system_utilities\hour_calculator.py`

**Description:**
This script handles hour calculator.

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 10.1 KB
- Lines of code: 229 (of 291 total)

**Functions:**
- `parse_time`: Convert a string 'hours:minutes' or 'hours' into total minutes as a float
- `format_hours`: Converts total minutes into 'hours:minutes' string, with rounding to nearest minute
- `evaluate_expression`: Given a list of tokens in the form [time_in_minutes, operator, time_in_minutes, operator,
- `main`: Main

**Classes:**
- `TimeCalculator`: Represents a time calculator
  - Methods:
    - `__init__`: Special method __init__
    - `on_button_clicked`: On button clicked
    - `clear_all`: Reset everything
    - `process_operator`: 1
    - `process_equals`: 1
    - `update_expression_display`: Updates the expression display with the newly entered time or operator
    - `show_error`: Show error based on message

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

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 1.8 KB
- Lines of code: 28 (of 50 total)

**Functions:**
- `system_discovery`: Function to gather and print system information

**Dependencies:**
- psutil