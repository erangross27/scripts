"""
This script handles interface manager.
"""

import psutil  # Library to retrieve information on running processes and system utilization
import socket  # Library for low-level networking functions 
import netifaces  # Library to get network interface information 
import wmi  # Library for accessing Windows Management Instrumentation
from bidi.algorithm import get_display  # Library to handle bidirectional display of strings
class InterfaceManager:
    """
    Manages interface.
    """
    def __init__(self, logger):
        """
        Special method __init__.
        """
        self.logger = logger

    def get_interfaces(self):
        """Retrieve a list of active network interfaces along with their IP addresses and netmasks."""
        interfaces = []  # Initialize an empty list to store interface details
        for iface, addrs in psutil.net_if_addrs().items():
            # Iterate over interfaces and associated addresses
            for addr in addrs:
                if (addr.family == socket.AF_INET and 
                    not addr.address.startswith('169.254.') and 
                    addr.address != '127.0.0.1'):
                    # Check if the address family is IPv4 and exclude link-local and loopback addresses
                    
                    # Get the real Windows interface name for each adapter
                    try:
                        real_name = iface  # Store the interface name
                        netmask = addr.netmask if hasattr(addr, 'netmask') else None  # Retrieve netmask if available
                        if netmask:
                            interfaces.append((real_name, addr.address, netmask))  # Append to the list
                            break  # Exit the inner loop once valid info is found
                    except Exception:
                        continue  # Continue to the next address if an exception occurs
        return interfaces

    def get_subnet_mask(self, interface_name, ip_address):
        """Get the subnet mask for a given interface."""
        try:
            if sys.platform.startswith('win'):
                import wmi
                c = wmi.WMI()  # Initialize WMI on Windows
                
                # Iterate over network adapter configurations
                for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                    if ip_address in interface.IPAddress:
                        return interface.IPSubnet[0]  # Return the first subnet mask
            else:  # Linux
                import subprocess
                output = subprocess.check_output(['ip', 'addr', 'show', interface_name]).decode()
                
                # Parse the output to locate the CIDR notation
                for line in output.split('\n'):
                    if ip_address in line and '/' in line:
                        # Convert CIDR to subnet mask
                        cidr = int(line.split('/')[1].split()[0])
                        mask = [0, 0, 0, 0]  # Initialize a list for the subnet mask
                        for i in range(cidr):
                            mask[i//8] = mask[i//8] + (1 << (7 - i % 8))  # Set the appropriate bits
                        return ".".join(map(str, mask))  # Convert the list to a dotted string
                        
            self.logger.warning(f"Could not determine subnet mask for {interface_name}, using default")
            return "255.255.255.0"  # Default subnet mask
        except Exception as e:
            self.logger.error(f"Error getting subnet mask: {e}")
            return "255.255.255.0"

    def choose_interface(self, interfaces):
        """Allow user to choose a network interface."""
        if not interfaces:
            self.logger.info("No active network interfaces found.")
            return None, None, None

        self.logger.info("Available active interfaces:")
        self.logger.info("")

        # Display interfaces
        for i, (iface, ip, _) in enumerate(interfaces):
            self.logger.info(f"{i}: {get_display(iface)} (IP: {ip})")

        self.logger.info("")

        while True:
            try:
                choice = input("Enter the number of the interface to use: ").strip()
                choice = int(choice)  # Convert user input to an integer
                if 0 <= choice < len(interfaces):
                    chosen_interface, chosen_ip, netmask = interfaces[choice]
                    self.logger.info(
                        f"Selected interface: {get_display(chosen_interface)} "
                        f"(IP: {chosen_ip}, Subnet: {netmask})"
                    )
                    return chosen_interface, chosen_ip, netmask
                else:
                    self.logger.info("Invalid choice. Please enter a number within range.")
            except ValueError:
                self.logger.info("Invalid input. Please enter a number.")

    def setup_interface(self, specified_interface=None):
        """Setup network interface either automatically or based on user choice."""
        interfaces = self.get_interfaces()

        if not interfaces:
            self.logger.info("No active network interfaces found. Exiting.")
            return None, None, None

        if specified_interface:
            interface_info = next(
                (info for info in interfaces if info[0] == specified_interface), 
                None
            )
            if interface_info:
                return interface_info  # Return the specific interface information
            else:
                self.logger.info(f"Specified interface {specified_interface} not found.")
                return None, None, None
        else:
            return self.choose_interface(interfaces)  # Allow the user to choose an interface
