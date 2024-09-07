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
import ipaddress
import netifaces
import argparse
import ctypes
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any, Tuple
from scapy.all import IP, IPv6, TCP, UDP, DNS, DNSQR, Raw, Ether, sniff
from scapy.layers import http
from scapy.layers import http, dns
from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict
from multiprocessing import Queue
from tqdm import tqdm
from bidi.algorithm import get_display
from logging.handlers import QueueHandler, QueueListener
from scapy.layers.llmnr import LLMNRQuery as LLMNR
from sklearn.ensemble import IsolationForest
from scapy.layers.llmnr import LLMNRQuery, LLMNRResponse
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS

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
    'is_icmpv6_nd'    # Boolean flag indicating if the packet is an ICMPv6 Neighbor Discovery packet
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

# PersistentAnomalyDetector class for detecting anomalies in network traffic
class PersistentAnomalyDetector:
    def __init__(self, model_path='anomaly_model.joblib', contamination=0.05):
        # Initialize the detector with a model path and contamination rate
        self.model_path = model_path
        self.contamination = contamination
        try:
            # Attempt to load a pre-existing model
            self.model = joblib.load(model_path)
        except:
            # If loading fails, create a new IsolationForest model
            self.model = IsolationForest(contamination=contamination, random_state=42)
        # Check if the model is already fitted
        self.is_fitted = hasattr(self.model, 'offset_')

    def partial_fit(self, X):
        # Method to fit the model on new data
        if not self.is_fitted:
            # If the model is not fitted, fit it on the new data
            self.model.fit(X)
            self.is_fitted = True
        else:
            # If the model is already fitted, create a new one and fit it
            # This is because IsolationForest doesn't support partial_fit
            self.model = IsolationForest(contamination=self.contamination, random_state=42)
            self.model.fit(X)
        # Save the updated model to disk
        joblib.dump(self.model, self.model_path)

    def predict(self, X):
        # Method to make predictions on new data
        if not self.is_fitted:
            # Raise an error if the model hasn't been fitted yet
            raise ValueError("Model is not fitted yet. Call 'partial_fit' first.")
        # Return predictions
        return self.model.predict(X)

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
        # Convert tuple packet to Scapy Ether packet if necessary
        if isinstance(packet, tuple):
            packet = Ether(packet[1])

        # Initialize multicast and broadcast flags
        is_multicast = False
        is_broadcast = False

        # Check for multicast in IPv6
        if IPv6 in packet:
            is_multicast = packet[IPv6].dst.startswith('ff')
        # Check for multicast and broadcast in IPv4
        elif IP in packet:
            is_multicast = packet[IP].dst.startswith('224')
            is_broadcast = packet[IP].dst == '255.255.255.255'

        # Check for ICMPv6 Neighbor Discovery
        is_icmpv6_nd = int(IPv6 in packet and ICMPv6ND_NS in packet)

        # Extract features from the packet
        feature = [
            len(packet),  # Total packet length
            int(IP in packet),  # Is IPv4
            int(IPv6 in packet),  # Is IPv6
            int(TCP in packet),  # Is TCP
            int(UDP in packet),  # Is UDP
            int(DNS in packet),  # Is DNS
            int(packet.haslayer(LLMNRQuery) or packet.haslayer(LLMNRResponse)),  # Is LLMNR
            int(is_multicast),  # Is multicast
            int(is_broadcast),  # Is broadcast
            packet[IP].ttl if IP in packet else (packet[IPv6].hlim if IPv6 in packet else 0),  # TTL or Hop Limit
            packet[TCP].sport if TCP in packet else (packet[UDP].sport if UDP in packet else 0),  # Source port
            packet[TCP].dport if TCP in packet else (packet[UDP].dport if UDP in packet else 0),  # Destination port
            int(packet.haslayer(Raw)),  # Has payload
            len(packet[Raw].load) if Raw in packet else 0,  # Payload length
            int(packet[TCP].flags == 2) if TCP in packet else 0,  # Is SYN flag set
            int(packet[TCP].flags == 18) if TCP in packet else 0,  # Is SYN-ACK flag set
            is_icmpv6_nd  # Is ICMPv6 Neighbor Discovery
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
    # Define a set of common ports that are considered normal
    common_ports = {80, 443, 53, 123}  # HTTP, HTTPS, DNS, NTP
    # Check if the packet is TCP or UDP
    if TCP in packet or UDP in packet:
        # Extract source and destination ports
        sport = packet[TCP].sport if TCP in packet else packet[UDP].sport
        dport = packet[TCP].dport if TCP in packet else packet[UDP].dport
        # Return True if either port is in the common_ports set
        return sport in common_ports or dport in common_ports
    # Check if the packet is an ICMPv6 Neighbor Discovery packet
    if IPv6 in packet and ICMPv6ND_NS in packet:
        # Whitelist ICMPv6 Neighbor Discovery packets
        return True
    # If none of the above conditions are met, return False
    return False



def analyze_traffic_with_ml(raw_packets, logger):
    global anomaly_detector

    # Extract features from the raw packets
    features = extract_features(raw_packets)
    # Create a DataFrame from the extracted features
    df = pd.DataFrame(features, columns=FEATURE_NAMES)

    # Check if the anomaly detector model has been fitted
    if not anomaly_detector.is_fitted:
        logger.info("Fitting the anomaly detection model for the first time.")
        # Fit the model with the current data
        anomaly_detector.partial_fit(df)
        # Make predictions using the newly fitted model
        anomalies = anomaly_detector.predict(df)
    else:
        try:
            # Attempt to make predictions with the existing model
            anomalies = anomaly_detector.predict(df)
        except ValueError as e:
            # Handle the case where there's a feature mismatch
            logger.warning(f"Feature mismatch detected: {str(e)}")
            logger.info("Retraining the model with the current feature set.")
            # Create a new anomaly detector and fit it with the current data
            anomaly_detector = PersistentAnomalyDetector()
            anomaly_detector.partial_fit(df)
            # Make predictions using the newly fitted model
            anomalies = anomaly_detector.predict(df)

    # Update the model with the current data to adapt over time
    anomaly_detector.partial_fit(df)

    # Count the number of detected anomalies
    anomaly_count = np.sum(anomalies == -1)
    logger.info(f"ML model detected {anomaly_count} anomalies out of {len(raw_packets)} packets")

    # Initialize a list to store detailed information about anomalies
    anomaly_details = []

    # Iterate through the anomalies and corresponding packets
    for i, (anomaly, packet) in enumerate(zip(anomalies, raw_packets)):
        if anomaly == -1:
            # Convert tuple packet to Scapy packet if necessary
            if isinstance(packet, tuple):
                packet = Ether(packet[1])
            # Check if the packet is not whitelisted
            if not is_whitelisted(packet):
                # Get a summary of the anomalous packet
                packet_summary = packet.summary()
                anomaly_details.append(f"Anomaly at packet {i}: {packet_summary}")

    # Log detailed information about the first 10 anomalies
    for detail in anomaly_details[:10]:
        logger.info(detail)

    # If there are more than 10 anomalies, log a summary of the remaining
    if len(anomaly_details) > 10:
        logger.info(f"... and {len(anomaly_details) - 10} more anomalies.")

    # Return the anomaly predictions and detailed information
    return anomalies, anomaly_details

def process_packet_batch(interface, count, logger, port_scan_threshold, dns_query_threshold, local_ip, subnet_mask):
    # Capture a specified number of packets from the given network interface
    packets = capture_packets(interface, count, logger)

    # Analyze the captured packets for suspicious activities
    # This includes checking for port scans, unusual DNS queries, and other potential threats
    suspicious_activities = analyze_traffic(packets, logger, port_scan_threshold, dns_query_threshold, local_ip, subnet_mask)

    # Perform machine learning-based anomaly detection on the captured packets
    # This can identify unusual patterns that might not be caught by rule-based analysis
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
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Network Monitor')
    parser.add_argument('--interface', type=str, help='Network interface to use')
    args = parser.parse_args()

    # Check for root privileges on Linux systems
    check_root_linux()

    # Set up logging queue and start the log listener
    logger, log_listener = setup_logging_queue()
    log_listener.start()
    try:
        # Define thresholds for detecting suspicious activities
        PORT_SCAN_THRESHOLD = 20
        DNS_QUERY_THRESHOLD = 50
        COUNT = 1000  # Number of packets to capture in each batch

        # Set up the network interface for packet capture
        interface, local_ip, subnet_mask = setup_network_interface(args, logger)
        if not interface:
            return  # Exit if no valid interface is found

        # Initialize a counter for tracking potential false positives
        false_positive_count = defaultdict(int)

        # Main monitoring loop
        while True:
            # Process a batch of packets and analyze for suspicious activities and anomalies
            packets, suspicious_activities, anomalies, anomaly_details = process_packet_batch(
                interface, COUNT, logger, PORT_SCAN_THRESHOLD, DNS_QUERY_THRESHOLD, local_ip, subnet_mask
            )

            # Log suspicious activities if any are detected
            if suspicious_activities:
                logger.info("Suspicious activities detected:")
                for activity in suspicious_activities:
                    logger.info(f"- {': '.join(map(str, activity))}")
            else:
                logger.info("No suspicious activities detected by regular analysis.")

            # Log anomalies detected by the machine learning model
            if anomaly_details:
                logger.info("Anomalies detected by machine learning model:")
                for detail in anomaly_details[:10]:  # Log details of first 10 anomalies
                    logger.info(detail)
                if len(anomaly_details) > 10:
                    logger.info(f"... and {len(anomaly_details) - 10} more anomalies.")
            else:
                logger.info("No anomalies detected by machine learning model.")

            # Handle potential false positives
            for detail in anomaly_details:
                false_positive_count[detail] += 1
                if false_positive_count[detail] > 10:  # Adjust this threshold as needed
                    logger.info(f"Adapting to frequent anomaly: {detail}")
                    # Here you could add logic to adjust the model or features
                    false_positive_count[detail] = 0

            # Wait for 60 seconds before processing the next batch
            time.sleep(60)

    except KeyboardInterrupt:
        # Handle user interruption (e.g., Ctrl+C)
        logger.info("\nStopping packet capture. Exiting.")
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"An error occurred: {e}", exc_info=True)
    finally:
        # Ensure the log listener is stopped before exiting
        log_listener.stop()

# Entry point of the script
if __name__ == "__main__":
    main()






