#!/bin/bash
# Script to run a simple authentication test

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Run the simple authentication test
echo "Running simple authentication test..."
python simple_auth_test.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "Simple authentication test passed!"
else
    echo "Simple authentication test failed."
fi