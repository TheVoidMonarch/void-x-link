#!/bin/bash
# VoidLink Setup Script

echo "╔═══════════════════════════════════════════╗"
echo "║           VoidLink Setup Script           ║"
echo "║  Secure Terminal-Based Chat & File Share  ║"
echo "╚═══════════════════════════════════════════╝"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d "." -f 1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d "." -f 2)

echo "Found Python $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    echo "VoidLink requires Python 3.7 or higher. Please upgrade your Python installation."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv voidlink-env || {
    echo "Failed to create virtual environment. Please make sure venv is installed."
    echo "On Ubuntu/Debian: sudo apt-get install python3-venv"
    echo "On Fedora: sudo dnf install python3-venv"
    echo "On macOS: pip3 install virtualenv"
    exit 1
}

# Activate virtual environment
echo "Activating virtual environment..."
source voidlink-env/bin/activate || {
    echo "Failed to activate virtual environment."
    exit 1
}

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip || echo "Warning: Failed to upgrade pip, continuing anyway..."

# Install packages from requirements.txt
echo "Installing required packages..."
pip install -r requirements.txt || {
    echo "Warning: Some packages failed to install. Trying to install them individually..."
    
    # Try to install each package individually
    pip install pycryptodome || echo "Warning: Failed to install pycryptodome"
    pip install cryptography || echo "Warning: Failed to install cryptography"
    pip install requests || echo "Warning: Failed to install requests"
    pip install python-dotenv || echo "Warning: Failed to install python-dotenv"
    
    # Only install windows-curses on Windows
    if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win"* ]]; then
        pip install windows-curses || echo "Warning: Failed to install windows-curses"
    fi
    
    pip install tqdm || echo "Warning: Failed to install tqdm"
    pip install colorama || echo "Warning: Failed to install colorama"
    pip install bcrypt || echo "Warning: Failed to install bcrypt"
}

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p database/files
mkdir -p database/metadata
mkdir -p database/chat_history

# Make scripts executable
echo "Making scripts executable..."
chmod +x make_network_scripts_executable.sh || echo "Warning: Failed to make make_network_scripts_executable.sh executable."
if [ -x make_network_scripts_executable.sh ]; then
    ./make_network_scripts_executable.sh
else
    echo "Warning: Could not execute make_network_scripts_executable.sh, trying to make scripts executable manually..."
    
    # Make Python scripts executable
    for script in simple_tui.py client.py run_client.py server.py run_server.py simple_encryption.py simple_authentication.py simple_file_security.py simple_file_transfer.py; do
        if [ -f "$script" ]; then
            chmod +x "$script" || echo "Warning: Failed to make $script executable."
        fi
    done
    
    # Make shell scripts executable
    for script in run_simple_tui.sh run_client.sh run_server.sh; do
        if [ -f "$script" ]; then
            chmod +x "$script" || echo "Warning: Failed to make $script executable."
        fi
    done
fi

echo
echo "╔═══════════════════════════════════════════╗"
echo "║           Setup Complete!                 ║"
echo "╚═══════════════════════════════════════════╝"
echo
echo "To use VoidLink:"
echo "1. Activate the virtual environment:"
echo "   source voidlink-env/bin/activate"
echo
echo "2. Run the server:"
echo "   ./run_server.sh"
echo
echo "3. Run the client (in another terminal):"
echo "   ./run_client.sh --host localhost"
echo
echo "4. Or run the simple TUI:"
echo "   ./run_simple_tui.sh"
echo
echo "Enjoy using VoidLink!"