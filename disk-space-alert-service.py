import sys
import os

def check_dependencies():
    required_modules = ['psutil', 'win32event', 'win32service', 'win32serviceutil', 'servicemanager', 'winreg', 'cryptography']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Error: The following required modules are missing:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install these modules using pip:")
        print(f"pip install {' '.join(missing_modules)}")
        return False
    return True

if not check_dependencies():
    sys.exit(1)

import psutil
import smtplib
import getpass
import logging
import time
import win32event
import win32service
import win32serviceutil
import servicemanager
import winreg
import json
from cryptography.fernet import Fernet
from email.message import EmailMessage

# Add the script's directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Logging configuration
log_file = os.path.join(script_dir, "diskspacealertservice.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s"
)

CONFIG_FILE = os.path.join(script_dir, "config.json")

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "check_interval": 3600,
            "min_free_space_gb": 10,
            "registry_key": r'SOFTWARE\DiskSpaceAlertService'
        }

config = load_config()

class DiskSpaceAlertService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DiskSpaceAlertService"
    _svc_display_name_ = "Disk Space Alert Service"
    _svc_description_ = "Checks local disks' free space and sends an email alert if any disk has less than the configured free space."

    def __init__(self, args):
        try:
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.is_alive = True
            logging.info("Service initialized")
        except Exception as e:
            logging.exception("Error during service initialization")
            raise

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
        logging.info("Service stop requested")

    def SvcDoRun(self):
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            self.main()
        except Exception as e:
            logging.exception("Error during service execution")
            self.SvcStop()

    def main(self):
        logging.info("Service started")
        while self.is_alive:
            try:
                disks = self.get_disks()
                for disk in disks:
                    if disk["FreeSpaceGB"] < config["min_free_space_gb"]:
                        self.send_alert(disk)
                
                # Wait for the specified interval or service stop signal
                win32event.WaitForSingleObject(self.hWaitStop, config["check_interval"] * 1000)
            except Exception as e:
                logging.exception("Error in main service loop")
                time.sleep(60)  # Wait a minute before retrying

    @staticmethod
    def get_disks():
        try:
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
            logging.exception("Error getting disk information")
            return []

    def send_alert(self, disk):
        try:
            creds = self.get_email_credentials()
            computer_name = os.environ.get('COMPUTERNAME', 'Unknown Computer')
            
            subject = f"Disk space alert on {computer_name}"
            body = f"The disk {disk['DeviceID']} on {computer_name} has {disk['FreeSpaceGB']:.2f} GB of free space left."

            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = subject
            msg["From"] = creds["EmailUsername"]
            msg["To"] = creds["RecipientEmail"]

            with smtplib.SMTP(creds["SmtpServer"], creds["SmtpPort"]) as server:
                server.starttls()
                server.login(creds["EmailUsername"], creds["EmailPassword"])
                server.send_message(msg)
            
            logging.info(f"Alert sent for disk {disk['DeviceID']}")
        except Exception as e:
            logging.exception("Error sending alert email")

    @staticmethod
    def get_email_credentials():
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, config["registry_key"]) as key:
                encrypted_email_username = winreg.QueryValueEx(key, "EmailUsername")[0]
                encrypted_email_password = winreg.QueryValueEx(key, "EmailPassword")[0]
                encryption_key = winreg.QueryValueEx(key, "EncryptionKey")[0]
                recipient_email = winreg.QueryValueEx(key, "RecipientEmail")[0]
                smtp_server = winreg.QueryValueEx(key, "SmtpServer")[0]
                smtp_port = winreg.QueryValueEx(key, "SmtpPort")[0]

            f = Fernet(encryption_key)
            return {
                "EmailUsername": f.decrypt(encrypted_email_username).decode(),
                "EmailPassword": f.decrypt(encrypted_email_password).decode(),
                "SmtpServer": smtp_server,
                "SmtpPort": int(smtp_port),
                "RecipientEmail": recipient_email
            }
        except WindowsError as e:
            logging.error(f"Error accessing Registry: {e}")
            logging.info("Attempting to reconfigure email settings...")
            DiskSpaceAlertService.configure_email()
            return DiskSpaceAlertService.get_email_credentials()

    @staticmethod
    def configure_email():
        email_username = input("Enter your email address (sender): ")
        email_password = getpass.getpass("Enter your email password: ")
        recipient_email = input("Enter recipient email address: ")
        smtp_server = input("Enter your SMTP server: ")
        smtp_port = input("Enter your SMTP port: ")

        encryption_key = Fernet.generate_key()
        f = Fernet(encryption_key)
        encrypted_email_username = f.encrypt(email_username.encode())
        encrypted_email_password = f.encrypt(email_password.encode())

        try:
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, config["registry_key"]) as key:
                winreg.SetValueEx(key, "EmailUsername", 0, winreg.REG_BINARY, encrypted_email_username)
                winreg.SetValueEx(key, "EmailPassword", 0, winreg.REG_BINARY, encrypted_email_password)
                winreg.SetValueEx(key, "EncryptionKey", 0, winreg.REG_BINARY, encryption_key)
                winreg.SetValueEx(key, "SmtpServer", 0, winreg.REG_SZ, smtp_server)
                winreg.SetValueEx(key, "SmtpPort", 0, winreg.REG_SZ, smtp_port)
                winreg.SetValueEx(key, "RecipientEmail", 0, winreg.REG_SZ, recipient_email)
            logging.info("Email configuration updated successfully")
        except WindowsError as e:
            logging.error(f"Failed to update Registry: {e}")
            raise

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