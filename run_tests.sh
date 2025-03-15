#!/bin/bash
# Script to run tests for VoidLink

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Install test dependencies if not already installed
pip install pytest pytest-cov coverage

# Run tests
echo "Running tests..."
python tests/run_tests.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Some tests failed."
fi