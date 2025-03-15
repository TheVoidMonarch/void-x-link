#!/usr/bin/env python3
"""
VoidLink Resumable File Transfer Module - Handles resumable file transfers
"""

import os
import json
import time
import hashlib
import base64
import threading
import tempfile
from typing import Dict, List, Optional, Tuple, BinaryIO, Any
from encryption import encrypt_message, decrypt_message
from file_security import scan_file, is_file_too_large
from error_handling import logger, log_info, log_warning, log_error, log_exception, FileTransferError

# Constants
FILE_STORAGE_DIR = "database/files/"
FILE_METADATA_FILE = "database/file_metadata.json"
TEMP_DIR = "database/temp/"
CHUNK_SIZE = 4096  # 4KB chunks for file transfer
MAX_RETRIES = 3    # Maximum number of retries for failed chunks

# Global transfer state
active_transfers = {}  # Dictionary to track active transfers
transfer_locks = {}    # Locks for each transfer

class TransferState:
    """Class to track the state of a file transfer"""
    def __init__(self, filename: str, total_size: int, sender: str = "unknown"):
        self.filename = filename
        self.total_size = total_size
        self.sender = sender
        self.received_size = 0
        self.chunks_received = 0
        self.start_time = time.time()
        self.last_update_time = time.time()
        self.temp_file: Optional[BinaryIO] = None
        self.temp_path: Optional[str] = None
        self.complete = False
        self.failed = False
        self.error = None
        self.file_hash = hashlib.sha256()
        self.chunk_hashes = {}  # Dictionary of chunk index -> hash
        self.retries = {}  # Dictionary of chunk index -> retry count
    
    def open_temp_file(self):
        """Open a temporary file for writing"""
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        
        self.temp_path = os.path.join(TEMP_DIR, f"{self.filename}.part")
        self.temp_file = open(self.temp_path, "wb")
    
    def close_temp_file(self):
        """Close the temporary file"""
        if self.temp_file:
            self.temp_file.close()
            self.temp_file = None
    
    def write_chunk(self, chunk_index: int, chunk_data: bytes, chunk_hash: str) -> bool:
        """Write a chunk to the temporary file"""
        if not self.temp_file:
            self.open_temp_file()
        
        try:
            # Verify chunk hash
            calculated_hash = hashlib.sha256(chunk_data).hexdigest()
            if calculated_hash != chunk_hash:
                log_warning(f"Chunk hash mismatch for {self.filename} chunk {chunk_index}")
                self.retries[chunk_index] = self.retries.get(chunk_index, 0) + 1
                return False
            
            # Seek to the correct position
            position = chunk_index * CHUNK_SIZE
            self.temp_file.seek(position)
            
            # Write the chunk
            self.temp_file.write(chunk_data)
            self.temp_file.flush()
            
            # Update state
            self.chunks_received += 1
            self.received_size += len(chunk_data)
            self.last_update_time = time.time()
            self.chunk_hashes[chunk_index] = chunk_hash
            self.file_hash.update(chunk_data)
            
            return True
        except Exception as e:
            log_error(f"Error writing chunk {chunk_index} for {self.filename}: {str(e)}")
            self.retries[chunk_index] = self.retries.get(chunk_index, 0) + 1
            return False
    
    def finalize(self) -> Optional[str]:
        """Finalize the transfer and move the file to its final location"""
        self.close_temp_file()
        
        if not self.temp_path or not os.path.exists(self.temp_path):
            return None
        
        # Generate a safe filename to prevent path traversal
        safe_filename = os.path.basename(self.filename)
        file_path = os.path.join(FILE_STORAGE_DIR, safe_filename)
        
        # If file exists, add timestamp to make it unique
        if os.path.exists(file_path):
            name, ext = os.path.splitext(safe_filename)
            safe_filename = f"{name}_{int(time.time())}{ext}"
            file_path = os.path.join(FILE_STORAGE_DIR, safe_filename)
        
        # Move the file to its final location
        os.rename(self.temp_path, file_path)
        
        return file_path
    
    def get_progress(self) -> Dict[str, Any]:
        """Get the current progress of the transfer"""
        elapsed = time.time() - self.start_time
        speed = self.received_size / elapsed if elapsed > 0 else 0
        percent = (self.received_size / self.total_size * 100) if self.total_size > 0 else 0
        
        return {
            "filename": self.filename,
            "total_size": self.total_size,
            "received_size": self.received_size,
            "percent": percent,
            "elapsed": elapsed,
            "speed": speed,
            "chunks_received": self.chunks_received,
            "complete": self.complete,
            "failed": self.failed,
            "error": self.error
        }

def ensure_dirs():
    """Ensure all necessary directories exist"""
    for directory in [FILE_STORAGE_DIR, TEMP_DIR, os.path.dirname(FILE_METADATA_FILE)]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # Initialize metadata file if it doesn't exist
    if not os.path.exists(FILE_METADATA_FILE):
        with open(FILE_METADATA_FILE, "w") as file:
            json.dump([], file)

