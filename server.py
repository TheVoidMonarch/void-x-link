#!/usr/bin/env python3
"""
VoidLink Server - Secure Terminal-Based Chat and File Transfer Server
"""

import socket
import threading
import json
import os
import time
from encryption import encrypt_message, decrypt_message
from authentication import authenticate_user, get_user_role, list_users
from storage import save_message, get_chat_history
from file_transfer import handle_file_transfer, get_file_list, FILE_STORAGE_DIR

# Ensure database directory exists
if not os.path.exists("database"):
    os.makedirs("database")

# Load configuration
CONFIG_FILE = "config.json"
if not os.path.exists(CONFIG_FILE):
    # Create default config
    default_config = {
        "server_host": "0.0.0.0",
        "server_port": 52384,
        "encryption_enabled": True,
        "storage": {
            "local": True,
            "cloud_backup": False
        }
    }
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(default_config, config_file, indent=4)
    config = default_config
else:
    with open(CONFIG_FILE, "r") as config_file:
        config = json.load(config_file)

HOST = config["server_host"]
PORT = config["server_port"]
clients = {}
client_locks = {}  # Thread locks for each client

def send_message(client_socket, message_data):
    """Send an encrypted message to a client"""
    try:
        # Convert message data to JSON string
        if isinstance(message_data, dict):
            message_str = json.dumps(message_data)
        else:
            message_str = str(message_data)
            
        # Encrypt and send
        encrypted_message = encrypt_message(message_str)
        client_socket.send(encrypted_message)
        return True
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False

def handle_client(client_socket, addr):
    """Handle client connection and messages"""
    username = None
    try:
        # Authentication phase
        auth_data = client_socket.recv(4096)
        auth_json = json.loads(decrypt_message(auth_data))
        
        username = auth_json.get("username")
        password = auth_json.get("password")
        
        # Authenticate user
        if authenticate_user(username, password):
            # Authentication successful
            client_locks[username] = threading.Lock()
            clients[username] = client_socket
            
            # Send welcome message
            welcome = {
                "type": "system",
                "content": f"Welcome to VoidLink, {username}!",
                "timestamp": time.time()
            }
            send_message(client_socket, welcome)
            
            # Broadcast user joined
            join_notification = {
                "type": "notification",
                "content": f"{username} has joined the chat",
                "timestamp": time.time()
            }
            broadcast(join_notification, username)
            
            print(f"User {username} authenticated from {addr}")
        else:
            # Authentication failed
            error_msg = {
                "type": "error",
                "content": "Authentication failed. Invalid username or password."
            }
            send_message(client_socket, error_msg)
            client_socket.close()
            return
        
        # Message handling loop
        while True:
            try:
                encrypted_data = client_socket.recv(4096)
                if not encrypted_data:
                    break  # Client disconnected
                
                # Decrypt and parse message
                decrypted_data = decrypt_message(encrypted_data)
                message_data = json.loads(decrypted_data)
                
                message_type = message_data.get("type", "message")
                
                if message_type == "message":
                    # Regular chat message
                    content = message_data.get("content", "")
                    timestamp = message_data.get("timestamp", time.time())
                    
                    # Save message to storage
                    message_obj = {
                        "sender": username,
                        "content": content,
                        "timestamp": timestamp
                    }
                    save_message(username, content)
                    
                    # Broadcast to other clients
                    broadcast(message_obj, username)
                    
                elif message_type == "file_request":
                    # Handle file transfer request
                    filename = message_data.get("filename")
                    filesize = message_data.get("filesize")
                    
                    # Notify client that server is ready to receive
                    ready_msg = {
                        "type": "file_ready",
                        "filename": filename
                    }
                    send_message(client_socket, ready_msg)
                    
                    # Handle the file transfer
                    file_info = handle_file_transfer(client_socket, filename, username)
                    
                    # Notify all users about the new file
                    file_notification = {
                        "type": "notification",
                        "content": f"{username} shared file: {filename}",
                        "filename": filename,
                        "sender": username,
                        "timestamp": time.time()
                    }
                    broadcast(file_notification, None)  # Send to all users including sender
                
                elif message_type == "command":
                    # Handle special commands
                    command = message_data.get("command")
                    
                    if command == "list_users":
                        # Check if user has permission
                        user_role = get_user_role(username)
                        if user_role == "admin":
                            # Admin can see all user details
                            user_list = list_users()
                            response = {
                                "type": "command_response",
                                "command": "list_users",
                                "data": user_list
                            }
                        else:
                            # Regular users can only see online users
                            user_list = list(clients.keys())
                            response = {
                                "type": "command_response",
                                "command": "list_users",
                                "data": user_list
                            }
                        send_message(client_socket, response)
                    
                    elif command == "list_files":
                        files = get_file_list()
                        response = {
                            "type": "command_response",
                            "command": "list_files",
                            "data": files
                        }
                        send_message(client_socket, response)
                    
                    elif command == "history":
                        # Get chat history
                        limit = message_data.get("limit", 50)
                        history = get_chat_history(limit=limit)
                        response = {
                            "type": "command_response",
                            "command": "history",
                            "data": history
                        }
                        send_message(client_socket, response)
            
            except json.JSONDecodeError:
                error_msg = {
                    "type": "error",
                    "content": "Invalid message format"
                }
                send_message(client_socket, error_msg)
            
            except Exception as e:
                print(f"Error processing message from {username}: {str(e)}")
                error_msg = {
                    "type": "error",
                    "content": f"Server error: {str(e)}"
                }
                send_message(client_socket, error_msg)

    except Exception as e:
        print(f"Error with connection {addr}: {str(e)}")
    
    finally:
        # Clean up when client disconnects
        if username in clients:
            with client_locks.get(username, threading.Lock()):
                del clients[username]
                if username in client_locks:
                    del client_locks[username]
            
            # Notify other users
            leave_notification = {
                "type": "notification",
                "content": f"{username} has left the chat",
                "timestamp": time.time()
            }
            broadcast(leave_notification, None)
            
        client_socket.close()
        print(f"Connection closed: {addr}")

def broadcast(message, exclude_user=None):
    """Broadcast a message to all connected clients except the sender"""
    message_str = json.dumps(message) if isinstance(message, dict) else str(message)
    encrypted_message = encrypt_message(message_str)
    
    for username, client in list(clients.items()):
        if exclude_user is None or username != exclude_user:
            try:
                with client_locks.get(username, threading.Lock()):
                    client.send(encrypted_message)
            except Exception as e:
                print(f"Error broadcasting to {username}: {str(e)}")
                # Client connection might be broken, will be cleaned up in its own thread

def start_server():
    """Start the VoidLink server"""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"VoidLink Server running on {HOST}:{PORT}")
        print(f"Encryption: {'Enabled' if config.get('encryption_enabled', True) else 'Disabled'}")
        print(f"Storage: {'Local' if config.get('storage', {}).get('local', True) else 'Disabled'}")
        
        while True:
            client_socket, addr = server.accept()
            print(f"New connection from: {addr}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {str(e)}")
    finally:
        if 'server' in locals():
            server.close()

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════╗
║               VoidLink Server             ║
║  Secure Terminal-Based Chat & File Share  ║
╚═══════════════════════════════════════════╝
    """)
    start_server()