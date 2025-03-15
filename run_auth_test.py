#!/usr/bin/env python3
"""
Simple script to run just the authentication tests
"""

import unittest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the test module
from tests.test_authentication import TestAuthentication

if __name__ == "__main__":
    # Create a test suite with just the authentication tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAuthentication)
    
    # Run the tests
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())