#!/usr/bin/env python3
"""
Tests for resource access methods in the MCP server.
"""
import os
import sys
import json
import pytest
from pathlib import Path

# Import the test fixture
from conftest import add_mcp_to_path

# Import the functions we need for testing
from server import get_file, get_project_structure, get_instructions, create_instruction


class TestResourceFunctions:
    """Test class for resource access functions in the server."""
    
    def test_get_file_resource(self, tmpdir):
        """Test the get_file resource function."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Create a test file
        test_content = "This is a test resource file"
        test_file = "test_resource.txt"
        
        with open(test_file, "w") as f:
            f.write(test_content)
        
        # Get the file using the resource function
        content = get_file(test_file)
        
        # Verify the content
        assert content == test_content
        
        # Test getting a non-existent file
        non_existent = "non_existent_resource.txt"
        content = get_file(non_existent)
        assert f"File not found: {non_existent}" == content
    
    def test_get_project_structure_resource(self, tmpdir):
        """Test the get_project_structure resource function."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Create a simple project structure for testing
        os.makedirs(os.path.join("src", "components"), exist_ok=True)
        os.makedirs(os.path.join("src", "utils"), exist_ok=True)
        os.makedirs(os.path.join("public", "assets"), exist_ok=True)
        
        # Create some test files
        with open(os.path.join("src", "components", "Button.tsx"), "w") as f:
            f.write("// Button component")
        
        with open(os.path.join("src", "utils", "helpers.js"), "w") as f:
            f.write("// Helper functions")
        
        with open(os.path.join("public", "assets", "logo.svg"), "w") as f:
            f.write("<svg></svg>")
        
        # Get the project structure
        structure = get_project_structure()
        
        # Verify the structure contains the expected directories and files
        assert "src" in structure
        assert structure["src"]["type"] == "directory"
        assert "components" in structure["src"]
        assert "utils" in structure["src"]
        
        assert "public" in structure
        assert structure["public"]["type"] == "directory"
        assert "assets" in structure["public"]
        
        # Verify file detection
        assert "Button.tsx" in structure["src"]["components"]
        assert structure["src"]["components"]["Button.tsx"]["type"] == "file"
        
        assert "helpers.js" in structure["src"]["utils"]
        assert structure["src"]["utils"]["helpers.js"]["type"] == "file"
        
        assert "logo.svg" in structure["public"]["assets"]
        assert structure["public"]["assets"]["logo.svg"]["type"] == "file"
    
    def test_get_instructions_resource(self, tmpdir):
        """Test the get_instructions resource function."""
        # Set up test environment
        os.chdir(tmpdir)
        os.makedirs(os.path.join(tmpdir, ".aerith", "instructions"), exist_ok=True)
        
        # Create a few test instructions
        instruction1 = create_instruction(
            title="Test Instruction 1",
            description="Test description 1",
            goal="Test goal 1",
            priority="high"
        )
        
        instruction2 = create_instruction(
            title="Test Instruction 2",
            description="Test description 2",
            goal="Test goal 2",
            priority="medium"
        )
        
        instruction3 = create_instruction(
            title="Test Instruction 3",
            description="Test description 3",
            goal="Test goal 3",
            priority="low"
        )
        
        # Get all instructions
        instructions = get_instructions()
        
        # Verify the instructions were retrieved
        assert len(instructions) >= 3  # There might be more from previous tests
        
        # Check if our instructions are in the list
        instruction_ids = [instr["id"] for instr in instructions]
        assert instruction1["instruction_id"] in instruction_ids
        assert instruction2["instruction_id"] in instruction_ids
        assert instruction3["instruction_id"] in instruction_ids
        
        # Verify instruction content
        for instr in instructions:
            if instr["id"] == instruction1["instruction_id"]:
                assert instr["title"] == "Test Instruction 1"
                assert instr["priority"] == "high"
            elif instr["id"] == instruction2["instruction_id"]:
                assert instr["title"] == "Test Instruction 2"
                assert instr["priority"] == "medium"
            elif instr["id"] == instruction3["instruction_id"]:
                assert instr["title"] == "Test Instruction 3"
                assert instr["priority"] == "low"
    
    def test_resource_error_handling(self, tmpdir):
        """Test error handling in resource functions."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Test with an invalid file path - must use mock to avoid TypeError
        with pytest.raises(TypeError):
            # This will raise TypeError as None can't be joined with a path
            # We're testing that this properly bubbles up
            get_file(None)
            
        # Use an absolute path to a non-existent file
        non_existent_file = os.path.join(tmpdir, "does_not_exist.txt")
        content = get_file(non_existent_file)
        assert f"File not found: {non_existent_file}" in content
        
        # Test with a directory instead of a file
        dir_path = os.path.join(tmpdir, "test_dir")
        os.makedirs(dir_path, exist_ok=True)
        content = get_file(dir_path)
        assert "Error reading file" in content
        
        # Test with a non-existent instructions directory
        # First, make sure we're in the tmpdir 
        # and don't accidentally remove real instruction files
        assert os.getcwd() == str(tmpdir)
        
        # Create a clean .aerith directory with no instructions
        import shutil
        if os.path.exists(os.path.join(".aerith", "instructions")):
            shutil.rmtree(os.path.join(".aerith", "instructions"))
        
        # Now test getting instructions from empty directory
        instructions = get_instructions()
        assert instructions == [] 