"""
Network Monitor

This script monitors network traffic, captures packets, and analyzes them for suspicious activities and anomalies.
It uses both rule-based analysis and machine learning techniques to detect potential security threats.

Features:
- Captures network packets from a specified or user-selected network interface
- Analyzes packets for suspicious activities such as port scans, unusual DNS queries, and potential data exfiltration
- Uses machine learning (Isolation Forest) to detect anomalies in network traffic
- Logs suspicious activities and anomalies for further investigation
- Adapts to frequently occurring anomalies to reduce false positives
- Supports both IPv4 and IPv6 traffic

Usage:
Run the script with root/administrator privileges. Optionally specify a network interface:
    sudo python3 network_monitor.py [--interface INTERFACE_NAME]

Dependencies:
- scapy
- psutil
- netifaces
- numpy
- pandas
- scikit-learn
- tqdm

Note: This script requires root privileges on Linux systems to capture network packets.
"""

from cryptography.utils import CryptographyDeprecationWarning
import warnings

def setup_environment():
    # Ignore CryptographyDeprecationWarning
    warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
#Calling it at the beginging of the script to suppress warnings during the execution of the script.
setup_environment()

import os
import time
import psutil
import socket
import re
import logging
import sys
import multiprocessing
from multiprocessing import Queue
import netifaces
import argparse
import ctypes
import numpy as np
import pandas as pd
import joblib
import ipaddress
from ipaddress import ip_network, ip_address
from sklearn.ensemble import IsolationForest
from concurrent.futures import ProcessPoolExecutor
from typing import List, Any, Tuple
from scapy.all import IP, IPv6, TCP, UDP, DNS, DNSQR, Raw, Ether, sniff, ARP, DHCP
from scapy.layers import http
from scapy.layers.inet6 import ICMPv6ND_NS
from collections import defaultdict
from tqdm import tqdm
from bidi.algorithm import get_display
from logging.handlers import QueueHandler, QueueListener
from scapy.layers.llmnr import LLMNRQuery, LLMNRResponse


# Whitelist configurations
WHITELISTED_IPS = [
    ip_network("192.168.1.0/24"),  # Local network
    ip_network("10.0.0.0/8"),      # Private network range
    ip_network("8.8.8.8/32"),      # Google DNS
]

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

WHITELISTED_PROTOCOLS = ["TCP", "UDP", "ICMP", "ICMPv6"]

TIME_BASED_WHITELIST = {
    "BACKUP_TRAFFIC": ("02:00", "04:00"),
    "MAINTENANCE_WINDOW": ("22:00", "23:00"),
}

WHITELISTED_DOMAINS = [
    r".*\.google\.com$",
    r".*\.microsoft\.com$",
    r".*\.apple\.com$",
]

COMPILED_DOMAIN_PATTERNS = [re.compile(pattern) for pattern in WHITELISTED_DOMAINS]



# Define a list of feature names used for machine learning analysis of network packets
FEATURE_NAMES = [
    'packet_length',  # Total length of the packet
    'is_ip',          # Boolean flag indicating if the packet is IPv4
    'is_ipv6',        # Boolean flag indicating if the packet is IPv6
    'is_tcp',         # Boolean flag indicating if the packet uses TCP protocol
    'is_udp',         # Boolean flag indicating if the packet uses UDP protocol
    'is_dns',         # Boolean flag indicating if the packet is a DNS packet
    'is_llmnr',       # Boolean flag indicating if the packet is an LLMNR packet
    'is_multicast',   # Boolean flag indicating if the packet is a multicast packet
    'is_broadcast',   # Boolean flag indicating if the packet is a broadcast packet
    'ttl',            # Time To Live value of the packet
    'src_port',       # Source port number
    'dst_port',       # Destination port number
    'has_payload',    # Boolean flag indicating if the packet has a payload
    'payload_length', # Length of the packet's payload
    'is_syn',         # Boolean flag indicating if the packet is a SYN packet
    'is_syn_ack',     # Boolean flag indicating if the packet is a SYN-ACK packet
    'is_icmpv6_nd',   # Boolean flag indicating if the packet is an ICMPv6 Neighbor Discovery packet
    'is_stp',         # Boolean flag indicating if the packet is a Spanning Tree Protocol packet
    'is_arp'          # Boolean flag indicating if the packet is an ARP packet
]



def setup_logger():
    # Create a logger for the current module
    logger = logging.getLogger(__name__)
    # Set the logging level to INFO, which means it will capture messages at this level and above
    logger.setLevel(logging.INFO)
    return logger
