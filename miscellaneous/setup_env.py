"""
This script handles setup env.
"""

import os
import winreg
import ctypes
import logging
import json
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EnvironmentManager:
    """
    Manages environment.
    """
    def __init__(self):
        """
        Special method __init__.
        """
        self.config_file = 'env_config.json'
        self.required_vars = {
            'ANTHROPIC_API_KEY': '',
            'SHUTTERSTOCK_CLIENT_ID': '',
            'SHUTTERSTOCK_CLIENT_SECRET': '',
            'DOWNLOAD_FOLDER': str(Path.home() / 'Downloads' / 'shutterstock_images'),
            'MAX_RETRIES': '3',
            'RETRY_DELAY': '5',
            'BATCH_SIZE': '10',
            'ANTHROPIC_MODEL': 'claude-3-sonnet-20240229'
        }

    def set_windows_env_variable(self, name: str, value: str) -> str:
        """
        Set Windows environment variable using registry and broadcast change.
        
        Args:
            name: Environment variable name
            value: Environment variable value
            
        Returns:
            Current value of the environment variable
        """
        try:
            # Update for the current process
            os.environ[name] = value

            # Create or open the key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
            
            # Set the value
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            
            # Close the key
            winreg.CloseKey(key)
            
            # Broadcast WM_SETTINGCHANGE message
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            SMTO_ABORTIFHUNG = 0x0002
            result = ctypes.c_long()
            SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
            SendMessageTimeoutW(
                HWND_BROADCAST, 
                WM_SETTINGCHANGE, 
                0, 
                'Environment', 
                SMTO_ABORTIFHUNG, 
                5000, 
                ctypes.byref(result)
            )
            
            logging.info(f"Environment variable '{name}' set to '{value}' in registry and current process")
            
            # Verify the change
            new_value = winreg.QueryValueEx(
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_READ), 
                name
            )[0]
            
            if new_value != value:
                logging.warning(f"Registry value mismatch. Expected: {value}, Got: {new_value}")
                
            # Check current process environment
            if os.environ.get(name) != value:
                logging.warning(f"Process environment mismatch. Expected: {value}, Got: {os.environ.get(name)}")
                
        except Exception as e:
            logging.error(f"Failed to set environment variable '{name}': {str(e)}")
            raise
            
        # Return the current value for verification
        return os.environ.get(name)

    def load_existing_config(self):
        """Load existing configuration if available."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.required_vars.update(saved_config)
                    logging.info("Loaded existing configuration")
        except Exception as e:
            logging.error(f"Error loading config file: {e}")

    def save_config(self):
        """Save configuration to file."""
        try:
            # Save only sensitive variables
            sensitive_vars = {
                'ANTHROPIC_API_KEY': self.required_vars['ANTHROPIC_API_KEY'],
                'SHUTTERSTOCK_CLIENT_ID': self.required_vars['SHUTTERSTOCK_CLIENT_ID'],
                'SHUTTERSTOCK_CLIENT_SECRET': self.required_vars['SHUTTERSTOCK_CLIENT_SECRET']
            }
            with open(self.config_file, 'w') as f:
                json.dump(sensitive_vars, f, indent=4)
            logging.info("Configuration saved successfully")
        except Exception as e:
            logging.error(f"Error saving config file: {e}")

    def get_user_input(self):
        """Get user input for required variables."""
        print("\nPlease enter the following configuration values:")
        print("(Press Enter to keep existing value if shown)\n")

        for key in self.required_vars:
            current_value = self.required_vars[key]
            if key in ['ANTHROPIC_API_KEY', 'SHUTTERSTOCK_CLIENT_ID', 'SHUTTERSTOCK_CLIENT_SECRET']:
                display_value = '*' * 8 if current_value else ''
            else:
                display_value = current_value

            if display_value:
                user_input = input(f"{key} [{display_value}]: ")
            else:
                user_input = input(f"{key}: ")

            if user_input:
                self.required_vars[key] = user_input

    def set_environment_variables(self):
        """Set all environment variables using the proven method."""
        success = True
        for var_name, var_value in self.required_vars.items():
            try:
                set_value = self.set_windows_env_variable(var_name, var_value)
                if set_value != var_value:
                    logging.error(f"Failed to verify {var_name}")
                    success = False
            except Exception as e:
                logging.error(f"Failed to set {var_name}: {e}")
                success = False
        return success

    def create_download_folder(self):
        """Create the download folder if it doesn't exist."""
        download_path = Path(self.required_vars['DOWNLOAD_FOLDER'])
        try:
            download_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Download folder created: {download_path}")
        except Exception as e:
            logging.error(f"Error creating download folder: {e}")

def main():
    """
    Main.
    """
    try:
        manager = EnvironmentManager()
        
        # Load existing configuration
        manager.load_existing_config()
        
        # Get user input
        manager.get_user_input()
        
        # Set environment variables
        if manager.set_environment_variables():
            # Save configuration
            manager.save_config()
            
            # Create download folder
            manager.create_download_folder()
            
            print("\nSetup completed successfully!")
            print("You may need to restart your applications for all changes to take effect.")
        else:
            print("\nSetup failed. Please check the logs for details.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print("\nSetup failed. Please check the logs for details.")

if __name__ == "__main__":
    main()