def start_resumable_upload(client_socket, filename: str, total_size: int, sender: str = "unknown") -> Dict:
    """Start a resumable file upload"""
    ensure_dirs()
    
    # Generate a unique transfer ID
    transfer_id = f"{sender}_{filename}_{int(time.time())}"
    
    # Create transfer state
    transfer_state = TransferState(filename, total_size, sender)
    transfer_state.open_temp_file()
    
    # Store in active transfers
    active_transfers[transfer_id] = transfer_state
    transfer_locks[transfer_id] = threading.Lock()
    
    # Send ready message
    ready_message = {
        "type": "upload_ready",
        "transfer_id": transfer_id,
        "chunk_size": CHUNK_SIZE
    }
    
    # Convert to JSON and encrypt
    encrypted_message = encrypt_message(json.dumps(ready_message))
    client_socket.send(encrypted_message)
    
    log_info(f"Started resumable upload for {filename} ({total_size} bytes) from {sender}")
    
    return {
        "transfer_id": transfer_id,
        "filename": filename,
        "total_size": total_size,
        "sender": sender,
        "start_time": time.time()
    }

def handle_chunk(client_socket, transfer_id: str, chunk_index: int, chunk_data: bytes, chunk_hash: str) -> Dict:
    """Handle a chunk of a resumable file upload"""
    if transfer_id not in active_transfers:
        raise FileTransferError(f"Invalid transfer ID: {transfer_id}")
    
    transfer_state = active_transfers[transfer_id]
    
    with transfer_locks[transfer_id]:
        # Write the chunk
        success = transfer_state.write_chunk(chunk_index, chunk_data, chunk_hash)
        
        # Check if we've exceeded retry limit
        if not success and transfer_state.retries.get(chunk_index, 0) >= MAX_RETRIES:
            transfer_state.failed = True
            transfer_state.error = f"Failed to write chunk {chunk_index} after {MAX_RETRIES} retries"
            log_error(transfer_state.error)
            
            # Clean up
            transfer_state.close_temp_file()
            if transfer_state.temp_path and os.path.exists(transfer_state.temp_path):
                os.remove(transfer_state.temp_path)
            
            # Send failure message
            failure_message = {
                "type": "chunk_failed",
                "transfer_id": transfer_id,
                "chunk_index": chunk_index,
                "error": transfer_state.error
            }
            encrypted_message = encrypt_message(json.dumps(failure_message))
            client_socket.send(encrypted_message)
            
            return {
                "success": False,
                "error": transfer_state.error
            }
        
        # Send acknowledgment
        ack_message = {
            "type": "chunk_ack",
            "transfer_id": transfer_id,
            "chunk_index": chunk_index,
            "received_size": transfer_state.received_size,
            "progress": transfer_state.get_progress()
        }
        encrypted_message = encrypt_message(json.dumps(ack_message))
        client_socket.send(encrypted_message)
        
        return {
            "success": success,
            "progress": transfer_state.get_progress()
        }

def complete_resumable_upload(client_socket, transfer_id: str) -> Dict:
    """Complete a resumable file upload"""
    if transfer_id not in active_transfers:
        raise FileTransferError(f"Invalid transfer ID: {transfer_id}")
    
    transfer_state = active_transfers[transfer_id]
    
    with transfer_locks[transfer_id]:
        try:
            # Finalize the transfer
            file_path = transfer_state.finalize()
            
            if not file_path:
                raise FileTransferError(f"Failed to finalize transfer: {transfer_id}")
            
            # Scan the file
            file_size = transfer_state.received_size
            scan_results = scan_file(file_path, transfer_state.filename, file_size)
            
            # Create file metadata
            file_metadata = {
                "filename": os.path.basename(file_path),
                "original_filename": transfer_state.filename,
                "path": file_path,
                "size": file_size,
                "hash": transfer_state.file_hash.hexdigest(),
                "uploaded_by": transfer_state.sender,
                "timestamp": time.time(),
                "security_scan": scan_results,
                "transfer_id": transfer_id
            }
            
            # Save metadata
            save_file_metadata(file_metadata)
            
            # Mark as complete
            transfer_state.complete = True
            
            # Send completion message
            completion_message = {
                "type": "upload_complete",
                "transfer_id": transfer_id,
                "filename": os.path.basename(file_path),
                "size": file_size,
                "hash": transfer_state.file_hash.hexdigest(),
                "is_safe": scan_results["is_safe"]
            }
            encrypted_message = encrypt_message(json.dumps(completion_message))
            client_socket.send(encrypted_message)
            
            # Log completion
            log_info(f"Completed resumable upload for {transfer_state.filename} ({file_size} bytes) from {transfer_state.sender}")
            
            # Clean up
            del active_transfers[transfer_id]
            del transfer_locks[transfer_id]
            
            return file_metadata
        
        except Exception as e:
            log_exception(e, f"completing transfer {transfer_id}")
            
            # Mark as failed
            transfer_state.failed = True
            transfer_state.error = str(e)
            
            # Send failure message
            failure_message = {
                "type": "upload_failed",
                "transfer_id": transfer_id,
                "error": str(e)
            }
            encrypted_message = encrypt_message(json.dumps(failure_message))
            client_socket.send(encrypted_message)
            
            # Clean up
            if transfer_id in active_transfers:
                del active_transfers[transfer_id]
            if transfer_id in transfer_locks:
                del transfer_locks[transfer_id]
            
            return {
                "error": str(e)
            }