## Start the QueueListener to begin listening for log messages
def setup_logging_queue():
    # Create a Queue for logging, with no limit on its size
    queue = Queue(-1)
    # Create a QueueHandler that will send log messages to the Queue
    queue_handler = QueueHandler(queue)
    # Set up a logger using the setup_logger function
    logger = setup_logger()
    # Add the QueueHandler to the logger to enable it to log messages to the queue
    logger.addHandler(queue_handler)
    # Create a StreamHandler to print log messages to the standard output (console)
    stream_handler = logging.StreamHandler(sys.stdout)
    # Create a QueueListener to listen for messages from the queue and send them to the stream handler
    listener = QueueListener(queue, stream_handler)
    return logger, listener  # Return both the logger and the listener for further use
#

class PersistentAnomalyDetector:
    def __init__(self, model_path='anomaly_model.joblib', contamination=0.01):
        self.model_path = model_path
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_fitted = False
        self.feature_names = None
        self.logger = logging.getLogger(__name__)

    def partial_fit(self, X):
        if not isinstance(X, pd.DataFrame):
            self.logger.error("Input X must be a pandas DataFrame")
            return

        if X.empty:
            self.logger.warning("Empty DataFrame provided. Skipping partial_fit.")
            return

        if not self.is_fitted or self.feature_names is None or set(X.columns) != set(self.feature_names):
            self.logger.info("Fitting new model or updating feature set")
            self.model = IsolationForest(contamination=self.contamination, random_state=42)
            self.model.fit(X)
            self.is_fitted = True
            self.feature_names = X.columns.tolist()
        else:
            self.logger.info("Updating existing model")
            self.model.fit(X)
        
        self.save_model()

    def predict(self, X):
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Call 'partial_fit' first.")
        return self.model.predict(X)

    def save_model(self):
        if self.is_fitted:
            joblib.dump({'model': self.model, 'feature_names': self.feature_names}, self.model_path)
            self.logger.info(f"Anomaly detection model saved to {self.model_path}")

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                loaded_data = joblib.load(self.model_path)
                if isinstance(loaded_data, dict):
                    self.model = loaded_data['model']
                    self.feature_names = loaded_data['feature_names']
                else:
                    # Handle the case of old format (only model was saved)
                    self.model = loaded_data
                    self.feature_names = None
                self.is_fitted = True
                self.logger.info(f"Anomaly detection model loaded from {self.model_path}")
            except Exception as e:
                self.logger.error(f"Error loading model: {e}")
                self.model = IsolationForest(contamination=self.contamination, random_state=42)
                self.is_fitted = False
                self.feature_names = None
        else:
            self.logger.info("No existing model found. A new model will be created.")

# Global variable to store our model instance
anomaly_detector = PersistentAnomalyDetector()

def get_interfaces():
    # Retrieve a list of active network interfaces along with their IP addresses
    # Filter out link-local addresses (starting with '169.254.') and the localhost address ('127.0.0.1')
    return [(iface, addr.address) for iface, addrs in psutil.net_if_addrs().items()
            for addr in addrs if addr.family == socket.AF_INET and not addr.address.startswith('169.254.') and addr.address != '127.0.0.1']


def choose_interface(interfaces, logger):
    # Check if there are any active interfaces
    if not interfaces:
        logger.info("No active network interfaces found. Exiting.")
        return None, None, None

    # Display available interfaces to the user
    logger.info("Available active interfaces:")
    logger.info("")

    # List each interface with an index number
    for i, (iface, ip) in enumerate(interfaces):
        logger.info(f"{i}: {get_display(iface)} (IP: {ip})")

    logger.info("")

    while True:
        # Prompt user to choose an interface
        choice = input("Enter the number of the interface to use: ").strip()
        try:
            choice = int(choice)
            # Check if the choice is within the valid range
            if 0 <= choice < len(interfaces):
                chosen_interface, chosen_ip = interfaces[choice]

                # Attempt to find the subnet mask for the chosen interface
                for ifname in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(ifname)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            if addr['addr'] == chosen_ip:
                                subnet_mask = addr['netmask']
                                logger.info(f"Selected interface: {chosen_interface} (IP: {chosen_ip}, Subnet: {subnet_mask})")
                                return chosen_interface, chosen_ip, subnet_mask

                # If subnet mask couldn't be determined, use a default value
                logger.warning(f"Could not determine subnet mask for {chosen_interface}. Using default 255.255.255.0")
                return chosen_interface, chosen_ip, "255.255.255.0"
            else:
                # Inform user of invalid choice
                logger.info("Invalid choice. Please enter a number within the range of available interfaces.")
        except ValueError:
            # Handle non-numeric input
            logger.info("Invalid input. Please enter a number.")




