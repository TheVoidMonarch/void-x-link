import socket
import json
import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Server connection details (change if needed)
HOST = "127.0.0.1"  # Change to your server IP if needed
PORT = 52384        # Make sure this matches your server's port

# Encryption key (must match server-side key)
SECRET_KEY = b"your-32-byte-secret-key-here"  # Change this to match server config


def encrypt_message(message):
    """Encrypts a message using AES encryption."""
    iv = os.urandom(16)  # Generate a random IV
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    encrypted_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted_bytes).decode()


def decrypt_message(encrypted_message):
    """Decrypts a message using AES encryption."""
    encrypted_data = base64.b64decode(encrypted_message)
    iv, encrypted_bytes = encrypted_data[:16], encrypted_data[16:]
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted_bytes), AES.block_size).decode()


def main():
    try:
        # Connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print("[✅] Connected to server!")

        while True:
            # Get user input
            message = input("Enter message to send (or type 'exit' to quit): ")
            if message.lower() == "exit":
                break

            # Encrypt message
            encrypted_message = encrypt_message(message)

            # Send encrypted message
            client_socket.send(encrypted_message.encode())

            # Receive encrypted response from server
            encrypted_response = client_socket.recv(4096).decode()
            decrypted_response = decrypt_message(encrypted_response)

            print(f"[🔒] Server Response: {decrypted_response}")

        client_socket.close()
    except Exception as e:
        print(f"[❌] Error: {e}")


if __name__ == "__main__":
    main()
