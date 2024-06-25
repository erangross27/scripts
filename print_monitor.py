import win32print
import win32con
import time
import tkinter as tk
from tkinter import simpledialog
import ctypes, sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("This script must be run with administrator privileges.")
    sys.exit(1)

def get_password():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    password = simpledialog.askstring("Password", "Enter password to print:", show='*')
    return password

def check_password(entered_password):
    # Replace this with your actual password checking logic
    correct_password = "1234"
    return entered_password == correct_password

def monitor_prints():
    print("Print monitoring started...")
    
    # Get the default printer
    printer_name = win32print.GetDefaultPrinter()
    print(f"Monitoring printer: {printer_name}")
    
    # Open the printer
    printer_handle = win32print.OpenPrinter(printer_name)
    
    # Keep track of the last job ID we've seen
    last_job_id = 0
    
    while True:
        try:
            jobs = win32print.EnumJobs(printer_handle, 0, 999)
            for job in jobs:
                job_id = job['JobId']
                if job_id > last_job_id:
                    print(f"New print job detected! Job ID: {job_id}, Document: {job['pDocument']}")
                    
                    # Continuously pause the job
                    password_correct = False
                    while not password_correct:
                        win32print.SetJob(printer_handle, job_id, 0, None, win32print.JOB_CONTROL_PAUSE)
                        print(f"Job {job_id} paused.")
                        
                        # Prompt for password
                        password = get_password()
                        
                        if password is None:
                            print("Print cancelled by user.")
                            win32print.SetJob(printer_handle, job_id, 0, None, win32print.JOB_CONTROL_DELETE)
                            print(f"Job {job_id} deleted.")
                            break
                        elif check_password(password):
                            print("Password correct. Resuming print job...")
                            win32print.SetJob(printer_handle, job_id, 0, None, win32print.JOB_CONTROL_RESUME)
                            print(f"Job {job_id} resumed.")
                            password_correct = True
                        else:
                            print("Incorrect password. Job remains paused.")
                    
                    if not password_correct:
                        win32print.SetJob(printer_handle, job_id, 0, None, win32print.JOB_CONTROL_DELETE)
                        print(f"Job {job_id} deleted due to incorrect password attempts.")
                    
                    last_job_id = job_id
            
            time.sleep(0.5)  # Check more frequently
            
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(1)

if __name__ == "__main__":
    monitor_prints()