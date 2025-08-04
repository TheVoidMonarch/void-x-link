#!/usr/bin/env python3
"""
VoidLink Server

A simple server for handling VoidLink client connections.
"""

import os
import sys
import json
import socket
import argparse
import logging
import threading
import time
from typing import Dict, Any, List, Optional

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voidlink_server')

# Try to import VoidLink modules
try:
    import simple_encryption as encryption
    import simple_authentication as authentication
    import simple_file_security as file_security
    import simple_file_transfer as file_transfer
    import core.chat as chat
    VOIDLINK_MODULES_LOADED = True
    logger.info("VoidLink modules loaded successfully")
except ImportError as e:
    logger.warning(f"Some VoidLink modules could not be imported: {e}")
    logger.warning("Running in demo mode")
    VOIDLINK_MODULES_LOADED = False

# Constants
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8000
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 10

# Demo data (used when modules are not available)
DEMO_USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
    "demo": {"password": "password", "role": "user"}
}

DEMO_FILES = [
    {
        "id": "file1",
        "name": "Project_Proposal.pdf",
        "size": "1.2 MB",
        "date": "2023-03-15",
        "type": "PDF",
        "owner": "admin",
        "shared_with": ["user"]
    },
    {
        "id": "file2",
        "name": "Vacation_Photo.jpg",
        "size": "3.5 MB",
        "date": "2023-03-14",
        "type": "Image",
        "owner": "user",
        "shared_with": []
    },
    {
        "id": "file3",
        "name": "Meeting_Notes.docx",
        "size": "245 KB",
        "date": "2023-03-12",
        "type": "Document",
        "owner": "admin",
        "shared_with": ["demo"]
    }
]

