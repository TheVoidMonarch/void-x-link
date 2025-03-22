#!/usr/bin/env python3
"""
Run VoidLink Client

A simple script to run the VoidLink client.
"""

import sys
import os

if __name__ == "__main__":
    # Add the current directory to the path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Import and run the client directly
    from client import VoidLinkClient, interactive_mode
    
    # Create and run the client
    client = VoidLinkClient()
    
    # Connect to server
    if not client.connect():
        print("Failed to connect to server. Exiting.")
        sys.exit(1)
    
    try:
        # Run in interactive mode
        interactive_mode(client)
    finally:
        # Disconnect from server
        client.disconnect()