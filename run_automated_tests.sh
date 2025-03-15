#!/bin/bash
# Script to run the VoidLink automated test runner

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Fix syntax and linting issues first
echo "===== Fixing syntax and linting issues ====="
chmod +x fix_all_issues.sh
./fix_all_issues.sh

# Make sure all required scripts are executable
chmod +x reset_db.sh
chmod +x run_server.py
chmod +x run_client.sh
chmod +x test_client.py
chmod +x test_runner_fixed.py

# Try to install expect if not already installed (but don't fail if we can't)
if ! command -v expect &> /dev/null; then
    echo "Expect command not found. Trying to install..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y expect || echo "Could not install expect. Will use fallback method."
    elif command -v yum &> /dev/null; then
        sudo yum install -y expect || echo "Could not install expect. Will use fallback method."
    elif command -v brew &> /dev/null; then
        brew install expect || echo "Could not install expect. Will use fallback method."
    else
        echo "Could not determine package manager. Will use fallback method."
    fi
fi

# Create test output directory
mkdir -p test_results

# Set timestamp for reports
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Run the test runner
echo "Starting test run at $(date)"
python test_runner_fixed.py --output test_results/test_report_${TIMESTAMP}.json --log test_results/test_runner_${TIMESTAMP}.log

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "Tests completed successfully!"
else
    echo "Tests completed with exit code: $EXIT_CODE"
fi

# Open the HTML report if it exists
HTML_REPORT="test_results/test_report_${TIMESTAMP}.html"
if [ -f "$HTML_REPORT" ]; then
    echo "Test report generated: $HTML_REPORT"

    # Try to open the report in a browser
    if command -v xdg-open &> /dev/null; then
        xdg-open "$HTML_REPORT" &
    elif command -v open &> /dev/null; then
        open "$HTML_REPORT" &
    else
        echo "To view the report, open: $HTML_REPORT"
    fi
fi

exit $EXIT_CODE