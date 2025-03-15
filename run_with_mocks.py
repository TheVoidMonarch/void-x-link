#!/usr/bin/env python3
"""
Run a Python script with mock modules for magic and clamd
"""

import sys
import os
import importlib.util

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import mock modules
from mock_magic import Magic
from mock_clamd import ClamdUnixSocket, ClamdNetworkSocket, ConnectionError

# Create mock modules
sys.modules['magic'] = type('magic', (), {'Magic': Magic})
sys.modules['clamd'] = type('clamd', (), {
    'ClamdUnixSocket': ClamdUnixSocket,
    'ClamdNetworkSocket': ClamdNetworkSocket,
    'ConnectionError': ConnectionError
})

# Run the specified script
if len(sys.argv) > 1:
    script_path = sys.argv[1]
    script_args = sys.argv[2:]
    
    # Load the script as a module
    spec = importlib.util.spec_from_file_location("__main__", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Run the script with the specified arguments
    sys.argv = [script_path] + script_args
    
    # Exit with the same exit code
    sys.exit(module.__dict__.get('exit_code', 0))
else:
    print("Usage: python run_with_mocks.py <script_path> [args...]")
    sys.exit(1)