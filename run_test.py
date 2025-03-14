#!/usr/bin/env python3
"""
VoidLink Comprehensive Test Script - Tests all core features
"""

import socket
import threading
import json
import os
import time
import base64
import sys
import unittest
from datetime import datetime

# Import server modules
from encryption import encrypt_message, decrypt_message
from authentication import authenticate_user, create_user, delete_user
from storage import save_message, get_chat_history
from file_transfer import ensure_file_dirs

# Global variables
SERVER_HOST = "localhost"
SERVER_PORT = 52384
server_thread = None
server_running = False

def start_server_thread():
    """Start the server in a separate thread"""
    global server_thread, server_running
    
    # Import server module
    import server
    
    # Define server thread function
    def run_server():
        global server_running
        server_running = True
        try:
            server.start_server()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Server error: {str(e)}")
        finally:
            server_running = False
    
    # Start server thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    return server_running

def stop_server_thread():
    """Stop the server thread"""
    global server_thread, server_running
    if server_thread and server_running:
        # The server will be terminated when the main thread exits
        server_running = False
        server_thread.join(timeout=1)

class TestClient:
    """Simple test client for VoidLink"""
    
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socket = None
        self.connected = False
        self.received_messages = []
        self.receive_thread = None
    
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Client connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False
    
    def authenticate(self):
        """Authenticate with the server"""
        if not self.connected:
            return False
        
        try:
            # Create authentication message
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            # Send encrypted authentication data
            encrypted_auth = encrypt_message(auth_data)
            self.socket.send(encrypted_auth)
            
            # Start message receiving thread
            self.start_receiving()
            
            # Wait for authentication response
            time.sleep(1)
            
            # Check if we received a welcome message
            for msg in self.received_messages:
                if isinstance(msg, dict) and msg.get("type") == "system" and "Welcome" in msg.get("content", ""):
                    print(f"Authentication successful for {self.username}")
                    return True
            
            print(f"Authentication failed for {self.username}")
            return False
        
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False
    
    def start_receiving(self):
        """Start receiving messages from the server"""
        def receive_messages():
            while self.connected:
                try:
                    encrypted_data = self.socket.recv(4096)
                    if not encrypted_data:
                        print("Connection to server lost")
                        self.connected = False
                        break
                    
                    message_data = decrypt_message(encrypted_data)
                    self.received_messages.append(message_data)
                    
                    if isinstance(message_data, dict):
                        message_type = message_data.get("type", "message")
                        
                        if message_type == "message":
                            sender = message_data.get("sender", "Unknown")
                            content = message_data.get("content", "")
                            print(f"Received message - {sender}: {content}")
                        
                        elif message_type == "system":
                            content = message_data.get("content", "")
                            print(f"Received system message: {content}")
                        
                        elif message_type == "notification":
                            content = message_data.get("content", "")
                            print(f"Received notification: {content}")
                        
                        elif message_type == "error":
                            content = message_data.get("content", "")
                            print(f"Received error: {content}")
                        
                        elif message_type == "command_response":
                            command = message_data.get("command", "")
                            data = message_data.get("data", [])
                            print(f"Received command response for '{command}': {data}")
                    else:
                        print(f"Received message: {message_data}")
                
                except Exception as e:
                    print(f"Error receiving message: {str(e)}")
                    self.connected = False
                    break
        
        self.receive_thread = threading.Thread(target=receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()
    
    def send_message(self, content):
        """Send a chat message"""
        if not self.connected:
            return False
        
        try:
            message = {
                "type": "message",
                "content": content,
                "timestamp": time.time()
            }
            
            encrypted_message = encrypt_message(message)
            self.socket.send(encrypted_message)
            print(f"Sent message: {content}")
            return True
        
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
    
    def send_command(self, command, **params):
        """Send a command to the server"""
        if not self.connected:
            return False
        
        try:
            command_data = {
                "type": "command",
                "command": command,
                **params
            }
            
            encrypted_command = encrypt_message(command_data)
            self.socket.send(encrypted_command)
            print(f"Sent command: {command}")
            return True
        
        except Exception as e:
            print(f"Error sending command: {str(e)}")
            return False
    
    def send_file(self, filepath):
        """Send a file to the server"""
        if not self.connected or not os.path.exists(filepath):
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
            
            encrypted_request = encrypt_message(file_request)
            self.socket.send(encrypted_request)
            print(f"Sent file request for {filename}")
            
            # Wait for server to be ready
            time.sleep(1)
            
            # Check if server is ready
            ready = False
            for msg in self.received_messages:
                if isinstance(msg, dict) and msg.get("type") == "file_ready" and msg.get("filename") == filename:
                    ready = True
                    break
            
            if not ready:
                print("Server not ready to receive file")
                return False
            
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
                    self.socket.send(chunk_size.to_bytes(8, byteorder='big'))
                    
                    # Send encrypted chunk
                    self.socket.send(encrypted_chunk)
            
            # Send end of file marker
            self.socket.send(b'ENDFILE')
            
            print(f"File {filename} sent successfully")
            return True
        
        except Exception as e:
            print(f"Error sending file: {str(e)}")
            return False
    
    def wait_for_message(self, timeout=5, condition=None):
        """Wait for a specific message"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for msg in self.received_messages:
                if condition is None or condition(msg):
                    return msg
            time.sleep(0.1)
        return None
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.connected:
            self.connected = False
            self.socket.close()
            print(f"Client {self.username} disconnected")

def run_comprehensive_test():
    """Run a comprehensive test of all features"""
    print("\n=== Starting Comprehensive VoidLink Test ===\n")
    
    # Create test file
    test_file_path = "test_file.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for VoidLink file transfer.")
    
    try:
        # Start server
        print("Starting server...")
        if not start_server_thread():
            print("Failed to start server")
            return False
        
        # Create test user if it doesn't exist
        create_user("testuser", "testpass", "user")
        
        # Connect first client (admin)
        print("\n--- Testing Admin Client ---")
        admin_client = TestClient(SERVER_HOST, SERVER_PORT, "admin", "admin123")
        if not admin_client.connect():
            print("Failed to connect admin client")
            return False
        
        if not admin_client.authenticate():
            print("Failed to authenticate admin client")
            return False
        
        # Connect second client (test user)
        print("\n--- Testing Regular User Client ---")
        user_client = TestClient(SERVER_HOST, SERVER_PORT, "testuser", "testpass")
        if not user_client.connect():
            print("Failed to connect user client")
            return False
        
        if not user_client.authenticate():
            print("Failed to authenticate user client")
            return False
        
        # Test message sending
        print("\n--- Testing Message Exchange ---")
        admin_client.send_message("Hello from admin!")
        time.sleep(1)
        user_client.send_message("Hello from test user!")
        time.sleep(1)
        
        # Test commands
        print("\n--- Testing Commands ---")
        admin_client.send_command("list_users")
        time.sleep(1)
        user_client.send_command("list_files")
        time.sleep(1)
        
        # Test file transfer
        print("\n--- Testing File Transfer ---")
        admin_client.send_file(test_file_path)
        time.sleep(2)
        
        # Check if file transfer notification was received
        file_notification = user_client.wait_for_message(
            condition=lambda msg: isinstance(msg, dict) and 
                                 msg.get("type") == "notification" and 
                                 "shared file" in msg.get("content", "")
        )
        
        if file_notification:
            print("File transfer notification received successfully")
        else:
            print("File transfer notification not received")
        
        # Test file listing after upload
        user_client.send_command("list_files")
        time.sleep(1)
        
        # Clean up
        admin_client.disconnect()
        user_client.disconnect()
        
        print("\n=== Comprehensive Test Completed Successfully ===")
        return True
    
    except Exception as e:
        print(f"Test error: {str(e)}")
        return False
    
    finally:
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        stop_server_thread()

if __name__ == "__main__":
    run_comprehensive_test()