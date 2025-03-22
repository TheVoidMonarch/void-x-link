#!/usr/bin/env python3
"""
VoidLink Comprehensive Test Runner

This script runs all tests for the VoidLink project, including:
1. Unit tests for individual modules
2. Integration tests for component interactions
3. End-to-end tests for full system functionality
4. Mock tests for testing without dependencies

It generates a comprehensive test report and code coverage analysis.
"""

import os
import sys
import time
import unittest
import coverage
import argparse
import subprocess
from datetime import datetime

# Constants
TEST_REPORT_DIR = "test_results"
COVERAGE_DIR = f"{TEST_REPORT_DIR}/coverage"
UNIT_TEST_DIR = "tests"
MOCK_TEST_FILE = "test_voidlink_mock.py"
INTEGRATION_TEST_FILE = "test_voidlink.py"
COMPREHENSIVE_TEST_FILE = "run_test.py"


def setup_environment():
    """Set up the test environment"""
    print("\n=== Setting up test environment ===")
    
    # Create test results directory
    os.makedirs(TEST_REPORT_DIR, exist_ok=True)
    os.makedirs(COVERAGE_DIR, exist_ok=True)
    
    # Reset database if reset_db.sh exists
    if os.path.exists("reset_db.sh"):
        print("Resetting database...")
        try:
            subprocess.run(["bash", "reset_db.sh"], check=True)
        except subprocess.SubprocessError as e:
            print(f"Warning: Could not reset database: {str(e)}")
            # Create database directories manually
            os.makedirs("database", exist_ok=True)
            os.makedirs("database/files", exist_ok=True)
            os.makedirs("database/chat_history", exist_ok=True)
    else:
        print("Warning: reset_db.sh not found. Creating database directories manually.")
        os.makedirs("database", exist_ok=True)
        os.makedirs("database/files", exist_ok=True)
        os.makedirs("database/chat_history", exist_ok=True)


def run_unit_tests():
    """Run unit tests for individual modules"""
    print("\n=== Running Unit Tests ===")
    
    # Start coverage
    cov = coverage.Coverage(
        source=['authentication', 'encryption', 'file_security', 'file_transfer',
                'file_transfer_resumable', 'storage', 'server', 'client'],
        omit=['*/__pycache__/*', '*/tests/*', '*_test.py', 'test_*.py']
    )
    cov.start()
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = UNIT_TEST_DIR
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Create a test result file
    result_file = f"{TEST_REPORT_DIR}/unit_test_results.txt"
    with open(result_file, 'w') as f:
        runner = unittest.TextTestRunner(verbosity=2, stream=f)
        result = runner.run(suite)
    
    # Stop coverage
    cov.stop()
    cov.save()
    
    # Generate coverage report
    cov.report()
    cov.html_report(directory=COVERAGE_DIR)
    
    print(f"Unit tests completed. Results saved to {result_file}")
    print(f"Coverage report generated in {COVERAGE_DIR}")
    
    return result.wasSuccessful()


def run_mock_tests():
    """Run mock tests that don't require actual dependencies"""
    print("\n=== Running Mock Tests ===")
    
    if not os.path.exists(MOCK_TEST_FILE):
        print(f"Warning: Mock test file {MOCK_TEST_FILE} not found. Skipping mock tests.")
        return True
    
    # Run the mock tests
    result_file = f"{TEST_REPORT_DIR}/mock_test_results.txt"
    try:
        with open(result_file, 'w') as f:
            result = subprocess.run(
                [sys.executable, MOCK_TEST_FILE],
                stdout=f,
                stderr=subprocess.STDOUT,
                check=False
            )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running mock tests: {str(e)}")
        return False


def run_integration_tests():
    """Run integration tests for component interactions"""
    print("\n=== Running Integration Tests ===")
    
    if not os.path.exists(INTEGRATION_TEST_FILE):
        print(f"Warning: Integration test file {INTEGRATION_TEST_FILE} not found. Skipping integration tests.")
        return True
    
    # Run the integration tests
    result_file = f"{TEST_REPORT_DIR}/integration_test_results.txt"
    try:
        with open(result_file, 'w') as f:
            result = subprocess.run(
                [sys.executable, INTEGRATION_TEST_FILE],
                stdout=f,
                stderr=subprocess.STDOUT,
                check=False
            )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running integration tests: {str(e)}")
        return False


def run_comprehensive_tests():
    """Run comprehensive end-to-end tests"""
    print("\n=== Running Comprehensive Tests ===")
    
    if not os.path.exists(COMPREHENSIVE_TEST_FILE):
        print(f"Warning: Comprehensive test file {COMPREHENSIVE_TEST_FILE} not found. Skipping comprehensive tests.")
        return True
    
    # Run the comprehensive tests
    result_file = f"{TEST_REPORT_DIR}/comprehensive_test_results.txt"
    try:
        with open(result_file, 'w') as f:
            result = subprocess.run(
                [sys.executable, COMPREHENSIVE_TEST_FILE],
                stdout=f,
                stderr=subprocess.STDOUT,
                check=False
            )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running comprehensive tests: {str(e)}")
        return False


def generate_test_summary(unit_success, mock_success, integration_success, comprehensive_success):
    """Generate a summary of all test results"""
    print("\n=== Generating Test Summary ===")
    
    summary_file = f"{TEST_REPORT_DIR}/test_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("VoidLink Test Summary\n")
        f.write("====================\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Test Results:\n")
        f.write(f"- Unit Tests: {'PASSED' if unit_success else 'FAILED'}\n")
        f.write(f"- Mock Tests: {'PASSED' if mock_success else 'FAILED'}\n")
        f.write(f"- Integration Tests: {'PASSED' if integration_success else 'FAILED'}\n")
        f.write(f"- Comprehensive Tests: {'PASSED' if comprehensive_success else 'FAILED'}\n\n")
        
        overall_success = unit_success and mock_success and integration_success and comprehensive_success
        f.write(f"Overall Result: {'PASSED' if overall_success else 'FAILED'}\n")
    
    print(f"Test summary generated in {summary_file}")
    return overall_success


def main():
    """Main function to run all tests"""
    parser = argparse.ArgumentParser(description="Run VoidLink tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--mock", action="store_true", help="Run only mock tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--comprehensive", action="store_true", help="Run only comprehensive tests")
    args = parser.parse_args()
    
    # If no specific test type is specified, run all tests
    run_all = not (args.unit or args.mock or args.integration or args.comprehensive)
    
    # Set up the test environment
    setup_environment()
    
    # Run the specified tests
    unit_success = True
    mock_success = True
    integration_success = True
    comprehensive_success = True
    
    if args.unit or run_all:
        unit_success = run_unit_tests()
    
    if args.mock or run_all:
        mock_success = run_mock_tests()
    
    if args.integration or run_all:
        integration_success = run_integration_tests()
    
    if args.comprehensive or run_all:
        comprehensive_success = run_comprehensive_tests()
    
    # Generate test summary
    overall_success = generate_test_summary(
        unit_success, mock_success, integration_success, comprehensive_success)
    
    # Print final result
    if overall_success:
        print("\n=== All tests passed! ===")
        return 0
    else:
        print("\n=== Some tests failed. See test summary for details. ===")
        return 1


if __name__ == "__main__":
    sys.exit(main())