def capture_packets_worker(interface, count, result_queue, logger):
    # This function captures packets on the specified network interface using Scapy.
    try:
        packets = []  # Initialize a list to store captured packets

        # Define a packet handler function for Scapy to call on each packet captured
        def packet_handler(pkt):
            packets.append(pkt)  # Append the captured packet to the packets list
            # Check if the number of captured packets has reached the specified count
            if len(packets) >= count:
                raise Exception("Capture complete")  # Raise an exception to indicate capture is complete

        start_time = time.time()  # Record the start time of the packet capture
        try:
            # Start sniffing the packets on the specified interface, calling packet_handler for each captured packet
            sniff(iface=interface, prn=packet_handler, store=False, timeout=300)
        except Exception as e:
            # If the exception raised was not "Capture complete", re-raise it
            if "Capture complete" not in str(e):
                raise e

        logger.info(f"Captured {len(packets)} packets")  # Log the total number of packets captured
        # Prepare the packet data as a list of tuples containing time and byte representation of each packet
        packet_data = [(pkt.time, bytes(pkt)) for pkt in packets]
        result_queue.put(packet_data)  # Put the captured packet data into the result queue for further processing
    except Exception as e:
        logger.error(f"Error in capture_packets_worker: {e}", exc_info=True)  # Log any errors that occur during capture
        result_queue.put([])  # Put an empty list into the result queue to indicate failure


def capture_packets(interface, total_count, logger):
    # Get the number of available CPU cores
    num_cores = multiprocessing.cpu_count()

    # Log the start of packet capture including the total number of packets and interface being used
    logger.info(f"Capturing {total_count} packets on {interface} using {num_cores} cores...")

    # Determine how many packets each worker process will capture
    packets_per_worker = total_count // num_cores
    result_queue = multiprocessing.Queue()  # Create a queue to collect results from worker processes
    processes = []  # List to keep track of the spawned processes
    start_time = time.time()  # Record the start time of the packet capture

    # Start worker processes to capture packets
    for _ in range(num_cores):
        p = multiprocessing.Process(target=capture_packets_worker, args=(interface, packets_per_worker, result_queue, logger))
        processes.append(p)  # Add each process to the list
        p.start()  # Start the packet capture process

    all_packets = []  # List to store all captured packets

    # Use a progress bar to visualize the progress of packet capture
    with tqdm(total=total_count, unit='packet', mininterval=0.1) as progress_bar:
        for _ in range(num_cores):
            packets = result_queue.get()  # Retrieve packets captured by the worker processes
            all_packets.extend(packets)  # Add the captured packets to the all_packets list
            progress_bar.update(len(packets))  # Update the progress bar with number of packets captured

    # Wait for all processes to finish their execution
    for p in processes:
        p.join()

    # Calculate duration of the capture and packets per second
    duration = time.time() - start_time
    packets_per_second = len(all_packets) / duration if duration > 0 else 0

    # Log the total number of packets captured, duration, and rate of packets captured per second
    logger.info(f"Captured {len(all_packets)} packets in {duration:.2f} seconds ({packets_per_second:.2f} packets/second)")

    return all_packets  # Return the complete list of captured packets

def analyze_packet(packet, local_ip, current_time, password_regex, credit_card_regex):
    # Check if the packet contains an IP layer
    if IP in packet or IPv6 in packet:
        # Extract source and destination IP addresses from the IP layer
        if IP in packet:
            src_ip, dst_ip = packet[IP].src, packet[IP].dst
        else:
            src_ip, dst_ip = packet[IPv6].src, packet[IPv6].dst

        # Check if the packet contains a TCP layer
        if TCP in packet:
            # Extract source and destination ports from the TCP layer
            src_port, dst_port = packet[TCP].sport, packet[TCP].dport

            # Check if the packet contains an HTTP request layer
            if packet.haslayer(http.HTTPRequest):
                # Convert the HTTP request fields to a string for inspection
                payload = str(packet[http.HTTPRequest].fields)
                # Search for potential password transmission in the payload
                if password_regex.search(payload):
                    return ('Potential password transmission', src_ip, dst_ip)
                # Search for potential credit card transmission in the payload
                if credit_card_regex.search(payload):
                    return ('Potential credit card transmission', src_ip, dst_ip)

            # Check if the TCP flags indicate a SYN packet, which signifies a connection request
            if packet[TCP].flags & 0x02:
                # Return a tuple indicating an outbound connection if the source IP matches the local IP
                return ('Outbound connection', dst_ip, dst_port, src_port, current_time) if src_ip == local_ip else ('Inbound connection', dst_port, src_ip)

        # Check if the packet contains a DNS query layer
        if packet.haslayer(DNSQR):
            # Return a tuple indicating a DNS query along with the source IP and the queried domain name
            return ('DNS query', src_ip, packet[DNSQR].qname.decode('utf-8'))

    # Return None if no relevant information is found in the packet
    return None


def default_dict():
    # This function creates and returns a defaultdict with int as the default_factory
    # It's used to create nested defaultdicts where the inner dictionary has integer values
    return defaultdict(int)

def resolve_ip(ip):
    # Attempt to resolve the given IP address to a hostname
    try:
        # Use gethostbyaddr to get the hostname associated with the provided IP
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.timeout):
        # If there is a socket error or timeout, return the IP as is
        return ip


