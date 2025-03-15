#!/bin/bash
# Master script to run all tests and generate a comprehensive report

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Create test results directory
mkdir -p test_results

# Run the simple tests
echo "=== Running Simple Tests ==="
echo ""

echo "Running authentication test..."
./simple_auth_test.sh > test_results/simple_auth_test.txt
if [ $? -eq 0 ]; then
    echo "Authentication test: PASSED"
    AUTH_RESULT="PASSED"
else
    echo "Authentication test: FAILED"
    AUTH_RESULT="FAILED"
fi
echo ""

echo "Running encryption test..."
./simple_encryption_test.sh > test_results/simple_encryption_test.txt
if [ $? -eq 0 ]; then
    echo "Encryption test: PASSED"
    ENCRYPTION_RESULT="PASSED"
else
    echo "Encryption test: FAILED"
    ENCRYPTION_RESULT="FAILED"
fi
echo ""

echo "Running file security test..."
./simple_file_security_test.sh > test_results/simple_file_security_test.txt
if [ $? -eq 0 ]; then
    echo "File security test: PASSED"
    FILE_SECURITY_RESULT="PASSED"
else
    echo "File security test: FAILED"
    FILE_SECURITY_RESULT="FAILED"
fi
echo ""

# Generate coverage report
echo "=== Generating Coverage Report ==="
./generate_coverage_report.sh > test_results/coverage_report.txt
echo ""

# Generate final summary
echo "=== Generating Final Summary ==="
echo "VoidLink Test Summary" > test_results/final_summary.txt
echo "====================" >> test_results/final_summary.txt
echo "" >> test_results/final_summary.txt
echo "Date: $(date)" >> test_results/final_summary.txt
echo "" >> test_results/final_summary.txt
echo "Simple Tests:" >> test_results/final_summary.txt
echo "- Authentication: $AUTH_RESULT" >> test_results/final_summary.txt
echo "- Encryption: $ENCRYPTION_RESULT" >> test_results/final_summary.txt
echo "- File Security: $FILE_SECURITY_RESULT" >> test_results/final_summary.txt
echo "" >> test_results/final_summary.txt

# Check if all simple tests passed
if [ "$AUTH_RESULT" = "PASSED" ] && [ "$ENCRYPTION_RESULT" = "PASSED" ] && [ "$FILE_SECURITY_RESULT" = "PASSED" ]; then
    echo "Overall Result: PASSED" >> test_results/final_summary.txt
    OVERALL_RESULT="PASSED"
else
    echo "Overall Result: FAILED" >> test_results/final_summary.txt
    OVERALL_RESULT="FAILED"
fi

echo "" >> test_results/final_summary.txt
echo "Coverage Report:" >> test_results/final_summary.txt
echo "- See test_results/coverage directory for detailed coverage report" >> test_results/final_summary.txt
echo "" >> test_results/final_summary.txt
echo "See test_results directory for detailed test results." >> test_results/final_summary.txt

# Display the summary
cat test_results/final_summary.txt

# Return appropriate exit code
if [ "$OVERALL_RESULT" = "PASSED" ]; then
    echo ""
    echo "All tests passed!"
    exit 0
else
    echo ""
    echo "Some tests failed. See test_results directory for details."
    exit 1
fi