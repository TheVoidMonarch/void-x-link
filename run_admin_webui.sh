#!/bin/bash
# Script to run the VoidLink Admin Web Interface

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Install dependencies if not already installed
pip install -r admin_webui/requirements.txt

# Run the web interface
cd admin_webui
python app.py