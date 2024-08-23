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
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any, Tuple
from scapy.all import IP, TCP, UDP, DNS, DNSQR, Raw, scapy, Ether
from scapy.layers import http, dns
from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict
from multiprocessing import Queue
from tqdm import tqdm
from bidi.algorithm import get_display
from logging.handlers import QueueHandler, QueueListener

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
def get_interfaces():
    # Retrieve a list of active network interfaces along with their IP addresses
    # Filter out link-local addresses (starting with '169.254.') and the localhost address ('127.0.0.1')
    return [(iface, addr.address) for iface, addrs in psutil.net_if_addrs().items()
            for addr in addrs if addr.family == socket.AF_INET and not addr.address.startswith('169.254.') and addr.address != '127.0.0.1']


def choose_interface(interfaces, logger):
    if not interfaces:
        logger.info("No active network interfaces found. Exiting.")
        return None, None, None

    logger.info("Available active interfaces:")
    logger.info("")

    for i, (iface, ip) in enumerate(interfaces):
        logger.info(f"{i}: {get_display(iface)} (IP: {ip})")

    logger.info("")

    while True:
        choice = input("Enter the number of the interface to use: ").strip()
        try:
            choice = int(choice)
            if 0 <= choice < len(interfaces):
                chosen_interface, chosen_ip = interfaces[choice]
                
                # Find the matching interface in netifaces
                for ifname in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(ifname)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            if addr['addr'] == chosen_ip:
                                subnet_mask = addr['netmask']
                                logger.info(f"Selected interface: {chosen_interface} (IP: {chosen_ip}, Subnet: {subnet_mask})")
                                return chosen_interface, chosen_ip, subnet_mask
                
                logger.warning(f"Could not determine subnet mask for {chosen_interface}. Using default 255.255.255.0")
                return chosen_interface, chosen_ip, "255.255.255.0"
            else:
                logger.info("Invalid choice. Please enter a number within the range of available interfaces.")
        except ValueError:
            logger.info("Invalid input. Please enter a number.")




def capture_packets_worker(interface, count, result_queue, logger):
    # This function captures packets on the specified network interface using Scapy.
    try:
        from scapy.all import sniff  # Import the sniff function from Scapy for packet capture
        logger.info(f"Starting packet capture on interface {interface} using scapy")  # Log the start of the capture
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
    if packet.haslayer(scapy.IP):
        # Extract source and destination IP addresses from the IP layer
        src_ip, dst_ip = packet[scapy.IP].src, packet[scapy.IP].dst
        
        # Check if the packet contains a TCP layer
        if packet.haslayer(scapy.TCP):
            # Extract source and destination ports from the TCP layer
            src_port, dst_port = packet[scapy.TCP].sport, packet[scapy.TCP].dport
            
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
            if packet[scapy.TCP].flags & 0x02:
                # Return a tuple indicating an outbound connection if the source IP matches the local IP
                return ('Outbound connection', dst_ip, dst_port, src_port, current_time) if src_ip == local_ip else ('Inbound connection', dst_port, src_ip)
        
        # Check if the packet contains a DNS query layer
        if packet.haslayer(dns.DNSQR):
            # Return a tuple indicating a DNS query along with the source IP and the queried domain name
            return ('DNS query', src_ip, packet[dns.DNSQR].qname.decode('utf-8'))
    
    # Return None if no relevant information is found in the packet
    return None

def default_dict():
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

def process_packet_batch(batch, local_network, password_regex_pattern, credit_card_regex_pattern, command_regex_pattern, malware_signatures_pattern, known_exploits_pattern):
    result = {
        'suspicious_activities': [],
        'inbound_connections': defaultdict(default_dict),
        'dns_queries': defaultdict(set),
        'port_scans': defaultdict(set)
    }
    local_net = ipaddress.ip_network(local_network)
    for packet_data in batch:
        try:
            # Check if packet_data is a tuple and extract the bytes
            if isinstance(packet_data, tuple):
                packet_data = packet_data[1]  # Assuming the bytes are in the second element of the tuple
            packet = Ether(packet_data)
            if IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                if is_inbound(packet, local_net):
                    if TCP in packet:
                        dst_port = packet[TCP].dport
                        result['inbound_connections'][dst_port][src_ip] += 1
                        result['port_scans'][src_ip].add(dst_port)
                    elif UDP in packet:
                        dst_port = packet[UDP].dport
                        result['inbound_connections'][dst_port][src_ip] += 1
                        result['port_scans'][src_ip].add(dst_port)
                    if DNS in packet and packet.haslayer(DNSQR):
                        query = packet[DNSQR].qname.decode('utf-8')
                        result['dns_queries'][src_ip].add(query)
                    if Raw in packet:
                        payload = packet[Raw].load.decode('utf-8', errors='ignore')
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
        except Exception as e:
            # Log the error or handle it as appropriate for your use case
            pass
    return result

