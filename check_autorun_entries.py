import winreg

def check_autorun_entries():
    # Registry key for autorun entries
    autorun_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        # Open the registry key
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, autorun_key, 0, winreg.KEY_READ)
        
        # Iterate through values
        index = 0
        while True:
            try:
                name, data, type = winreg.EnumValue(key, index)
                print(f"Autorun entry found: {name} -> {data}")
                index += 1
            except WindowsError:
                # No more values
                break
        
        winreg.CloseKey(key)
    except WindowsError:
        print("Failed to access the registry key.")

if __name__ == "__main__":
    check_autorun_entries()
