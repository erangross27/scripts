import numpy as np
from feature_extractor import FeatureExtractor

class AnomalyDetector:
    def __init__(self, logger):
        self.logger = logger
        self.feature_extractor = FeatureExtractor()

    def analyze_traffic(self, raw_packets, persistent_detector):
        """Analyze traffic for anomalies using machine learning."""
        try:
            # Extract features from packets
            features = self.feature_extractor.extract_features(raw_packets)
            if not features:
                return [], []

            # Get predictions from the model
            anomaly_scores = -persistent_detector.model.score_samples(features)
            threshold = np.percentile(anomaly_scores, 99)
            anomalies = anomaly_scores > threshold

            # Generate detailed information about detected anomalies 
            anomaly_details = self._generate_anomaly_details(
                raw_packets, anomalies, anomaly_scores
            )

            anomaly_count = np.sum(anomalies)
            self.logger.info(
                f"ML model detected {anomaly_count} anomalies "
                f"out of {len(raw_packets)} packets"
            )

            return anomalies, anomaly_details

        except Exception as e:
            self.logger.error(f"Error in anomaly detection: {e}", exc_info=True)
            return [], []

    def _generate_anomaly_details(self, raw_packets, anomalies, scores):
        """Generate detailed information about detected anomalies."""
        anomaly_details = []
        
        for i, (is_anomaly, score, packet) in enumerate(zip(anomalies, scores, raw_packets)):
            if is_anomaly:
                if isinstance(packet, tuple):
                    packet = packet[1]
                
                packet_summary = packet.summary()
                packet_type = "Unknown"
                protocol = packet.lastlayer().name

                if hasattr(packet, 'type'):
                    if packet.type == 0x0800:
                        packet_type = "IPv4"
                    elif packet.type == 0x86DD:
                        packet_type = "IPv6"
                    elif packet.type == 0x0806:
                        packet_type = "ARP"

                detail = (
                    f"Anomaly at packet {i}: {packet_summary} | "
                    f"Type: {packet_type} | Protocol: {protocol} | "
                    f"Score: {score:.2f}"
                )
                anomaly_details.append(detail)

        return anomaly_details
