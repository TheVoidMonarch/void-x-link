#!/bin/bash
# Make all scripts executable

# Make the script itself executable
chmod +x make_all_scripts_executable.sh

# Make all .sh files executable
find . -name "*.sh" -type f -exec chmod +x {} \;

# Make all .py files executable
find . -name "*.py" -type f -exec chmod +x {} \;

echo "All scripts are now executable."