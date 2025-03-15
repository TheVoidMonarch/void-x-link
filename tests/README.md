# VoidLink Testing Infrastructure

This directory contains the testing infrastructure for the VoidLink project.

## Test Types

The VoidLink project uses several types of tests:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test the entire system from a user perspective
4. **Mock Tests**: Test components with dependencies mocked out

## Test Files

- `run_tests.py`: Main test runner for unit tests
- `test_authentication.py`: Unit tests for the authentication module
- `test_encryption.py`: Unit tests for the encryption module
- `test_file_security.py`: Unit tests for the file security module
- `test_file_transfer.py`: Unit tests for the file transfer module
- `test_resumable_transfer.py`: Unit tests for the resumable file transfer module
- `test_cases.json`: Test cases for manual and automated testing

## Running Tests

### Running Unit Tests

To run all unit tests:

```bash
python tests/run_tests.py
```

### Running All Tests

To run all tests (unit, integration, end-to-end, and mock tests):

```bash
python run_all_tests.py
```

### Running Specific Test Types

To run only specific types of tests:

```bash
python run_all_tests.py --unit      # Run only unit tests
python run_all_tests.py --mock      # Run only mock tests
python run_all_tests.py --integration  # Run only integration tests
python run_all_tests.py --comprehensive  # Run only comprehensive tests
```

### Using the Test Shell Script

For convenience, you can use the test shell script:

```bash
./test1.sh
```

This script will:
1. Check if you're in the virtual environment
2. Install test dependencies if needed
3. Run the comprehensive test runner

## Test Results

Test results are stored in the `test_results` directory:

- `unit_test_results.txt`: Results of unit tests
- `mock_test_results.txt`: Results of mock tests
- `integration_test_results.txt`: Results of integration tests
- `comprehensive_test_results.txt`: Results of comprehensive tests
- `test_summary.txt`: Summary of all test results

## Code Coverage

Code coverage reports are generated in the `test_results/coverage` directory. Open `index.html` in a web browser to view the coverage report.

## Adding New Tests

### Adding Unit Tests

1. Create a new file in the `tests` directory with the naming pattern `test_*.py`
2. Implement test cases using the `unittest` framework
3. Run the tests to verify they work correctly

### Adding Test Cases

To add new test cases for automated testing:

1. Edit the `test_cases.json` file
2. Add a new test case object with the required fields:
   - `id`: Unique identifier for the test case
   - `category`: Category of the test case
   - `name`: Name of the test case
   - `description`: Description of what the test case tests
   - `steps`: List of steps to execute
   - `expected_results`: List of expected results
   - `setup_commands`: List of commands to run before the test
   - `teardown_commands`: List of commands to run after the test

## Troubleshooting

If you encounter issues with the tests:

1. Make sure all dependencies are installed:
   ```bash
   pip install pytest pytest-cov coverage
   ```

2. Check that the server and client are properly configured

3. Verify that the database directories exist:
   ```bash
   mkdir -p database/files database/chat_history
   ```

4. Make sure all test scripts are executable:
   ```bash
   chmod +x test1.sh run_tests.sh run_test.py run_all_tests.py
   ```