import warnings
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
import newrelic.agent
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings("ignore", category=DeprecationWarning, module="cryptography")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {}

config = load_config('config.json')

if 'NEW_RELIC_CONFIG_FILE' in os.environ:
    newrelic.agent.initialize(os.environ['NEW_RELIC_CONFIG_FILE'])
    class NewRelicLogHandler(logging.Handler):
        def emit(self, record):
            newrelic.agent.record_custom_event('Log', {
                'level': record.levelname,
                'message': record.getMessage(),
                'filename': record.filename,
                'lineno': record.lineno
            })
    
    if not any(isinstance(h, NewRelicLogHandler) for h in logger.handlers):
        logger.addHandler(NewRelicLogHandler())
    
    logger.info("New Relic initialized successfully")
else:
    logger.info("NEW_RELIC_CONFIG_FILE not set. New Relic will not be initialized.")

MALICIOUS_IPS = set(config.get('malicious_ips', []))
MONITORED_EXTENSIONS = set(config.get('monitored_extensions', []))
PORT_SCAN_THRESHOLD = config.get('port_scan_threshold', 10)
DNS_QUERY_THRESHOLD = config.get('dns_query_threshold', 50)

def get_interfaces():
    return [(iface, addr.address) for iface, addrs in psutil.net_if_addrs().items() 
            for addr in addrs if addr.family == socket.AF_INET and not addr.address.startswith('169.254.') and addr.address != '127.0.0.1']

def choose_interface(interfaces):
    if not interfaces:
        logger.info("No active network interfaces found. Exiting.")
        return None
    logger.info("Available active interfaces:")
    for i, (iface, ip) in enumerate(interfaces):
        logger.info(f"{i}: {get_display(iface)} (IP: {ip})")
    while True:
        try:
            choice = int(input("Enter the number of the interface to use: "))
            return interfaces[choice][0] if 0 <= choice < len(interfaces) else None
        except ValueError:
            logger.info("Invalid choice. Please try again.")

def capture_packets(interface, count=1000):
    logger.info(f"Capturing {count} packets on {interface}...")
    try:
        return scapy.sniff(iface=interface, count=count)
    except Exception as e:
        logger.error(f"Error capturing packets: {e}")
        return []

def resolve_ip(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.timeout):
        return ip

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

def analyze_traffic(packets):
    suspicious_activities = []
    inbound_connections = defaultdict(lambda: defaultdict(int))
    outbound_connections = deque(maxlen=10000)
    dns_queries = defaultdict(set)
    port_scans = defaultdict(set)
    current_time = time.time()

    local_ip = packets[0][scapy.IP].src if packets and packets[0].haslayer(scapy.IP) else None
    password_regex = re.compile(r'password=\S+', re.IGNORECASE)
    credit_card_regex = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')

    with ThreadPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(lambda pkt: analyze_packet(pkt, local_ip, current_time, password_regex, credit_card_regex), packets))

    for result in results:
        if result:
            activity_type = result[0]
            if activity_type in ['Potential password transmission', 'Potential credit card transmission']:
                suspicious_activities.append(result)
            elif activity_type == 'Outbound connection':
                outbound_connections.append(result[1:])
            elif activity_type == 'Inbound connection':
                dst_port, src_ip = result[1:]
                inbound_connections[dst_port][src_ip] += 1
                port_scans[src_ip].add(dst_port)
            elif activity_type == 'DNS query':
                src_ip, query = result[1:]
                dns_queries[src_ip].add(query)

    outbound_connections = deque((conn for conn in outbound_connections if current_time - conn[3] < 60), maxlen=10000)

    for port, connections in inbound_connections.items():
        total_attempts = sum(connections.values())
        if total_attempts > 0 and port < 1024:
            suspicious_activities.append(('Unsolicited inbound connection attempt', port, total_attempts, f"Sources: {', '.join(map(resolve_ip, connections.keys()))}"))

    for src_ip, ports in port_scans.items():
        if len(ports) > PORT_SCAN_THRESHOLD:
            suspicious_activities.append(('Potential port scan (lateral movement attempt)', src_ip, f"Scanned ports: {', '.join(map(str, ports))}"))

    for ip, queries in dns_queries.items():
        if len(queries) > DNS_QUERY_THRESHOLD:
            suspicious_activities.append(('Excessive DNS queries (potential discovery activity)', ip, f"Number of unique queries: {len(queries)}"))

    return suspicious_activities

def log_suspicious_activities(log_file, data):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a', encoding='utf-8') as f:
        for item in data:
            log_message = f"{timestamp} - {': '.join(map(str, item))}"
            f.write(log_message + "\n")
            logger.warning(log_message)
        f.flush()
        os.fsync(f.fileno())
def main():
    interfaces = get_interfaces()
    if not interfaces:
        logger.info("No active network interfaces found. Exiting.")
        return

    interface = choose_interface(interfaces)
    if not interface:
        logger.info("No interface selected. Exiting.")
        return
    
    logger.info(f"Using network interface: {get_display(interface)}")
    log_file = 'security_log.txt'
    
    try:
        while True:
            packets = capture_packets(interface)
            suspicious_activities = analyze_traffic(packets)
            
            if suspicious_activities:
                logger.info("Suspicious activities detected!")
                log_suspicious_activities(log_file, suspicious_activities)
                for activity in suspicious_activities:
                    logger.info(f"- {': '.join(map(str, activity))}")
            else:
                logger.info("No suspicious activities detected in this batch.")
            
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("\nStopping packet capture. Exiting.")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    if 'NEW_RELIC_CONFIG_FILE' in os.environ:
        newrelic.agent.register_application(timeout=10.0)
    main()