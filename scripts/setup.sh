#!/bin/bash
#
# This script installs dependencies and makes other scripts executable.
#

# Exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r "$SCRIPT_DIR/../requirements.txt"

# Make other scripts executable
echo "Making other scripts executable..."
chmod +x "$SCRIPT_DIR/run_server.sh"
chmod +x "$SCRIPT_DIR/run_client.sh"
chmod +x "$SCRIPT_DIR/run_admin_webui.sh"
chmod +x "$SCRIPT_DIR/run_tests.sh"

echo "Setup complete."
