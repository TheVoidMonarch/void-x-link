#!/usr/bin/env python3
"""
VoidLink File Security Module - Provides security measures for file transfers
"""

import os
import hashlib
import magic  # Requires python-magic package
import re
import time
from typing import Dict, List, Tuple, Optional
from error_handling import logger, log_info, log_warning, log_error, FileSecurityError
from virus_scanner import scan_file_for_viruses, is_clamd_available

# Constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB max file size
QUARANTINE_DIR = "database/quarantine/"

# Dangerous file extensions that are commonly used for malware
DANGEROUS_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.msi', '.vbs', '.js', '.jar', '.ps1', '.scr', 
    '.dll', '.com', '.pif', '.application', '.gadget', '.msc', '.hta', '.cpl',
    '.msp', '.inf', '.reg', '.sh', '.py', '.pl', '.php'
]

# Allowed MIME types (whitelist approach)
ALLOWED_MIME_TYPES = [
    # Documents
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/rtf',
    'application/x-rtf',
    'text/plain',
    'text/csv',
    'text/markdown',
    
    # Images
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/bmp',
    'image/tiff',
    'image/webp',
    'image/svg+xml',
    
    # Audio
    'audio/mpeg',
    'audio/wav',
    'audio/ogg',
    'audio/flac',
    'audio/aac',
    
    # Video
    'video/mp4',
    'video/mpeg',
    'video/quicktime',
    'video/x-msvideo',
    'video/webm',
    
    # Archives (potentially risky but commonly used)
    'application/zip',
    'application/x-rar-compressed',
    'application/x-tar',
    'application/gzip',
    'application/x-7z-compressed'
]

def ensure_security_dirs():
    """Ensure security directories exist"""
    if not os.path.exists(QUARANTINE_DIR):
        os.makedirs(QUARANTINE_DIR)

def is_file_too_large(file_size: int) -> bool:
    """Check if file size exceeds the maximum allowed size"""
    return file_size > MAX_FILE_SIZE

def has_dangerous_extension(filename: str) -> bool:
    """Check if file has a dangerous extension"""
    _, ext = os.path.splitext(filename.lower())
    return ext in DANGEROUS_EXTENSIONS

def is_mime_type_allowed(file_path: str) -> Tuple[bool, str]:
    """Check if file's MIME type is in the allowed list"""
    try:
        mime = magic.Magic(mime=True)
        file_mime = mime.from_file(file_path)
        return file_mime in ALLOWED_MIME_TYPES, file_mime
    except Exception as e:
        print(f"Error checking MIME type: {str(e)}")
        return False, "unknown/error"

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def scan_file(file_path: str, filename: str, file_size: int) -> Dict:
    """Scan a file for potential security issues

    Returns a dictionary with scan results
    """
    ensure_security_dirs()

    scan_start_time = time.time()
    log_info(f"Starting security scan for file: {filename}")

    results = {
        "filename": filename,
        "size": file_size,
        "size_check": "PASSED" if not is_file_too_large(file_size) else "FAILED",
        "extension_check": "PASSED" if not has_dangerous_extension(filename) else "FAILED",
        "hash": calculate_file_hash(file_path),
        "scan_time": time.time(),
        "is_safe": True,
        "quarantined": False,
        "reason": None,
        "virus_scan": "SKIPPED"  # Default if ClamAV is not available
    }

    # Check MIME type
    mime_allowed, mime_type = is_mime_type_allowed(file_path)
    results["mime_type"] = mime_type
    results["mime_check"] = "PASSED" if mime_allowed else "FAILED"

    # Determine if file is safe based on basic checks
    if results["size_check"] == "FAILED":
        results["is_safe"] = False
        results["reason"] = f"File exceeds maximum size limit of {MAX_FILE_SIZE/1024/1024} MB"

    elif results["extension_check"] == "FAILED":
        results["is_safe"] = False
        results["reason"] = f"File has a potentially dangerous extension"

    elif results["mime_check"] == "FAILED":
        results["is_safe"] = False
        results["reason"] = f"File type {mime_type} is not allowed"

    # If file passed basic checks, scan for viruses
    if results["is_safe"]:
        # Scan for viruses if ClamAV is available
        is_clean, virus_name = scan_file_for_viruses(file_path)

        if is_clamd_available():
            results["virus_scan"] = "PASSED" if is_clean else "FAILED"

            if not is_clean:
                results["is_safe"] = False
                results["reason"] = f"Virus detected: {virus_name}"
                results["virus_name"] = virus_name
                log_warning(f"Virus detected in file {filename}: {virus_name}")
        else:
            log_warning(f"Virus scanning skipped for {filename} - ClamAV not available")

    # Quarantine file if not safe
    if not results["is_safe"]:
        quarantine_path = os.path.join(QUARANTINE_DIR, filename)
        try:
            os.rename(file_path, quarantine_path)
            results["quarantined"] = True
            results["quarantine_path"] = quarantine_path
            log_warning(f"File quarantined: {filename} -> {quarantine_path}")
        except Exception as e:
            log_error(f"Error quarantining file: {str(e)}")

    scan_duration = time.time() - scan_start_time
    results["scan_duration"] = scan_duration

    log_info(f"Security scan completed for {filename} in {scan_duration:.2f}s: " +
             ("PASSED" if results["is_safe"] else f"FAILED - {results['reason']}"))

    return results

# Initialize security directories
ensure_security_dirs()