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
import traceback
from getpass import getpass

# Add current directory to path to ensure modules can be found
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Try to import device_id module
try:
    from core.device_id import get_device_id
    DEVICE_ID_AVAILABLE = True
except ImportError:
    DEVICE_ID_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voidlink_client')

# Try to import encryption module
try:
    # Add current directory to path to ensure modules can be found
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    # Try to import encryption modules with proper path
    try:
        import fixed_encryption as encryption
        ENCRYPTION_AVAILABLE = True
        logger.info("Encryption module loaded successfully")
    except ImportError:
        try:
            import simple_encryption as encryption
            ENCRYPTION_AVAILABLE = True
            logger.info("Encryption module loaded successfully")
        except ImportError:
            ENCRYPTION_AVAILABLE = False
            logger.warning("Encryption module not available, data will be sent unencrypted")
except Exception as e:
    logger.error(f"Error setting up encryption: {e}")
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
            logger.info(f"Connected to server at {self.host}:{self.port}")
            return True
        except socket.error as e:
            logger.error(f"Failed to connect to server: {e}")
            self.socket = None
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.connected:
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
            
            # Send unencrypted (for simplicity)
            self.socket.sendall(json_message.encode('utf-8'))
            
            # Wait for response
            response = self.socket.recv(BUFFER_SIZE)
            if not response:
                logger.error("No response from server")
                return None
            
            # Parse response
            try:
                # Decode response
                response_text = response.decode('utf-8')
                logger.debug(f"Raw response: {response_text}")
                
                # Try to parse as JSON directly first
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    logger.debug("Response is not valid JSON, trying to decrypt...")
                
                # Try to decrypt if encryption is available
                if ENCRYPTION_AVAILABLE:
                    try:
                        # Check if it's already a JSON string
                        if response_text.startswith('{') and response_text.endswith('}'):
                            try:
                                return json.loads(response_text)
                            except json.JSONDecodeError:
                                pass  # Not valid JSON, continue with decryption

                        decrypted_response = encryption.decrypt_message(response_text)
                        logger.debug(f"Decrypted response: {decrypted_response}")

                        # Return the decrypted response
                        return decrypted_response
                    except Exception as e:
                        logger.error(f"Decryption error: {e}")
                        logger.error(traceback.format_exc())
                        return {"status": "error", "error": f"Decryption error: {str(e)}"}
                else:
                    logger.error("Cannot decrypt response: encryption module not available")
                    return {"status": "error", "error": "Cannot decrypt response: encryption module not available"}
            
            except Exception as e:
                logger.error(f"Error parsing response: {e}")
                logger.error(traceback.format_exc())
                return {"status": "error", "error": f"Error parsing response: {str(e)}"}
        
        except socket.error as e:
            logger.error(f"Error communicating with server: {e}")
            self.connected = False
            return None
    
    def login(self, username, password):
        """Log in to the server"""
        try:
            # Get device ID if available
            device_id = None
            if DEVICE_ID_AVAILABLE:
                try:
                    device_id = get_device_id()
                    logger.info(f"Using device ID: {device_id}")
                except Exception as e:
                    logger.warning(f"Could not get device ID: {e}")

            # Prepare login data
            login_data = {
                "username": username,
                "password": password
            }

            # Add device ID if available
            if device_id:
                login_data["device_id"] = device_id

            # Send login command
            response = self.send_command("login", login_data)

            if not response:
                logger.error("No response from server during login")
                return False

            # Check if the response is a dictionary
            if not isinstance(response, dict):
                logger.error(f"Invalid response type: {type(response)}")
                return False

            # Check if login was successful
            if response.get("status") == "success":
                self.username = username
                logger.info(f"Logged in as {username}")

                # Check for device binding warnings
                if response.get("device_binding") == "new":
                    print("\nIMPORTANT: Your account has been created with permanent credentials.")
                    print("Your username and password cannot be changed.")
                    print("This account can be used on multiple devices.")
                    print("Device ID:", device_id)
                elif response.get("device_binding") == "added":
                    print("\nINFO: This device has been registered to your account.")
                    print("Device ID:", device_id)

                return True
            else:
                error = response.get("error", "Unknown error")
                logger.error(f"Login failed: {error}")

                # Handle specific error cases
                if response.get("reason") == "device_id_required":
                    print("\nERROR: Device ID is required for account creation.")
                    print("Please update your client to the latest version.")

                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def logout(self):
        """Log out from the server"""
        try:
            response = self.send_command("logout")
            
            if not response:
                logger.error("No response from server during logout")
                return False
            
            # Check if the response is a dictionary
            if not isinstance(response, dict):
                logger.error(f"Invalid response type: {type(response)}")
                return False
            
            # Check if logout was successful
            if response.get("status") == "success":
                self.username = None
                logger.info("Logged out")
                return True
            else:
                error = response.get("error", "Unknown error")
                logger.error(f"Logout failed: {error}")
                return False
        
        except Exception as e:
            logger.error(f"Logout error: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def list_files(self):
        """List files on the server"""
        try:
            response = self.send_command("list_files")
            
            if not response:
                logger.error("No response from server when listing files")
                return None
            
            # Check if the response is a dictionary
            if not isinstance(response, dict):
                logger.error(f"Invalid response type: {type(response)}")
                return None
            
            # Check if listing was successful
            if response.get("status") == "success":
                files = response.get("files", [])
                logger.info(f"Listed {len(files)} files")
                return files
            else:
                error = response.get("error", "Unknown error")
                logger.error(f"List files failed: {error}")
                return None
        
        except Exception as e:
            logger.error(f"List files error: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def upload_file(self, file_path):
        """Upload a file to the server"""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        try:
            # Get file info
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Start upload
            response = self.send_command("start_upload", {
                "filename": file_name,
                "size": file_size
            })
            
            if not response:
                logger.error("No response from server when starting upload")
                return False
            
            # Check if the response is a dictionary
            if not isinstance(response, dict):
                logger.error(f"Invalid response type: {type(response)}")
                return False
            
            # Check if upload start was successful
            if response.get("status") != "ready":
                error = response.get("error", "Unknown error")
                logger.error(f"Start upload failed: {error}")
                return False
            
            # Get upload ID
            upload_id = response.get("upload_id")
            if not upload_id:
                logger.error("No upload ID received")
                return False
            
            # Upload file in chunks
            with open(file_path, 'rb') as f:
                chunk_index = 0
                while True:
                    chunk = f.read(BUFFER_SIZE // 2)  # Half buffer size to account for encoding overhead
                    if not chunk:
                        break
                    
                    # Send chunk
                    chunk_response = self.send_command("upload_chunk", {
                        "upload_id": upload_id,
                        "chunk_index": chunk_index,
                        "chunk_data": chunk.hex()
                    })
                    
                    if not chunk_response:
                        logger.error("No response from server when uploading chunk")
                        return False
                    
                    # Check if the response is a dictionary
                    if not isinstance(chunk_response, dict):
                        logger.error(f"Invalid response type: {type(chunk_response)}")
                        return False
                    
                    # Check if chunk upload was successful
                    if chunk_response.get("status") != "success":
                        error = chunk_response.get("error", "Unknown error")
                        logger.error(f"Upload chunk failed: {error}")
                        return False
                    
                    chunk_index += 1
                    
                    # Print progress
                    progress = min(100, int((f.tell() / file_size) * 100))
                    print(f"Uploading: {progress}% complete", end="\r")
            
            # Complete upload
            complete_response = self.send_command("complete_upload", {
                "upload_id": upload_id
            })
            
            if not complete_response:
                logger.error("No response from server when completing upload")
                return False
            
            # Check if the response is a dictionary
            if not isinstance(complete_response, dict):
                logger.error(f"Invalid response type: {type(complete_response)}")
                return False
            
            # Check if upload completion was successful
            if complete_response.get("status") != "success":
                error = complete_response.get("error", "Unknown error")
                logger.error(f"Complete upload failed: {error}")
                return False
            
            print("Upload complete!                ")
            logger.info(f"File uploaded: {file_name}")
            return True
        
        except Exception as e:
            logger.error(f"Upload error: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def download_file(self, file_id, output_path=None):
        """Download a file from the server"""
        try:
            # Start download
            response = self.send_command("download_file", {
                "file_id": file_id
            })
            
            if not response:
                logger.error("No response from server when starting download")
                return False
            
            # Check if the response is a dictionary
            if not isinstance(response, dict):
                logger.error(f"Invalid response type: {type(response)}")
                return False
            
            # Check if download start was successful
            if response.get("status") != "ready":
                error = response.get("error", "Unknown error")
                logger.error(f"Start download failed: {error}")
                return False
            
            # Get download info
            download_id = response.get("download_id")
            filename = response.get("filename")
            file_size = response.get("size")
            
            if not download_id or not filename or not file_size:
                logger.error("Missing download information")
                return False
            
            # Determine output path
            if not output_path:
                output_path = filename
            
            # Download file in chunks
            with open(output_path, 'wb') as f:
                chunk_index = 0
                bytes_received = 0
                
                while bytes_received < file_size:
                    # Request chunk
                    chunk_response = self.send_command("download_chunk", {
                        "file_id": file_id,
                        "chunk_index": chunk_index
                    })
                    
                    if not chunk_response:
                        logger.error("No response from server when downloading chunk")
                        return False
                    
                    # Check if the response is a dictionary
                    if not isinstance(chunk_response, dict):
                        logger.error(f"Invalid response type: {type(chunk_response)}")
                        return False
                    
                    # Check if chunk download was successful
                    if chunk_response.get("status") != "success":
                        error = chunk_response.get("error", "Unknown error")
                        logger.error(f"Download chunk failed: {error}")
                        return False
                    
                    # Get chunk data
                    chunk_data_hex = chunk_response.get("chunk_data")
                    if not chunk_data_hex:
                        logger.error("No chunk data received")
                        return False
                    
                    # Convert hex to bytes
                    chunk_data = bytes.fromhex(chunk_data_hex)
                    
                    # Write chunk
                    f.write(chunk_data)
                    
                    bytes_received += len(chunk_data)
                    chunk_index += 1
                    
                    # Print progress
                    progress = min(100, int((bytes_received / file_size) * 100))
                    print(f"Downloading: {progress}% complete", end="\r")
            
            print("Download complete!                ")
            logger.info(f"File downloaded: {filename}")
            return True
        
        except Exception as e:
            logger.error(f"Download error: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def share_file(self, file_id, recipient):
        """Share a file with another user"""
        try:
            response = self.send_command("share_file", {
                "file_id": file_id,
                "recipient": recipient
            })
            
            if not response:
                logger.error("No response from server when sharing file")
                return False
            
            # Check if the response is a dictionary
            if not isinstance(response, dict):
                logger.error(f"Invalid response type: {type(response)}")
                return False
            
            # Check if sharing was successful
            if response.get("status") == "success":
                logger.info(f"File shared with {recipient}")
                return True
            else:
                error = response.get("error", "Unknown error")
                logger.error(f"Share file failed: {error}")
                return False
        
        except Exception as e:
            logger.error(f"Share file error: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def delete_file(self, file_id):
        """Delete a file"""
        try:
            response = self.send_command("delete_file", {
                "file_id": file_id
            })
            
            if not response:
                logger.error("No response from server when deleting file")
                return False
            
            # Check if the response is a dictionary
            if not isinstance(response, dict):
                logger.error(f"Invalid response type: {type(response)}")
                return False
            
            # Check if deletion was successful
            if response.get("status") == "success":
                logger.info("File deleted")
                return True
            else:
                error = response.get("error", "Unknown error")
                logger.error(f"Delete file failed: {error}")
                return False
        
        except Exception as e:
            logger.error(f"Delete file error: {e}")
            logger.error(traceback.format_exc())
            return False

def interactive_mode(client):
    """Run the client in interactive mode"""
    print("\nVoidLink Client")
    print("==============")
    
    # Login
    while not client.username:
        username = input("Username: ")
        if not username:
            print("Username is required.")
            continue
            
        password = getpass("Password: ")
        if not password:
            print("Password is required.")
            continue
        
        if client.login(username, password):
            print(f"Welcome, {username}!")
            break
        else:
            print("Login failed. Please try again.")
    
    # Main loop
    while True:
        print("\nOptions:")
        print("1. List files")
        print("2. Upload file")
        print("3. Download file")
        print("4. Share file")
        print("5. Delete file")
        print("6. Logout")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ")
        
        if choice == "1":
            # List files
            files = client.list_files()
            if files:
                print("\nFiles:")
                print("-----")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['name']} ({file['size']}, {file['date']})")
            else:
                print("No files found or error listing files.")
        
        elif choice == "2":
            # Upload file
            file_path = input("Enter file path: ")
            if not file_path:
                print("File path is required.")
                continue
            
            if client.upload_file(file_path):
                print("Upload successful!")
            else:
                print("Upload failed.")
        
        elif choice == "3":
            # Download file
            files = client.list_files()
            if not files:
                print("No files found or error listing files.")
                continue
            
            print("\nFiles:")
            print("-----")
            for i, file in enumerate(files):
                print(f"{i+1}. {file['name']} ({file['size']}, {file['date']})")
            
            try:
                index = int(input("\nEnter file number to download: ")) - 1
                if index < 0 or index >= len(files):
                    print("Invalid file number.")
                    continue
                
                file_id = files[index]["id"]
                output_path = input("Enter output path (leave blank for default): ")
                
                if client.download_file(file_id, output_path):
                    print("Download successful!")
                else:
                    print("Download failed.")
            
            except ValueError:
                print("Invalid input.")
        
        elif choice == "4":
            # Share file
            files = client.list_files()
            if not files:
                print("No files found or error listing files.")
                continue
            
            print("\nFiles:")
            print("-----")
            for i, file in enumerate(files):
                print(f"{i+1}. {file['name']} ({file['size']}, {file['date']})")
            
            try:
                index = int(input("\nEnter file number to share: ")) - 1
                if index < 0 or index >= len(files):
                    print("Invalid file number.")
                    continue
                
                file_id = files[index]["id"]
                recipient = input("Enter recipient username: ")
                
                if not recipient:
                    print("Recipient username is required.")
                    continue
                
                if client.share_file(file_id, recipient):
                    print("File shared successfully!")
                else:
                    print("Sharing failed.")
            
            except ValueError:
                print("Invalid input.")
        
        elif choice == "5":
            # Delete file
            files = client.list_files()
            if not files:
                print("No files found or error listing files.")
                continue
            
            print("\nFiles:")
            print("-----")
            for i, file in enumerate(files):
                print(f"{i+1}. {file['name']} ({file['size']}, {file['date']})")
            
            try:
                index = int(input("\nEnter file number to delete: ")) - 1
                if index < 0 or index >= len(files):
                    print("Invalid file number.")
                    continue
                
                file_id = files[index]["id"]
                confirm = input(f"Are you sure you want to delete '{files[index]['name']}'? (y/n): ")
                
                if confirm.lower() != "y":
                    print("Deletion cancelled.")
                    continue
                
                if client.delete_file(file_id):
                    print("File deleted successfully!")
                else:
                    print("Deletion failed.")
            
            except ValueError:
                print("Invalid input.")
        
        elif choice == "6":
            # Logout
            if client.logout():
                print("Logged out successfully.")
                
                # Ask for new login
                while not client.username:
                    username = input("Username: ")
                    if not username:
                        print("Username is required.")
                        continue
                        
                    password = getpass("Password: ")
                    if not password:
                        print("Password is required.")
                        continue
                    
                    if client.login(username, password):
                        print(f"Welcome, {username}!")
                        break
                    else:
                        print("Login failed. Please try again.")
            else:
                print("Logout failed.")
        
        elif choice == "7":
            # Exit
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="VoidLink Client")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Server host (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Server port (default: {DEFAULT_PORT})")
    parser.add_argument("--username", help="Username for login")
    parser.add_argument("--password", help="Password for login (not recommended, will prompt if not provided)")
    parser.add_argument("--command", choices=["list", "upload", "download", "share", "delete"], help="Command to execute")
    parser.add_argument("--file", help="File path for upload command")
    parser.add_argument("--file-id", help="File ID for download, share, or delete commands")
    parser.add_argument("--recipient", help="Recipient username for share command")
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