#!/bin/bash
# Script to run the VoidLink Server

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Make the server script executable
chmod +x server.py
chmod +x run_server.py
chmod +x simple_encryption.py
chmod +x simple_authentication.py

# Create necessary directories
mkdir -p database/files
mkdir -p database/metadata

# Run the server
echo "Starting VoidLink Server..."
python run_server.py "$@"