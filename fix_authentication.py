#!/usr/bin/env python3
"""
Fix Authentication Script

This script creates a default user database file with known credentials.
"""

import os
import json
import hashlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('fix_authentication')

# Constants
USER_DB_FILE = "database/users.json"

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    """Main function"""
    print("VoidLink Authentication Fix")
    print("==========================")
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
    
    # Create default users
    default_users = [
        {
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "role": "admin",
            "created_at": 0,
            "last_login": None,
            "devices": []
        },
        {
            "username": "user",
            "password_hash": hash_password("user123"),
            "role": "user",
            "created_at": 0,
            "last_login": None,
            "devices": []
        },
        {
            "username": "demo",
            "password_hash": hash_password("password"),
            "role": "user",
            "created_at": 0,
            "last_login": None,
            "devices": []
        }
    ]
    
    # Write to file
    with open(USER_DB_FILE, 'w') as f:
        json.dump(default_users, f, indent=2)
    
    print(f"Created user database file: {USER_DB_FILE}")
    print("Default users:")
    print("  - Username: admin, Password: admin123")
    print("  - Username: user, Password: user123")
    print("  - Username: demo, Password: password")
    
    return 0

if __name__ == "__main__":
    main()