#!/usr/bin/env python3
"""
VoidLink Simple Encryption Module

A simplified encryption module that doesn't rely on external dependencies.
"""

import os
import base64
import hashlib
import json
import logging
from typing import Any, Dict, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voidlink_encryption')

# Constants
KEY_FILE = "database/encryption_key.txt"
DEFAULT_KEY = "voidlink_default_encryption_key"

def ensure_key_file():
    """Ensure the encryption key file exists"""
    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
    if not os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'w') as f:
            f.write(DEFAULT_KEY)
        logger.info(f"Created default encryption key file: {KEY_FILE}")

def get_encryption_key() -> bytes:
    """Get the encryption key"""
    ensure_key_file()
    with open(KEY_FILE, 'r') as f:
        key = f.read().strip()
    
    # Convert key to bytes and ensure it's 32 bytes long (for AES-256)
    key_bytes = hashlib.sha256(key.encode()).digest()
    return key_bytes

def simple_encrypt(data: bytes, key: bytes = None) -> bytes:
    """
    Simple XOR encryption
    
    This is NOT secure for production use, but works for demonstration purposes
    """
    if key is None:
        key = get_encryption_key()
    
    # Use key as a repeating XOR pad
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = data[i] ^ key[i % len(key)]
    
    return bytes(result)

def simple_decrypt(data: bytes, key: bytes = None) -> bytes:
    """
    Simple XOR decryption
    
    XOR is symmetric, so encryption and decryption are the same operation
    """
    return simple_encrypt(data, key)  # XOR is its own inverse

def encrypt_message(message: Union[str, dict, bytes]) -> str:
    """Encrypt a message (string, dictionary, or bytes)"""
    try:
        # Convert message to bytes
        if isinstance(message, str):
            data = message.encode('utf-8')
        elif isinstance(message, dict):
            data = json.dumps(message).encode('utf-8')
        elif isinstance(message, bytes):
            data = message
        else:
            raise TypeError(f"Unsupported message type: {type(message)}")
        
        # Encrypt data
        encrypted = simple_encrypt(data)
        
        # Encode as base64 for easy transmission
        encoded = base64.b64encode(encrypted).decode('utf-8')
        
        return encoded
    
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise

def decrypt_message(encrypted_message: str) -> Any:
    """Decrypt a message"""
    try:
        # Decode from base64
        encrypted = base64.b64decode(encrypted_message)
        
        # Decrypt data
        decrypted = simple_decrypt(encrypted)
        
        # Try to parse as JSON
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            # Not JSON, return as string
            return decrypted.decode('utf-8')
    
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise

# Initialize
ensure_key_file()

# Test the encryption
if __name__ == "__main__":
    test_message = "Hello, VoidLink!"
    encrypted = encrypt_message(test_message)
    decrypted = decrypt_message(encrypted)
    
    print(f"Original: {test_message}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    
    test_dict = {"name": "VoidLink", "version": "1.0.0"}
    encrypted = encrypt_message(test_dict)
    decrypted = decrypt_message(encrypted)
    
    print(f"\nOriginal: {test_dict}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")