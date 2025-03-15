#!/usr/bin/env python3
"""
Generate a test coverage report for VoidLink
"""

import os
import sys
import coverage
import unittest
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

# Create test results directory
os.makedirs("test_results/coverage", exist_ok=True)

# Start coverage
cov = coverage.Coverage(
    source=['authentication', 'encryption', 'file_security', 'file_transfer',
            'file_transfer_resumable', 'storage', 'server', 'client'],
    omit=['*/__pycache__/*', '*/tests/*', '*_test.py', 'test_*.py', 'mock_*.py']
)
cov.start()

# Run the simple tests
print("Running simple tests for coverage...")

# Authentication tests
print("Running authentication tests...")
from simple_auth_test import test_hash_password, test_verify_password
test_hash_password()
test_verify_password()

# Encryption tests
print("Running encryption tests...")
from simple_encryption_test import test_encrypt_decrypt_string, test_encrypt_decrypt_dict
test_encrypt_decrypt_string()
test_encrypt_decrypt_dict()

# File security tests
print("Running file security tests...")
from simple_file_security_test import (
    test_is_file_too_large, test_has_dangerous_extension,
    test_is_mime_type_allowed, test_calculate_file_hash, test_scan_file
)
test_is_file_too_large()
test_has_dangerous_extension()
test_is_mime_type_allowed()
test_calculate_file_hash()
test_scan_file()

# Stop coverage
cov.stop()
cov.save()

# Generate coverage report
print("\nCoverage Report:")
cov.report()
cov.html_report(directory="test_results/coverage")

print(f"\nCoverage report generated in test_results/coverage")
print("Open test_results/coverage/index.html in a browser to view the detailed report")