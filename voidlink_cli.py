#!/usr/bin/env python3
"""
VoidLink CLI - Command Line Interface for VoidLink administration
"""

import os
import sys
import json
import time
import argparse
import getpass
import socket
import threading
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Import VoidLink modules if available
try:
    from encryption import encrypt_message, decrypt_message
    from authentication import authenticate_user, get_user_role, list_users, create_user, delete_user
    from file_transfer import get_file_list, get_file_metadata, delete_file
    from file_transfer_resumable import get_active_transfers, cancel_transfer
    from storage import get_chat_history
    from rooms import get_rooms, create_room, delete_room
    from error_handling import logger, log_info, log_warning, log_error
    
    # Direct connection to server modules
    DIRECT_MODE = True
except ImportError:
    # Remote connection to server
    DIRECT_MODE = False
    
    # Simple encryption functions for remote mode
    def encrypt_message(message):
        """Encrypt a message (simplified version for testing)"""
        if isinstance(message, dict):
            message = json.dumps(message)
        if isinstance(message, str):
            message = message.encode('utf-8')
        return base64.b64encode(message)
    
    def decrypt_message(message):
        """Decrypt a message (simplified version for testing)"""
        try:
            decrypted = base64.b64decode(message)
            try:
                # Try to parse as JSON
                return json.loads(decrypted)
            except:
                # Return as string or bytes
                try:
                    return decrypted.decode('utf-8')
                except:
                    return decrypted
        except:
            return message

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Global variables
server_host = "localhost"
server_port = 52384
admin_username = None
admin_password = None
client_socket = None

def print_header():
    """Print the VoidLink CLI header"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════╗")
    print("║             VoidLink CLI Tool             ║")
    print("║  Secure Terminal-Based Chat & File Share  ║")
    print("╚═══════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def print_info(message):
    """Print an info message"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.ENDC}")

def print_table(headers, rows):
    """Print a formatted table"""
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print headers
    header_row = " | ".join(f"{h:{w}}" for h, w in zip(headers, col_widths))
    print(f"{Colors.BOLD}{header_row}{Colors.ENDC}")
    print("-" * len(header_row))
    
    # Print rows
    for row in rows:
        print(" | ".join(f"{str(cell):{w}}" for cell, w in zip(row, col_widths)))

def connect_to_server():
    """Connect to the VoidLink server"""
    global client_socket
    
    if DIRECT_MODE:
        print_info("Running in direct mode (local server)")
        return True
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))
        print_success(f"Connected to server at {server_host}:{server_port}")
        return True
    except Exception as e:
        print_error(f"Failed to connect to server: {str(e)}")
        return False

def authenticate():
    """Authenticate with the server"""
    global admin_username, admin_password
    
    if DIRECT_MODE:
        # Direct authentication
        try:
            if authenticate_user(admin_username, admin_password):
                role = get_user_role(admin_username)
                if role == "admin":
                    print_success(f"Authenticated as admin user: {admin_username}")
                    return True
                else:
                    print_error("Admin privileges required")
                    return False
            else:
                print_error("Authentication failed")
                return False
        except Exception as e:
            print_error(f"Authentication error: {str(e)}")
            return False
    else:
        # Remote authentication
        try:
            # Create authentication message
            auth_message = {
                "username": admin_username,
                "password": admin_password,
                "admin_cli": True  # Flag to indicate CLI admin connection
            }
            
            # Encrypt and send
            encrypted_auth = encrypt_message(auth_message)
            client_socket.send(encrypted_auth)
            
            # Receive response
            response_data = client_socket.recv(4096)
            response = decrypt_message(response_data)
            
            if isinstance(response, dict) and response.get("type") == "auth_success":
                print_success(f"Authenticated as admin user: {admin_username}")
                return True
            else:
                print_error("Authentication failed")
                return False
        except Exception as e:
            print_error(f"Authentication error: {str(e)}")
            return False

