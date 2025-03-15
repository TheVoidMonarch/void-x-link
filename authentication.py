#!/usr/bin/env python3
"""
VoidLink Authentication Module - Handles user authentication and management
"""

import json
import os
import hashlib
import secrets
import time
import bcrypt
from typing import Dict, Optional, Tuple, List
from error_handling import logger, log_info, log_warning, log_error, AuthenticationError

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
    """Hash a password for storing using bcrypt"""
    # Generate a salt and hash the password
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)  # Higher rounds = more secure but slower
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')  # Store as string


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a password against a stored bcrypt hash"""
    # Handle legacy format (PBKDF2)
    if ':' in stored_password:
        log_warning("Legacy password format detected, will upgrade on successful login")
        salt, stored_hash = stored_password.split(':')
        pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'),
                                      salt.encode('utf-8'), 100000)
        return pwdhash.hex() == stored_hash

    # Bcrypt verification
    try:
        return bcrypt.checkpw(
            provided_password.encode('utf-8'),
            stored_password.encode('utf-8')
        )
    except Exception as e:
        log_error(f"Password verification error: {str(e)}")
        return False


def authenticate_user(username: str, password: str, device_id: str = None) -> bool:
    """Authenticate a user with username and password"""
    ensure_user_db()

    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)

        # If user doesn't exist and auto-registration is enabled, create the user
        if username not in users:
            log_info(f"Creating new user: {username}")
            # Create new user with bcrypt hashed password
            users[username] = {
                "password": hash_password(password),
                "role": "user",
                "created_at": time.time(),
                "device_ids": [device_id] if device_id else [],
                "failed_attempts": 0,
                "last_login": time.time()
            }

            with open(USER_DB_FILE, "w") as user_db:
                json.dump(users, user_db, indent=4)

            log_info(f"New user created: {username}")
            return True

        # User exists, authenticate
        if username in users:
            # Check for account lockout
            if users[username].get("locked_until", 0) > time.time():
                log_warning(f"Account locked: {username}")
                raise AuthenticationError(
                    "Account is temporarily locked due to too many failed attempts", {
                        "locked_until": users[username]["locked_until"]})

            # Verify password
            authenticated = verify_password(users[username]["password"], password)

            if authenticated:
                # Reset failed attempts on successful login
                users[username]["failed_attempts"] = 0
                users[username]["last_login"] = time.time()

                # Upgrade legacy password format if needed
                if ':' in users[username]["password"]:
                    log_info(f"Upgrading password hash for user: {username}")
                    users[username]["password"] = hash_password(password)

                # If device_id is provided, add it to the user's device list
                if device_id:
                    if "device_ids" not in users[username]:
                        users[username]["device_ids"] = []

                    if device_id not in users[username]["device_ids"]:
                        users[username]["device_ids"].append(device_id)
                        log_info(f"New device registered for user {username}: {device_id}")

                # Save changes
                with open(USER_DB_FILE, "w") as user_db:
                    json.dump(users, user_db, indent=4)

                return True
            else:
                # Increment failed attempts
                users[username]["failed_attempts"] = users[username].get("failed_attempts", 0) + 1

                # Lock account after 5 failed attempts
                if users[username]["failed_attempts"] >= 5:
                    # Lock for 15 minutes
                    lock_duration = 15 * 60  # 15 minutes in seconds
                    users[username]["locked_until"] = time.time() + lock_duration
                    log_warning(f"Account locked for {username} due to too many failed attempts")

                # Save changes
                with open(USER_DB_FILE, "w") as user_db:
                    json.dump(users, user_db, indent=4)

                log_warning(
                    f"Failed login attempt for {username} (attempt {
                        users[username]['failed_attempts']})")
                return False

        return False
    except AuthenticationError:
        # Re-raise authentication errors to be handled by the caller
        raise
    except Exception as e:
        log_error(f"Authentication error: {str(e)}")
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
