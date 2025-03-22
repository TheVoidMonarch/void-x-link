#!/usr/bin/env python3
"""
Fixed VoidLink Client

A client for testing authentication with a VoidLink server that uses the fixed encryption module.
"""

import socket
import json
import sys
import os
import traceback

# Import the fixed encryption module
import fixed_encryption as encryption

# Constants
HOST = 'localhost'
PORT = 8000
BUFFER_SIZE = 4096

def main():
    """Main function"""
    print("\nFixed VoidLink Client")
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
        
        # Convert to JSON
        json_message = json.dumps(login_message)
        
        # Send message (unencrypted for simplicity)
        print("Sending login request...")
        client_socket.sendall(json_message.encode('utf-8'))
        
        # Receive response
        print("Waiting for response...")
        response = client_socket.recv(BUFFER_SIZE)
        
        # Print raw response
        print(f"Raw response: {response}")
        
        # Try to decode response
        response_text = response.decode('utf-8')
        print(f"Decoded response: {response_text}")
        
        # Try to parse directly as JSON first
        try:
            response_json = json.loads(response_text)
            print(f"Parsed JSON: {response_json}")
            
            # Check login status
            if response_json.get("status") == "success":
                print("Login successful!")
            else:
                print(f"Login failed: {response_json.get('error', 'Unknown error')}")
            
            return 0
        except json.JSONDecodeError:
            print("Response is not valid JSON, trying to decrypt...")
        
        # Try to decrypt response
        try:
            decrypted_response = encryption.decrypt_message(response_text)
            print(f"Decrypted response: {decrypted_response}")
            
            # Check if decrypted response is a dictionary
            if isinstance(decrypted_response, dict):
                # Check login status
                if decrypted_response.get("status") == "success":
                    print("Login successful!")
                else:
                    print(f"Login failed: {decrypted_response.get('error', 'Unknown error')}")
            
            # If decrypted response is a string, try to parse as JSON
            elif isinstance(decrypted_response, str):
                try:
                    response_json = json.loads(decrypted_response)
                    print(f"Parsed JSON from decrypted string: {response_json}")
                    
                    # Check login status
                    if response_json.get("status") == "success":
                        print("Login successful!")
                    else:
                        print(f"Login failed: {response_json.get('error', 'Unknown error')}")
                except json.JSONDecodeError:
                    print(f"Decrypted response is not valid JSON: {decrypted_response}")
            
            else:
                print(f"Unexpected decrypted response type: {type(decrypted_response)}")
        
        except Exception as e:
            print(f"Error processing response: {e}")
            print(traceback.format_exc())
    
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
    
    finally:
        # Close socket
        client_socket.close()
        print("Connection closed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())