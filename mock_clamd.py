#!/usr/bin/env python3
"""
Mock implementation of the clamd module for testing
"""

class ClamdUnixSocket:
    def __init__(self, path=None):
        self.path = path
    
    def scan(self, file_path):
        return {file_path: ('OK', None)}
    
    def version(self):
        return "MockClamAV 0.0.0"

class ClamdNetworkSocket:
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port
    
    def scan(self, file_path):
        return {file_path: ('OK', None)}
    
    def version(self):
        return "MockClamAV 0.0.0"

# Define ConnectionError for compatibility
class ConnectionError(Exception):
    pass