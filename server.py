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
                    self.client_socket.sendall(encrypted_response.encode('utf-8'))
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
        
        if command == "login":
            self.handle_login(message)
        elif command == "logout":
            self.handle_logout()
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
        
        if not username or not password:
            self.send_response({
                "status": "error",
                "error": "Username and password are required"
            })
            return
        
        # Authenticate user
        if VOIDLINK_MODULES_LOADED:
            try:
                success = authentication.authenticate_user(username, password, self.client_address[0])
                if success:
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
                temp_path = os.path.join("database", "temp", f"{upload_id}")
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                
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