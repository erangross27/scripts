import psutil

# Get disk usage statistics
disk_usage = psutil.disk_partitions(all=True)

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
     