#!/usr/bin/env python3
"""
VoidLink Client - Secure Terminal-Based Chat and File Transfer Client
"""

import socket
import threading
import json
import os
import time
import sys
import getpass
import argparse
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any

# Check if we're in the client directory or the main directory
if os.path.exists("encryption.py"):
    # We're in the main directory, import directly
    from encryption import encrypt_message, decrypt_message
else:
    # We might be in a client-only directory, try to import from parent
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from encryption import encrypt_message, decrypt_message
    except ImportError:
        # Create local versions of encryption functions
        from Crypto.Cipher import AES
        from Crypto.Protocol.KDF import PBKDF2
        from Crypto.Random import get_random_bytes
        
        # Default key for client-only mode (should be replaced with proper key exchange)
        DEFAULT_KEY = b'voidlink_default_encryption_key_12345'
        DEFAULT_SALT = b'voidlink_salt'
        
        def get_encryption_key():
            """Get encryption key for client-only mode"""
            # In a real implementation, this would use proper key exchange
            password = os.environ.get("VOIDLINK_KEY_PASSWORD", "voidlink_default_password")
            key = PBKDF2(password, DEFAULT_SALT, dkLen=32)
            return key, DEFAULT_SALT
        
        KEY, SALT = get_encryption_key()
        
        def encrypt_message(message):
            """Encrypt a message using AES-256"""
            if isinstance(message, dict):
                message = json.dumps(message)
            
            # Convert to bytes if string
            if isinstance(message, str):
                message = message.encode('utf-8')
            
            # Create cipher
            cipher = AES.new(KEY, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(message)
            
            # Combine nonce, tag, and ciphertext
            encrypted_data = cipher.nonce + tag + ciphertext
            
            # Return base64 encoded string
            return base64.b64encode(encrypted_data)
        
        def decrypt_message(encrypted_message):
            """Decrypt an encrypted message"""
            try:
                # Decode base64
                data = base64.b64decode(encrypted_message)
                
                # Extract components
                nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
                
                # Create cipher
                cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)
                
                # Decrypt
                decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
                
                # Try to decode as JSON
                try:
                    return json.loads(decrypted_data.decode('utf-8'))
                except json.JSONDecodeError:
                    # Return as string if not valid JSON
                    return decrypted_data.decode('utf-8')
                
            except Exception as e:
                print(f"Decryption error: {str(e)}")
                return None

# Constants
CONFIG_FILE = "client_config.json"
CHAT_HISTORY_DIR = "chat_history"
DOWNLOADS_DIR = "downloads"

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

# Default configuration
DEFAULT_CONFIG = {
    "server_host": "localhost",
    "server_port": 5000,
    "username": "",
    "auto_reconnect": True,
    "save_history": True,
    "download_dir": DOWNLOADS_DIR,
    "theme": {
        "system_msg": "cyan",
        "user_msg": "green",
        "other_msg": "white",
        "error_msg": "red",
        "notification": "yellow"
    }
}

# Global variables
client_socket = None
connected = False
message_lock = threading.Lock()
config = DEFAULT_CONFIG.copy()
current_user = None

def ensure_dirs():
    """Ensure necessary directories exist"""
    if not os.path.exists(CHAT_HISTORY_DIR):
        os.makedirs(CHAT_HISTORY_DIR)
    
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

def load_config():
    """Load client configuration"""
    global config
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                loaded_config = json.load(file)
                # Update default config with loaded values
                config.update(loaded_config)
        except Exception as e:
            print(f"{Colors.RED}Error loading configuration: {str(e)}{Colors.RESET}")
    else:
        # Save default config
        save_config()

def save_config():
    """Save client configuration"""
    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        print(f"{Colors.RED}Error saving configuration: {str(e)}{Colors.RESET}")

def connect_to_server():
    """Connect to the VoidLink server"""
    global client_socket, connected
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((config["server_host"], config["server_port"]))
        connected = True
        return True
    except Exception as e:
        print(f"{Colors.RED}Error connecting to server: {str(e)}{Colors.RESET}")
        connected = False
        return False

