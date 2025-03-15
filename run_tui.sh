#!/bin/bash
# Script to run the VoidLink Terminal User Interface

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Make the TUI script executable
chmod +x tui.py

# Run the TUI
echo "Starting VoidLink Terminal User Interface..."
python tui.py