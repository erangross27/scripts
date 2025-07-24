"""
This script handles network monitor.
"""

# Import required libraries
import argparse  # For parsing command-line arguments
import sys      # For system-specific parameters and functions
import time     # For time-related functions
import os       # For operating system dependent functionality
import socket   # For resolving IP addresses to hostnames
from collections import defaultdict  # For creating dictionaries with default values
import pandas as pd  # For DataFrame operations
import numpy as np   # For numerical operations

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

# Import custom modules for network monitoring functionality
from logger_setup import LoggerSetup                                    # Module for setting up logging
from interface_manager import InterfaceManager                          # Module for managing network interfaces
from packet_capture import PacketCapture                               # Module for capturing network packets
from packet_analyzer import PacketAnalyzer                             # Module for analyzing network packets
from anomaly_detector import AnomalyDetector                           # Module for detecting network anomalies
from models.persistent_anomaly_detector import PersistentAnomalyDetector  # Module for persistent anomaly detection
from models.deep_packet_analyzer import DeepPacketAnalyzer, SequenceAnomalyDetector  # Deep learning models

class NetworkMonitor:
    """Main class for monitoring network traffic and detecting anomalies"""
    def __init__(self):
        """
        Special method __init__.
        """
        # Initialize components for logging, interface management, packet capture/analysis, and anomaly detection
        self.logger_setup = LoggerSetup()                    # Create logger setup instance
        self.logger = self.logger_setup.get_logger()         # Get logger instance
        self.interface_manager = InterfaceManager(self.logger)    # Initialize interface manager
        self.packet_capture = PacketCapture(self.logger)         # Initialize packet capture
        self.packet_analyzer = PacketAnalyzer(self.logger)       # Initialize packet analyzer
        self.anomaly_detector = AnomalyDetector(self.logger)     # Initialize anomaly detector
        self.persistent_detector = PersistentAnomalyDetector()   # Initialize persistent anomaly detector
        
        # Select the most sophisticated model available
        if DEEP_LEARNING_AVAILABLE:
            model_type = 'deep_nn'
            self.logger.info("Using Deep Neural Network model (most sophisticated)")
        elif NEURAL_NETWORK_AVAILABLE:
            model_type = 'neural_network'
            self.logger.info("Using Neural Network model")
        else:
            model_type = 'random_forest'
            self.logger.info("Using Random Forest model")
            
        self.deep_analyzer = DeepPacketAnalyzer(model_type=model_type)  # Initialize deep analyzer
        self.sequence_analyzer = SequenceAnomalyDetector(sequence_length=5)  # Initialize sequence analyzer

    def check_root_linux(self):
        """Check if script is running with root privileges on Linux systems"""
        # Root privileges are required for packet capture on Linux
        if sys.platform.startswith('linux'):
            if os.geteuid() != 0:
                print("This script requires root privileges to capture network packets on Linux.")
                print("Please run the script with sudo, like this:")
                print("sudo python3 network_monitor.py")
                sys.exit(1)

    def run(self, interface_name=None):
        """Main monitoring loop that captures and analyzes network traffic"""
        try:
            # Define thresholds and configuration parameters for monitoring
            PORT_SCAN_THRESHOLD = 10          # Threshold for detecting port scans
            DNS_QUERY_THRESHOLD = 25          # Threshold for detecting DNS query anomalies
            PACKET_COUNT = 1000               # Number of packets to capture in each batch
            MODEL_UPDATE_INTERVAL = 5         # Frequency of model updates (in iterations)
            
            # Set up network interface and get network details
            interface, local_ip, subnet_mask = self.interface_manager.setup_interface(interface_name)
            if not interface:
                self.logger.error("No valid interface found. Exiting.")
                return

            self.logger.info(f"Monitoring interface: {interface}")

            # Initialize tracking variables for monitoring
            false_positive_count = defaultdict(int)  # Track potential false positives
            iteration_count = 0                      # Count monitoring iterations
            save_interval = 10                       # Interval for saving model state
            collected_features = []                  # Store features for model updates
            collected_labels = []                    # Store labels for deep learning model training
            
            # Try to load existing model or prepare for new model creation
            try:
                self.persistent_detector.load_model()
                self.logger.info("Loaded existing anomaly detection model")
            except Exception as e:
                self.logger.warning(f"Could not load model: {e}. Will create new model after collecting data.")

            # Main monitoring loop
            while True:
                try:
                    # Capture network packets using specified interface
                    packets = self.packet_capture.capture_packets(
                        interface, 
                        PACKET_COUNT
                    )

                    if packets:
                        self.logger.debug(f"Captured {len(packets)} packets")
                        
                        # Analyze captured packets for suspicious behavior
                        try:
                            suspicious_activities = self.packet_analyzer.analyze_traffic(
                                packets,
                                PORT_SCAN_THRESHOLD,
                                DNS_QUERY_THRESHOLD,
                                local_ip,
                                subnet_mask
                            )
                        except Exception as e:
                            self.logger.error(f"Error in packet analysis: {e}", exc_info=True)
                            suspicious_activities = []

                        # Extract features from packets for anomaly detection
                        try:
                            features = self.anomaly_detector.feature_extractor.extract_features(packets)
                            if features is not None and not features.empty:
                                # Convert DataFrame to list for storage if needed
                                if hasattr(features, 'values'):
                                    collected_features.extend(features.values.tolist())
                                else:
                                    collected_features.extend(features)
                                
                                # Generate labels based on suspicious activities detected
                                # In a real implementation, you would have actual labels
                                labels = np.zeros(len(features))
                                if suspicious_activities:
                                    # Mark some samples as potentially anomalous
                                    labels[-min(5, len(labels)):] = 1
                                collected_labels.extend(labels.tolist())
                                
                                # Update model periodically with collected features
                                if iteration_count % MODEL_UPDATE_INTERVAL == 0 and len(collected_features) > 0:
                                    self.logger.info("Updating anomaly detection models...")
                                    
                                    # Prepare features as DataFrame
                                    if not isinstance(features, pd.DataFrame):
                                        features_df = pd.DataFrame(collected_features[-len(features):], 
                                                                 columns=self.anomaly_detector.feature_extractor.feature_names)
                                    else:
                                        features_df = features
                                    
                                    # Update traditional model
                                    self.persistent_detector.partial_fit(features_df)
                                    
                                    # Train deep learning model if we have enough data
                                    if len(collected_features) >= 100:
                                        try:
                                            # Use recent data for training
                                            recent_features = np.array(collected_features[-100:])
                                            recent_labels = np.array(collected_labels[-100:])
                                            self.anomaly_detector.train_deep_analyzer(recent_features, recent_labels)
                                        except Exception as e:
                                            self.logger.debug(f"Could not train deep analyzer: {e}")
                                    
                                    # Only keep recent data to avoid memory issues
                                    if len(collected_features) > 500:
                                        collected_features = collected_features[-500:]
                                        collected_labels = collected_labels[-500:]
                        except Exception as e:
                            self.logger.error(f"Error in feature extraction: {e}", exc_info=True)

                        # Perform anomaly detection on current packets
                        try:
                            anomalies, anomaly_details = self.anomaly_detector.analyze_traffic(
                                packets,
                                self.persistent_detector
                            )
                        except Exception as e:
                            self.logger.error(f"Error in anomaly detection: {e}", exc_info=True)
                            anomalies, anomaly_details = [], []

                        # Log detection results and update false positive tracking
                        try:
                            self._log_results(suspicious_activities, anomaly_details)
                            self._update_false_positives(anomaly_details, false_positive_count)
                        except Exception as e:
                            self.logger.error(f"Error in logging results: {e}", exc_info=True)

                    else:
                        self.logger.warning("No packets captured in this batch.")

                    # Save model state periodically
                    iteration_count += 1
                    if iteration_count % save_interval == 0:
                        try:
                            self.persistent_detector.save_model()
                            self.logger.info("Saved anomaly detection model")
                        except Exception as e:
                            self.logger.error(f"Error saving model: {e}", exc_info=True)

                except Exception as e:
                    self.logger.error(f"Packet processing error: {e}", exc_info=True)

                # Use a more adaptive sleep time
                try:
                    time.sleep(60)
                except Exception as e:
                    self.logger.error(f"Sleep interrupted: {e}")

        except KeyboardInterrupt:
            self.logger.info("\nStopping packet capture. Exiting.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        finally:
            # Ensure model state is saved before exiting
            try:
                if hasattr(self, 'persistent_detector'):
                    self.persistent_detector.save_model()
                    self.logger.info("Saved final model state")
            except Exception as e:
                self.logger.error(f"Error saving final model state: {e}")
            finally:
                try:
                    self.logger_setup.stop_listener()
                except Exception as e:
                    self.logger.error(f"Error stopping logger: {e}")

    def _log_results(self, suspicious_activities, anomaly_details):
        """Log detected suspicious activities and anomalies"""
        # Log suspicious activities if any were detected
        if suspicious_activities:
            self.logger.info("Suspicious activities detected:")
            for activity in suspicious_activities:
                activity_type, ip_address = activity[0], activity[1]
                
                # Try to resolve IP to hostname
                try:
                    hostname = socket.gethostbyaddr(ip_address)[0]
                    # Show both IP and hostname if they're different
                    if hostname != ip_address:
                        self.logger.info(f"- {activity_type}: {ip_address} ({hostname})")
                    else:
                        self.logger.info(f"- {activity_type}: {ip_address}")
                except (socket.herror, socket.timeout):
                    # If we can't resolve, just show the IP
                    self.logger.info(f"- {activity_type}: {ip_address}")
        else:
            self.logger.info("No suspicious activities detected.")

        # Log anomalies, limiting output to first 10 if there are many
        if anomaly_details:
            self.logger.info("Anomalies detected:")
            for detail in anomaly_details[:10]:
                self.logger.info(detail)
            if len(anomaly_details) > 10:
                self.logger.info(f"... and {len(anomaly_details) - 10} more anomalies.")
        else:
            self.logger.info("No anomalies detected.")

    def _update_false_positives(self, anomaly_details, false_positive_count):
        """Track and handle potential false positive detections"""
        # Update counter for each anomaly and handle frequent occurrences
        for detail in anomaly_details:
            false_positive_count[detail] += 1
            if false_positive_count[detail] > 10:
                self.logger.info(f"Adapting to frequent anomaly: {detail}")
                false_positive_count[detail] = 0

def main():
    """Entry point of the script - parse arguments and start monitoring"""
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Network Monitor')
    parser.add_argument('--interface', type=str, help='Network interface to use')
    parser.add_argument('--model-type', type=str, default='auto', 
                        choices=['auto', 'random_forest', 'neural_network', 'deep_nn'],
                        help='Type of model to use for anomaly detection')
    args = parser.parse_args()

    # Create monitor instance and start monitoring
    monitor = NetworkMonitor()
    monitor.check_root_linux()
    monitor.run(args.interface)

if __name__ == "__main__":
    main()