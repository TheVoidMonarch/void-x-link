#!/usr/bin/env python3
"""
VoidLink Server - Secure Terminal-Based Chat and File Transfer Server
"""

import socket
import threading
import json
import os
import time
import re
import traceback
from encryption import encrypt_message, decrypt_message
from authentication import authenticate_user, get_user_role, list_users
from storage import save_message, get_chat_history
from file_transfer import handle_file_transfer, get_file_list, send_file, FILE_STORAGE_DIR
from file_transfer_resumable import (
    start_resumable_upload, handle_chunk, complete_resumable_upload,
    start_resumable_download, send_file_chunk, get_active_transfers, cancel_transfer
)
from rooms import get_rooms, create_room, delete_room, join_room, leave_room, get_room_members, get_user_rooms, get_room_info
from error_handling import (
    logger, log_info, log_warning, log_error, log_exception,
    VoidLinkError, AuthenticationError, AuthorizationError, FileTransferError, RoomError
)

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
        log_info(f"New connection from {addr}")

        # Authentication phase
        try:
            auth_data = client_socket.recv(4096)
            if not auth_data:
                raise AuthenticationError("No authentication data received")

            auth_json = decrypt_message(auth_data)

            # Make sure we have a dictionary
            if not isinstance(auth_json, dict):
                try:
                    auth_json = json.loads(auth_json)
                except:
                    auth_json = {}

            username = auth_json.get("username")
            password = auth_json.get("password")
            device_id = auth_json.get("device_id", f"{addr[0]}:{addr[1]}")  # Use IP:port as device ID if none provided

            if not username or not password:
                raise AuthenticationError("Missing username or password",
                                         {"username_provided": bool(username),
                                          "password_provided": bool(password)})

            # Authenticate user with device ID
            if authenticate_user(username, password, device_id):
                # Authentication successful
                log_info(f"User {username} authenticated successfully from {addr}")
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
        else:
            # Authentication failed
            log_warning(f"Failed authentication attempt for user {username} from {addr}")
            error = AuthenticationError("Invalid username or password",
                                       {"ip": addr[0], "username": username})
            error_msg = error.to_dict()
            send_message(client_socket, error_msg)
            client_socket.close()
            return
        except AuthenticationError as e:
            log_warning(f"Authentication error: {str(e)}")
            send_message(client_socket, e.to_dict())
            client_socket.close()
            return
        except Exception as e:
            log_exception(e, "authentication")
            error_msg = {
                "type": "error",
                "code": 500,
                "message": "Internal server error during authentication"
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
                message_data = decrypt_message(encrypted_data)

                # Make sure we have a dictionary
                if not isinstance(message_data, dict):
                    try:
                        message_data = json.loads(message_data)
                    except:
                        # If we can't parse it, create a simple message
                        message_data = {
                            "type": "message",
                            "content": str(message_data)
                        }
                
                message_type = message_data.get("type", "message")
                
                if message_type == "message":
                    # Regular chat message
                    content = message_data.get("content", "")
                    timestamp = message_data.get("timestamp", time.time())
                    room = message_data.get("room", "general")

                    # Check if this is a private message (starts with @username)
                    private_match = re.match(r'^@(\w+)\s+(.+)$', content)

                    if private_match:
                        # Private message
                        recipient = private_match.group(1)
                        private_content = private_match.group(2)

                        if recipient in clients:
                            # Save private message
                            save_message(username, private_content, recipient=recipient, message_type="private")

                            # Create message object
                            private_msg = {
                                "type": "private",
                                "sender": username,
                                "content": private_content,
                                "timestamp": timestamp
                            }

                            # Send to recipient and sender
                            broadcast(private_msg, None, recipients=[recipient, username])

                            print(f"Private message from {username} to {recipient}")
                        else:
                            # User not online
                            error_msg = {
                                "type": "error",
                                "content": f"User {recipient} is not online."
                            }
                            send_message(client_socket, error_msg)
                    else:
                        # Regular room message
                        # Save message to storage
                        save_message(username, content, room=room)

                        # Create message object
                        message_obj = {
                            "type": "message",
                            "sender": username,
                            "content": content,
                            "room": room,
                            "timestamp": timestamp
                        }

                        # Broadcast to room members
                        broadcast(message_obj, username, room=room)

                        print(f"Message from {username} in room {room}")

                elif message_type == "file_request":
                    # Handle file transfer request
                    filename = message_data.get("filename")
                    filesize = message_data.get("filesize")
                    recipient = message_data.get("recipient", "all")  # "all" or username
                    room = message_data.get("room", "general")
                    resumable = message_data.get("resumable", False)

                    try:
                        if resumable:
                            # Handle resumable file transfer
                            log_info(f"Starting resumable file upload for {filename} ({filesize} bytes) from {username}")

                            # Start the upload
                            upload_info = start_resumable_upload(client_socket, filename, filesize, username)

                            # The rest of the upload will be handled by chunk messages
                            # We'll store the recipient and room info for later
                            upload_info["recipient"] = recipient
                            upload_info["room"] = room

                        else:
                            # Handle regular file transfer
                            log_info(f"Starting regular file upload for {filename} ({filesize} bytes) from {username}")

                            # Notify client that server is ready to receive
                            ready_msg = {
                                "type": "file_ready",
                                "filename": filename
                            }
                            send_message(client_socket, ready_msg)

                            # Handle the file transfer
                            file_info = handle_file_transfer(client_socket, filename, username)

                    except FileTransferError as e:
                        error_msg = {
                            "type": "error",
                            "content": str(e)
                        }
                        send_message(client_socket, error_msg)
                        continue

                    if recipient != "all":
                        # Targeted file transfer
                        if recipient in clients:
                            # Notify recipient about the new file
                            # Check if file passed security scan
                            is_safe = True
                            security_message = ""
                            if "security_scan" in file_info:
                                is_safe = file_info["security_scan"].get("is_safe", True)
                                if not is_safe:
                                    security_message = f" (SECURITY WARNING: {file_info['security_scan'].get('reason', 'Unknown issue')})"

                            file_notification = {
                                "type": "notification",
                                "content": f"{username} shared file with you: {filename}{security_message}",
                                "filename": filename,
                                "sender": username,
                                "timestamp": time.time(),
                                "file_info": file_info,
                                "is_safe": is_safe
                            }
                            broadcast(file_notification, None, recipients=[recipient, username])

                            # Save as a private message
                            save_message(username, f"Shared file: {filename}", recipient=recipient, message_type="file")

                            print(f"File {filename} shared from {username} to {recipient}")
                        else:
                            # User not online
                            error_msg = {
                                "type": "error",
                                "content": f"User {recipient} is not online. File saved but not delivered."
                            }
                            send_message(client_socket, error_msg)
                    else:
                        # Room file transfer
                        # Check if file passed security scan
                        is_safe = True
                        security_message = ""
                        if "security_scan" in file_info:
                            is_safe = file_info["security_scan"].get("is_safe", True)
                            if not is_safe:
                                security_message = f" (SECURITY WARNING: {file_info['security_scan'].get('reason', 'Unknown issue')})"

                        file_notification = {
                            "type": "notification",
                            "content": f"{username} shared file in {room}: {filename}{security_message}",
                            "filename": filename,
                            "sender": username,
                            "room": room,
                            "timestamp": time.time(),
                            "file_info": file_info,
                            "is_safe": is_safe
                        }

                        # Broadcast to room or all users
                        if room != "all":
                            broadcast(file_notification, None, room=room)
                            # Save as a room message
                            save_message(username, f"Shared file: {filename}", room=room, message_type="file")
                        else:
                            broadcast(file_notification, None)
                            # Save as a global message
                            save_message(username, f"Shared file: {filename}", message_type="file")

                        print(f"File {filename} shared from {username} in {room}")
                
                elif message_type == "file_chunk":
                    # Handle a chunk of a resumable file upload
                    transfer_id = message_data.get("transfer_id")
                    chunk_index = message_data.get("chunk_index")
                    chunk_data = message_data.get("chunk_data")
                    chunk_hash = message_data.get("chunk_hash")

                    if not transfer_id or chunk_index is None or not chunk_data or not chunk_hash:
                        error_msg = {
                            "type": "error",
                            "content": "Missing required chunk information"
                        }
                        send_message(client_socket, error_msg)
                    else:
                        try:
                            # Handle the chunk
                            result = handle_chunk(client_socket, transfer_id, chunk_index, chunk_data, chunk_hash)
                            log_info(f"Processed chunk {chunk_index} for transfer {transfer_id}")
                        except FileTransferError as e:
                            error_msg = {
                                "type": "error",
                                "content": str(e)
                            }
                            send_message(client_socket, error_msg)

                elif message_type == "upload_complete":
                    # Complete a resumable file upload
                    transfer_id = message_data.get("transfer_id")

                    if not transfer_id:
                        error_msg = {
                            "type": "error",
                            "content": "Missing transfer ID"
                        }
                        send_message(client_socket, error_msg)
                    else:
                        try:
                            # Complete the upload
                            file_info = complete_resumable_upload(client_socket, transfer_id)

                            if "error" in file_info:
                                error_msg = {
                                    "type": "error",
                                    "content": file_info["error"]
                                }
                                send_message(client_socket, error_msg)
                            else:
                                log_info(f"Completed file upload: {file_info['filename']}")

                                # Get recipient and room info
                                recipient = file_info.get("recipient", "all")
                                room = file_info.get("room", "general")

                                # Handle notifications similar to regular file uploads
                                if recipient != "all":
                                    # Targeted file transfer
                                    if recipient in clients:
                                        # Check if file passed security scan
                                        is_safe = True
                                        security_message = ""
                                        if "security_scan" in file_info:
                                            is_safe = file_info["security_scan"].get("is_safe", True)
                                            if not is_safe:
                                                security_message = f" (SECURITY WARNING: {file_info['security_scan'].get('reason', 'Unknown issue')})"

                                        # Notify recipient
                                        file_notification = {
                                            "type": "notification",
                                            "content": f"{username} shared file with you: {file_info['filename']}{security_message}",
                                            "filename": file_info['filename'],
                                            "sender": username,
                                            "timestamp": time.time(),
                                            "file_info": file_info,
                                            "is_safe": is_safe
                                        }
                                        broadcast(file_notification, None, recipients=[recipient, username])
                                    else:
                                        # User not online
                                        error_msg = {
                                            "type": "error",
                                            "content": f"User {recipient} is not online. File saved but not delivered."
                                        }
                                        send_message(client_socket, error_msg)
                                else:
                                    # Room file transfer
                                    # Check if file passed security scan
                                    is_safe = True
                                    security_message = ""
                                    if "security_scan" in file_info:
                                        is_safe = file_info["security_scan"].get("is_safe", True)
                                        if not is_safe:
                                            security_message = f" (SECURITY WARNING: {file_info['security_scan'].get('reason', 'Unknown issue')})"

                                    # Notify room
                                    file_notification = {
                                        "type": "notification",
                                        "content": f"{username} shared file in {room}: {file_info['filename']}{security_message}",
                                        "filename": file_info['filename'],
                                        "sender": username,
                                        "room": room,
                                        "timestamp": time.time(),
                                        "file_info": file_info,
                                        "is_safe": is_safe
                                    }

                                    # Broadcast to room or all users
                                    if room != "all":
                                        broadcast(file_notification, None, room=room)
                                    else:
                                        broadcast(file_notification, None)
                        except FileTransferError as e:
                            error_msg = {
                                "type": "error",
                                "content": str(e)
                            }
                            send_message(client_socket, error_msg)

                elif message_type == "chunk_request":
                    # Handle a request for a chunk of a file download
                    transfer_id = message_data.get("transfer_id")
                    chunk_index = message_data.get("chunk_index")

                    if not transfer_id or chunk_index is None:
                        error_msg = {
                            "type": "error",
                            "content": "Missing required chunk information"
                        }
                        send_message(client_socket, error_msg)
                    else:
                        try:
                            # Get the filename from the transfer ID
                            filename = transfer_id.split("_")[1] if "_" in transfer_id else ""

                            # Send the chunk
                            result = send_file_chunk(client_socket, transfer_id, filename, chunk_index)

                            if not result.get("success", False):
                                error_msg = {
                                    "type": "error",
                                    "content": result.get("error", "Unknown error sending chunk")
                                }
                                send_message(client_socket, error_msg)
                            elif result.get("eof", False):
                                # End of file reached
                                eof_msg = {
                                    "type": "download_complete",
                                    "transfer_id": transfer_id,
                                    "filename": filename
                                }
                                send_message(client_socket, eof_msg)
                        except FileTransferError as e:
                            error_msg = {
                                "type": "error",
                                "content": str(e)
                            }
                            send_message(client_socket, error_msg)

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

                    elif command == "list_rooms":
                        # List available rooms
                        rooms = get_rooms()
                        room_list = []
                        for room_id, room_data in rooms.items():
                            room_list.append({
                                "id": room_id,
                                "name": room_data["name"],
                                "description": room_data["description"],
                                "members": len(room_data["members"])
                            })

                        response = {
                            "type": "command_response",
                            "command": "list_rooms",
                            "data": room_list
                        }
                        send_message(client_socket, response)

                    elif command == "create_room":
                        # Create a new room
                        room_id = message_data.get("room_id")
                        room_name = message_data.get("name", room_id)
                        room_desc = message_data.get("description", "")

                        if not room_id:
                            error_msg = {
                                "type": "error",
                                "content": "Room ID is required."
                            }
                            send_message(client_socket, error_msg)
                        elif not re.match(r'^[a-zA-Z0-9_-]+$', room_id):
                            error_msg = {
                                "type": "error",
                                "content": "Room ID can only contain letters, numbers, underscores, and hyphens."
                            }
                            send_message(client_socket, error_msg)
                        else:
                            success = create_room(room_id, room_name, room_desc, username)

                            if success:
                                response = {
                                    "type": "command_response",
                                    "command": "create_room",
                                    "data": {
                                        "success": True,
                                        "room_id": room_id
                                    }
                                }
                                send_message(client_socket, response)

                                # Notify all users about the new room
                                notification = {
                                    "type": "notification",
                                    "content": f"{username} created a new room: {room_name}"
                                }
                                broadcast(notification, None)
                            else:
                                error_msg = {
                                    "type": "error",
                                    "content": f"Failed to create room {room_id}. It may already exist."
                                }
                                send_message(client_socket, error_msg)

                    elif command == "join_room":
                        # Join a room
                        room_id = message_data.get("room_id")

                        if not room_id:
                            error_msg = {
                                "type": "error",
                                "content": "Room ID is required."
                            }
                            send_message(client_socket, error_msg)
                        else:
                            success = join_room(room_id, username)

                            if success:
                                room_info = get_room_info(room_id)
                                response = {
                                    "type": "command_response",
                                    "command": "join_room",
                                    "data": {
                                        "success": True,
                                        "room_id": room_id,
                                        "room_name": room_info["name"]
                                    }
                                }
                                send_message(client_socket, response)

                                # Notify room members
                                notification = {
                                    "type": "notification",
                                    "content": f"{username} joined the room",
                                    "room": room_id
                                }
                                broadcast(notification, None, room=room_id)
                            else:
                                error_msg = {
                                    "type": "error",
                                    "content": f"Failed to join room {room_id}. It may not exist."
                                }
                                send_message(client_socket, error_msg)

                    elif command == "leave_room":
                        # Leave a room
                        room_id = message_data.get("room_id")

                        if not room_id:
                            error_msg = {
                                "type": "error",
                                "content": "Room ID is required."
                            }
                            send_message(client_socket, error_msg)
                        else:
                            success = leave_room(room_id, username)

                            if success:
                                response = {
                                    "type": "command_response",
                                    "command": "leave_room",
                                    "data": {
                                        "success": True,
                                        "room_id": room_id
                                    }
                                }
                                send_message(client_socket, response)

                                # Notify room members
                                notification = {
                                    "type": "notification",
                                    "content": f"{username} left the room",
                                    "room": room_id
                                }
                                broadcast(notification, None, room=room_id)
                            else:
                                error_msg = {
                                    "type": "error",
                                    "content": f"Failed to leave room {room_id}. It may not exist or you can't leave the general room."
                                }
                                send_message(client_socket, error_msg)

                    elif command == "room_info":
                        # Get room information
                        room_id = message_data.get("room_id", "general")
                        room_info = get_room_info(room_id)

                        if room_info:
                            response = {
                                "type": "command_response",
                                "command": "room_info",
                                "data": room_info
                            }
                            send_message(client_socket, response)
                        else:
                            error_msg = {
                                "type": "error",
                                "content": f"Room {room_id} not found."
                            }
                            send_message(client_socket, error_msg)

                    elif command == "my_rooms":
                        # Get rooms the user is a member of
                        user_rooms = get_user_rooms(username)
                        response = {
                            "type": "command_response",
                            "command": "my_rooms",
                            "data": user_rooms
                        }
                        send_message(client_socket, response)

                    elif command == "download_file":
                        # Download a file
                        filename = message_data.get("filename")
                        resumable = message_data.get("resumable", False)
                        start_position = message_data.get("start_position", 0)

                        if not filename:
                            error_msg = {
                                "type": "error",
                                "content": "Filename is required."
                            }
                            send_message(client_socket, error_msg)
                        else:
                            try:
                                if resumable:
                                    # Start resumable download
                                    log_info(f"Starting resumable download of {filename} for {username} from position {start_position}")
                                    result = start_resumable_download(client_socket, filename, start_position)

                                    # Wait for client to request chunks
                                    # (Handled in the message loop)
                                else:
                                    # Regular download
                                    log_info(f"Starting regular download of {filename} for {username}")
                                    # Notify client that server is ready to send
                                    ready_msg = {
                                        "type": "file_download",
                                        "filename": filename,
                                        "status": "ready"
                                    }
                                    send_message(client_socket, ready_msg)

                                    # Send the file
                                    success = send_file(client_socket, filename)

                                    if success:
                                        log_info(f"File {filename} sent to {username}")
                                    else:
                                        error_msg = {
                                            "type": "error",
                                            "content": f"Failed to send file {filename}."
                                        }
                                        send_message(client_socket, error_msg)
                            except FileTransferError as e:
                                error_msg = {
                                    "type": "error",
                                    "content": str(e)
                                }
                                send_message(client_socket, error_msg)

                    elif command == "active_transfers":
                        # Get active transfers
                        transfers = get_active_transfers()
                        response = {
                            "type": "command_response",
                            "command": "active_transfers",
                            "data": transfers
                        }
                        send_message(client_socket, response)

                    elif command == "cancel_transfer":
                        # Cancel a transfer
                        transfer_id = message_data.get("transfer_id")
                        if not transfer_id:
                            error_msg = {
                                "type": "error",
                                "content": "Transfer ID is required."
                            }
                            send_message(client_socket, error_msg)
                        else:
                            success = cancel_transfer(transfer_id)
                            response = {
                                "type": "command_response",
                                "command": "cancel_transfer",
                                "data": {
                                    "success": success,
                                    "transfer_id": transfer_id
                                }
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

    except socket.error as e:
        log_error(f"Socket error with connection {addr}: {str(e)}")
    except json.JSONDecodeError as e:
        log_error(f"JSON decode error with connection {addr}: {str(e)}")
    except Exception as e:
        log_exception(e, f"connection {addr}")

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
            log_info(f"User {username} disconnected from {addr}")

        client_socket.close()
        log_info(f"Connection closed: {addr}")

def broadcast(message, exclude_user=None, room=None, recipients=None):
    """Broadcast a message to clients

    Args:
        message: The message to broadcast
        exclude_user: User to exclude from broadcast (usually the sender)
        room: If specified, only broadcast to users in this room
        recipients: If specified, only broadcast to these users
    """
    message_str = json.dumps(message) if isinstance(message, dict) else str(message)
    encrypted_message = encrypt_message(message_str)

    # Determine target users
    target_users = []

    if recipients:
        # Send to specific recipients
        target_users = recipients
    elif room:
        # Send to users in a specific room
        target_users = get_room_members(room)
    else:
        # Send to all connected users
        target_users = list(clients.keys())

    # Send the message to each target user
    for username in target_users:
        if username in clients and (exclude_user is None or username != exclude_user):
            try:
                with client_locks.get(username, threading.Lock()):
                    clients[username].send(encrypted_message)
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