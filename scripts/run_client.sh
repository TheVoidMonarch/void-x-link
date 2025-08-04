#!/bin/bash
#
# This script runs the VoidLink client.
#

# Exit on error
set -e

# Get the root directory of the project
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"

# Run the client
echo "Starting VoidLink client..."
python3 "$ROOT_DIR/core/client.py" "$@"
