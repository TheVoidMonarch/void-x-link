#!/usr/bin/env python3
"""
Simple test for the file_security module
"""

import sys
import os
import tempfile

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the file_security module
import file_security

def test_is_file_too_large():
    """Test the is_file_too_large function"""
    # Test with a small file size
    assert not file_security.is_file_too_large(1024)
    
    # Test with a large file size
    assert file_security.is_file_too_large(file_security.MAX_FILE_SIZE + 1)
    
    print("is_file_too_large test passed!")
    return True

def test_has_dangerous_extension():
    """Test the has_dangerous_extension function"""
    # Test with a safe extension
    assert not file_security.has_dangerous_extension("test.txt")
    
    # Test with a dangerous extension
    assert file_security.has_dangerous_extension("test.exe")
    
    print("has_dangerous_extension test passed!")
    return True

def test_is_mime_type_allowed():
    """Test the is_mime_type_allowed function"""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        # Test with a safe MIME type
        allowed, mime_type = file_security.is_mime_type_allowed(temp_file.name)
        assert allowed
    
    # Create a temporary file with a dangerous extension
    with tempfile.NamedTemporaryFile(suffix=".exe") as temp_file:
        # Test with a dangerous MIME type
        allowed, mime_type = file_security.is_mime_type_allowed(temp_file.name)
        assert not allowed
    
    print("is_mime_type_allowed test passed!")
    return True

def test_calculate_file_hash():
    """Test the calculate_file_hash function"""
    # Create a temporary file with known content
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as temp_file:
        temp_file.write("test content")
        temp_file.flush()
        
        # Calculate the hash
        file_hash = file_security.calculate_file_hash(temp_file.name)
        
        # Verify the hash is a string
        assert isinstance(file_hash, str)
        
        # Verify the hash is not empty
        assert file_hash
    
    print("calculate_file_hash test passed!")
    return True

def test_scan_file():
    """Test the scan_file function"""
    # Create a temporary file with safe content
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as temp_file:
        temp_file.write("test content")
        temp_file.flush()
        
        # Scan the file
        results = file_security.scan_file(temp_file.name, "test.txt", 12)
        
        # Verify the results
        assert results["is_safe"]
        assert results["size_check"] == "PASSED"
        assert results["extension_check"] == "PASSED"
        assert results["mime_check"] == "PASSED"
    
    # Create a temporary file with a dangerous extension
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".exe") as temp_file:
        temp_file.write("test content")
        temp_file.flush()
        
        # Scan the file
        results = file_security.scan_file(temp_file.name, "test.exe", 12)
        
        # Verify the results
        assert not results["is_safe"]
        assert results["size_check"] == "PASSED"
        assert results["extension_check"] == "FAILED"
    
    print("scan_file test passed!")
    return True

if __name__ == "__main__":
    print("Running simple file_security tests...")
    
    success = True
    
    try:
        success = test_is_file_too_large() and success
    except Exception as e:
        print(f"is_file_too_large test failed: {str(e)}")
        success = False
    
    try:
        success = test_has_dangerous_extension() and success
    except Exception as e:
        print(f"has_dangerous_extension test failed: {str(e)}")
        success = False
    
    try:
        success = test_is_mime_type_allowed() and success
    except Exception as e:
        print(f"is_mime_type_allowed test failed: {str(e)}")
        success = False
    
    try:
        success = test_calculate_file_hash() and success
    except Exception as e:
        print(f"calculate_file_hash test failed: {str(e)}")
        success = False
    
    try:
        success = test_scan_file() and success
    except Exception as e:
        print(f"scan_file test failed: {str(e)}")
        success = False
    
    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed.")
        sys.exit(1)