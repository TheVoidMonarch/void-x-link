#!/usr/bin/env python3
"""
Tests for the file transfer module
"""

import os
import sys
import unittest
import tempfile
import json
import shutil
import socket
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import after adding parent directory to path
import file_transfer
from file_transfer import (
    ensure_file_dirs, handle_file_transfer, send_file,
    save_file_metadata, get_file_list, get_file_metadata, delete_file
)


class MockSocket:
    """Mock socket for testing"""

    def __init__(self):
        self.sent_data = []
        self.recv_data = []
        self.recv_index = 0

    def send(self, data):
        """Mock send method"""
        self.sent_data.append(data)
        return len(data)

    def recv(self, bufsize):
        """Mock recv method"""
        if self.recv_index >= len(self.recv_data):
            return b''
        data = self.recv_data[self.recv_index]
        self.recv_index += 1
        return data

    def add_recv_data(self, data):
        """Add data to be received"""
        self.recv_data.append(data)


class TestFileTransfer(unittest.TestCase):
    """Test cases for file transfer module"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.original_storage_dir = file_transfer.FILE_STORAGE_DIR
        self.original_metadata_file = file_transfer.FILE_METADATA_FILE

        # Set the storage directory to a temporary directory
        file_transfer.FILE_STORAGE_DIR = os.path.join(self.test_dir, "files")
        file_transfer.FILE_METADATA_FILE = os.path.join(self.test_dir, "file_metadata.json")

        # Create test file
        self.test_file_path = os.path.join(self.test_dir, "test_file.txt")
        with open(self.test_file_path, "w") as f:
            f.write("This is a test file for file transfer.")

        # Ensure directories
        ensure_file_dirs()

    def tearDown(self):
        """Clean up after tests"""
        # Restore original paths
        file_transfer.FILE_STORAGE_DIR = self.original_storage_dir
        file_transfer.FILE_METADATA_FILE = self.original_metadata_file

        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_ensure_file_dirs(self):
        """Test ensuring file directories exist"""
        # Remove directories if they exist
        if os.path.exists(file_transfer.FILE_STORAGE_DIR):
            shutil.rmtree(file_transfer.FILE_STORAGE_DIR)
        if os.path.exists(os.path.dirname(file_transfer.FILE_METADATA_FILE)):
            os.remove(file_transfer.FILE_METADATA_FILE)

        # Ensure directories
        ensure_file_dirs()

        # Verify directories were created
        self.assertTrue(os.path.exists(file_transfer.FILE_STORAGE_DIR))
        self.assertTrue(os.path.exists(file_transfer.FILE_METADATA_FILE))

    @patch('file_transfer.decrypt_message')
    @patch('file_security.scan_file')
    def test_handle_file_transfer(self, mock_scan_file, mock_decrypt_message):
        """Test handling file transfer"""
        # Set up mocks
        mock_decrypt_message.return_value = b"Test file content"
        mock_scan_file.return_value = {
            "is_safe": True,
            "size_check": "PASSED",
            "extension_check": "PASSED",
            "mime_check": "PASSED"
        }

        # Create mock socket
        mock_socket = MockSocket()
        mock_socket.add_recv_data((8).to_bytes(8, byteorder='big'))  # Chunk size
        mock_socket.add_recv_data(b"encrypted_chunk")  # Encrypted chunk
        mock_socket.add_recv_data(b'ENDFILE')  # End of file marker

        # Handle file transfer
        result = handle_file_transfer(mock_socket, "test_file.txt", "testuser")

        # Verify result
        self.assertEqual(result["filename"], "test_file.txt")
        self.assertEqual(result["uploaded_by"], "testuser")
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    file_transfer.FILE_STORAGE_DIR,
                    "test_file.txt")))

    @patch('file_transfer.encrypt_message')
    def test_send_file(self, mock_encrypt_message):
        """Test sending file"""
        # Set up mocks
        mock_encrypt_message.return_value = b"encrypted_chunk"

        # Create test file in storage directory
        stored_file_path = os.path.join(file_transfer.FILE_STORAGE_DIR, "stored_file.txt")
        with open(stored_file_path, "w") as f:
            f.write("This is a stored file for testing.")

        # Create mock socket
        mock_socket = MockSocket()

        # Create file metadata
        metadata = {
            "filename": "stored_file.txt",
            "original_filename": "stored_file.txt",
            "path": stored_file_path,
            "size": os.path.getsize(stored_file_path),
            "hash": "test_hash",
            "uploaded_by": "testuser",
            "timestamp": 1234567890,
            "security_scan": {
                "is_safe": True
            }
        }
        save_file_metadata(metadata)

        # Send file
        result = send_file(mock_socket, "stored_file.txt")

        # Verify result
        self.assertTrue(result)
        self.assertTrue(len(mock_socket.sent_data) > 0)

    def test_save_file_metadata(self):
        """Test saving file metadata"""
        # Create test metadata
        metadata = {
            "filename": "metadata_test.txt",
            "original_filename": "metadata_test.txt",
            "path": "/path/to/metadata_test.txt",
            "size": 1024,
            "hash": "test_hash",
            "uploaded_by": "testuser",
            "timestamp": 1234567890
        }

        # Save metadata
        save_file_metadata(metadata)

        # Verify metadata was saved
        with open(file_transfer.FILE_METADATA_FILE, "r") as f:
            file_list = json.load(f)

        self.assertTrue(any(f["filename"] == "metadata_test.txt" for f in file_list))

    def test_get_file_list(self):
        """Test getting file list"""
        # Create test metadata
        metadata1 = {
            "filename": "file1.txt",
            "original_filename": "file1.txt",
            "path": "/path/to/file1.txt",
            "size": 1024,
            "hash": "hash1",
            "uploaded_by": "user1",
            "timestamp": 1234567890
        }

        metadata2 = {
            "filename": "file2.txt",
            "original_filename": "file2.txt",
            "path": "/path/to/file2.txt",
            "size": 2048,
            "hash": "hash2",
            "uploaded_by": "user2",
            "timestamp": 1234567891
        }

        # Save metadata
        save_file_metadata(metadata1)
        save_file_metadata(metadata2)

        # Get file list
        file_list = get_file_list()

        # Verify file list
        self.assertEqual(len(file_list), 2)
        self.assertTrue(any(f["filename"] == "file1.txt" for f in file_list))
        self.assertTrue(any(f["filename"] == "file2.txt" for f in file_list))

    def test_get_file_metadata(self):
        """Test getting file metadata"""
        # Create test metadata
        metadata = {
            "filename": "metadata_get_test.txt",
            "original_filename": "metadata_get_test.txt",
            "path": "/path/to/metadata_get_test.txt",
            "size": 1024,
            "hash": "test_hash",
            "uploaded_by": "testuser",
            "timestamp": 1234567890
        }

        # Save metadata
        save_file_metadata(metadata)

        # Get metadata
        result = get_file_metadata("metadata_get_test.txt")

        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result["filename"], "metadata_get_test.txt")
        self.assertEqual(result["size"], 1024)

    def test_delete_file(self):
        """Test deleting file"""
        # Create test file in storage directory
        stored_file_path = os.path.join(file_transfer.FILE_STORAGE_DIR, "delete_test.txt")
        with open(stored_file_path, "w") as f:
            f.write("This is a file to be deleted.")

        # Create file metadata
        metadata = {
            "filename": "delete_test.txt",
            "original_filename": "delete_test.txt",
            "path": stored_file_path,
            "size": os.path.getsize(stored_file_path),
            "hash": "test_hash",
            "uploaded_by": "testuser",
            "timestamp": 1234567890
        }
        save_file_metadata(metadata)

        # Delete file
        result = delete_file("delete_test.txt")

        # Verify result
        self.assertTrue(result)
        self.assertFalse(os.path.exists(stored_file_path))

        # Verify metadata was updated
        self.assertIsNone(get_file_metadata("delete_test.txt"))


if __name__ == "__main__":
    unittest.main()
