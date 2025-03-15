#!/bin/bash
# Script to fix the test1.sh file

# Make the new test script executable
chmod +x test1_fixed.sh

# Replace the old test script with the new one
mv test1_fixed.sh test1.sh

# Make sure it's executable
chmod +x test1.sh

# Make other test scripts executable
chmod +x run_all_tests.py
chmod +x make_tests_executable.sh
if [ -f "tests/run_tests.py" ]; then
    chmod +x tests/run_tests.py
fi
if [ -f "run_test.py" ]; then
    chmod +x run_test.py
fi

echo "Test scripts fixed and made executable."