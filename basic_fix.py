#!/usr/bin/env python3
"""
Basic Authentication Fix

A very basic script to create a user database file with default credentials.
"""

import os
import json
import hashlib

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    """Main function"""
    print("\nBasic Authentication Fix")
    print("=======================")
    
    # Create database directory
    os.makedirs("database", exist_ok=True)
    
    # Create default users
    users = [
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
    with open("database/users.json", 'w') as f:
        json.dump(users, f, indent=2)
    
    print("Created user database file: database/users.json")
    print("Default users:")
    print("  - Username: admin, Password: admin123")
    print("  - Username: user, Password: user123")
    print("  - Username: demo, Password: password")
    
    return 0

if __name__ == "__main__":
    main()