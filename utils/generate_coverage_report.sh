#!/bin/bash
# Script to generate a test coverage report

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Run the coverage report generator
echo "Generating test coverage report..."
python generate_coverage_report.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "Coverage report generated successfully!"
else
    echo "Failed to generate coverage report."
fi