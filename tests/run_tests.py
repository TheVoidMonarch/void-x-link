#!/usr/bin/env python3
"""
Test runner for VoidLink
"""

import os
import sys
import unittest
import coverage

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_tests_with_coverage():
    """Run tests with coverage"""
    # Start coverage
    cov = coverage.Coverage(
        source=['authentication', 'encryption', 'file_security', 'file_transfer',
                'file_transfer_resumable', 'rooms', 'storage', 'server'],
        omit=['*/__pycache__/*', '*/tests/*']
    )
    cov.start()

    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Stop coverage
    cov.stop()
    cov.save()

    # Print coverage report
    print("\nCoverage Report:")
    cov.report()

    # Generate HTML report
    html_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'coverage_html')
    cov.html_report(directory=html_dir)
    print(f"\nHTML coverage report generated in {html_dir}")

    return result


def run_tests():
    """Run tests without coverage"""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    # Check if coverage is installed
    try:
        import coverage
        result = run_tests_with_coverage()
    except ImportError:
        print("Coverage not installed. Running tests without coverage.")
        result = run_tests()

    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
