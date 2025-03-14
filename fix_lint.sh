#!/bin/bash
# Script to quickly fix common linting issues

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Run the quick lint fix script
python quick_lint_fix.py

echo "Quick lint fix complete!"
echo "For more comprehensive linting, run: ./lint.sh"