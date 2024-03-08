import subprocess
import pandas as pd

def get_netbios_names():
    # Run the nbtscan command with a timeout and get the output
    command = "nbtscan 172.21.0.0/19"
    try:
        result = subprocess.check_output(command, shell=True, timeout=600).decode()  # 10 minutes timeout
    except subprocess.TimeoutExpired:
        print("The nbtscan command timed out.")
        return []

    # Split the output into lines
    lines = result.split("\n")

    # Extract the NetBIOS names
    netbios_names = [line.split()[1] for line in lines if line and line[0].isdigit()]

    return netbios_names

netbios_names = get_netbios_names()

# Create a DataFrame from the NetBIOS names
df = pd.DataFrame(netbios_names, columns=['NetBIOS Name'])

# Write the DataFrame to an Excel file
df.to_excel('netbios_names.xlsx', index=False)