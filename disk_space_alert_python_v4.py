import os
import sys
import psutil
import smtplib
import getpass
import logging
import time

import win32event  # Import the win32event module

from cryptography.fernet import Fernet
from email.message import EmailMessage

# Set up logging
logging.basicConfig(
    filename="diskspacealertservice.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s"
)

def wait_or_exit(hWaitStop, interval):
    if os.name == 'nt':
        return win32event.WaitForSingleObject(hWaitStop, interval) == win32event.WAIT_OBJECT_0
    else:
        time.sleep(interval / 1000)
        return False

if os.name == 'nt':
    import win32serviceutil
    import win32service
    import servicemanager
    import winreg

    class DiskSpaceAlertService(win32serviceutil.ServiceFramework):
        _svc_name_ = "DiskSpaceAlertService"
        _svc_display_name_ = "Disk Space Alert Service"
        _svc_description_ = "Checks local disks' free space and sends an email alert if any disk has less than 10GB of free space."

        def __init__(self, args):
            super().__init__(args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        def SvcStop(self):
            with open("startup.log", "a") as startup_log:
                startup_log.write("Script started\n")
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)

        def SvcDoRun(self):
            with open("startup.log", "a") as startup_log:
                 startup_log.write("Script started\n")
            self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
            try:
                self.main()
            except Exception as e:
                servicemanager.LogErrorMsg(str(e))
                logging.exception("An unhandled exception occurred while executing the service")

        def main(self):
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            self.run()

        def run(self):
            while not wait_or_exit(self.hWaitStop, 3600 * 1000):  # Check every hour
                disks = self.get_disks()
                for disk in disks:
                    if disk["FreeSpaceGB"] < 10:
                        try:
                            email_credentials = self.get_email_credentials()
                            computer_name = os.environ['COMPUTERNAME']
                            device_id = disk["DeviceID"]
                            free_space_gb = disk["FreeSpaceGB"]
                            username = email_credentials["EmailUsername"]
                            password = email_credentials["EmailPassword"]
                            smtp_server = email_credentials["SmtpServer"]
                            smtp_port = email_credentials["SmtpPort"]

                            self.send_alert_email(
                                computer_name=computer_name,
                                device_id=device_id,
                                free_space_gb=free_space_gb,
                                email_username=username,
                                email_password=password,
                                smtp_server=smtp_server,
                                smtp_port=smtp_port
                            )
                        except Exception as e:
                            servicemanager.LogErrorMsg(str(e))

        @staticmethod
        def get_disks():
            nt_filter = lambda p: 'cdrom' not in p.opts and p.fstype != ''
            partitions = filter(nt_filter, psutil.disk_partitions()) if os.name == 'nt' else psutil.disk_partitions()

            return [
                {
                    "DeviceID": partition.device,
                    "FreeSpaceGB": psutil.disk_usage(partition.mountpoint).free / (1024 ** 3),
                }
                for partition in partitions
            ]

        def get_email_credentials(self):
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\DiskSpaceAlertService') as key:
                    encrypted_email_username = winreg.QueryValueEx(key, "EmailUsername")[0]
                    encrypted_email_password = winreg.QueryValueEx(key, "EmailPassword")[0]
                    encryption_key = winreg.QueryValueEx(key, "EncryptionKey")[0]

                f = Fernet(encryption_key)
                return {
                    "EmailUsername": f.decrypt(encrypted_email_username).decode(),
                    "EmailPassword": f.decrypt(encrypted_email_password).decode(),
                    "SmtpServer": winreg.QueryValueEx(key, "SmtpServer")[0],
                    "SmtpPort": int(winreg.QueryValueEx(key, "SmtpPort")[0])
                }
            except FileNotFoundError as e:
                raise Exception("Cannot retrieve email credentials from registry")

        @staticmethod
        def send_alert_email(computer_name, device_id, free_space_gb, email_username, email_password, smtp_server, smtp_port):
            subject = f"Disk space alert on {computer_name}"
            body = f"The disk {device_id} on {computer_name} has {free_space_gb:.2f} GB of free space left."

            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = subject
            msg["From"] = email_username
            msg["To"] = email_username

            try:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(email_username, email_password)
                    server.send_message(msg)
            except Exception as e:
                raise Exception(f"Failed to send email: {str(e)}")

        @staticmethod
        def install_service():
            try:
                # Get email username, password, SMTP server, and port from user
                email_username = input("Enter your email address: ")
                email_password = getpass.getpass("Enter your email password: ")
                smtp_server = input("Enter your SMTP server: ")
                smtp_port = input("Enter your SMTP port: ")

                # Generate encryption key
                encryption_key = Fernet.generate_key()

                # Encrypt and store email credentials
                f = Fernet(encryption_key)
                encrypted_email_username = f.encrypt(email_username.encode())
                encrypted_email_password = f.encrypt(email_password.encode())

                key_path = r'SOFTWARE\DiskSpaceAlertService'
                with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    winreg.SetValueEx(key, "EmailUsername", 0, winreg.REG_BINARY, encrypted_email_username)
                    winreg.SetValueEx(key, "EmailPassword", 0, winreg.REG_BINARY, encrypted_email_password)
                    winreg.SetValueEx(key, "EncryptionKey", 0, winreg.REG_BINARY, encryption_key)
                    winreg.SetValueEx(key, "SmtpServer", 0, winreg.REG_SZ, smtp_server)
                    winreg.SetValueEx(key, "SmtpPort", 0, winreg.REG_SZ, smtp_port)

                # Install the service          
                win32serviceutil.InstallService(
                    pythonClassString="__main__.DiskSpaceAlertService",
                    serviceName=DiskSpaceAlertService._svc_name_,
                    displayName=DiskSpaceAlertService._svc_display_name_,
                    startType=win32service.SERVICE_AUTO_START,
                    exeArgs=f"\"{__file__}\"",  # Pass the script path as an argument
                    description=DiskSpaceAlertService._svc_description_
                )
                
                print(f"Successfully installed the {DiskSpaceAlertService._svc_display_name_}.")

            except Exception as e:
                print(f"Failed to install the service: {str(e)}")

if __name__ == '__main__':
    with open("startup.log", "a") as startup_log:
         startup_log.write("Script started\n")
    if os.name == 'nt':
        if len(sys.argv) > 1 and sys.argv[1].lower() == "install":
            DiskSpaceAlertService.install_service()
        else:
            win32serviceutil.HandleCommandLine(DiskSpaceAlertService)
    else:
        print("This script is designed to run as a Windows service. Please modify the code to run on other operating systems.")