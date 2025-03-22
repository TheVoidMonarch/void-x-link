#!/usr/bin/env python3
"""
Run VoidLink Server

A simple script to run the VoidLink server.
"""

import sys
import os

if __name__ == "__main__":
    # Add the current directory to the path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Import and run the server
    from server import main
    
    # Run the server
    sys.exit(main())