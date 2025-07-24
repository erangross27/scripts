"""
This script handles packet capture.
"""

try:
    from scapy.all import sniff
except ImportError:
    print("Warning: scapy is not installed. Packet capture functionality will be limited.")
    
import time
import multiprocessing
from multiprocessing import Queue, Process
from queue import Empty
try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm is not available
    class tqdm:
        def __init__(self, total, unit):
            self.total = total
            self.unit = unit
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            pass
            
        def update(self, n):
            pass

class PacketCapture:
    """
    Represents a packet capture.
    """
    def __init__(self, logger):
        """
        Special method __init__.
        """
        self.logger = logger
        try:
            self.num_cores = multiprocessing.cpu_count()
        except Exception:
            self.num_cores = 1
            self.logger.warning("Could not determine number of CPU cores, defaulting to 1")

    def capture_packets_worker(self, interface, count, result_queue):
        """
        Capture packets worker based on interface, count, result queue.
        """
        packets_captured = 0
        
        def packet_handler(pkt):
            """
            Packet handler based on pkt.
            """
            nonlocal packets_captured
            if packets_captured < count:
                try:
                    result_queue.put((pkt.time, bytes(pkt)))
                    packets_captured += 1
                except Exception as e:
                    self.logger.debug(f"Error processing packet: {e}")
        
        try:
            sniff(
                iface=interface,
                prn=packet_handler,
                store=False,
                count=count,
                timeout=30
            )
        except Exception as e:
            self.logger.error(f"Capture error on interface {interface}: {e}")
        finally:
            try:
                result_queue.put(None)
            except Exception as e:
                self.logger.debug(f"Error putting None in queue: {e}")

    def capture_packets(self, interface, total_count):
        """
        Capture packets based on interface, total count.
        """
        try:
            # Validate inputs
            if not interface:
                self.logger.error("No interface specified for packet capture")
                return []
                
            if total_count <= 0:
                self.logger.error("Invalid packet count specified")
                return []

            result_queue = Queue()
            processes = []
            packets_per_worker = max(1, total_count // self.num_cores)
            
            # Start worker processes
            for i in range(min(self.num_cores, total_count)):
                try:
                    p = Process(
                        target=self.capture_packets_worker,
                        args=(interface, packets_per_worker, result_queue),
                        daemon=True
                    )
                    processes.append(p)
                    p.start()
                except Exception as e:
                    self.logger.error(f"Error starting worker process {i}: {e}")

            all_packets = []
            completed_workers = 0
            
            with tqdm(total=total_count, unit='packet') as pbar:
                while completed_workers < len(processes) and len(all_packets) < total_count:
                    try:
                        packet = result_queue.get(timeout=1)
                        if packet is None:
                            completed_workers += 1
                            continue
                        all_packets.append(packet)
                        pbar.update(1)
                    except Empty:
                        continue
                    except Exception as e:
                        self.logger.debug(f"Error getting packet from queue: {e}")
                        continue

            # Cleanup
            for p in processes:
                try:
                    if p.is_alive():
                        p.terminate()
                    p.join(timeout=1)
                except Exception as e:
                    self.logger.debug(f"Error cleaning up process: {e}")

            return all_packets

        except Exception as e:
            self.logger.error(f"Capture failed: {e}")
            return []