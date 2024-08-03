import warnings
# Suppress DeprecationWarnings from cryptography module
warnings.filterwarnings("ignore", category=DeprecationWarning, module="cryptography")

# Import necessary modules
import scapy.all as scapy
import time
import os
import psutil
from bidi.algorithm import get_display
from collections import defaultdict
import socket
from collections import deque
import re
from scapy.layers import http, dns
# List of known malicious IP addresses (you should update this with real data)
MALICIOUS_IPS = {'192.168.1.100', '10.0.0.50'}

# List of file extensions to monitor
MONITORED_EXTENSIONS = {'.exe', '.dll', '.bat', '.sh', '.py'}

def is_interface_active(ip):
    # Check if the IP is not a link-local address and not localhost
    return not ip.startswith('169.254.') and ip != '127.0.0.1'

def get_interfaces():
    interfaces = []
    # Iterate through network interfaces and their addresses
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == 2:  # IPv4
                if is_interface_active(addr.address):
                    interfaces.append((iface, addr.address))
                    break  # We only need one IPv4 address per interface
    return interfaces

def choose_interface(interfaces):
    if not interfaces:
        print("No active network interfaces found.")
        return None
    
    print("Available active interfaces:")
    # Display available interfaces
    for i, (iface, ip) in enumerate(interfaces):
        iface_display = get_display(iface)
        print(f"{i}: {iface_display} (IP: {ip})")
    
    # Allow user to choose an interface
    while True:
        try:
            choice = int(input("Enter the number of the interface you want to use: "))
            if 0 <= choice < len(interfaces):
                return interfaces[choice][0]
        except ValueError:
            pass
        print("Invalid choice. Please try again.")

def capture_packets(interface, count=1000):
    print(f"Capturing {count} packets on {interface}...")
    # Use scapy to capture packets on the specified interface
    return scapy.sniff(iface=interface, count=count)

def resolve_ip(ip):
    try:
        # Attempt to resolve IP to hostname
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.timeout):
        return ip  # Return the IP if resolution fails



def analyze_traffic(packets):
    suspicious_activities = []
    inbound_connections = defaultdict(lambda: defaultdict(int))
    outbound_connections = deque(maxlen=10000)
    data_transfer = defaultdict(int)
    dns_queries = defaultdict(set)
    port_scans = defaultdict(set)
    current_time = time.time()
    local_ip = None

    # Regular expressions for sensitive information
    password_regex = re.compile(r'password=\S+', re.IGNORECASE)
    credit_card_regex = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')

    for packet in packets:
        if packet.haslayer(scapy.IP):
            src_ip = packet[scapy.IP].src
            dst_ip = packet[scapy.IP].dst

            # Determine local IP if not yet set
            if local_ip is None and packet.sniffed_on:
                local_ip = next((addr.address for addr in psutil.net_if_addrs()[packet.sniffed_on] 
                                 if addr.family == socket.AF_INET), None)

            # Track data transfer
            data_transfer[src_ip] += len(packet)

            if packet.haslayer(scapy.TCP):
                src_port = packet[scapy.TCP].sport
                dst_port = packet[scapy.TCP].dport

                # Credential theft detection
                if packet.haslayer(http.HTTPRequest):
                    payload = str(packet[http.HTTPRequest].Fields)
                    if password_regex.search(payload):
                        suspicious_activities.append(('Potential password transmission', src_ip, dst_ip))
                    if credit_card_regex.search(payload):
                        suspicious_activities.append(('Potential credit card transmission', src_ip, dst_ip))

                # Track outbound connections
                if src_ip == local_ip and packet[scapy.TCP].flags & 0x02:
                    outbound_connections.append((dst_ip, dst_port, src_port, current_time))

                # Track inbound connections and potential port scans
                elif dst_ip == local_ip and packet[scapy.TCP].flags & 0x02:
                    inbound_connections[dst_port][src_ip] += 1
                    port_scans[src_ip].add(dst_port)

            # DNS query monitoring (part of discovery phase)
            if packet.haslayer(dns.DNSQR):
                query = packet[dns.DNSQR].qname.decode('utf-8')
                dns_queries[src_ip].add(query)

    # Clear old outbound connections
    outbound_connections = deque((conn for conn in outbound_connections if current_time - conn[3] < 60), maxlen=10000)

    # Analyze inbound connections for potential threats
    for port, connections in inbound_connections.items():
        total_attempts = sum(connections.values())
        if total_attempts > 0 and port < 1024:
            suspicious_activities.append((
                'Unsolicited inbound connection attempt',
                port,
                total_attempts,
                f"Sources: {', '.join(map(resolve_ip, connections.keys()))}"
            ))

    # Detect potential lateral movement
    for src_ip, ports in port_scans.items():
        if len(ports) > 10:  # Adjust threshold as needed
            suspicious_activities.append((
                'Potential port scan (lateral movement attempt)',
                src_ip,
                f"Scanned ports: {', '.join(map(str, ports))}"
            ))

    # Detect unusual data collection or exfiltration
    for ip, amount in data_transfer.items():
        if amount > 10000000:  # 10 MB, adjust as needed
            suspicious_activities.append((
                'Large data transfer (potential exfiltration)',
                ip,
                f"{amount/1000000:.2f} MB"
            ))

    # Detect excessive DNS queries (potential discovery phase activity)
    for ip, queries in dns_queries.items():
        if len(queries) > 50:  # Adjust threshold as needed
            suspicious_activities.append((
                'Excessive DNS queries (potential discovery activity)',
                ip,
                f"Number of unique queries: {len(queries)}"
            ))

    return suspicious_activities


def burn_in_log(log_file, data):
    # Open the log file in append mode
    with open(log_file, 'a', encoding='utf-8') as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        # Write each suspicious activity to the log file
        for item in data:
            f.write(f"{timestamp} - {': '.join(map(str, item))}\n")
        f.flush()  # Ensure data is written to the file
        os.fsync(f.fileno())  # Flush operating system buffers

def main():
    # Get list of network interfaces
    interfaces = get_interfaces()
    if not interfaces:
        print("No active network interfaces found. Exiting.")
        return

    # Let user choose an interface
    interface = choose_interface(interfaces)
    if not interface:
        print("No interface selected. Exiting.")
        return

    print(f"Using network interface: {get_display(interface)}")
    log_file = 'security_log.txt'

    # Main loop for continuous monitoring
    try:
        while True:
            # Capture packets
            packets = capture_packets(interface)
            
            # Analyze captured packets
            suspicious_activities = analyze_traffic(packets)
            
            if suspicious_activities:
                print("Suspicious activities detected!")
                # Log suspicious activities
                burn_in_log(log_file, suspicious_activities)
                # Print suspicious activities to console
                for activity in suspicious_activities:
                    print(f"- {': '.join(map(str, activity))}")
            else:
                print("No suspicious activities detected in this batch.")
            
            time.sleep(60)  # Wait for 60 seconds before the next capture

    except KeyboardInterrupt:
        print("\nStopping packet capture. Exiting.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Error details: {type(e).__name__}, {str(e)}")

if __name__ == "__main__":
    main()
