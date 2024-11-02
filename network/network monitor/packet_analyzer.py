from collections import defaultdict
import ipaddress
import re
import time
from scapy.all import Ether, Raw
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6
from scapy.layers.dns import DNS, DNSQR

class PacketAnalyzer:
    def __init__(self, logger):
        self.logger = logger
        self.whitelist_patterns = [
            r'(?i)User-Agent:',
            r'(?i)Accept:',
            r'(?i)Host:',
            r'(?i)Connection:',
            r'(?i)Content-Type:',
            r'GET /|POST /',
            r'(?i)Content-Length:',
            r'(?i)Cache-Control:',
            r'(?i)X-Requested-With:',
        ]
        
        self.threat_patterns = {
            # Command injection patterns with Hebrew support
            r'(?i)(;|\||\`)\s*(cat|pwd|ls|wget|curl|bash|sh|sudo|צו|פקודה|הרץ)\s': 'Command injection attempt',
            
            # SQL injection patterns
            r'(?i)(UNION\s+SELECT|INSERT\s+INTO|UPDATE\s+.*SET|DELETE\s+FROM)\s+[\w_]+': 'SQL injection attempt',
            r'(?i)(DROP\s+TABLE|ALTER\s+TABLE|CREATE\s+TABLE)\s+[\w_]+': 'Database modification attempt',
            
            # XSS patterns
            r'(?i)(<script>|javascript:|\balert\s*\(|document\.cookie)': 'Cross-site scripting attempt',
            
            # Path traversal - modified to reduce false positives
            r'(?i)(\.\./|\.\\/|~/)(etc|bin|usr|root|system32|windows)': 'Path traversal attempt',
            
            # Common malware patterns
            r'(?i)(eval\(|base64_decode\(|system\(|exec\(|shell_exec\()': 'Code execution attempt',
            
            # Data exfiltration patterns with Hebrew support
            r'(?i)(סיסמה|משתמש|כניסה|התחברות|שם|מייל)=': 'Hebrew credential exposure',
            r'(?i)(password=|passwd=|pwd=|user=|username=|login=)': 'Credential exposure',
            r'\b\d{16}\b': 'Potential credit card number',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': 'Email address exposure'
        }

    def _is_binary_or_encrypted(self, data):
        """Check if the data appears to be binary or encrypted."""
        try:
            # Calculate ratio of printable characters
            printable_count = sum(1 for c in data if c.isprintable() or c.isspace())
            ratio = printable_count / len(data)
            
            # If less than 30% printable characters, likely binary/encrypted
            if ratio < 0.30:
                return True
                
            # Check for high entropy (randomness)
            char_freq = defaultdict(int)
            for c in data:
                char_freq[c] += 1
            entropy = sum(-freq/len(data) * len(data)/freq for freq in char_freq.values())
            
            return entropy > 5.0  # High entropy threshold
            
        except Exception:
            return True

    def _decode_payload(self, raw_data):
        """Try multiple encodings to decode the payload."""
        encodings = [
            'utf-8',
            'cp1255',  # Windows Hebrew
            'iso-8859-8',  # Hebrew
            'hebrew',
            'windows-1255',
            'ascii'
        ]
        
        for encoding in encodings:
            try:
                decoded = raw_data.decode(encoding)
                if not self._is_binary_or_encrypted(decoded):
                    return decoded, encoding
            except Exception:
                continue
                
        return None, None

    def analyze_traffic(self, raw_packets, port_scan_threshold, dns_query_threshold, local_ip, subnet_mask):
        """Analyze network traffic for suspicious activities."""
        suspicious_activities = []
        inbound_connections = defaultdict(lambda: defaultdict(int))
        dns_queries = defaultdict(set)
        port_scans = defaultdict(set)
        
        try:
            local_network = ipaddress.ip_network(f"{local_ip}/{subnet_mask}", strict=False)
            self.logger.debug(f"Starting analysis of {len(raw_packets)} packets for network: {local_network}")
            
            packet_types = defaultdict(int)
            protocols = defaultdict(int)
            
            for packet_data in raw_packets:
                try:
                    if isinstance(packet_data, tuple):
                        packet = Ether(packet_data[1])
                        
                        if IP in packet:
                            packet_types['IPv4'] += 1
                            protocols[packet[IP].proto] += 1
                        elif IPv6 in packet:
                            packet_types['IPv6'] += 1
                        if TCP in packet:
                            packet_types['TCP'] += 1
                        if UDP in packet:
                            packet_types['UDP'] += 1
                        if DNS in packet:
                            packet_types['DNS'] += 1
                            
                except Exception as e:
                    self.logger.debug(f"Error processing packet: {e}")
                    continue

            self.logger.info("Packet Statistics:")
            for ptype, count in packet_types.items():
                self.logger.info(f"- {ptype}: {count} packets")
            
            self.logger.info("Protocol Statistics:")
            for proto, count in protocols.items():
                protocol_name = {6: "TCP", 17: "UDP", 1: "ICMP"}.get(proto, f"Protocol {proto}")
                self.logger.info(f"- {protocol_name}: {count} packets")

            self._analyze_packets(
                raw_packets,
                local_network,
                inbound_connections,
                dns_queries,
                port_scans,
                suspicious_activities
            )

        except Exception as e:
            self.logger.error(f"Error during traffic analysis: {e}", exc_info=True)

        return suspicious_activities

    def _analyze_packets(self, raw_packets, local_network, inbound_connections, 
                        dns_queries, port_scans, suspicious_activities):
        """Analyze individual packets for suspicious behavior."""
        time_window = defaultdict(list)
        current_time = time.time()
        
        connection_stats = {
            'total_analyzed': 0,
            'inbound': 0,
            'outbound': 0,
            'local': 0
        }

        for packet_data in raw_packets:
            try:
                if isinstance(packet_data, tuple):
                    packet = Ether(packet_data[1])
                    connection_stats['total_analyzed'] += 1

                    if IP in packet:
                        src_ip = packet[IP].src
                        dst_ip = packet[IP].dst
                        src_ip_obj = ipaddress.ip_address(src_ip)
                        dst_ip_obj = ipaddress.ip_address(dst_ip)

                        is_inbound = dst_ip_obj in local_network and src_ip_obj not in local_network
                        is_outbound = src_ip_obj in local_network and dst_ip_obj not in local_network
                        is_local = src_ip_obj in local_network and dst_ip_obj in local_network

                        if is_inbound:
                            connection_stats['inbound'] += 1
                            
                            if TCP in packet:
                                dst_port = packet[TCP].dport
                                src_port = packet[TCP].sport
                                inbound_connections[dst_port][src_ip] += 1
                                port_scans[src_ip].add(dst_port)
                                
                                self.logger.debug(f"Inbound TCP: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
                                
                                if packet[TCP].flags & 0x02:
                                    time_window[f"{src_ip}:{dst_port}"].append(current_time)
                                    recent_syns = [t for t in time_window[f"{src_ip}:{dst_port}"] 
                                                 if t > current_time - 60]
                                    if len(recent_syns) > 50:
                                        suspicious_activities.append(
                                            ('Potential SYN flood detected', src_ip, dst_ip, dst_port)
                                        )
                            
                            elif UDP in packet:
                                dst_port = packet[UDP].dport
                                src_port = packet[UDP].sport
                                inbound_connections[dst_port][src_ip] += 1
                                port_scans[src_ip].add(dst_port)
                                self.logger.debug(f"Inbound UDP: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")

                        elif is_outbound:
                            connection_stats['outbound'] += 1
                        elif is_local:
                            connection_stats['local'] += 1

                        if DNS in packet and packet.haslayer(DNSQR):
                            query = packet[DNSQR].qname.decode('utf-8', errors='ignore')
                            dns_queries[src_ip].add(query)
                            self.logger.debug(f"DNS Query from {src_ip}: {query}")

                        if Raw in packet and not self._is_whitelisted(packet):
                            try:
                                raw_data = packet[Raw].load
                                decoded_payload, encoding = self._decode_payload(raw_data)
                                
                                if decoded_payload and not self._is_binary_or_encrypted(decoded_payload):
                                    threats = self._check_payload_for_threats(decoded_payload)
                                    for threat_type, context in threats:
                                        # Only log if we have meaningful context
                                        if not self._is_binary_or_encrypted(context):
                                            suspicious_activities.append(
                                                ('Suspicious payload detected', 
                                                 src_ip, 
                                                 dst_ip, 
                                                 threat_type,
                                                 f"Context ({encoding}): {context[:100]}...")
                                            )
                            except Exception as e:
                                self.logger.debug(f"Error processing payload: {e}")

            except Exception as e:
                self.logger.debug(f"Error analyzing packet: {e}")
                continue

        self.logger.info("\nConnection Statistics:")
        self.logger.info(f"Total packets analyzed: {connection_stats['total_analyzed']}")
        self.logger.info(f"Inbound connections: {connection_stats['inbound']}")
        self.logger.info(f"Outbound connections: {connection_stats['outbound']}")
        self.logger.info(f"Local network traffic: {connection_stats['local']}")
        
        if inbound_connections:
            self.logger.info("\nMost active destination ports:")
            port_activity = [(port, sum(connections.values())) 
                           for port, connections in inbound_connections.items()]
            port_activity.sort(key=lambda x: x[1], reverse=True)
            for port, count in port_activity[:5]:
                self.logger.info(f"Port {port}: {count} connections")

        if port_scans:
            self.logger.info("\nMost active source IPs:")
            ip_activity = [(ip, len(ports)) for ip, ports in port_scans.items()]
            ip_activity.sort(key=lambda x: x[1], reverse=True)
            for ip, port_count in ip_activity[:5]:
                self.logger.info(f"IP {ip}: accessed {port_count} unique ports")

    def _check_payload_for_threats(self, payload):
        """Check packet payload for potential threats with context."""
        if self._is_binary_or_encrypted(payload):
            return []

        detected_threats = []
        for pattern, description in self.threat_patterns.items():
            if re.search(pattern, payload):
                matches = re.finditer(pattern, payload)
                for match in matches:
                    start = max(0, match.start() - 20)
                    end = min(len(payload), match.end() + 20)
                    context = payload[start:end].strip()
                    if not self._is_binary_or_encrypted(context):
                        detected_threats.append((description, context))
        return detected_threats

    def _is_whitelisted(self, packet):
        """Check if packet matches any whitelist patterns."""
        if Raw in packet:
            try:
                raw_data = packet[Raw].load
                decoded_payload, _ = self._decode_payload(raw_data)
                
                if decoded_payload:
                    if self._is_binary_or_encrypted(decoded_payload):
                        return True
                        
                    return any(re.search(pattern, decoded_payload) for pattern in self.whitelist_patterns)
            except:
                return True
        return False
