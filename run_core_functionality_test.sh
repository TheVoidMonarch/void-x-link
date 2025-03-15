#!/bin/bash
# Script to run the core functionality test for VoidLink

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Create test results directory
mkdir -p test_results

# Run the core functionality test
echo "Running core functionality test..."
python core_functionality_test.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "All core functionality tests passed!"
else
    echo "Some core functionality tests failed. Check test_results/core_functionality_test_results.txt for details."
fi