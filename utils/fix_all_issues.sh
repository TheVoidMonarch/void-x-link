#!/bin/bash
# Script to fix all syntax and linting issues in the VoidLink codebase

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Install required packages
pip install autopep8 pycodestyle pylint

# Make scripts executable
chmod +x fix_syntax_issues.py
chmod +x fix_all_linting.py

echo "===== Step 1: Fixing syntax issues ====="
python fix_syntax_issues.py

echo "===== Step 2: Fixing linting issues ====="
python fix_all_linting.py --aggressive

echo "===== Step 3: Running final syntax check ====="
python -m compileall .

echo "===== Step 4: Running final linting check ====="
pylint --errors-only .

echo "All fixes complete!"