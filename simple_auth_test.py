#!/usr/bin/env python3
"""
Simple test for the authentication module
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the authentication module
import authentication

def test_hash_password():
    """Test the hash_password function"""
    password = "testpassword"
    hashed = authentication.hash_password(password)
    
    # Verify the hash is not the same as the password
    assert password != hashed
    
    # Verify the hash is a string
    assert isinstance(hashed, str)
    
    # Verify the hash is not empty
    assert hashed
    
    print("Hash password test passed!")
    return True

def test_verify_password():
    """Test the verify_password function"""
    password = "testpassword"
    hashed = authentication.hash_password(password)
    
    # Verify correct password
    assert authentication.verify_password(hashed, password)
    
    # Verify incorrect password
    assert not authentication.verify_password(hashed, "wrongpassword")
    
    print("Verify password test passed!")
    return True

if __name__ == "__main__":
    print("Running simple authentication tests...")
    
    success = True
    
    try:
        success = test_hash_password() and success
    except Exception as e:
        print(f"Hash password test failed: {str(e)}")
        success = False
    
    try:
        success = test_verify_password() and success
    except Exception as e:
        print(f"Verify password test failed: {str(e)}")
        success = False
    
    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed.")
        sys.exit(1)