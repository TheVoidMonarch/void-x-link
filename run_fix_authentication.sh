#!/bin/bash
# Script to run the Fix Authentication Script

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

# Make the script executable
chmod +x fix_authentication.py

# Run the script
echo "Running Fix Authentication Script..."
python -u fix_authentication.py