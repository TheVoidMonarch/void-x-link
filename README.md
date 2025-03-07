# void-x-link

# Server

## Overview
VoidLink is a **lightweight, encrypted chat and file transfer framework** designed for private circles and institutional/organizational intranet deployments. The server-side implementation is modular, allowing for easy customization and extension. The server manages authentication, message encryption, file transfers, and optional cloud storage integration.

## Features
- **End-to-End Encryption (E2EE)**: Ensures all communication is secured.
- **Terminal-Based Chat**: Lightweight, no GUI required for clients.
- **File Transfer with Encryption**: Securely send files over the network.
- **Persistent Chat History**: Chat logs are stored both on the server and client-side for seamless multi-device access.
- **Modular Design**: Customizable server modules for authentication, storage, and more.
- **Optional API Authentication**: Can integrate with external account databases.
- **Cloud Storage Integration**: Server admin can choose to store chat logs locally or in a free cloud storage service.
- **Basic Web UI (Optional)**: For server-side settings and maintenance only.

## Installation
### Prerequisites
- Python 3.x
- `pip` (Python package manager)
- OpenSSL (for encryption)
- A Linux or Windows server

### Setup
```sh
# Clone the repository
git clone https://github.com/TheVoidMonarch/VoidLink-Server.git
cd VoidLink-Server

# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

## Configuration
Modify `config.json` to customize:
- **Server Port**
- **Encryption Settings**
- **Storage Options**
- **API Authentication (Enable/Disable)**

## Running the Server
```sh
python server.py
```
By default, the server listens on port `5000`. Change this in `config.json` if needed.

## Authentication Options
- **Local Authentication**: Users create accounts directly on the server.
- **API Authentication** (Optional): The server can fetch user credentials from an external database.

## Chat Persistence
- **Stored on Server & Client**: Users can access previous messages when switching devices.
- **Encryption in Storage**: Messages are stored securely.
- **Cloud Storage Support**: Admins can configure external storage via API.

## Security Measures
- **AES-256 Encrypted Messages**
- **TLS for Server Communication**
- **Public/Private Key Authentication (Optional)**

## Web UI (Optional)
- **For Server Admins Only**
- **Built with Flask (or CGI-based alternative in C)**
- **Manages User Accounts, Logs, and Configuration**

## Future Features
- **Chatbot Support**
- **Better Multi-User Load Management**
- **Improved File Transfer Performance**

## License
[MIT License](LICENSE)

---
For client setup, refer to the [VoidLink Client Repository](https://github.com/TheVoidMonarch/void-x-link-client).

