#!/bin/bash
# Start script for VoidLink server

# Make scripts executable
chmod +x server.py
chmod +x run_server.py
chmod +x test_client_fixed.py
chmod +x run_test_fixed.py
chmod +x test_server.py

# Create necessary directories
mkdir -p database/files
mkdir -p database/chat_history

# Copy fixed files to original names
cp test_client_fixed.py test_client.py
cp run_test_fixed.py run_test.py

echo "VoidLink server is ready to run!"
echo ""
echo "To start the server, run:"
echo "  python run_server.py"
echo ""
echo "To test the server, run:"
echo "  python run_test.py"
echo ""
echo "To connect as a client, run:"
echo "  python test_client.py"