def authenticate():
    """Authenticate with the server"""
    global current_user
    
    # Get username from config or prompt
    username = config.get("username", "")
    if not username:
        username = input("Username: ")
    
    # Always prompt for password
    password = getpass.getpass("Password: ")
    
    # Save username to config if successful
    config["username"] = username
    save_config()
    
    # Create authentication message
    auth_data = {
        "username": username,
        "password": password
    }
    
    # Send encrypted authentication data
    encrypted_auth = encrypt_message(json.dumps(auth_data))
    client_socket.send(encrypted_auth)
    
    # Wait for response
    try:
        response = client_socket.recv(4096)
        decrypted_response = decrypt_message(response)
        
        if isinstance(decrypted_response, dict):
            if decrypted_response.get("type") == "error":
                print(f"{Colors.RED}Authentication failed: {decrypted_response.get('content')}{Colors.RESET}")
                return False
            elif decrypted_response.get("type") == "system":
                print(f"{Colors.GREEN}Authentication successful!{Colors.RESET}")
                current_user = username
                return True
        else:
            print(f"{Colors.RED}Unexpected response from server{Colors.RESET}")
            return False
    except Exception as e:
        print(f"{Colors.RED}Error during authentication: {str(e)}{Colors.RESET}")
        return False

def receive_messages():
    """Receive and process messages from the server"""
    global connected
    
    while connected:
        try:
            # Receive encrypted message
            encrypted_data = client_socket.recv(4096)
            if not encrypted_data:
                print(f"{Colors.RED}Connection to server lost{Colors.RESET}")
                connected = False
                break
            
            # Decrypt message
            message_data = decrypt_message(encrypted_data)
            
            if not message_data:
                continue
            
            # Process message based on type
            if isinstance(message_data, dict):
                message_type = message_data.get("type", "message")
                
                if message_type == "message":
                    # Regular chat message
                    sender = message_data.get("sender", "Unknown")
                    content = message_data.get("content", "")
                    timestamp = message_data.get("timestamp", time.time())
                    time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
                    
                    with message_lock:
                        if sender == current_user:
                            color = getattr(Colors, config["theme"]["user_msg"].upper(), Colors.GREEN)
                        else:
                            color = getattr(Colors, config["theme"]["other_msg"].upper(), Colors.WHITE)
                        print(f"{Colors.GRAY}[{time_str}] {color}{sender}: {content}{Colors.RESET}")
                
                elif message_type == "system":
                    # System message
                    content = message_data.get("content", "")
                    color = getattr(Colors, config["theme"]["system_msg"].upper(), Colors.CYAN)
                    with message_lock:
                        print(f"{color}[SYSTEM] {content}{Colors.RESET}")
                
                elif message_type == "notification":
                    # Notification message
                    content = message_data.get("content", "")
                    color = getattr(Colors, config["theme"]["notification"].upper(), Colors.YELLOW)
                    with message_lock:
                        print(f"{color}[NOTIFICATION] {content}{Colors.RESET}")
                
                elif message_type == "error":
                    # Error message
                    content = message_data.get("content", "")
                    color = getattr(Colors, config["theme"]["error_msg"].upper(), Colors.RED)
                    with message_lock:
                        print(f"{color}[ERROR] {content}{Colors.RESET}")
                
                elif message_type == "file_ready":
                    # Server is ready to receive a file
                    filename = message_data.get("filename", "")
                    with message_lock:
                        print(f"{Colors.CYAN}[FILE] Server is ready to receive file: {filename}{Colors.RESET}")
                
                elif message_type == "command_response":
                    # Response to a command
                    command = message_data.get("command", "")
                    data = message_data.get("data", [])
                    
                    with message_lock:
                        print(f"{Colors.CYAN}[COMMAND] Response for '{command}':{Colors.RESET}")
                        if isinstance(data, list):
                            for item in data:
                                print(f"  - {item}")
                        else:
                            print(f"  {data}")
            
            else:
                # Plain text message
                with message_lock:
                    print(f"{Colors.WHITE}{message_data}{Colors.RESET}")
            
            # Save message to history if enabled
            if config.get("save_history", True):
                save_message_to_history(message_data)
        
        except Exception as e:
            print(f"{Colors.RED}Error receiving message: {str(e)}{Colors.RESET}")
            connected = False
            break

