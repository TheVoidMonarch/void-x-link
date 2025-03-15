#!/bin/bash
# Simple test script

echo "Running simple test..."

# Check if Python is installed
python --version

# Check if the virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment is not activated."
else
    echo "Virtual environment is activated: $VIRTUAL_ENV"
fi

# Check if pytest is installed
if pip show pytest > /dev/null 2>&1; then
    echo "pytest is installed."
else
    echo "pytest is not installed."
fi

# Create test directories
mkdir -p test_results
mkdir -p test_results/coverage

echo "Simple test completed."