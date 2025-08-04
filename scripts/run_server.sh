#!/bin/bash
#
# This script runs the VoidLink server.
#

# Exit on error
set -e

# Get the root directory of the project
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"

# Run the server
echo "Starting VoidLink server..."
python3 "$ROOT_DIR/core/server.py" "$@"
