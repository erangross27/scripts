"""
Disk Space Alert Service

This script implements a Windows service that monitors disk space on local drives
and sends email alerts when available space falls below a configured threshold.

Features:
- Runs as a Windows service
- Configurable check interval and minimum free space threshold
- Email alerts with customizable SMTP settings
- Encrypted storage of email credentials in Windows Registry
- Logging with rotation to prevent excessive log file growth

Usage:
python script.py [install|start|stop|remove|update|reconfigure]
- install: Install the service and configure email settings
- start: Start the service
- stop: Stop the service
- remove: Remove the service
- update: Update the service configuration
- reconfigure: Reconfigure email settings

Dependencies:
psutil, win32event, win32service, win32serviceutil, servicemanager, winreg, cryptography

Configuration:
Settings are stored in a 'config.json' file in the same directory as the script.
Email credentials are securely stored in the Windows Registry.

Note: This script is designed to run on Windows systems only.
"""

import sys
import os
from typing import Dict, List, Optional
import json
import logging
from logging.handlers import RotatingFileHandler
import time
from dataclasses import dataclass

# Function to check if all required modules are installed
def check_dependencies() -> bool:
    required_modules = ['psutil', 'win32event', 'win32service', 'win32serviceutil', 'servicemanager', 'winreg', 'cryptography']
    missing_modules = [module for module in required_modules if not check_module(module)]
    
    if missing_modules:
        print("Error: The following required modules are missing:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install these modules using pip:")
        print(f"pip install {' '.join(missing_modules)}")
        return False
    return True

# Helper function to check if a single module is installed
def check_module(module: str) -> bool:
    try:
        __import__(module)
        return True
    except ImportError:
        return False

# Exit if any required dependencies are missing
if not check_dependencies():
    sys.exit(1)

# Import required modules
import psutil
import smtplib
import getpass
import win32event
import win32service
import win32serviceutil
import servicemanager
import winreg
from cryptography.fernet import Fernet
from email.message import EmailMessage

# Add the script's directory to the Python path to ensure local imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Set up logging with rotation to prevent log files from growing too large
log_file = os.path.join(script_dir, "diskspacealertservice.log")
logger = logging.getLogger("DiskSpaceAlertService")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Define the path for the configuration file
CONFIG_FILE = os.path.join(script_dir, "config.json")

# Define a dataclass to hold configuration settings
@dataclass
class Config:
    check_interval: int = 3600  # Default check interval: 1 hour
    min_free_space_gb: float = 10.0  # Default minimum free space: 10 GB
    registry_key: str = r'SOFTWARE\DiskSpaceAlertService'
    smtp_server: str = ""
    smtp_port: int = 587
    recipient_email: str = ""

# Function to load configuration from file or return default values
def load_config() -> Config:
    try:
        with open(CONFIG_FILE, 'r') as f:
            config_dict = json.load(f)
        return Config(**config_dict)
    except FileNotFoundError:
        return Config()

# Load the configuration
config = load_config()