def start_resumable_download(client_socket, filename: str, start_position: int = 0) -> Dict:
    """Start a resumable file download"""
    ensure_dirs()
    
    file_path = os.path.join(FILE_STORAGE_DIR, filename)
    
    if not os.path.exists(file_path):
        raise FileTransferError(f"File not found: {filename}")
    
    # Check if file is quarantined
    file_metadata = get_file_metadata(filename)
    if file_metadata and file_metadata.get("quarantined", False):
        raise FileTransferError(f"File is quarantined: {filename}")
    
    # Check if file has failed security scan
    if file_metadata and "security_scan" in file_metadata:
        scan_results = file_metadata["security_scan"]
        if not scan_results.get("is_safe", True):
            raise FileTransferError(f"File failed security scan: {scan_results.get('reason', 'Unknown reason')}")
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Generate a unique transfer ID
    transfer_id = f"download_{filename}_{int(time.time())}"
    
    # Send file metadata
    metadata_message = {
        "type": "download_ready",
        "transfer_id": transfer_id,
        "filename": filename,
        "total_size": file_size,
        "chunk_size": CHUNK_SIZE,
        "start_position": start_position
    }
    encrypted_message = encrypt_message(json.dumps(metadata_message))
    client_socket.send(encrypted_message)
    
    log_info(f"Started resumable download for {filename} ({file_size} bytes) from position {start_position}")
    
    return {
        "transfer_id": transfer_id,
        "filename": filename,
        "total_size": file_size,
        "start_position": start_position
    }

def send_file_chunk(client_socket, transfer_id: str, filename: str, chunk_index: int) -> Dict:
    """Send a chunk of a file"""
    file_path = os.path.join(FILE_STORAGE_DIR, filename)
    
    if not os.path.exists(file_path):
        raise FileTransferError(f"File not found: {filename}")
    
    try:
        with open(file_path, "rb") as file:
            # Calculate position
            position = chunk_index * CHUNK_SIZE
            
            # Seek to position
            file.seek(position)
            
            # Read chunk
            chunk_data = file.read(CHUNK_SIZE)
            
            if not chunk_data:
                # End of file
                return {
                    "success": True,
                    "eof": True
                }
            
            # Calculate chunk hash
            chunk_hash = hashlib.sha256(chunk_data).hexdigest()
            
            # Send chunk
            chunk_message = {
                "type": "file_chunk",
                "transfer_id": transfer_id,
                "chunk_index": chunk_index,
                "chunk_size": len(chunk_data),
                "chunk_hash": chunk_hash
            }
            encrypted_message = encrypt_message(json.dumps(chunk_message))
            client_socket.send(encrypted_message)
            
            # Send chunk data
            encrypted_chunk = encrypt_message(chunk_data)
            chunk_size = len(encrypted_chunk)
            client_socket.send(chunk_size.to_bytes(8, byteorder='big'))
            client_socket.send(encrypted_chunk)
            
            return {
                "success": True,
                "chunk_index": chunk_index,
                "chunk_size": len(chunk_data),
                "chunk_hash": chunk_hash
            }
    
    except Exception as e:
        log_error(f"Error sending chunk {chunk_index} of {filename}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def save_file_metadata(metadata: Dict) -> None:
    """Save file metadata to the metadata file"""
    ensure_dirs()
    
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
        log_error(f"Error saving file metadata: {str(e)}")

def get_file_metadata(filename: str) -> Optional[Dict]:
    """Get metadata for a specific file"""
    ensure_dirs()
    
    try:
        file_list = []
        if os.path.exists(FILE_METADATA_FILE):
            with open(FILE_METADATA_FILE, "r") as file:
                try:
                    file_list = json.load(file)
                except json.JSONDecodeError:
                    file_list = []
        
        for file_info in file_list:
            if file_info.get("filename") == filename:
                return file_info
        
        return None
    
    except Exception as e:
        log_error(f"Error getting file metadata: {str(e)}")
        return None

def get_active_transfers() -> Dict[str, Dict]:
    """Get information about active transfers"""
    result = {}
    
    for transfer_id, transfer_state in active_transfers.items():
        result[transfer_id] = transfer_state.get_progress()
    
    return result

def cancel_transfer(transfer_id: str) -> bool:
    """Cancel an active transfer"""
    if transfer_id not in active_transfers:
        return False
    
    with transfer_locks[transfer_id]:
        transfer_state = active_transfers[transfer_id]
        
        # Close and remove temp file
        transfer_state.close_temp_file()
        if transfer_state.temp_path and os.path.exists(transfer_state.temp_path):
            os.remove(transfer_state.temp_path)
        
        # Mark as failed
        transfer_state.failed = True
        transfer_state.error = "Transfer cancelled"
        
        # Clean up
        del active_transfers[transfer_id]
        del transfer_locks[transfer_id]
        
        log_info(f"Transfer cancelled: {transfer_id}")
        
        return True

# Initialize directories
ensure_dirs()