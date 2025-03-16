#!/usr/bin/env python3
"""
VoidLink Server

A simple server for handling VoidLink client connections over the network.
"""

import os
import sys
import json
import socket
import argparse
import logging
import threading
import time
import uuid
from datetime import datetime

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
    import simple_authentication as authentication
    import simple_encryption as encryption
    import file_security
    import file_transfer
    VOIDLINK_MODULES_LOADED = True
    logger.info("VoidLink modules loaded successfully")
except ImportError as e:
    logger.warning(f"Some VoidLink modules could not be imported: {e}")
    logger.warning("Running in demo mode")
    VOIDLINK_MODULES_LOADED = False

# Constants
DEFAULT_HOST = '0.0.0.0'  # Listen on all interfaces
DEFAULT_PORT = 8000
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 10
FILES_DIR = "database/files"
METADATA_DIR = "database/metadata"

# Demo data
DEMO_USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin"
    },
    "user": {
        "password": "user123",
        "role": "user"
    },
    "demo": {
        "password": "password",
        "role": "user"
    }
}

DEMO_FILES = [
    {
        "id": "file1",
        "name": "Project_Proposal.pdf",
        "size": "1.2 MB",
        "date": "2023-03-15",
        "type": "PDF",
        "owner": "admin"
    },
    {
        "id": "file2",
        "name": "Vacation_Photo.jpg",
        "size": "3.5 MB",
        "date": "2023-03-14",
        "type": "Image",
        "owner": "admin"
    },
    {
        "id": "file3",
        "name": "Meeting_Notes.docx",
        "size": "245 KB",
        "date": "2023-03-12",
        "type": "Document",
        "owner": "user"
    },
    {
        "id": "file4",
        "name": "Budget_2023.xlsx",
        "size": "1.8 MB",
        "date": "2023-03-08",
        "type": "Spreadsheet",
        "owner": "user"
    }
]

# In-memory storage for uploads
active_uploads = {}
active_downloads = {}

