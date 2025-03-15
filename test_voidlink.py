#!/usr/bin/env python3
"""
VoidLink Test Suite - Comprehensive tests for real-life usage scenarios
"""

import unittest
import threading
import socket
import json
import os
import time
from server import start_server
from client import VoidLinkClient
from encryption import encrypt_message, decrypt_message


class TestVoidLink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Start server in a separate thread
        cls.server_thread = threading.Thread(target=start_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # Wait for server to start

        # Create test directories
        os.makedirs("test_files", exist_ok=True)
        os.makedirs("test_downloads", exist_ok=True)

        # Create test files
        with open("test_files/test.txt", "w") as f:
            f.write("Test content")
        with open("test_files/large.txt", "w") as f:
            f.write("Large content" * 1000)

    def setUp(self):
        """Set up test cases"""
        self.client1 = VoidLinkClient()
        self.client2 = VoidLinkClient()
        self.client3 = VoidLinkClient()

    def test_01_connection(self):
        """Test basic server connection"""
        self.assertTrue(self.client1.connect("localhost", 52384))
        self.assertTrue(self.client2.connect("localhost", 52384))

    def test_02_authentication(self):
        """Test user authentication"""
        # Test valid authentication
        self.assertTrue(self.client1.connect("localhost", 52384))
        self.assertTrue(self.client1.authenticate("user1", "password1"))

        # Test invalid authentication
        self.assertTrue(self.client2.connect("localhost", 52384))
        self.assertFalse(self.client2.authenticate("user2", "wrongpass"))

    def test_03_messaging(self):
        """Test basic messaging functionality"""
        # Connect and authenticate clients
        self.client1.connect("localhost", 52384)
        self.client2.connect("localhost", 52384)
        self.client1.authenticate("user1", "password1")
        self.client2.authenticate("user2", "password2")

        # Test message sending
        message = "Hello, World!"
        self.assertTrue(self.client1.send_message(message))

        # Wait for message delivery
        time.sleep(0.5)

        # Verify message received
        received = self.client2.get_last_message()
        self.assertEqual(received["content"], message)

    def test_04_private_messaging(self):
        """Test private messaging"""
        # Connect and authenticate clients
        self.client1.connect("localhost", 52384)
        self.client2.connect("localhost", 52384)
        self.client3.connect("localhost", 52384)
        self.client1.authenticate("user1", "password1")
        self.client2.authenticate("user2", "password2")
        self.client3.authenticate("user3", "password3")

        # Send private message
        message = "@user2 This is a private message"
        self.client1.send_message(message)

        time.sleep(0.5)

        # Verify message received by intended recipient
        received = self.client2.get_last_message()
        self.assertEqual(received["type"], "private")
        self.assertEqual(received["content"], "This is a private message")

        # Verify message not received by other users
        received = self.client3.get_last_message()
        self.assertNotEqual(received["content"], "This is a private message")

    def test_05_file_transfer(self):
        """Test file transfer functionality"""
        # Connect and authenticate clients
        self.client1.connect("localhost", 52384)
        self.client2.connect("localhost", 52384)
        self.client1.authenticate("user1", "password1")
        self.client2.authenticate("user2", "password2")

        # Send file
        self.assertTrue(self.client1.send_file("test_files/test.txt"))

        time.sleep(1)

        # Verify file received
        files = self.client2.list_files()
        self.assertIn("test.txt", [f["filename"] for f in files])

        # Download file
        self.assertTrue(self.client2.download_file("test.txt", "test_downloads"))

        # Verify file contents
        with open("test_downloads/test.txt", "r") as f:
            content = f.read()
        self.assertEqual(content, "Test content")

    def test_06_room_management(self):
        """Test chat room functionality"""
        # Connect and authenticate clients
        self.client1.connect("localhost", 52384)
        self.client2.connect("localhost", 52384)
        self.client1.authenticate("user1", "password1")
        self.client2.authenticate("user2", "password2")

        # Create room
        room_id = "test_room"
        self.assertTrue(self.client1.create_room(room_id, "Test Room"))

        # Join room
        self.assertTrue(self.client2.join_room(room_id))

        # Send message to room
        message = "Hello room!"
        self.client1.send_message(message, room=room_id)

        time.sleep(0.5)

        # Verify message received in room
        received = self.client2.get_last_message()
        self.assertEqual(received["content"], message)
        self.assertEqual(received["room"], room_id)

    def test_07_large_file_transfer(self):
        """Test large file transfer"""
        # Connect and authenticate clients
        self.client1.connect("localhost", 52384)
        self.client2.connect("localhost", 52384)
        self.client1.authenticate("user1", "password1")
        self.client2.authenticate("user2", "password2")

        # Send large file
        self.assertTrue(self.client1.send_file("test_files/large.txt"))

        time.sleep(2)

        # Verify file received
        files = self.client2.list_files()
        self.assertIn("large.txt", [f["filename"] for f in files])

        # Download and verify large file
        self.assertTrue(self.client2.download_file("large.txt", "test_downloads"))

        with open("test_downloads/large.txt", "r") as f:
            content = f.read()
        self.assertEqual(content, "Large content" * 1000)

    def test_08_concurrent_messaging(self):
        """Test concurrent message handling"""
        # Connect and authenticate all clients
        self.client1.connect("localhost", 52384)
        self.client2.connect("localhost", 52384)
        self.client3.connect("localhost", 52384)
        self.client1.authenticate("user1", "password1")
        self.client2.authenticate("user2", "password2")
        self.client3.authenticate("user3", "password3")

        # Send messages concurrently
        messages = []

        def send_messages(client, count):
            for i in range(count):
                msg = f"Message {i} from {client.username}"
                messages.append(msg)
                client.send_message(msg)
                time.sleep(0.1)

        threads = [
            threading.Thread(target=send_messages, args=(self.client1, 5)),
            threading.Thread(target=send_messages, args=(self.client2, 5)),
            threading.Thread(target=send_messages, args=(self.client3, 5))
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        time.sleep(1)

        # Verify all messages received
        received_messages = self.client1.get_message_history()
        for msg in messages:
            self.assertTrue(any(msg in m["content"] for m in received_messages))

    def test_09_error_handling(self):
        """Test error handling scenarios"""
        # Test connection to wrong port
        client = VoidLinkClient()
        self.assertFalse(client.connect("localhost", 12345))

        # Test invalid room join
        self.client1.connect("localhost", 52384)
        self.client1.authenticate("user1", "password1")
        self.assertFalse(self.client1.join_room("nonexistent_room"))

        # Test invalid file download
        self.assertFalse(self.client1.download_file("nonexistent.txt", "test_downloads"))

    def test_10_reconnection(self):
        """Test client reconnection"""
        # Connect and authenticate
        self.client1.connect("localhost", 52384)
        self.client1.authenticate("user1", "password1")

        # Simulate connection loss
        self.client1.disconnect()
        time.sleep(1)

        # Reconnect
        self.assertTrue(self.client1.connect("localhost", 52384))
        self.assertTrue(self.client1.authenticate("user1", "password1"))

        # Verify functionality after reconnection
        self.assertTrue(self.client1.send_message("After reconnection"))

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
