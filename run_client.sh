#!/bin/bash
# Script to run the VoidLink Client

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Make the client script executable
chmod +x client.py
chmod +x run_client.py
chmod +x simple_encryption.py

# Run the client
echo "Starting VoidLink Client..."
python run_client.py "$@"