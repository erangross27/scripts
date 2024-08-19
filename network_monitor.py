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
import platform
from scapy.all import IP, TCP, UDP, DNS, DNSQR, Raw, scapy
from scapy.layers import http, dns
from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict
from multiprocessing import Queue
from tqdm import tqdm
from bidi.algorithm import get_display
from logging.handlers import QueueHandler, QueueListener

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger

def setup_logging_queue():
    queue = Queue(-1)
    queue_handler = QueueHandler(queue)
    logger = setup_logger()
    logger.addHandler(queue_handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    listener = QueueListener(queue, stream_handler)
    return logger, listener

def get_interfaces():
    return [(iface, addr.address) for iface, addrs in psutil.net_if_addrs().items()
            for addr in addrs if addr.family == socket.AF_INET and not addr.address.startswith('169.254.') and addr.address != '127.0.0.1']

def choose_interface(interfaces, logger):
    if not interfaces:
        logger.info("No active network interfaces found. Exiting.")
        return None, None
    logger.info("Available active interfaces:")
    logger.info("")  # Add an empty line before listing interfaces
    for i, (iface, ip) in enumerate(interfaces):
        logger.info(f"{i}: {get_display(iface)} (IP: {ip})")
    logger.info("")  # Add an empty line after listing interfaces
    while True:
        try:
            choice = int(input("Enter the number of the interface to use: "))
            if 0 <= choice < len(interfaces):
                return interfaces[choice]
            else:
                logger.info("Invalid choice. Please try again.")
        except ValueError:
            logger.info("Invalid input. Please enter a number.")

def capture_packets_worker(interface, count, result_queue, logger):
    try:
        if platform.system() == "Windows":
            from scapy.all import sniff

            logger.info(f"Starting packet capture on interface {interface} using scapy")
            packets = []

            # Define packet handler for scapy
            def packet_handler(pkt):
                packets.append(pkt)
                if len(packets) >= count:
                    raise Exception("Capture complete")

            start_time = time.time()
            try:
                sniff(iface=interface, prn=packet_handler, store=False, timeout=300)
            except Exception as e:
                if "Capture complete" not in str(e):
                    raise e

            logger.info(f"Captured {len(packets)} packets")
            packet_data = [(pkt.time, bytes(pkt)) for pkt in packets]

        elif platform.system() == "Linux":
            import pcap # type: ignore

            cap = pcap.pcap(name=interface, promisc=True, immediate=True, timeout_ms=100)
            logger.info(f"Pcap object created on interface {interface}")
            packets = []
            start_time = time.time()

            for timestamp, packet in cap:
                packets.append((timestamp, packet))
                if len(packets) >= count:
                    break
                # Check for timeout
                if time.time() - start_time > 300:  # 5 minutes timeout
                    logger.warning(f"Timeout reached. Captured {len(packets)} packets in 5 minutes.")
                    break

            packet_data = packets

        result_queue.put(packet_data)
    except Exception as e:
        logger.error(f"Error in capture_packets_worker: {e}", exc_info=True)
        result_queue.put([])

def capture_packets(interface, total_count, logger):
    logger.info(f"Capturing {total_count} packets on {interface} using 8 cores...")
    
    packets_per_worker = total_count // 8
    result_queue = multiprocessing.Queue()
    processes = []
    
    start_time = time.time()  # Define start_time here
    
    for _ in range(8):
        p = multiprocessing.Process(target=capture_packets_worker, args=(interface, packets_per_worker, result_queue, logger))
        processes.append(p)
        p.start()
    
    all_packets = []
    with tqdm(total=total_count, unit='packet', mininterval=0.1) as progress_bar:
        for _ in range(8):
            packets = result_queue.get()
            all_packets.extend(packets)
            progress_bar.update(len(packets))
    
    for p in processes:
        p.join()
    
    duration = time.time() - start_time
    packets_per_second = len(all_packets) / duration if duration > 0 else 0
    logger.info(f"Captured {len(all_packets)} packets in {duration:.2f} seconds ({packets_per_second:.2f} packets/second)")
    
    return all_packets


def analyze_packet(packet, local_ip, current_time, password_regex, credit_card_regex):
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
    return packet[IP].dst.startswith(local_network) and not packet[IP].src.startswith(local_network)

def process_packet_batch(raw_packet_batch, local_network, password_regex_pattern, credit_card_regex_pattern):
    password_regex = re.compile(password_regex_pattern, re.IGNORECASE)
    credit_card_regex = re.compile(credit_card_regex_pattern)
    batch_results = {
        'suspicious_activities': [],
        'inbound_connections': defaultdict(lambda: defaultdict(int)),
        'dns_queries': defaultdict(set),
        'port_scans': defaultdict(set)
    }

    for _, packet_data in raw_packet_batch:
        try:
            packet = IP(packet_data)
        except:
            continue  # Skip packets that can't be parsed as IP

        if is_inbound(packet, local_network):
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            if TCP in packet:
                dst_port = packet[TCP].dport
                batch_results['inbound_connections'][dst_port][src_ip] += 1
                batch_results['port_scans'][src_ip].add(dst_port)

            if Raw in packet:
                payload = str(packet[Raw].load)
                if password_regex.search(payload):
                    batch_results['suspicious_activities'].append(('Potential password transmission', src_ip, dst_ip))
                if credit_card_regex.search(payload):
                    batch_results['suspicious_activities'].append(('Potential credit card transmission', src_ip, dst_ip))
            elif DNS in packet and DNSQR in packet:
                query = packet[DNSQR].qname.decode('utf-8')
                batch_results['dns_queries'][src_ip].add(query)

    return {k: dict(v) if isinstance(v, defaultdict) else v for k, v in batch_results.items()}

def analyze_traffic(raw_packets, logger, port_scan_threshold, dns_query_threshold, local_ip):
    suspicious_activities = []
    inbound_connections = defaultdict(lambda: defaultdict(int))
    dns_queries = defaultdict(set)
    port_scans = defaultdict(set)
    if not local_ip:
        logger.warning("Unable to determine local IP. Analysis may be inaccurate.")
        return suspicious_activities
    # Correct the network calculation
    local_network = '.'.join(local_ip.split('.')[:3]) + '.0'
    logger.info(f"Local IP: {local_ip}")
    logger.info(f"Local network: {local_network}")
    password_regex_pattern = r'password=\S+'
    credit_card_regex_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'

    batch_size = 100
    packet_batches = [raw_packets[i:i+batch_size] for i in range(0, len(raw_packets), batch_size)]

    with ProcessPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(
            process_packet_batch,
            packet_batches,
            [local_network] * len(packet_batches),
            [password_regex_pattern] * len(packet_batches),
            [credit_card_regex_pattern] * len(packet_batches)
        ))

    for result in results:
        suspicious_activities.extend(result['suspicious_activities'])
        for port, connections in result['inbound_connections'].items():
            inbound_connections[port].update(connections)
        for src_ip, queries in result['dns_queries'].items():
            dns_queries[src_ip].update(queries)
        for src_ip, ports in result['port_scans'].items():
            port_scans[src_ip].update(ports)

    for port, connections in inbound_connections.items():
        total_attempts = sum(connections.values())
        if total_attempts > 0 and port < 1024:
            suspicious_activities.append(('Unsolicited inbound connection attempt', port, total_attempts, f"Sources: {', '.join(map(resolve_ip, connections.keys()))}"))

    for src_ip, ports in port_scans.items():
        if len(ports) > port_scan_threshold:
            suspicious_activities.append(('Potential port scan attempt', src_ip, f"Scanned ports: {', '.join(map(str, ports))}"))

    for ip, queries in dns_queries.items():
        if len(queries) > dns_query_threshold:
            suspicious_activities.append(('Excessive inbound DNS queries', ip, f"Number of unique queries: {len(queries)}"))

    return suspicious_activities

