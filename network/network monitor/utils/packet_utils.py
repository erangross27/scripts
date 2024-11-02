import ipaddress
from scapy.layers.inet import IP

def is_inbound(packet, local_network):
    """Check if a packet is inbound to the local network."""
    if IP in packet:
        dst_ip = ipaddress.ip_address(packet[IP].dst)
        src_ip = ipaddress.ip_address(packet[IP].src)
        return dst_ip in local_network and src_ip not in local_network
    return False

def get_packet_protocol(packet):
    """Get the protocol of a packet."""
    if IP in packet:
        proto = packet[IP].proto
        return {
            6: "TCP",
            17: "UDP",
            1: "ICMP"
        }.get(proto, "Unknown")
    return "Unknown"

def get_packet_ports(packet):
    """Get source and destination ports of a packet."""
    if TCP in packet:
        return packet[TCP].sport, packet[TCP].dport
    elif UDP in packet:
        return packet[UDP].sport, packet[UDP].dport
    return None, None