# Define the Windows service class
class DiskSpaceAlertService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DiskSpaceAlertService"
    _svc_display_name_ = "Disk Space Alert Service"
    _svc_description_ = "Checks local disks' free space and sends an email alert if any disk has less than the configured free space."

    def __init__(self, args):
        try:
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.is_alive = True
            logger.info("Service initialized")
        except Exception as e:
            logger.exception("Error during service initialization")
            raise

    # Method called when the service is being stopped
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
        logger.info("Service stop requested")

    # Main service loop
    def SvcDoRun(self):
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            self.main()
        except Exception as e:
            logger.exception("Error during service execution")
            self.SvcStop()

    # Main loop of the service
    def main(self):
        logger.info("Service started")
        while self.is_alive:
            try:
                self.check_disk_space()
                # Wait for the specified interval or service stop signal
                win32event.WaitForSingleObject(self.hWaitStop, config.check_interval * 1000)
            except Exception as e:
                logger.exception("Error in main service loop")
                time.sleep(60)  # Wait a minute before retrying

    # Method to check disk space and send alerts if necessary
    def check_disk_space(self):
        disks = self.get_disks()
        for disk in disks:
            if disk["FreeSpaceGB"] < config.min_free_space_gb:
                self.send_alert(disk)

    # Static method to get disk information
    @staticmethod
    def get_disks() -> List[Dict[str, float]]:
        try:
            # Filter out CD-ROM drives and empty drives on Windows
            nt_filter = lambda p: 'cdrom' not in p.opts and p.fstype != ''
            partitions = filter(nt_filter, psutil.disk_partitions()) if os.name == 'nt' else psutil.disk_partitions()

            return [
                {
                    "DeviceID": partition.device,
                    "FreeSpaceGB": psutil.disk_usage(partition.mountpoint).free / (1024 ** 3),
                }
                for partition in partitions
            ]
        except Exception as e:
            logger.exception("Error getting disk information")
            return []

    # Method to send alert emails
    def send_alert(self, disk: Dict[str, float]):
        try:
            creds = self.get_email_credentials()
            computer_name = os.environ.get('COMPUTERNAME', 'Unknown Computer')
            
            subject = f"Disk space alert on {computer_name}"
            body = f"The disk {disk['DeviceID']} on {computer_name} has {disk['FreeSpaceGB']:.2f} GB of free space left."

            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = subject
            msg["From"] = creds["EmailUsername"]
            msg["To"] = config.recipient_email

            # Send the email using SMTP
            with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
                server.starttls()
                server.login(creds["EmailUsername"], creds["EmailPassword"])
                server.send_message(msg)
            
            logger.info(f"Alert sent for disk {disk['DeviceID']}")
        except Exception as e:
            logger.exception("Error sending alert email")

    # Static method to retrieve email credentials from Windows Registry
    @staticmethod
    def get_email_credentials() -> Dict[str, str]:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, config.registry_key) as key:
                encrypted_email_username = winreg.QueryValueEx(key, "EmailUsername")[0]
                encrypted_email_password = winreg.QueryValueEx(key, "EmailPassword")[0]
                encryption_key = winreg.QueryValueEx(key, "EncryptionKey")[0]

            # Decrypt the credentials
            f = Fernet(encryption_key)
            return {
                "EmailUsername": f.decrypt(encrypted_email_username).decode(),
                "EmailPassword": f.decrypt(encrypted_email_password).decode(),
            }
        except WindowsError as e:
            logger.error(f"Error accessing Registry: {e}")
            logger.info("Attempting to reconfigure email settings...")
            DiskSpaceAlertService.configure_email()
            return DiskSpaceAlertService.get_email_credentials()

    # Static method to configure email settings
    @staticmethod
    def configure_email():
        email_username = input("Enter your email address (sender): ")
        email_password = getpass.getpass("Enter your email password: ")
        config.recipient_email = input("Enter recipient email address: ")
        config.smtp_server = input("Enter your SMTP server: ")
        config.smtp_port = int(input("Enter your SMTP port: "))

        # Encrypt the email credentials
        encryption_key = Fernet.generate_key()
        f = Fernet(encryption_key)
        encrypted_email_username = f.encrypt(email_username.encode())
        encrypted_email_password = f.encrypt(email_password.encode())

        try:
            # Store encrypted credentials in Windows Registry
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, config.registry_key) as key:
                winreg.SetValueEx(key, "EmailUsername", 0, winreg.REG_BINARY, encrypted_email_username)
                winreg.SetValueEx(key, "EmailPassword", 0, winreg.REG_BINARY, encrypted_email_password)
                winreg.SetValueEx(key, "EncryptionKey", 0, winreg.REG_BINARY, encryption_key)
            
            # Save updated config to file
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config.__dict__, f, indent=2)
            
            logger.info("Email configuration updated successfully")
        except WindowsError as e:
            logger.error(f"Failed to update Registry: {e}")
            raise

# Main function to handle command-line arguments
def main():
    if os.name != 'nt':
        print("This script is designed to run as a Windows service. Please modify the code to run on other operating systems.")
        sys.exit(1)

    if len(sys.argv) > 1:
        if sys.argv[1] in ['install', 'update', 'reconfigure']:
            DiskSpaceAlertService.configure_email()
        if sys.argv[1] != 'reconfigure':
            win32serviceutil.HandleCommandLine(DiskSpaceAlertService)
    else:
        print("Usage: python script.py [install|start|stop|remove|update|reconfigure]")
        print("       python script.py install - Install the service and configure email")
        print("       python script.py start - Start the service")
        print("       python script.py stop - Stop the service")
        print("       python script.py remove - Remove the service")
        print("       python script.py update - Update the service configuration")
        print("       python script.py reconfigure - Reconfigure email settings")

if __name__ == '__main__':
    main()
