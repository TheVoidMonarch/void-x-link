#!/usr/bin/env python3
"""
VoidLink Simple Authentication Module

A simplified authentication module for demo purposes.
"""

import os
import json
import hashlib
import logging
import time
from typing import List, Dict, Optional, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voidlink_authentication')

# Constants
USER_DB_FILE = "database/users.json"
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 15 * 60  # 15 minutes in seconds

# In-memory storage for failed login attempts
failed_attempts = {}  # username -> [(timestamp, ip_address), ...]

def ensure_user_db():
    """Ensure the user database file exists"""
    os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
    if not os.path.exists(USER_DB_FILE):
        # Create default users
        default_users = [
            {
                "username": "admin",
                "password_hash": hash_password("admin123"),
                "role": "admin",
                "created_at": time.time(),
                "last_login": None,
                "devices": []
            },
            {
                "username": "user",
                "password_hash": hash_password("user123"),
                "role": "user",
                "created_at": time.time(),
                "last_login": None,
                "devices": []
            },
            {
                "username": "demo",
                "password_hash": hash_password("password"),
                "role": "user",
                "created_at": time.time(),
                "last_login": None,
                "devices": []
            }
        ]
        
        with open(USER_DB_FILE, 'w') as f:
            json.dump(default_users, f, indent=2)
        
        logger.info(f"Created default user database: {USER_DB_FILE}")

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password against its hash"""
    return password_hash == hash_password(password)

def user_exists(username: str) -> bool:
    """Check if a user exists"""
    ensure_user_db()
    
    with open(USER_DB_FILE, 'r') as f:
        users = json.load(f)
    
    return any(user["username"] == username for user in users)

def is_account_locked(username: str) -> Tuple[bool, Optional[float]]:
    """Check if an account is locked due to too many failed login attempts"""
    if username not in failed_attempts:
        return False, None
    
    # Get recent failed attempts (within lockout duration)
    recent_attempts = [
        attempt for attempt in failed_attempts[username]
        if time.time() - attempt[0] < LOCKOUT_DURATION
    ]
    
    # Update failed attempts
    failed_attempts[username] = recent_attempts
    
    # Check if there are too many recent attempts
    if len(recent_attempts) >= MAX_FAILED_ATTEMPTS:
        # Calculate time remaining in lockout
        oldest_recent_attempt = min(recent_attempts, key=lambda x: x[0])
        time_remaining = LOCKOUT_DURATION - (time.time() - oldest_recent_attempt[0])
        return True, max(0, time_remaining)
    
    return False, None

def record_failed_attempt(username: str, ip_address: str = "unknown"):
    """Record a failed login attempt"""
    if username not in failed_attempts:
        failed_attempts[username] = []
    
    failed_attempts[username].append((time.time(), ip_address))

def clear_failed_attempts(username: str):
    """Clear failed login attempts for a user"""
    if username in failed_attempts:
        del failed_attempts[username]

def authenticate_user(username: str, password: str, ip_address: str = "unknown") -> bool:
    """Authenticate a user"""
    # Check if account is locked
    locked, time_remaining = is_account_locked(username)
    if locked:
        logger.warning(f"Account locked for {username} from {ip_address}. "
                      f"Time remaining: {time_remaining:.1f} seconds")
        return False
    
    # Check if user exists
    if not user_exists(username):
        logger.warning(f"Authentication failed for non-existent user: {username} from {ip_address}")
        record_failed_attempt(username, ip_address)
        return False
    
    # Get user data
    with open(USER_DB_FILE, 'r') as f:
        users = json.load(f)
    
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        logger.warning(f"Authentication failed for non-existent user: {username} from {ip_address}")
        record_failed_attempt(username, ip_address)
        return False
    
    # Verify password
    if not verify_password(user["password_hash"], password):
        logger.warning(f"Authentication failed for user: {username} from {ip_address} (invalid password)")
        record_failed_attempt(username, ip_address)
        return False
    
    # Authentication successful
    clear_failed_attempts(username)
    
    # Update last login time
    user["last_login"] = time.time()
    
    # Add device if not already present
    if ip_address not in user["devices"]:
        user["devices"].append(ip_address)
    
    # Save changes
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    
    logger.info(f"Authentication successful for user: {username} from {ip_address}")
    return True

def create_user(username: str, password: str, role: str = "user") -> bool:
    """Create a new user"""
    ensure_user_db()
    
    # Check if user already exists
    if user_exists(username):
        logger.warning(f"User already exists: {username}")
        return False
    
    # Create user
    new_user = {
        "username": username,
        "password_hash": hash_password(password),
        "role": role,
        "created_at": time.time(),
        "last_login": None,
        "devices": []
    }
    
    # Add to database
    with open(USER_DB_FILE, 'r') as f:
        users = json.load(f)
    
    users.append(new_user)
    
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    
    logger.info(f"User created: {username} with role {role}")
    return True

def delete_user(username: str) -> bool:
    """Delete a user"""
    ensure_user_db()
    
    # Check if user exists
    if not user_exists(username):
        logger.warning(f"User does not exist: {username}")
        return False
    
    # Remove from database
    with open(USER_DB_FILE, 'r') as f:
        users = json.load(f)
    
    users = [u for u in users if u["username"] != username]
    
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    
    logger.info(f"User deleted: {username}")
    return True

def get_user_role(username: str) -> Optional[str]:
    """Get a user's role"""
    ensure_user_db()
    
    # Check if user exists
    if not user_exists(username):
        logger.warning(f"User does not exist: {username}")
        return None
    
    # Get user data
    with open(USER_DB_FILE, 'r') as f:
        users = json.load(f)
    
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        return None
    
    return user["role"]

def list_users() -> List[Dict[str, Any]]:
    """List all users"""
    ensure_user_db()
    
    with open(USER_DB_FILE, 'r') as f:
        users = json.load(f)
    
    # Remove sensitive information
    return [
        {
            "username": user["username"],
            "role": user["role"],
            "created_at": user["created_at"],
            "last_login": user["last_login"]
        }
        for user in users
    ]

# Initialize
ensure_user_db()

# Test the authentication
if __name__ == "__main__":
    # Test user creation
    create_user("testuser", "testpass")
    
    # Test authentication
    print(f"Authentication result: {authenticate_user('testuser', 'testpass')}")
    print(f"Authentication with wrong password: {authenticate_user('testuser', 'wrongpass')}")
    
    # Test user listing
    print(f"Users: {list_users()}")
    
    # Test user deletion
    delete_user("testuser")