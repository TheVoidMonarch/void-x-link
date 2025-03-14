#!/bin/bash
# Start script for VoidLink server

# Make scripts executable
chmod +x server.py
chmod +x run_server.py
chmod +x test_client.py
chmod +x run_test.py
chmod +x test_server.py

# Create necessary directories
mkdir -p database/files
mkdir -p database/chat_history

echo "VoidLink server is ready to run!"
echo ""
echo "To start the server, run:"
echo "  python run_server.py"
echo ""
echo "To test the server, run:"
echo "  python run_test.py"
echo ""
echo "To connect as a client, run:"
echo "  python test_client.py"#!/bin/bash
# Start script for VoidLink server

# Make scripts executable
chmod +x server.py
chmod +x run_server.py
chmod +x test_client.py
chmod +x run_test.py
chmod +x test_server.py

# Create necessary directories
mkdir -p database/files
mkdir -p database/chat_history

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