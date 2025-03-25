#!/usr/bin/env python3
"""
Test runner script for the Aerith Admin MCP server.
This script handles test discovery and execution with appropriate options.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"

def find_venv():
    """Find the virtual environment to use."""
    venv_candidates = [
        PROJECT_ROOT / "mcp-venv",
        PROJECT_ROOT / "venv",
        PROJECT_ROOT.parent / "venv",
    ]
    
    for venv_path in venv_candidates:
        if venv_path.exists():
            # Check for the Python executable
            if os.name == 'nt':  # Windows
                python_path = venv_path / "Scripts" / "python.exe"
            else:  # Unix-like
                python_path = venv_path / "bin" / "python"
            
            if python_path.exists():
                return python_path
    
    # If no venv is found, use the current Python interpreter
    return sys.executable

def main():
    """Execute tests based on command line arguments."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Run MCP server tests"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Increase verbosity"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Generate coverage report"
    )
    parser.add_argument(
        "--browser", 
        action="store_true", 
        help="Include browser automation tests"
    )
    parser.add_argument(
        "--html", 
        action="store_true", 
        help="Generate HTML test report"
    )
    parser.add_argument(
        "--slow", 
        action="store_true", 
        help="Include slow tests"
    )
    parser.add_argument(
        "pattern", 
        nargs="?", 
        default=None, 
        help="Pattern to match test files (e.g. 'test_core' to run only core tests)"
    )
    
    args = parser.parse_args()
    
    # Find the Python interpreter to use
    python_path = find_venv()
    print(f"Using Python interpreter: {python_path}")
    
    # We need to run pytest as a module using python -m pytest
    # This ensures we're using the right pytest from the virtual environment
    pytest_cmd = [str(python_path), "-m", "pytest"]
    
    # Add verbose flag if requested
    if args.verbose:
        pytest_cmd.append("-v")
    
    # Add coverage if requested
    if args.coverage:
        pytest_cmd.extend(["--cov=server", "--cov-report=term", "--cov-report=html"])
    
    # Add HTML report if requested
    if args.html:
        pytest_cmd.append("--html=test-report.html")
    
    # Set up test markers based on options
    markers = []
    if not args.browser:
        markers.append("not browser")
    if not args.slow:
        markers.append("not slow")
    
    if markers:
        marker_expr = " and ".join(markers)
        pytest_cmd.extend(["-m", marker_expr])
    
    # Add the test pattern - ensure all paths are converted to strings
    tests_dir_str = str(TESTS_DIR)
    
    # Add the tests directory
    pytest_cmd.append(tests_dir_str)
    
    # Add pattern filter if specified
    if args.pattern:
        pytest_cmd.extend(["-k", args.pattern])
    
    # Print the command being run
    print(f"Running: {' '.join(pytest_cmd)}")
    
    # Run the tests and return the exit code
    result = subprocess.run(pytest_cmd)
    return result.returncode

if __name__ == "__main__":
    # Ensure we're running in the correct directory
    os.chdir(str(PROJECT_ROOT))
    
    # Set up environment variables for testing
    os.environ["PYTHONPATH"] = str(PROJECT_ROOT)
    
    # Run tests and exit with the appropriate code
    sys.exit(main()) 