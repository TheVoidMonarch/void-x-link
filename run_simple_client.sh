#!/bin/bash
# Script to run the Simple VoidLink Client

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    # Try to activate the virtual environment
    if [ -f voidlink-env/bin/activate ]; then
        echo "Activating virtual environment..."
        source voidlink-env/bin/activate
    else
        echo "Please activate the virtual environment first:"
        echo "source voidlink-env/bin/activate"
        exit 1
    fi
fi

# Make the client script executable
chmod +x simple_client.py

# Run the client
echo "Starting Simple VoidLink Client..."
python -u simple_client.py