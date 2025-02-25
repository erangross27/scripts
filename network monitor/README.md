# Directory Scripts Documentation

## Available Scripts


### __init__.py

**Path:** `network monitor\__init__.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 0.0 KB
- Lines of code: 0 (of 0 total)

### anomaly_detector.py

**Path:** `network monitor\anomaly_detector.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 4.1 KB
- Lines of code: 73 (of 104 total)

**Classes:**
- `AnomalyDetector`: A class for detecting network traffic anomalies using machine learning
  - Methods:
    - `__init__`: Initialize the AnomalyDetector with a logger
    - `analyze_traffic`: Analyze network traffic for anomalies using machine learning
    - `_generate_anomaly_details`: Generate detailed information about detected anomalies

**Dependencies:**
- feature_extractor
- numpy

### feature_extractor.py

**Path:** `network monitor\feature_extractor.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 4.1 KB
- Lines of code: 95 (of 124 total)

**Classes:**
- `FeatureExtractor`: A class for extracting features from network packets for machine learning analysis
  - Methods:
    - `__init__`: Initialize the FeatureExtractor with predefined feature names
    - `extract_features`: Extract features from a list of packets for machine learning analysis
    - `_extract_packet_features`: Extract features from a single packet

**Dependencies:**
- config
- pandas
- scapy

### interface_manager.py

**Path:** `network monitor\interface_manager.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 5.6 KB
- Lines of code: 92 (of 113 total)

**Classes:**
- `InterfaceManager`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `get_interfaces`: Retrieve a list of active network interfaces along with their IP addresses and netmasks
    - `get_subnet_mask`: Get the subnet mask for a given interface
    - `choose_interface`: Allow user to choose a network interface
    - `setup_interface`: Setup network interface either automatically or based on user choice

**Dependencies:**
- bidi
- netifaces
- psutil
- wmi

### logger_setup.py

**Path:** `network monitor\logger_setup.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 2.4 KB
- Lines of code: 34 (of 59 total)

**Classes:**
- `LoggerSetup`: A class to set up and manage a thread-safe logging system using a queue-based approach
  - Methods:
    - `__init__`: Initialize the logger setup with a queue, logger, and queue listener
    - `_setup_logger`: Configure and return a logger instance with queue handler
    - `_setup_queue_listener`: Set up and return a queue listener with stream handler for console output
    - `get_logger`: Return the configured logger instance
    - `stop_listener`: Stop the queue listener if it exists

### network_monitor.py

**Path:** `network monitor\network_monitor.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 9.3 KB
- Lines of code: 130 (of 173 total)

**Functions:**
- `main`: Entry point of the script - parse arguments and start monitoring

**Classes:**
- `NetworkMonitor`: Main class for monitoring network traffic and detecting anomalies
  - Methods:
    - `__init__`: No documentation
    - `check_root_linux`: Check if script is running with root privileges on Linux systems
    - `run`: Main monitoring loop that captures and analyzes network traffic
    - `_log_results`: Log detected suspicious activities and anomalies
    - `_update_false_positives`: Track and handle potential false positive detections

**Dependencies:**
- anomaly_detector
- interface_manager
- logger_setup
- models
- packet_analyzer
- packet_capture

### packet_analyzer.py

**Path:** `network monitor\packet_analyzer.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 13.4 KB
- Lines of code: 233 (of 292 total)

**Classes:**
- `PacketAnalyzer`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `_is_binary_or_encrypted`: Check if the data appears to be binary or encrypted
    - `_decode_payload`: Try multiple encodings to decode the payload
    - `analyze_traffic`: Analyze network traffic for suspicious activities
    - `_analyze_packets`: Analyze individual packets for suspicious behavior
    - `_check_payload_for_threats`: Check packet payload for potential threats with context
    - `_is_whitelisted`: Check if packet matches any whitelist patterns

**Dependencies:**
- ipaddress
- scapy

### packet_capture.py

**Path:** `network monitor\packet_capture.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 2.4 KB
- Lines of code: 63 (of 76 total)

**Classes:**
- `PacketCapture`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `capture_packets_worker`: No documentation
    - `capture_packets`: No documentation

**Dependencies:**
- scapy
- tqdm

### whitelist_manager.py

**Path:** `network monitor\whitelist_manager.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 4.4 KB
- Lines of code: 106 (of 124 total)

**Classes:**
- `WhitelistManager`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `is_whitelisted`: Check if a packet matches any whitelist rules
    - `is_whitelisted_port`: Check if a port is whitelisted
    - `_check_ip_whitelist`: Check if packet IPs are whitelisted
    - `_check_port_whitelist`: Check if packet ports are whitelisted
    - `_check_protocol_whitelist`: Check if packet protocol is whitelisted
    - `_check_time_based_whitelist`: Check if current time falls within whitelisted time windows
    - `_check_domain_whitelist`: Check if DNS query domain is whitelisted
    - `_check_broadcast_whitelist`: Check if broadcast packet should be whitelisted
    - `_check_multicast_whitelist`: Check if multicast packet should be whitelisted

**Dependencies:**
- config
- ipaddress
- scapy