class ClientHandler(threading.Thread):
    """Handler for client connections"""
    
    def __init__(self, client_socket, client_address, server):
        """Initialize the handler"""
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.server = server
        self.username = None
        self.running = True
    
    def run(self):
        """Handle client connection"""
        logger.info(f"Client connected: {self.client_address}")

        try:
            while self.running:
                # Receive data
                data = self.client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                # Parse message
                try:
                    # Try to decrypt the message if encryption is available
                    if VOIDLINK_MODULES_LOADED:
                        try:
                            # Try to decrypt as JSON
                            decrypted_data = encryption.decrypt_message(data.decode('utf-8'))
                            if isinstance(decrypted_data, dict):
                                message = decrypted_data
                            else:
                                message = json.loads(decrypted_data)
                        except Exception:
                            # If decryption fails, try parsing as plain JSON
                            message = json.loads(data.decode('utf-8'))
                    else:
                        # Parse as plain JSON
                        message = json.loads(data.decode('utf-8'))

                    command = message.get("command")

                    # Check if user is authenticated for protected commands
                    if command not in ["login"] and not self.username:
                        self.send_response({
                            "status": "error",
                            "error": "Authentication required"
                        })
                        continue

                    # Handle command
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

                except json.JSONDecodeError:
                    self.send_response({
                        "status": "error",
                        "error": "Invalid JSON message"
                    })
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    self.send_response({
                        "status": "error",
                        "error": f"Internal server error: {str(e)}"
                    })

        except socket.error as e:
            logger.error(f"Socket error: {e}")

        finally:
            # Clean up
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
                success = authentication.authenticate_user(username, password)
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
            files = [f for f in DEMO_FILES if f["owner"] == self.username]
            self.send_response({
                "status": "success",
                "files": files
            })
    
    def handle_start_upload(self, message):
        """Handle start_upload command"""
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
        upload_id = str(uuid.uuid4())
        
        # Create upload record
        active_uploads[upload_id] = {
            "filename": filename,
            "size": size,
            "uploader": self.username,
            "chunks": {},
            "start_time": time.time()
        }
        
        self.send_response({
            "status": "ready",
            "upload_id": upload_id,
            "message": "Ready to receive file"
        })
    
    def handle_upload_chunk(self, message):
        """Handle upload_chunk command"""
        data = message.get("data", {})
        upload_id = data.get("upload_id")
        chunk_index = data.get("chunk_index")
        chunk_data_hex = data.get("chunk_data")
        
        if not upload_id or chunk_index is None or not chunk_data_hex:
            self.send_response({
                "status": "error",
                "error": "Upload ID, chunk index, and chunk data are required"
            })
            return
        
        # Check if upload exists
        if upload_id not in active_uploads:
            self.send_response({
                "status": "error",
                "error": "Invalid upload ID"
            })
            return
        
        # Check if uploader matches
        upload = active_uploads[upload_id]
        if upload["uploader"] != self.username:
            self.send_response({
                "status": "error",
                "error": "You are not the uploader of this file"
            })
            return
        
        # Convert hex to bytes
        try:
            chunk_data = bytes.fromhex(chunk_data_hex)
        except ValueError:
            self.send_response({
                "status": "error",
                "error": "Invalid chunk data format"
            })
            return
        
        # Store chunk
        upload["chunks"][chunk_index] = chunk_data
        
        self.send_response({
            "status": "success",
            "message": f"Chunk {chunk_index} received"
        })
    
    def handle_complete_upload(self, message):
        """Handle complete_upload command"""
        data = message.get("data", {})
        upload_id = data.get("upload_id")
        
        if not upload_id:
            self.send_response({
                "status": "error",
                "error": "Upload ID is required"
            })
            return
        
        # Check if upload exists
        if upload_id not in active_uploads:
            self.send_response({
                "status": "error",
                "error": "Invalid upload ID"
            })
            return
        
        # Check if uploader matches
        upload = active_uploads[upload_id]
        if upload["uploader"] != self.username:
            self.send_response({
                "status": "error",
                "error": "You are not the uploader of this file"
            })
            return
        
        # Ensure directories exist
        os.makedirs(FILES_DIR, exist_ok=True)
        os.makedirs(METADATA_DIR, exist_ok=True)
        
        # Generate file ID
        file_id = str(uuid.uuid4())
        
        # Determine file path
        file_path = os.path.join(FILES_DIR, file_id)
        
        # Write file
        try:
            with open(file_path, 'wb') as f:
                # Sort chunks by index
                sorted_chunks = sorted(upload["chunks"].items(), key=lambda x: x[0])
                for _, chunk_data in sorted_chunks:
                    f.write(chunk_data)
            
            # Create metadata
            metadata = {
                "id": file_id,
                "name": upload["filename"],
                "size": upload["size"],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": os.path.splitext(upload["filename"])[1][1:].upper() or "Unknown",
                "owner": self.username,
                "upload_time": time.time(),
                "shared_with": []
            }
            
            # Save metadata
            metadata_path = os.path.join(METADATA_DIR, f"{file_id}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
            
            # Add to demo files (for demo mode)
            if not VOIDLINK_MODULES_LOADED:
                size_str = f"{upload['size']} bytes"
                if upload['size'] >= 1024 * 1024:
                    size_str = f"{upload['size'] / (1024 * 1024):.1f} MB"
                elif upload['size'] >= 1024:
                    size_str = f"{upload['size'] / 1024:.1f} KB"
                
                DEMO_FILES.append({
                    "id": file_id,
                    "name": upload["filename"],
                    "size": size_str,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "type": os.path.splitext(upload["filename"])[1][1:].upper() or "Unknown",
                    "owner": self.username
                })
            
            # Clean up
            del active_uploads[upload_id]
            
            self.send_response({
                "status": "success",
                "file_id": file_id,
                "message": "File uploaded successfully"
            })
        
        except Exception as e:
            logger.error(f"Error completing upload: {e}")
            self.send_response({
                "status": "error",
                "error": f"Error completing upload: {str(e)}"
            })
    
    def handle_download_file(self, message):
        """Handle download_file command"""
        data = message.get("data", {})
        file_id = data.get("file_id")
        
        if not file_id:
            self.send_response({
                "status": "error",
                "error": "File ID is required"
            })
            return
        
        # Find file
        if VOIDLINK_MODULES_LOADED:
            try:
                # Use actual file_transfer module
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
                        "error": "You do not have access to this file"
                    })
                    return
                
                # Get file path
                file_path = os.path.join(FILES_DIR, file_id)
                if not os.path.exists(file_path):
                    self.send_response({
                        "status": "error",
                        "error": "File not found on server"
                    })
                    return
                
                # Create download record
                download_id = str(uuid.uuid4())
                active_downloads[download_id] = {
                    "file_id": file_id,
                    "file_path": file_path,
                    "filename": metadata["name"],
                    "size": os.path.getsize(file_path),
                    "downloader": self.username,
                    "start_time": time.time()
                }
                
                self.send_response({
                    "status": "ready",
                    "download_id": download_id,
                    "filename": metadata["name"],
                    "size": os.path.getsize(file_path),
                    "message": "Ready to send file"
                })
            
            except Exception as e:
                logger.error(f"Error starting download: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error starting download: {str(e)}"
                })
        
        else:
            # Demo mode
            file = next((f for f in DEMO_FILES if f["id"] == file_id), None)
            if not file:
                self.send_response({
                    "status": "error",
                    "error": "File not found"
                })
                return
            
            # Check if user has access
            if file["owner"] != self.username:
                self.send_response({
                    "status": "error",
                    "error": "You do not have access to this file"
                })
                return
            
            # Create dummy file content
            dummy_content = f"This is a dummy file content for {file['name']}".encode('utf-8')
            
            # Create download record
            download_id = str(uuid.uuid4())
            active_downloads[download_id] = {
                "file_id": file_id,
                "dummy_content": dummy_content,
                "filename": file["name"],
                "size": len(dummy_content),
                "downloader": self.username,
                "start_time": time.time()
            }
            
            self.send_response({
                "status": "ready",
                "download_id": download_id,
                "filename": file["name"],
                "size": len(dummy_content),
                "message": "Ready to send file"
            })
    
    def handle_download_chunk(self, message):
        """Handle download_chunk command"""
        data = message.get("data", {})
        file_id = data.get("file_id")
        chunk_index = data.get("chunk_index")
        
        if not file_id or chunk_index is None:
            self.send_response({
                "status": "error",
                "error": "File ID and chunk index are required"
            })
            return
        
        # Find download
        download = next((d for d in active_downloads.values() if d["file_id"] == file_id and d["downloader"] == self.username), None)
        if not download:
            self.send_response({
                "status": "error",
                "error": "Download not found"
            })
            return
        
        # Get chunk
        chunk_size = 1024 * 1024  # 1 MB chunks
        
        if VOIDLINK_MODULES_LOADED:
            try:
                # Read chunk from file
                with open(download["file_path"], 'rb') as f:
                    f.seek(chunk_index * chunk_size)
                    chunk_data = f.read(chunk_size)
                
                if not chunk_data:
                    self.send_response({
                        "status": "error",
                        "error": "End of file reached"
                    })
                    return
                
                self.send_response({
                    "status": "success",
                    "chunk_index": chunk_index,
                    "chunk_data": chunk_data.hex(),
                    "message": f"Chunk {chunk_index} sent"
                })
            
            except Exception as e:
                logger.error(f"Error sending chunk: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error sending chunk: {str(e)}"
                })
        
        else:
            # Demo mode
            dummy_content = download["dummy_content"]
            start = chunk_index * chunk_size
            end = min(start + chunk_size, len(dummy_content))
            
            if start >= len(dummy_content):
                self.send_response({
                    "status": "error",
                    "error": "End of file reached"
                })
                return
            
            chunk_data = dummy_content[start:end]
            
            self.send_response({
                "status": "success",
                "chunk_index": chunk_index,
                "chunk_data": chunk_data.hex(),
                "message": f"Chunk {chunk_index} sent"
            })
    
    def handle_share_file(self, message):
        """Handle share_file command"""
        data = message.get("data", {})
        file_id = data.get("file_id")
        recipient = data.get("recipient")
        
        if not file_id or not recipient:
            self.send_response({
                "status": "error",
                "error": "File ID and recipient are required"
            })
            return
        
        if VOIDLINK_MODULES_LOADED:
            try:
                # Use actual file_transfer module
                metadata = file_transfer.get_file_metadata(file_id)
                if not metadata:
                    self.send_response({
                        "status": "error",
                        "error": "File not found"
                    })
                    return
                
                # Check if user is the owner
                if metadata["owner"] != self.username:
                    self.send_response({
                        "status": "error",
                        "error": "You are not the owner of this file"
                    })
                    return
                
                # Check if recipient exists
                if not authentication.user_exists(recipient):
                    self.send_response({
                        "status": "error",
                        "error": "Recipient not found"
                    })
                    return
                
                # Share file
                shared_with = metadata.get("shared_with", [])
                if recipient not in shared_with:
                    shared_with.append(recipient)
                    metadata["shared_with"] = shared_with
                    
                    # Save metadata
                    metadata_path = os.path.join(METADATA_DIR, f"{file_id}.json")
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f)
                
                # Generate share link
                share_link = f"https://voidlink.example.com/share/{file_id}"
                
                self.send_response({
                    "status": "success",
                    "share_link": share_link,
                    "message": f"File shared with {recipient}"
                })
            
            except Exception as e:
                logger.error(f"Error sharing file: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error sharing file: {str(e)}"
                })
        
        else:
            # Demo mode
            file = next((f for f in DEMO_FILES if f["id"] == file_id), None)
            if not file:
                self.send_response({
                    "status": "error",
                    "error": "File not found"
                })
                return
            
            # Check if user is the owner
            if file["owner"] != self.username:
                self.send_response({
                    "status": "error",
                    "error": "You are not the owner of this file"
                })
                return
            
            # Check if recipient exists
            if recipient not in DEMO_USERS:
                self.send_response({
                    "status": "error",
                    "error": "Recipient not found"
                })
                return
            
            # Generate share link
            share_link = f"https://voidlink.example.com/share/{file_id}"
            
            self.send_response({
                "status": "success",
                "share_link": share_link,
                "message": f"File shared with {recipient}"
            })
    
    def handle_delete_file(self, message):
        """Handle delete_file command"""
        data = message.get("data", {})
        file_id = data.get("file_id")
        
        if not file_id:
            self.send_response({
                "status": "error",
                "error": "File ID is required"
            })
            return
        
        if VOIDLINK_MODULES_LOADED:
            try:
                # Use actual file_transfer module
                metadata = file_transfer.get_file_metadata(file_id)
                if not metadata:
                    self.send_response({
                        "status": "error",
                        "error": "File not found"
                    })
                    return
                
                # Check if user is the owner
                if metadata["owner"] != self.username:
                    self.send_response({
                        "status": "error",
                        "error": "You are not the owner of this file"
                    })
                    return
                
                # Delete file
                file_path = os.path.join(FILES_DIR, file_id)
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # Delete metadata
                metadata_path = os.path.join(METADATA_DIR, f"{file_id}.json")
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
                
                self.send_response({
                    "status": "success",
                    "message": "File deleted successfully"
                })
            
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
                self.send_response({
                    "status": "error",
                    "error": f"Error deleting file: {str(e)}"
                })
        
        else:
            # Demo mode
            global DEMO_FILES
            file = next((f for f in DEMO_FILES if f["id"] == file_id), None)
            if not file:
                self.send_response({
                    "status": "error",
                    "error": "File not found"
                })
                return
            
            # Check if user is the owner
            if file["owner"] != self.username:
                self.send_response({
                    "status": "error",
                    "error": "You are not the owner of this file"
                })
                return
            
            # Remove file from list
            DEMO_FILES = [f for f in DEMO_FILES if f["id"] != file_id]
            
            self.send_response({
                "status": "success",
                "message": "File deleted successfully"
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
            
            # Accept connections
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    
                    # Create handler thread
                    handler = ClientHandler(client_socket, client_address, self)
                    handler.daemon = True
                    handler.start()
                    
                    # Add to clients list
                    self.clients.append(handler)
                    
                    # Clean up finished clients
                    self.clients = [c for c in self.clients if c.is_alive()]
                
                except socket.error as e:
                    if self.running:
                        logger.error(f"Socket error: {e}")
                    break
            
            logger.info("Server stopped")
        
        except socket.error as e:
            logger.error(f"Failed to start server: {e}")
            return False
        
        return True
    
    def stop(self):
        """Stop the server"""
        self.running = False
        
        # Close socket
        if self.socket:
            self.socket.close()
            self.socket = None
        
        # Wait for clients to finish
        for client in self.clients:
            client.running = False
            client.join(1)
        
        logger.info("Server stopped")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="VoidLink Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to listen on (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to listen on (default: {DEFAULT_PORT})")
    
    args = parser.parse_args()
    
    # Create server
    server = VoidLinkServer(args.host, args.port)
    
    # Start server
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    finally:
        server.stop()
    
    return 0

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs(FILES_DIR, exist_ok=True)
    os.makedirs(METADATA_DIR, exist_ok=True)
    
    sys.exit(main())