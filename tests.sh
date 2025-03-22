#!/bin/bash
# Script to run comprehensive tests for VoidLink

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Set PYTHONPATH to include the core directory
export PYTHONPATH=$PYTHONPATH:$(pwd)/core

# Install test dependencies if not already installed
pip show pytest > /dev/null 2>&1 || pip install pytest pytest-cov coverage

# Run the comprehensive test runner
echo "Running comprehensive tests..."
python run_all_tests.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Some tests failed. Check test_results directory for details."
fi