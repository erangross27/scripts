# Directory Scripts Documentation

## Available Scripts


### build_app.py

**Path:** `speech_to_text\build_app.py`

**Description:**
This script handles build app.

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 4.3 KB
- Lines of code: 112 (of 150 total)

**Functions:**
- `build_executable`: Build executable

### transcription_app.py

**Path:** `speech_to_text\transcription_app.py`

**Description:**
This script handles transcription app.

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 22.7 KB
- Lines of code: 535 (of 670 total)

**Functions:**
- `get_embedded_api_key`: Retrieves embedded api key
- `main`: Main

**Classes:**
- `ProofreadingDialog`: Represents a proofreading dialog
  - Methods:
    - `__init__`: Special method __init__
- `ProofreadingWorker`: Represents a proofreading worker
  - Methods:
    - `__init__`: Special method __init__
    - `run`: Run
- `TranscriptionWorker`: Represents a transcription worker
  - Methods:
    - `__init__`: Special method __init__
    - `format_transcript`: Format transcript based on text
    - `split_audio`: Split audio based on audio segment, max size mb
    - `run`: Run
- `TranscriptionApp`: Represents a transcription app
  - Methods:
    - `__init__`: Special method __init__
    - `toggle_maximize`: Toggle maximize
    - `copy_text`: Copy text
    - `init_ui`: Init ui
    - `mousePressEvent`: Mousepressevent based on event
    - `mouseMoveEvent`: Mousemoveevent based on event
    - `update_status`: Updates status based on text
    - `browse_file`: Browse file
    - `start_transcription`: Start transcription
    - `start_proofreading`: Start proofreading
    - `proofreading_complete`: Proofreading complete based on corrected text
    - `proofreading_error`: Proofreading error based on error message
    - `update_progress`: Updates progress based on status, value
    - `transcription_complete`: Transcription complete based on transcript
    - `save_transcript`: Save transcript
    - `transcription_error`: Transcription error based on error message

**Dependencies:**
- PyQt5
- openai
- pydub