class ClientHandler(threading.Thread):
    """Handler for client connections"""
    
    def __init__(self, client_socket, client_address, server):
        """Initialize the client handler"""
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.server = server
        self.running = True
        self.username = None
    
    def run(self):
        """Run the client handler"""
        logger.info(f"Client connected: {self.client_address}")

        try:
            while self.running:
                # Receive message
                data = self.client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                # Parse message
                try:
                    # Try to decrypt if encryption is available
                    if VOIDLINK_MODULES_LOADED:
                        try:
                            decrypted_data = encryption.decrypt_message(data.decode('utf-8'))
                            if isinstance(decrypted_data, dict):
                                message = decrypted_data
                            else:
                                message = json.loads(decrypted_data)
                        except Exception as e:
                            logger.error(f"Decryption error: {e}")
                            # Fall back to unencrypted
                            message = json.loads(data.decode('utf-8'))
                    else:
                        # Parse unencrypted
                        message = json.loads(data.decode('utf-8'))

                    # Handle message
                    self.handle_message(message)

                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from client: {self.client_address}")
                    self.send_response({
                        "status": "error",
                        "error": "Invalid JSON"
                    })

                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    self.send_response({
                        "status": "error",
                        "error": f"Server error: {str(e)}"
                    })

        except socket.error as e:
            logger.error(f"Socket error: {e}")

        finally:
            self.client_socket.close()
            logger.info(f"Client disconnected: {self.client_address}")

    def send_response(self, response):
        """Send a response to the client"""
        try:
            # Convert response to JSON
            json_response = json.dumps(response)

            # Encrypt if encryption is available
            if VOIDLINK_MODULES_LOADED:
                try:
                    encrypted_response = encryption.encrypt_message(json_response)
                    # Check if the response is already a string (which it should be)
                    if isinstance(encrypted_response, str):
                        self.client_socket.sendall(encrypted_response.encode('utf-8'))
                    else:
                        # If it's not a string (unlikely), convert it
                        self.client_socket.sendall(str(encrypted_response).encode('utf-8'))
                except Exception as e:
                    logger.error(f"Encryption error: {e}")
                    # Fall back to unencrypted
                    self.client_socket.sendall(json_response.encode('utf-8'))
            else:
                # Send unencrypted
                self.client_socket.sendall(json_response.encode('utf-8'))
        except socket.error as e:
            logger.error(f"Error sending response: {e}")
            self.running = False
    
    def handle_message(self, message):
        """Handle a message from the client"""
        command = message.get("command")

        # Authentication commands
        if command == "login":
            self.handle_login(message)
        elif command == "logout":
            self.handle_logout()

        # File commands
        elif command == "list_files":
            self.handle_list_files()
        elif command == "start_upload":
            self.handle_start_upload(message)
        elif command == "upload_chunk":
            self.handle_upload_chunk(message)
        elif command == "complete_upload":
            self.handle_complete_upload(message)
        elif command == "download_file":
            self.handle_download_file(message)
        elif command == "download_chunk":
            self.handle_download_chunk(message)
        elif command == "share_file":
            self.handle_share_file(message)
        elif command == "delete_file":
            self.handle_delete_file(message)

        # Chat commands
        elif command == "list_rooms":
            self.handle_list_rooms()
        elif command == "create_room":
            self.handle_create_room(message)
        elif command == "delete_room":
            self.handle_delete_room(message)
        elif command == "join_room":
            self.handle_join_room(message)
        elif command == "leave_room":
            self.handle_leave_room(message)
        elif command == "get_room_messages":
            self.handle_get_room_messages(message)
        elif command == "send_room_message":
            self.handle_send_room_message(message)
        elif command == "get_private_messages":
            self.handle_get_private_messages(message)
        elif command == "send_private_message":
            self.handle_send_private_message(message)
        elif command == "mark_messages_read":
            self.handle_mark_messages_read(message)
        elif command == "get_unread_counts":
            self.handle_get_unread_counts()
        else:
            self.send_response({
                "status": "error",
                "error": f"Unknown command: {command}"
            })

    def handle_login(self, message):
        """Handle login command"""
        data = message.get("data", {})
        username = data.get("username")
        password = data.get("password")
        device_id = data.get("device_id")

        if not username or not password:
            self.send_response({
                "status": "error",
                "error": "Username and password are required"
            })
            return

        # Authenticate user
        if VOIDLINK_MODULES_LOADED:
            try:
                # Check if this is a new user registration
                is_new_user = not authentication.user_exists(username) if hasattr(authentication, 'user_exists') else False

                # Get existing user info to check if this is a new device
                is_new_device = False
                if not is_new_user and device_id and hasattr(authentication, 'user_exists'):
                    user_info = authentication.get_user_info(username) if hasattr(authentication, 'get_user_info') else None
                    if user_info and "device_ids" in user_info:
                        is_new_device = device_id not in user_info["device_ids"]

                # Authenticate with device ID if provided
                success = authentication.authenticate_user(username, password, device_id)

                if success:
                    self.username = username

                    # Add user to active users
                    self.server.active_users[username] = self

                    # Prepare response
                    response = {
                        "status": "success",
                        "message": "Login successful"
                    }

                    # Add device binding info
                    if is_new_user and device_id:
                        response["device_binding"] = "new"
                    elif is_new_device and device_id:
                        response["device_binding"] = "added"

                    self.send_response(response)
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Invalid username or password"
                    })
            except authentication.AuthenticationError as e:
                logger.error(f"Authentication error: {e}")

                # Get error details if available
                error_details = getattr(e, 'details', {}) if hasattr(e, 'details') else {}

                # Prepare error response
                response = {
                    "status": "error",
                    "error": str(e)
                }

                # Add reason if available
                if "reason" in error_details:
                    response["reason"] = error_details["reason"]

                self.send_response(response)
            except Exception as e:
                logger.error(f"Authentication error: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Authentication error: {str(e)}"
                })
        else:
            # Demo mode
            if username in DEMO_USERS and DEMO_USERS[username]["password"] == password:
                self.username = username
                self.send_response({
                    "status": "success",
                    "message": "Login successful"
                })
            else:
                self.send_response({
                    "status": "error",
                    "error": "Invalid username or password"
                })
    
    def handle_logout(self):
        """Handle logout command"""
        if self.username:
            # Remove from active users
            if self.username in self.server.active_users:
                del self.server.active_users[self.username]

        self.username = None
        self.send_response({
            "status": "success",
            "message": "Logout successful"
        })
    
    def handle_list_files(self):
        """Handle list_files command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Use actual file_transfer module
                files = file_transfer.get_file_list(self.username)
                self.send_response({
                    "status": "success",
                    "files": files
                })
            except Exception as e:
                logger.error(f"Error listing files: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error listing files: {str(e)}"
                })
        else:
            # Demo mode
            files = [f for f in DEMO_FILES if f["owner"] == self.username or self.username in f["shared_with"]]
            self.send_response({
                "status": "success",
                "files": files
            })
    
    def handle_start_upload(self, message):
        """Handle start_upload command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        filename = data.get("filename")
        size = data.get("size")
        
        if not filename or size is None:
            self.send_response({
                "status": "error",
                "error": "Filename and size are required"
            })
            return
        
        # Generate upload ID
        upload_id = f"upload_{int(time.time())}_{self.username}"
        
        # Store upload info in server
        self.server.uploads[upload_id] = {
            "filename": filename,
            "size": size,
            "owner": self.username,
            "chunks": {},
            "complete": False
        }
        
        self.send_response({
            "status": "ready",
            "upload_id": upload_id
        })
    
    def handle_upload_chunk(self, message):
        """Handle upload_chunk command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        upload_id = data.get("upload_id")
        chunk_index = data.get("chunk_index")
        chunk_data = data.get("chunk_data")
        
        if not upload_id or chunk_index is None or not chunk_data:
            self.send_response({
                "status": "error",
                "error": "Upload ID, chunk index, and chunk data are required"
            })
            return
        
        # Check if upload exists
        if upload_id not in self.server.uploads:
            self.send_response({
                "status": "error",
                "error": "Upload not found"
            })
            return
        
        # Check if upload belongs to user
        upload = self.server.uploads[upload_id]
        if upload["owner"] != self.username:
            self.send_response({
                "status": "error",
                "error": "Not authorized to upload to this ID"
            })
            return
        
        # Store chunk
        upload["chunks"][chunk_index] = bytes.fromhex(chunk_data)
        
        self.send_response({
            "status": "success",
            "message": f"Chunk {chunk_index} received"
        })
    
    def handle_complete_upload(self, message):
        """Handle complete_upload command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        upload_id = data.get("upload_id")
        
        if not upload_id:
            self.send_response({
                "status": "error",
                "error": "Upload ID is required"
            })
            return
        
        # Check if upload exists
        if upload_id not in self.server.uploads:
            self.send_response({
                "status": "error",
                "error": "Upload not found"
            })
            return
        
        # Check if upload belongs to user
        upload = self.server.uploads[upload_id]
        if upload["owner"] != self.username:
            self.send_response({
                "status": "error",
                "error": "Not authorized to complete this upload"
            })
            return
        
        # Combine chunks
        chunks = upload["chunks"]
        chunk_indices = sorted(chunks.keys())
        combined_data = b"".join(chunks[i] for i in chunk_indices)
        
        # Save file
        if VOIDLINK_MODULES_LOADED:
            try:
                # Create temporary file
                temp_dir = os.path.join("database", "temp")
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, f"{upload_id}")

                with open(temp_path, 'wb') as f:
                    f.write(combined_data)

                # Upload file
                file_id = file_transfer.upload_file(temp_path, upload["filename"], self.username)

                # Clean up
                os.remove(temp_path)
                del self.server.uploads[upload_id]

                if file_id:
                    self.send_response({
                        "status": "success",
                        "file_id": file_id
                    })
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Error saving file"
                    })
            except Exception as e:
                logger.error(f"Error completing upload: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error completing upload: {str(e)}"
                })
        else:
            # Demo mode
            file_id = f"file{len(DEMO_FILES) + 1}"
            
            # Add to demo files
            DEMO_FILES.append({
                "id": file_id,
                "name": upload["filename"],
                "size": file_transfer.format_size(len(combined_data)) if VOIDLINK_MODULES_LOADED else "1.0 MB",
                "date": time.strftime("%Y-%m-%d"),
                "type": os.path.splitext(upload["filename"])[1][1:].upper() or "Unknown",
                "owner": self.username,
                "shared_with": []
            })
            
            # Clean up
            del self.server.uploads[upload_id]
            
            self.send_response({
                "status": "success",
                "file_id": file_id
            })
    
    def handle_download_file(self, message):
        """Handle download_file command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        file_id = data.get("file_id")
        
        if not file_id:
            self.send_response({
                "status": "error",
                "error": "File ID is required"
            })
            return
        
        # Check if file exists and user has access
        if VOIDLINK_MODULES_LOADED:
            try:
                # Get file metadata
                metadata = file_transfer.get_file_metadata(file_id)
                if not metadata:
                    self.send_response({
                        "status": "error",
                        "error": "File not found"
                    })
                    return
                
                # Check if user has access
                if metadata["owner"] != self.username and self.username not in metadata.get("shared_with", []):
                    self.send_response({
                        "status": "error",
                        "error": "Not authorized to download this file"
                    })
                    return
                
                # Generate download ID
                download_id = f"download_{int(time.time())}_{self.username}"
                
                # Store download info in server
                self.server.downloads[download_id] = {
                    "file_id": file_id,
                    "owner": self.username
                }
                
                # Get file size
                file_path = os.path.join(file_transfer.FILES_DIR, file_id)
                file_size = os.path.getsize(file_path)

                self.send_response({
                    "status": "ready",
                    "download_id": download_id,
                    "filename": metadata["name"],
                    "size": file_size
                })
            except Exception as e:
                logger.error(f"Error starting download: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error starting download: {str(e)}"
                })
        else:
            # Demo mode
            file = next((f for f in DEMO_FILES if f["id"] == file_id and (f["owner"] == self.username or self.username in f["shared_with"])), None)
            if not file:
                self.send_response({
                    "status": "error",
                    "error": "File not found or not authorized"
                })
                return
            
            # Generate download ID
            download_id = f"download_{int(time.time())}_{self.username}"
            
            # Store download info in server
            self.server.downloads[download_id] = {
                "file_id": file_id,
                "owner": self.username
            }
            
            self.send_response({
                "status": "ready",
                "download_id": download_id,
                "filename": file["name"],
                "size": 1024  # Demo size
            })
    
    def handle_download_chunk(self, message):
        """Handle download_chunk command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        file_id = data.get("file_id")
        chunk_index = data.get("chunk_index")
        
        if not file_id or chunk_index is None:
            self.send_response({
                "status": "error",
                "error": "File ID and chunk index are required"
            })
            return
        
        # Check if file exists and user has access
        if VOIDLINK_MODULES_LOADED:
            try:
                # Get file metadata
                metadata = file_transfer.get_file_metadata(file_id)
                if not metadata:
                    self.send_response({
                        "status": "error",
                        "error": "File not found"
                    })
                    return
                
                # Check if user has access
                if metadata["owner"] != self.username and self.username not in metadata.get("shared_with", []):
                    self.send_response({
                        "status": "error",
                        "error": "Not authorized to download this file"
                    })
                    return
                
                # Get file path
                file_path = os.path.join(file_transfer.FILES_DIR, file_id)

                # Read chunk
                with open(file_path, 'rb') as f:
                    f.seek(chunk_index * BUFFER_SIZE)
                    chunk = f.read(BUFFER_SIZE)

                self.send_response({
                    "status": "success",
                    "chunk_data": chunk.hex()
                })
            except Exception as e:
                logger.error(f"Error downloading chunk: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error downloading chunk: {str(e)}"
                })
        else:
            # Demo mode
            file = next((f for f in DEMO_FILES if f["id"] == file_id and (f["owner"] == self.username or self.username in f["shared_with"])), None)
            if not file:
                self.send_response({
                    "status": "error",
                    "error": "File not found or not authorized"
                })
                return
            
            # Generate demo data
            chunk = b"This is demo data for file " + file["name"].encode() + b"\n" * 100
            
            self.send_response({
                "status": "success",
                "chunk_data": chunk.hex()
            })
    
    def handle_share_file(self, message):
        """Handle share_file command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        file_id = data.get("file_id")
        recipient = data.get("recipient")
        
        if not file_id or not recipient:
            self.send_response({
                "status": "error",
                "error": "File ID and recipient are required"
            })
            return
        
        # Share file
        if VOIDLINK_MODULES_LOADED:
            try:
                # Check if recipient exists
                if not authentication.user_exists(recipient):
                    self.send_response({
                        "status": "error",
                        "error": "Recipient not found"
                    })
                    return
                
                # Share file
                success = file_transfer.share_file(file_id, self.username, recipient)
                if success:
                    self.send_response({
                        "status": "success",
                        "message": f"File shared with {recipient}"
                    })
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Error sharing file"
                    })
            except Exception as e:
                logger.error(f"Error sharing file: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error sharing file: {str(e)}"
                })
        else:
            # Demo mode
            file = next((f for f in DEMO_FILES if f["id"] == file_id and f["owner"] == self.username), None)
            if not file:
                self.send_response({
                    "status": "error",
                    "error": "File not found or not authorized"
                })
                return
            
            # Check if recipient exists
            if recipient not in DEMO_USERS:
                self.send_response({
                    "status": "error",
                    "error": "Recipient not found"
                })
                return
            
            # Share file
            if recipient not in file["shared_with"]:
                file["shared_with"].append(recipient)
            
            self.send_response({
                "status": "success",
                "message": f"File shared with {recipient}"
            })
    
    def handle_delete_file(self, message):
        """Handle delete_file command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        file_id = data.get("file_id")
        
        if not file_id:
            self.send_response({
                "status": "error",
                "error": "File ID is required"
            })
            return
        
        # Delete file
        if VOIDLINK_MODULES_LOADED:
            try:
                # Delete file
                success = file_transfer.delete_file(file_id, self.username)
                if success:
                    self.send_response({
                        "status": "success",
                        "message": "File deleted"
                    })
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Error deleting file"
                    })
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error deleting file: {str(e)}"
                })
        else:
            # Demo mode
            file_index = next((i for i, f in enumerate(DEMO_FILES) if f["id"] == file_id and f["owner"] == self.username), None)
            if file_index is None:
                self.send_response({
                    "status": "error",
                    "error": "File not found or not authorized"
                })
                return

            # Delete file
            del DEMO_FILES[file_index]

            self.send_response({
                "status": "success",
                "message": "File deleted"
            })

    # Chat command handlers
    def handle_list_rooms(self):
        """Handle list_rooms command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Get rooms the user has access to
                rooms = chat.get_rooms(self.username)

                # Convert to list for response
                room_list = []
                for room_id, room_info in rooms.items():
                    room_list.append({
                        "id": room_id,
                        "name": room_info.get("name", ""),
                        "description": room_info.get("description", ""),
                        "is_public": room_info.get("is_public", True),
                        "created_by": room_info.get("created_by", ""),
                        "created_at": room_info.get("created_at", 0),
                        "member_count": len(room_info.get("members", []))
                    })

                self.send_response({
                    "status": "success",
                    "rooms": room_list
                })
            except Exception as e:
                logger.error(f"Error listing rooms: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error listing rooms: {str(e)}"
                })
        else:
            # Demo mode
            self.send_response({
                "status": "success",
                "rooms": [
                    {
                        "id": "general",
                        "name": "General",
                        "description": "General discussion",
                        "is_public": True,
                        "created_by": "system",
                        "created_at": time.time() - 86400,
                        "member_count": 3
                    },
                    {
                        "id": "random",
                        "name": "Random",
                        "description": "Random topics",
                        "is_public": True,
                        "created_by": "admin",
                        "created_at": time.time() - 43200,
                        "member_count": 2
                    }
                ]
            })

    def handle_create_room(self, message):
        """Handle create_room command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        name = data.get("name")
        description = data.get("description", "")
        is_public = data.get("is_public", True)
        members = data.get("members", [])

        if not name:
            self.send_response({
                "status": "error",
                "error": "Room name is required"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Create room
                room_id = chat.create_room(name, description, self.username, is_public, members)

                if room_id:
                    self.send_response({
                        "status": "success",
                        "room_id": room_id
                    })
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Error creating room"
                    })
            except Exception as e:
                logger.error(f"Error creating room: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error creating room: {str(e)}"
                })
        else:
            # Demo mode
            room_id = name.lower().replace(' ', '_')
            self.send_response({
                "status": "success",
                "room_id": room_id
            })

    def handle_delete_room(self, message):
        """Handle delete_room command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        room_id = data.get("room_id")

        if not room_id:
            self.send_response({
                "status": "error",
                "error": "Room ID is required"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Delete room
                success = chat.delete_room(room_id, self.username)

                if success:
                    self.send_response({
                        "status": "success",
                        "message": "Room deleted"
                    })
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Error deleting room"
                    })
            except Exception as e:
                logger.error(f"Error deleting room: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error deleting room: {str(e)}"
                })
        else:
            # Demo mode
            self.send_response({
                "status": "success",
                "message": "Room deleted"
            })

    def handle_join_room(self, message):
        """Handle join_room command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        room_id = data.get("room_id")

        if not room_id:
            self.send_response({
                "status": "error",
                "error": "Room ID is required"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Join room
                success = chat.join_room(room_id, self.username)

                if success:
                    self.send_response({
                        "status": "success",
                        "message": "Joined room"
                    })
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Error joining room"
                    })
            except Exception as e:
                logger.error(f"Error joining room: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error joining room: {str(e)}"
                })
        else:
            # Demo mode
            self.send_response({
                "status": "success",
                "message": "Joined room"
            })

    def handle_leave_room(self, message):
        """Handle leave_room command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        room_id = data.get("room_id")

        if not room_id:
            self.send_response({
                "status": "error",
                "error": "Room ID is required"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Leave room
                success = chat.leave_room(room_id, self.username)

                if success:
                    self.send_response({
                        "status": "success",
                        "message": "Left room"
                    })
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Error leaving room"
                    })
            except Exception as e:
                logger.error(f"Error leaving room: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error leaving room: {str(e)}"
                })
        else:
            # Demo mode
            self.send_response({
                "status": "success",
                "message": "Left room"
            })

    def handle_get_room_messages(self, message):
        """Handle get_room_messages command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        room_id = data.get("room_id")
        limit = data.get("limit", 50)
        before_timestamp = data.get("before_timestamp")

        if not room_id:
            self.send_response({
                "status": "error",
                "error": "Room ID is required"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Check if user has access to the room
                rooms = chat.get_rooms(self.username)
                if room_id not in rooms:
                    self.send_response({
                        "status": "error",
                        "error": "Room not found or not authorized"
                    })
                    return

                # Get messages
                messages = chat.get_room_messages(room_id, limit, before_timestamp)

                self.send_response({
                    "status": "success",
                    "messages": messages
                })
            except Exception as e:
                logger.error(f"Error getting room messages: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error getting room messages: {str(e)}"
                })
        else:
            # Demo mode
            self.send_response({
                "status": "success",
                "messages": [
                    {
                        "id": "msg1",
                        "room_id": room_id,
                        "username": "admin",
                        "content": "Welcome to the chat room!",
                        "timestamp": time.time() - 3600
                    },
                    {
                        "id": "msg2",
                        "room_id": room_id,
                        "username": "user",
                        "content": "Hello everyone!",
                        "timestamp": time.time() - 1800
                    }
                ]
            })

    def handle_send_room_message(self, message):
        """Handle send_room_message command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        room_id = data.get("room_id")
        content = data.get("content")

        if not room_id or not content:
            self.send_response({
                "status": "error",
                "error": "Room ID and content are required"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Send message
                msg = chat.send_room_message(room_id, self.username, content)

                if msg:
                    self.send_response({
                        "status": "success",
                        "message": msg
                    })

                    # Notify other users in the room
                    self.notify_room_message(room_id, msg)
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Error sending message"
                    })
            except Exception as e:
                logger.error(f"Error sending room message: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error sending room message: {str(e)}"
                })
        else:
            # Demo mode
            msg = {
                "id": f"msg_{int(time.time())}",
                "room_id": room_id,
                "username": self.username,
                "content": content,
                "timestamp": time.time()
            }

            self.send_response({
                "status": "success",
                "message": msg
            })

    def handle_get_private_messages(self, message):
        """Handle get_private_messages command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        other_username = data.get("username")
        limit = data.get("limit", 50)
        before_timestamp = data.get("before_timestamp")

        if not other_username:
            self.send_response({
                "status": "error",
                "error": "Username is required"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Get messages
                messages = chat.get_private_messages(self.username, other_username, limit, before_timestamp)

                # Mark messages as read
                chat.mark_private_messages_read(self.username, other_username)

                self.send_response({
                    "status": "success",
                    "messages": messages
                })
            except Exception as e:
                logger.error(f"Error getting private messages: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error getting private messages: {str(e)}"
                })
        else:
            # Demo mode
            self.send_response({
                "status": "success",
                "messages": [
                    {
                        "id": "pm1",
                        "from_username": other_username,
                        "to_username": self.username,
                        "content": "Hi there!",
                        "timestamp": time.time() - 3600,
                        "read": True
                    },
                    {
                        "id": "pm2",
                        "from_username": self.username,
                        "to_username": other_username,
                        "content": "Hello!",
                        "timestamp": time.time() - 3500,
                        "read": True
                    }
                ]
            })

    def handle_send_private_message(self, message):
        """Handle send_private_message command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        to_username = data.get("username")
        content = data.get("content")

        if not to_username or not content:
            self.send_response({
                "status": "error",
                "error": "Username and content are required"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Send message
                msg = chat.send_private_message(self.username, to_username, content)

                if msg:
                    self.send_response({
                        "status": "success",
                        "message": msg
                    })

                    # Notify recipient
                    self.notify_private_message(to_username, msg)
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Error sending message"
                    })
            except Exception as e:
                logger.error(f"Error sending private message: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error sending private message: {str(e)}"
                })
        else:
            # Demo mode
            msg = {
                "id": f"pm_{int(time.time())}",
                "from_username": self.username,
                "to_username": to_username,
                "content": content,
                "timestamp": time.time(),
                "read": False
            }

            self.send_response({
                "status": "success",
                "message": msg
            })

    def handle_mark_messages_read(self, message):
        """Handle mark_messages_read command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        data = message.get("data", {})
        other_username = data.get("username")

        if not other_username:
            self.send_response({
                "status": "error",
                "error": "Username is required"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Mark messages as read
                success = chat.mark_private_messages_read(self.username, other_username)

                if success:
                    self.send_response({
                        "status": "success",
                        "message": "Messages marked as read"
                    })
                else:
                    self.send_response({
                        "status": "error",
                        "error": "Error marking messages as read"
                    })
            except Exception as e:
                logger.error(f"Error marking messages as read: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error marking messages as read: {str(e)}"
                })
        else:
            # Demo mode
            self.send_response({
                "status": "success",
                "message": "Messages marked as read"
            })

    def handle_get_unread_counts(self):
        """Handle get_unread_counts command"""
        if not self.username:
            self.send_response({
                "status": "error",
                "error": "Not logged in"
            })
            return

        if VOIDLINK_MODULES_LOADED:
            try:
                # Get unread counts
                unread_counts = chat.get_unread_message_counts(self.username)

                self.send_response({
                    "status": "success",
                    "unread_counts": unread_counts
                })
            except Exception as e:
                logger.error(f"Error getting unread counts: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error getting unread counts: {str(e)}"
                })
        else:
            # Demo mode
            self.send_response({
                "status": "success",
                "unread_counts": {
                    "admin": 2,
                    "user": 1
                }
            })

    def notify_room_message(self, room_id, message):
        """Notify other users in the room about a new message"""
        if not VOIDLINK_MODULES_LOADED:
            return

        try:
            # Get room info
            rooms = chat.get_rooms()
            if room_id not in rooms:
                return

            room_info = rooms[room_id]

            # Get users to notify
            users_to_notify = []

            if room_info.get("is_public", False):
                # Notify all active users
                users_to_notify = list(self.server.active_users.keys())
            else:
                # Notify only members
                users_to_notify = room_info.get("members", [])

            # Remove sender
            if self.username in users_to_notify:
                users_to_notify.remove(self.username)

            # Send notification to each user
            for username in users_to_notify:
                if username in self.server.active_users:
                    client = self.server.active_users[username]
                    client.send_notification("new_room_message", {
                        "room_id": room_id,
                        "message": message
                    })
        except Exception as e:
            logger.error(f"Error notifying room message: {e}")

    def notify_private_message(self, to_username, message):
        """Notify recipient about a new private message"""
        if not VOIDLINK_MODULES_LOADED:
            return

        try:
            # Check if recipient is active
            if to_username in self.server.active_users:
                client = self.server.active_users[to_username]
                client.send_notification("new_private_message", {
                    "message": message
                })
        except Exception as e:
            logger.error(f"Error notifying private message: {e}")

    def send_notification(self, notification_type, data):
        """Send a notification to the client"""
        try:
            notification = {
                "notification": notification_type,
                "data": data
            }

            # Convert to JSON
            json_notification = json.dumps(notification)

            # Encrypt if encryption is available
            if VOIDLINK_MODULES_LOADED:
                try:
                    encrypted_notification = encryption.encrypt_message(json_notification)
                    self.client_socket.sendall(encrypted_notification.encode('utf-8'))
                except Exception as e:
                    logger.error(f"Encryption error: {e}")
                    # Fall back to unencrypted
                    self.client_socket.sendall(json_notification.encode('utf-8'))
            else:
                # Send unencrypted
                self.client_socket.sendall(json_notification.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error sending notification: {e}")


class VoidLinkServer:
    """Server for handling VoidLink client connections"""

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        """Initialize the server"""
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.clients = []
        self.uploads = {}
        self.downloads = {}
        self.active_users = {}  # Username -> ClientHandler
    
    def start(self):
        """Start the server"""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(MAX_CONNECTIONS)
            
            self.running = True
            logger.info(f"VoidLink server started on {self.host}:{self.port}")
            
            # Create temp directory
            os.makedirs(os.path.join("database", "temp"), exist_ok=True)

            # Accept connections
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    
                    # Create client handler
                    handler = ClientHandler(client_socket, client_address, self)
                    handler.start()
                    
                    # Add to clients
                    self.clients.append(handler)
                    
                    # Clean up finished clients
                    self.clients = [c for c in self.clients if c.is_alive()]
                
                except socket.error as e:
                    if self.running:
                        logger.error(f"Socket error: {e}")
                    break
        
        except Exception as e:
            logger.error(f"Server error: {e}")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        
        # Close socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Stop clients
        for client in self.clients:
            try:
                client.running = False
            except:
                pass
        
        logger.info("VoidLink server stopped")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="VoidLink Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to listen on (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to listen on (default: {DEFAULT_PORT})")
    
    args = parser.parse_args()
    
    # Create and start server
    server = VoidLinkServer(args.host, args.port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Server interrupted")
    finally:
        server.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())