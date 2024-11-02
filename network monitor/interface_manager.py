import psutil
import socket
import netifaces
import wmi
from bidi.algorithm import get_display

class InterfaceManager:
    def __init__(self, logger):
        self.logger = logger

    def get_interfaces(self):
        """Retrieve a list of active network interfaces along with their IP addresses and netmasks."""
        interfaces = []
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if (addr.family == socket.AF_INET and 
                    not addr.address.startswith('169.254.') and 
                    addr.address != '127.0.0.1'):
                    # Get the real Windows interface name for each adapter
                    try:
                        real_name = iface
                        netmask = addr.netmask if hasattr(addr, 'netmask') else None
                        if netmask:
                            interfaces.append((real_name, addr.address, netmask))
                            break
                    except Exception:
                        continue
        return interfaces

    def get_subnet_mask(self, interface_name, ip_address):
        """Get the subnet mask for a given interface."""
        try:
            if sys.platform.startswith('win'):
                import wmi
                c = wmi.WMI()
                for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                    if ip_address in interface.IPAddress:
                        return interface.IPSubnet[0]
            else:  # Linux
                import subprocess
                output = subprocess.check_output(['ip', 'addr', 'show', interface_name]).decode()
                for line in output.split('\n'):
                    if ip_address in line and '/' in line:
                        # Convert CIDR to subnet mask
                        cidr = int(line.split('/')[1].split()[0])
                        mask = [0, 0, 0, 0]
                        for i in range(cidr):
                            mask[i//8] = mask[i//8] + (1 << (7 - i % 8))
                        return ".".join(map(str, mask))
                        
            self.logger.warning(f"Could not determine subnet mask for {interface_name}, using default")
            return "255.255.255.0"
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
                choice = int(choice)
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
                return interface_info
            else:
                self.logger.info(f"Specified interface {specified_interface} not found.")
                return None, None, None
        else:
            return self.choose_interface(interfaces)
