#!/bin/bash
# Script to run the VoidLink client

# Copy the fixed client to the main client file
cp test_client_fixed.py test_client.py

# Make it executable
chmod +x test_client.py

# Run the client
python test_client.py