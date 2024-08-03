import warnings

# Suppress DeprecationWarnings from cryptography module
warnings.filterwarnings("ignore", category=DeprecationWarning, module="cryptography")

import scapy.all as scapy
from scapy.layers import http
import time
import os
import psutil
from bidi.algorithm import get_display
from collections import defaultdict
import socket
# List of known malicious IP addresses (you should update this with real data)
MALICIOUS_IPS = {'192.168.1.100', '10.0.0.50'}

# List of file extensions to monitor
MONITORED_EXTENSIONS = {'.exe', '.dll', '.bat', '.sh', '.py'}

def is_interface_active(ip):
    return not ip.startswith('169.254.') and ip != '127.0.0.1'

def get_interfaces():
    interfaces = []
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
    for i, (iface, ip) in enumerate(interfaces):
        iface_display = get_display(iface)
        print(f"{i}: {iface_display} (IP: {ip})")
    
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
    return scapy.sniff(iface=interface, count=count)


def resolve_ip(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.timeout):
        return ip  # Return the IP if resolution fails

def analyze_traffic(packets):
    suspicious_activities = []
    port_connections = defaultdict(lambda: defaultdict(set))
    data_transfer = defaultdict(int)
    syn_counts = defaultdict(lambda: defaultdict(int))
    monitored_ports = {80, 443, 22, 21}

    for packet in packets:
        if packet.haslayer(scapy.IP):
            src_ip = packet[scapy.IP].src
            dst_ip = packet[scapy.IP].dst
            # Monitor data transfer
            data_transfer[src_ip] += len(packet)

            if packet.haslayer(scapy.TCP):
                dst_port = packet[scapy.TCP].dport
                src_port = packet[scapy.TCP].sport
                # Record connection details
                port_connections[dst_port][src_ip].add(dst_ip)

                # Check for unusual ports
                if dst_port < 1024 and dst_port not in monitored_ports:
                    suspicious_activities.append(('Connection to unusual port', resolve_ip(src_ip), resolve_ip(dst_ip), dst_port))

                # Count SYN packets for each source IP to each destination IP
                if packet[scapy.TCP].flags == 2:  # SYN flag
                    syn_counts[src_ip][dst_ip] += 1

            if packet.haslayer(http.HTTPRequest):
                url = packet[http.HTTPRequest].Host.decode('utf-8', errors='ignore') + packet[http.HTTPRequest].Path.decode('utf-8', errors='ignore')
                method = packet[http.HTTPRequest].Method.decode('utf-8', errors='ignore')

                # Check for sensitive file downloads
                if any(url.lower().endswith(ext) for ext in MONITORED_EXTENSIONS):
                    suspicious_activities.append(('Sensitive file download detected', method, url))

                # Check for potential credential submission
                if method == 'POST' and 'login' in url.lower():
                    suspicious_activities.append(('Potential credential submission', method, url))

                # Check for potential admin access attempts
                elif any(keyword in url.lower() for keyword in ['admin', 'config', 'setup']):
                    suspicious_activities.append(('Potential admin access attempt', method, url))

    # Check for large data transfers
    for ip, amount in data_transfer.items():
        if amount > 10000000:  # More than 10MB
            suspicious_activities.append(('Large data transfer detected', resolve_ip(ip), f"{amount/1000000:.2f} MB"))

    # Check for potential port scanning (many SYN packets to different IPs)
    for src_ip, dst_ips in syn_counts.items():
        if len(dst_ips) > 10:  # If connecting to more than 10 different IPs
            suspicious_activities.append(('Potential port scan detected', resolve_ip(src_ip), f"{len(dst_ips)} different IPs"))

    # Check for high number of connections to ports
    for port, connections in port_connections.items():
        total_connections = sum(len(dsts) for dsts in connections.values())
        threshold = 20 if port in monitored_ports else 50
        if total_connections > threshold:
            details = [f"{resolve_ip(src)} -> {', '.join(map(resolve_ip, dsts))}" for src, dsts in connections.items()]
            suspicious_activities.append((
                'High number of connections to port',
                port,
                total_connections,
                f"Details: {'; '.join(details)}"
            ))

    return suspicious_activities


def burn_in_log(log_file, data):
    with open(log_file, 'a', encoding='utf-8') as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        for item in data:
            f.write(f"{timestamp} - {': '.join(map(str, item))}\n")
        f.flush()  # Ensure data is written to the file
        os.fsync(f.fileno())  # Flush operating system buffers

def main():
    interfaces = get_interfaces()
    if not interfaces:
        print("No active network interfaces found. Exiting.")
        return

    interface = choose_interface(interfaces)
    if not interface:
        print("No interface selected. Exiting.")
        return

    print(f"Using network interface: {get_display(interface)}")
    log_file = 'security_log.txt'

    while True:
        try:
            packets = capture_packets(interface)
            suspicious_activities = analyze_traffic(packets)
            if suspicious_activities:
                print("Suspicious activities detected!")
                burn_in_log(log_file, suspicious_activities)
                for activity in suspicious_activities:
                    print(f"- {': '.join(map(str, activity))}")
            else:
                print("No suspicious activities detected in this batch.")
            time.sleep(60)  # Wait for 60 seconds before the next capture
        except KeyboardInterrupt:
            print("\nStopping packet capture. Exiting.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print(f"Error details: {type(e).__name__}, {str(e)}")
            time.sleep(60)  # Wait before trying again




if __name__ == "__main__":
    main()
