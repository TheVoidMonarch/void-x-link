#!/bin/bash
# Script to run the VoidLink Simple Terminal User Interface

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Make the TUI script executable
chmod +x simple_tui.py

# Run the TUI
echo "Starting VoidLink Simple Terminal User Interface..."
python simple_tui.py