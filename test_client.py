#!/usr/bin/env python3
"""
VoidLink Test Client - Simple client for testing the server
"""

import socket
import threading
import json
import os
import time
import sys
import getpass
import base64
import uuid
import platform
from datetime import datetime

# Import encryption functions if available
try:
    from encryption import encrypt_message, decrypt_message
except ImportError:
    # Simple encryption functions for testing
    def encrypt_message(message):
        """Encrypt a message (simplified version for testing)"""
        if isinstance(message, dict):
            message = json.dumps(message)
        if isinstance(message, str):
            message = message.encode('utf-8')
        return base64.b64encode(message)

    def decrypt_message(encrypted_message):
        """Decrypt a message (simplified version for testing)"""
        try:
            data = base64.b64decode(encrypted_message)
            try:
                return json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                return data.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return None

def get_device_id():
    """Generate a unique device ID based on hardware information"""
    try:
        # Try to get a hardware-based identifier
        if platform.system() == "Windows":
            # Windows - use machine GUID
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Cryptography")
            machine_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
            return f"win-{machine_guid}"
        
        elif platform.system() == "Darwin":
            # macOS - use hardware UUID
            import subprocess
            result = subprocess.run(['system_profiler', 'SPHardwareDataType'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if "Hardware UUID" in line:
                    uuid = line.split(":")[1].strip()
                    return f"mac-{uuid}"
        
        elif platform.system() == "Linux":
            # Linux - try to use machine-id
            if os.path.exists('/etc/machine-id'):
                with open('/etc/machine-id', 'r') as f:
                    machine_id = f.read().strip()
                    return f"linux-{machine_id}"
            
            # Fallback to /var/lib/dbus/machine-id
            elif os.path.exists('/var/lib/dbus/machine-id'):
                with open('/var/lib/dbus/machine-id', 'r') as f:
                    machine_id = f.read().strip()
                    return f"linux-{machine_id}"
    
    except Exception as e:
        print(f"Error getting hardware ID: {str(e)}")
    
    # Fallback to a random UUID stored in a file
    device_id_file = os.path.expanduser("~/.voidlink_device_id")
    
    if os.path.exists(device_id_file):
        with open(device_id_file, 'r') as f:
            return f.read().strip()
    else:
        # Generate a new UUID
        device_id = str(uuid.uuid4())
        os.makedirs(os.path.dirname(device_id_file), exist_ok=True)
        with open(device_id_file, 'w') as f:
            f.write(device_id)
        return device_id

def main():
    """Main client function"""
    print("""
╔═══════════════════════════════════════════╗
║            VoidLink Test Client           ║
║  Secure Terminal-Based Chat & File Share  ║
╚═══════════════════════════════════════════╝
    """)
    
    # Get device ID
    device_id = get_device_id()
    print(f"Device ID: {device_id}")
    
    # Connect to server
    server_host = input("Server host (default: localhost): ") or "localhost"
    server_port = int(input("Server port (default: 52384): ") or "52384")
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))
        print(f"Connected to server at {server_host}:{server_port}")
    except Exception as e:
        print(f"Error connecting to server: {str(e)}")
        return
    
    # Authenticate
    username = input("Username (default: admin): ") or "admin"
    password = getpass.getpass("Password (default: admin123): ") or "admin123"
    
    auth_data = {
        "username": username,
        "password": password,
        "device_id": device_id
    }
    
    # Send encrypted authentication data - directly encrypt the dictionary
    encrypted_auth = encrypt_message(auth_data)
    client_socket.send(encrypted_auth)
    
    # Start message receiving thread
    def receive_messages():
        while True:
            try:
                encrypted_data = client_socket.recv(4096)
                if not encrypted_data:
                    print("Connection to server lost")
                    break
                
                message_data = decrypt_message(encrypted_data)
                
                if isinstance(message_data, dict):
                    message_type = message_data.get("type", "message")
                    
                    if message_type == "message":
                        sender = message_data.get("sender", "Unknown")
                        content = message_data.get("content", "")
                        print(f"{sender}: {content}")
                    
                    elif message_type == "system":
                        content = message_data.get("content", "")
                        print(f"[SYSTEM] {content}")
                    
                    elif message_type == "notification":
                        content = message_data.get("content", "")
                        print(f"[NOTIFICATION] {content}")
                    
                    elif message_type == "error":
                        content = message_data.get("content", "")
                        print(f"[ERROR] {content}")
                    
                    elif message_type == "command_response":
                        command = message_data.get("command", "")
                        data = message_data.get("data", [])
                        print(f"[COMMAND] Response for '{command}':")
                        if isinstance(data, list):
                            for item in data:
                                print(f"  - {item}")
                        else:
                            print(f"  {data}")
                else:
                    print(message_data)
            
            except Exception as e:
                print(f"Error receiving message: {str(e)}")
                break
    
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()
    
    # Print help
    print("\nAvailable commands:")
    print("  /help - Show this help")
    print("  /exit - Exit the client")
    print("  /users - List connected users")
    print("  /files - List available files")
    print("  /send <filepath> - Send a file")
    print("  /history - Show chat history")
    print("\nType your messages and press Enter to send.")
    
    # Main message loop
    try:
        while True:
            user_input = input("")
            
            if user_input.lower() == "/exit":
                break
            
            elif user_input.lower() == "/help":
                print("\nAvailable commands:")
                print("  /help - Show this help")
                print("  /exit - Exit the client")
                print("  /users - List connected users")
                print("  /files - List available files")
                print("  /send <filepath> - Send a file")
                print("  /history - Show chat history")
            
            elif user_input.lower() == "/users":
                command = {
                    "type": "command",
                    "command": "list_users"
                }
                # Directly encrypt the dictionary
                encrypted_command = encrypt_message(command)
                client_socket.send(encrypted_command)
            
            elif user_input.lower() == "/files":
                command = {
                    "type": "command",
                    "command": "list_files"
                }
                # Directly encrypt the dictionary
                encrypted_command = encrypt_message(command)
                client_socket.send(encrypted_command)
            
            elif user_input.lower() == "/history":
                command = {
                    "type": "command",
                    "command": "history",
                    "limit": 10
                }
                # Directly encrypt the dictionary
                encrypted_command = encrypt_message(command)
                client_socket.send(encrypted_command)
            
            elif user_input.lower().startswith("/send "):
                filepath = user_input[6:].strip()
                if not os.path.exists(filepath):
                    print(f"File not found: {filepath}")
                    continue
                
                filename = os.path.basename(filepath)
                filesize = os.path.getsize(filepath)
                
                # Send file request
                file_request = {
                    "type": "file_request",
                    "filename": filename,
                    "filesize": filesize
                }
                
                # Directly encrypt the dictionary
                encrypted_request = encrypt_message(file_request)
                client_socket.send(encrypted_request)
                print(f"Sending file request for {filename}...")
                
                # Wait for server response (handled in receive thread)
                time.sleep(1)
                
                # Send the file
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
                
                print(f"File {filename} sent")
            
            elif user_input.startswith("/"):
                print(f"Unknown command: {user_input}")
            
            else:
                # Regular message
                message = {
                    "type": "message",
                    "content": user_input,
                    "timestamp": time.time()
                }
                
                # Directly encrypt the dictionary
                encrypted_message = encrypt_message(message)
                client_socket.send(encrypted_message)
    
    except KeyboardInterrupt:
        print("\nDisconnecting from server...")
    
    finally:
        client_socket.close()
        print("Disconnected. Goodbye!")

if __name__ == "__main__":
    main()