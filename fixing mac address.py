known_devices_file = "known_devices.txt"
with open(known_devices_file) as f:
    known_devices = [line.split()[2].replace(":", "").replace(" ", "") for line in f]

with open(known_devices_file, "w") as f:
    for mac_address in known_devices:
        f.write(mac_address + "\n")