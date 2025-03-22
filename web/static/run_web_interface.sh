#!/bin/bash
# Script to run the VoidLink web interface

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Make the web server executable
chmod +x web_server.py

# Create necessary directories
mkdir -p web/img

# Run the web server
echo "Starting VoidLink Web Interface..."
python web_server.py