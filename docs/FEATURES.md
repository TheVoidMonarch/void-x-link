# VoidLink — Feature Overview

This document explains every major feature of VoidLink: what it does and how it is implemented.

---

## Table of Contents

1. [End-to-End Encryption](#1-end-to-end-encryption)
2. [User Authentication](#2-user-authentication)
3. [Device Binding](#3-device-binding)
4. [Chat Rooms](#4-chat-rooms)
5. [Private Messaging](#5-private-messaging)
6. [Secure File Transfer](#6-secure-file-transfer)
7. [Resumable File Transfer](#7-resumable-file-transfer)
8. [File Security & Virus Scanning](#8-file-security--virus-scanning)
9. [Terminal UI (TUI)](#9-terminal-ui-tui)
10. [Web UI](#10-web-ui)
11. [Admin Web Panel](#11-admin-web-panel)
12. [CLI Tool](#12-cli-tool)
13. [Bot / API Extension](#13-bot--api-extension)
14. [Error Handling & Logging](#14-error-handling--logging)

---

## 1. End-to-End Encryption

### What it does
All messages and file payloads transmitted between a client and the server are encrypted so that only the intended recipient can read them.

### How it is implemented
**Implementation file:** `core/encryption.py`

- Uses **AES-256 in EAX mode** via the `cryptography` library (`cryptography.hazmat.primitives.ciphers.aead.AESGCM` / `AESCCM`).
- A symmetric master key is derived at first run using **PBKDF2-HMAC-SHA256** from the environment variable `VOIDLINK_KEY_PASSWORD` and stored in `database/encryption_key.json`.
- Every call to `encrypt(data)` generates a fresh random nonce; the nonce is prepended to the ciphertext so it can be recovered during decryption.
- `decrypt(token)` splits the nonce prefix from the ciphertext, re-derives the key, and returns the plaintext bytes.
- Helper functions `encrypt_file` / `decrypt_file` stream data in chunks so large files are never fully loaded into memory.
- The simple standalone variant in `simple_encryption.py` wraps the same primitives with a minimal API for testing.

---

## 2. User Authentication

### What it does
Users register with a username and password. Subsequent logins are verified against stored credential hashes. Sessions are tracked with tokens so clients do not need to re-send passwords on every request.

### How it is implemented
**Implementation file:** `core/authentication.py`

- User records are stored as JSON objects in `database/users.json` with fields: `username`, `password_hash`, `role`, `devices`.
- Passwords are hashed with **bcrypt** (12 rounds) using the `bcrypt` library. A legacy PBKDF2-SHA256 path is kept for backward compatibility.
- `register_user(username, password)` — checks uniqueness, hashes the password, appends the record to `users.json`.
- `authenticate_user(username, password)` — loads the stored hash and calls `bcrypt.checkpw`; raises `AuthenticationError` on failure.
- Successful login creates a signed session token (UUID4 + timestamp) written to `database/sessions.json`.
- `validate_session(token)` checks that the token exists and has not expired.
- `simple_authentication.py` provides a stand-alone demo implementation used by `simple_auth_test.py` and the TUI demo mode.

---

## 3. Device Binding

### What it does
A user account can be locked to specific hardware. When device binding is enabled, a login is only accepted if the connecting device matches a fingerprint that was previously registered.

### How it is implemented
**Implementation file:** `core/device_id.py`

- A device fingerprint is assembled from: MAC address (via `uuid.getnode()`), hostname (`socket.gethostname()`), operating system, and CPU architecture.
- The raw fields are concatenated and hashed with **SHA-256** to produce a short, stable identifier.
- `get_device_id()` — returns the fingerprint for the current machine.
- `register_device(username, device_id)` — appends the fingerprint to the `devices` list in `users.json`.
- `verify_device(username, device_id)` — looks up the stored list and returns `True` only if the fingerprint is present.
- The server calls `verify_device` after a successful password check when the client supplies a `device_id` field in the login message.
- `test_device_binding.py` exercises registration and verification paths.

---

## 4. Chat Rooms

### What it does
Users can join named chat rooms (public or private) and exchange messages that are persisted on the server with a rolling history.

### How it is implemented
**Implementation file:** `core/chat.py`, storage in `database/chat/`

- Room definitions (name, type, members list) live in `database/chat/rooms.json`.
- Each room has a corresponding message file `database/chat/messages/<room_name>.json`.
- `create_room(name, room_type, creator)` — writes a new entry to `rooms.json`.
- `send_message(room, username, text)` — appends a timestamped message dict to the room's message file. The list is capped at **1,000 messages**; older messages are dropped when the cap is exceeded.
- `get_messages(room, limit)` — returns the last `limit` messages (default 50).
- `join_room` / `leave_room` update the `members` list in `rooms.json` for private rooms.
- Messages are passed through `core/encryption.py` before being written to disk, so stored history is encrypted at rest.

---

## 5. Private Messaging

### What it does
Two users can exchange direct messages that are not visible in any chat room.

### How it is implemented
**Implementation files:** `core/chat.py`, `core/storage.py`, storage in `database/chat/private/`

- Direct messages are stored in `database/chat/private/<user_a>_<user_b>.json` (participants sorted alphabetically so the file name is deterministic).
- `send_private_message(sender, recipient, text)` in `core/chat.py` appends the message and enforces a cap of **500 messages** per pair.
- `get_private_messages(user_a, user_b, limit)` returns recent history.
- `core/storage.py` provides lower-level helpers for reading and writing per-user history files in `database/chat_history/`, encrypting content with the master key before persisting.

---

## 6. Secure File Transfer

### What it does
Clients can upload files to the server and download or share them with other users. All file data is encrypted in transit and at rest.

### How it is implemented
**Implementation file:** `core/file_transfer.py`, metadata in `database/file_metadata.json`, files in `database/files/`

- **Upload flow:**
  1. Client opens the file, reads it in 4 KB chunks, encrypts each chunk with `core/encryption.py`, and sends a series of `upload_chunk` protocol messages.
  2. Server reassembles chunks, writes the encrypted blob to `database/files/<uuid>`, and records metadata (original filename, uploader, size, SHA-256 hash, `shared_with` list) in `file_metadata.json`.
- **Download flow:**
  1. Client sends a `download` message with the file ID.
  2. Server verifies ownership or sharing permission, reads the encrypted blob, and streams it back in chunks.
  3. Client decrypts each chunk and writes the plaintext to the local destination path.
- **Share / Delete:** `share_file(file_id, recipient)` appends the recipient to `shared_with`; `delete_file(file_id, requester)` checks ownership before removing the blob and metadata entry.

---

## 7. Resumable File Transfer

### What it does
Large file transfers can be paused and resumed, even across network interruptions, without restarting from the beginning.

### How it is implemented
**Implementation file:** `core/file_transfer_resumable.py`, temp state in `database/temp/`

- A *transfer manifest* is saved to `database/temp/<transfer_id>.json` containing: file name, total size, list of received chunk indices, and a SHA-256 hash of each chunk.
- **Upload:** the client divides the file into fixed-size chunks (default 64 KB), computes a hash for each, and sends them one by one. The server records each successfully stored chunk in the manifest. On reconnection the client requests the manifest, skips already-received chunks, and resumes from the first missing one.
- **Download:** similarly, the server tracks which chunks have been acknowledged and retransmits only the missing ones on resume.
- Once the final chunk is received, the server verifies the whole-file hash, moves the completed file to `database/files/`, and removes the temp manifest.

---

## 8. File Security & Virus Scanning

### What it does
Every uploaded file is validated for size, MIME type, and dangerous file extensions. Optionally, each file is scanned for malware before being accepted.

### How it is implemented
**Implementation files:** `core/file_security.py`, `core/virus_scanner.py`, quarantine in `database/quarantine/`

#### `core/file_security.py`
- **Size limit:** rejects files larger than **100 MB**.
- **MIME whitelist:** only types in an allowed list (images, documents, archives, text, video, audio) pass. Unknown MIME types are rejected.
- **Extension blocklist:** extensions such as `.exe`, `.bat`, `.sh`, `.ps1`, `.py`, `.js`, etc. are always rejected regardless of declared MIME type.
- **Hash calculation:** computes SHA-256 of the raw bytes for deduplication and integrity verification.
- `validate_file(path_or_bytes)` — runs all checks in sequence and raises `FileSecurityError` with a descriptive reason on failure.

#### `core/virus_scanner.py`
- Wraps **ClamAV**: first attempts a Unix-domain-socket connection (`/var/run/clamav/clamd.ctl`), falls back to a TCP connection (`127.0.0.1:3310`).
- `scan_file(path)` — sends the file path to ClamAV via the `SCAN` command; returns `(clean: bool, threat_name: str | None)`.
- If ClamAV is unavailable the scanner logs a warning and returns `(True, None)` (fail-open) so that the system keeps working without an antivirus daemon.
- Infected files are moved to `database/quarantine/` and their metadata is flagged; they cannot be downloaded.

---

## 9. Terminal UI (TUI)

### What it does
A full-screen terminal application built with Python's `curses` library. It presents menus, a file browser, an authentication screen, and progress bars — all without needing a graphical environment.

### How it is implemented
**Implementation directory:** `tui/`

- `tui/tui.py` — main application class `VoidLinkTUI`.
  - `init_menus()` — builds the menu tree (Main Menu → Files, Chat, Settings, …).
  - `draw_header()` / `draw_footer()` — render the top status bar and bottom key-hint bar.
  - `draw_menu()` — renders the currently active menu; arrow-key navigation updates an internal `selected` index.
  - `show_progress(label, percent)` — draws a text progress bar used during transfers.
  - `login_screen()` — renders username/password input boxes; submits credentials to `core/authentication.py`.
- When core modules are available, actions are delegated to the real `core/` APIs. When they are absent, the TUI falls back to **demo mode** using hardcoded `DEMO_FILES` mock data.
- The curses `stdscr` is passed through the call stack so every drawing function can write to the same screen object.
- See also: `docs/TUI_README.md` for usage instructions.

---

## 10. Web UI

### What it does
A browser-based interface that lets users manage files and exchange messages without using the terminal.

### How it is implemented
**Implementation directory:** `web_ui/`

- Built with **Flask**. The main application object is defined in `web_ui/app.py`.
- Routes:
  - `GET /` — renders `index.html` (file listing).
  - `POST /upload` — receives a multipart file, delegates to `core/file_transfer.py`, and redirects back to `/`.
  - `GET /download/<file_id>` — streams the decrypted file as a response.
  - `POST /share` — calls `share_file(file_id, recipient)`.
  - `GET /messages` / `POST /messages` — renders and submits chat messages via `core/chat.py`.
- Templates in `web_ui/templates/` use Jinja2. Static assets (CSS, JS) live in `web_ui/static/`.
- Session management relies on **Flask-Login**; user objects are looked up from `core/authentication.py` on each request.

---

## 11. Admin Web Panel

### What it does
A separate Flask application for server administrators to manage users, chat rooms, uploaded files, and active transfers through a browser.

### How it is implemented
**Implementation directory:** `admin_webui/`

- Separate Flask app (`admin_webui/app.py`) mounted on a different port (default `5001`).
- Requires an `admin` role; role check is enforced by a `before_request` hook.
- Key routes:
  - `/users` — lists all users from `database/users.json`; admin can delete or promote/demote users.
  - `/rooms` — lists rooms from `database/chat/rooms.json`; admin can create or delete rooms.
  - `/files` — lists all uploaded files; admin can delete any file regardless of ownership.
  - `/transfers` — shows active and completed transfer manifests from `database/temp/`.
- Destructive actions require a POST with a CSRF token to prevent cross-site request forgery.

---

## 12. CLI Tool

### What it does
A scriptable command-line client (`voidlink`) for automating VoidLink operations from shell scripts or cron jobs.

### How it is implemented
**Implementation file:** `cli/voidlink_cli.py`

- Uses **argparse** for argument parsing.
- Supports two modes:
  - **Direct mode** — imports `core/` modules directly (no network hop); useful when running on the same machine as the server.
  - **Remote mode** — opens a TCP socket to the server and speaks the JSON protocol, identical to `client.py`.
- Common sub-commands:

  | Sub-command | Flags | Action |
  |-------------|-------|--------|
  | `list` | `--username`, `--password` | Print owned and shared files |
  | `upload` | `--file`, `--username`, `--password` | Upload a local file |
  | `download` | `--file-id`, `--output` | Download to a local path |
  | `share` | `--file-id`, `--recipient` | Share a file with another user |
  | `delete` | `--file-id` | Delete an owned file |
  | `send` | `--room`, `--message` | Post a message to a chat room |

- Output is coloured with ANSI escape codes; `--no-color` disables this.
- Exit codes follow UNIX conventions (`0` success, non-zero error).

---

## 13. Bot / API Extension

### What it does
Server-side hooks let developers plug in automated bots that react to events (new messages, file uploads) and expose a REST API for external integrations.

### How it is implemented
**Implementation files:** `modules/bot_integration.py`, `modules/api_extension.py`

#### `modules/bot_integration.py`
- Defines a `BotBase` class with overridable `on_message(room, sender, text)` and `on_file_upload(uploader, file_id)` hooks.
- The server calls these hooks at the relevant points in the message-handling path.
- Bot subclasses can be registered via `register_bot(bot_instance)` at startup.

#### `modules/api_extension.py`
- A **Flask Blueprint** that adds REST endpoints under `/api/v1/`:
  - `GET /api/v1/rooms` — list rooms (JSON).
  - `GET /api/v1/rooms/<name>/messages` — fetch recent messages (JSON).
  - `POST /api/v1/rooms/<name>/messages` — post a message (JSON body: `{"text": "…"}`).
  - `GET /api/v1/files` — list files accessible to the authenticated user.
- Authentication uses Bearer tokens (the same session tokens issued by `core/authentication.py`).
- The Blueprint is registered on the main Flask app at startup if the `api_extension` module is present.

---

## 14. Error Handling & Logging

### What it does
All runtime errors are caught, classified, and recorded. Structured log files let administrators diagnose problems without exposing sensitive information in error messages returned to clients.

### How it is implemented
**Implementation file:** `core/error_handling.py`, logs in `logs/`

- A hierarchy of custom exception classes extends `VoidLinkError`:
  - `AuthenticationError` — wrong password, expired session, unrecognised device.
  - `EncryptionError` — key derivation failure, corrupt ciphertext.
  - `FileTransferError` — missing file, permission denied, storage full.
  - `FileSecurityError` — size, MIME, extension, or virus check failure.
  - `ChatError` — unknown room, permission denied.

- `setup_logging(log_dir="logs/")` — configures Python's `logging` module with two handlers:
  - **RotatingFileHandler** (`logs/voidlink.log`) — INFO level, rotates at 5 MB, keeps 3 backups.
  - **StreamHandler** (stdout) — WARNING level and above so the terminal is not flooded.

- `handle_error(exc, context)` — logs the full traceback at ERROR level, then constructs a sanitised dict `{"error": exc.__class__.__name__, "message": str(exc)}` safe to send back over the wire.

- Every module obtains its logger with `logging.getLogger(__name__)` so log records carry the module name for easy filtering.
