import os
import time
import sys
import psutil
import smtplib
import winreg
import getpass
import base64

from email.message import EmailMessage
from cryptography.fernet import Fernet

if os.name == 'nt':
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager

# The service class
class DiskSpaceAlertService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DiskSpaceAlertService"
    _svc_display_name_ = "Disk Space Alert Service"
    _svc_description_ = "Checks the local disks' free space and sends an email alert if any disk has less than 10GB of free space."

    # The constructor of the class
    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    # Called when the service is first started
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
    # The main function of the service
    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.run()

        # The main loop of the service
    def run(self):
        while True:
            disks = self.get_disks()
            for disk in disks:
                if disk["FreeSpaceGB"] < 10:
                    email_credentials = self.get_email_credentials()
                    self.send_alert_email(
                        computer_name=os.environ['COMPUTERNAME'],
                        device_id=disk["DeviceID"],
                        free_space_gb=disk["FreeSpaceGB"],
                        email_username=email_credentials["EmailUsername"],
                        email_password=email_credentials["EmailPassword"]
                    )
            time.sleep(3600)

    # Get the local disks' free space
    def get_disks(self):
        disks = []
        for partition in psutil.disk_partitions():
            if os.name == 'nt':
                if 'cdrom' in partition.opts or partition.fstype == '':
                    # skip CD-ROM drives with no disk inserted
                    continue
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "DeviceID": partition.device,
                "FreeSpaceGB": usage.free / 1024 / 1024 / 1024,
            })
        return disks
    # Send an email alert
    def send_alert_email(self, computer_name, device_id, free_space_gb, email_username, email_password):
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        email_from = email_username
        email_to = email_username

        subject = f"Disk space alert on {computer_name}"
        body = f"The disk {device_id} on {computer_name} has {free_space_gb:.2f} GB of free space left."

        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = email_from
        msg["To"] = email_to

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_username, email_password)
        server.send_message(msg)
        server.quit()
        # Generate a new encryption key
    @staticmethod
    def generate_key():
        return Fernet.generate_key()
        # Encrypt data
    @staticmethod
    def encrypt_data(key, data):
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    # Decrypt data
    @staticmethod
    def decrypt_data(key, data):
        f = Fernet(key)
        encrypted_data = base64.urlsafe_b64decode(data.encode())
        return f.decrypt(encrypted_data).decode()
    # Save the encryption key and the email credentials in the Windows registry
    @classmethod
    def save_credentials(cls, key, username, password):
        encrypted_username = cls.encrypt_data(key, username)
        encrypted_password = cls.encrypt_data(key, password)

        registry_key = winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE,
            fr"SYSTEM\CurrentControlSet\Services\{cls._svc_name_}\Parameters"
        )
        winreg.SetValueEx(registry_key, "EncryptionKey", 0, winreg.REG_SZ, key.decode())
        winreg.SetValueEx(registry_key, "EmailUsername", 0, winreg.REG_SZ, encrypted_username)
        winreg.SetValueEx(registry_key, "EmailPassword", 0, winreg.REG_SZ, encrypted_password)
        winreg.CloseKey(registry_key)
    # Get the email credentials from the Windows registry
    @classmethod
    def get_email_credentials(cls):
        registry_key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
            fr"SYSTEM\CurrentControlSet\Services\{cls._svc_name_}\Parameters"
        )
        encryption_key, _ = winreg.QueryValueEx(registry_key, "EncryptionKey")
        encrypted_username, _ = winreg.QueryValueEx(registry_key, "EmailUsername")
        encrypted_password, _ = winreg.QueryValueEx(registry_key, "EmailPassword")
        winreg.CloseKey(registry_key)

        email_username = cls.decrypt_data(encryption_key.encode(), encrypted_username)
        email_password = cls.decrypt_data(encryption_key.encode(), encrypted_password)

        return {"EmailUsername": email_username, "EmailPassword": email_password}


def prompt_for_credentials():
    email_username = input("Enter email username: ")
    encrypted_email_username = DiskSpaceAlertService.encrypt_data(encryption_key, email_username)
    del email_username

    if hasattr(sys, 'frozen'):
        email_password = input("Enter email password: ")
    else:
        email_password = getpass.getpass("Enter email password: ")
    encrypted_email_password = DiskSpaceAlertService.encrypt_data(encryption_key, email_password)
    del email_password

    return encrypted_email_username, encrypted_email_password
# Install the service
def install_service():
    encrypted_email_username, encrypted_email_password = prompt_for_credentials()

    DiskSpaceAlertService.save_credentials(encryption_key, encrypted_email_username, encrypted_email_password)
    win32serviceutil.InstallServiceWithParameters(
        pythonClassString="PythonService",
        serviceName=DiskSpaceAlertService._svc_name_,
        displayName=DiskSpaceAlertService._svc_display_name_,
        startType=win32service.SERVICE_AUTO_START,
        exeName=None,
        exeArgs=None
    )
    print("Service installed successfully")
# The main function of the script
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == "install":
        encryption_key = DiskSpaceAlertService.generate_key()
        install_service()
    else:
        win32serviceutil.HandleCommandLine(DiskSpaceAlertService)







