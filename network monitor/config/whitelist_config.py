"""
This script handles whitelist config.
"""

import re
from ipaddress import ip_network

# IP address whitelist
WHITELISTED_IPS = [
    ip_network("192.168.1.0/24"),  # Local network
    ip_network("10.0.0.0/8"),      # Private network range
    ip_network("8.8.8.8/32"),      # Google DNS
]

# Port ranges whitelist
WHITELISTED_PORTS = [
    (80, 80),    # HTTP
    (443, 443),  # HTTPS
    (53, 53),    # DNS
    (123, 123),  # NTP
    (67, 68),    # DHCP
    (20, 21),    # FTP
    (22, 22),    # SSH
    (3389, 3389),# RDP
]

# Protocol whitelist
WHITELISTED_PROTOCOLS = ["TCP", "UDP", "ICMP", "ICMPv6"]

# Time-based whitelist
TIME_BASED_WHITELIST = {
    "BACKUP_TRAFFIC": ("02:00", "04:00"),
    "MAINTENANCE_WINDOW": ("22:00", "23:00"),
}

# Domain whitelist patterns
WHITELISTED_DOMAINS = [
    r".*\.google\.com$",
    r".*\.microsoft\.com$",
    r".*\.apple\.com$",
]

# Compile domain patterns for better performance
COMPILED_DOMAIN_PATTERNS = [re.compile(pattern) for pattern in WHITELISTED_DOMAINS]
