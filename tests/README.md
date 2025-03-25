# Aerith Admin MCP Server Tests

This directory contains tests for the Aerith Admin MCP server implementing the Manus-inspired development workflow.

## Test Structure

The tests are organized by functionality:

- `test_browser_automation.py` - Tests for browser automation capabilities
- `test_core_workflow.py` - Tests for each step of the 5-step Manus workflow
- `test_integration.py` - End-to-end integration tests for the complete workflow
- `test_resources.py` - Tests for resource access methods
- `test_server_modes.py` - Tests for HTTP and STDIO server modes
- `test_utils.py` - Tests for utility functions like file operations

## Prerequisites

- Python 3.8 or higher
- Virtual environment with dependencies installed

## Running Tests

### Using the Test Runner Script

The simplest way to run tests is with the provided script:

```bash
# From the mcp directory
./bin/run_tests.py -v

# Run with coverage report
./bin/run_tests.py --coverage

# Include browser automation tests
./bin/run_tests.py --browser

# Include slow tests (actual server processes)
./bin/run_tests.py --slow

# Run specific test categories
./bin/run_tests.py test_core_workflow
```

### Manual Test Execution

If you prefer to run tests manually:

```bash
# Make sure you're in the activated virtual environment
source bin/activate_venv.sh

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_core_workflow.py -v

# Skip slow or browser tests
pytest tests/ -v -m "not slow and not browser"

# Generate coverage report
pytest tests/ --cov=server --cov-report=html
```

## Test Environment

Test fixtures are defined in `conftest.py` and include:

- `add_mcp_to_path` - Ensures MCP module is in the Python path
- `configure_logging` - Sets up logging for tests
- `mock_browser_context` - Provides a mock browser context for testing
- `mock_browser_agent` - Provides a mock browser agent for testing

Tests use `tmpdir` fixtures to create isolated test environments that are automatically cleaned up.

## What's Being Tested

### 1. Core Workflow
- Each step of the 5-step Manus workflow:
  - USER_INSTRUCTION - Creating development instructions
  - TASK_PLANNING - Breaking down tasks into subtasks
  - INFORMATION_GATHERING - Collecting relevant information
  - ANALYSIS_AND_ORCHESTRATION - Analyzing and creating execution plans
  - RESULT_SYNTHESIS - Executing steps and generating reports

### 2. Integration Tests
- End-to-end workflow validation
- Error handling and resilience
- File operation execution

### 3. Server Modes
- HTTP server mode
- STDIO server mode
- Signal handling for graceful shutdown

### 4. Resource Access
- File resource access
- Project structure exploration
- Instructions listing and management

### 5. Browser Automation
- Basic browser automation commands
- Error handling in browser automation
- Support for complex multi-step browser tasks

### 6. Utility Functions
- File operations (read/write)
- Command execution
- Project structure exploration
- JSON serialization

## Adding New Tests

Follow these guidelines when adding new tests:

1. Place tests in the appropriate file based on functionality
2. Use pytest fixtures for environment setup and teardown
3. Follow the AAA pattern: Arrange, Act, Assert
4. Use descriptive test and function names
5. Include docstrings explaining what the test verifies

Example:
```python
def test_something_specific(tmpdir):
    """Test that something specific works as expected."""
    # Arrange - Set up the test environment
    os.chdir(tmpdir)
    os.makedirs(os.path.join(tmpdir, ".aerith", "instructions"), exist_ok=True)
    
    # Act - Perform the action being tested
    result = some_function(params)
    
    # Assert - Verify the expected behavior
    assert result["success"] is True
    assert result["some_field"] == expected_value
```

## Test Markers

Custom markers are defined to categorize tests:

- `@pytest.mark.slow` - Tests that take a long time to run
- `@pytest.mark.browser` - Tests that require browser automation

These can be used to selectively run or skip certain test categories. 