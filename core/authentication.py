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
    """
    Authenticate a user with username and password

    Implements permanent credentials with multi-device support:
    - Username and password set on first login—no changes allowed
    - Account can be used on multiple devices
    - Each user can only have one account
    """
    ensure_user_db()

    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)

        # If user doesn't exist, create the user (first-time registration)
        if username not in users:
            # Device ID is required for new account creation
            if not device_id:
                log_warning(f"Device ID required for new account creation: {username}")
                raise AuthenticationError(
                    "Device ID is required for new account creation", {
                        "reason": "device_id_required"})

            log_info(f"Creating new user with permanent credentials: {username}")
            # Create new user with bcrypt hashed password
            users[username] = {
                "password": hash_password(password),
                "role": "user",
                "created_at": time.time(),
                "device_ids": [device_id],  # Store as a list to support multiple devices
                "failed_attempts": 0,
                "last_login": time.time(),
                "permanent": True  # Flag indicating credentials cannot be changed
            }

            with open(USER_DB_FILE, "w") as user_db:
                json.dump(users, user_db, indent=4)

            log_info(f"New user created with permanent credentials: {username}")
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

                # If this is a legacy account without the permanent flag, add it
                if "permanent" not in users[username]:
                    users[username]["permanent"] = True
                    log_info(f"Upgraded account to permanent credentials: {username}")

                # Handle device registration
                if device_id:
                    # Ensure device_ids exists
                    if "device_ids" not in users[username]:
                        users[username]["device_ids"] = []

                    # Handle legacy accounts that might have device_id instead of device_ids
                    if "device_id" in users[username] and users[username]["device_id"]:
                        # Migrate to new format if not already in the list
                        legacy_device = users[username]["device_id"]
                        if legacy_device not in users[username]["device_ids"]:
                            users[username]["device_ids"].append(legacy_device)

                    # Register new device if not already registered
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
    """
    Change a user's password

    Note: For permanent accounts (created with the new registration system),
    password changes are not allowed.
    """
    ensure_user_db()

    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)

        if username not in users:
            log_warning(f"Attempted to change password for non-existent user: {username}")
            return False  # User doesn't exist

        # Check if this is a permanent account
        if users[username].get("permanent", False):
            log_warning(f"Attempted to change password for permanent account: {username}")
            raise AuthenticationError(
                "Password changes are not allowed for this account", {
                    "reason": "permanent_credentials"})

        # Update password for non-permanent accounts
        users[username]["password"] = hash_password(new_password)

        with open(USER_DB_FILE, "w") as user_db:
            json.dump(users, user_db, indent=4)

        log_info(f"Password changed for user: {username}")
        return True
    except AuthenticationError:
        # Re-raise authentication errors to be handled by the caller
        raise
    except Exception as e:
        log_error(f"Error changing password: {str(e)}")
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


def user_exists(username: str) -> bool:
    """Check if a user exists"""
    ensure_user_db()

    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)

        return username in users
    except Exception as e:
        log_error(f"Error checking if user exists: {str(e)}")
        return False


def get_user_info(username: str) -> Optional[Dict[str, Any]]:
    """Get user information"""
    ensure_user_db()

    try:
        with open(USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)

        if username in users:
            # Return a copy of the user info to prevent accidental modification
            return dict(users[username])

        return None
    except Exception as e:
        log_error(f"Error getting user info: {str(e)}")
        return None


# Initialize the user database
ensure_user_db()
