#!/bin/bash
# Script to run just the authentication tests

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Run the authentication tests
echo "Running authentication tests..."
python run_auth_test.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "Authentication tests passed!"
else
    echo "Authentication tests failed."
fi