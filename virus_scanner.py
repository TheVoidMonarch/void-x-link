#!/usr/bin/env python3
"""
VoidLink Virus Scanner Module - Provides virus scanning for file uploads
"""

import os
import clamd
import socket
import tempfile
from typing import Dict, Tuple, Optional, List
from error_handling import logger, log_info, log_warning, log_error, FileSecurityError

# Constants
CLAMD_SOCKET = "/var/run/clamav/clamd.sock"  # Default ClamAV socket path
CLAMD_HOST = "localhost"  # Default ClamAV host
CLAMD_PORT = 3310  # Default ClamAV port

def get_clamd():
    """Get a connection to ClamAV daemon"""
    try:
        # Try to connect via Unix socket first
        if os.path.exists(CLAMD_SOCKET):
            return clamd.ClamdUnixSocket(path=CLAMD_SOCKET)
        
        # Try to connect via TCP
        try:
            return clamd.ClamdNetworkSocket(host=CLAMD_HOST, port=CLAMD_PORT)
        except (clamd.ConnectionError, socket.error):
            log_warning("Could not connect to ClamAV daemon via network")
            return None
    
    except Exception as e:
        log_warning(f"Could not initialize ClamAV connection: {str(e)}")
        return None

def is_clamd_available() -> bool:
    """Check if ClamAV daemon is available"""
    try:
        cd = get_clamd()
        if cd:
            version = cd.version()
            log_info(f"ClamAV version: {version}")
            return True
        return False
    except Exception as e:
        log_warning(f"ClamAV not available: {str(e)}")
        return False

def scan_file_for_viruses(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Scan a file for viruses using ClamAV
    
    Args:
        file_path: Path to the file to scan
        
    Returns:
        Tuple of (is_clean, virus_name)
        - is_clean: True if no virus found, False otherwise
        - virus_name: Name of the virus if found, None otherwise
    """
    if not os.path.exists(file_path):
        log_error(f"File not found for virus scanning: {file_path}")
        return False, "File not found"
    
    # Check if ClamAV is available
    if not is_clamd_available():
        log_warning("ClamAV not available, skipping virus scan")
        return True, None
    
    try:
        cd = get_clamd()
        if not cd:
            log_warning("Could not connect to ClamAV daemon, skipping virus scan")
            return True, None
        
        # Scan the file
        scan_result = cd.scan(file_path)
        
        # Parse the result
        file_result = scan_result.get(file_path)
        if file_result:
            status, virus_name = file_result
            if status == "FOUND":
                log_warning(f"Virus found in {file_path}: {virus_name}")
                return False, virus_name
        
        # No virus found
        log_info(f"No virus found in {file_path}")
        return True, None
    
    except Exception as e:
        log_error(f"Error scanning file for viruses: {str(e)}")
        return False, f"Scan error: {str(e)}"

def scan_file_content(file_content: bytes) -> Tuple[bool, Optional[str]]:
    """
    Scan file content for viruses using ClamAV
    
    Args:
        file_content: File content as bytes
        
    Returns:
        Tuple of (is_clean, virus_name)
    """
    if not file_content:
        return False, "Empty file content"
    
    # Check if ClamAV is available
    if not is_clamd_available():
        log_warning("ClamAV not available, skipping virus scan")
        return True, None
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(file_content)
        
        try:
            # Scan the temporary file
            return scan_file_for_viruses(temp_path)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        log_error(f"Error scanning file content for viruses: {str(e)}")
        return False, f"Scan error: {str(e)}"

# Initialize by checking if ClamAV is available
CLAMD_AVAILABLE = is_clamd_available()
if CLAMD_AVAILABLE:
    log_info("ClamAV is available for virus scanning")
else:
    log_warning("ClamAV is not available, virus scanning will be skipped")