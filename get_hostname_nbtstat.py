import socket
import subprocess
import winreg
import re
import uuid

def get_local_ip_and_network():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces')
        for i in range(winreg.QueryInfoKey(key)[0]):
            try:
                interface_key = winreg.OpenKey(key, winreg.EnumKey(key, i))
                ip_address = winreg.QueryValueEx(interface_key, 'IPAddress')[0][0]
                subnet_mask = winreg.QueryValueEx(interface_key, 'SubnetMask')[0]
                
                if ip_address == local_ip:
                    ip_int = int.from_bytes(socket.inet_aton(local_ip), 'big')
                    mask_int = int.from_bytes(socket.inet_aton(subnet_mask), 'big')
                    network_int = ip_int & mask_int
                    network_address = socket.inet_ntoa(network_int.to_bytes(4, 'big'))
                    cidr = bin(mask_int).count('1')
                    return local_ip, f"{network_address}/{cidr}"
            except WindowsError:
                continue
    except WindowsError:
        pass

    return local_ip, f"{local_ip.rsplit('.', 1)[0]}.0/24"

def get_arp_table():
    arp_output = subprocess.check_output("arp -a", shell=True).decode()
    ips = []
    for line in arp_output.split('\n'):
        if 'dynamic' in line.lower():
            ip = line.split()[0]
            ips.append(ip)
    return ips

def get_netbios_name(ip):
    try:
        output = subprocess.check_output(f'nbtstat -A {ip}', shell=True, stderr=subprocess.DEVNULL, timeout=2).decode('ascii', errors='ignore')
        for line in output.splitlines():
            if '<00>' in line and 'UNIQUE' in line:
                return line.split()[0].strip().rstrip('<00>')
    except subprocess.TimeoutExpired:
        pass
    except subprocess.CalledProcessError:
        pass
    return None

def get_local_mac():
    return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,8*6,8)][::-1])

def get_mac_address(ip, local_ip):
    if ip == local_ip:
        return get_local_mac()
    
    arp_output = subprocess.check_output(f"arp -a {ip}", shell=True).decode()
    for line in arp_output.split('\n'):
        if ip in line:
            mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', line)
            if mac:
                return mac.group()
    return "Unknown"

def get_device_type(mac):
    mac_prefix = mac[:8].upper()
    prefixes = {
        '00:50:56': 'VMware',
        '00:0C:29': 'VMware',
        '00:1A:11': 'Google',
        '00:03:93': 'Apple',
        '00:05:02': 'Apple',
        'AC:DE:48': 'Apple',
        '00:1A:A0': 'Dell',
        '00:14:22': 'Dell',
        '00:60:52': 'Realtek',
        '52:54:00': 'QEMU/KVM',
        '00:E0:4C': 'Realtek'
    }
    return prefixes.get(mac_prefix, "Unknown")

def get_hostname(ip, local_ip):
    if ip == local_ip:
        return socket.gethostname()
    
    netbios_name = get_netbios_name(ip)
    if netbios_name:
        return netbios_name
    
    return f"Unknown-{ip}"
def main():
    local_ip, network = get_local_ip_and_network()
    print(f"Local IP: {local_ip}")
    print(f"Network: {network}")
    
    print("Discovering active IPs using ARP...")
    active_ips = get_arp_table()
    
    if local_ip not in active_ips:
        active_ips.append(local_ip)
    
    print(f"Found {len(active_ips)} active IPs (including local IP)")
    
    results = []
    for ip in active_ips:
        hostname = get_hostname(ip, local_ip)
        mac = get_mac_address(ip, local_ip)
        device_type = get_device_type(mac)
        results.append((ip, hostname, mac, device_type))
        print(f"IP: {ip}, Hostname: {hostname}, MAC: {mac}, Type: {device_type}")
    
    with open('network_scan_results.txt', 'w') as f:
        f.write("IP,Hostname,MAC,DeviceType\n")
        for ip, hostname, mac, device_type in results:
            f.write(f"{ip},{hostname},{mac},{device_type}\n")

if __name__ == "__main__":
    main()
