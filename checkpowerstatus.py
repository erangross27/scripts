import win32serviceutil
import win32service
import win32event
import smtplib
import psutil

class PowerCheckService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PowerCheckService"
    _svc_display_name_ = "Power Check Service"
    _svc_description_ = "Checks the power status and sends an email if unplugged"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        while True:
            battery = psutil.sensors_battery()
            if battery.power_plugged == False:
                self.send_email()
            win32event.WaitForSingleObject(self.hWaitStop, 60000)  # Check every minute

    def send_email(self):
        sender_email = "your_email@gmail.com"
        sender_password = "your_password"
        receiver_email = "recipient_email@gmail.com"
        message = "Subject: Power source unplugged\n\nThe power source has been unplugged from your computer."

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PowerCheckService)