# Directory Scripts Documentation

## Available Scripts


### __init__.py

**Path:** `network monitor\utils\__init__.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 0.3 KB
- Lines of code: 9 (of 10 total)

**Dependencies:**
- network_utils
- packet_utils

### network_utils.py

**Path:** `network monitor\utils\network_utils.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 0.6 KB
- Lines of code: 18 (of 21 total)

**Functions:**
- `resolve_ip`: Resolve an IP address to a hostname
- `is_private_ip`: Check if an IP address is private

### packet_utils.py

**Path:** `network monitor\utils\packet_utils.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 0.9 KB
- Lines of code: 26 (of 29 total)

**Functions:**
- `is_inbound`: Check if a packet is inbound to the local network
- `get_packet_protocol`: Get the protocol of a packet
- `get_packet_ports`: Get source and destination ports of a packet

**Dependencies:**
- ipaddress
- scapy