import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def get_disks():
    """
    Uses WMIC to get information about the local disks.
    Returns a list of dictionaries, each containing the device ID and free space in GB for a disk.
    """
    disks = os.popen("wmic logicaldisk get deviceid,freespace").read()
    disks = disks.split('\n')[1:-1]
    disks = [disk.split() for disk in disks if len(disk.split()) == 2]
    disks = [{"DeviceID": d[0], "FreeSpaceGB": round(float(d[1])/(1024**3), 2)} for d in disks]
    return disks

def send_alert_email(computer_name, disk_id, free_space, smtp_server, smtp_port, email_from, email_to, email_username, email_password):
    """
    Sends an email alert for the specified disk with less than 10GB of free space.
    """
    message = MIMEMultipart()
    message['From'] = email_from
    message['To'] = email_to
    message['Subject'] = "Low Disk Space Alert"
    body = f"{computer_name} reports that the following drive has less than 10GB of free space: {disk_id}, {free_space}GB remaining."
    message.attach(MIMEText(body, "plain"))

    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()
    smtp.login(email_username, email_password)
    smtp.sendmail(email_from, email_to, message.as_string())
    smtp.quit()

def main():
    """
    Main program that gets information about the local disks, and sends an email alert if any disk has less than 10GB of free space.
    """
    computer_name = os.environ['COMPUTERNAME']
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_from = "maayan12scomputersalerts@gmail.com"
    email_to = "maayan12scomputersalerts@gmail.com"
    email_username = "maayan12scomputersalerts@gmail.com"
    email_password = "alwicjdyyxwxnepz"
    disks = get_disks()
    for disk in disks:
        if disk["FreeSpaceGB"] < 10:
            send_alert_email(computer_name, disk["DeviceID"], disk["FreeSpaceGB"], smtp_server, smtp_port, email_from, email_to, email_username, email_password)

if __name__ == "__main__":
    main()
