import platform
import psutil
import wmi

# Get computer model and serial number
computer = wmi.WMI()
system_info = computer.Win32_ComputerSystem()[0]
model = system_info.Model
serial_number = computer.Win32_BIOS()[0].SerialNumber.strip()

# Get OS version
os_version = platform.win32_ver()[0]

# Get disk size and type
disk_usage = psutil.disk_usage('/')
disk_size_gb = round(disk_usage.total / (1024 ** 3), 2)
disk_type = psutil.disk_partitions()[0].opts.split(',')[0]

# Get memory size in GB
memory_size_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)

# Get CPU model
cpu_info = platform.processor()
if 'Intel' in cpu_info:
    cpu_info = cpu_info.replace('(R)', '').replace('CPU', '').strip()
    cpu_info = ' '.join(cpu_info.split()[:4])
elif 'AMD' in cpu_info:
    cpu_info = cpu_info.replace('Processor', '').strip()

# Display computer information
print(f"Computer model: {model}")
print(f"Serial number: {serial_number}")
print(f"OS version: {os_version}")
print(f"Disk size: {disk_size_gb} GB")
print(f"Disk type: {disk_type}")
print(f"Memory size: {memory_size_gb} GB")
print(f"CPU model: {cpu_info}")