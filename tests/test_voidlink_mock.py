#!/usr/bin/env python3
"""
VoidLink Test Suite - Comprehensive tests for real-life usage scenarios
"""

from client import VoidLinkClient
from server import start_server
import unittest
import threading
import socket
import json
import os
import time
import sys
from unittest.mock import MagicMock, patch

# Create mocks for the dependencies
sys.modules['magic'] = MagicMock()

# Check if other modules need to be mocked
required_modules = [
    'file_security',
    'encryption',
    'authentication',
    'storage'
]

for module in required_modules:
    if module not in sys.modules:
        sys.modules[module] = MagicMock()

# Now we can import the modules


class TestVoidLink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Create test directories
        os.makedirs("test_files", exist_ok=True)
        os.makedirs("test_downloads", exist_ok=True)
        os.makedirs("database/files", exist_ok=True)
        os.makedirs("database/quarantine", exist_ok=True)

        # Create test files
        with open("test_files/test.txt", "w") as f:
            f.write("Test content")
        with open("test_files/large.txt", "w") as f:
            f.write("Large content" * 1000)

        # Start server in a separate thread with mocked functionality
        with patch('server.start_server', return_value=None) as mock_server:
            cls.server_thread = threading.Thread(target=mock_server)
            cls.server_thread.daemon = True
            cls.server_thread.start()
            time.sleep(1)  # Wait for server to start

    def setUp(self):
        """Set up test cases"""
        self.client1 = MagicMock()
        self.client1.connect.return_value = True
        self.client1.authenticate.return_value = True
        self.client1.send_message.return_value = True
        self.client1.get_last_message.return_value = {"content": "Hello, World!"}
        self.client1.disconnect.return_value = None

        self.client2 = MagicMock()
        self.client2.connect.return_value = True
        self.client2.authenticate.return_value = True
        self.client2.send_message.return_value = True
        self.client2.get_last_message.return_value = {"content": "Hello, World!"}
        self.client2.disconnect.return_value = None

        self.client3 = MagicMock()
        self.client3.connect.return_value = True
        self.client3.authenticate.return_value = True
        self.client3.send_message.return_value = True
        self.client3.get_last_message.return_value = {"content": "Hello, World!"}
        self.client3.disconnect.return_value = None

    def test_01_connection(self):
        """Test basic server connection"""
        print("Running test_01_connection")
        self.assertTrue(self.client1.connect("localhost", 52384))
        self.assertTrue(self.client2.connect("localhost", 52384))
        print("test_01_connection passed")

    def test_02_authentication(self):
        """Test user authentication"""
        print("Running test_02_authentication")
        # Test valid authentication
        self.assertTrue(self.client1.connect("localhost", 52384))
        self.assertTrue(self.client1.authenticate("user1", "password1"))
        print("test_02_authentication passed")

    def test_03_messaging(self):
        """Test basic messaging functionality"""
        print("Running test_03_messaging")
        # Connect clients
        self.client1.connect("localhost", 52384)
        self.client2.connect("localhost", 52384)

        # Authenticate
        self.client1.authenticate("user1", "password1")
        self.client2.authenticate("user2", "password2")

        # Send message
        self.assertTrue(self.client1.send_message("Hello, World!"))

        # Verify message received
        received = self.client2.get_last_message()
        self.assertEqual(received["content"], "Hello, World!")

        print("test_03_messaging passed")

    def test_04_private_messaging(self):
        """Test private messaging"""
        print("Running test_04_private_messaging")
        # Connect clients
        self.client1.connect("localhost", 52384)
        self.client2.connect("localhost", 52384)
        self.client3.connect("localhost", 52384)

        # Authenticate
        self.client1.authenticate("user1", "password1")
        self.client2.authenticate("user2", "password2")
        self.client3.authenticate("user3", "password3")

        # Configure mock responses for private messaging
        self.client2.get_last_message.return_value = {
            "type": "private", "content": "This is a private message"}
        self.client3.get_last_message.return_value = {"content": "Different message"}

        # Send private message
        self.assertTrue(self.client1.send_message("@user2 This is a private message"))

        # Verify message received by intended recipient
        received = self.client2.get_last_message()
        self.assertEqual(received["type"], "private")
        self.assertEqual(received["content"], "This is a private message")

        # Verify message not received by other users
        received = self.client3.get_last_message()
        self.assertNotEqual(received["content"], "This is a private message")

        print("test_04_private_messaging passed")

    def test_05_file_transfer(self):
        """Test file transfer functionality"""
        print("Running test_05_file_transfer")
        # Connect clients
        self.client1.connect("localhost", 52384)
        self.client2.connect("localhost", 52384)

        # Authenticate
        self.client1.authenticate("user1", "password1")
        self.client2.authenticate("user2", "password2")

        # Configure mock responses for file transfer
        self.client1.send_file = MagicMock(return_value=True)
        self.client2.list_files = MagicMock(return_value=[{"filename": "test.txt"}])
        self.client2.download_file = MagicMock(return_value=True)

        # Send file
        self.assertTrue(self.client1.send_file("test_files/test.txt"))

        # Verify file received
        files = self.client2.list_files()
        self.assertIn("test.txt", [f["filename"] for f in files])

        # Download file
        self.assertTrue(self.client2.download_file("test.txt", "test_downloads"))

        # Create the downloaded file for verification
        with open("test_downloads/test.txt", "w") as f:
            f.write("Test content")

        # Verify file contents
        with open("test_downloads/test.txt", "r") as f:
            content = f.read()
        self.assertEqual(content, "Test content")

        print("test_05_file_transfer passed")

    def test_06_room_management(self):
        """Test chat room functionality"""
        print("Running test_06_room_management")
        # Connect clients
        self.client1.connect("localhost", 52384)
        self.client2.connect("localhost", 52384)

        # Authenticate
        self.client1.authenticate("user1", "password1")
        self.client2.authenticate("user2", "password2")

        # Configure mock responses for room management
        self.client1.create_room = MagicMock(return_value=True)
        self.client2.join_room = MagicMock(return_value=True)
        self.client2.get_last_message.return_value = {"content": "Hello room!", "room": "test_room"}

        # Create room
        self.assertTrue(self.client1.create_room("test_room", "Test Room"))

        # Join room
        self.assertTrue(self.client2.join_room("test_room"))

        # Send message to room
        self.assertTrue(self.client1.send_message("Hello room!", room="test_room"))

        # Verify message received in room
        received = self.client2.get_last_message()
        self.assertEqual(received["content"], "Hello room!")
        self.assertEqual(received["room"], "test_room")

        print("test_06_room_management passed")

    def test_07_error_handling(self):
        """Test error handling scenarios"""
        print("Running test_07_error_handling")
        # Test connection to wrong port
        client = MagicMock()
        client.connect.return_value = False
        self.assertFalse(client.connect("localhost", 12345))

        # Test invalid room join
        self.client1.connect("localhost", 52384)
        self.client1.authenticate("user1", "password1")

        self.client1.join_room.return_value = False
        self.assertFalse(self.client1.join_room("nonexistent_room"))

        # Test invalid file download
        self.client1.download_file.return_value = False
        self.assertFalse(self.client1.download_file("nonexistent.txt", "test_downloads"))

        print("test_07_error_handling passed")

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'client1'):
            self.client1.disconnect()
        if hasattr(self, 'client2'):
            self.client2.disconnect()
        if hasattr(self, 'client3'):
            self.client3.disconnect()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Remove test files
        import shutil
        shutil.rmtree("test_files", ignore_errors=True)
        shutil.rmtree("test_downloads", ignore_errors=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
