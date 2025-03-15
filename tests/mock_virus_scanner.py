#!/usr/bin/env python3
"""
Mock version of the virus_scanner module for testing
"""

import os
from typing import Dict, Tuple, Optional, List

# Constants
CLAMD_SOCKET = "/var/run/clamav/clamd.sock"  # Default ClamAV socket path
CLAMD_HOST = "localhost"  # Default ClamAV host
CLAMD_PORT = 3310  # Default ClamAV port

# Mock ClamAV availability
CLAMD_AVAILABLE = True


def get_clamd():
    """Get a connection to ClamAV daemon"""
    return ClamdUnixSocket()


def is_clamd_available() -> bool:
    """Check if ClamAV daemon is available"""
    return CLAMD_AVAILABLE


def scan_file_for_viruses(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Mock version: Scan a file for viruses
    
    Args:
        file_path: Path to the file to scan
        
    Returns:
        Tuple of (is_clean, virus_name)
    """
    if not os.path.exists(file_path):
        return False, "File not found"
    
    # For testing, we'll consider certain files as "infected"
    if "virus" in file_path.lower() or "malware" in file_path.lower():
        return False, "Test virus detected"
    
    # All other files are considered clean
    return True, None


def scan_file_content(file_content: bytes) -> Tuple[bool, Optional[str]]:
    """
    Mock version: Scan file content for viruses
    
    Args:
        file_content: File content as bytes
        
    Returns:
        Tuple of (is_clean, virus_name)
    """
    if not file_content:
        return False, "Empty file content"
    
    # For testing, we'll consider certain content as "infected"
    if b"virus" in file_content.lower() or b"malware" in file_content.lower():
        return False, "Test virus detected"
    
    # All other content is considered clean
    return True, None


class ClamdUnixSocket:
    """Mock ClamdUnixSocket class"""
    
    def __init__(self, path=None):
        self.path = path
    
    def scan(self, file_path):
        """Mock scan method"""
        # For testing, we'll consider certain files as "infected"
        if "virus" in file_path.lower() or "malware" in file_path.lower():
            return {file_path: ('FOUND', 'Test virus')}
        return {file_path: ('OK', None)}
    
    def version(self):
        """Mock version method"""
        return "MockClamAV 0.0.0"


class ClamdNetworkSocket:
    """Mock ClamdNetworkSocket class"""
    
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port
    
    def scan(self, file_path):
        """Mock scan method"""
        # For testing, we'll consider certain files as "infected"
        if "virus" in file_path.lower() or "malware" in file_path.lower():
            return {file_path: ('FOUND', 'Test virus')}
        return {file_path: ('OK', None)}
    
    def version(self):
        """Mock version method"""
        return "MockClamAV 0.0.0"