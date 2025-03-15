#!/bin/bash
# Script to fix the file_security.py module

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Run the fix script
echo "Fixing file_security.py and virus_scanner.py..."
python fix_file_security.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "Fix applied successfully!"
else
    echo "Failed to apply fix."
fi