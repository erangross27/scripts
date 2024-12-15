"""
This script provides information about disk usage and CPU utilization.

It uses the psutil library to gather and display the following information:
1. Free space available on C: and D: drives (in GB)
2. CPU usage statistics for each CPU core (user, system, and idle percentages)

The script first checks disk partitions, focusing on C: and D: drives,
and reports the free space available on each.

Then, it collects CPU usage data for a 1-second interval and displays
the usage percentages for each CPU core.

Requirements:
- psutil library must be installed

Note: This script is designed for Windows systems, as it specifically looks for
C: and D: drives.
"""

import psutil

# Get disk usage statistics
disk_usage = [p for p in psutil.disk_partitions(all=True) if p.device.startswith('C:') or p.device.startswith('D:')]

# Iterate over each partition and display free space in GB
for partition in disk_usage:
    partition_usage = psutil.disk_usage(partition.mountpoint)
    free_space_gb = round(partition_usage.free / (1024 ** 3), 2)
    print(f"Partition {partition.mountpoint} has {free_space_gb} GB free space.")

# Get CPU usage statistics
cpu_times = psutil.cpu_times_percent(interval=1, percpu=True)
# Display CPU usage details
for i, cpu in enumerate(cpu_times):
     print(f"CPU {i}: {cpu.user}% user, {cpu.system}% system, {cpu.idle}% idle")