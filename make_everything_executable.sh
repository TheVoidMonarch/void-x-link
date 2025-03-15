#!/bin/bash
# Make everything executable

# Make this script executable
chmod +x make_everything_executable.sh

# Make all shell scripts executable
find . -name "*.sh" -type f -exec chmod +x {} \;

# Make all Python scripts executable
find . -name "*.py" -type f -exec chmod +x {} \;

echo "All scripts are now executable."