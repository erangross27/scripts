from cryptography.utils import CryptographyDeprecationWarning
import warnings

def setup_environment():
    # Define a list of warnings to ignore
    ignored_warnings = [
        (DeprecationWarning, "cryptography", None),
        (UserWarning, "scapy", None),
        (CryptographyDeprecationWarning, None, None),  # None means it applies to all modules
        (UserWarning, None, "Wireshark is installed, but cannot read manuf !"),
    ]

    # Set up warning filters
    for warning in ignored_warnings:
        category, module, message = warning
        kwargs = {"category": category}
        if module is not None:
            kwargs["module"] = module
        if message is not None:
            kwargs["message"] = message
        warnings.filterwarnings("ignore", **kwargs)

    # Use a context manager to catch and ignore CryptographyDeprecationWarnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=CryptographyDeprecationWarning)
 
# Call this function at the start of your script
setup_environment()

# Import necessary libraries

import os
import time
import psutil
import socket
import re
import logging
import sys
import json
from collections import defaultdict, deque
from bidi.algorithm import get_display
from scapy.layers import http, dns
import scapy.all as scapy
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue
from logging.handlers import QueueHandler, QueueListener
from collections import defaultdict



       

def setup_logger():
    # Set up and configure the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger

def setup_logging_queue():
    # Set up a logging queue for multi-process logging
    queue = Queue(-1)
    queue_handler = QueueHandler(queue)
    logger = setup_logger()
    logger.addHandler(queue_handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    listener = QueueListener(queue, stream_handler)
    return logger, listener

def load_config(file_path, logger):
    # Load configuration from a JSON file
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {}

def get_interfaces():
    # Get a list of active network interfaces
    return [(iface, addr.address) for iface, addrs in psutil.net_if_addrs().items()
            for addr in addrs if addr.family == socket.AF_INET and not addr.address.startswith('169.254.') and addr.address != '127.0.0.1']

def choose_interface(interfaces, logger):
    if not interfaces:
        logger.info("No active network interfaces found. Exiting.")
        return None
    
    logger.info("Available active interfaces:")
    for i, (iface, ip) in enumerate(interfaces):
        logger.info(f"{i}: {get_display(iface)} (IP: {ip})")
    
    logger.info("") # Add an empty line for better readability
    
    while True:
        try:
            choice = int(input("Enter the number of the interface to use: "))
            if 0 <= choice < len(interfaces):
                return interfaces[choice][0]
            else:
                logger.info("Invalid choice. Please try again.")
        except ValueError:
            logger.info("Invalid input. Please enter a number.")


def capture_packets(interface, count, logger):
    # Capture network packets using scapy
    logger.info(f"Capturing {count} packets on {interface}...")
    try:
        return scapy.sniff(iface=interface, count=count)
    except Exception as e:
        logger.error(f"Error capturing packets: {e}")
        return []

def resolve_ip(ip):
    # Resolve IP address to hostname
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.timeout):
        return ip

def analyze_packet(packet, local_ip, current_time, password_regex, credit_card_regex):
    # Analyze a single packet for suspicious activity
    if packet.haslayer(scapy.IP):
        src_ip, dst_ip = packet[scapy.IP].src, packet[scapy.IP].dst
        if packet.haslayer(scapy.TCP):
            src_port, dst_port = packet[scapy.TCP].sport, packet[scapy.TCP].dport
            if packet.haslayer(http.HTTPRequest):
                payload = str(packet[http.HTTPRequest].fields)
                if password_regex.search(payload):
                    return ('Potential password transmission', src_ip, dst_ip)
                if credit_card_regex.search(payload):
                    return ('Potential credit card transmission', src_ip, dst_ip)
            if packet[scapy.TCP].flags & 0x02:
                return ('Outbound connection', dst_ip, dst_port, src_port, current_time) if src_ip == local_ip else ('Inbound connection', dst_port, src_ip)
        if packet.haslayer(dns.DNSQR):
            return ('DNS query', src_ip, packet[dns.DNSQR].qname.decode('utf-8'))
    return None


def is_inbound(packet, local_network):
    return packet.haslayer(scapy.IP) and packet[scapy.IP].dst.startswith(local_network) and not packet[scapy.IP].src.startswith(local_network)

def process_packet_batch(packet_batch, local_network, password_regex_pattern, credit_card_regex_pattern):
    password_regex = re.compile(password_regex_pattern, re.IGNORECASE)
    credit_card_regex = re.compile(credit_card_regex_pattern)
    
    batch_results = {
        'suspicious_activities': [],
        'inbound_connections': defaultdict(lambda: defaultdict(int)),
        'dns_queries': defaultdict(set),
        'port_scans': defaultdict(set)
    }
    
    for packet in packet_batch:
        if is_inbound(packet, local_network):
            src_ip = packet[scapy.IP].src
            dst_ip = packet[scapy.IP].dst
            
            if packet.haslayer(scapy.TCP):
                dst_port = packet[scapy.TCP].dport
                batch_results['inbound_connections'][dst_port][src_ip] += 1
                batch_results['port_scans'][src_ip].add(dst_port)
                
                if packet.haslayer(http.HTTPRequest):
                    payload = str(packet[http.HTTPRequest].fields)
                    if password_regex.search(payload):
                        batch_results['suspicious_activities'].append(('Potential password transmission', src_ip, dst_ip))
                    if credit_card_regex.search(payload):
                        batch_results['suspicious_activities'].append(('Potential credit card transmission', src_ip, dst_ip))
            
            elif packet.haslayer(dns.DNSQR):
                query = packet[dns.DNSQR].qname.decode('utf-8')
                batch_results['dns_queries'][src_ip].add(query)

    # Convert defaultdict to regular dict for pickling
    return {k: dict(v) if isinstance(v, defaultdict) else v for k, v in batch_results.items()}

