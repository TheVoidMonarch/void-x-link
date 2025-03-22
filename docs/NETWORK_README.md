# VoidLink Network Functionality

This document explains how to use VoidLink's network functionality to share files over a local area network (LAN).

## Overview

VoidLink includes a client-server architecture that allows you to:

1. Run a VoidLink server on one machine
2. Connect to it from multiple clients on different machines
3. Upload, download, and share files between users

## Server Setup

To run the VoidLink server:

1. Activate the virtual environment:
   ```bash
   source voidlink-env/bin/activate
   ```

2. Make the run script executable:
   ```bash
   chmod +x run_server.sh
   ```

3. Run the server:
   ```bash
   ./run_server.sh
   ```

By default, the server listens on all network interfaces (0.0.0.0) on port 8000.

## Client Setup

To run the VoidLink client:

1. Activate the virtual environment:
   ```bash
   source voidlink-env/bin/activate
   ```

2. Make the run script executable:
   ```bash
   chmod +x run_client.sh
   ```

3. Run the client:
   ```bash
   ./run_client.sh --host SERVER_IP
   ```

Replace `SERVER_IP` with the IP address of the machine running the server.

## Demo Users

In demo mode, the following users are available:

- Username: `admin`, Password: `admin123`
- Username: `user`, Password: `user123`
- Username: `demo`, Password: `password`

## Client Commands

The client can be run in interactive mode or with specific commands:

### Interactive Mode

```bash
./run_client.sh --host SERVER_IP
```

This will start an interactive session where you can:
- List files
- Upload files
- Download files
- Share files
- Delete files

### Command-Line Mode

```bash
# List files
./run_client.sh --host SERVER_IP --username USER --password PASS --command list

# Upload a file
./run_client.sh --host SERVER_IP --username USER --password PASS --command upload --file PATH_TO_FILE

# Download a file
./run_client.sh --host SERVER_IP --username USER --password PASS --command download --file-id FILE_ID --output OUTPUT_PATH

# Share a file
./run_client.sh --host SERVER_IP --username USER --password PASS --command share --file-id FILE_ID --recipient RECIPIENT

# Delete a file
./run_client.sh --host SERVER_IP --username USER --password PASS --command delete --file-id FILE_ID
```

## Finding Your Server IP

To find the IP address of your server machine:

### On Linux/macOS:
```bash
ifconfig
```
Look for the `inet` address on your network interface (e.g., eth0, wlan0).

### On Windows:
```bash
ipconfig
```
Look for the IPv4 address of your network adapter.

## Troubleshooting

1. **Connection Refused**: Make sure the server is running and that there are no firewall rules blocking the connection.

2. **Cannot Connect from Another Machine**: Ensure the server machine's firewall allows incoming connections on port 8000.

3. **Slow Transfers**: The demo implementation uses a simple protocol. For better performance, consider using the core VoidLink modules.

4. **Authentication Errors**: In demo mode, only the predefined users can log in. When using the actual VoidLink modules, users must be created first.

## Security Considerations

This implementation is intended for use on trusted local networks only. For production use:

1. Implement proper TLS/SSL encryption
2. Use stronger authentication mechanisms
3. Add rate limiting and other security measures
4. Consider using a reverse proxy for additional security