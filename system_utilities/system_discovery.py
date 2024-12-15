"""
This script provides functionality to gather and display system information.

It uses the platform, socket, and psutil modules to collect various details about the system,
including the operating system, machine architecture, hostname, IP address, CPU cores, and total RAM.

The main function, system_discovery(), prints this information to the console.

When run as a standalone script, it automatically executes the system_discovery() function.

Dependencies:
    - platform
    - socket
    - psutil

Usage:
    Run the script directly to see the system information output.
    Alternatively, import the system_discovery function to use it in other scripts.
"""

# Import necessary modules
import platform  # For system and OS information
import socket    # For network-related functions
import psutil    # For hardware and system utilization information
def system_discovery():
    """Function to gather and print system information"""
    print("System Discovery:")
    
    # Print operating system name and version
    print(f"OS: {platform.system()} {platform.release()}")
    
    # Print machine architecture
    print(f"Machine: {platform.machine()}")
    
    # Print hostname of the machine
    print(f"Hostname: {socket.gethostname()}")
    
    # Print IP address of the machine
    print(f"IP Address: {socket.gethostbyname(socket.gethostname())}")
    
    # Print number of CPU cores
    print(f"CPU Cores: {psutil.cpu_count()}")
    
    # Print total RAM in GB, rounded to 2 decimal places
    print(f"Total RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB")

# Check if the script is being run directly (not imported)
if __name__ == "__main__":
    # Call the system_discovery function
    system_discovery()