def is_inbound(packet, local_network):
    # Check if the packet's destination IP belongs to the local network
    # and if the source IP does not belong to the local network
    return ipaddress.ip_address(packet[IP].dst) in local_network and ipaddress.ip_address(packet[IP].src) not in local_network

def analyze_packet_batch(batch, local_network, password_regex_pattern, credit_card_regex_pattern, command_regex_pattern, malware_signatures_pattern, known_exploits_pattern, sql_injection_pattern, xss_pattern):
    # Initialize the result dictionary with default values
    result = {
        'suspicious_activities': [],
        'inbound_connections': defaultdict(default_dict),
        'dns_queries': defaultdict(set),
        'port_scans': defaultdict(set)
    }
    # Convert the local network string to an IP network object
    local_net = ipaddress.ip_network(local_network)

    # Iterate through each packet in the batch
    for packet_data in batch:
        try:
            # Check if packet_data is a tuple and extract the bytes
            if isinstance(packet_data, tuple):
                packet_data = packet_data[1]  # Assuming the bytes are in the second element of the tuple

            # Create a scapy Ether packet object from the raw bytes
            packet = Ether(packet_data)

            # Check if the packet has an IP layer
            if IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                # Check if the packet is inbound to the local network
                if is_inbound(packet, local_net):
                    # Handle TCP packets
                    if TCP in packet:
                        dst_port = packet[TCP].dport
                        result['inbound_connections'][dst_port][src_ip] += 1
                        result['port_scans'][src_ip].add(dst_port)
                    # Handle UDP packets
                    elif UDP in packet:
                        dst_port = packet[UDP].dport
                        result['inbound_connections'][dst_port][src_ip] += 1
                        result['port_scans'][src_ip].add(dst_port)

                    # Check for DNS queries
                    if DNS in packet and packet.haslayer(DNSQR):
                        query = packet[DNSQR].qname.decode('utf-8')
                        result['dns_queries'][src_ip].add(query)

                    # Analyze packet payload if present
                    if Raw in packet:
                        payload = packet[Raw].load.decode('utf-8', errors='ignore')
                        # Check for various suspicious patterns in the payload
                        if re.search(password_regex_pattern, payload):
                            result['suspicious_activities'].append(('Potential password in clear text', src_ip, dst_ip))
                        if re.search(credit_card_regex_pattern, payload):
                            result['suspicious_activities'].append(('Potential credit card number in clear text', src_ip, dst_ip))
                        if re.search(command_regex_pattern, payload):
                            result['suspicious_activities'].append(('Potential command execution', src_ip, dst_ip))
                        if re.search(malware_signatures_pattern, payload):
                            result['suspicious_activities'].append(('Potential malware signature', src_ip, dst_ip))
                        if re.search(known_exploits_pattern, payload):
                            result['suspicious_activities'].append(('Potential known exploit', src_ip, dst_ip))
                        if re.search(sql_injection_pattern, payload):
                            result['suspicious_activities'].append(('Potential SQL injection attempt', src_ip, dst_ip))
                        if re.search(xss_pattern, payload):
                            result['suspicious_activities'].append(('Potential XSS attack', src_ip, dst_ip))
        except Exception as e:
            # Log the error or handle it as appropriate for your use case
            pass

    # Return the analysis results
    return result


