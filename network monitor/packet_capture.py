"""
This script handles packet capture.
"""

from scapy.all import sniff
import time
import multiprocessing
from multiprocessing import Queue, Process
from queue import Empty
from tqdm import tqdm

class PacketCapture:
    """
    Represents a packet capture.
    """
    def __init__(self, logger):
        """
        Special method __init__.
        """
        self.logger = logger
        self.num_cores = multiprocessing.cpu_count()

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
                result_queue.put((pkt.time, bytes(pkt)))
                packets_captured += 1
        
        try:
            sniff(
                iface=interface,
                prn=packet_handler,
                store=False,
                count=count,
                timeout=30
            )
        except Exception as e:
            self.logger.error(f"Capture error: {e}")
        finally:
            result_queue.put(None)

    def capture_packets(self, interface, total_count):
        """
        Capture packets based on interface, total count.
        """
        try:
            result_queue = Queue()
            processes = []
            packets_per_worker = total_count // self.num_cores
            
            # Start worker processes
            for _ in range(self.num_cores):
                p = Process(
                    target=self.capture_packets_worker,
                    args=(interface, packets_per_worker, result_queue),
                    daemon=True
                )
                processes.append(p)
                p.start()

            all_packets = []
            completed_workers = 0
            
            with tqdm(total=total_count, unit='packet') as pbar:
                while completed_workers < self.num_cores and len(all_packets) < total_count:
                    try:
                        packet = result_queue.get(timeout=1)
                        if packet is None:
                            completed_workers += 1
                            continue
                        all_packets.append(packet)
                        pbar.update(1)
                    except Empty:
                        continue

            # Cleanup
            for p in processes:
                if p.is_alive():
                    p.terminate()
                p.join(timeout=1)

            return all_packets

        except Exception as e:
            self.logger.error(f"Capture failed: {e}")
            return []
