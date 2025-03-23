#!/usr/bin/env python3
"""
VoidLink Device ID Module - Provides functions for device identification
"""

import os
import sys
import uuid
import hashlib
import platform
import socket
import json
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voidlink_device_id')

# Constants
DEVICE_ID_FILE = "device_id.json"

def get_hardware_info() -> dict:
    """Get hardware information for device identification"""
    info = {}
    
    # Get platform information
    info['platform'] = platform.platform()
    info['machine'] = platform.machine()
    info['processor'] = platform.processor()
    info['node'] = platform.node()
    
    # Get network information
    try:
        info['hostname'] = socket.gethostname()
        info['ip'] = socket.gethostbyname(socket.gethostname())
    except:
        info['hostname'] = "unknown"
        info['ip'] = "unknown"
    
    # Get MAC address (platform specific)
    try:
        if sys.platform == 'win32':
            # Windows
            import subprocess
            output = subprocess.check_output('getmac').decode()
            mac = output.split('\r\n')[3].replace('-', ':').split()[0]
            info['mac'] = mac
        else:
            # Unix-like
            from uuid import getnode
            mac = ':'.join(['{:02x}'.format((getnode() >> elements) & 0xff) 
                           for elements in range(0, 48, 8)][::-1])
            info['mac'] = mac
    except:
        info['mac'] = "unknown"
    
    return info

def generate_device_id() -> str:
    """Generate a unique device ID based on hardware information"""
    # Get hardware info
    hw_info = get_hardware_info()
    
    # Create a string with all hardware info
    hw_str = json.dumps(hw_info, sort_keys=True)
    
    # Hash the hardware info to create a device ID
    device_id = hashlib.sha256(hw_str.encode()).hexdigest()
    
    return device_id

def get_device_id(regenerate: bool = False) -> str:
    """
    Get the device ID, generating and saving if it doesn't exist
    
    Args:
        regenerate: If True, regenerate the device ID even if it exists
        
    Returns:
        The device ID as a string
    """
    # Check if device ID file exists
    if os.path.exists(DEVICE_ID_FILE) and not regenerate:
        try:
            with open(DEVICE_ID_FILE, 'r') as f:
                data = json.load(f)
                if 'device_id' in data:
                    return data['device_id']
        except Exception as e:
            logger.warning(f"Error reading device ID file: {e}")
    
    # Generate new device ID
    device_id = generate_device_id()
    
    # Save device ID
    try:
        with open(DEVICE_ID_FILE, 'w') as f:
            json.dump({'device_id': device_id}, f, indent=4)
    except Exception as e:
        logger.warning(f"Error saving device ID: {e}")
    
    return device_id

def verify_device_id(stored_id: str) -> bool:
    """
    Verify if the current device matches the stored device ID
    
    Args:
        stored_id: The stored device ID to verify against
        
    Returns:
        True if the device IDs match, False otherwise
    """
    current_id = get_device_id()
    return current_id == stored_id

if __name__ == "__main__":
    # Test the device ID generation
    device_id = get_device_id()
    print(f"Device ID: {device_id}")
    
    # Verify the device ID
    print(f"Device ID verification: {verify_device_id(device_id)}")