def analyze_traffic(raw_packets: List[Tuple[Any, bytes]], logger: Any, port_scan_threshold: int, dns_query_threshold: int, local_ip: str, subnet_mask: str) -> List[Tuple]:
    # Initialize data structures to store analysis results
    suspicious_activities = []
    inbound_connections = defaultdict(lambda: defaultdict(int))
    dns_queries = defaultdict(set)
    port_scans = defaultdict(set)

    # Check if local IP and subnet mask are provided
    if not local_ip or not subnet_mask:
        logger.warning("Unable to determine local IP or subnet mask. Analysis may be inaccurate.")
        return suspicious_activities

    try:
        # Create an IP network object from local IP and subnet mask
        local_network = ipaddress.ip_network(f"{local_ip}/{subnet_mask}", strict=False)
        logger.info(f"Local IP: {local_ip}")
        logger.info(f"Subnet Mask: {subnet_mask}")
        logger.info(f"Local network: {local_network}")

        # Define regex patterns for various types of suspicious activities
        password_regex_pattern = r'password=\S+'
        credit_card_regex_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        command_regex_pattern = r'\b(curl|wget|bash|sh|php|ruby|perl|nc)\b'
        malware_signatures_pattern = r'\b(eval\(|base64_decode|exec|system|shell_exec|cmd\.exe|powershell\.exe)\b'
        known_exploits_pattern = r'(/etc/passwd|/bin/bash|/bin/sh|\.\.\/\.\./|\.php\?id=)'
        sql_injection_pattern = r'\b(UNION\s+SELECT|OR\s+1=1|AND\s+1=1|SLEEP\(\d+\)|WAITFOR\s+DELAY|SELECT\s+FROM|INSERT\s+INTO|UPDATE\s+.*SET|DELETE\s+FROM)\b'
        xss_pattern = r'(<script>|<\/script>|javascript:|onerror=|onload=|eval\(|document\.cookie)'

        # Split raw packets into batches for parallel processing
        batch_size = 100
        packet_batches = [raw_packets[i:i + batch_size] for i in range(0, len(raw_packets), batch_size)]

        # Use ProcessPoolExecutor for parallel processing of packet batches
        with ProcessPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(
                analyze_packet_batch,
                packet_batches,
                [str(local_network)] * len(packet_batches),
                [password_regex_pattern] * len(packet_batches),
                [credit_card_regex_pattern] * len(packet_batches),
                [command_regex_pattern] * len(packet_batches),
                [malware_signatures_pattern] * len(packet_batches),
                [known_exploits_pattern] * len(packet_batches),
                [sql_injection_pattern] * len(packet_batches),
                [xss_pattern] * len(packet_batches)
            ))

        # Process results from parallel execution
        for result in results:
            # Add suspicious activities to the list
            for activity_type, *params in result['suspicious_activities']:
                resolved_params = [resolve_ip(param) if isinstance(param, str) and re.match(r'\d+\.\d+\.\d+\.\d+', param) else param for param in params]
                suspicious_activities.append((activity_type, *resolved_params))

            # Update inbound connections data
            for port, connections in result['inbound_connections'].items():
                inbound_connections[port].update(connections)

            # Update DNS queries data
            for src_ip, queries in result['dns_queries'].items():
                dns_queries[src_ip].update(queries)

            # Update port scans data
            for src_ip, ports in result['port_scans'].items():
                port_scans[src_ip].update(ports)

        # Analyze inbound connections for suspicious activity
        for port, connections in inbound_connections.items():
            total_attempts = sum(connections.values())
            if total_attempts > 10 and port < 1024:
                top_source = max(connections, key=connections.get)
                suspicious_activities.append(('High volume of inbound connections to privileged port', port, total_attempts, f"Top source: {resolve_ip(top_source)}"))

        # Analyze port scans
        for src_ip, ports in port_scans.items():
            if len(ports) > port_scan_threshold:
                suspicious_activities.append(('Potential port scan attempt', resolve_ip(src_ip), f"Ports scanned: {len(ports)}"))

        # Analyze DNS queries
        for ip, queries in dns_queries.items():
            if len(queries) > dns_query_threshold:
                suspicious_activities.append(('High volume of unique DNS queries', resolve_ip(ip), f"Unique queries: {len(queries)}"))

        # Remove duplicate suspicious activities
        unique_suspicious_activities = list(set(suspicious_activities))

    except Exception as e:
        # Log any errors that occur during analysis
        logger.error(f"Error during traffic analysis: {str(e)}")
        unique_suspicious_activities = []

    # Return the list of unique suspicious activities
    return unique_suspicious_activities

def extract_features(raw_packets):
    features = []
    for packet in raw_packets:
        if isinstance(packet, tuple):
            packet = Ether(packet[1])
        
        is_ip = int(IP in packet)
        is_ipv6 = int(IPv6 in packet)
        is_tcp = int(TCP in packet)
        is_udp = int(UDP in packet)
        
        # Determine IP layer
        ip_layer = packet[IP] if is_ip else (packet[IPv6] if is_ipv6 else None)
        
        # Handle TTL extraction
        ttl = 0
        if ip_layer:
            try:
                ttl = ip_layer.ttl
            except AttributeError:
                try:
                    ttl = ip_layer._ttl
                except AttributeError:
                    # If both fail, leave ttl as 0
                    pass

        feature = [
            len(packet),                    # packet_length
            is_ip,                          # is_ip
            is_ipv6,                        # is_ipv6
            is_tcp,                         # is_tcp
            is_udp,                         # is_udp
            int(DNS in packet),             # is_dns
            int(packet.haslayer(LLMNRQuery) or packet.haslayer(LLMNRResponse)),  # is_llmnr
            int(packet.dst.startswith("01:00:5e") or packet.dst.startswith("33:33")),  # is_multicast
            int(packet.dst == "ff:ff:ff:ff:ff:ff" or (is_ip and ip_layer.dst == "255.255.255.255")),  # is_broadcast
            ttl,                            # ttl (now using the value we extracted above)
            packet[TCP].sport if is_tcp else (packet[UDP].sport if is_udp else 0),  # src_port
            packet[TCP].dport if is_tcp else (packet[UDP].dport if is_udp else 0),  # dst_port
            int(packet.haslayer(Raw)),      # has_payload
            len(packet[Raw].load) if Raw in packet else 0,  # payload_length
            int(is_tcp and packet[TCP].flags & 0x02),  # is_syn
            int(is_tcp and packet[TCP].flags & 0x12),  # is_syn_ack
            int(is_ipv6 and ICMPv6ND_NS in packet),  # is_icmpv6_nd
            int('STP' in packet),           # is_stp
            int(ARP in packet)              # is_arp
        ]
        features.append(feature)
    return features





