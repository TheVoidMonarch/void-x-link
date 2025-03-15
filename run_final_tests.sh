#!/bin/bash
# Script to run the final tests for VoidLink

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Make all scripts executable
echo "Making all scripts executable..."
chmod +x make_all_executable.sh
./make_all_executable.sh

# Create test results directory
mkdir -p test_results

# Run the comprehensive tests
echo "Running comprehensive tests..."
python run_comprehensive_tests.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "All comprehensive tests passed!"
else
    echo "Some comprehensive tests failed. Check test_results/comprehensive_test_results.txt for details."
fi

# Display a summary
if [ -f test_results/comprehensive_test_results.txt ]; then
    echo ""
    echo "Test Summary:"
    grep -E "^(FAILED|ERROR|PASSED)" test_results/comprehensive_test_results.txt | sort | uniq -c
    echo ""
    echo "For detailed results, see test_results/comprehensive_test_results.txt"
fi