#!/usr/bin/env python3
"""
VoidLink Chat Module - Provides chat room and private messaging functionality
"""

import os
import json
import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voidlink_chat')

# Constants
CHAT_DIR = "database/chat"
ROOMS_FILE = os.path.join(CHAT_DIR, "rooms.json")
MESSAGES_DIR = os.path.join(CHAT_DIR, "messages")
PRIVATE_MESSAGES_DIR = os.path.join(CHAT_DIR, "private")
MAX_MESSAGES_PER_ROOM = 1000  # Maximum number of messages to keep per room
MAX_PRIVATE_MESSAGES = 500  # Maximum number of private messages to keep per user pair

# Ensure directories exist
def ensure_chat_dirs():
    """Ensure chat directories exist"""
    os.makedirs(CHAT_DIR, exist_ok=True)
    os.makedirs(MESSAGES_DIR, exist_ok=True)
    os.makedirs(PRIVATE_MESSAGES_DIR, exist_ok=True)
    
    # Initialize rooms file if it doesn't exist
    if not os.path.exists(ROOMS_FILE):
        with open(ROOMS_FILE, 'w') as f:
            json.dump({
                "general": {
                    "name": "General",
                    "description": "General discussion",
                    "created_by": "system",
                    "created_at": time.time(),
                    "is_public": True,
                    "members": []  # For private rooms, this would contain allowed users
                }
            }, f, indent=4)
        logger.info("Created default chat rooms file")

# Room Management
def get_rooms(username: str = None) -> Dict[str, Dict[str, Any]]:
    """
    Get available chat rooms
    
    Args:
        username: If provided, only return rooms the user has access to
        
    Returns:
        Dictionary of room_id -> room_info
    """
    ensure_chat_dirs()
    
    try:
        with open(ROOMS_FILE, 'r') as f:
            rooms = json.load(f)
        
        # Filter rooms if username is provided
        if username:
            filtered_rooms = {}
            for room_id, room_info in rooms.items():
                # Include room if it's public or user is a member
                if room_info.get("is_public", False) or username in room_info.get("members", []):
                    filtered_rooms[room_id] = room_info
            return filtered_rooms
        
        return rooms
    except Exception as e:
        logger.error(f"Error getting rooms: {e}")
        return {}

def create_room(name: str, description: str, created_by: str, is_public: bool = True, 
               members: List[str] = None) -> Optional[str]:
    """
    Create a new chat room
    
    Args:
        name: Room name
        description: Room description
        created_by: Username of creator
        is_public: Whether the room is public
        members: List of usernames allowed in the room (for private rooms)
        
    Returns:
        Room ID if successful, None otherwise
    """
    ensure_chat_dirs()
    
    try:
        # Generate room ID
        room_id = name.lower().replace(' ', '_')
        
        # Ensure unique room ID
        rooms = get_rooms()
        if room_id in rooms:
            # Append timestamp to make unique
            room_id = f"{room_id}_{int(time.time())}"
        
        # Create room info
        room_info = {
            "name": name,
            "description": description,
            "created_by": created_by,
            "created_at": time.time(),
            "is_public": is_public,
            "members": members or []
        }
        
        # Add creator to members if private room
        if not is_public and created_by not in room_info["members"]:
            room_info["members"].append(created_by)
        
        # Add room to rooms file
        rooms[room_id] = room_info
        
        with open(ROOMS_FILE, 'w') as f:
            json.dump(rooms, f, indent=4)
        
        logger.info(f"Created new room: {name} ({room_id})")
        return room_id
    except Exception as e:
        logger.error(f"Error creating room: {e}")
        return None

def delete_room(room_id: str, username: str) -> bool:
    """
    Delete a chat room
    
    Args:
        room_id: Room ID to delete
        username: Username of user attempting to delete
        
    Returns:
        True if successful, False otherwise
    """
    ensure_chat_dirs()
    
    try:
        rooms = get_rooms()
        
        if room_id not in rooms:
            logger.warning(f"Room not found: {room_id}")
            return False
        
        # Check if user is allowed to delete the room
        room_info = rooms[room_id]
        if room_info["created_by"] != username and username != "admin":
            logger.warning(f"User {username} not allowed to delete room {room_id}")
            return False
        
        # Delete room from rooms file
        del rooms[room_id]
        
        with open(ROOMS_FILE, 'w') as f:
            json.dump(rooms, f, indent=4)
        
        # Delete room messages file if it exists
        room_file = os.path.join(MESSAGES_DIR, f"{room_id}.json")
        if os.path.exists(room_file):
            os.remove(room_file)
        
        logger.info(f"Deleted room: {room_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting room: {e}")
        return False

