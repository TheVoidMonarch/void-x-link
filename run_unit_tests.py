#!/usr/bin/env python3
"""
Simple Unit Test Runner for VoidLink
"""

import os
import sys
import unittest

# Create test results directory
os.makedirs("test_results", exist_ok=True)

# Discover and run tests
loader = unittest.TestLoader()
start_dir = "tests"
suite = loader.discover(start_dir, pattern="test_*.py")

# Run tests
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with appropriate code
sys.exit(not result.wasSuccessful())