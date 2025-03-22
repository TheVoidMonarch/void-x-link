#!/usr/bin/env python3
"""
Basic VoidLink Client

A very basic client for testing authentication with a VoidLink server.
"""

import socket
import json
import sys

# Constants
HOST = 'localhost'
PORT = 8000
BUFFER_SIZE = 4096

def main():
    """Main function"""
    print("\nBasic VoidLink Client")
    print("====================")
    
    # Create socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to server
        print(f"Connecting to {HOST}:{PORT}...")
        client_socket.connect((HOST, PORT))
        print("Connected!")
        
        # Get username and password
        username = input("Username: ")
        password = input("Password: ")
        
        # Create login message
        login_message = {
            "command": "login",
            "data": {
                "username": username,
                "password": password
            }
        }
        
        # Send login message
        print("Sending login request...")
        client_socket.sendall(json.dumps(login_message).encode('utf-8'))
        
        # Receive response
        print("Waiting for response...")
        response = client_socket.recv(BUFFER_SIZE)
        
        # Print raw response
        print(f"Raw response: {response}")
        
        # Try to decode response
        response_text = response.decode('utf-8')
        print(f"Decoded response: {response_text}")
        
        # Try to parse as JSON
        try:
            response_json = json.loads(response_text)
            print(f"Parsed JSON: {response_json}")
            
            # Check login status
            if isinstance(response_json, dict):
                if response_json.get("status") == "success":
                    print("Login successful!")
                else:
                    print(f"Login failed: {response_json.get('error', 'Unknown error')}")
            else:
                print(f"Unexpected response type: {type(response_json)}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse response as JSON: {e}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Close socket
        client_socket.close()
        print("Connection closed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())