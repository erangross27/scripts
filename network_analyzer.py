import sys
import os
import time
import psutil
import socket
import re
import logging
from collections import defaultdict, deque, Counter
from threading import Thread, Event
from queue import Queue

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
                             QLabel, QComboBox, QFrame, QSplitter, QStyleFactory, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import QThread, pyqtSignal, Qt,QTimer
from PyQt5.QtGui import QFont

import scapy.all as scapy
from scapy.layers import http, dns

# Suppress warnings
import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning, module="cryptography")
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
os.environ['SCAPY_MANUF'] = ''

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Constants
MALICIOUS_IPS = {'192.168.1.100', '10.0.0.50'}
MONITORED_EXTENSIONS = {'.exe', '.dll', '.bat', '.sh', '.py'}

class NetworkAnalyzer(QThread):
    update_signal = pyqtSignal(dict)
    stopped_signal = pyqtSignal()

    def __init__(self, interface):
        super().__init__()
        self.interface = interface
        self.stop_event = Event()
        self.packet_queue = Queue()
        self.ssl_connections = defaultdict(lambda: defaultdict(Counter))
        self.last_reported_activities = set()

    def run(self):
        self.update_signal.emit({"message": "Starting network analysis..."})
        sniffer = Thread(target=self.capture_packets)
        sniffer.start()

        while not self.stop_event.is_set():
            try:
                time.sleep(10)  # Wait for 10 seconds before processing
                packets = []
                while not self.packet_queue.empty() and not self.stop_event.is_set():
                    packets.append(self.packet_queue.get_nowait())
                
                if packets and not self.stop_event.is_set():
                    suspicious_activities = self.analyze_traffic(packets)
                    new_activities = [
                        activity for activity in suspicious_activities
                        if self.activity_to_string(activity) not in self.last_reported_activities
                    ]
                    
                    if new_activities:
                        for activity in new_activities:
                            self.update_signal.emit({"type": "activity", "data": activity})
                            self.last_reported_activities.add(self.activity_to_string(activity))
                    else:
                        self.update_signal.emit({"message": "No new suspicious activities detected."})
                    
                    # Limit the size of last_reported_activities to prevent unbounded growth
                    if len(self.last_reported_activities) > 1000:
                        self.last_reported_activities = set(list(self.last_reported_activities)[-1000:])
            except Exception as e:
                self.update_signal.emit({"message": f"Error in network analysis: {str(e)}"})

        # Clear the queue
        while not self.packet_queue.empty():
            try:
                self.packet_queue.get_nowait()
            except Queue.Empty:
                pass

        sniffer.join(timeout=1)  # Wait for sniffer to finish, but with a timeout
        self.update_signal.emit({"message": "Network analysis stopped."})
        self.stopped_signal.emit()

    def capture_packets(self):
        scapy.sniff(iface=self.interface, prn=self.process_packet, stop_filter=lambda _: self.stop_event.is_set())

    def process_packet(self, packet):
        if not self.stop_event.is_set():
            self.packet_queue.put(packet)

    def stop(self):
        self.stop_event.set()

    def is_stopped(self):
        return self.stop_event.is_set()

    def activity_to_string(self, activity):
        return f"{activity['type']}:{activity.get('source_ip', '')}:{activity.get('destination_ip', '')}"
    
    def capture_packets(self):
        scapy.sniff(iface=self.interface, prn=self.process_packet, stop_filter=lambda _: self.stop_event.is_set())

    def process_packet(self, packet):
        self.packet_queue.put(packet)

    def analyze_traffic(self, packets):
        suspicious_activities = []
        inbound_connections = defaultdict(lambda: defaultdict(int))
        outbound_connections = deque(maxlen=10000)
        data_transfer = defaultdict(int)
        dns_queries = defaultdict(set)
        port_scans = defaultdict(set)
        http_requests = defaultdict(list)
        current_time = time.time()
        local_ip = None

        password_regex = re.compile(r'password=\S+', re.IGNORECASE)
        credit_card_regex = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
        
        for packet in packets:
            if packet.haslayer(scapy.IP):
                src_ip = packet[scapy.IP].src
                dst_ip = packet[scapy.IP].dst

                if local_ip is None and packet.sniffed_on:
                    local_ip = next((addr.address for addr in psutil.net_if_addrs()[packet.sniffed_on]
                                     if addr.family == socket.AF_INET), None)

                data_transfer[src_ip] += len(packet)

                if packet.haslayer(scapy.TCP):
                    src_port = packet[scapy.TCP].sport
                    dst_port = packet[scapy.TCP].dport

                    if packet.haslayer(http.HTTPRequest):
                        payload = str(packet[http.HTTPRequest].fields)
                        if password_regex.search(payload):
                            suspicious_activities.append({
                                'type': 'Potential password transmission',
                                'source_ip': src_ip,
                                'destination_ip': dst_ip
                            })
                        if credit_card_regex.search(payload):
                            suspicious_activities.append({
                                'type': 'Potential credit card transmission',
                                'source_ip': src_ip,
                                'destination_ip': dst_ip
                            })
                        http_requests[src_ip].append((dst_ip, dst_port))

                    if src_ip == local_ip and packet[scapy.TCP].flags & 0x02:
                        outbound_connections.append((dst_ip, dst_port, src_port, current_time))
                    elif dst_ip == local_ip and packet[scapy.TCP].flags & 0x02:
                        inbound_connections[dst_port][src_ip] += 1
                        port_scans[src_ip].add(dst_port)

                    if dst_port == 443:
                        self.ssl_connections[src_ip][dst_ip][dst_port] += 1

                if packet.haslayer(dns.DNSQR):
                    query = packet[dns.DNSQR].qname.decode('utf-8')
                    dns_queries[src_ip].add(query)

        outbound_connections = deque((conn for conn in outbound_connections if current_time - conn[3] < 60), maxlen=10000)

        for port, connections in inbound_connections.items():
            total_attempts = sum(connections.values())
            if total_attempts > 0 and port < 1024:
                suspicious_activities.append({
                    'type': 'Unsolicited inbound connection attempt',
                    'port': port,
                    'total_attempts': total_attempts,
                    'sources': [self.resolve_ip(ip) for ip in connections.keys()]
                })

        for src_ip, ports in port_scans.items():
            if len(ports) > 10:
                suspicious_activities.append({
                    'type': 'Potential port scan (lateral movement attempt)',
                    'source_ip': src_ip,
                    'scanned_ports': list(ports)
                })

        for ip, amount in data_transfer.items():
            if amount > 10000000:
                suspicious_activities.append({
                    'type': 'Large data transfer (potential exfiltration)',
                    'source_ip': ip,
                    'amount': f"{amount/1000000:.2f} MB"
                })

        for ip, queries in dns_queries.items():
            if len(queries) > 50:
                suspicious_activities.append({
                    'type': 'Excessive DNS queries (potential discovery activity)',
                    'source_ip': ip,
                    'query_count': len(queries)
                })

        for ip, requests in http_requests.items():
            if len(requests) > 100:
                suspicious_activities.append({
                    'type': 'High number of HTTP requests',
                    'source_ip': ip,
                    'request_count': len(requests)
                })

        for src_ip, destinations in self.ssl_connections.items():
            total_connections = sum(sum(conns.values()) for conns in destinations.values())
            if total_connections > 50:
                details = {dst_ip: dict(conns) for dst_ip, conns in destinations.items()}
                suspicious_activities.append({
                    'type': 'High number of SSL connections',
                    'source_ip': src_ip,
                    'total_connections': total_connections,
                    'details': details
                })

        return suspicious_activities

    def resolve_ip(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.timeout):
            return ip

    def stop(self):
        self.stop_event.set()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Security Analyzer")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel, QPushButton, QComboBox, QTreeWidget {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QComboBox {
                background-color: #3d3d3d;
                border: 1px solid #5d5d5d;
                padding: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #5d5d5d;
                border-left-style: solid;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: #ffffff;
                selection-background-color: #3d3d3d;
            }
            QTreeWidget {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
            }
            QTreeWidget::item {
                color: #ffffff;
            }
            QTreeWidget::item:selected {
                background-color: #3d3d3d;
            }
        """)

        self.create_layout()

        self.analyzer = None

        self.stop_check_timer = QTimer()
        self.stop_check_timer.timeout.connect(self.check_analyzer_stopped)
        self.stop_check_timer.setInterval(100)  # Check every 100ms


    def create_layout(self):
        main_layout = QHBoxLayout()

        # Left sidebar
        left_sidebar = QFrame()
        left_sidebar.setFrameShape(QFrame.StyledPanel)
        left_sidebar_layout = QVBoxLayout(left_sidebar)

        interface_label = QLabel("Network Interface:")
        interface_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_sidebar_layout.addWidget(interface_label)

        self.interface_combo = QComboBox()
        self.interface_combo.setFont(QFont("Arial", 10))
        interfaces = self.get_interfaces()
        self.interface_combo.addItems([f"{iface} ({ip})" for iface, ip in interfaces])
        self.interface_combo.currentIndexChanged.connect(self.select_interface)
        left_sidebar_layout.addWidget(self.interface_combo)

        self.start_button = QPushButton("Start Monitoring")
        self.start_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.start_button.clicked.connect(self.start_monitoring)
        left_sidebar_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        left_sidebar_layout.addWidget(self.stop_button)

        left_sidebar_layout.addStretch()

        # Right content area
        right_content = QFrame()
        right_content.setFrameShape(QFrame.StyledPanel)
        right_content_layout = QVBoxLayout(right_content)

        log_label = QLabel("Activity Log:")
        log_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_content_layout.addWidget(log_label)

        self.log_output = QTreeWidget()
        self.log_output.setHeaderLabels(["Event"])
        self.log_output.setFont(QFont("Courier", 10))
        right_content_layout.addWidget(self.log_output)

        # Add left sidebar and right content to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_sidebar)
        splitter.addWidget(right_content)
        splitter.setSizes([200, 800])

        main_layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Set the default interface
        if interfaces:
            self.selected_interface = interfaces[0][0]
            self.log_output.addTopLevelItem(QTreeWidgetItem([f"Selected interface: {self.selected_interface}"]))
            self.start_button.setEnabled(True)

    def get_interfaces(self):
        interfaces = []
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith('169.254.') and addr.address != '127.0.0.1':
                    interfaces.append((iface, addr.address))
                    break
        return interfaces

    def select_interface(self, index):
        self.selected_interface = self.get_interfaces()[index][0]
        self.log_output.addTopLevelItem(QTreeWidgetItem([f"Selected interface: {self.selected_interface}"]))
        self.start_button.setEnabled(True)

    def start_monitoring(self):
        if self.selected_interface:
            self.analyzer = NetworkAnalyzer(self.selected_interface)
            self.analyzer.update_signal.connect(self.update_log)
            self.analyzer.stopped_signal.connect(self.on_analyzer_stopped)
            self.analyzer.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.interface_combo.setEnabled(False)
        else:
            self.log_output.addTopLevelItem(QTreeWidgetItem(["Please select a network interface first."]))

    def stop_monitoring(self):
        if self.analyzer:
            self.log_output.addTopLevelItem(QTreeWidgetItem(["Stopping network analysis..."]))
            self.analyzer.stop()
            self.stop_check_timer.start()
            self.stop_button.setEnabled(False)
            self.start_button.setEnabled(False)
            self.interface_combo.setEnabled(False)

    def check_analyzer_stopped(self):
        if self.analyzer and self.analyzer.is_stopped():
            self.stop_check_timer.stop()
            self.analyzer.wait(1000)  # Wait for a maximum of 1 second
            self.on_analyzer_stopped()

    def on_analyzer_stopped(self):
        self.analyzer = None
        self.start_button.setEnabled(True)
        self.interface_combo.setEnabled(True)
        self.log_output.addTopLevelItem(QTreeWidgetItem(["Network analysis stopped."]))

    def update_log(self, data):
        if "message" in data:
            item = QTreeWidgetItem([data["message"]])
            self.log_output.addTopLevelItem(item)
        elif "type" in data and data["type"] == "activity":
            activity = data["data"]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            item = QTreeWidgetItem([f"{timestamp} - {activity['type']}: {activity.get('source_ip', 'N/A')}"])
            
            for key, value in activity.items():
                if key not in ['type', 'source_ip']:
                    if isinstance(value, dict):
                        sub_item = QTreeWidgetItem([f"{key}:"])
                        item.addChild(sub_item)
                        for sub_key, sub_value in value.items():
                            sub_item.addChild(QTreeWidgetItem([f"{sub_key}: {sub_value}"]))
                    elif isinstance(value, list):
                        sub_item = QTreeWidgetItem([f"{key}: {', '.join(map(str, value))}"])
                        item.addChild(sub_item)
                    else:
                        item.addChild(QTreeWidgetItem([f"{key}: {value}"]))
            
            self.log_output.addTopLevelItem(item)
            item.setExpanded(True)

        while self.log_output.topLevelItemCount() > 1000:  # Limit to 1000 items
            self.log_output.takeTopLevelItem(0)

        self.log_output.scrollToBottom()

    def closeEvent(self, event):
        if self.analyzer:
            self.analyzer.stop()
            self.analyzer.wait(1000)  # Wait for a maximum of 1 second
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

