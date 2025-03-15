#!/bin/bash
# Script to install dependencies for VoidLink

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Detected Linux OS"
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        echo "Installing dependencies using apt..."
        sudo apt-get update
        sudo apt-get install -y libmagic-dev python3-dev
    elif command -v dnf &> /dev/null; then
        # Fedora
        echo "Installing dependencies using dnf..."
        sudo dnf install -y file-devel python3-devel
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        echo "Installing dependencies using yum..."
        sudo yum install -y file-devel python3-devel
    else
        echo "Unsupported Linux distribution. Please install libmagic manually."
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS"
    if command -v brew &> /dev/null; then
        echo "Installing dependencies using Homebrew..."
        brew install libmagic
    else
        echo "Homebrew not found. Please install it first:"
        echo "  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    echo "Detected Windows"
    echo "Please install libmagic manually for Windows."
    echo "You can download it from: https://github.com/pidydx/libmagicwin64"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install python-magic pytest pytest-cov coverage

echo "Dependencies installed successfully!"