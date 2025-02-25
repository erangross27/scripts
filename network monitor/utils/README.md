# Directory Scripts Documentation

## Available Scripts


### __init__.py

**Path:** `network monitor\utils\__init__.py`

**Description:**
This script handles   init  .

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 0.3 KB
- Lines of code: 12 (of 14 total)

**Dependencies:**
- network_utils
- packet_utils

### network_utils.py

**Path:** `network monitor\utils\network_utils.py`

**Description:**
This script provides utility functions for networks.

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 0.6 KB
- Lines of code: 21 (of 25 total)

**Functions:**
- `resolve_ip`: Resolve an IP address to a hostname
- `is_private_ip`: Check if an IP address is private

### packet_utils.py

**Path:** `network monitor\utils\packet_utils.py`

**Description:**
This script provides utility functions for packets.

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 1.0 KB
- Lines of code: 29 (of 33 total)

**Functions:**
- `is_inbound`: Check if a packet is inbound to the local network
- `get_packet_protocol`: Get the protocol of a packet
- `get_packet_ports`: Get source and destination ports of a packet

**Dependencies:**
- ipaddress
- scapy