#!/usr/bin/env python3
"""
VoidLink Test Runner with Mocks

This script runs the tests with mock modules to avoid dependencies like libmagic.
"""

import os
import sys
import unittest
import coverage
import importlib.util
import shutil
from unittest.mock import MagicMock

# Create test results directory
os.makedirs("test_results", exist_ok=True)

# Set up mocking
sys.modules['magic'] = MagicMock()

# Save original modules
original_modules = {}
if 'file_security' in sys.modules:
    original_modules['file_security'] = sys.modules['file_security']
if 'virus_scanner' in sys.modules:
    original_modules['virus_scanner'] = sys.modules['virus_scanner']

# Load mock modules
mock_file_security_path = os.path.join('tests', 'mock_file_security.py')
mock_virus_scanner_path = os.path.join('tests', 'mock_virus_scanner.py')

if os.path.exists(mock_file_security_path):
    spec = importlib.util.spec_from_file_location('file_security', mock_file_security_path)
    mock_file_security = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mock_file_security)
    sys.modules['file_security'] = mock_file_security
    print("Loaded mock file_security module")

if os.path.exists(mock_virus_scanner_path):
    spec = importlib.util.spec_from_file_location('virus_scanner', mock_virus_scanner_path)
    mock_virus_scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mock_virus_scanner)
    sys.modules['virus_scanner'] = mock_virus_scanner
    print("Loaded mock virus_scanner module")

try:
    # Start coverage
    cov = coverage.Coverage(
        source=['authentication', 'encryption', 'file_security', 'file_transfer',
                'file_transfer_resumable', 'storage', 'server', 'client'],
        omit=['*/__pycache__/*', '*/tests/*', '*_test.py', 'test_*.py']
    )
    cov.start()
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Run tests
    result_file = "test_results/unit_test_results.txt"
    with open(result_file, 'w') as f:
        runner = unittest.TextTestRunner(verbosity=2, stream=f)
        result = runner.run(suite)
    
    # Stop coverage
    cov.stop()
    cov.save()
    
    # Generate coverage report
    cov.report()
    cov.html_report(directory="test_results/coverage")
    
    print(f"Tests completed. Results saved to {result_file}")
    print(f"Coverage report generated in test_results/coverage")
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())

finally:
    # Restore original modules
    for name, module in original_modules.items():
        sys.modules[name] = module