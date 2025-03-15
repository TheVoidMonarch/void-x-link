#!/bin/bash
# Script to run unit tests for VoidLink

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Install test dependencies if not already installed
pip show pytest > /dev/null 2>&1 || pip install pytest pytest-cov coverage

# Run the unit test runner
echo "Running unit tests..."
python run_unit_tests.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "All unit tests passed!"
else
    echo "Some unit tests failed."
fi