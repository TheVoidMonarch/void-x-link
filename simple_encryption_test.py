#!/usr/bin/env python3
"""
Simple test for the encryption module
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the encryption module
import encryption

def test_encrypt_decrypt_string():
    """Test encrypting and decrypting a string"""
    original = "Hello, World!"
    encrypted = encryption.encrypt_message(original)
    decrypted = encryption.decrypt_message(encrypted)
    
    # Verify the decrypted message matches the original
    assert decrypted == original
    
    print("Encrypt/decrypt string test passed!")
    return True

def test_encrypt_decrypt_dict():
    """Test encrypting and decrypting a dictionary"""
    original = {"key": "value", "number": 42}
    encrypted = encryption.encrypt_message(original)
    decrypted = encryption.decrypt_message(encrypted)
    
    # Verify the decrypted dictionary matches the original
    assert decrypted == original
    
    print("Encrypt/decrypt dictionary test passed!")
    return True

if __name__ == "__main__":
    print("Running simple encryption tests...")
    
    success = True
    
    try:
        success = test_encrypt_decrypt_string() and success
    except Exception as e:
        print(f"Encrypt/decrypt string test failed: {str(e)}")
        success = False
    
    try:
        success = test_encrypt_decrypt_dict() and success
    except Exception as e:
        print(f"Encrypt/decrypt dictionary test failed: {str(e)}")
        success = False
    
    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed.")
        sys.exit(1)