def analyze_traffic(packets, logger, port_scan_threshold, dns_query_threshold):
    suspicious_activities = []
    inbound_connections = defaultdict(lambda: defaultdict(int))
    dns_queries = defaultdict(set)
    port_scans = defaultdict(set)
    
    # Determine the local network range
    local_ip = packets[0][scapy.IP].dst if packets and packets[0].haslayer(scapy.IP) else None
    if not local_ip:
        logger.warning("Unable to determine local IP. Analysis may be inaccurate.")
        return suspicious_activities
    
    local_network = '.'.join(local_ip.split('.')[:3]) + '.'  # Assuming a /24 network

    password_regex_pattern = r'password=\S+'
    credit_card_regex_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'

    # Process packets in batches using multiprocessing
    batch_size = 100
    packet_batches = [packets[i:i+batch_size] for i in range(0, len(packets), batch_size)]

    with ProcessPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(
            process_packet_batch,
            packet_batches,
            [local_network] * len(packet_batches),
            [password_regex_pattern] * len(packet_batches),
            [credit_card_regex_pattern] * len(packet_batches)
        ))

    # Combine results from all batches
    for result in results:
        suspicious_activities.extend(result['suspicious_activities'])
        for port, connections in result['inbound_connections'].items():
            inbound_connections[port].update(connections)
        for src_ip, queries in result['dns_queries'].items():
            dns_queries[src_ip].update(queries)
        for src_ip, ports in result['port_scans'].items():
            port_scans[src_ip].update(ports)

    # Check for unsolicited inbound connection attempts
    for port, connections in inbound_connections.items():
        total_attempts = sum(connections.values())
        if total_attempts > 0 and port < 1024:
            suspicious_activities.append(('Unsolicited inbound connection attempt', port, total_attempts, f"Sources: {', '.join(map(resolve_ip, connections.keys()))}"))

    # Check for potential port scans
    for src_ip, ports in port_scans.items():
        if len(ports) > port_scan_threshold:
            suspicious_activities.append(('Potential port scan attempt', src_ip, f"Scanned ports: {', '.join(map(str, ports))}"))

    # Check for excessive DNS queries
    for ip, queries in dns_queries.items():
        if len(queries) > dns_query_threshold:
            suspicious_activities.append(('Excessive inbound DNS queries', ip, f"Number of unique queries: {len(queries)}"))

    return suspicious_activities




def log_suspicious_activities(log_file, data, logger):
    # Log suspicious activities to a file and logger
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a', encoding='utf-8') as f:
        for item in data:
            log_message = f"{timestamp} - {': '.join(map(str, item))}"
            f.write(log_message + "\n")
            logger.warning(log_message)
        f.flush()
        os.fsync(f.fileno())

def main():
    # Main function to run the network traffic analyzer
    logger, log_listener = setup_logging_queue()
    log_listener.start()

    try:
        # Load configuration
        config = load_config('config.json', logger)
        
        global MALICIOUS_IPS, MONITORED_EXTENSIONS, PORT_SCAN_THRESHOLD, DNS_QUERY_THRESHOLD
        MALICIOUS_IPS = set(config.get('malicious_ips', []))
        MONITORED_EXTENSIONS = set(config.get('monitored_extensions', []))
        PORT_SCAN_THRESHOLD = config.get('port_scan_threshold', 10)
        DNS_QUERY_THRESHOLD = config.get('dns_query_threshold', 50)

        count = config.get('packet_capture_count', 1000)

        # Get and choose network interface
        interfaces = get_interfaces()
        if not interfaces:
            logger.info("No active network interfaces found. Exiting.")
            return

        interface = choose_interface(interfaces, logger)
        if not interface:
            logger.info("No interface selected. Exiting.")
            return

        logger.info(f"Using network interface: {get_display(interface)}")
        log_file = 'security_log.txt'

        # Main loop for continuous packet capture and analysis
        while True:
            packets = capture_packets(interface, count, logger)
            suspicious_activities = analyze_traffic(packets, logger, PORT_SCAN_THRESHOLD, DNS_QUERY_THRESHOLD)
            if suspicious_activities:
                logger.info("Suspicious activities detected!")
                log_suspicious_activities(log_file, suspicious_activities, logger)
                for activity in suspicious_activities:
                    logger.info(f"- {': '.join(map(str, activity))}")
            else:
                logger.info("No suspicious activities detected in this batch.")
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("\nStopping packet capture. Exiting.")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
    finally:
        log_listener.stop()

if __name__ == "__main__":
    main()
