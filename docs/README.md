# VoidLink: Secure Terminal-Based Chat and File Transfer Framework

VoidLink is a lightweight, secure, and modular chat and file transfer framework designed to run entirely in the terminal. It is built to function in private circles as well as for institutional or organizational intranet deployments. With a focus on simplicity, security, and extensibility, VoidLink provides a self-hosted alternative to commercial chat solutions.

## Core Features

- **Lightweight & Terminal-Based**: Minimal dependencies and full CLI support.
- **Privacy & Security**: End-to-end encrypted chat and file transfers using AES-256.
- **Modular & Customizable**: Easily extendable server-side functionality.
- **Self-Hosted & Decentralized**: No reliance on third-party servers.
- **Seamless Deployment**: Works on LAN, VPN (Tailscale/ZeroTier), or public networks with proper configuration.

## System Architecture

VoidLink consists of two main components:

### 1. Server-Side (VoidLink-Server)

Handles authentication, message encryption, storage, and modular functionality.

```
VoidLink/
│── server.py                 # Main server script
│── encryption.py             # Handles encryption (AES-256)
│── authentication.py         # Manages user authentication
│── storage.py                # Handles chat persistence
│── file_transfer.py          # Secure file transfer module
│── config.json               # Server configuration file
│── database/                 # Stores user and chat data (encrypted)
│   │── users.json            # User database
│   │── chat_log.json         # Chat history
│   │── chat_history/         # User-specific chat history
│   │── files/                # Stored files
│   └── encryption_key.json   # Encryption key (protected)
│── requirements.txt          # Dependencies
└── README.md                 # Documentation
```

### 2. Client-Side (VoidLink-Client)

Provides a terminal-based interface for chat and file transfer.

```
VoidLink-Client/
│── client.py                 # Main client script
│── client_config.json        # Client-side configuration
│── chat_history/             # Stores local chat history
│── downloads/                # Downloaded files
└── requirements.txt          # Dependencies
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- Dependencies from requirements.txt

### Server Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/VoidLink.git
   cd VoidLink
   ```

2. Install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # (Windows: venv\Scripts\activate)
   pip install -r requirements.txt
   ```

3. Start the server:
   ```
   python server.py
   ```

By default, the server listens on 0.0.0.0:52384 (configurable in config.json).

### Client Setup

The client will be available in a separate repository. Follow the instructions in the client repository for setup.

## Security Considerations

- Uses AES-256 encryption for messages and file transfers
- Passwords are stored using PBKDF2 with SHA-256
- Server-side encryption key is generated on first run
- All file transfers are encrypted

## Customization

### Server Configuration

Edit `config.json` to customize server settings:

```json
{
    "server_host": "0.0.0.0",
    "server_port": 52384,
    "encryption_enabled": true,
    "storage": {
        "local": true,
        "cloud_backup": false
    }
}
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.