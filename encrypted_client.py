#!/usr/bin/env python3
"""
Encrypted VoidLink Client

A client for testing authentication with a VoidLink server that handles encryption.
"""

import socket
import json
import sys
import os

# Try to import encryption module
try:
    import simple_encryption as encryption
    ENCRYPTION_AVAILABLE = True
    print("Encryption module loaded successfully")
except ImportError:
    ENCRYPTION_AVAILABLE = False
    print("Encryption module not available, data will be sent unencrypted")

# Constants
HOST = 'localhost'
PORT = 8000
BUFFER_SIZE = 4096

def main():
    """Main function"""
    print("\nEncrypted VoidLink Client")
    print("========================")
    
    if not ENCRYPTION_AVAILABLE:
        print("Error: Encryption module is required but not available.")
        return 1
    
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
        
        # Encrypt message
        try:
            encrypted_message = encryption.encrypt_message(json_message)
            print(f"Encrypted message: {encrypted_message}")
            
            # Send encrypted message
            print("Sending encrypted login request...")
            client_socket.sendall(encrypted_message.encode('utf-8'))
        except Exception as e:
            print(f"Encryption error: {e}")
            print("Sending unencrypted message...")
            client_socket.sendall(json_message.encode('utf-8'))
        
        # Receive response
        print("Waiting for response...")
        response = client_socket.recv(BUFFER_SIZE)
        
        # Print raw response
        print(f"Raw response: {response}")
        
        # Try to decode response
        response_text = response.decode('utf-8')
        print(f"Decoded response: {response_text}")
        
        # Try to decrypt response
        try:
            print("Attempting to decrypt response...")
            decrypted_response = encryption.decrypt_message(response_text)
            print(f"Decrypted response: {decrypted_response}")
            
            # Check if decrypted response is a dictionary
            if isinstance(decrypted_response, dict):
                print(f"Response is a dictionary: {decrypted_response}")
                
                # Check login status
                if decrypted_response.get("status") == "success":
                    print("Login successful!")
                else:
                    print(f"Login failed: {decrypted_response.get('error', 'Unknown error')}")
            
            # If decrypted response is a string, try to parse as JSON
            elif isinstance(decrypted_response, str):
                print("Response is a string, trying to parse as JSON...")
                try:
                    response_json = json.loads(decrypted_response)
                    print(f"Parsed JSON: {response_json}")
                    
                    # Check login status
                    if response_json.get("status") == "success":
                        print("Login successful!")
                    else:
                        print(f"Login failed: {response_json.get('error', 'Unknown error')}")
                except json.JSONDecodeError as e:
                    print(f"Failed to parse decrypted response as JSON: {e}")
            
            else:
                print(f"Unexpected decrypted response type: {type(decrypted_response)}")
        
        except Exception as e:
            print(f"Decryption error: {e}")
            
            # Try to parse as JSON directly (in case it's not encrypted)
            try:
                response_json = json.loads(response_text)
                print(f"Parsed JSON: {response_json}")
                
                # Check login status
                if response_json.get("status") == "success":
                    print("Login successful!")
                else:
                    print(f"Login failed: {response_json.get('error', 'Unknown error')}")
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