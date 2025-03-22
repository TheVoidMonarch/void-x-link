#!/usr/bin/env python3
"""
Mock implementation of the magic module for testing
"""

import os

class Magic:
    def __init__(self, mime=False):
        self.mime = mime
    
    def from_file(self, file_path):
        # Determine MIME type based on extension
        ext = os.path.splitext(file_path.lower())[1]
        mime_map = {
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
            '.7z': 'application/x-7z-compressed',
            '.exe': 'application/x-msdownload',
            '.sh': 'application/x-sh',
            '.py': 'text/x-python',
            '.js': 'application/javascript',
        }
        return mime_map.get(ext, 'application/octet-stream')