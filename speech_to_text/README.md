# Directory Scripts Documentation

## Available Scripts


### build_app.py

**Path:** `speech_to_text\build_app.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 4.2 KB
- Lines of code: 106 (of 143 total)

**Functions:**
- `build_executable`: No documentation

### transcription_app.py

**Path:** `speech_to_text\transcription_app.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 21.0 KB
- Lines of code: 445 (of 579 total)

**Functions:**
- `get_embedded_api_key`: No documentation
- `main`: No documentation

**Classes:**
- `ProofreadingDialog`: No documentation
  - Methods:
    - `__init__`: No documentation
- `ProofreadingWorker`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `run`: No documentation
- `TranscriptionWorker`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `format_transcript`: No documentation
    - `split_audio`: No documentation
    - `run`: No documentation
- `TranscriptionApp`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `toggle_maximize`: No documentation
    - `copy_text`: No documentation
    - `init_ui`: No documentation
    - `mousePressEvent`: No documentation
    - `mouseMoveEvent`: No documentation
    - `update_status`: No documentation
    - `browse_file`: No documentation
    - `start_transcription`: No documentation
    - `start_proofreading`: No documentation
    - `proofreading_complete`: No documentation
    - `proofreading_error`: No documentation
    - `update_progress`: No documentation
    - `transcription_complete`: No documentation
    - `save_transcript`: No documentation
    - `transcription_error`: No documentation

**Dependencies:**
- PyQt5
- openai
- pydub