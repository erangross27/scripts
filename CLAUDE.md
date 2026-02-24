# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

A collection of 60+ standalone Python utility scripts organized into 10 category directories. Each script is typically self-contained. There is no central application entry point — scripts are run individually.

## Running Scripts

```bash
python <category>/<script_name>.py
```

For scripts with GUI (PyQt6), ensure a display is available. Network Monitor is the exception — it has a modular CLI structure:

```bash
python "network monitor/network_monitor.py" --help
```

## Installing Dependencies

```bash
# Install all core dependencies
pip install -r requirements.txt

# Regenerate requirements.txt from actual imports
python setup_requirements.py
```

Some optional dependencies (torch, qiskit, scapy, pycuda, google-cloud-*) are only needed for specific scripts. Install selectively as needed.

## Building Executables

```bash
# PDF Compressor (prompts for portable vs light mode)
build_windows.bat

# YouTube Downloader
python video_processing/youtube_downloader/build_app.py

# Speech-to-Text Transcription
python speech_to_text/build_app.py
```

Both `build_app.py` scripts use PyInstaller to create standalone Windows executables.

## Architecture

### GUI Framework
- **PyQt6** is the current standard (use this for new GUI scripts)
- Older scripts may use PyQt5 or Tkinter — migrate to PyQt6 when modifying them
- Long-running operations use `QThread` subclasses to keep the GUI responsive

### Directory Structure

| Directory | Contents |
|-----------|----------|
| `file_management/` | PDF tools (compress, number pages) |
| `healthcare/` | ML classification (breast cancer detector) |
| `image_processing/` | OpenCV/Pillow image tools, OCR, watermark removal, dataset prep |
| `machine_learning/` | PyTorch MNIST training, GPU benchmarks, YOLOv5 training |
| `miscellaneous/` | GPU/CUDA benchmarks, system info, utility scripts |
| `network monitor/` | Modular packet capture + ML anomaly detection (Scapy, PyTorch, sklearn) |
| `quantum_computing/` | IBM Quantum algorithms via Qiskit (Grover, Deutsch-Jozsa, RNG) |
| `speech_to_text/` | Audio transcription via Anthropic/OpenAI APIs |
| `system_utilities/` | FastAPI/SQLAlchemy backend, disk monitoring, time calculator, Qwen chat |
| `video_processing/` | FFmpeg/Moviepy video tools, YouTube downloader (yt-dlp + PyQt6) |

### Network Monitor Module Structure
The `network monitor/` directory is the only multi-module package:
```
network monitor/
├── network_monitor.py      # CLI entry point (argparse)
├── packet_capture.py       # Scapy sniff wrapper (multiprocessing)
├── packet_analyzer.py      # Packet parsing (IPv4/IPv6/DNS)
├── anomaly_detector.py     # ML anomaly detection
├── feature_extractor.py    # Traffic feature engineering
├── interface_manager.py    # NIC enumeration
├── config/                 # Feature + whitelist configuration
├── models/                 # PyTorch deep packet analyzer, persistent detector
└── utils/                  # Network and packet utilities
```

### External API Dependencies
Scripts may require API keys in environment variables or `.env` files (not committed):
- `OPENAI_API_KEY` — OpenAI and transcription scripts
- `ANTHROPIC_API_KEY` — transcription app
- Google Cloud credentials — OCR and Speech-to-Text scripts
- IBM Quantum credentials — quantum computing scripts

### Key Technical Patterns
- **GPU benchmarking**: `miscellaneous/` scripts follow a consistent pattern: run operation on CPU, run on GPU (CUDA), compare timing and memory
- **ML models**: Saved as `.joblib` files (e.g., `anomaly_model.joblib` in root)
- **Windows-specific**: Several scripts use `wmi`, `win32serviceutil`, or Windows Registry — these will not run on other platforms
- **`network monitor/` has spaces in directory name** — quote paths when referencing it in shell
