"""
This script handles discover gpu memory.
"""

import wmi

def get_intel_gpu_info():
    """
    Retrieves and displays information about the Intel GPU installed on the system.

    This function uses Windows Management Instrumentation (WMI) to query for
    information about the Intel GPU. It prints the following details:
    - GPU name
    - Total VRAM (in GB, if available)
    - Driver version
    - Video processor information

    The function handles potential errors and prints an error message if an exception occurs.

    Note: This function is designed to work on Windows systems with Intel GPUs.
    Returns:
    None. Information is printed to the console.

    Raises:
    Exception: Any exception that occurs during WMI querying or data processing.
    """
    try:
        # Initialize WMI object
        c = wmi.WMI()
        
        # Query for Intel GPU information
        gpu_info = c.Win32_VideoController(AdapterCompatibility="Intel Corporation")[0]
        
        # Print GPU name
        print(f"GPU: {gpu_info.Name}")
        
        # Convert memory to GB and handle cases where AdapterRAM is not available
        memory_gb = int(gpu_info.AdapterRAM) / (1024**3) if gpu_info.AdapterRAM else "Unknown"
        
        # Print total VRAM, formatting as float if available, otherwise as string
        print(f"Total VRAM: {memory_gb:.2f} GB" if isinstance(memory_gb, float) else f"Total VRAM: {memory_gb}")
        
        # Print driver version
        print(f"Driver Version: {gpu_info.DriverVersion}")
        
        # Print video processor information
        print(f"Video Processor: {gpu_info.VideoProcessor}")
        
    except Exception as e:
        # Handle and print any exceptions that occur
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Call the function when the script is run directly
    get_intel_gpu_info()
