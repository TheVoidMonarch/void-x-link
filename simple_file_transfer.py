#!/usr/bin/env python3
"""
VoidLink Simple File Transfer Module

A simplified file transfer module for demo purposes.
"""

import os
import json
import logging
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voidlink_file_transfer')

# Constants
FILES_DIR = "database/files"
METADATA_DIR = "database/metadata"

def ensure_directories():
    """Ensure the necessary directories exist"""
    os.makedirs(FILES_DIR, exist_ok=True)
    os.makedirs(METADATA_DIR, exist_ok=True)

def get_file_list(username: str) -> List[Dict[str, Any]]:
    """Get a list of files for a user"""
    ensure_directories()
    
    # Get all metadata files
    files = []
    for filename in os.listdir(METADATA_DIR):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(METADATA_DIR, filename), 'r') as f:
                    metadata = json.load(f)
                
                # Check if user has access
                if metadata["owner"] == username or username in metadata.get("shared_with", []):
                    files.append(metadata)
            except Exception as e:
                logger.error(f"Error reading metadata file {filename}: {e}")
    
    return files

def get_file_metadata(file_id: str) -> Optional[Dict[str, Any]]:
    """Get metadata for a file"""
    ensure_directories()
    
    metadata_path = os.path.join(METADATA_DIR, f"{file_id}.json")
    if not os.path.exists(metadata_path):
        logger.error(f"Metadata file not found: {metadata_path}")
        return None
    
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading metadata file: {e}")
        return None

def save_file_metadata(metadata: Dict[str, Any]) -> bool:
    """Save metadata for a file"""
    ensure_directories()
    
    if "id" not in metadata:
        logger.error("Metadata missing file ID")
        return False
    
    metadata_path = os.path.join(METADATA_DIR, f"{metadata['id']}.json")
    
    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving metadata file: {e}")
        return False

def upload_file(file_path: str, filename: str, owner: str) -> Optional[str]:
    """Upload a file"""
    ensure_directories()
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    # Generate file ID
    file_id = str(uuid.uuid4())
    
    # Determine file path
    dest_path = os.path.join(FILES_DIR, file_id)
    
    try:
        # Copy file
        with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
            dst.write(src.read())
        
        # Create metadata
        file_size = os.path.getsize(dest_path)
        file_type = os.path.splitext(filename)[1][1:].upper() or "Unknown"
        
        metadata = {
            "id": file_id,
            "name": filename,
            "size": format_size(file_size),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": file_type,
            "owner": owner,
            "upload_time": time.time(),
            "shared_with": []
        }
        
        # Save metadata
        if save_file_metadata(metadata):
            logger.info(f"File uploaded: {filename} ({file_id})")
            return file_id
        else:
            # Clean up on metadata save failure
            os.remove(dest_path)
            return None
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        # Clean up on error
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return None

def download_file(file_id: str, output_path: str) -> bool:
    """Download a file"""
    ensure_directories()
    
    # Get metadata
    metadata = get_file_metadata(file_id)
    if not metadata:
        logger.error(f"File not found: {file_id}")
        return False
    
    # Get file path
    file_path = os.path.join(FILES_DIR, file_id)
    if not os.path.exists(file_path):
        logger.error(f"File not found on server: {file_id}")
        return False
    
    try:
        # Copy file
        with open(file_path, 'rb') as src, open(output_path, 'wb') as dst:
            dst.write(src.read())
        
        logger.info(f"File downloaded: {metadata['name']} ({file_id})")
        return True
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return False

def share_file(file_id: str, owner: str, recipient: str) -> bool:
    """Share a file with another user"""
    ensure_directories()
    
    # Get metadata
    metadata = get_file_metadata(file_id)
    if not metadata:
        logger.error(f"File not found: {file_id}")
        return False
    
    # Check if user is the owner
    if metadata["owner"] != owner:
        logger.error(f"User {owner} is not the owner of file {file_id}")
        return False
    
    # Add recipient to shared_with list
    shared_with = metadata.get("shared_with", [])
    if recipient not in shared_with:
        shared_with.append(recipient)
        metadata["shared_with"] = shared_with
        
        # Save metadata
        if save_file_metadata(metadata):
            logger.info(f"File shared: {metadata['name']} ({file_id}) with {recipient}")
            return True
        else:
            return False
    else:
        # Already shared
        logger.info(f"File already shared: {metadata['name']} ({file_id}) with {recipient}")
        return True

def delete_file(file_id: str, owner: str) -> bool:
    """Delete a file"""
    ensure_directories()
    
    # Get metadata
    metadata = get_file_metadata(file_id)
    if not metadata:
        logger.error(f"File not found: {file_id}")
        return False
    
    # Check if user is the owner
    if metadata["owner"] != owner:
        logger.error(f"User {owner} is not the owner of file {file_id}")
        return False
    
    # Delete file
    file_path = os.path.join(FILES_DIR, file_id)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    # Delete metadata
    metadata_path = os.path.join(METADATA_DIR, f"{file_id}.json")
    if os.path.exists(metadata_path):
        try:
            os.remove(metadata_path)
        except Exception as e:
            logger.error(f"Error deleting metadata: {e}")
            return False
    
    logger.info(f"File deleted: {metadata['name']} ({file_id})")
    return True

def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

# Initialize
ensure_directories()

# Test the module
if __name__ == "__main__":
    # Create a test file
    test_file = "test_file.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test file for VoidLink file transfer module.")
    
    # Upload file
    file_id = upload_file(test_file, "test_file.txt", "admin")
    print(f"Uploaded file ID: {file_id}")
    
    # Get file list
    files = get_file_list("admin")
    print(f"Files for admin: {files}")
    
    # Share file
    share_file(file_id, "admin", "user")
    
    # Get file list for user
    files = get_file_list("user")
    print(f"Files for user: {files}")
    
    # Download file
    download_file(file_id, "downloaded_test_file.txt")
    
    # Delete file
    delete_file(file_id, "admin")
    
    # Clean up
    os.remove(test_file)
    os.remove("downloaded_test_file.txt")