#!/usr/bin/env python3
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
