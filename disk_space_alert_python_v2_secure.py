import os
import pickle
import smtplib
import ssl
import subprocess
import time
import sys
from cryptography.fernet import Fernet


CREDENTIALS_FILE = "email_credentials.pickle"


def get_disks():
    """
    Returns a list of dictionaries containing information about the local disks.
    """
    disks = subprocess.check_output("wmic logicaldisk get deviceid,freespace").decode("utf-8")
    disks = [d.split() for d in disks.splitlines() if len(d.split()) == 2 and d.split()[0] != "DeviceID"]
    disks = [{"DeviceID": d[0], "FreeSpaceGB": round(float(d[1]) / (1024**3), 2)} for d in disks if int(d[1]) > 0]
    return disks


def send_alert_email(computer_name, device_id, free_space_gb, smtp_server, smtp_port, email_from, email_to, email_username, email_password):
    """
    Sends an email alert if any disk has less than 10GB of free space.
    """
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls(context=context)
        smtp.login(email_username, email_password)
        subject = "Low Disk Space Alert"
        body = f"{computer_name} reports that the following drive has less than 10GB of free space: {device_id}, {free_space_gb}GB remaining."
        message = f"Subject: {subject}\n\n{body}"
        smtp.sendmail(email_from, email_to, message)




def main(sleep_time):
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
    while True:
        for disk in disks:
            if disk["FreeSpaceGB"] < 10:
                send_alert_email(computer_name, disk["DeviceID"], disk["FreeSpaceGB"], smtp_server, smtp_port, email_from, email_to, email_username, email_password)
        time.sleep(sleep_time)

if __name__ == '__main__':
    sleep_time = int(sys.argv[1])
    main(sleep_time)


