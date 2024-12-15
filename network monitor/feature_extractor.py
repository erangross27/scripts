# Import necessary libraries
import pandas as pd
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.layers.dns import DNS
from scapy.layers.l2 import ARP
from scapy.packet import Raw
from config.feature_config import FEATURE_NAMES

class FeatureExtractor:
    """A class for extracting features from network packets for machine learning analysis."""
    
    def __init__(self):
        """Initialize the FeatureExtractor with predefined feature names."""
        self.feature_names = FEATURE_NAMES

    def extract_features(self, raw_packets):
        """Extract features from a list of packets for machine learning analysis.
        
        Args:
            raw_packets: List of network packets to analyze
        Returns:
            pandas DataFrame containing extracted features, or None if no features could be extracted
        """
        features = []
        
        for packet in raw_packets:
            # Handle packets that come as tuples (timestamp, packet)
            if isinstance(packet, tuple):
                packet = packet[1]
            
            try:
                feature_vector = self._extract_packet_features(packet)
                features.append(feature_vector)
            except Exception:
                continue

        if not features:
            return None

        df = pd.DataFrame(features, columns=self.feature_names)
        return df

    def _extract_packet_features(self, packet):
        """Extract features from a single packet.
        
        Args:
            packet: A single network packet to analyze
            
        Returns:
            list of extracted features in the order defined by feature_names
        """
        # Basic packet information - checks for presence of different protocols
        packet_length = len(packet)
        is_ip = int(IP in packet)
        is_ipv6 = int(IPv6 in packet)
        is_tcp = int(TCP in packet)
        is_udp = int(UDP in packet)
        is_dns = int(DNS in packet)
        is_llmnr = int('LLMNR' in packet.summary())
        
        # Check if packet is multicast (starts with specific MAC prefixes)
        # or broadcast (sent to all devices on network)
        is_multicast = int(
            packet.dst.startswith("01:00:5e") or 
            packet.dst.startswith("33:33")
        )
        is_broadcast = int(
            packet.dst == "ff:ff:ff:ff:ff:ff" or 
            (is_ip and packet[IP].dst == "255.255.255.255")
        )

        # Extract Time To Live value for IP/IPv6 packets
        ttl = 0
        if is_ip:
            ttl = packet[IP].ttl
        elif is_ipv6:
            ttl = packet[IPv6].hlim

        # Extract source and destination ports for TCP/UDP packets
        src_port = 0
        dst_port = 0
        if is_tcp:
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
        elif is_udp:
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport

        # Check for and analyze packet payload
        has_payload = int(Raw in packet)
        payload_length = len(packet[Raw].load) if has_payload else 0

        # Analyze TCP flags for connection establishment
        is_syn = int(is_tcp and (packet[TCP].flags & 0x02))
        is_syn_ack = int(is_tcp and (packet[TCP].flags & 0x12))

        # Check for special protocol packets
        is_icmpv6_nd = int(is_ipv6 and ICMPv6ND_NS in packet)
        is_stp = int('STP' in packet.summary())
        is_arp = int(ARP in packet)

        # Return all extracted features as a list
        return [
            packet_length,
            is_ip,
            is_ipv6,
            is_tcp,
            is_udp,
            is_dns,
            is_llmnr,
            is_multicast,
            is_broadcast,
            ttl,
            src_port,
            dst_port,
            has_payload,
            payload_length,
            is_syn,
            is_syn_ack,
            is_icmpv6_nd,
            is_stp,
            is_arp
        ]
