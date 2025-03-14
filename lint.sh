#!/bin/bash
# Script to run linting and auto-fix common issues

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "source voidlink-env/bin/activate"
    exit 1
fi

# Install linting tools if not already installed
pip install flake8 autopep8 isort mypy pylint

# Run isort to fix import order
echo "Fixing import order with isort..."
isort --profile black .

# Run autopep8 to fix PEP 8 issues
echo "Fixing PEP 8 issues with autopep8..."
autopep8 --in-place --recursive --aggressive --aggressive .

# Run flake8 to check for remaining issues
echo "Checking for remaining issues with flake8..."
flake8 --count --select=E9,F63,F7,F82 --show-source --statistics .

# Run mypy for type checking
echo "Running type checking with mypy..."
mypy --ignore-missing-imports .

# Run pylint for more comprehensive linting
echo "Running pylint for comprehensive linting..."
pylint --disable=C0111,C0103,C0303,W0611,R0903,R0913,R0914,R0915 *.py

# Run our custom linting fixes
echo "Running custom linting fixes..."
python lint_fixes.py

echo "Linting complete!"