# Make sure to define or import the resolve_ip function
def resolve_ip(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.timeout):
        return ip


def log_suspicious_activities(log_file, data, logger):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a', encoding='utf-8') as f:
        for item in data:
            log_message = f"{timestamp} - {': '.join(map(str, item))}"
            f.write(log_message + "\n")
            logger.warning(log_message)
        f.flush()
        os.fsync(f.fileno())

def main():
    logger, log_listener = setup_logging_queue()
    log_listener.start()
    try:
        # Define parameters directly in the script
        MALICIOUS_IPS = set()  # Add any known malicious IPs here
        MONITORED_EXTENSIONS = set(['.exe', '.dll', '.bat'])  # Add file extensions to monitor
        PORT_SCAN_THRESHOLD = 10
        DNS_QUERY_THRESHOLD = 50
        count = 1000  # Total number of packets to capture in each iteration
        
        interfaces = get_interfaces()
        if not interfaces:
            logger.info("No active network interfaces found. Exiting.")
            return
        interface, local_ip = choose_interface(interfaces, logger)
        if not interface:
            logger.info("No interface selected. Exiting.")
            return
        logger.info(f"Using network interface: {get_display(interface)} with IP: {local_ip}")
        
        log_file = 'security_log.txt'
        
        while True:
            packets = capture_packets(interface, count, logger)
            suspicious_activities = analyze_traffic(packets, logger, PORT_SCAN_THRESHOLD, DNS_QUERY_THRESHOLD, local_ip)
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
