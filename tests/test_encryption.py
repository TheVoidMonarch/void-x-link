#!/usr/bin/env python3
"""
Tests for the encryption module
"""

import os
import sys
import unittest
import tempfile
import json
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import after adding parent directory to path
import encryption
from encryption import (
    get_encryption_key, encrypt_message, decrypt_message
)


class TestEncryption(unittest.TestCase):
    """Test cases for encryption module"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.original_key_file = encryption.KEY_FILE

        # Set the key file to a temporary file
        encryption.KEY_FILE = os.path.join(self.test_dir, "encryption_key.json")

    def tearDown(self):
        """Clean up after tests"""
        # Restore original key file
        encryption.KEY_FILE = self.original_key_file

        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_get_encryption_key(self):
        """Test getting encryption key"""
        # Get key (should generate a new one)
        key, salt = get_encryption_key()

        # Verify key and salt are bytes
        self.assertIsInstance(key, bytes)
        self.assertIsInstance(salt, bytes)

        # Verify key file was created
        self.assertTrue(os.path.exists(encryption.KEY_FILE))

        # Get key again (should load the existing one)
        key2, salt2 = get_encryption_key()

        # Verify keys are the same
        self.assertEqual(key, key2)
        self.assertEqual(salt, salt2)

    def test_encrypt_decrypt_string(self):
        """Test encrypting and decrypting a string"""
        # Test message
        message = "This is a test message"

        # Encrypt message
        encrypted = encrypt_message(message)

        # Verify encrypted message is bytes
        self.assertIsInstance(encrypted, bytes)

        # Decrypt message
        decrypted = decrypt_message(encrypted)

        # Verify decrypted message matches original
        self.assertEqual(decrypted, message)

    def test_encrypt_decrypt_bytes(self):
        """Test encrypting and decrypting bytes"""
        # Test message
        message = b"This is a test message in bytes"

        # Encrypt message
        encrypted = encrypt_message(message)

        # Verify encrypted message is bytes
        self.assertIsInstance(encrypted, bytes)

        # Decrypt message
        decrypted = decrypt_message(encrypted)

        # Verify decrypted message matches original
        self.assertEqual(decrypted, message)

    def test_encrypt_decrypt_dict(self):
        """Test encrypting and decrypting a dictionary"""
        # Test message
        message = {
            "key1": "value1",
            "key2": 123,
            "key3": [1, 2, 3],
            "key4": {"nested": "value"}
        }

        # Encrypt message
        encrypted = encrypt_message(message)

        # Verify encrypted message is bytes
        self.assertIsInstance(encrypted, bytes)

        # Decrypt message
        decrypted = decrypt_message(encrypted)

        # Verify decrypted message matches original
        self.assertEqual(decrypted, message)

    def test_decrypt_invalid_data(self):
        """Test decrypting invalid data"""
        # Test with invalid data
        with self.assertRaises(Exception):
            decrypt_message(b"invalid data")


if __name__ == "__main__":
    unittest.main()
