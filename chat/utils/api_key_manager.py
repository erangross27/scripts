import os
import winreg
import ctypes
import logging

def get_api_key():
    return os.getenv('ANTHROPIC_API_KEY')

def set_api_key(api_key):
    os.environ['ANTHROPIC_API_KEY'] = api_key
    set_windows_env_variable('ANTHROPIC_API_KEY', api_key)

def set_windows_env_variable(name, value):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Environment')
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_long()
        SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
        SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, u'Environment', SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))
    except WindowsError:
        logging.error(f"Failed to set environment variable '{name}'")