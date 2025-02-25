"""
This script handles network monitor.
"""

# Import required libraries
import argparse  # For parsing command-line arguments
import sys      # For system-specific parameters and functions
import time     # For time-related functions
import os       # For operating system dependent functionality
from collections import defaultdict  # For creating dictionaries with default values
# Import custom modules for network monitoring functionality
from logger_setup import LoggerSetup                                    # Module for setting up logging
from interface_manager import InterfaceManager                          # Module for managing network interfaces
from packet_capture import PacketCapture                               # Module for capturing network packets
from packet_analyzer import PacketAnalyzer                             # Module for analyzing network packets
from anomaly_detector import AnomalyDetector                           # Module for detecting network anomalies
from models.persistent_anomaly_detector import PersistentAnomalyDetector  # Module for persistent anomaly detection
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

            # Initialize tracking variables for monitoring
            false_positive_count = defaultdict(int)  # Track potential false positives
            iteration_count = 0                      # Count monitoring iterations
            save_interval = 10                       # Interval for saving model state
            collected_features = []                  # Store features for model updates
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
                        # Analyze captured packets for suspicious behavior
                        suspicious_activities = self.packet_analyzer.analyze_traffic(
                            packets,
                            PORT_SCAN_THRESHOLD,
                            DNS_QUERY_THRESHOLD,
                            local_ip,
                            subnet_mask
                        )

                        # Extract features from packets for anomaly detection
                        features = self.anomaly_detector.feature_extractor.extract_features(packets)
                        if features is not None and len(features) > 0:
                            collected_features.extend(features)
                            
                            # Update model periodically with collected features
                            if iteration_count % MODEL_UPDATE_INTERVAL == 0 and collected_features:
                                self.logger.info("Updating anomaly detection model...")
                                self.persistent_detector.update_model(collected_features)
                                collected_features = []  # Reset after update

                        # Perform anomaly detection on current packets
                        anomalies, anomaly_details = self.anomaly_detector.analyze_traffic(
                            packets,
                            self.persistent_detector
                        )

                        # Log detection results and update false positive tracking
                        self._log_results(suspicious_activities, anomaly_details)
                        self._update_false_positives(anomaly_details, false_positive_count)

                    else:
                        self.logger.warning("No packets captured in this batch.")

                    # Save model state periodically
                    iteration_count += 1
                    if iteration_count % save_interval == 0:
                        self.persistent_detector.save_model()
                        self.logger.info("Saved anomaly detection model")

                except Exception as e:
                    self.logger.error(f"Packet processing error: {e}", exc_info=True)

                time.sleep(60)  # Pause between monitoring iterations

        except KeyboardInterrupt:
            self.logger.info("\nStopping packet capture. Exiting.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        finally:
            # Ensure model state is saved before exiting
            if hasattr(self, 'persistent_detector'):
                try:
                    self.persistent_detector.save_model()
                    self.logger.info("Saved final model state")
                except Exception as e:
                    self.logger.error(f"Error saving final model state: {e}")
            self.logger_setup.stop_listener()

    def _log_results(self, suspicious_activities, anomaly_details):
        """Log detected suspicious activities and anomalies"""
        # Log suspicious activities if any were detected
        if suspicious_activities:
            self.logger.info("Suspicious activities detected:")
            for activity in suspicious_activities:
                self.logger.info(f"- {': '.join(map(str, activity))}")
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
    args = parser.parse_args()

    # Create monitor instance and start monitoring
    monitor = NetworkMonitor()
    monitor.check_root_linux()
    monitor.run(args.interface)

if __name__ == "__main__":
    main()
