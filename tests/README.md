# SWE-Flow Tests

This directory contains unit tests for the SWE-Flow project.

## Running Tests

To run the tests, you need to have pytest installed. You can install it along with other development dependencies using:

```bash
pip install -r requirements-dev.txt
```

Then, you can run the tests using:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=sweflow

# Run a specific test file
pytest tests/utils/test_token_utils.py

# Run a specific test
pytest tests/utils/test_token_utils.py::TestTokenCounter::test_count_tokens_of_string
```

## Test Structure

The test directory structure mirrors the project structure:

- `tests/utils/`: Tests for utility modules in `sweflow/utils/`
- `tests/extensions/python/`: Tests for Python extension modules in `sweflow/extensions/python/`

## Adding New Tests

When adding new tests:

1. Create a new test file with the name pattern `test_*.py`
2. Create test classes with the name pattern `Test*`
3. Create test methods with the name pattern `test_*`
4. Use pytest fixtures for setup and teardown
5. Add appropriate assertions to verify the behavior of the code

## Test Coverage

To generate a test coverage report:

```bash
pytest --cov=sweflow --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov` directory.
