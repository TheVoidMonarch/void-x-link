#!/usr/bin/env python3
"""
VoidLink Chat Client

A client for using the chat and private messaging features of VoidLink.
"""

import os
import sys
import json
import socket
import argparse
import logging
import time
import threading
import traceback
from getpass import getpass
from datetime import datetime

# Add current directory to path to ensure modules can be found
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import client module
from client import VoidLinkClient, DEFAULT_HOST, DEFAULT_PORT, ENCRYPTION_AVAILABLE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voidlink_chat_client')

class VoidLinkChatClient(VoidLinkClient):
    """Extended client for VoidLink chat functionality"""
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        """Initialize the chat client"""
        super().__init__(host, port)
        self.current_room = None
        self.notification_thread = None
        self.running = False
        self.unread_counts = {}
    
    def start_notification_listener(self):
        """Start a thread to listen for notifications"""
        if self.notification_thread is not None:
            return
        
        self.running = True
        self.notification_thread = threading.Thread(target=self.notification_listener)
        self.notification_thread.daemon = True
        self.notification_thread.start()
    
    def stop_notification_listener(self):
        """Stop the notification listener thread"""
        self.running = False
        if self.notification_thread is not None:
            self.notification_thread.join(1)
            self.notification_thread = None
    
    def notification_listener(self):
        """Listen for notifications from the server"""
        while self.running and self.connected:
            try:
                # Check if there's data available
                self.socket.settimeout(0.5)
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        continue
                    
                    # Parse notification
                    try:
                        # Try to decrypt if encryption is available
                        if ENCRYPTION_AVAILABLE:
                            try:
                                from simple_encryption import decrypt_message
                                decrypted_data = decrypt_message(data.decode('utf-8'))
                                notification = decrypted_data
                            except:
                                # Fall back to unencrypted
                                notification = json.loads(data.decode('utf-8'))
                        else:
                            # Parse as JSON directly
                            notification = json.loads(data.decode('utf-8'))
                        
                        # Handle notification
                        self.handle_notification(notification)
                    except Exception as e:
                        logger.error(f"Error parsing notification: {e}")
                except socket.timeout:
                    # No data available, continue
                    continue
            except Exception as e:
                logger.error(f"Error in notification listener: {e}")
                time.sleep(1)
    
    def handle_notification(self, notification):
        """Handle a notification from the server"""
        notification_type = notification.get("notification")
        data = notification.get("data", {})
        
        if notification_type == "new_room_message":
            # New message in a chat room
            room_id = data.get("room_id")
            message = data.get("message", {})
            
            # Print notification if not in the room
            if self.current_room != room_id:
                print(f"\n[NEW MESSAGE] {message.get('username')} in {room_id}: {message.get('content')}")
                print("Type your message or command: ", end="", flush=True)
            else:
                # Print message in current room view
                self.print_message(message)
        
        elif notification_type == "new_private_message":
            # New private message
            message = data.get("message", {})
            from_username = message.get("from_username")
            
            # Update unread counts
            if from_username not in self.unread_counts:
                self.unread_counts[from_username] = 0
            self.unread_counts[from_username] += 1
            
            # Print notification
            print(f"\n[WHISPER] {from_username}: {message.get('content')}")
            print("Type your message or command: ", end="", flush=True)
    
    def list_rooms(self):
        """List available chat rooms"""
        response = self.send_command("list_rooms")
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error listing rooms: {error}")
            return None
        
        return response.get("rooms", [])
    
    def create_room(self, name, description="", is_public=True, members=None):
        """Create a new chat room"""
        response = self.send_command("create_room", {
            "name": name,
            "description": description,
            "is_public": is_public,
            "members": members or []
        })
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error creating room: {error}")
            return None
        
        return response.get("room_id")
    
    def delete_room(self, room_id):
        """Delete a chat room"""
        response = self.send_command("delete_room", {
            "room_id": room_id
        })
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error deleting room: {error}")
            return False
        
        return True
    
    def join_room(self, room_id):
        """Join a chat room"""
        response = self.send_command("join_room", {
            "room_id": room_id
        })
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error joining room: {error}")
            return False
        
        return True
    
    def leave_room(self, room_id):
        """Leave a chat room"""
        response = self.send_command("leave_room", {
            "room_id": room_id
        })
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error leaving room: {error}")
            return False
        
        return True
    
    def get_room_messages(self, room_id, limit=50, before_timestamp=None):
        """Get messages from a chat room"""
        response = self.send_command("get_room_messages", {
            "room_id": room_id,
            "limit": limit,
            "before_timestamp": before_timestamp
        })
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error getting room messages: {error}")
            return None
        
        return response.get("messages", [])
    
    def send_room_message(self, room_id, content):
        """Send a message to a chat room"""
        response = self.send_command("send_room_message", {
            "room_id": room_id,
            "content": content
        })
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error sending room message: {error}")
            return None
        
        return response.get("message")
    
    def get_private_messages(self, username, limit=50, before_timestamp=None):
        """Get private messages with another user"""
        response = self.send_command("get_private_messages", {
            "username": username,
            "limit": limit,
            "before_timestamp": before_timestamp
        })
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error getting private messages: {error}")
            return None
        
        # Reset unread count for this user
        if username in self.unread_counts:
            self.unread_counts[username] = 0
        
        return response.get("messages", [])
    
    def send_private_message(self, username, content):
        """Send a private message to another user"""
        response = self.send_command("send_private_message", {
            "username": username,
            "content": content
        })
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error sending private message: {error}")
            return None
        
        return response.get("message")
    
    def mark_messages_read(self, username):
        """Mark messages from a user as read"""
        response = self.send_command("mark_messages_read", {
            "username": username
        })
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error marking messages as read: {error}")
            return False
        
        # Reset unread count for this user
        if username in self.unread_counts:
            self.unread_counts[username] = 0
        
        return True
    
    def get_unread_counts(self):
        """Get counts of unread private messages"""
        response = self.send_command("get_unread_counts")
        
        if not response or response.get("status") != "success":
            error = response.get("error", "Unknown error") if response else "No response from server"
            logger.error(f"Error getting unread counts: {error}")
            return None
        
        # Update local unread counts
        self.unread_counts = response.get("unread_counts", {})
        
        return self.unread_counts
    
    def print_message(self, message):
        """Print a chat message with formatting"""
        timestamp = message.get("timestamp", 0)
        time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
        
        if "room_id" in message:
            # Room message
            print(f"[{time_str}] {message.get('username')}: {message.get('content')}")
        else:
            # Private message
            if message.get("from_username") == self.username:
                print(f"[{time_str}] You -> {message.get('to_username')}: {message.get('content')}")
            else:
                print(f"[{time_str}] {message.get('from_username')} -> You: {message.get('content')}")
    
    def enter_room(self, room_id):
        """Enter a chat room and display messages"""
        # Get room messages
        messages = self.get_room_messages(room_id)
        if messages is None:
            print(f"Error: Could not get messages for room {room_id}")
            return False
        
        # Set current room
        self.current_room = room_id
        
        # Display room header
        print(f"\n===== Room: {room_id} =====")
        print("Type your message or /help for commands")
        print("=" * 30)
        
        # Display messages (newest last)
        messages.reverse()
        for message in messages:
            self.print_message(message)
        
        return True
    
    def enter_private_chat(self, username):
        """Enter a private chat with another user"""
        # Get private messages
        messages = self.get_private_messages(username)
        if messages is None:
            print(f"Error: Could not get messages with {username}")
            return False
        
        # Set current room to None (private chat mode)
        self.current_room = None
        
        # Display chat header
        print(f"\n===== Private Chat with {username} =====")
        print("Type your message or /help for commands")
        print("=" * 40)
        
        # Display messages (newest last)
        messages.reverse()
        for message in messages:
            self.print_message(message)
        
        return True
    
    def run_chat_interface(self):
        """Run the interactive chat interface"""
        if not self.connected or not self.username:
            print("Error: Not connected or not logged in")
            return
        
        # Start notification listener
        self.start_notification_listener()
        
        # Get unread counts
        self.get_unread_counts()
        
        # Show unread messages
        if self.unread_counts:
            print("\nYou have unread messages from:")
            for username, count in self.unread_counts.items():
                print(f"  {username}: {count} message(s)")
        
        # Main chat loop
        try:
            print("\nWelcome to VoidLink Chat!")
            print("Type /help for available commands")
            
            current_chat_partner = None
            
            while self.connected:
                if self.current_room:
                    prompt = f"[{self.current_room}] "
                elif current_chat_partner:
                    prompt = f"[PM: {current_chat_partner}] "
                else:
                    prompt = ""
                
                user_input = input(f"{prompt}> ")
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    parts = user_input.split()
                    command = parts[0].lower()
                    
                    if command == "/help":
                        print("\nAvailable commands:")
                        print("  /rooms - List available chat rooms")
                        print("  /create <name> [description] - Create a new chat room")
                        print("  /join <room_id> - Join a chat room")
                        print("  /leave - Leave the current room")
                        print("  /whisper <username> <message> - Send a private message")
                        print("  /pm <username> - Start a private chat session")
                        print("  /exit - Exit private chat or current room")
                        print("  /quit - Disconnect and exit")
                        print("  /unread - Show unread message counts")
                    
                    elif command == "/rooms":
                        rooms = self.list_rooms()
                        if rooms:
                            print("\nAvailable rooms:")
                            for room in rooms:
                                print(f"  {room['id']} - {room['name']}: {room['description']}")
                        else:
                            print("No rooms available")
                    
                    elif command == "/create":
                        if len(parts) < 2:
                            print("Usage: /create <name> [description]")
                            continue
                        
                        name = parts[1]
                        description = " ".join(parts[2:]) if len(parts) > 2 else ""
                        
                        room_id = self.create_room(name, description)
                        if room_id:
                            print(f"Room created: {room_id}")
                            # Enter the new room
                            self.enter_room(room_id)
                        else:
                            print("Error creating room")
                    
                    elif command == "/join":
                        if len(parts) < 2:
                            print("Usage: /join <room_id>")
                            continue
                        
                        room_id = parts[1]
                        if self.join_room(room_id):
                            self.enter_room(room_id)
                        else:
                            print(f"Error joining room {room_id}")
                    
                    elif command == "/leave":
                        if not self.current_room:
                            print("Not in a room")
                            continue
                        
                        room_id = self.current_room
                        if self.leave_room(room_id):
                            print(f"Left room {room_id}")
                            self.current_room = None
                        else:
                            print(f"Error leaving room {room_id}")
                    
                    elif command == "/whisper":
                        if len(parts) < 3:
                            print("Usage: /whisper <username> <message>")
                            continue
                        
                        username = parts[1]
                        content = " ".join(parts[2:])
                        
                        message = self.send_private_message(username, content)
                        if message:
                            print(f"Message sent to {username}")
                        else:
                            print(f"Error sending message to {username}")
                    
                    elif command == "/pm":
                        if len(parts) < 2:
                            print("Usage: /pm <username>")
                            continue
                        
                        username = parts[1]
                        if self.enter_private_chat(username):
                            current_chat_partner = username
                        else:
                            print(f"Error starting private chat with {username}")
                    
                    elif command == "/exit":
                        if self.current_room:
                            print(f"Exited room {self.current_room}")
                            self.current_room = None
                        elif current_chat_partner:
                            print(f"Exited private chat with {current_chat_partner}")
                            current_chat_partner = None
                        else:
                            print("Not in a room or private chat")
                    
                    elif command == "/quit":
                        print("Disconnecting...")
                        break
                    
                    elif command == "/unread":
                        unread = self.get_unread_counts()
                        if unread:
                            print("\nUnread messages:")
                            for username, count in unread.items():
                                print(f"  {username}: {count} message(s)")
                        else:
                            print("No unread messages")
                    
                    else:
                        print(f"Unknown command: {command}")
                        print("Type /help for available commands")
                
                else:
                    # Send message
                    if self.current_room:
                        # Send to current room
                        message = self.send_room_message(self.current_room, user_input)
                        if not message:
                            print("Error sending message")
                    elif current_chat_partner:
                        # Send private message
                        message = self.send_private_message(current_chat_partner, user_input)
                        if not message:
                            print("Error sending message")
                    else:
                        print("Not in a room or private chat")
                        print("Type /help for available commands")
        
        except KeyboardInterrupt:
            print("\nExiting chat...")
        finally:
            # Stop notification listener
            self.stop_notification_listener()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="VoidLink Chat Client")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Server host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Server port")
    args = parser.parse_args()
    
    # Create client
    client = VoidLinkChatClient(args.host, args.port)
    
    try:
        # Connect to server
        if not client.connect():
            print("Error: Could not connect to server")
            return
        
        # Login
        username = input("Username: ")
        password = getpass("Password: ")
        
        if not client.login(username, password):
            print("Error: Login failed")
            client.disconnect()
            return
        
        # Run chat interface
        client.run_chat_interface()
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Disconnect
        client.disconnect()

if __name__ == "__main__":
    main()