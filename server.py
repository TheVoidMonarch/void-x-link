import socket
import threading
import json
from encryption import encrypt_message, decrypt_message
from authentication import authenticate_user
from storage import save_message
from file_transfer import handle_file_transfer

# Load configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file)

HOST = config["server_host"]
PORT = config["server_port"]
clients = {}

def handle_client(client_socket, addr):
    try:
        username = None  # Declare it at the beginning
        encrypted_data = client_socket.recv(4096)
        decrypted_data = decrypt_message(encrypted_data)  # Ensure decryption works
        username = decrypted_data.get("username", None)

        if username:
            clients[username] = client_socket
        else:
            raise ValueError("Username not received from client")

        # Handle chat messages...

    except Exception as e:
        print(f"Error with {addr}: {str(e)}")
    
    finally:
        if username in clients:  # Avoid KeyError
            del clients[username]
        client_socket.close()

def broadcast(message, sender):
    encrypted_message = encrypt_message(message)
    for user, client in clients.items():
        if user != sender:
            client.send(encrypted_message)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, 0))
    PORT = server.getsockname()[1] 
    server.listen(5)
    print(f"VoidLink Server running on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"New connection: {addr}")
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    start_server()
