# Feature names used for machine learning analysis
FEATURE_NAMES = [
    'packet_length',    # Total length of the packet
    'is_ip',           # Boolean flag for IPv4
    'is_ipv6',         # Boolean flag for IPv6  
    'is_tcp',          # Boolean flag for TCP protocol
    'is_udp',          # Boolean flag for UDP protocol
    'is_dns',          # Boolean flag for DNS packet
    'is_llmnr',        # Boolean flag for LLMNR packet
    'is_multicast',    # Boolean flag for multicast packet
    'is_broadcast',    # Boolean flag for broadcast packet
    'ttl',             # Time To Live value
    'src_port',        # Source port number  
    'dst_port',        # Destination port number
    'has_payload',     # Boolean flag for payload presence
    'payload_length',  # Length of payload
    'is_syn',          # Boolean flag for SYN packet
    'is_syn_ack',      # Boolean flag for SYN-ACK packet
    'is_icmpv6_nd',    # Boolean flag for ICMPv6 Neighbor Discovery
    'is_stp',          # Boolean flag for Spanning Tree Protocol
    'is_arp'           # Boolean flag for ARP packet
]
