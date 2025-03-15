#!/bin/bash
# Script to run a simple file_security test with mock modules

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Run the simple file_security test with mock modules
echo "Running simple file_security test with mock modules..."
./run_with_mocks.sh simple_file_security_test.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "Simple file_security test passed!"
else
    echo "Simple file_security test failed."
fi