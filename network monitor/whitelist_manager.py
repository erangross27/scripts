"""
This script handles whitelist manager.
"""

try:
    from config.whitelist_config import (
        WHITELISTED_IPS,
        WHITELISTED_PORTS,
        WHITELISTED_PROTOCOLS,
        TIME_BASED_WHITELIST,
        WHITELISTED_DOMAINS,
        COMPILED_DOMAIN_PATTERNS
    )
except ImportError:
    # Fallback defaults if config is not available
    WHITELISTED_IPS = []
    WHITELISTED_PORTS = []
    WHITELISTED_PROTOCOLS = []
    TIME_BASED_WHITELIST = {}
    WHITELISTED_DOMAINS = []
    COMPILED_DOMAIN_PATTERNS = []

import time
try:
    from scapy.layers.inet import IP, TCP, UDP
    from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
    from scapy.layers.l2 import ARP
    from scapy.layers.dns import DNSQR
except ImportError:
    print("Warning: scapy is not installed. Some whitelist functionality may be limited.")

import ipaddress

class WhitelistManager:
    """
    Manages whitelist.
    """
    def __init__(self, logger):
        """
        Special method __init__.
        """
        self.logger = logger

    def is_whitelisted(self, packet):
        """Check if a packet matches any whitelist rules."""
        try:
            if self._check_ip_whitelist(packet):
                return True

            if self._check_port_whitelist(packet):
                return True

            if self._check_protocol_whitelist(packet):
                return True

            if self._check_time_based_whitelist():
                return True

            if self._check_domain_whitelist(packet):
                return True

            if self._check_broadcast_whitelist(packet):
                return True

            if self._check_multicast_whitelist(packet):
                return True

            return False

        except Exception as e:
            self.logger.debug(f"Error in whitelist check: {e}")
            # In case of error, we err on the side of caution and treat as whitelisted
            # to avoid false positives
            return True

    def is_whitelisted_port(self, port):
        """Check if a port is whitelisted."""
        try:
            return any(start <= port <= end for start, end in WHITELISTED_PORTS)
        except Exception as e:
            self.logger.debug(f"Error checking if port {port} is whitelisted: {e}")
            return True

    def _check_ip_whitelist(self, packet):
        """Check if packet IPs are whitelisted."""
        try:
            if IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                return any(
                    ipaddress.ip_address(src_ip) in network or 
                    ipaddress.ip_address(dst_ip) in network 
                    for network in WHITELISTED_IPS
                )
            return False
        except Exception as e:
            self.logger.debug(f"Error checking IP whitelist: {e}")
            return True

    def _check_port_whitelist(self, packet):
        """Check if packet ports are whitelisted."""
        try:
            if TCP in packet or UDP in packet:
                sport = packet[TCP].sport if TCP in packet else packet[UDP].sport
                dport = packet[TCP].dport if TCP in packet else packet[UDP].dport
                return any(start <= sport <= end or start <= dport <= end 
                          for start, end in WHITELISTED_PORTS)
            return False
        except Exception as e:
            self.logger.debug(f"Error checking port whitelist: {e}")
            return True

    def _check_protocol_whitelist(self, packet):
        """Check if packet protocol is whitelisted."""
        try:
            if IP in packet:
                proto = packet[IP].proto
                proto_name = {6: "TCP", 17: "UDP", 1: "ICMP"}.get(proto)
                return proto_name in WHITELISTED_PROTOCOLS
            elif IPv6 in packet:
                nh = packet[IPv6].nh
                proto_name = {6: "TCP", 17: "UDP", 58: "ICMPv6"}.get(nh)
                return proto_name in WHITELISTED_PROTOCOLS
            return False
        except Exception as e:
            self.logger.debug(f"Error checking protocol whitelist: {e}")
            return True

    def _check_time_based_whitelist(self):
        """Check if current time falls within whitelisted time windows."""
        try:
            current_time = time.strftime("%H:%M")
            return any(
                start_time <= current_time <= end_time 
                for start_time, end_time in TIME_BASED_WHITELIST.values()
            )
        except Exception as e:
            self.logger.debug(f"Error checking time-based whitelist: {e}")
            return True

    def _check_domain_whitelist(self, packet):
        """Check if DNS query domain is whitelisted."""
        try:
            if packet.haslayer(DNSQR):
                qname = packet[DNSQR].qname.decode('utf-8')
                return any(pattern.match(qname) for pattern in COMPILED_DOMAIN_PATTERNS)
            return False
        except Exception as e:
            self.logger.debug(f"Error checking domain whitelist: {e}")
            return True

    def _check_broadcast_whitelist(self, packet):
        """Check if broadcast packet should be whitelisted."""
        try:
            if packet.dst == "ff:ff:ff:ff:ff:ff":
                return (
                    ARP in packet or
                    packet.type == 0x0806 or  # ARP
                    (UDP in packet and packet[UDP].dport in [67, 68]) or  # DHCP
                    (IPv6 in packet and ICMPv6ND_NS in packet)  # IPv6 ND
                )
            return False
        except Exception as e:
            self.logger.debug(f"Error checking broadcast whitelist: {e}")
            return True

    def _check_multicast_whitelist(self, packet):
        """Check if multicast packet should be whitelisted."""
        try:
            return (
                packet.dst.startswith("01:00:5e") or  # IPv4 multicast
                packet.dst.startswith("33:33") or     # IPv6 multicast
                packet.dst in [
                    "01:80:c2:00:00:00",  # STP
                    "01:80:c2:00:00:0e",  # LLDP
                    "01:00:0c:cc:cc:cc",  # Cisco CDP/VTP/UDLD
                    "01:00:0c:cc:cc:cd"   # Cisco PVST+
                ]
            )
        except Exception as e:
            self.logger.debug(f"Error checking multicast whitelist: {e}")
            return True