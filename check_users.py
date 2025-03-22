#!/usr/bin/env python3
"""
Check Users Script

This script checks if the user database exists and creates it if it doesn't.
"""

import os
import json
import hashlib

# Constants
USER_DB_FILE = "database/users.json"

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    """Main function"""
    print("\nVoidLink User Database Check")
    print("==========================")
    
    # Check if database directory exists
    if not os.path.exists(os.path.dirname(USER_DB_FILE)):
        print(f"Creating database directory: {os.path.dirname(USER_DB_FILE)}")
        os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
    
    # Check if user database exists
    if os.path.exists(USER_DB_FILE):
        print(f"User database exists: {USER_DB_FILE}")
        
        # Read existing users
        try:
            with open(USER_DB_FILE, 'r') as f:
                users = json.load(f)
            
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - Username: {user.get('username')}, Role: {user.get('role')}")
        
        except Exception as e:
            print(f"Error reading user database: {e}")
            print("Creating new user database...")
            create_user_database()
    
    else:
        print(f"User database does not exist: {USER_DB_FILE}")
        print("Creating new user database...")
        create_user_database()
    
    return 0

def create_user_database():
    """Create a new user database with default users"""
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

if __name__ == "__main__":
    main()#!/usr/bin/env python3
"""
Check Users Script

This script checks if the user database exists and creates it if it doesn't.
"""

import os
import json
import hashlib

# Constants
USER_DB_FILE = "database/users.json"

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    """Main function"""
    print("\nVoidLink User Database Check")
    print("==========================")
    
    # Check if database directory exists
    if not os.path.exists(os.path.dirname(USER_DB_FILE)):
        print(f"Creating database directory: {os.path.dirname(USER_DB_FILE)}")
        os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
    
    # Check if user database exists
    if os.path.exists(USER_DB_FILE):
        print(f"User database exists: {USER_DB_FILE}")
        
        # Read existing users
        try:
            with open(USER_DB_FILE, 'r') as f:
                users = json.load(f)
            
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - Username: {user.get('username')}, Role: {user.get('role')}")
        
        except Exception as e:
            print(f"Error reading user database: {e}")
            print("Creating new user database...")
            create_user_database()
    
    else:
        print(f"User database does not exist: {USER_DB_FILE}")
        print("Creating new user database...")
        create_user_database()
    
    return 0

def create_user_database():
    """Create a new user database with default users"""
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

if __name__ == "__main__":
    main()#!/usr/bin/env python3
"""
Check Users Script

This script checks if the user database exists and creates it if it doesn't.
"""

import os
import json
import hashlib

# Constants
USER_DB_FILE = "database/users.json"

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    """Main function"""
    print("\nVoidLink User Database Check")
    print("==========================")
    
    # Check if database directory exists
    if not os.path.exists(os.path.dirname(USER_DB_FILE)):
        print(f"Creating database directory: {os.path.dirname(USER_DB_FILE)}")
        os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
    
    # Check if user database exists
    if os.path.exists(USER_DB_FILE):
        print(f"User database exists: {USER_DB_FILE}")
        
        # Read existing users
        try:
            with open(USER_DB_FILE, 'r') as f:
                users = json.load(f)
            
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - Username: {user.get('username')}, Role: {user.get('role')}")
        
        except Exception as e:
            print(f"Error reading user database: {e}")
            print("Creating new user database...")
            create_user_database()
    
    else:
        print(f"User database does not exist: {USER_DB_FILE}")
        print("Creating new user database...")
        create_user_database()
    
    return 0

def create_user_database():
    """Create a new user database with default users"""
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

if __name__ == "__main__":
    main()