def send_message(message_text):
    """Send a message to the server"""
    if not connected or not client_socket:
        print(f"{Colors.RED}Not connected to server{Colors.RESET}")
        return False
    
    try:
        # Create message object
        message = {
            "type": "message",
            "content": message_text,
            "timestamp": time.time()
        }
        
        # Encrypt and send
        encrypted_message = encrypt_message(json.dumps(message))
        client_socket.send(encrypted_message)
        return True
    
    except Exception as e:
        print(f"{Colors.RED}Error sending message: {str(e)}{Colors.RESET}")
        return False

def send_file(filepath):
    """Send a file to the server"""
    if not connected or not client_socket:
        print(f"{Colors.RED}Not connected to server{Colors.RESET}")
        return False
    
    if not os.path.exists(filepath):
        print(f"{Colors.RED}File not found: {filepath}{Colors.RESET}")
        return False
    
    try:
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        # Send file request
        file_request = {
            "type": "file_request",
            "filename": filename,
            "filesize": filesize
        }
        
        encrypted_request = encrypt_message(json.dumps(file_request))
        client_socket.send(encrypted_request)
        
        # Wait for server to be ready
        response = client_socket.recv(4096)
        response_data = decrypt_message(response)
        
        if isinstance(response_data, dict) and response_data.get("type") == "file_ready":
            # Server is ready, send the file
            with open(filepath, "rb") as file:
                while True:
                    chunk = file.read(4096)  # Read in 4KB chunks
                    if not chunk:
                        break
                    
                    # Encrypt chunk
                    encrypted_chunk = encrypt_message(chunk)
                    
                    # Send chunk size first
                    chunk_size = len(encrypted_chunk)
                    client_socket.send(chunk_size.to_bytes(8, byteorder='big'))
                    
                    # Send encrypted chunk
                    client_socket.send(encrypted_chunk)
            
            # Send end of file marker
            client_socket.send(b'ENDFILE')
            
            print(f"{Colors.GREEN}File {filename} sent successfully{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}Server not ready to receive file{Colors.RESET}")
            return False
    
    except Exception as e:
        print(f"{Colors.RED}Error sending file: {str(e)}{Colors.RESET}")
        return False

def save_message_to_history(message_data):
    """Save a message to the local chat history"""
    if not os.path.exists(CHAT_HISTORY_DIR):
        os.makedirs(CHAT_HISTORY_DIR)
    
    history_file = os.path.join(CHAT_HISTORY_DIR, f"{current_user}_history.json")
    
    try:
        # Load existing history
        history = []
        if os.path.exists(history_file):
            with open(history_file, "r") as file:
                try:
                    history = json.load(file)
                except json.JSONDecodeError:
                    history = []
        
        # Add new message
        history.append(message_data)
        
        # Save updated history
        with open(history_file, "w") as file:
            json.dump(history, file, indent=2)
    
    except Exception as e:
        print(f"{Colors.RED}Error saving message to history: {str(e)}{Colors.RESET}")