def join_room(room_id: str, username: str) -> bool:
    """
    Join a chat room
    
    Args:
        room_id: Room ID to join
        username: Username of user joining
        
    Returns:
        True if successful, False otherwise
    """
    ensure_chat_dirs()
    
    try:
        rooms = get_rooms()
        
        if room_id not in rooms:
            logger.warning(f"Room not found: {room_id}")
            return False
        
        room_info = rooms[room_id]
        
        # Check if room is public or user is already a member
        if room_info.get("is_public", False):
            # Public rooms don't need explicit membership
            return True
        
        if username in room_info.get("members", []):
            # Already a member
            return True
        
        # Add user to members
        if "members" not in room_info:
            room_info["members"] = []
        
        room_info["members"].append(username)
        
        # Update rooms file
        with open(ROOMS_FILE, 'w') as f:
            json.dump(rooms, f, indent=4)
        
        logger.info(f"User {username} joined room {room_id}")
        return True
    except Exception as e:
        logger.error(f"Error joining room: {e}")
        return False

def leave_room(room_id: str, username: str) -> bool:
    """
    Leave a chat room
    
    Args:
        room_id: Room ID to leave
        username: Username of user leaving
        
    Returns:
        True if successful, False otherwise
    """
    ensure_chat_dirs()
    
    try:
        rooms = get_rooms()
        
        if room_id not in rooms:
            logger.warning(f"Room not found: {room_id}")
            return False
        
        room_info = rooms[room_id]
        
        # Check if room is private and user is a member
        if not room_info.get("is_public", False):
            if username in room_info.get("members", []):
                room_info["members"].remove(username)
                
                # Update rooms file
                with open(ROOMS_FILE, 'w') as f:
                    json.dump(rooms, f, indent=4)
                
                logger.info(f"User {username} left room {room_id}")
        
        return True
    except Exception as e:
        logger.error(f"Error leaving room: {e}")
        return False

# Message Management
def get_room_messages(room_id: str, limit: int = 50, before_timestamp: float = None) -> List[Dict[str, Any]]:
    """
    Get messages from a chat room
    
    Args:
        room_id: Room ID to get messages from
        limit: Maximum number of messages to return
        before_timestamp: Only return messages before this timestamp
        
    Returns:
        List of messages, newest first
    """
    ensure_chat_dirs()
    
    try:
        room_file = os.path.join(MESSAGES_DIR, f"{room_id}.json")
        
        if not os.path.exists(room_file):
            return []
        
        with open(room_file, 'r') as f:
            messages = json.load(f)
        
        # Filter by timestamp if provided
        if before_timestamp is not None:
            messages = [msg for msg in messages if msg.get("timestamp", 0) < before_timestamp]
        
        # Sort by timestamp (newest first) and limit
        messages.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return messages[:limit]
    except Exception as e:
        logger.error(f"Error getting room messages: {e}")
        return []

def send_room_message(room_id: str, username: str, content: str) -> Optional[Dict[str, Any]]:
    """
    Send a message to a chat room
    
    Args:
        room_id: Room ID to send message to
        username: Username of sender
        content: Message content
        
    Returns:
        Message object if successful, None otherwise
    """
    ensure_chat_dirs()
    
    try:
        rooms = get_rooms()
        
        if room_id not in rooms:
            logger.warning(f"Room not found: {room_id}")
            return None
        
        room_info = rooms[room_id]
        
        # Check if user has access to the room
        if not room_info.get("is_public", False) and username not in room_info.get("members", []):
            logger.warning(f"User {username} not allowed to send message to room {room_id}")
            return None
        
        # Create message
        message = {
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "username": username,
            "content": content,
            "timestamp": time.time()
        }
        
        # Load existing messages
        room_file = os.path.join(MESSAGES_DIR, f"{room_id}.json")
        
        if os.path.exists(room_file):
            with open(room_file, 'r') as f:
                messages = json.load(f)
        else:
            messages = []
        
        # Add new message
        messages.append(message)
        
        # Limit number of messages
        if len(messages) > MAX_MESSAGES_PER_ROOM:
            # Sort by timestamp (oldest first) and remove oldest
            messages.sort(key=lambda x: x.get("timestamp", 0))
            messages = messages[-MAX_MESSAGES_PER_ROOM:]
        
        # Save messages
        with open(room_file, 'w') as f:
            json.dump(messages, f, indent=4)
        
        logger.info(f"User {username} sent message to room {room_id}")
        return message
    except Exception as e:
        logger.error(f"Error sending room message: {e}")
        return None

