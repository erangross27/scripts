"""
This script handles discover monitor information.
"""

import wmi
import sys
import subprocess

def get_monitor_info_wmi():
    """
    Retrieve monitor information using Windows Management Instrumentation (WMI).
    
    Returns:
        list: A list of dictionaries containing monitor information.
    """
    try:
        c = wmi.WMI(namespace="wmi")
        monitors = c.WmiMonitorID()
        
        if not monitors:
            print("No monitors found using WMI.")
            return []

        monitor_info = []
        for monitor in monitors:
            # Extract monitor information and convert byte arrays to strings
            info = {
                "ManufacturerName": "".join([chr(x) for x in monitor.ManufacturerName if x > 0]),
                "ProductCodeID": "".join([chr(x) for x in monitor.ProductCodeID if x > 0]),
                "SerialNumberID": "".join([chr(x) for x in monitor.SerialNumberID if x > 0]),
                "UserFriendlyName": "".join([chr(x) for x in monitor.UserFriendlyName if x > 0]),
                "YearOfManufacture": monitor.YearOfManufacture,
                "WeekOfManufacture": monitor.WeekOfManufacture
            }
            monitor_info.append(info)

        return monitor_info

    except Exception as e:
        print(f"An error occurred with WMI: {e}")
        return []

def get_monitor_info_powershell():
    """
    Retrieve monitor information using PowerShell as a fallback method.
    
    Returns:
        list: A list of dictionaries containing monitor information.
    """
    try:
        # PowerShell command to retrieve monitor information
        command = "Get-WmiObject WmiMonitorID -Namespace root\\wmi | ForEach-Object { $m = $_; $info = @{}; 'ManufacturerName','ProductCodeID','SerialNumberID','UserFriendlyName' | ForEach-Object { $info[$_] = [System.Text.Encoding]::ASCII.GetString($m.$_).Trim(\"`0\") }; $info['YearOfManufacture'] = $m.YearOfManufacture; $info['WeekOfManufacture'] = $m.WeekOfManufacture; $info }"
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"PowerShell command failed: {result.stderr}")
            return []

        # Parse the PowerShell output
        lines = result.stdout.strip().split('\n')
        monitor_info = []
        current_monitor = {}
        for line in lines:
            if line.strip():
                key, value = line.split(':', 1)
                current_monitor[key.strip()] = value.strip()
            else:
                if current_monitor:
                    monitor_info.append(current_monitor)
                    current_monitor = {}
        if current_monitor:
            monitor_info.append(current_monitor)

        return monitor_info

    except Exception as e:
        print(f"An error occurred with PowerShell: {e}")
        return []

def main():
    """
    Main function to retrieve and display monitor information.
    """
    print("Fetching monitor information...")
    
    # Try to get monitor info using WMI first
    monitor_info = get_monitor_info_wmi()
    
    # If WMI fails, try using PowerShell
    if not monitor_info:
        print("Attempting to fetch information using PowerShell...")
        monitor_info = get_monitor_info_powershell()
    
    # Display the retrieved monitor information
    if monitor_info:
        print("\nDetected Monitors:")
        for i, info in enumerate(monitor_info, 1):
            print(f"Monitor {i}:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            print()
    else:
        print("No monitor information found or unable to retrieve monitor information.")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()