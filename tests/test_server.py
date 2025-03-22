#!/usr/bin/env python3
"""
VoidLink Server Test Script - Tests basic server functionality
"""

import unittest
import os
import json
import time
from authentication import authenticate_user, create_user, delete_user, get_user_role, list_users
from encryption import encrypt_message, decrypt_message
from storage import save_message, get_chat_history
from file_transfer import ensure_file_dirs


class TestVoidLinkServer(unittest.TestCase):
    """Test cases for VoidLink server components"""

    def setUp(self):
        """Set up test environment"""
        # Ensure database directories exist
        if not os.path.exists("database"):
            os.makedirs("database")

        # Create test user
        create_user("testuser", "testpass", "user")

    def tearDown(self):
        """Clean up after tests"""
        # Delete test user
        delete_user("testuser")

    def test_authentication(self):
        """Test user authentication"""
        # Test valid credentials
        self.assertTrue(authenticate_user("testuser", "testpass"))

        # Test invalid credentials
        self.assertFalse(authenticate_user("testuser", "wrongpass"))
        self.assertFalse(authenticate_user("nonexistent", "anypass"))

    def test_user_management(self):
        """Test user management functions"""
        # Test user role
        self.assertEqual(get_user_role("testuser"), "user")

        # Test user listing
        users = list_users()
        self.assertTrue(any(user["username"] == "testuser" for user in users))

        # Test user creation and deletion
        self.assertTrue(create_user("tempuser", "temppass"))
        self.assertTrue(authenticate_user("tempuser", "temppass"))
        self.assertTrue(delete_user("tempuser"))
        self.assertFalse(authenticate_user("tempuser", "temppass"))

    def test_encryption(self):
        """Test encryption and decryption"""
        # Test string encryption/decryption
        message = "Hello, VoidLink!"
        encrypted = encrypt_message(message)
        decrypted = decrypt_message(encrypted)
        self.assertEqual(decrypted, message)

        # Test dict encryption/decryption
        message_dict = {"type": "message", "content": "Hello, VoidLink!", "timestamp": time.time()}
        encrypted = encrypt_message(json.dumps(message_dict))
        decrypted = decrypt_message(encrypted)
        self.assertEqual(decrypted["content"], message_dict["content"])

    def test_storage(self):
        """Test message storage"""
        # Save a test message
        save_message("testuser", "Test message")

        # Get chat history
        history = get_chat_history()
        self.assertTrue(any(msg["sender"] == "testuser" and msg["content"]
                        == "Test message" for msg in history))

    def test_file_storage(self):
        """Test file storage directories"""
        ensure_file_dirs()
        self.assertTrue(os.path.exists("database/files"))


if __name__ == "__main__":
    unittest.main()
