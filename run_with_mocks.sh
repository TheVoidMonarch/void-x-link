#!/bin/bash
# Script to run a Python script with mock modules

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Check if a script path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <script_path> [args...]"
    exit 1
fi

# Run the script with mock modules
echo "Running $1 with mock modules..."
python run_with_mocks.py "$@"

# Check exit code
if [ $? -eq 0 ]; then
    echo "Script executed successfully!"
else
    echo "Script execution failed."
fi