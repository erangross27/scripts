import boto3
import subprocess
import time
import botocore.exceptions

# Define the name of the S3 bucket where the known devices will be stored
BUCKET_NAME = "bucket1"

def read_known_devices():
    """
    Reads the known devices from the S3 bucket and returns them as a set.
    """
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=BUCKET_NAME, Key="known_devices.txt")
    known_devices = response["Body"].read().decode().splitlines()
    return set(known_devices)

def write_known_devices(known_devices):
    """
    Writes the known devices to the S3 bucket.
    """
    s3 = boto3.client("s3")
    s3.put_object(Bucket=BUCKET_NAME, Key="known_devices.txt", Body="\n".join(sorted(known_devices)))

def scan_network():
    """
    Scans the network for active devices using the nmap command and returns the output as a string.
    """
    output = subprocess.check_output(["nmap.exe", "-sn", "172.21.0.0/19"])
    return output.decode()

def find_new_devices(known_devices, nmap_output):
    """
    Compares the known devices to the nmap output and returns a set of new devices.
    """
    new_devices = set()
    for line in nmap_output.splitlines():
        if "MAC Address:" in line:
            mac_address = line.split("MAC Address: ")[1].split()[0]
            if mac_address not in known_devices:
                new_devices.add(mac_address)
    return new_devices

def translate_mac_address(mac_address):
    """
    Translates a MAC address to a NetBIOS name using the nbtstat command and returns the name as a string.
    """
    try:
        netbios_name = subprocess.check_output(["nbtstat", "-A", mac_address])
        netbios_name = netbios_name.decode().split("\n")[1].strip()
    except:
        netbios_name = "Unknown"
    return netbios_name

def write_alert(alert):
    """
    Writes an alert to the console and sends it to an SNS topic.
    """
    print(alert)
    sns = boto3.client("sns")
    sns.publish(TopicArn="arn:aws:sns:us-east-1:123456789012:alerts", Message=alert)

def monitor_network():
    """
    Monitors the network for new and missing devices and writes alerts to the console and an SNS topic.
    """
    create_bucket_if_not_exists()
    known_devices = read_known_devices()
    while True:
        nmap_output = scan_network()
        missing_devices = known_devices - set(nmap_output.split())
        new_devices = find_new_devices(known_devices, nmap_output)
        for mac_address in new_devices:
            netbios_name = translate_mac_address(mac_address)
            alert = f"New device found: {netbios_name} ({mac_address})"
            write_alert(alert)
        if missing_devices:
            alert = f"Missing devices: {', '.join(missing_devices)}"
            write_alert(alert)
        else:
            print("All devices present")
        known_devices.update(new_devices)
        write_known_devices(known_devices)
        time.sleep(300)

def create_bucket_if_not_exists():
    """
    Creates the S3 bucket if it does not already exist.
    """
    s3 = boto3.client("s3")
    try:
        if BUCKET_NAME not in [bucket["Name"] for bucket in s3.list_buckets()["Buckets"]]:
            s3.create_bucket(Bucket=BUCKET_NAME)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AccessDenied":
            print("Error: Access denied. Please check your AWS credentials and permissions.")
        else:
            print(f"Error: {e}")

            


if __name__ == "__main__":
    monitor_network()