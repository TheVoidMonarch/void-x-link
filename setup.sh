#!/bin/bash
# Setup script for VoidLink

# Create virtual environment
python -m venv voidlink-env

# Activate virtual environment
source voidlink-env/bin/activate

# Install dependencies
pip install pycryptodome

# Make scripts executable
chmod +x server.py
chmod +x run_server.py
chmod +x test_client_fixed.py
chmod +x run_test_fixed.py
chmod +x test_server.py
chmod +x run_client.sh
chmod +x reset_db.sh
chmod +x lint.sh
chmod +x lint_fixes.py
chmod +x quick_lint_fix.py
chmod +x fix_lint.sh
chmod +x run_tests.sh
chmod +x tests/run_tests.py
chmod +x voidlink_cli.py
chmod +x run_admin_webui.sh
chmod +x admin_webui/app.py

# Create necessary directories
mkdir -p database/files
mkdir -p database/chat_history

# Copy fixed files to original names
cp test_client_fixed.py test_client.py
cp run_test_fixed.py run_test.py

echo "VoidLink setup complete!"
echo ""
echo "To start the server, run:"
echo "  source voidlink-env/bin/activate"
echo "  python run_server.py"
echo ""
echo "To connect as a client, run in a new terminal:"
echo "  source voidlink-env/bin/activate"
echo "  ./run_client.sh"
echo ""
echo "To run the comprehensive test, run:"
echo "  source voidlink-env/bin/activate"
echo "  python run_test.py"