def send_command(command, **kwargs):
    """Send a command to the server"""
    if DIRECT_MODE:
        # Execute command directly
        try:
            if command == "list_users":
                return list_users()
            elif command == "create_user":
                return create_user(kwargs.get("username"), kwargs.get("password"), kwargs.get("role", "user"))
            elif command == "delete_user":
                return delete_user(kwargs.get("username"))
            elif command == "list_files":
                return get_file_list()
            elif command == "file_info":
                return get_file_metadata(kwargs.get("filename"))
            elif command == "delete_file":
                return delete_file(kwargs.get("filename"))
            elif command == "list_rooms":
                return get_rooms()
            elif command == "create_room":
                return create_room(
                    kwargs.get("room_id"),
                    kwargs.get("name", kwargs.get("room_id")),
                    kwargs.get("description", ""),
                    admin_username
                )
            elif command == "delete_room":
                return delete_room(kwargs.get("room_id"), admin_username)
            elif command == "active_transfers":
                return get_active_transfers()
            elif command == "cancel_transfer":
                return cancel_transfer(kwargs.get("transfer_id"))
            elif command == "chat_history":
                return get_chat_history(limit=kwargs.get("limit", 10))
            else:
                print_error(f"Unknown command: {command}")
                return None
        except Exception as e:
            print_error(f"Error executing command: {str(e)}")
            return None
    else:
        # Send command to server
        try:
            # Create command message
            command_message = {
                "type": "admin_command",
                "command": command,
                **kwargs
            }
            
            # Encrypt and send
            encrypted_command = encrypt_message(command_message)
            client_socket.send(encrypted_command)
            
            # Receive response
            response_data = client_socket.recv(4096)
            response = decrypt_message(response_data)
            
            if isinstance(response, dict) and response.get("type") == "command_response":
                return response.get("data")
            else:
                print_error("Invalid response from server")
                return None
        except Exception as e:
            print_error(f"Error sending command: {str(e)}")
            return None

def cmd_users(args):
    """Handle users command"""
    if args.action == "list":
        users = send_command("list_users")
        if users:
            headers = ["Username", "Role", "Created", "Last Login", "Devices"]
            rows = []
            for user in users:
                created = datetime.fromtimestamp(user.get("created_at", 0)).strftime("%Y-%m-%d %H:%M:%S")
                last_login = "Never"
                if user.get("last_login"):
                    last_login = datetime.fromtimestamp(user.get("last_login")).strftime("%Y-%m-%d %H:%M:%S")
                devices = len(user.get("device_ids", []))
                rows.append([user.get("username"), user.get("role"), created, last_login, devices])
            print_table(headers, rows)
        else:
            print_error("Failed to retrieve users")
    
    elif args.action == "add":
        username = args.username
        if not username:
            username = input("Enter username: ")
        
        password = args.password
        if not password:
            password = getpass.getpass("Enter password: ")
        
        role = args.role or "user"
        
        result = send_command("create_user", username=username, password=password, role=role)
        if result:
            print_success(f"User {username} created successfully")
        else:
            print_error(f"Failed to create user {username}")
    
    elif args.action == "delete":
        username = args.username
        if not username:
            username = input("Enter username to delete: ")
        
        if username == admin_username:
            print_error("You cannot delete your own account")
            return
        
        confirm = input(f"Are you sure you want to delete user {username}? (y/n): ")
        if confirm.lower() != "y":
            print_info("Operation cancelled")
            return
        
        result = send_command("delete_user", username=username)
        if result:
            print_success(f"User {username} deleted successfully")
        else:
            print_error(f"Failed to delete user {username}")
    
    else:
        print_error(f"Unknown action: {args.action}")

