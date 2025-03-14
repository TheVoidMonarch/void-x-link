#!/usr/bin/env python3
"""
VoidLink Authentication Module - Handles user authentication and management
"""

import json
import os
import hashlib
import secrets
import time
from typing import Dict, Optional, Tuple, List

# Constants
USER_DB_FILE = "database/users.json"
SESSION_DB_FILE = "database/sessions.json"

def ensure_user_db():
    """Ensure the user database exists"""
    if not os.path.exists(os.path.dirname(USER_DB_FILE)):
        os.makedirs(os.path.dirname(USER_DB_FILE))
    
    if not os.path.exists(USER_DB_FILE):
        # Create default admin user
        default_users = {
            "admin": {
                "password": hash_password("admin123"),
                "role": "admin",
                "created_at": time.time()
            }
        }
        with open(USER_DB_FILE, "w") as user_db:
            json.dump(default_users, user_db, indent=4)

def hash_password(password: str) -> str:
    """Hash a password for storing"""
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                  salt.encode('utf-8'), 100000)
    return salt + ':' + pwdhash.hex()

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against a provided password"""
    salt, stored_hash = stored_password.split(':')
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), 
                                  salt.encode('utf-8'), 100000)
    return pwdhash.hex() == stored_hash

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user with username and password"""
    ensure_user_db()
    
    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)
        
        if username in users:
            # If password is already hashed
            if ':' in users[username]["password"]:
                return verify_password(users[username]["password"], password)
            else:
                # Legacy plain text password - update to hashed
                if users[username]["password"] == password:
                    # Update to hashed password
                    users[username]["password"] = hash_password(password)
                    with open(USER_DB_FILE, "w") as user_db:
                        json.dump(users, user_db, indent=4)
                    return True
                return False
        return False
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return False

def create_user(username: str, password: str, role: str = "user") -> bool:
    """Create a new user"""
    ensure_user_db()
    
    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)
        
        if username in users:
            return False  # User already exists
        
        # Create new user with hashed password
        users[username] = {
            "password": hash_password(password),
            "role": role,
            "created_at": time.time()
        }
        
        with open(USER_DB_FILE, "w") as user_db:
            json.dump(users, user_db, indent=4)
        
        return True
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return False

def delete_user(username: str) -> bool:
    """Delete a user"""
    ensure_user_db()
    
    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)
        
        if username not in users:
            return False  # User doesn't exist
        
        # Delete user
        del users[username]
        
        with open(USER_DB_FILE, "w") as user_db:
            json.dump(users, user_db, indent=4)
        
        return True
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return False

def get_user_role(username: str) -> Optional[str]:
    """Get a user's role"""
    ensure_user_db()
    
    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)
        
        if username in users:
            return users[username]["role"]
        return None
    except Exception as e:
        print(f"Error getting user role: {str(e)}")
        return None

def list_users() -> List[Dict]:
    """List all users (without passwords)"""
    ensure_user_db()
    
    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)
        
        # Return user info without passwords
        user_list = []
        for username, data in users.items():
            user_list.append({
                "username": username,
                "role": data["role"],
                "created_at": data.get("created_at", 0)
            })
        
        return user_list
    except Exception as e:
        print(f"Error listing users: {str(e)}")
        return []

def change_password(username: str, new_password: str) -> bool:
    """Change a user's password"""
    ensure_user_db()
    
    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)
        
        if username not in users:
            return False  # User doesn't exist
        
        # Update password
        users[username]["password"] = hash_password(new_password)
        
        with open(USER_DB_FILE, "w") as user_db:
            json.dump(users, user_db, indent=4)
        
        return True
    except Exception as e:
        print(f"Error changing password: {str(e)}")
        return False

def change_role(username: str, new_role: str) -> bool:
    """Change a user's role"""
    ensure_user_db()
    
    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)
        
        if username not in users:
            return False  # User doesn't exist
        
        # Update role
        users[username]["role"] = new_role
        
        with open(USER_DB_FILE, "w") as user_db:
            json.dump(users, user_db, indent=4)
        
        return True
    except Exception as e:
        print(f"Error changing role: {str(e)}")
        return False

# Initialize the user database
ensure_user_db()