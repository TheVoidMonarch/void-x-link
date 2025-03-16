#!/usr/bin/env python3
"""
VoidLink Client

A simple client for connecting to a VoidLink server over the network.
"""

import os
import sys
import json
import socket
import argparse
import logging
import time
from getpass import getpass

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voidlink_client')

# Try to import encryption module
try:
    import simple_encryption as encryption
    ENCRYPTION_AVAILABLE = True
    logger.info("Encryption module loaded successfully")
except ImportError:
    ENCRYPTION_AVAILABLE = False
    logger.warning("Encryption module not available, data will be sent unencrypted")

# Constants
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8000
BUFFER_SIZE = 4096
TIMEOUT = 10  # seconds

class VoidLinkClient:
    """Client for connecting to a VoidLink server"""
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        """Initialize the client"""
        self.host = host
        self.port = port
        self.socket = None
        self.username = None
        self.connected = False
    
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(TIMEOUT)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to VoidLink server at {self.host}:{self.port}")
            return True
        except socket.error as e:
            logger.error(f"Failed to connect to server: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            self.socket.close()
            self.socket = None
            self.connected = False
            logger.info("Disconnected from server")
    
    def send_command(self, command, data=None):
        """Send a command to the server"""
        if not self.connected:
            logger.error("Not connected to server")
            return None

        # Prepare message
        message = {
            "command": command,
            "data": data or {}
        }

        # Add authentication if logged in
        if self.username:
            message["username"] = self.username

        # Send message
        try:
            # Convert message to JSON
            json_message = json.dumps(message)

            # Encrypt if encryption is available
            if ENCRYPTION_AVAILABLE:
                try:
                    encrypted_message = encryption.encrypt_message(json_message)
                    self.socket.sendall(encrypted_message.encode('utf-8'))
                except Exception as e:
                    logger.error(f"Encryption error: {e}")
                    # Fall back to unencrypted
                    self.socket.sendall(json_message.encode('utf-8'))
            else:
                # Send unencrypted
                self.socket.sendall(json_message.encode('utf-8'))

            # Wait for response
            response = self.socket.recv(BUFFER_SIZE)
            if not response:
                logger.error("No response from server")
                return None

            # Parse response
            try:
                # Try to decrypt if encryption is available
                if ENCRYPTION_AVAILABLE:
                    try:
                        decrypted_response = encryption.decrypt_message(response.decode('utf-8'))
                        if isinstance(decrypted_response, str):
                            return json.loads(decrypted_response)
                        return decrypted_response
                    except Exception as e:
                        logger.error(f"Decryption error: {e}")
                        # Fall back to unencrypted
                        return json.loads(response.decode('utf-8'))
                else:
                    # Parse unencrypted
                    return json.loads(response.decode('utf-8'))
            except json.JSONDecodeError:
                logger.error("Invalid response from server")
                return None
        except socket.error as e:
            logger.error(f"Error communicating with server: {e}")
            self.connected = False
            return None
    
    def login(self, username, password):
        """Log in to the server"""
        response = self.send_command("login", {
            "username": username,
            "password": password
        })
        
        if response and response.get("status") == "success":
            self.username = username
            logger.info(f"Logged in as {username}")
            return True
        else:
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Login failed: {error}")
            return False
    
    def logout(self):
        """Log out from the server"""
        if not self.username:
            logger.warning("Not logged in")
            return True
        
        response = self.send_command("logout")
        
        if response and response.get("status") == "success":
            self.username = None
            logger.info("Logged out")
            return True
        else:
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Logout failed: {error}")
            return False
    
    def list_files(self):
        """List files on the server"""
        response = self.send_command("list_files")
        
        if response and response.get("status") == "success":
            files = response.get("files", [])
            return files
        else:
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Failed to list files: {error}")
            return None
    
    def upload_file(self, file_path):
        """Upload a file to the server"""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        # Start upload
        response = self.send_command("start_upload", {
            "filename": file_name,
            "size": file_size
        })
        
        if not response or response.get("status") != "ready":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Failed to start upload: {error}")
            return False
        
        # Get upload ID
        upload_id = response.get("upload_id")
        if not upload_id:
            logger.error("No upload ID received from server")
            return False
        
        # Upload file in chunks
        with open(file_path, 'rb') as f:
            bytes_sent = 0
            chunk_size = 1024 * 1024  # 1 MB chunks
            
            while bytes_sent < file_size:
                # Read chunk
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                # Send chunk
                chunk_response = self.send_command("upload_chunk", {
                    "upload_id": upload_id,
                    "chunk_index": bytes_sent // chunk_size,
                    "chunk_data": chunk.hex()  # Convert binary to hex string
                })
                
                if not chunk_response or chunk_response.get("status") != "success":
                    error = chunk_response.get("error", "Unknown error") if chunk_response else "No response from server"
                    logger.error(f"Failed to upload chunk: {error}")
                    return False
                
                # Update progress
                bytes_sent += len(chunk)
                progress = bytes_sent / file_size * 100
                print(f"\rUploading: {progress:.1f}% ({bytes_sent}/{file_size} bytes)", end="")
            
            print()  # New line after progress
        
        # Complete upload
        complete_response = self.send_command("complete_upload", {
            "upload_id": upload_id
        })
        
        if complete_response and complete_response.get("status") == "success":
            logger.info(f"File uploaded successfully: {file_name}")
            return True
        else:
            error = complete_response.get("error", "Unknown error") if complete_response else "No response from server"
            logger.error(f"Failed to complete upload: {error}")
            return False
    
    def download_file(self, file_id, output_path=None):
        """Download a file from the server"""
        # Start download
        response = self.send_command("download_file", {
            "file_id": file_id
        })
        
        if not response or response.get("status") != "ready":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Failed to start download: {error}")
            return False
        
        # Get file info
        file_name = response.get("filename", "unknown")
        file_size = response.get("size", 0)
        
        # Determine output path
        if not output_path:
            output_path = file_name
        
        # Download file in chunks
        with open(output_path, 'wb') as f:
            bytes_received = 0
            chunk_index = 0
            
            while bytes_received < file_size:
                # Request chunk
                chunk_response = self.send_command("download_chunk", {
                    "file_id": file_id,
                    "chunk_index": chunk_index
                })
                
                if not chunk_response or chunk_response.get("status") != "success":
                    error = chunk_response.get("error", "Unknown error") if chunk_response else "No response from server"
                    logger.error(f"Failed to download chunk: {error}")
                    return False
                
                # Get chunk data
                chunk_data = bytes.fromhex(chunk_response.get("chunk_data", ""))
                if not chunk_data:
                    logger.error("Empty chunk received")
                    return False
                
                # Write chunk to file
                f.write(chunk_data)
                
                # Update progress
                bytes_received += len(chunk_data)
                progress = bytes_received / file_size * 100
                print(f"\rDownloading: {progress:.1f}% ({bytes_received}/{file_size} bytes)", end="")
                
                chunk_index += 1
            
            print()  # New line after progress
        
        logger.info(f"File downloaded successfully: {output_path}")
        return True
    
    def share_file(self, file_id, recipient):
        """Share a file with another user"""
        response = self.send_command("share_file", {
            "file_id": file_id,
            "recipient": recipient
        })
        
        if response and response.get("status") == "success":
            share_link = response.get("share_link")
            logger.info(f"File shared successfully with {recipient}")
            if share_link:
                logger.info(f"Share link: {share_link}")
            return True
        else:
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Failed to share file: {error}")
            return False
    
    def delete_file(self, file_id):
        """Delete a file from the server"""
        response = self.send_command("delete_file", {
            "file_id": file_id
        })
        
        if response and response.get("status") == "success":
            logger.info("File deleted successfully")
            return True
        else:
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Failed to delete file: {error}")
            return False

def interactive_mode(client):
    """Run the client in interactive mode"""
    print("VoidLink Client")
    print("==============")
    print(f"Connected to server at {client.host}:{client.port}")
    print()
    
    # Login
    username = input("Username: ")
    password = getpass("Password: ")
    
    if not client.login(username, password):
        print("Login failed. Exiting.")
        return
    
    print()
    print(f"Welcome, {username}!")
    
    # Main loop
    while True:
        print("\nVoidLink Commands:")
        print("1. List Files")
        print("2. Upload File")
        print("3. Download File")
        print("4. Share File")
        print("5. Delete File")
        print("6. Logout and Exit")
        
        choice = input("\nEnter choice (1-6): ")
        
        if choice == "1":
            # List files
            files = client.list_files()
            if files:
                print("\nYour Files:")
                print("-----------")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['name']} ({file['size']}, {file['date']})")
            else:
                print("No files found or error listing files.")
        
        elif choice == "2":
            # Upload file
            file_path = input("Enter file path to upload: ")
            if os.path.exists(file_path):
                print(f"Uploading {file_path}...")
                if client.upload_file(file_path):
                    print("Upload successful!")
                else:
                    print("Upload failed.")
            else:
                print(f"File not found: {file_path}")
        
        elif choice == "3":
            # Download file
            files = client.list_files()
            if files:
                print("\nYour Files:")
                print("-----------")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['name']} ({file['size']}, {file['date']})")
                
                try:
                    file_index = int(input("\nEnter file number to download: ")) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index].get("id")
                        output_path = input(f"Enter output path (default: {files[file_index]['name']}): ")
                        if not output_path:
                            output_path = files[file_index]['name']
                        
                        print(f"Downloading to {output_path}...")
                        if client.download_file(file_id, output_path):
                            print("Download successful!")
                        else:
                            print("Download failed.")
                    else:
                        print("Invalid file number.")
                except ValueError:
                    print("Invalid input.")
            else:
                print("No files found or error listing files.")
        
        elif choice == "4":
            # Share file
            files = client.list_files()
            if files:
                print("\nYour Files:")
                print("-----------")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['name']} ({file['size']}, {file['date']})")
                
                try:
                    file_index = int(input("\nEnter file number to share: ")) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index].get("id")
                        recipient = input("Enter recipient username or email: ")
                        
                        if client.share_file(file_id, recipient):
                            print("File shared successfully!")
                        else:
                            print("Sharing failed.")
                    else:
                        print("Invalid file number.")
                except ValueError:
                    print("Invalid input.")
            else:
                print("No files found or error listing files.")
        
        elif choice == "5":
            # Delete file
            files = client.list_files()
            if files:
                print("\nYour Files:")
                print("-----------")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['name']} ({file['size']}, {file['date']})")
                
                try:
                    file_index = int(input("\nEnter file number to delete: ")) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index].get("id")
                        confirm = input(f"Are you sure you want to delete {files[file_index]['name']}? (y/n): ")
                        
                        if confirm.lower() == 'y':
                            if client.delete_file(file_id):
                                print("File deleted successfully!")
                            else:
                                print("Deletion failed.")
                        else:
                            print("Deletion cancelled.")
                    else:
                        print("Invalid file number.")
                except ValueError:
                    print("Invalid input.")
            else:
                print("No files found or error listing files.")
        
        elif choice == "6":
            # Logout and exit
            client.logout()
            print("Logged out. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="VoidLink Client")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Server hostname or IP (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Server port (default: {DEFAULT_PORT})")
    parser.add_argument("--username", help="Username for authentication")
    parser.add_argument("--password", help="Password for authentication")
    parser.add_argument("--command", choices=["list", "upload", "download", "share", "delete"], help="Command to execute")
    parser.add_argument("--file", help="File path for upload/download/share/delete commands")
    parser.add_argument("--file-id", help="File ID for download/share/delete commands")
    parser.add_argument("--recipient", help="Recipient for share command")
    parser.add_argument("--output", help="Output path for download command")
    
    args = parser.parse_args()
    
    # Create client
    client = VoidLinkClient(args.host, args.port)
    
    # Connect to server
    if not client.connect():
        print("Failed to connect to server. Exiting.")
        return 1
    
    try:
        # Check if we're running a specific command or interactive mode
        if args.command:
            # Login if username and password provided
            if args.username:
                password = args.password or getpass("Password: ")
                if not client.login(args.username, password):
                    print("Login failed. Exiting.")
                    return 1
            
            # Execute command
            if args.command == "list":
                files = client.list_files()
                if files:
                    print("\nFiles:")
                    print("-----")
                    for i, file in enumerate(files):
                        print(f"{i+1}. {file['name']} ({file['size']}, {file['date']})")
                else:
                    print("No files found or error listing files.")
            
            elif args.command == "upload":
                if not args.file:
                    print("Error: --file is required for upload command")
                    return 1
                
                if client.upload_file(args.file):
                    print("Upload successful!")
                else:
                    print("Upload failed.")
            
            elif args.command == "download":
                if not args.file_id:
                    print("Error: --file-id is required for download command")
                    return 1
                
                if client.download_file(args.file_id, args.output):
                    print("Download successful!")
                else:
                    print("Download failed.")
            
            elif args.command == "share":
                if not args.file_id:
                    print("Error: --file-id is required for share command")
                    return 1
                
                if not args.recipient:
                    print("Error: --recipient is required for share command")
                    return 1
                
                if client.share_file(args.file_id, args.recipient):
                    print("File shared successfully!")
                else:
                    print("Sharing failed.")
            
            elif args.command == "delete":
                if not args.file_id:
                    print("Error: --file-id is required for delete command")
                    return 1
                
                if client.delete_file(args.file_id):
                    print("File deleted successfully!")
                else:
                    print("Deletion failed.")
        
        else:
            # Run in interactive mode
            interactive_mode(client)
    
    finally:
        # Disconnect from server
        client.disconnect()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())