# Private Messaging (Whisper)
def get_private_messages(username1: str, username2: str, limit: int = 50, 
                        before_timestamp: float = None) -> List[Dict[str, Any]]:
    """
    Get private messages between two users
    
    Args:
        username1: First username
        username2: Second username
        limit: Maximum number of messages to return
        before_timestamp: Only return messages before this timestamp
        
    Returns:
        List of messages, newest first
    """
    ensure_chat_dirs()
    
    try:
        # Sort usernames to ensure consistent file naming
        users = sorted([username1, username2])
        pm_file = os.path.join(PRIVATE_MESSAGES_DIR, f"{users[0]}_{users[1]}.json")
        
        if not os.path.exists(pm_file):
            return []
        
        with open(pm_file, 'r') as f:
            messages = json.load(f)
        
        # Filter by timestamp if provided
        if before_timestamp is not None:
            messages = [msg for msg in messages if msg.get("timestamp", 0) < before_timestamp]
        
        # Sort by timestamp (newest first) and limit
        messages.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return messages[:limit]
    except Exception as e:
        logger.error(f"Error getting private messages: {e}")
        return []

def send_private_message(from_username: str, to_username: str, content: str) -> Optional[Dict[str, Any]]:
    """
    Send a private message (whisper)
    
    Args:
        from_username: Username of sender
        to_username: Username of recipient
        content: Message content
        
    Returns:
        Message object if successful, None otherwise
    """
    ensure_chat_dirs()
    
    try:
        # Create message
        message = {
            "id": str(uuid.uuid4()),
            "from_username": from_username,
            "to_username": to_username,
            "content": content,
            "timestamp": time.time(),
            "read": False
        }
        
        # Sort usernames to ensure consistent file naming
        users = sorted([from_username, to_username])
        pm_file = os.path.join(PRIVATE_MESSAGES_DIR, f"{users[0]}_{users[1]}.json")
        
        # Load existing messages
        if os.path.exists(pm_file):
            with open(pm_file, 'r') as f:
                messages = json.load(f)
        else:
            messages = []
        
        # Add new message
        messages.append(message)
        
        # Limit number of messages
        if len(messages) > MAX_PRIVATE_MESSAGES:
            # Sort by timestamp (oldest first) and remove oldest
            messages.sort(key=lambda x: x.get("timestamp", 0))
            messages = messages[-MAX_PRIVATE_MESSAGES:]
        
        # Save messages
        with open(pm_file, 'w') as f:
            json.dump(messages, f, indent=4)
        
        logger.info(f"User {from_username} sent private message to {to_username}")
        return message
    except Exception as e:
        logger.error(f"Error sending private message: {e}")
        return None

def mark_private_messages_read(username1: str, username2: str) -> bool:
    """
    Mark private messages as read
    
    Args:
        username1: First username
        username2: Second username
        
    Returns:
        True if successful, False otherwise
    """
    ensure_chat_dirs()
    
    try:
        # Sort usernames to ensure consistent file naming
        users = sorted([username1, username2])
        pm_file = os.path.join(PRIVATE_MESSAGES_DIR, f"{users[0]}_{users[1]}.json")
        
        if not os.path.exists(pm_file):
            return True  # No messages to mark
        
        with open(pm_file, 'r') as f:
            messages = json.load(f)
        
        # Mark messages as read where the recipient is username1
        updated = False
        for message in messages:
            if message.get("to_username") == username1 and not message.get("read", False):
                message["read"] = True
                updated = True
        
        # Save messages if updated
        if updated:
            with open(pm_file, 'w') as f:
                json.dump(messages, f, indent=4)
            
            logger.info(f"Marked private messages as read for {username1} from {username2}")
        
        return True
    except Exception as e:
        logger.error(f"Error marking private messages as read: {e}")
        return False

def get_unread_message_counts(username: str) -> Dict[str, int]:
    """
    Get counts of unread private messages
    
    Args:
        username: Username to get unread counts for
        
    Returns:
        Dictionary of sender_username -> unread_count
    """
    ensure_chat_dirs()
    
    try:
        unread_counts = {}
        
        # Scan private messages directory
        for filename in os.listdir(PRIVATE_MESSAGES_DIR):
            if not filename.endswith('.json'):
                continue
            
            # Extract usernames from filename
            users = filename[:-5].split('_')
            
            # Skip if user is not involved
            if username not in users:
                continue
            
            # Load messages
            with open(os.path.join(PRIVATE_MESSAGES_DIR, filename), 'r') as f:
                messages = json.load(f)
            
            # Count unread messages
            unread = 0
            other_user = None
            
            for message in messages:
                if message.get("to_username") == username and not message.get("read", False):
                    unread += 1
                    other_user = message.get("from_username")
            
            # Add to counts if there are unread messages
            if unread > 0 and other_user:
                unread_counts[other_user] = unread
        
        return unread_counts
    except Exception as e:
        logger.error(f"Error getting unread message counts: {e}")
        return {}

# Initialize
ensure_chat_dirs()