def train_anomaly_detector(data):
    # Initialize an Isolation Forest model with 10% contamination and a fixed random state
    model = IsolationForest(contamination=0.1, random_state=42)
    # Fit the model to the provided data
    model.fit(data)
    # Return the trained model
    return model

def detect_anomalies(model, new_data):
    # Use the trained model to make predictions on new data
    predictions = model.predict(new_data)
    # Return the predictions (-1 for anomalies, 1 for normal instances)
    return predictions

def is_whitelisted(packet):
    logger = logging.getLogger(__name__)
    
    # Check IP whitelist
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        if any(ip_address(src_ip) in network or ip_address(dst_ip) in network for network in WHITELISTED_IPS):
            logger.debug(f"Packet whitelisted due to IP: {src_ip} or {dst_ip}")
            return True

    # Check port whitelist
    if TCP in packet or UDP in packet:
        sport = packet[TCP].sport if TCP in packet else packet[UDP].sport
        dport = packet[TCP].dport if TCP in packet else packet[UDP].dport
        if any(start <= sport <= end or start <= dport <= end for start, end in WHITELISTED_PORTS):
            logger.debug(f"Packet whitelisted due to port: {sport} or {dport}")
            return True

    # Check protocol whitelist
    if IP in packet:
        proto = packet[IP].proto
        if proto in [6, 17, 1]:  # TCP, UDP, ICMP
            proto_name = {6: "TCP", 17: "UDP", 1: "ICMP"}[proto]
            if proto_name in WHITELISTED_PROTOCOLS:
                logger.debug(f"Packet whitelisted due to protocol: {proto_name}")
                return True
    elif IPv6 in packet:
        if packet[IPv6].nh in [6, 17, 58]:  # TCP, UDP, ICMPv6
            proto_name = {6: "TCP", 17: "UDP", 58: "ICMPv6"}[packet[IPv6].nh]
            if proto_name in WHITELISTED_PROTOCOLS:
                logger.debug(f"Packet whitelisted due to protocol: {proto_name}")
                return True

    # Check time-based whitelist
    current_time = time.strftime("%H:%M")
    for window_name, (start_time, end_time) in TIME_BASED_WHITELIST.items():
        if start_time <= current_time <= end_time:
            logger.debug(f"Packet whitelisted due to time window: {window_name}")
            return True

    # Check domain whitelist for DNS queries
    if packet.haslayer(DNSQR):
        qname = packet[DNSQR].qname.decode('utf-8')
        if any(pattern.match(qname) for pattern in COMPILED_DOMAIN_PATTERNS):
            logger.debug(f"Packet whitelisted due to DNS query domain: {qname}")
            return True

    # Whitelist certain types of broadcast packets
    if packet.dst == "ff:ff:ff:ff:ff:ff":
        # Whitelist common broadcast protocols
        if ARP in packet:
            logger.debug("Packet whitelisted: ARP broadcast")
            return True
        if DHCP in packet or (UDP in packet and packet[UDP].dport in [67, 68]):  # DHCP
            logger.debug("Packet whitelisted: DHCP broadcast")
            return True
        if packet.type == 0x0806:  # ARP
            logger.debug("Packet whitelisted: ARP broadcast")
            return True
        if packet.type == 0x86DD and ICMPv6ND_NS in packet:  # IPv6 Neighbor Discovery
            logger.debug("Packet whitelisted: IPv6 Neighbor Discovery")
            return True

    # Whitelist ICMPv6 Neighbor Discovery packets
    if IPv6 in packet and ICMPv6ND_NS in packet:
        logger.debug("Packet whitelisted: ICMPv6 Neighbor Discovery")
        return True

    # Whitelist STP (Spanning Tree Protocol) packets
    if packet.haslayer('STP'):
        logger.debug("Packet whitelisted: Spanning Tree Protocol")
        return True

    # Whitelist LLDP (Link Layer Discovery Protocol) packets
    if packet.type == 0x88cc:
        logger.debug("Packet whitelisted: LLDP")
        return True

    # Whitelist common multicast packets
    if packet.dst.startswith(("01:00:5e", "33:33")):  # IPv4 and IPv6 multicast
        logger.debug("Packet whitelisted: Multicast")
        return True

    # Whitelist local network ARP
    if ARP in packet:
        arp_src_ip = packet[ARP].psrc
        arp_dst_ip = packet[ARP].pdst
        if (ip_address(arp_src_ip) in ip_network('10.0.0.0/8') or
            ip_address(arp_dst_ip) in ip_network('10.0.0.0/8') or
            ip_address(arp_src_ip) in ip_network('192.168.0.0/16') or
            ip_address(arp_dst_ip) in ip_network('192.168.0.0/16') or
            ip_address(arp_src_ip) in ip_network('172.16.0.0/12') or
            ip_address(arp_dst_ip) in ip_network('172.16.0.0/12')):
            logger.debug("Packet whitelisted: Local network ARP")
            return True

    logger.debug(f"Packet not whitelisted: {packet.summary()}")
    return False



