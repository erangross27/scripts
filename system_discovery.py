import platform
import socket
import psutil

def system_discovery():
    print("System Discovery:")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Hostname: {socket.gethostname()}")
    print(f"IP Address: {socket.gethostbyname(socket.gethostname())}")
    print(f"CPU Cores: {psutil.cpu_count()}")
    print(f"Total RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB")

if __name__ == "__main__":
    system_discovery()
