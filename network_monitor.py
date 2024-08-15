# Import CryptographyDeprecationWarning
from cryptography.utils import CryptographyDeprecationWarning
import warnings
import os
# Suppress DeprecationWarnings from cryptography module
warnings.filterwarnings("ignore", category=DeprecationWarning, module="cryptography")
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# Suppress DeprecationWarnings from cryptography module
os.environ['SCAPY_MANUF'] = ''

import time
import psutil
from bidi.algorithm import get_display
from collections import defaultdict, deque
import socket
import re
from scapy.layers import http, dns
import newrelic.agent
import logging
import sys
import scapy.all as scapy

# Get New Relic config file path from environment variable
new_relic_config = os.environ.get('NEW_RELIC_CONFIG_FILE')

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if new_relic_config:
    # Initialize New Relic
    newrelic.agent.initialize(new_relic_config)

    # Create a handler that sends logs to New Relic
    class NewRelicLogHandler(logging.Handler):
        def emit(self, record):
            newrelic.agent.record_custom_event('Log', {
                'level': record.levelname,
                'message': record.getMessage(),
                'filename': record.filename,
                'lineno': record.lineno
            })

    # Add the New Relic handler to the logger
    logger.addHandler(NewRelicLogHandler())

    logger.info("New Relic initialized successfully")
else:
    logger.info("NEW_RELIC_CONFIG_FILE environment variable not set. New Relic will not be initialized.")

# Add a stream handler to print logs to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# List of known malicious IP addresses (you should update this with real data)
MALICIOUS_IPS = {'192.168.1.100', '10.0.0.50'}

# List of file extensions to monitor
MONITORED_EXTENSIONS = {'.exe', '.dll', '.bat', '.sh', '.py'}

# Function to check if an interface is active (not a link-local or loopback address)
def is_interface_active(ip):
    return not ip.startswith('169.254.') and ip != '127.0.0.1'

# Function to get a list of active network interfaces
def get_interfaces():
    interfaces = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            # Only consider IPv4 addresses that are active
            if addr.family == 2 and is_interface_active(addr.address):
                interfaces.append((iface, addr.address))
                break
    return interfaces

# Function to let the user choose a network interface
def choose_interface(interfaces):
    if not interfaces:
        logger.info("No active network interfaces found. Exiting.")
        return None
    logger.info("Available active interfaces:")
    # Display available interfaces
    for i, (iface, ip) in enumerate(interfaces):
        iface_display = get_display(iface)
        logger.info(f"{i}: {iface_display} (IP: {ip})")
    # Loop until a valid choice is made
    while True:
        try:
            choice = int(input("Enter the number of the interface you want to use: "))
            if 0 <= choice < len(interfaces):
                return interfaces[choice][0]
        except ValueError:
            pass
        logger.info("Invalid choice. Please try again.")

# Function to capture network packets on a specified interface
def capture_packets(interface, count=1000):
    logger.info(f"Capturing {count} packets on {interface}...")
    return scapy.sniff(iface=interface, count=count)

# Function to resolve an IP address to a hostname
def resolve_ip(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.timeout):
        return ip

# Function to analyze captured network traffic for suspicious activities
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
                    payload = str(packet[http.HTTPRequest].fields)  # Changed from .Fields to .fields
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
        # Get the current timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        # Iterate through each item in the data
        for item in data:
            # Create a log message with timestamp and item details
            log_message = f"{timestamp} - {': '.join(map(str, item))}"
            # Write the log message to the file
            f.write(log_message + "\n")
            # Log the message as a warning
            logger.warning(log_message)
        # Ensure the data is written to disk
        f.flush()
        os.fsync(f.fileno())

def main():
    # Get a list of active network interfaces
    interfaces = get_interfaces()
    # Check if any interfaces were found
    if not interfaces:
        logger.info("No active network interfaces found. Exiting.")
        return
    # Let the user choose an interface
    interface = choose_interface(interfaces)
    # Check if an interface was selected
    if not interface:
        logger.info("No interface selected. Exiting.")
        return
    # Log the selected interface
    logger.info(f"Using network interface: {get_display(interface)}")
    # Set the log file name
    log_file = 'security_log.txt'
    try:
        # Start the main loop
        while True:
            # Capture packets on the selected interface
            packets = capture_packets(interface)
            # Analyze the captured traffic
            suspicious_activities = analyze_traffic(packets)
            # Check if any suspicious activities were detected
            if suspicious_activities:
                logger.info("Suspicious activities detected!")
                # Log the suspicious activities
                burn_in_log(log_file, suspicious_activities)
                # Print each suspicious activity
                for activity in suspicious_activities:
                    logger.info(f"- {': '.join(map(str, activity))}")
            else:
                logger.info("No suspicious activities detected in this batch.")
            # Wait for 60 seconds before the next capture
            time.sleep(60)
    except KeyboardInterrupt:
        # Handle user interruption (Ctrl+C)
        logger.info("\nStopping packet capture. Exiting.")
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    # Check if New Relic configuration is set
    if 'NEW_RELIC_CONFIG_FILE' in os.environ:
        # Register the application with New Relic
        newrelic.agent.register_application(timeout=10.0)
    # Run the main function
    main()
