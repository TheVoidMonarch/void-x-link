#!/usr/bin/env python3
"""
VoidLink Client Reference - A simple reference implementation for the client
This file should be moved to a separate client repository
"""

import socket
import threading
import json
import os
import time
import sys
import getpass
import base64
from datetime import datetime

# Simple encryption functions for client-only mode
def encrypt_message(message):
    """Encrypt a message (simplified version for reference)"""
    if isinstance(message, dict):
        message = json.dumps(message)
    if isinstance(message, str):
        message = message.encode('utf-8')
    return base64.b64encode(message)

def decrypt_message(encrypted_message):
    """Decrypt a message (simplified version for reference)"""
    try:
        data = base64.b64decode(encrypted_message)
        try:
            return json.loads(data.decode('utf-8'))
        except json.JSONDecodeError:
            return data.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        return None

# Main client function
def main():
    """Main client function"""
    print("""
╔═══════════════════════════════════════════╗
║               VoidLink Client              ║
║  Secure Terminal-Based Chat & File Share  ║
╚═══════════════════════════════════════════╝
    """)
    
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
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    
    auth_data = {
        "username": username,
        "password": password
    }
    
    # Send encrypted authentication data
    encrypted_auth = encrypt_message(json.dumps(auth_data))
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
                else:
                    print(message_data)
            
            except Exception as e:
                print(f"Error receiving message: {str(e)}")
                break
    
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()
    
    # Main message loop
    try:
        print("Type your messages (or /exit to quit):")
        while True:
            message_text = input("")
            
            if message_text.lower() == "/exit":
                break
            
            message = {
                "type": "message",
                "content": message_text,
                "timestamp": time.time()
            }
            
            encrypted_message = encrypt_message(json.dumps(message))
            client_socket.send(encrypted_message)
    
    except KeyboardInterrupt:
        print("\nDisconnecting from server...")
    
    finally:
        client_socket.close()
        print("Disconnected. Goodbye!")

if __name__ == "__main__":
    main()