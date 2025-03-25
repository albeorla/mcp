# Aerith Admin MCP Server

The Aerith Admin MCP (Model, Controller, Presenter) server implements a MANUS-inspired development workflow for RBAC dashboard applications with browser automation capabilities. This server is designed to be run locally and accessed by Cursor IDE's MCP integration.

## Overview

This server provides a structured approach to development through a 5-step workflow:

1. **USER_INSTRUCTION** - Define development tasks with clear goals
2. **TASK_PLANNING** - Break down tasks into specific subtasks
3. **INFORMATION_GATHERING** - Collect relevant information from various sources
4. **ANALYSIS_AND_ORCHESTRATION** - Analyze information and create execution plans
5. **RESULT_SYNTHESIS** - Execute steps and generate comprehensive reports

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/aerith-admin.git
cd aerith-admin/mcp

# Run the installation script (creates virtual environment and installs dependencies)
./bin/install.sh

# Activate the virtual environment
source bin/activate_venv.sh
```

## Usage

The server can run in two modes:

### HTTP Mode (Default)

```bash
python server.py --port 8090
```

This starts the server on port 8090 (or specify a different port). The server provides a REST API and Server-Sent Events (SSE) for real-time updates.

### STDIO Mode

```bash
python server.py --stdio
```

This mode is designed for integration with other tools, communicating through standard input/output using JSON-RPC protocol.

## Cursor IDE Integration

This MCP server is specifically designed to work with Cursor IDE. Cursor can connect to the server to utilize its capabilities directly from the editor.

### Setup Cursor Integration:

1. Make sure the MCP server is running in HTTP mode: `python server.py --port 8090`
2. Cursor automatically detects the MCP server using the `.cursor/mcp.json` configuration:
   ```json
   {
     "mcpServers": {
       "aerith-admin-mcp": {
         "url": "http://localhost:8090/sse"
       }
     }
   }
   ```
3. Open the Aerith Admin project in Cursor IDE
4. Use the Cursor MCP integration UI to interact with the server

## Project Structure

```
mcp/
├── bin/                    # Executable scripts
│   ├── activate_venv.sh    # Script to activate virtual environment
│   ├── install.sh          # Installation script
│   ├── check_env.py        # Environment validation script
│   └── run_tests.py        # Test runner script
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── server.py               # Main MCP server implementation
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest configuration and fixtures
│   ├── README.md           # Testing documentation
│   ├── test_browser_automation.py # Browser automation tests
│   ├── test_core_workflow.py      # Workflow step tests
│   ├── test_integration.py        # End-to-end integration tests
│   ├── test_resources.py          # Resource access tests
│   ├── test_server_modes.py       # Server operation mode tests
│   └── test_utils.py              # Utility function tests
└── venv/                   # Virtual environment (created by install.sh)
```

## Development Setup

This project uses a dedicated virtual environment for development:

```bash
# Run the installation script
./bin/install.sh

# Or manually set up the environment
python -m venv venv
source bin/activate_venv.sh
pip install -r requirements-dev.txt

# For browser automation testing
python -m playwright install
```

## Testing

Tests are written using pytest and located in the `tests/` directory.

### Running Tests

Use the provided script to run tests:

```bash
# Run all tests except browser and slow tests
./bin/run_tests.py -v

# Run with coverage report
./bin/run_tests.py --coverage

# Include browser automation tests
./bin/run_tests.py --browser

# Include slow integration tests
./bin/run_tests.py --slow

# Run specific test files or patterns
./bin/run_tests.py test_core_workflow
```

## Environment Variables

- `MCP_DEBUG=true` - Enable debug logging (set automatically by activate_venv.sh)
- Additional environment variables can be configured as needed

## API Documentation

### Tools

The server provides the following tools:

#### Instruction Management

- `create_instruction(title, description, goal, priority)` - Create a new development instruction
- `get_instruction(instruction_id)` - Retrieve an existing instruction
- `build_feature(title, description, goal, priority)` - High-level orchestration to build a complete feature

#### Workflow Steps

- `create_task_plan(instruction_id, subtasks)` - Break down an instruction into specific subtasks
- `gather_information(instruction_id, sources)` - Gather information from various sources
- `analyze_and_orchestrate(instruction_id, analysis, execution_plan)` - Analyze and create an execution plan
- `execute_step(instruction_id, step_id, execution_details)` - Execute a specific step in the plan
- `generate_final_report(instruction_id, include_details)` - Generate a final report

#### Browser Automation

- `run_browser_agent(goal)` - Run a browser-use agent to achieve a specified goal

#### Filesystem Tools

- `tree_directory(directory_path, max_depth, show_files, show_hidden, pattern, exclude_common, custom_excludes)` - Generate a tree representation of a directory structure similar to the Unix 'tree' command

#### Git Tools

- `git_status(detailed)` - Show the working tree status
- `git_log(count, show_stats, path, author, since, until)` - Show commit logs
- `git_diff(file_path, staged, commit, compare_with)` - Show changes between commits or working tree
- `git_branch(create, delete, remote, branch_name, base_branch)` - List, create, or delete branches
- `git_checkout(branch_name, create, force)` - Switch branches or restore working tree files
- `git_commit(message, all_changes, amend)` - Record changes to the repository
- `git_push(remote, branch, force, tags)` - Update remote refs along with associated objects
- `git_pull(remote, branch, rebase)` - Fetch from and integrate with another repository
- `git_add(paths)` - Add file contents to the staging area

### Resources

The server provides these resources:

- `file://{path}` - Get file contents by path
- `project://structure` - Get the project structure as a dictionary
- `instructions://list` - Get list of all instructions

## Data Storage

All instructions and related data are stored in JSON files in the `.aerith/instructions` directory.

## Logging

Logs are stored in `.aerith/logs/mcp_server.log` and also output to stderr. When `MCP_DEBUG=true` is set (default in the development environment), detailed debug logging is enabled.

## License

[MIT License](LICENSE)
