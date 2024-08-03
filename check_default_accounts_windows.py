import subprocess
import sys

def check_default_accounts():
    # List of common default account names
    default_accounts = ['Administrator', 'Guest', 'DefaultAccount']
    
    for account in default_accounts:
        try:
            # Run 'net user' command to check if the account exists
            result = subprocess.run(['net', 'user', account], 
                                    capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                print(f"Default account found: {account}")
            else:
                print(f"Default account not found: {account}")
        except subprocess.CalledProcessError as e:
            print(f"Error checking account {account}: {e}")
        except Exception as e:
            print(f"Unexpected error checking account {account}: {e}")

if __name__ == "__main__":
    check_default_accounts()
