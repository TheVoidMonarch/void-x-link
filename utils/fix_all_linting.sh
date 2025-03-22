#!/bin/bash
# Script to fix linting issues across the entire VoidLink codebase

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Install autopep8 if not already installed
pip install autopep8

# Make the fix script executable
chmod +x fix_all_linting.py

# Run the fix script with aggressive mode
python fix_all_linting.py --aggressive

echo "Linting fixes complete!"