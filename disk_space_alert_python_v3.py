import os
import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import psutil
import smtplib
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
                    self.send_alert_email(
                        computer_name=os.environ['COMPUTERNAME'],
                        device_id=disk["DeviceID"],
                        free_space_gb=disk["FreeSpaceGB"]
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
    def send_alert_email(self, computer_name, device_id, free_space_gb):
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        email_from = "maayan12scomputersalerts@gmail.com"
        email_to = "maayan12scomputersalerts@gmail.com"
        email_username = "maayan12scomputersalerts@gmail.com"
        email_password = "alwicjdyyxwxnepz"

        subject = f"Disk space alert on {computer_name}"
        body = f"The disk {device_id} on {computer_name} has {free_space_gb:.2f} GB of free space left."

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_username, email_password)
        server.sendmail(email_from, email_to, f"Subject: {subject}\n\n{body}")
        server.quit()


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(DiskSpaceAlertService)
