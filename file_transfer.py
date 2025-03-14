#!/usr/bin/env python3
"""
VoidLink File Transfer Module - Handles secure file transfers
"""

import os
import json
import time
import hashlib
import base64
from typing import Dict, List, Optional, Tuple
from encryption import encrypt_message, decrypt_message

# Constants
FILE_STORAGE_DIR = "database/files/"
FILE_METADATA_FILE = "database/file_metadata.json"
CHUNK_SIZE = 4096  # 4KB chunks for file transfer

def ensure_file_dirs():
    """Ensure file storage directories exist"""
    if not os.path.exists(FILE_STORAGE_DIR):
        os.makedirs(FILE_STORAGE_DIR)
    
    if not os.path.exists(os.path.dirname(FILE_METADATA_FILE)):
        os.makedirs(os.path.dirname(FILE_METADATA_FILE))
    
    # Initialize metadata file if it doesn't exist
    if not os.path.exists(FILE_METADATA_FILE):
        with open(FILE_METADATA_FILE, "w") as file:
            json.dump([], file)

def handle_file_transfer(client_socket, filename: str, sender: str = "unknown") -> Dict:
    """Handle receiving a file from a client"""
    ensure_file_dirs()
    
    # Generate a safe filename to prevent path traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(FILE_STORAGE_DIR, safe_filename)
    
    # If file exists, add timestamp to make it unique
    if os.path.exists(file_path):
        name, ext = os.path.splitext(safe_filename)
        safe_filename = f"{name}_{int(time.time())}{ext}"
        file_path = os.path.join(FILE_STORAGE_DIR, safe_filename)
    
    file_size = 0
    file_hash = hashlib.sha256()
    
    try:
        with open(file_path, "wb") as file:
            # Receive file data in chunks
            while True:
                # Receive chunk size first
                chunk_size_data = client_socket.recv(8)
                if not chunk_size_data or chunk_size_data == b'ENDFILE':
                    break
                
                chunk_size = int.from_bytes(chunk_size_data, byteorder='big')
                
                # Receive encrypted chunk
                encrypted_chunk = client_socket.recv(chunk_size)
                if not encrypted_chunk:
                    break
                
                # Decrypt chunk
                try:
                    decrypted_chunk = decrypt_message(encrypted_chunk)
                    if isinstance(decrypted_chunk, str):
                        chunk_data = decrypted_chunk.encode('utf-8')
                    else:
                        chunk_data = decrypted_chunk
                    
                    # Write to file
                    file.write(chunk_data)
                    
                    # Update hash and size
                    file_hash.update(chunk_data)
                    file_size += len(chunk_data)
                except Exception as e:
                    print(f"Error decrypting file chunk: {str(e)}")
                    break
        
        # Create file metadata
        file_metadata = {
            "filename": safe_filename,
            "original_filename": filename,
            "path": file_path,
            "size": file_size,
            "hash": file_hash.hexdigest(),
            "uploaded_by": sender,
            "timestamp": time.time()
        }
        
        # Save metadata
        save_file_metadata(file_metadata)
        
        print(f"File {safe_filename} received and saved. Size: {file_size} bytes")
        return file_metadata
    
    except Exception as e:
        print(f"Error receiving file {filename}: {str(e)}")
        # Clean up partial file
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"error": str(e)}

def send_file(client_socket, filename: str) -> bool:
    """Send a file to a client"""
    ensure_file_dirs()
    
    file_path = os.path.join(FILE_STORAGE_DIR, filename)
    
    if not os.path.exists(file_path):
        print(f"File {filename} not found")
        return False
    
    try:
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                # Encrypt chunk
                encrypted_chunk = encrypt_message(chunk)
                
                # Send chunk size first
                chunk_size = len(encrypted_chunk)
                client_socket.send(chunk_size.to_bytes(8, byteorder='big'))
                
                # Send encrypted chunk
                client_socket.send(encrypted_chunk)
        
        # Send end of file marker
        client_socket.send(b'ENDFILE')
        
        print(f"File {filename} sent successfully")
        return True
    
    except Exception as e:
        print(f"Error sending file {filename}: {str(e)}")
        return False

def save_file_metadata(metadata: Dict) -> None:
    """Save file metadata to the metadata file"""
    ensure_file_dirs()
    
    try:
        # Load existing metadata
        file_list = []
        if os.path.exists(FILE_METADATA_FILE):
            with open(FILE_METADATA_FILE, "r") as file:
                try:
                    file_list = json.load(file)
                except json.JSONDecodeError:
                    file_list = []
        
        # Add new metadata
        file_list.append(metadata)
        
        # Save updated metadata
        with open(FILE_METADATA_FILE, "w") as file:
            json.dump(file_list, file, indent=2)
    
    except Exception as e:
        print(f"Error saving file metadata: {str(e)}")

def get_file_list() -> List[Dict]:
    """Get list of available files with metadata"""
    ensure_file_dirs()
    
    try:
        if os.path.exists(FILE_METADATA_FILE):
            with open(FILE_METADATA_FILE, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []
    
    except Exception as e:
        print(f"Error getting file list: {str(e)}")
        return []

def get_file_metadata(filename: str) -> Optional[Dict]:
    """Get metadata for a specific file"""
    file_list = get_file_list()
    
    for file_info in file_list:
        if file_info.get("filename") == filename:
            return file_info
    
    return None

def delete_file(filename: str) -> bool:
    """Delete a file and its metadata"""
    ensure_file_dirs()
    
    file_path = os.path.join(FILE_STORAGE_DIR, filename)
    
    try:
        # Delete the file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Update metadata
        file_list = get_file_list()
        updated_list = [f for f in file_list if f.get("filename") != filename]
        
        with open(FILE_METADATA_FILE, "w") as file:
            json.dump(updated_list, file, indent=2)
        
        return True
    
    except Exception as e:
        print(f"Error deleting file {filename}: {str(e)}")
        return False

# Initialize file storage
ensure_file_dirs()