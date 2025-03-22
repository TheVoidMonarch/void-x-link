#!/usr/bin/env python3
"""
Simple VoidLink Client

A simplified client for testing authentication with a VoidLink server.
"""

import os
import sys
import json
import socket
import logging
from getpass import getpass

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('simple_client')

# Constants
HOST = 'localhost'
PORT = 8000
BUFFER_SIZE = 4096
TIMEOUT = 10  # seconds

def main():
    """Main function"""
    print("\nSimple VoidLink Client")
    print("=====================")
    
    # Create socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(TIMEOUT)
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")
    except socket.error as e:
        print(f"Failed to connect to server: {e}")
        return 1
    
    try:
        # Get username and password
        username = input("Username: ")
        password = getpass("Password: ")
        
        # Prepare login message
        login_message = {
            "command": "login",
            "data": {
                "username": username,
                "password": password
            }
        }
        
        # Convert to JSON
        json_message = json.dumps(login_message)
        
        # Send message
        client_socket.sendall(json_message.encode('utf-8'))
        
        # Receive response
        response = client_socket.recv(BUFFER_SIZE)
        if not response:
            print("No response from server")
            return 1
        
        # Print raw response for debugging
        print(f"Raw response: {response}")
        
        # Try to parse response
        try:
            response_text = response.decode('utf-8')
            print(f"Decoded response: {response_text}")
            
            # Try to parse as JSON
            try:
                response_json = json.loads(response_text)
                print(f"Parsed JSON: {response_json}")
                
                # Check if login was successful
                if isinstance(response_json, dict) and response_json.get("status") == "success":
                    print(f"Login successful! Welcome, {username}!")
                else:
                    error = response_json.get("error", "Unknown error") if isinstance(response_json, dict) else "Invalid response format"
                    print(f"Login failed: {error}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse response as JSON: {e}")
                print("This suggests the server is not sending valid JSON.")
        except Exception as e:
            print(f"Error processing response: {e}")
    
    finally:
        # Close socket
        client_socket.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())