def cmd_files(args):
    """Handle files command"""
    if args.action == "list":
        files = send_command("list_files")
        if files:
            headers = ["Filename", "Size", "Uploaded By", "Uploaded At", "Security"]
            rows = []
            for file in files:
                size = format_size(file.get("size", 0))
                uploaded = datetime.fromtimestamp(file.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S")
                security = "Unknown"
                if file.get("security_scan"):
                    security = "Safe" if file.get("security_scan", {}).get("is_safe", False) else "Unsafe"
                rows.append([file.get("filename"), size, file.get("uploaded_by"), uploaded, security])
            print_table(headers, rows)
        else:
            print_error("Failed to retrieve files")
    
    elif args.action == "info":
        filename = args.filename
        if not filename:
            filename = input("Enter filename: ")
        
        file_info = send_command("file_info", filename=filename)
        if file_info:
            print(f"{Colors.BOLD}File Information:{Colors.ENDC}")
            print(f"  Filename: {file_info.get('filename')}")
            print(f"  Original Filename: {file_info.get('original_filename')}")
            print(f"  Size: {format_size(file_info.get('size', 0))}")
            print(f"  Uploaded By: {file_info.get('uploaded_by')}")
            print(f"  Uploaded At: {datetime.fromtimestamp(file_info.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  File Path: {file_info.get('path')}")
            print(f"  File Hash: {file_info.get('hash')}")
            
            if file_info.get("security_scan"):
                scan = file_info.get("security_scan")
                print(f"\n{Colors.BOLD}Security Scan Results:{Colors.ENDC}")
                status = "Safe" if scan.get("is_safe", False) else "Unsafe"
                status_color = Colors.GREEN if scan.get("is_safe", False) else Colors.RED
                print(f"  Security Status: {status_color}{status}{Colors.ENDC}")
                
                if not scan.get("is_safe", False):
                    print(f"  Reason: {scan.get('reason')}")
                
                size_check = scan.get("size_check", "UNKNOWN")
                size_color = Colors.GREEN if size_check == "PASSED" else Colors.RED
                print(f"  Size Check: {size_color}{size_check}{Colors.ENDC}")
                
                ext_check = scan.get("extension_check", "UNKNOWN")
                ext_color = Colors.GREEN if ext_check == "PASSED" else Colors.RED
                print(f"  Extension Check: {ext_color}{ext_check}{Colors.ENDC}")
                
                print(f"  MIME Type: {scan.get('mime_type')}")
                
                mime_check = scan.get("mime_check", "UNKNOWN")
                mime_color = Colors.GREEN if mime_check == "PASSED" else Colors.RED
                print(f"  MIME Check: {mime_color}{mime_check}{Colors.ENDC}")
                
                virus_scan = scan.get("virus_scan", "SKIPPED")
                if virus_scan == "PASSED":
                    virus_color = Colors.GREEN
                elif virus_scan == "SKIPPED":
                    virus_color = Colors.YELLOW
                else:
                    virus_color = Colors.RED
                print(f"  Virus Scan: {virus_color}{virus_scan}{Colors.ENDC}")
                
                if virus_scan == "FAILED":
                    print(f"  Virus Name: {scan.get('virus_name')}")
                
                quarantined = "Yes" if scan.get("quarantined", False) else "No"
                quarantine_color = Colors.YELLOW if scan.get("quarantined", False) else Colors.GREEN
                print(f"  Quarantined: {quarantine_color}{quarantined}{Colors.ENDC}")
                
                if scan.get("quarantined", False):
                    print(f"  Quarantine Path: {scan.get('quarantine_path')}")
                
                print(f"  Scan Duration: {scan.get('scan_duration', 0):.2f} seconds")
        else:
            print_error(f"Failed to retrieve information for file {filename}")
    
    elif args.action == "delete":
        filename = args.filename
        if not filename:
            filename = input("Enter filename to delete: ")
        
        confirm = input(f"Are you sure you want to delete file {filename}? (y/n): ")
        if confirm.lower() != "y":
            print_info("Operation cancelled")
            return
        
        result = send_command("delete_file", filename=filename)
        if result:
            print_success(f"File {filename} deleted successfully")
        else:
            print_error(f"Failed to delete file {filename}")
    
    else:
        print_error(f"Unknown action: {args.action}")

def cmd_rooms(args):
    """Handle rooms command"""
    if args.action == "list":
        rooms = send_command("list_rooms")
        if rooms:
            headers = ["Room ID", "Name", "Description", "Created By", "Members"]
            rows = []
            for room_id, room in rooms.items():
                rows.append([
                    room_id,
                    room.get("name"),
                    room.get("description"),
                    room.get("created_by"),
                    len(room.get("members", []))
                ])
            print_table(headers, rows)
        else:
            print_error("Failed to retrieve rooms")
    
    elif args.action == "create":
        room_id = args.room_id
        if not room_id:
            room_id = input("Enter room ID: ")
        
        name = args.name or room_id
        description = args.description or f"Room created by {admin_username}"
        
        result = send_command("create_room", room_id=room_id, name=name, description=description)
        if result:
            print_success(f"Room {room_id} created successfully")
        else:
            print_error(f"Failed to create room {room_id}")
    
    elif args.action == "delete":
        room_id = args.room_id
        if not room_id:
            room_id = input("Enter room ID to delete: ")
        
        if room_id == "general":
            print_error("Cannot delete the general room")
            return
        
        confirm = input(f"Are you sure you want to delete room {room_id}? (y/n): ")
        if confirm.lower() != "y":
            print_info("Operation cancelled")
            return
        
        result = send_command("delete_room", room_id=room_id)
        if result:
            print_success(f"Room {room_id} deleted successfully")
        else:
            print_error(f"Failed to delete room {room_id}")
    
    else:
        print_error(f"Unknown action: {args.action}")

def cmd_transfers(args):
    """Handle transfers command"""
    if args.action == "list":
        transfers = send_command("active_transfers")
        if transfers:
            headers = ["Transfer ID", "Filename", "Size", "Progress", "Speed", "Sender"]
            rows = []
            for transfer_id, transfer in transfers.items():
                progress = f"{transfer.get('percent', 0):.1f}%"
                speed = format_size(transfer.get('speed', 0)) + "/s"
                rows.append([
                    transfer_id,
                    transfer.get("filename"),
                    format_size(transfer.get("total_size", 0)),
                    progress,
                    speed,
                    transfer.get("sender", "Unknown")
                ])
            print_table(headers, rows)
        else:
            print_info("No active transfers")
    
    elif args.action == "cancel":
        transfer_id = args.transfer_id
        if not transfer_id:
            transfer_id = input("Enter transfer ID to cancel: ")
        
        confirm = input(f"Are you sure you want to cancel transfer {transfer_id}? (y/n): ")
        if confirm.lower() != "y":
            print_info("Operation cancelled")
            return
        
        result = send_command("cancel_transfer", transfer_id=transfer_id)
        if result:
            print_success(f"Transfer {transfer_id} cancelled successfully")
        else:
            print_error(f"Failed to cancel transfer {transfer_id}")
    
    else:
        print_error(f"Unknown action: {args.action}")

def cmd_history(args):
    """Handle history command"""
    limit = args.limit or 10
    history = send_command("chat_history", limit=limit)
    
    if history:
        headers = ["Time", "Sender", "Recipient", "Room", "Message"]
        rows = []
        for message in history:
            time_str = datetime.fromtimestamp(message.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S")
            recipient = message.get("recipient", "all")
            room = message.get("room", "general")
            rows.append([
                time_str,
                message.get("sender"),
                recipient,
                room,
                message.get("content")
            ])
        print_table(headers, rows)
    else:
        print_error("Failed to retrieve chat history")

def format_size(size_bytes):
    """Format size in bytes to human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def main():
    """Main function"""
    global server_host, server_port, admin_username, admin_password
    
    # Create argument parser
    parser = argparse.ArgumentParser(description="VoidLink CLI - Command Line Interface for VoidLink administration")
    parser.add_argument("--host", help="Server hostname or IP address", default="localhost")
    parser.add_argument("--port", type=int, help="Server port", default=52384)
    parser.add_argument("--username", help="Admin username")
    parser.add_argument("--password", help="Admin password")
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Users command
    users_parser = subparsers.add_parser("users", help="User management")
    users_subparsers = users_parser.add_subparsers(dest="action", help="Action to perform")
    
    # Users list
    users_list_parser = users_subparsers.add_parser("list", help="List users")
    
    # Users add
    users_add_parser = users_subparsers.add_parser("add", help="Add a user")
    users_add_parser.add_argument("--username", help="Username")
    users_add_parser.add_argument("--password", help="Password")
    users_add_parser.add_argument("--role", help="User role (user or admin)", choices=["user", "admin"], default="user")
    
    # Users delete
    users_delete_parser = users_subparsers.add_parser("delete", help="Delete a user")
    users_delete_parser.add_argument("--username", help="Username to delete")
    
    # Files command
    files_parser = subparsers.add_parser("files", help="File management")
    files_subparsers = files_parser.add_subparsers(dest="action", help="Action to perform")
    
    # Files list
    files_list_parser = files_subparsers.add_parser("list", help="List files")
    
    # Files info
    files_info_parser = files_subparsers.add_parser("info", help="Get file information")
    files_info_parser.add_argument("--filename", help="Filename")
    
    # Files delete
    files_delete_parser = files_subparsers.add_parser("delete", help="Delete a file")
    files_delete_parser.add_argument("--filename", help="Filename to delete")
    
    # Rooms command
    rooms_parser = subparsers.add_parser("rooms", help="Room management")
    rooms_subparsers = rooms_parser.add_subparsers(dest="action", help="Action to perform")
    
    # Rooms list
    rooms_list_parser = rooms_subparsers.add_parser("list", help="List rooms")
    
    # Rooms create
    rooms_create_parser = rooms_subparsers.add_parser("create", help="Create a room")
    rooms_create_parser.add_argument("--room-id", help="Room ID")
    rooms_create_parser.add_argument("--name", help="Room name")
    rooms_create_parser.add_argument("--description", help="Room description")
    
    # Rooms delete
    rooms_delete_parser = rooms_subparsers.add_parser("delete", help="Delete a room")
    rooms_delete_parser.add_argument("--room-id", help="Room ID to delete")
    
    # Transfers command
    transfers_parser = subparsers.add_parser("transfers", help="Transfer management")
    transfers_subparsers = transfers_parser.add_subparsers(dest="action", help="Action to perform")
    
    # Transfers list
    transfers_list_parser = transfers_subparsers.add_parser("list", help="List active transfers")
    
    # Transfers cancel
    transfers_cancel_parser = transfers_subparsers.add_parser("cancel", help="Cancel a transfer")
    transfers_cancel_parser.add_argument("--transfer-id", help="Transfer ID to cancel")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Chat history")
    history_parser.add_argument("--limit", type=int, help="Maximum number of messages to retrieve", default=10)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set global variables
    server_host = args.host
    server_port = args.port
    admin_username = args.username
    admin_password = args.password
    
    # Print header
    print_header()
    
    # Check if command is specified
    if not args.command:
        parser.print_help()
        return
    
    # Prompt for username and password if not provided
    if not admin_username:
        admin_username = input("Admin username: ")
    
    if not admin_password:
        admin_password = getpass.getpass("Admin password: ")
    
    # Connect to server
    if not connect_to_server():
        return
    
    # Authenticate
    if not authenticate():
        return
    
    # Execute command
    if args.command == "users":
        cmd_users(args)
    elif args.command == "files":
        cmd_files(args)
    elif args.command == "rooms":
        cmd_rooms(args)
    elif args.command == "transfers":
        cmd_transfers(args)
    elif args.command == "history":
        cmd_history(args)
    else:
        print_error(f"Unknown command: {args.command}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    finally:
        # Close socket if open
        if client_socket:
            try:
                client_socket.close()
            except:
                pass