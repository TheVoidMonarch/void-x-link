#!/usr/bin/env python3
"""
VoidLink Encryption Module - Handles encryption for secure communication
"""

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import base64
import os
import json

# Key management
KEY_FILE = "database/encryption_key.json"

def get_encryption_key():
    """Get or generate the encryption key"""
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r") as key_file:
                key_data = json.load(key_file)
                key = base64.b64decode(key_data["key"])
                salt = base64.b64decode(key_data["salt"])
                return key, salt
        except Exception as e:
            print(f"Error loading encryption key: {str(e)}")
    
    # Generate new key if not exists
    print("Generating new encryption key...")
    salt = get_random_bytes(16)
    password = os.environ.get("VOIDLINK_KEY_PASSWORD", "voidlink_default_password")
    key = PBKDF2(password, salt, dkLen=32)
    
    # Save the key
    if not os.path.exists(os.path.dirname(KEY_FILE)):
        os.makedirs(os.path.dirname(KEY_FILE))
        
    key_data = {
        "key": base64.b64encode(key).decode(),
        "salt": base64.b64encode(salt).decode()
    }
    
    with open(KEY_FILE, "w") as key_file:
        json.dump(key_data, key_file)
    
    return key, salt

# Get the encryption key
KEY, SALT = get_encryption_key()

def encrypt_message(message):
    """Encrypt a message using AES-256"""
    if isinstance(message, dict):
        message = json.dumps(message)
    
    # Convert to bytes if string
    if isinstance(message, str):
        message = message.encode('utf-8')
    
    # Create cipher
    cipher = AES.new(KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    
    # Combine nonce, tag, and ciphertext
    encrypted_data = cipher.nonce + tag + ciphertext
    
    # Return base64 encoded string
    return base64.b64encode(encrypted_data)

def decrypt_message(encrypted_message):
    """Decrypt an encrypted message"""
    try:
        # Decode base64
        data = base64.b64decode(encrypted_message)
        
        # Extract components
        nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
        
        # Create cipher
        cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)
        
        # Decrypt
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        
        # Try to decode as JSON
        try:
            return json.loads(decrypted_data.decode('utf-8'))
        except json.JSONDecodeError:
            # Return as string if not valid JSON
            return decrypted_data.decode('utf-8')
        
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        return None