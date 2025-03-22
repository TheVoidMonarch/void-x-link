#!/bin/bash
# Make all network-related scripts executable

# Function to make a file executable if it exists
make_executable() {
    if [ -f "$1" ]; then
        chmod +x "$1"
        echo "Made $1 executable"
    else
        echo "Warning: $1 not found, skipping"
    fi
}

# Make Python scripts executable
make_executable simple_tui.py
make_executable client.py
make_executable run_client.py
make_executable server.py
make_executable run_server.py
make_executable simple_encryption.py
make_executable simple_authentication.py
make_executable simple_file_security.py
make_executable simple_file_transfer.py

# Make shell scripts executable
make_executable run_simple_tui.sh
make_executable run_client.sh
make_executable run_server.sh
make_executable make_network_scripts_executable.sh
make_executable setup.sh

echo "All network scripts are now executable."