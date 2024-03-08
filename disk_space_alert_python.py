import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# get the name of the local computer
computerName = os.environ['COMPUTERNAME']

# specify the SMTP server and port to use for sending email
smtpServer = "smtp.gmail.com"
smtpPort = 587

# specify the email addresses and credentials to use for sending email
emailFrom = "Look at the email address"
emailTo = "look at the email address"
emailUsername = "look at the email address"
emailPassword = "look at the password"

# use WMIC to get information about the local disks
disks = os.popen("wmic logicaldisk get deviceid,freespace").read()

# split the WMIC output into lines and skip the header and footer
disks = disks.split('\n')[1:-1]

# split each line of the output into device ID and free space values
# and filter out any lines that do not contain exactly two values
disks = [disk.split() for disk in disks if len(disk.split()) == 2]

# convert the free space value to GB and create a dictionary with the
# device ID and free space in GB for each disk
disks = [{"DeviceID": d[0], "FreeSpaceGB": round(float(d[1])/(1024**3), 2)} for d in disks]

# loop through each disk and send an email alert if the free space is less than 10 GB
for disk in disks:
    if disk["FreeSpaceGB"] < 10:
        # create a new email message
        message = MIMEMultipart()
        message['From'] = emailFrom
        message['To'] = emailTo
        message['Subject'] = "Low Disk Space Alert"
        body = f"{computerName} reports that the following drive has less than 10GB of free space: {disk['DeviceID']}, {disk['FreeSpaceGB']}GB remaining."
        message.attach(MIMEText(body, "plain"))
        
        # connect to the SMTP server, authenticate with the email credentials, and send the email
        smtp = smtplib.SMTP(smtpServer, smtpPort)
        smtp.starttls()
        smtp.login(emailUsername, emailPassword)
        smtp.sendmail(emailFrom, emailTo, message.as_string())
        smtp.quit()
