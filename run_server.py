#!/usr/bin/env python3
"""
Run VoidLink Server

A simple script to run the VoidLink server.
"""

import os
import sys
import argparse
from server import VoidLinkServer

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="VoidLink Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to listen on (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs("database/files", exist_ok=True)
    os.makedirs("database/metadata", exist_ok=True)
    
    # Create server
    server = VoidLinkServer(args.host, args.port)
    
    # Start server
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
    finally:
        server.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())#!/usr/bin/env python3
"""
VoidLink Server Runner - Simple script to start the server
"""

import os
import sys
from server import start_server

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════╗
║               VoidLink Server             ║
║  Secure Terminal-Based Chat & File Share  ║
╚═══════════════════════════════════════════╝
    """)

    # Check if database directory exists
    if not os.path.exists("database"):
        os.makedirs("database")
        print("Created database directory")

    # Check if database/files directory exists
    if not os.path.exists("database/files"):
        os.makedirs("database/files")
        print("Created files directory")

    # Check if database/chat_history directory exists
    if not os.path.exists("database/chat_history"):
        os.makedirs("database/chat_history")
        print("Created chat history directory")

    # Start the server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {str(e)}")
        sys.exit(1)
