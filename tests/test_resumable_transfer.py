#!/usr/bin/env python3
"""
Tests for the resumable file transfer module
"""

import os
import sys
import unittest
import tempfile
import json
import shutil
import hashlib
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from file_transfer_resumable import (
    ensure_dirs, TransferState, start_resumable_upload, handle_chunk,
    complete_resumable_upload, start_resumable_download, send_file_chunk,
    get_active_transfers, cancel_transfer
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

class TestResumableTransfer(unittest.TestCase):
    """Test cases for resumable file transfer module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.original_storage_dir = file_transfer_resumable.FILE_STORAGE_DIR
        self.original_metadata_file = file_transfer_resumable.FILE_METADATA_FILE
        self.original_temp_dir = file_transfer_resumable.TEMP_DIR
        
        # Set the directories to temporary directories
        file_transfer_resumable.FILE_STORAGE_DIR = os.path.join(self.test_dir, "files")
        file_transfer_resumable.FILE_METADATA_FILE = os.path.join(self.test_dir, "file_metadata.json")
        file_transfer_resumable.TEMP_DIR = os.path.join(self.test_dir, "temp")
        
        # Create test file
        self.test_file_path = os.path.join(self.test_dir, "test_file.txt")
        with open(self.test_file_path, "w") as f:
            f.write("This is a test file for resumable file transfer.")
        
        # Ensure directories
        ensure_dirs()
        
        # Clear active transfers
        file_transfer_resumable.active_transfers.clear()
        file_transfer_resumable.transfer_locks.clear()
    
    def tearDown(self):
        """Clean up after tests"""
        # Restore original paths
        file_transfer_resumable.FILE_STORAGE_DIR = self.original_storage_dir
        file_transfer_resumable.FILE_METADATA_FILE = self.original_metadata_file
        file_transfer_resumable.TEMP_DIR = self.original_temp_dir
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        
        # Clear active transfers
        file_transfer_resumable.active_transfers.clear()
        file_transfer_resumable.transfer_locks.clear()
    
    def test_transfer_state(self):
        """Test TransferState class"""
        # Create transfer state
        state = TransferState("test_file.txt", 1024, "testuser")
        
        # Verify initial state
        self.assertEqual(state.filename, "test_file.txt")
        self.assertEqual(state.total_size, 1024)
        self.assertEqual(state.sender, "testuser")
        self.assertEqual(state.received_size, 0)
        self.assertEqual(state.chunks_received, 0)
        self.assertFalse(state.complete)
        self.assertFalse(state.failed)
        
        # Test opening temp file
        state.open_temp_file()
        self.assertIsNotNone(state.temp_file)
        self.assertIsNotNone(state.temp_path)
        
        # Test writing chunk
        chunk_data = b"Test chunk data"
        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
        success = state.write_chunk(0, chunk_data, chunk_hash)
        self.assertTrue(success)
        self.assertEqual(state.received_size, len(chunk_data))
        self.assertEqual(state.chunks_received, 1)
        
        # Test closing temp file
        state.close_temp_file()
        self.assertIsNone(state.temp_file)
        
        # Test get progress
        progress = state.get_progress()
        self.assertEqual(progress["filename"], "test_file.txt")
        self.assertEqual(progress["total_size"], 1024)
        self.assertEqual(progress["received_size"], len(chunk_data))
        self.assertEqual(progress["chunks_received"], 1)
    
    @patch('file_transfer_resumable.encrypt_message')
    def test_start_resumable_upload(self, mock_encrypt_message):
        """Test starting resumable upload"""
        # Set up mocks
        mock_encrypt_message.return_value = b"encrypted_message"
        
        # Create mock socket
        mock_socket = MockSocket()
        
        # Start resumable upload
        result = start_resumable_upload(mock_socket, "test_file.txt", 1024, "testuser")
        
        # Verify result
        self.assertIn("transfer_id", result)
        self.assertEqual(result["filename"], "test_file.txt")
        self.assertEqual(result["total_size"], 1024)
        self.assertEqual(result["sender"], "testuser")
        
        # Verify active transfers
        self.assertEqual(len(file_transfer_resumable.active_transfers), 1)
        
        # Verify socket communication
        self.assertEqual(len(mock_socket.sent_data), 1)
    
    @patch('file_transfer_resumable.encrypt_message')
    def test_handle_chunk(self, mock_encrypt_message):
        """Test handling chunk"""
        # Set up mocks
        mock_encrypt_message.return_value = b"encrypted_message"
        
        # Create mock socket
        mock_socket = MockSocket()
        
        # Start resumable upload
        result = start_resumable_upload(mock_socket, "test_file.txt", 1024, "testuser")
        transfer_id = result["transfer_id"]
        
        # Create chunk data
        chunk_data = b"Test chunk data"
        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
        
        # Handle chunk
        result = handle_chunk(mock_socket, transfer_id, 0, chunk_data, chunk_hash)
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertIn("progress", result)
        
        # Verify transfer state
        state = file_transfer_resumable.active_transfers[transfer_id]
        self.assertEqual(state.received_size, len(chunk_data))
        self.assertEqual(state.chunks_received, 1)
        
        # Verify socket communication
        self.assertEqual(len(mock_socket.sent_data), 2)  # Initial message + ack
    
    @patch('file_transfer_resumable.encrypt_message')
    @patch('file_security.scan_file')
    def test_complete_resumable_upload(self, mock_scan_file, mock_encrypt_message):
        """Test completing resumable upload"""
        # Set up mocks
        mock_encrypt_message.return_value = b"encrypted_message"
        mock_scan_file.return_value = {
            "is_safe": True,
            "size_check": "PASSED",
            "extension_check": "PASSED",
            "mime_check": "PASSED"
        }
        
        # Create mock socket
        mock_socket = MockSocket()
        
        # Start resumable upload
        result = start_resumable_upload(mock_socket, "test_file.txt", 1024, "testuser")
        transfer_id = result["transfer_id"]
        
        # Create chunk data
        chunk_data = b"Test chunk data"
        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
        
        # Handle chunk
        handle_chunk(mock_socket, transfer_id, 0, chunk_data, chunk_hash)
        
        # Complete upload
        result = complete_resumable_upload(mock_socket, transfer_id)
        
        # Verify result
        self.assertIn("filename", result)
        self.assertIn("hash", result)
        
        # Verify active transfers
        self.assertEqual(len(file_transfer_resumable.active_transfers), 0)
        
        # Verify socket communication
        self.assertEqual(len(mock_socket.sent_data), 3)  # Initial message + ack + completion
    
    @patch('file_transfer_resumable.encrypt_message')
    def test_start_resumable_download(self, mock_encrypt_message):
        """Test starting resumable download"""
        # Set up mocks
        mock_encrypt_message.return_value = b"encrypted_message"
        
        # Create mock socket
        mock_socket = MockSocket()
        
        # Create test file in storage directory
        stored_file_path = os.path.join(file_transfer_resumable.FILE_STORAGE_DIR, "download_test.txt")
        with open(stored_file_path, "w") as f:
            f.write("This is a file for download testing.")
        
        # Start resumable download
        result = start_resumable_download(mock_socket, "download_test.txt")
        
        # Verify result
        self.assertIn("transfer_id", result)
        self.assertEqual(result["filename"], "download_test.txt")
        
        # Verify socket communication
        self.assertEqual(len(mock_socket.sent_data), 1)
    
    @patch('file_transfer_resumable.encrypt_message')
    def test_send_file_chunk(self, mock_encrypt_message):
        """Test sending file chunk"""
        # Set up mocks
        mock_encrypt_message.side_effect = lambda x: b"encrypted_" + (x if isinstance(x, bytes) else str(x).encode())
        
        # Create mock socket
        mock_socket = MockSocket()
        
        # Create test file in storage directory
        stored_file_path = os.path.join(file_transfer_resumable.FILE_STORAGE_DIR, "chunk_test.txt")
        with open(stored_file_path, "w") as f:
            f.write("This is a file for chunk testing.")
        
        # Send file chunk
        result = send_file_chunk(mock_socket, "test_transfer", "chunk_test.txt", 0)
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertIn("chunk_hash", result)
        
        # Verify socket communication
        self.assertEqual(len(mock_socket.sent_data), 3)  # Message + size + chunk
    
    def test_get_active_transfers(self):
        """Test getting active transfers"""
        # Create mock socket
        mock_socket = MockSocket()
        
        # Start two uploads
        result1 = start_resumable_upload(mock_socket, "file1.txt", 1024, "user1")
        result2 = start_resumable_upload(mock_socket, "file2.txt", 2048, "user2")
        
        # Get active transfers
        transfers = get_active_transfers()
        
        # Verify result
        self.assertEqual(len(transfers), 2)
        self.assertIn(result1["transfer_id"], transfers)
        self.assertIn(result2["transfer_id"], transfers)
    
    def test_cancel_transfer(self):
        """Test cancelling transfer"""
        # Create mock socket
        mock_socket = MockSocket()
        
        # Start upload
        result = start_resumable_upload(mock_socket, "cancel_test.txt", 1024, "testuser")
        transfer_id = result["transfer_id"]
        
        # Verify transfer exists
        self.assertIn(transfer_id, file_transfer_resumable.active_transfers)
        
        # Cancel transfer
        success = cancel_transfer(transfer_id)
        
        # Verify result
        self.assertTrue(success)
        
        # Verify transfer was removed
        self.assertNotIn(transfer_id, file_transfer_resumable.active_transfers)

if __name__ == "__main__":
    unittest.main()