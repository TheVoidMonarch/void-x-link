#!/bin/bash
# Script to run a simple encryption test

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Run the simple encryption test
echo "Running simple encryption test..."
python simple_encryption_test.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "Simple encryption test passed!"
else
    echo "Simple encryption test failed."
fi