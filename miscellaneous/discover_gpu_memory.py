"""
This script discovers and displays information about all GPUs installed on the system.
"""

import wmi
import subprocess
import re

def get_nvidia_vram():
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True
        )
        vram_list = [int(x.strip()) for x in result.stdout.strip().split('\n') if x.strip().isdigit()]
        # Returns list of VRAM values in MB
        return vram_list
    except Exception:
        return []

def get_all_gpu_info():
    """
    Retrieves and displays information about all GPUs installed on the system.

    Uses Windows Management Instrumentation (WMI) to query for information about all video controllers.
    Prints the following details for each GPU:
    - GPU name
    - Total VRAM (in GB, if available)
    - Driver version
    - Video processor information

    Handles potential errors and prints an error message if an exception occurs.
    """
    try:
        c = wmi.WMI()
        gpus = c.Win32_VideoController()
        nvidia_vram_list = get_nvidia_vram()
        nvidia_idx = 0

        if not gpus:
            print("No GPUs found.")
            return

        for idx, gpu in enumerate(gpus, 1):
            print(f"\nGPU #{idx}: {gpu.Name}")
            vram_shown = False

            # Try NVIDIA-SMI for NVIDIA cards
            if "NVIDIA" in gpu.Name.upper() and nvidia_idx < len(nvidia_vram_list):
                memory_gb = nvidia_vram_list[nvidia_idx] / 1024
                print(f"Total VRAM: {memory_gb:.2f} GB (from nvidia-smi)")
                vram_shown = True
                nvidia_idx += 1

            # Fallback to WMI
            if not vram_shown:
                try:
                    adapter_ram = int(gpu.AdapterRAM) if gpu.AdapterRAM is not None else None
                    if adapter_ram and adapter_ram > 0:
                        memory_gb = adapter_ram / (1024**3)
                        print(f"Total VRAM: {memory_gb:.2f} GB")
                    else:
                        print("Total VRAM: Unknown")
                except Exception:
                    print("Total VRAM: Unknown")

            print(f"Driver Version: {gpu.DriverVersion}")
            print(f"Video Processor: {gpu.VideoProcessor}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Call the function when the script is run directly
    get_all_gpu_info()
