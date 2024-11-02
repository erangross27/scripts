import argparse
import sys
import time
import os
from collections import defaultdict

from logger_setup import LoggerSetup
from interface_manager import InterfaceManager
from packet_capture import PacketCapture
from packet_analyzer import PacketAnalyzer
from anomaly_detector import AnomalyDetector
from models.persistent_anomaly_detector import PersistentAnomalyDetector

class NetworkMonitor:
    def __init__(self):
        self.logger_setup = LoggerSetup()
        self.logger = self.logger_setup.get_logger()
        self.interface_manager = InterfaceManager(self.logger)
        self.packet_capture = PacketCapture(self.logger)
        self.packet_analyzer = PacketAnalyzer(self.logger)
        self.anomaly_detector = AnomalyDetector(self.logger)
        self.persistent_detector = PersistentAnomalyDetector()

    def check_root_linux(self):
        if sys.platform.startswith('linux'):
            if os.geteuid() != 0:
                print("This script requires root privileges to capture network packets on Linux.")
                print("Please run the script with sudo, like this:")
                print("sudo python3 network_monitor.py")
                sys.exit(1)

    def run(self, interface_name=None):
        try:
            PORT_SCAN_THRESHOLD = 10
            DNS_QUERY_THRESHOLD = 25
            PACKET_COUNT = 1000
            MODEL_UPDATE_INTERVAL = 5  # Update model every 5 iterations
            
            # Setup network interface
            interface, local_ip, subnet_mask = self.interface_manager.setup_interface(interface_name)
            if not interface:
                self.logger.error("No valid interface found. Exiting.")
                return

            false_positive_count = defaultdict(int)
            iteration_count = 0
            save_interval = 10
            collected_features = []

            # Load or initialize the model
            try:
                self.persistent_detector.load_model()
                self.logger.info("Loaded existing anomaly detection model")
            except Exception as e:
                self.logger.warning(f"Could not load model: {e}. Will create new model after collecting data.")

            while True:
                try:
                    # Capture packets
                    packets = self.packet_capture.capture_packets(
                        interface, 
                        PACKET_COUNT
                    )

                    if packets:
                        # Analyze for suspicious activities
                        suspicious_activities = self.packet_analyzer.analyze_traffic(
                            packets,
                            PORT_SCAN_THRESHOLD,
                            DNS_QUERY_THRESHOLD,
                            local_ip,
                            subnet_mask
                        )

                        # Extract features and update model
                        features = self.anomaly_detector.feature_extractor.extract_features(packets)
                        if features is not None and len(features) > 0:
                            collected_features.extend(features)
                            
                            # Update model periodically
                            if iteration_count % MODEL_UPDATE_INTERVAL == 0 and collected_features:
                                self.logger.info("Updating anomaly detection model...")
                                self.persistent_detector.update_model(collected_features)
                                collected_features = []  # Reset after update

                        # Detect anomalies
                        anomalies, anomaly_details = self.anomaly_detector.analyze_traffic(
                            packets,
                            self.persistent_detector
                        )

                        # Log results
                        self._log_results(suspicious_activities, anomaly_details)
                        
                        # Update false positive tracking
                        self._update_false_positives(anomaly_details, false_positive_count)

                    else:
                        self.logger.warning("No packets captured in this batch.")

                    # Save model periodically
                    iteration_count += 1
                    if iteration_count % save_interval == 0:
                        self.persistent_detector.save_model()
                        self.logger.info("Saved anomaly detection model")

                except Exception as e:
                    self.logger.error(f"Packet processing error: {e}", exc_info=True)

                time.sleep(60)

        except KeyboardInterrupt:
            self.logger.info("\nStopping packet capture. Exiting.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        finally:
            # Save final model state
            if hasattr(self, 'persistent_detector'):
                try:
                    self.persistent_detector.save_model()
                    self.logger.info("Saved final model state")
                except Exception as e:
                    self.logger.error(f"Error saving final model state: {e}")
            self.logger_setup.stop_listener()


    def _log_results(self, suspicious_activities, anomaly_details):
        if suspicious_activities:
            self.logger.info("Suspicious activities detected:")
            for activity in suspicious_activities:
                self.logger.info(f"- {': '.join(map(str, activity))}")
        else:
            self.logger.info("No suspicious activities detected.")

        if anomaly_details:
            self.logger.info("Anomalies detected:")
            for detail in anomaly_details[:10]:
                self.logger.info(detail)
            if len(anomaly_details) > 10:
                self.logger.info(f"... and {len(anomaly_details) - 10} more anomalies.")
        else:
            self.logger.info("No anomalies detected.")

    def _update_false_positives(self, anomaly_details, false_positive_count):
        for detail in anomaly_details:
            false_positive_count[detail] += 1
            if false_positive_count[detail] > 10:
                self.logger.info(f"Adapting to frequent anomaly: {detail}")
                false_positive_count[detail] = 0

def main():
    parser = argparse.ArgumentParser(description='Network Monitor')
    parser.add_argument('--interface', type=str, help='Network interface to use')
    args = parser.parse_args()

    monitor = NetworkMonitor()
    monitor.check_root_linux()
    monitor.run(args.interface)

if __name__ == "__main__":
    main()