def process_command(command_text):
    """Process a client-side command"""
    parts = command_text.split()
    cmd = parts[0].lower()
    
    if cmd == "help":
        print_help()
    
    elif cmd == "exit" or cmd == "quit":
        print(f"{Colors.YELLOW}Disconnecting from server...{Colors.RESET}")
        return False  # Signal to exit
    
    elif cmd == "clear":
        os.system("cls" if os.name == "nt" else "clear")
    
    elif cmd == "users":
        # Send command to list users
        command = {
            "type": "command",
            "command": "list_users"
        }
        encrypted_command = encrypt_message(json.dumps(command))
        client_socket.send(encrypted_command)
    
    elif cmd == "files":
        # Send command to list files
        command = {
            "type": "command",
            "command": "list_files"
        }
        encrypted_command = encrypt_message(json.dumps(command))
        client_socket.send(encrypted_command)
    
    elif cmd == "send":
        if len(parts) < 2:
            print(f"{Colors.RED}Usage: /send <filepath>{Colors.RESET}")
        else:
            filepath = " ".join(parts[1:])
            send_file(filepath)
    
    elif cmd == "config":
        if len(parts) == 1:
            # Show current config
            print(f"{Colors.CYAN}Current configuration:{Colors.RESET}")
            for key, value in config.items():
                if key != "theme":
                    print(f"  {key}: {value}")
                else:
                    print(f"  theme:")
                    for theme_key, theme_value in value.items():
                        print(f"    {theme_key}: {theme_value}")
        elif len(parts) == 3:
            # Set config value
            key, value = parts[1], parts[2]
            if key in config and key != "theme":
                # Convert value to appropriate type
                if value.lower() in ("true", "false"):
                    config[key] = value.lower() == "true"
                elif value.isdigit():
                    config[key] = int(value)
                else:
                    config[key] = value
                save_config()
                print(f"{Colors.GREEN}Configuration updated: {key} = {value}{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid configuration key: {key}{Colors.RESET}")
        else:
            print(f"{Colors.RED}Usage: /config [key value]{Colors.RESET}")
    
    else:
        print(f"{Colors.RED}Unknown command: {cmd}{Colors.RESET}")
    
    return True  # Continue running

def print_help():
    """Print help information"""
    help_text = f"""
{Colors.CYAN}VoidLink Client Commands:{Colors.RESET}
  {Colors.BOLD}/help{Colors.RESET}              Show this help message
  {Colors.BOLD}/exit{Colors.RESET}, {Colors.BOLD}/quit{Colors.RESET}      Exit the client
  {Colors.BOLD}/clear{Colors.RESET}             Clear the screen
  {Colors.BOLD}/users{Colors.RESET}             List connected users
  {Colors.BOLD}/files{Colors.RESET}             List available files
  {Colors.BOLD}/send <filepath>{Colors.RESET}   Send a file to the server
  {Colors.BOLD}/config{Colors.RESET}            Show current configuration
  {Colors.BOLD}/config key value{Colors.RESET}  Set configuration value

{Colors.YELLOW}To send a message, simply type and press Enter.{Colors.RESET}
"""
    print(help_text)

def main():
    """Main client function"""
    global connected, client_socket
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="VoidLink Client")
    parser.add_argument("--host", help="Server hostname or IP")
    parser.add_argument("--port", type=int, help="Server port")
    parser.add_argument("--username", help="Username for authentication")
    args = parser.parse_args()
    
    # Ensure directories exist
    ensure_dirs()
    
    # Load configuration
    load_config()
    
    # Override config with command line arguments
    if args.host:
        config["server_host"] = args.host
    if args.port:
        config["server_port"] = args.port
    if args.username:
        config["username"] = args.username
    
    # Print welcome message
    print(f"""
{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════╗
║               VoidLink Client              ║
╚═══════════════════════════════════════════╝{Colors.RESET}

{Colors.YELLOW}Connecting to server at {config["server_host"]}:{config["server_port"]}...{Colors.RESET}
""")
    
    # Connect to server
    if not connect_to_server():
        print(f"{Colors.RED}Failed to connect to server. Exiting.{Colors.RESET}")
        return
    
    # Authenticate
    if not authenticate():
        print(f"{Colors.RED}Authentication failed. Exiting.{Colors.RESET}")
        client_socket.close()
        return
    
    # Start message receiving thread
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()
    
    # Print help
    print_help()
    
    # Main message loop
    try:
        while connected:
            user_input = input("")
            
            # Check if input is empty
            if not user_input.strip():
                continue
            
            # Check if input is a command
            if user_input.startswith("/"):
                if not process_command(user_input[1:]):
                    break
            else:
                # Regular message
                send_message(user_input)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Disconnecting from server...{Colors.RESET}")
    
    finally:
        # Clean up
        connected = False
        if client_socket:
            client_socket.close()
        print(f"{Colors.GREEN}Disconnected. Goodbye!{Colors.RESET}")

if __name__ == "__main__":
    main()