#!/usr/bin/env python3
"""
Test script for device-bound registration system
"""

import os
import sys
import json
import time
import argparse

# Add current directory to path to ensure modules can be found
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import required modules
try:
    from core.authentication import authenticate_user, change_password, user_exists
    from core.device_id import get_device_id
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def test_new_user_registration():
    """Test registering a new user with device binding"""
    print("\n=== Testing New User Registration ===")
    
    # Generate a unique username
    timestamp = int(time.time())
    username = f"test_user_{timestamp}"
    password = "test_password"
    
    # Get device ID
    device_id = get_device_id()
    print(f"Device ID: {device_id}")
    
    # Register new user
    print(f"Registering new user: {username}")
    result = authenticate_user(username, password, device_id)
    
    if result:
        print("✅ User registration successful")
    else:
        print("❌ User registration failed")
        return False
    
    # Try to authenticate with wrong password
    print("Testing authentication with wrong password...")
    result = authenticate_user(username, "wrong_password", device_id)
    
    if not result:
        print("✅ Authentication with wrong password correctly failed")
    else:
        print("❌ Authentication with wrong password incorrectly succeeded")
        return False
    
    # Try to authenticate with correct password
    print("Testing authentication with correct password...")
    result = authenticate_user(username, password, device_id)
    
    if result:
        print("✅ Authentication with correct password successful")
    else:
        print("❌ Authentication with correct password failed")
        return False
    
    # Try to authenticate with different device ID (should succeed with multi-device support)
    print("Testing authentication with different device ID...")
    fake_device_id = "fake_device_id_" + device_id[5:]

    try:
        result = authenticate_user(username, password, fake_device_id)
        if result:
            print("✅ Authentication with different device ID succeeded (multi-device support)")

            # Check if the new device was added to the user's device list
            from core.authentication import get_user_info
            user_info = get_user_info(username)
            if user_info and "device_ids" in user_info and fake_device_id in user_info["device_ids"]:
                print("✅ New device was correctly added to user's device list")
            else:
                print("❌ New device was not added to user's device list")
                return False
        else:
            print("❌ Authentication with different device ID failed")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Try to change password
    print("Testing password change (should fail for permanent accounts)...")
    
    try:
        result = change_password(username, "new_password")
        print("❌ Password change incorrectly succeeded")
        return False
    except Exception as e:
        if "permanent" in str(e).lower():
            print("✅ Password change correctly failed for permanent account")
        else:
            print(f"❌ Unexpected error: {e}")
            return False
    
    print("\n✅ All device binding tests passed!")
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test device-bound registration")
    args = parser.parse_args()
    
    # Run tests
    test_new_user_registration()

if __name__ == "__main__":
    main()