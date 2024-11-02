import socket

def resolve_ip(ip):
    """Resolve an IP address to a hostname."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.timeout):
        return ip

def is_private_ip(ip):
    """Check if an IP address is private."""
    try:
        # Split IP into octets
        octets = list(map(int, ip.split('.')))
        return (
            octets[0] == 10 or
            (octets[0] == 172 and octets[1] >= 16 and octets[1] <= 31) or
            (octets[0] == 192 and octets[1] == 168)
        )
    except:
        return False
