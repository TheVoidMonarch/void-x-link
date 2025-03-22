#!/bin/bash
# Script to run the VoidLink Server

# Make sure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    # Try to activate the virtual environment
    if [ -f voidlink-env/bin/activate ]; then
        echo "Activating virtual environment..."
        source voidlink-env/bin/activate
    else
        echo "Please activate the virtual environment first:"
        echo "source voidlink-env/bin/activate"
        exit 1
    fi
fi

# Make the server script executable
if [ -f server.py ]; then
    chmod +x server.py
fi

if [ -f run_server.py ]; then
    chmod +x run_server.py
fi

# Create necessary directories
mkdir -p database/files
mkdir -p database/metadata
mkdir -p database/chat_history
mkdir -p database/temp

# Parse command line arguments
HOST="0.0.0.0"
PORT="8000"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        *)
            # Unknown option
            shift
            ;;
    esac
done

# Run the server
echo "Starting VoidLink Server..."
echo "Listening on $HOST:$PORT..."

# Set PYTHONPATH to include the current directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Run the server with debug logging
python -u server.py --host "$HOST" --port "$PORT"