def analyze_traffic_with_ml(raw_packets, logger):
    global anomaly_detector

    features = extract_features(raw_packets)
    
    if not features:
        logger.warning("No packets captured or no features extracted. Skipping ML analysis.")
        return [], []

    df = pd.DataFrame(features, columns=FEATURE_NAMES)

    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            logger.warning(f"Column {col} is not numeric. Converting to numeric.")
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.fillna(0)

    if df.empty:
        logger.warning("DataFrame is empty after preprocessing. Skipping ML analysis.")
        return [], []

    # Always update the model
    anomaly_detector.partial_fit(df)
    
    if not anomaly_detector.is_fitted:
        logger.warning("Anomaly detector is not fitted. Skipping anomaly detection.")
        return [], []

    anomaly_scores = -anomaly_detector.model.score_samples(df)

    threshold = np.percentile(anomaly_scores, 99)  # Adjust this percentile as needed
    anomalies = anomaly_scores > threshold

    anomaly_count = np.sum(anomalies)
    logger.info(f"ML model detected {anomaly_count} anomalies out of {len(raw_packets)} packets")

    anomaly_details = []
    whitelisted_anomalies = 0
    broadcast_anomalies = 0
    broadcast_types = defaultdict(int)

    for i, (is_anomaly, score, packet) in enumerate(zip(anomalies, anomaly_scores, raw_packets)):
        if is_anomaly:
            if isinstance(packet, tuple):
                packet = Ether(packet[1])
            
            if packet.dst == "ff:ff:ff:ff:ff:ff":
                broadcast_anomalies += 1
                broadcast_types[packet.type] += 1
                logger.debug(f"Broadcast packet detected at packet {i}: {packet.summary()} | Score: {score:.2f}")
            elif not is_whitelisted(packet):
                packet_summary = packet.summary()
                packet_type = "Unicast"
                protocol = packet.lastlayer().name
                anomaly_details.append(f"Anomaly at packet {i}: {packet_summary} | Type: {packet_type} | Protocol: {protocol} | Score: {score:.2f}")
            else:
                whitelisted_anomalies += 1
                logger.debug(f"Whitelisted anomaly at packet {i}: {packet.summary()} | Score: {score:.2f}")

    logger.info(f"Total anomalies: {anomaly_count}, Whitelisted: {whitelisted_anomalies}, Broadcast: {broadcast_anomalies}, Reported: {len(anomaly_details)}")
    
    if broadcast_types:
        logger.info("Broadcast packet types detected as anomalies:")
        for ether_type, count in broadcast_types.items():
            logger.info(f"  EtherType 0x{ether_type:04x}: {count} packets")

    if anomaly_details:
        logger.info("Anomalies detected by machine learning model after whitelisting and broadcast filtering:")
        for detail in anomaly_details[:10]:
            logger.info(detail)
        if len(anomaly_details) > 10:
            logger.info(f"... and {len(anomaly_details) - 10} more anomalies.")
    else:
        logger.info("No non-broadcast anomalies detected by machine learning model after whitelisting.")

    return anomalies, anomaly_details




def process_packet_batch(interface, count, logger, port_scan_threshold, dns_query_threshold, local_ip, subnet_mask):
    # Capture a specified number of packets from the given network interface
    packets = capture_packets(interface, count, logger)

    # Check if any packets were captured
    if not packets:
        logger.warning("No packets captured. Network might be disconnected.")
        return [], [], [], []  # Return empty lists for all results

    # Analyze the captured packets for suspicious activities
    suspicious_activities = analyze_traffic(packets, logger, port_scan_threshold, dns_query_threshold, local_ip, subnet_mask)

    # Perform machine learning-based anomaly detection on the captured packets
    anomalies, anomaly_details = analyze_traffic_with_ml(packets, logger)

    # Return all the results: raw packets, detected suspicious activities,
    # anomaly flags, and detailed information about the anomalies
    return packets, suspicious_activities, anomalies, anomaly_details



def log_results(logger, suspicious_activities, anomaly_details):
    # Check if any suspicious activities were detected
    if suspicious_activities:
        logger.info("Suspicious activities detected!")
        # Iterate through each suspicious activity and log it
        for activity in suspicious_activities:
            logger.info(f"- {': '.join(map(str, activity))}")
    else:
        # Log if no suspicious activities were found
        logger.info("No suspicious activities detected in this batch.")

    # Check if any anomalies were detected by the machine learning model
    if anomaly_details:
        logger.info("Anomalies detected by machine learning model!")
        # Log the details of the first 10 anomalies
        for detail in anomaly_details[:10]:
            logger.info(detail)
        # If there are more than 10 anomalies, log a summary of the remaining
        if len(anomaly_details) > 10:
            logger.info(f"... and {len(anomaly_details) - 10} more anomalies.")