def analyze_traffic(raw_packets: List[Tuple[Any, bytes]], logger: Any, port_scan_threshold: int, dns_query_threshold: int, local_ip: str, subnet_mask: str) -> List[Tuple]:
    suspicious_activities = []
    inbound_connections = defaultdict(lambda: defaultdict(int))
    dns_queries = defaultdict(set)
    port_scans = defaultdict(set)

    if not local_ip or not subnet_mask:
        logger.warning("Unable to determine local IP or subnet mask. Analysis may be inaccurate.")
        return suspicious_activities

    try:
        # Create local_network using the provided local_ip and subnet_mask
        local_network = ipaddress.ip_network(f"{local_ip}/{subnet_mask}", strict=False)
        logger.info(f"Local IP: {local_ip}")
        logger.info(f"Subnet Mask: {subnet_mask}")
        logger.info(f"Local network: {local_network}")

        password_regex_pattern = r'password=\S+'
        credit_card_regex_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        command_regex_pattern = r'\b(curl|wget|bash|sh|php|ruby|perl|nc)\b'
        malware_signatures_pattern = r'\b(eval\(|base64_decode|exec|system|shell_exec|cmd\.exe|powershell\.exe)\b'
        known_exploits_pattern = r'(/etc/passwd|/bin/bash|/bin/sh|\.\.\/\.\./|\.php\?id=)'

        batch_size = 100
        packet_batches = [raw_packets[i:i + batch_size] for i in range(0, len(raw_packets), batch_size)]

        with ProcessPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(
                process_packet_batch,
                packet_batches,
                [str(local_network)] * len(packet_batches),
                [password_regex_pattern] * len(packet_batches),
                [credit_card_regex_pattern] * len(packet_batches),
                [command_regex_pattern] * len(packet_batches),
                [malware_signatures_pattern] * len(packet_batches),
                [known_exploits_pattern] * len(packet_batches)
            ))

        for result in results:
            for activity_type, *params in result['suspicious_activities']:
                resolved_params = [resolve_ip(param) if isinstance(param, str) and re.match(r'\d+\.\d+\.\d+\.\d+', param) else param for param in params]
                suspicious_activities.append((activity_type, *resolved_params))

            for port, connections in result['inbound_connections'].items():
                inbound_connections[port].update(connections)

            for src_ip, queries in result['dns_queries'].items():
                dns_queries[src_ip].update(queries)

            for src_ip, ports in result['port_scans'].items():
                port_scans[src_ip].update(ports)

        for port, connections in inbound_connections.items():
            total_attempts = sum(connections.values())
            if total_attempts > 10 and port < 1024:
                top_source = max(connections, key=connections.get)
                suspicious_activities.append(('High volume of inbound connections to privileged port', port, total_attempts, f"Top source: {resolve_ip(top_source)}"))

        for src_ip, ports in port_scans.items():
            if len(ports) > port_scan_threshold:
                suspicious_activities.append(('Potential port scan attempt', resolve_ip(src_ip), f"Ports scanned: {len(ports)}"))

        for ip, queries in dns_queries.items():
            if len(queries) > dns_query_threshold:
                suspicious_activities.append(('High volume of unique DNS queries', resolve_ip(ip), f"Unique queries: {len(queries)}"))

        # Remove duplicates
        unique_suspicious_activities = list(set(suspicious_activities))

    except Exception as e:
        logger.error(f"Error during traffic analysis: {str(e)}")
        unique_suspicious_activities = []

    return unique_suspicious_activities



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

def main():
    # Setup the logger and log listener to handle logging messages in a queue
    logger, log_listener = setup_logging_queue()
    log_listener.start()  # Start the log listener to listen for log messages
    try:
        # Define parameters directly in the script for monitoring
        PORT_SCAN_THRESHOLD = 20  # Define the threshold for detecting port scans
        DNS_QUERY_THRESHOLD = 50  # Define the threshold for excessive DNS queries
        count = 1000  # Total number of packets to capture in each iteration
        
        interfaces = get_interfaces()  # Retrieve active network interfaces
        if not interfaces:  # Check if no interfaces were found
            logger.info("No active network interfaces found. Exiting.")
            return  # Exit if no valid interfaces are available
        
        # Prompt user to choose a network interface for packet capture
        interface, local_ip, subnet_mask = choose_interface(interfaces, logger)
        if not interface:  # Check if no interface was selected
            logger.info("No interface selected. Exiting.")
            return  # Exit if no interface is chosen
        logger.info(f"Using network interface: {get_display(interface)} with IP: {local_ip}")  # Log the chosen interface information
        
        log_file = 'security_log.txt'  # Define the log file for suspicious activity logs
        
        while True:  # Continuous loop to capture packets and analyze
            packets = capture_packets(interface, count, logger)  # Capture packets on the selected interface
            suspicious_activities = analyze_traffic(packets, logger, PORT_SCAN_THRESHOLD, DNS_QUERY_THRESHOLD, local_ip, subnet_mask)# Analyze the captured packets
            if suspicious_activities:  # Check if any suspicious activities were detected
                logger.info("Suspicious activities detected!")  # Log that suspicious activities were found
                log_suspicious_activities(log_file, suspicious_activities, logger)  # Log the suspicious activities to the file
                for activity in suspicious_activities:  # Iterate through the suspicious activities
                    logger.info(f"- {': '.join(map(str, activity))}")  # Log each activity in detail
            else:
                logger.info("No suspicious activities detected in this batch.")  # Log that there were no suspicious activities
            
            time.sleep(60)  # Wait for 60 seconds before the next iteration
    except KeyboardInterrupt:  # Handle keyboard interrupt to stop the loop gracefully
        logger.info("\nStopping packet capture. Exiting.")  # Log the stopping of packet capture
    except Exception as e:  # Catch any other exceptions that occur
        logger.error(f"An error occurred: {e}", exc_info=True)  # Log the error with traceback information
    finally:
        log_listener.stop()  # Stop the log listener when done

# Entry point of the script
if __name__ == "__main__":
    main()  # Call the main function to start execution
