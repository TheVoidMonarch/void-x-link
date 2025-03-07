import os
from encryption import encrypt_message, decrypt_message

FILE_STORAGE_DIR = "database/files/"

if not os.path.exists(FILE_STORAGE_DIR):
    os.makedirs(FILE_STORAGE_DIR)

def handle_file_transfer(client_socket, filename):
    file_path = os.path.join(FILE_STORAGE_DIR, filename)

    with open(file_path, "wb") as file:
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            file.write(decrypt_message(chunk))
    print(f"File {filename} received and saved.")
