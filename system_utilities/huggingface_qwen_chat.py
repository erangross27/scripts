import os
import sys
import json
import requests
import logging
from typing import List, Dict, Any
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qwen_chat.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

API_URL = "https://router.huggingface.co/v1/chat/completions"

class QwenChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Qwen Chat")
        self.root.geometry("800x600")
        
        # Get HF token from environment or ask user
        self.hf_token = os.environ.get('HF_KEY')
        logging.info(f"Environment variable HF_KEY present: {self.hf_token is not None}")
        if not self.hf_token:
            logging.warning("HF_KEY environment variable not found")
            self.ask_for_token()
        else:
            logging.info("HF_KEY environment variable found")
        
        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
        }
        logging.info("Headers configured with bearer token")
        
        # Chat history
        self.chat_history: List[Dict[str, str]] = []
        
        # Setup UI
        self.setup_ui()
        logging.info("Application initialized successfully")
        
    def ask_for_token(self):
        """Ask user for Hugging Face token"""
        logging.info("Prompting user for Hugging Face token")
        token_window = tk.Toplevel(self.root)
        token_window.title("Enter Hugging Face Token")
        token_window.geometry("400x150")
        token_window.grab_set()
        
        tk.Label(token_window, text="Please enter your Hugging Face token:").pack(pady=10)
        
        token_entry = tk.Entry(token_window, width=50, show="*")
        token_entry.pack(pady=5)
        token_entry.focus()
        
        def save_token():
            self.hf_token = token_entry.get().strip()
            if self.hf_token:
                os.environ['HF_KEY'] = self.hf_token
                self.headers = {
                    "Authorization": f"Bearer {self.hf_token}",
                }
                logging.info("User entered token and saved to HF_KEY environment variable")
                token_window.destroy()
            else:
                logging.error("User attempted to save empty token")
                messagebox.showerror("Error", "Token cannot be empty!")
                
        tk.Button(token_window, text="Save Token", command=save_token).pack(pady=10)
        token_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(1))
        
    def setup_ui(self):
        """Setup the user interface"""
        logging.info("Setting up user interface")
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(main_frame, state='disabled', wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X)
        
        # User input
        self.user_input = tk.Text(input_frame, height=4)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Control-Return>", self.send_message)
        
        # Send button
        send_button = ttk.Button(input_frame, text="Send (Ctrl+Enter)", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        logging.info("User interface setup completed")
        
    def query(self, payload):
        """Send query to Hugging Face API"""
        logging.info(f"Sending request to {API_URL}")
        logging.debug(f"Request payload: {payload}")
        try:
            response = requests.post(API_URL, headers=self.headers, json=payload, timeout=30)
            logging.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 401:
                logging.error("Authentication failed - check your HF_KEY token")
                messagebox.showerror("Authentication Error", "Authentication failed. Please check your HF_KEY token.")
                return None
            elif response.status_code == 403:
                logging.error("Forbidden - you may need to purchase tokens or upgrade your account")
                messagebox.showerror("Access Forbidden", "Access denied. You may need to purchase tokens or upgrade your account.")
                return None
            elif response.status_code == 429:
                logging.error("Rate limit exceeded - too many requests")
                messagebox.showerror("Rate Limit", "Rate limit exceeded. Please wait before sending more requests.")
                return None
                
            response.raise_for_status()
            result = response.json()
            logging.debug(f"Response JSON: {result}")
            return result
        except requests.exceptions.Timeout:
            logging.error("Request timeout - the server took too long to respond")
            messagebox.showerror("Timeout Error", "Request timeout. The server took too long to respond.")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to connect to API: {str(e)}")
            messagebox.showerror("API Error", f"Failed to connect to API: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse response: {str(e)}")
            messagebox.showerror("JSON Error", f"Failed to parse response: {str(e)}")
            return None
            
    def send_message(self, event=None):
        """Send message to Qwen model"""
        logging.info("Sending message to Qwen model")
        # Get user input
        user_message = self.user_input.get("1.0", tk.END).strip()
        if not user_message:
            logging.warning("User tried to send empty message")
            return
            
        # Clear input field
        self.user_input.delete("1.0", tk.END)
        
        # Add user message to chat history
        self.chat_history.append({"role": "user", "content": user_message})
        self.display_message("You", user_message)
        logging.info(f"User message added to history: {user_message}")
        
        # Update status
        self.status_var.set("Thinking...")
        self.root.update()
        logging.info("Updated status to 'Thinking...'")
        
        # Prepare payload with the correct model name
        payload = {
            "messages": self.chat_history,
            "model": "Qwen/Qwen3-Coder-480B-A35B-Instruct"
        }
        logging.debug(f"Prepared payload: {payload}")
        
        # Send request
        response = self.query(payload)
        
        if response and "choices" in response and len(response["choices"]) > 0:
            assistant_message = response["choices"][0]["message"]["content"]
            logging.info("Successfully received response from Qwen model")
            
            # Add assistant message to chat history
            self.chat_history.append({"role": "assistant", "content": assistant_message})
            self.display_message("Qwen", assistant_message)
            self.status_var.set("Ready")
            logging.info("Updated UI with Qwen response")
        else:
            error_msg = "Failed to get response from Qwen"
            logging.error("Failed to get response from Qwen")
            self.display_message("System", error_msg)
            self.status_var.set("Error")
            
    def display_message(self, sender, message):
        """Display message in chat window"""
        logging.debug(f"Displaying message from {sender}")
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

def main():
    logging.info("Starting Qwen Chat Application")
    root = tk.Tk()
    app = QwenChatApp(root)
    root.mainloop()
    logging.info("Qwen Chat Application closed")

if __name__ == "__main__":
    main()