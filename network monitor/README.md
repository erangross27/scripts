# Directory Scripts Documentation

## Available Scripts


### __init__.py

**Path:** `network monitor\__init__.py`

**Description:**
No description available

### anomaly_detector.py

**Path:** `network monitor\anomaly_detector.py`

**Description:**
No description available

**Dependencies:**
- feature_extractor
- numpy

### feature_extractor.py

**Path:** `network monitor\feature_extractor.py`

**Description:**
No description available

**Dependencies:**
- config
- pandas
- scapy

### interface_manager.py

**Path:** `network monitor\interface_manager.py`

**Description:**
No description available

**Dependencies:**
- bidi
- netifaces
- psutil
- subprocess
- wmi

### logger_setup.py

**Path:** `network monitor\logger_setup.py`

**Description:**
No description available

**Dependencies:**

### network_monitor.py

**Path:** `network monitor\network_monitor.py`

**Description:**
No description available

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

**Dependencies:**
- ipaddress
- scapy

### packet_capture.py

**Path:** `network monitor\packet_capture.py`

**Description:**
No description available

**Dependencies:**
- queue
- scapy
- tqdm

### whitelist_manager.py

**Path:** `network monitor\whitelist_manager.py`

**Description:**
No description available

**Dependencies:**
- config
- ipaddress
- scapy