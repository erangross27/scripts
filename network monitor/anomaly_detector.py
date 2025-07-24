"""
This script handles anomaly detector that performs numerical operations.
"""

import numpy as np
from feature_extractor import FeatureExtractor
from models.deep_packet_analyzer import DeepPacketAnalyzer

# Check what ML libraries are available
DEEP_LEARNING_AVAILABLE = False
try:
    import torch
    DEEP_LEARNING_AVAILABLE = True
except ImportError:
    pass

NEURAL_NETWORK_AVAILABLE = False
try:
    from sklearn.neural_network import MLPClassifier
    NEURAL_NETWORK_AVAILABLE = True
except ImportError:
    pass

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
        # Select the most sophisticated model available
        if DEEP_LEARNING_AVAILABLE:
            model_type = 'deep_nn'
            self.logger.info("AnomalyDetector: Using Deep Neural Network model (most sophisticated)")
        elif NEURAL_NETWORK_AVAILABLE:
            model_type = 'neural_network'
            self.logger.info("AnomalyDetector: Using Neural Network model")
        else:
            model_type = 'random_forest'
            self.logger.info("AnomalyDetector: Using Random Forest model")
            
        # Initialize the deep packet analyzer
        self.deep_analyzer = DeepPacketAnalyzer(model_type=model_type)

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
            if features is None or (hasattr(features, 'empty') and features.empty):
                return [], []

            # Try to use the deep analyzer if it's fitted
            if hasattr(self.deep_analyzer, 'is_fitted') and self.deep_analyzer.is_fitted:
                try:
                    # Use the deep analyzer for predictions
                    anomaly_probs = self.deep_analyzer.predict_proba(features)
                    # Use a lower threshold for deep learning model
                    threshold = 0.8
                    anomalies = anomaly_probs[:, 1] > threshold
                    anomaly_scores = anomaly_probs[:, 1]
                except Exception as e:
                    self.logger.debug(f"Deep analyzer failed, falling back to traditional method: {e}")
                    # Fallback to traditional method
                    anomalies, anomaly_scores = self._traditional_analysis(features, persistent_detector)
            else:
                # Use traditional method
                anomalies, anomaly_scores = self._traditional_analysis(features, persistent_detector)

            # Generate detailed descriptions for each anomalous packet
            try:
                anomaly_details = self._generate_anomaly_details(
                    raw_packets, anomalies, anomaly_scores
                )
            except Exception as e:
                self.logger.error(f"Error generating anomaly details: {e}")
                anomaly_details = []

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

    def _traditional_analysis(self, features, persistent_detector):
        """
        Traditional anomaly analysis using the isolation forest model.
        
        Args:
            features: Extracted features from packets
            persistent_detector: The persistent anomaly detector
            
        Returns:
            tuple: (anomalies, scores)
        """
        # Check if the model is fitted before trying to use it
        if not hasattr(persistent_detector, 'is_fitted') or not persistent_detector.is_fitted:
            self.logger.warning("Anomaly detection model is not fitted yet.")
            return np.array([]), np.array([])

        # Calculate anomaly scores using the model's negative log-likelihood
        try:
            anomaly_scores = -persistent_detector.score_samples(features)
        except Exception as e:
            self.logger.error(f"Error calculating anomaly scores: {e}")
            return np.array([]), np.array([])

        # Set threshold at 99th percentile of scores
        try:
            threshold = np.percentile(anomaly_scores, 99)
        except Exception as e:
            self.logger.error(f"Error calculating threshold: {e}")
            return np.array([]), np.array([])

        # Flag packets with scores above threshold as anomalies
        anomalies = anomaly_scores > threshold
        return anomalies, anomaly_scores

    def train_deep_analyzer(self, features, labels):
        """
        Train the deep analyzer with labeled data.
        
        Args:
            features: Feature data for training
            labels: Labels for the data (0 for normal, 1 for anomaly)
        """
        try:
            self.deep_analyzer.fit(features, labels)
            self.logger.info("Deep analyzer trained successfully")
        except Exception as e:
            self.logger.error(f"Error training deep analyzer: {e}")

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
                try:
                    # Handle packets that come as tuples (sometimes from packet capture)
                    if isinstance(packet, tuple):
                        packet = packet[1]
                    
                    # Extract basic packet information
                    try:
                        packet_summary = packet.summary()
                    except:
                        packet_summary = "Unknown packet"
                        
                    packet_type = "Unknown"
                    
                    try:
                        protocol = packet.lastlayer().name
                    except:
                        protocol = "Unknown"

                    # Determine packet type based on its type attribute
                    try:
                        if hasattr(packet, 'type'):
                            if packet.type == 0x0800:
                                packet_type = "IPv4"
                            elif packet.type == 0x86DD:
                                packet_type = "IPv6"
                            elif packet.type == 0x0806:
                                packet_type = "ARP"
                    except:
                        pass

                    # Format the anomaly details string
                    detail = (
                        f"Anomaly at packet {i}: {packet_summary} | "
                        f"Type: {packet_type} | Protocol: {protocol} | "
                        f"Score: {score:.2f}"
                    )
                    anomaly_details.append(detail)
                except Exception as e:
                    self.logger.debug(f"Error processing anomaly details for packet {i}: {e}")

        return anomaly_details