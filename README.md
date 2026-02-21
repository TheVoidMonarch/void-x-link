# VoidLink

A lightweight, secure, terminal-based chat and file transfer application written in Python. VoidLink is self-hosted and designed for private circles or intranet deployments — no third-party servers required.

## Features

- **Encrypted chat** — end-to-end AES-256 encrypted messaging
- **Secure file transfer** — encrypted uploads, downloads, and resumable transfers
- **User authentication** — password hashing with PBKDF2/bcrypt, device binding
- **Terminal UI (TUI)** — full curses-based interface with menus and progress bars
- **Web UI & Admin panel** — optional browser-based interfaces
- **CLI tool** — scriptable command-line client
- **Bot / API extension** — extendable server-side modules
- **Self-hosted** — runs on LAN, VPN (Tailscale/ZeroTier), or public networks

## Project Structure

```
void-x-link/
├── server.py           # Main server entry point
├── client.py           # Main client entry point
├── config.json         # Server configuration
├── core/               # Core modules (auth, encryption, file transfer, chat, …)
├── tui/                # Terminal User Interface (curses)
├── cli/                # Command-line interface
├── web/                # Static web interface
├── web_ui/             # Flask-based web UI
├── admin_webui/        # Flask-based admin panel
├── modules/            # Optional extensions (bot, API)
├── utils/              # Utility scripts (key generation, backup, …)
├── database/           # Runtime data (users, chat logs, files)
├── tests/              # Test suite
└── requirements.txt    # Python dependencies
```

## Requirements

- Python 3.8+
- pip dependencies listed in `requirements.txt`

## Quick Start

### 1 — Install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2 — Start the server

```bash
python server.py
```

The server listens on `0.0.0.0:52384` by default (configurable in `config.json`).

### 3 — Connect with a client

```bash
python client.py
```

Or launch the Terminal UI:

```bash
./tui/run_tui.sh
```

## Configuration

Edit `config.json` to change server settings:

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

## Security

- AES-256 encryption for messages and file transfers
- Passwords stored with PBKDF2-SHA256 / bcrypt
- Encryption key generated locally on first run
- Virus scanning hook for uploaded files

## License

[MIT License](docs/LICENSE)

## Contributing

Contributions are welcome — feel free to open an issue or submit a pull request.
