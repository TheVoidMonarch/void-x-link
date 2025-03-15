#!/usr/bin/env python3
"""
Tests for the file security module
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from file_security import (
    ensure_security_dirs, is_file_too_large, has_dangerous_extension,
    is_mime_type_allowed, calculate_file_hash, scan_file
)

class TestFileSecurity(unittest.TestCase):
    """Test cases for file security module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.original_quarantine_dir = file_security.QUARANTINE_DIR
        
        # Set the quarantine directory to a temporary directory
        file_security.QUARANTINE_DIR = os.path.join(self.test_dir, "quarantine")
        
        # Create test files
        self.safe_file_path = os.path.join(self.test_dir, "safe_file.txt")
        with open(self.safe_file_path, "w") as f:
            f.write("This is a safe test file.")
        
        self.dangerous_file_path = os.path.join(self.test_dir, "dangerous_file.exe")
        with open(self.dangerous_file_path, "w") as f:
            f.write("This is a dangerous test file.")
        
        self.large_file_path = os.path.join(self.test_dir, "large_file.txt")
        with open(self.large_file_path, "wb") as f:
            f.write(b"0" * (file_security.MAX_FILE_SIZE + 1))
    
    def tearDown(self):
        """Clean up after tests"""
        # Restore original quarantine directory
        file_security.QUARANTINE_DIR = self.original_quarantine_dir
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_ensure_security_dirs(self):
        """Test ensuring security directories exist"""
        # Remove quarantine directory if it exists
        if os.path.exists(file_security.QUARANTINE_DIR):
            shutil.rmtree(file_security.QUARANTINE_DIR)
        
        # Ensure directories
        ensure_security_dirs()
        
        # Verify quarantine directory was created
        self.assertTrue(os.path.exists(file_security.QUARANTINE_DIR))
    
    def test_is_file_too_large(self):
        """Test file size checking"""
        # Test small file
        self.assertFalse(is_file_too_large(1024))
        
        # Test file at the limit
        self.assertFalse(is_file_too_large(file_security.MAX_FILE_SIZE))
        
        # Test file over the limit
        self.assertTrue(is_file_too_large(file_security.MAX_FILE_SIZE + 1))
    
    def test_has_dangerous_extension(self):
        """Test dangerous extension checking"""
        # Test safe extensions
        self.assertFalse(has_dangerous_extension("safe_file.txt"))
        self.assertFalse(has_dangerous_extension("image.jpg"))
        self.assertFalse(has_dangerous_extension("document.pdf"))
        
        # Test dangerous extensions
        self.assertTrue(has_dangerous_extension("dangerous.exe"))
        self.assertTrue(has_dangerous_extension("script.bat"))
        self.assertTrue(has_dangerous_extension("macro.vbs"))
    
    def test_is_mime_type_allowed(self):
        """Test MIME type checking"""
        # Mock the magic.Magic.from_file method
        with patch('magic.Magic') as mock_magic:
            mock_instance = MagicMock()
            mock_magic.return_value = mock_instance
            
            # Test allowed MIME types
            mock_instance.from_file.return_value = "text/plain"
            allowed, mime_type = is_mime_type_allowed(self.safe_file_path)
            self.assertTrue(allowed)
            self.assertEqual(mime_type, "text/plain")
            
            mock_instance.from_file.return_value = "image/jpeg"
            allowed, mime_type = is_mime_type_allowed(self.safe_file_path)
            self.assertTrue(allowed)
            self.assertEqual(mime_type, "image/jpeg")
            
            # Test disallowed MIME types
            mock_instance.from_file.return_value = "application/x-dosexec"
            allowed, mime_type = is_mime_type_allowed(self.dangerous_file_path)
            self.assertFalse(allowed)
            self.assertEqual(mime_type, "application/x-dosexec")
    
    def test_calculate_file_hash(self):
        """Test file hash calculation"""
        # Calculate hash of a known file
        file_hash = calculate_file_hash(self.safe_file_path)
        
        # Verify the hash is a string
        self.assertIsInstance(file_hash, str)
        
        # Verify the hash is not empty
        self.assertTrue(file_hash)
        
        # Verify the hash is consistent
        self.assertEqual(file_hash, calculate_file_hash(self.safe_file_path))
    
    def test_scan_file(self):
        """Test file scanning"""
        # Mock virus scanning
        with patch('virus_scanner.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, None)  # No virus
            
            # Test safe file
            results = scan_file(self.safe_file_path, "safe_file.txt", os.path.getsize(self.safe_file_path))
            self.assertTrue(results["is_safe"])
            self.assertEqual(results["size_check"], "PASSED")
            self.assertEqual(results["extension_check"], "PASSED")
            
            # Test dangerous extension
            results = scan_file(self.dangerous_file_path, "dangerous_file.exe", os.path.getsize(self.dangerous_file_path))
            self.assertFalse(results["is_safe"])
            self.assertEqual(results["extension_check"], "FAILED")
            
            # Test large file
            results = scan_file(self.large_file_path, "large_file.txt", os.path.getsize(self.large_file_path))
            self.assertFalse(results["is_safe"])
            self.assertEqual(results["size_check"], "FAILED")
            
            # Test virus detection
            mock_scan.return_value = (False, "Test Virus")  # Virus detected
            results = scan_file(self.safe_file_path, "infected_file.txt", os.path.getsize(self.safe_file_path))
            self.assertFalse(results["is_safe"])
            self.assertEqual(results["virus_scan"], "FAILED")
            self.assertIn("Virus detected", results["reason"])

if __name__ == "__main__":
    unittest.main()