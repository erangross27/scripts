import numpy as np
from feature_extractor import FeatureExtractor

class AnomalyDetector:
    """A class for detecting network traffic anomalies using machine learning."""
    
    def __init__(self, logger):
        """
        Initialize the AnomalyDetector with a logger.
        
        Args:
            logger: Logger object for recording detection events and errors
        """
        self.logger = logger
        self.feature_extractor = FeatureExtractor()

    def analyze_traffic(self, raw_packets, persistent_detector):
        """
        Analyze network traffic for anomalies using machine learning.
        
        Args:
            raw_packets: List of network packets to analyze
            persistent_detector: Object containing the trained ML model
            
        Returns:
            tuple: (anomalies, anomaly_details) where anomalies is a boolean array
                  and anomaly_details is a list of strings describing the anomalies
        """
        try:
            # Extract features from packets using the feature extractor
            features = self.feature_extractor.extract_features(raw_packets)
            if not features:
                return [], []

            # Calculate anomaly scores using the model's negative log-likelihood
            anomaly_scores = -persistent_detector.model.score_samples(features)
            # Set threshold at 99th percentile of scores
            threshold = np.percentile(anomaly_scores, 99)
            # Flag packets with scores above threshold as anomalies
            anomalies = anomaly_scores > threshold

            # Generate detailed descriptions for each anomalous packet
            anomaly_details = self._generate_anomaly_details(
                raw_packets, anomalies, anomaly_scores
            )

            # Log the detection results
            anomaly_count = np.sum(anomalies)
            self.logger.info(
                f"ML model detected {anomaly_count} anomalies "
                f"out of {len(raw_packets)} packets"
            )

            return anomalies, anomaly_details

        except Exception as e:
            # Log any errors that occur during analysis
            self.logger.error(f"Error in anomaly detection: {e}", exc_info=True)
            return [], []

    def _generate_anomaly_details(self, raw_packets, anomalies, scores):
        """
        Generate detailed information about detected anomalies.
        
        Args:
            raw_packets: List of original network packets
            anomalies: Boolean array indicating which packets are anomalous
            scores: Array of anomaly scores for each packet
            
        Returns:
            list: Detailed descriptions of each anomalous packet
        """
        anomaly_details = []
        
        # Iterate through all packets and generate details for anomalous ones
        for i, (is_anomaly, score, packet) in enumerate(zip(anomalies, scores, raw_packets)):
            if is_anomaly:
                # Handle packets that come as tuples (sometimes from packet capture)
                if isinstance(packet, tuple):
                    packet = packet[1]
                
                # Extract basic packet information
                packet_summary = packet.summary()
                packet_type = "Unknown"
                protocol = packet.lastlayer().name

                # Determine packet type based on its type attribute
                if hasattr(packet, 'type'):
                    if packet.type == 0x0800:
                        packet_type = "IPv4"
                    elif packet.type == 0x86DD:
                        packet_type = "IPv6"
                    elif packet.type == 0x0806:
                        packet_type = "ARP"

                # Format the anomaly details string
                detail = (
                    f"Anomaly at packet {i}: {packet_summary} | "
                    f"Type: {packet_type} | Protocol: {protocol} | "
                    f"Score: {score:.2f}"
                )
                anomaly_details.append(detail)

        return anomaly_details
