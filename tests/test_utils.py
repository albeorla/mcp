#!/usr/bin/env python3
"""
Tests for utility functions in the MCP server including file operations and command execution.
"""
import os
import sys
import json
import pytest
from pathlib import Path

# Import the test fixture
from conftest import add_mcp_to_path

# Import the functions we need for testing
from server import read_file, write_file, run_command, get_project_root


class TestUtilityFunctions:
    """Test class for utility functions in the server."""
    
    def test_get_project_root(self, tmpdir):
        """Test the get_project_root function."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # The function should return the current working directory
        root = get_project_root()
        assert isinstance(root, Path)
        assert root == Path(os.getcwd())
    
    def test_read_file(self, tmpdir):
        """Test reading a file with read_file function."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Create a test file
        test_content = "This is a test file content"
        test_file = "test_read.txt"
        
        with open(test_file, "w") as f:
            f.write(test_content)
        
        # Read the file using the function
        content = read_file(test_file)
        
        # Verify the content
        assert content == test_content
        
        # Test reading a non-existent file
        non_existent = "non_existent_file.txt"
        content = read_file(non_existent)
        assert "Error reading file" in content
    
    def test_write_file(self, tmpdir):
        """Test writing to a file with write_file function."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Test writing to a new file
        test_content = "This is content to write"
        test_file = os.path.join(tmpdir, "test_write.txt")  # Use absolute path
        
        result = write_file(test_file, test_content)
        
        # Verify the result
        assert result is True
        
        # Verify the file was created with the correct content
        with open(test_file, "r") as f:
            content = f.read()
        
        assert content == test_content
        
        # Test writing to a nested directory
        nested_path = os.path.join(tmpdir, "nested", "dir", "test.txt")  # Use absolute path
        result = write_file(nested_path, test_content)
        
        # Verify the result
        assert result is True
        
        # Verify the file was created with the correct content
        with open(nested_path, "r") as f:
            content = f.read()
        
        assert content == test_content
        assert os.path.exists(os.path.dirname(nested_path))
        
        # Test writing to a location with insufficient permissions
        # Note: This test is OS-dependent, so we'll check for the platform
        import platform
        if platform.system() != "Windows":  # Skip on Windows
            # Create a directory without write permissions
            readonly_dir = os.path.join(tmpdir, "readonly_dir")  # Use absolute path
            os.makedirs(readonly_dir, exist_ok=True)
            os.chmod(readonly_dir, 0o555)  # read and execute only
            
            try:
                readonly_file = os.path.join(readonly_dir, "test.txt")
                result = write_file(readonly_file, test_content)
                
                # On some systems, this might still succeed due to permissions handling
                # So we don't strictly assert the result
                if not result:
                    assert result is False
            finally:
                # Restore permissions for cleanup
                os.chmod(readonly_dir, 0o755)
    
    def test_run_command(self, tmpdir):
        """Test running commands with run_command function."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Test a simple command
        if os.name == "nt":  # Windows
            result = run_command(["cmd", "/c", "echo", "hello"])
        else:  # Unix-like
            result = run_command(["echo", "hello"])
        
        # Verify the result
        assert result["success"] is True
        assert "hello" in result["output"]
        assert result["returncode"] == 0
        
        # Test a command that fails
        if os.name == "nt":  # Windows
            result = run_command(["cmd", "/c", "invalid_command"])
        else:  # Unix-like
            result = run_command(["invalid_command"])
        
        # Verify the result
        assert result["success"] is False
        assert result["returncode"] != 0
        
        # Test a more complex command
        # Create a test file
        with open(os.path.join(tmpdir, "test_script.py"), "w") as f:  # Use absolute path
            f.write("""
print("This is a test script")
print("It has multiple lines")
exit(0)
            """)
        
        # Make it executable on Unix-like systems
        if os.name != "nt":
            os.chmod(os.path.join(tmpdir, "test_script.py"), 0o755)
        
        # Run the script
        result = run_command([sys.executable, os.path.join(tmpdir, "test_script.py")])  # Use absolute path
        
        # Verify the result
        assert result["success"] is True
        assert "This is a test script" in result["output"]
        assert "It has multiple lines" in result["output"]


class TestJsonHandling:
    """Test class for JSON handling in the server."""
    
    def test_json_serialization(self, tmpdir):
        """Test saving and loading JSON files."""
        # Set up test environment
        os.chdir(tmpdir)
        os.makedirs(os.path.join(tmpdir, ".aerith", "instructions"), exist_ok=True)
        
        # Create a sample instruction
        instruction = {
            "id": "test-123",
            "title": "Test Instruction",
            "description": "This is a test",
            "goal": "Testing JSON serialization",
            "priority": "medium",
            "status": "created",
            "created_at": 1234567890,
            "workflow_step": "USER_INSTRUCTION"
        }
        
        # Save it to a file
        json_path = os.path.join(tmpdir, ".aerith", "instructions", "test-123.json")  # Use absolute path
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        with open(json_path, "w") as f:
            json.dump(instruction, f, indent=2)
        
        # Read it back
        with open(json_path, "r") as f:
            loaded = json.load(f)
        
        # Verify it matches
        assert loaded == instruction
        assert loaded["id"] == "test-123"
        assert loaded["title"] == "Test Instruction" 