def log_suspicious_activities(log_file, data, logger):
    # Get the current timestamp for logging
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # Open the log file in append mode with UTF-8 encoding
    with open(log_file, 'a', encoding='utf-8') as f:
        # Iterate over the list of suspicious activity data
        for item in data:
            # Create a log message by combining the timestamp and the string representation of each item
            log_message = f"{timestamp} - {': '.join(map(str, item))}"
            # Write the log message to the log file
            f.write(log_message + "\n")
            # Log the message as a warning
            logger.warning(log_message)
        f.flush()  # Ensure all data is flushed to the file
        # Synchronize the file's contents with the storage device
        os.fsync(f.fileno())

def check_root_linux():
    # Check if the script is running on a Linux system
    if sys.platform.startswith('linux'):
        # Check if the script is running with root privileges
        if os.geteuid() != 0:
            # If not running as root, print instructions and exit
            print("This script requires root privileges to capture network packets on Linux.")
            print("Please run the script with sudo, like this:")
            print("sudo python3 network_monitor.py")
            sys.exit(1)

def setup_network_interface(args, logger):
    # Get a list of active network interfaces
    interfaces = get_interfaces()

    # If no active interfaces are found, log the information and return None values
    if not interfaces:
        logger.info("No active network interfaces found. Exiting.")
        return None, None, None

    # Check if a specific interface was provided as an argument
    if args.interface:
        interface = args.interface
        # Find the interface info that matches the provided interface name
        interface_info = next((info for info in interfaces if info[0] == interface), None)
        if interface_info:
            # If the interface is found, set the local IP and assume a default subnet mask
            local_ip, subnet_mask = interface_info[1], "255.255.255.0"  # Assuming a default subnet mask
        else:
            # If the specified interface is not found, log the information and return None values
            logger.info(f"Specified interface {interface} not found. Exiting.")
            return None, None, None
    else:
        # If no interface was specified, prompt the user to choose one
        interface, local_ip, subnet_mask = choose_interface(interfaces, logger)

    # If no interface was selected (user cancelled or error occurred), return None values
    if not interface:
        logger.info("No interface selected. Exiting.")
        return None, None, None

    # Log the selected interface and its IP address
    logger.info(f"Using network interface: {get_display(interface)} with IP: {local_ip}")
    # Return the selected interface, its IP address, and subnet mask
    return interface, local_ip, subnet_mask

def main():
    parser = argparse.ArgumentParser(description='Network Monitor')
    parser.add_argument('--interface', type=str, help='Network interface to use')
    args = parser.parse_args()

    check_root_linux()

    logger, log_listener = setup_logging_queue()
    log_listener.start()

    try:
        PORT_SCAN_THRESHOLD = 20
        DNS_QUERY_THRESHOLD = 50
        COUNT = 1000

        interface, local_ip, subnet_mask = setup_network_interface(args, logger)
        if not interface:
            logger.error("No valid interface found. Exiting.")
            return

        false_positive_count = defaultdict(int)
        iteration_count = 0
        save_interval = 10  # Save every 10 iterations, adjust as needed

        global anomaly_detector
        anomaly_detector = PersistentAnomalyDetector()
        anomaly_detector.load_model()  # Load existing model if available

        while True:
            try:
                packets, suspicious_activities, anomalies, anomaly_details = process_packet_batch(
                    interface, COUNT, logger, PORT_SCAN_THRESHOLD, DNS_QUERY_THRESHOLD, local_ip, subnet_mask
                )

                if packets:
                    if suspicious_activities:
                        logger.info("Suspicious activities detected:")
                        for activity in suspicious_activities:
                            logger.info(f"- {': '.join(map(str, activity))}")
                    else:
                        logger.info("No suspicious activities detected by regular analysis.")

                    if anomaly_details:
                        logger.info("Anomalies detected by machine learning model:")
                        for detail in anomaly_details[:10]:
                            logger.info(detail)
                        if len(anomaly_details) > 10:
                            logger.info(f"... and {len(anomaly_details) - 10} more anomalies.")
                    else:
                        logger.info("No anomalies detected by machine learning model.")

                    for detail in anomaly_details:
                        false_positive_count[detail] += 1
                        if false_positive_count[detail] > 10:
                            logger.info(f"Adapting to frequent anomaly: {detail}")
                            false_positive_count[detail] = 0
                else:
                    logger.warning("No packets captured in this batch. Network might be disconnected.")

                iteration_count += 1
                if iteration_count % save_interval == 0:
                    anomaly_detector.save_model()

            except Exception as e:
                logger.error(f"An error occurred during packet processing: {e}", exc_info=True)

            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("\nStopping packet capture. Exiting.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        log_listener.stop()

if __name__ == "__main__":
    main()







