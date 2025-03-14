#!/usr/bin/env python3
"""
VoidLink Storage Module - Handles message persistence and chat history
"""

import json
import os
import time
from typing import Dict, List, Optional, Any
from encryption import encrypt_message, decrypt_message

# Constants
CHAT_LOG_FILE = "database/chat_log.json"
CHAT_HISTORY_DIR = "database/chat_history"

def ensure_storage_dirs():
    """Ensure all storage directories exist"""
    if not os.path.exists(os.path.dirname(CHAT_LOG_FILE)):
        os.makedirs(os.path.dirname(CHAT_LOG_FILE))
    
    if not os.path.exists(CHAT_HISTORY_DIR):
        os.makedirs(CHAT_HISTORY_DIR)

def save_message(username: str, message: str, recipient: str = "all", timestamp: float = None) -> bool:
    """Save a message to the chat log"""
    ensure_storage_dirs()
    
    try:
        # Create message object
        message_obj = {
            "sender": username,
            "content": message,
            "recipient": recipient,
            "timestamp": timestamp or time.time()
        }
        
        # Save to main chat log
        with open(CHAT_LOG_FILE, "a") as file:
            json.dump(message_obj, file)
            file.write("\n")
        
        # Save to user-specific chat history
        save_to_user_history(username, message_obj)
        
        if recipient != "all" and recipient != username:
            # Save to recipient's chat history for direct messages
            save_to_user_history(recipient, message_obj)
        
        return True
    except Exception as e:
        print(f"Error saving message: {str(e)}")
        return False

def save_to_user_history(username: str, message_obj: Dict) -> None:
    """Save a message to a user's chat history"""
    user_history_file = os.path.join(CHAT_HISTORY_DIR, f"{username}_history.json")
    
    try:
        # Load existing history
        history = []
        if os.path.exists(user_history_file):
            with open(user_history_file, "r") as file:
                try:
                    history = json.load(file)
                except json.JSONDecodeError:
                    history = []
        
        # Append new message
        history.append(message_obj)
        
        # Save updated history
        with open(user_history_file, "w") as file:
            json.dump(history, file, indent=2)
    except Exception as e:
        print(f"Error saving to user history for {username}: {str(e)}")

def get_chat_history(username: str = None, limit: int = 100) -> List[Dict]:
    """Get chat history, optionally filtered by username"""
    ensure_storage_dirs()
    
    try:
        if username:
            # Get user-specific history
            user_history_file = os.path.join(CHAT_HISTORY_DIR, f"{username}_history.json")
            if os.path.exists(user_history_file):
                with open(user_history_file, "r") as file:
                    try:
                        history = json.load(file)
                        return history[-limit:] if limit else history
                    except json.JSONDecodeError:
                        return []
            return []
        else:
            # Get global chat history
            history = []
            if os.path.exists(CHAT_LOG_FILE):
                with open(CHAT_LOG_FILE, "r") as file:
                    for line in file:
                        try:
                            message = json.loads(line.strip())
                            history.append(message)
                        except json.JSONDecodeError:
                            continue
            
            return history[-limit:] if limit else history
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return []

def get_direct_messages(username1: str, username2: str, limit: int = 100) -> List[Dict]:
    """Get direct messages between two users"""
    ensure_storage_dirs()
    
    try:
        # Get user1's history
        user1_history = get_chat_history(username1)
        
        # Filter for direct messages between the two users
        direct_messages = []
        for message in user1_history:
            sender = message.get("sender")
            recipient = message.get("recipient")
            
            if (sender == username1 and recipient == username2) or \
               (sender == username2 and recipient == username1):
                direct_messages.append(message)
        
        # Sort by timestamp
        direct_messages.sort(key=lambda x: x.get("timestamp", 0))
        
        return direct_messages[-limit:] if limit else direct_messages
    except Exception as e:
        print(f"Error getting direct messages: {str(e)}")
        return []

def clear_chat_history(username: str = None) -> bool:
    """Clear chat history, optionally for a specific user"""
    ensure_storage_dirs()
    
    try:
        if username:
            # Clear user-specific history
            user_history_file = os.path.join(CHAT_HISTORY_DIR, f"{username}_history.json")
            if os.path.exists(user_history_file):
                with open(user_history_file, "w") as file:
                    json.dump([], file)
        else:
            # Clear global chat history
            with open(CHAT_LOG_FILE, "w") as file:
                file.write("")
        
        return True
    except Exception as e:
        print(f"Error clearing chat history: {str(e)}")
        return False

def backup_chat_history(backup_file: str = None) -> bool:
    """Backup chat history to a file"""
    ensure_storage_dirs()
    
    if not backup_file:
        backup_file = f"database/backups/chat_backup_{int(time.time())}.json"
    
    try:
        # Create backup directory if it doesn't exist
        backup_dir = os.path.dirname(backup_file)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Get all chat history
        history = get_chat_history(limit=None)
        
        # Save to backup file
        with open(backup_file, "w") as file:
            json.dump(history, file, indent=2)
        
        return True
    except Exception as e:
        print(f"Error backing up chat history: {str(e)}")
        return False

# Initialize storage
ensure_storage_dirs()