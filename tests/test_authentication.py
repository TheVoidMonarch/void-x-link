#!/usr/bin/env python3
"""
Tests for the authentication module
"""

import os
import sys
import unittest
import tempfile
import json
import time
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import after adding parent directory to path
import authentication
from authentication import (
    ensure_user_db, hash_password, verify_password, authenticate_user,
    create_user, delete_user, get_user_role, list_users
)


class TestAuthentication(unittest.TestCase):
    """Test cases for authentication module"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.original_user_db_file = authentication.USER_DB_FILE

        # Set the user database file to a temporary file
        authentication.USER_DB_FILE = os.path.join(self.test_dir, "users.json")

        # Create a test user
        create_user("testuser", "testpass", "user")
        create_user("admin", "adminpass", "admin")

    def tearDown(self):
        """Clean up after tests"""
        # Restore original database file path
        authentication.USER_DB_FILE = self.original_user_db_file

        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword"
        hashed = hash_password(password)

        # Verify the hash is not the same as the password
        self.assertNotEqual(password, hashed)

        # Verify the hash is a string
        self.assertIsInstance(hashed, str)

        # Verify the hash is not empty
        self.assertTrue(hashed)

    def test_verify_password(self):
        """Test password verification"""
        password = "testpassword"
        hashed = hash_password(password)

        # Verify correct password
        self.assertTrue(verify_password(hashed, password))

        # Verify incorrect password
        self.assertFalse(verify_password(hashed, "wrongpassword"))

    def test_authenticate_user(self):
        """Test user authentication"""
        # Test valid credentials
        self.assertTrue(authenticate_user("testuser", "testpass"))

        # Test invalid password
        self.assertFalse(authenticate_user("testuser", "wrongpass"))

        # Test non-existent user
        self.assertFalse(authenticate_user("nonexistent", "anypass"))

    def test_create_user(self):
        """Test user creation"""
        # Create a new user
        result = create_user("newuser", "newpass", "user")
        self.assertTrue(result)

        # Verify user was created
        self.assertTrue(authenticate_user("newuser", "newpass"))

        # Test creating a user that already exists
        result = create_user("newuser", "anotherpass", "user")
        self.assertFalse(result)

    def test_delete_user(self):
        """Test user deletion"""
        # Create a user to delete
        create_user("deleteuser", "deletepass", "user")

        # Delete the user
        result = delete_user("deleteuser")
        self.assertTrue(result)

        # Verify user was deleted
        self.assertFalse(authenticate_user("deleteuser", "deletepass"))

        # Test deleting a non-existent user
        result = delete_user("nonexistent")
        self.assertFalse(result)

    def test_get_user_role(self):
        """Test getting user role"""
        # Test existing users
        self.assertEqual(get_user_role("testuser"), "user")
        self.assertEqual(get_user_role("admin"), "admin")

        # Test non-existent user
        self.assertIsNone(get_user_role("nonexistent"))

    def test_list_users(self):
        """Test listing users"""
        users = list_users()

        # Verify the list is not empty
        self.assertTrue(users)

        # Verify the test users are in the list
        usernames = [user["username"] for user in users]
        self.assertIn("testuser", usernames)
        self.assertIn("admin", usernames)

    def test_account_lockout(self):
        """Test account lockout after failed attempts"""
        # Create a user for lockout testing
        create_user("lockoutuser", "lockoutpass", "user")

        # Authenticate with correct password
        self.assertTrue(authenticate_user("lockoutuser", "lockoutpass"))

        # Attempt authentication with wrong password multiple times
        for _ in range(5):
            self.assertFalse(authenticate_user("lockoutuser", "wrongpass"))

        # Verify account is locked (should raise AuthenticationError)
        with self.assertRaises(Exception):
            authenticate_user("lockoutuser", "lockoutpass")

    def test_device_id_tracking(self):
        """Test device ID tracking"""
        # Create a user for device tracking
        create_user("deviceuser", "devicepass", "user")

        # Authenticate with a device ID
        device_id = "test-device-1"
        self.assertTrue(authenticate_user("deviceuser", "devicepass", device_id))

        # Load user data and verify device ID was added
        with open(authentication.USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)

        self.assertIn("deviceuser", users)
        self.assertIn("device_ids", users["deviceuser"])
        self.assertIn(device_id, users["deviceuser"]["device_ids"])

        # Authenticate with a different device ID
        device_id2 = "test-device-2"
        self.assertTrue(authenticate_user("deviceuser", "devicepass", device_id2))

        # Load user data and verify both device IDs are present
        with open(authentication.USER_DB_FILE, "r") as user_db:
            users = json.load(user_db)

        self.assertIn(device_id, users["deviceuser"]["device_ids"])
        self.assertIn(device_id2, users["deviceuser"]["device_ids"])


if __name__ == "__main__":
    unittest.main()
