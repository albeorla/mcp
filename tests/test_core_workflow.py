#!/usr/bin/env python3
"""
Core workflow tests for the Aerith Admin MCP server.
These tests validate each step of the Manus-inspired 5-step workflow.
"""
import os
import json
import sys
import pytest
from pathlib import Path

# Import the functions we need for testing
from server import (
    create_instruction, 
    get_instruction, 
    create_task_plan, 
    gather_information, 
    analyze_and_orchestrate, 
    execute_step, 
    generate_final_report,
    build_feature
)

# Import test fixture
from conftest import add_mcp_to_path


class TestCoreWorkflow:
    """Test class for the core 5-step workflow."""
    
    def test_create_instruction(self, tmpdir):
        """Test step 1: USER_INSTRUCTION - Creating a new instruction."""
        # Set up test environment
        os.chdir(tmpdir)
        os.makedirs(os.path.join(tmpdir, ".aerith", "instructions"), exist_ok=True)
        
        # Create a new instruction
        result = create_instruction(
            title="Add dark mode toggle",
            description="Implement a dark mode toggle component for the dashboard",
            goal="Create a reusable dark mode toggle button",
            priority="medium"
        )
        
        # Verify the response
        assert result["success"] is True
        assert "instruction_id" in result
        assert result["instruction"]["title"] == "Add dark mode toggle"
        assert result["instruction"]["workflow_step"] == "USER_INSTRUCTION"
        
        # Verify the file was created
        instruction_path = os.path.join(".aerith", "instructions", f"{result['instruction_id']}.json")
        assert os.path.exists(instruction_path)
        
        # Verify get_instruction works
        get_result = get_instruction(result["instruction_id"])
        assert get_result["success"] is True
        assert get_result["instruction"]["id"] == result["instruction_id"]
    
    def test_create_task_plan(self, tmpdir):
        """Test step 2: TASK_PLANNING - Breaking down an instruction into subtasks."""
        # Set up test environment
        os.chdir(tmpdir)
        os.makedirs(os.path.join(tmpdir, ".aerith", "instructions"), exist_ok=True)
        
        # First create an instruction
        instruction_result = create_instruction(
            title="Add user profile page",
            description="Create a user profile page with editable fields",
            goal="Allow users to view and edit their profile information",
            priority="high"
        )
        
        instruction_id = instruction_result["instruction_id"]
        
        # Create a task plan
        subtasks = [
            {
                "id": "st-1",
                "title": "Create profile component",
                "description": "Build the main profile component structure",
                "complexity": 3
            },
            {
                "id": "st-2",
                "title": "Implement edit form",
                "description": "Create form for editing user information",
                "complexity": 2,
                "dependencies": ["st-1"]
            },
            {
                "id": "st-3",
                "title": "Add API integration",
                "description": "Connect to backend API for saving profile data",
                "complexity": 4,
                "dependencies": ["st-2"]
            }
        ]
        
        result = create_task_plan(instruction_id, subtasks)
        
        # Verify the response
        assert result["success"] is True
        assert "task_plan" in result["instruction"]
        assert len(result["instruction"]["task_plan"]["subtasks"]) == 3
        assert result["instruction"]["workflow_step"] == "TASK_PLANNING"
        assert result["instruction"]["task_plan"]["has_dependencies"] is True
        
        # Verify the changes in the stored instruction
        get_result = get_instruction(instruction_id)
        assert get_result["instruction"]["status"] == "planned"
    
    def test_gather_information(self, tmpdir):
        """Test step 3: INFORMATION_GATHERING - Collecting information from various sources."""
        # Set up test environment
        os.chdir(tmpdir)
        os.makedirs(os.path.join(tmpdir, ".aerith", "instructions"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, "src", "components"), exist_ok=True)
        
        # Create a simple component for testing
        with open(os.path.join(tmpdir, "src", "components", "Button.tsx"), "w") as f:
            f.write("""
import React from 'react';

interface ButtonProps {
    text: string;
    onClick?: () => void;
}

const Button: React.FC<ButtonProps> = ({ text, onClick }) => {
    return (
        <button onClick={onClick} className="btn">
            {text}
        </button>
    );
};

export default Button;
            """)
        
        # First create an instruction and task plan
        instruction_result = create_instruction(
            title="Update button component",
            description="Update the Button component to support different sizes",
            goal="Enhance Button component with size variants",
            priority="medium"
        )
        
        instruction_id = instruction_result["instruction_id"]
        
        # Create a basic task plan
        subtasks = [
            {
                "title": "Analyze current Button implementation",
                "description": "Review existing Button component code",
                "complexity": 1
            },
            {
                "title": "Add size property",
                "description": "Implement size property and CSS classes",
                "complexity": 2
            }
        ]
        
        create_task_plan(instruction_id, subtasks)
        
        # Define information sources
        sources = [
            {
                "type": "file",
                "path": os.path.join(tmpdir, "src", "components", "Button.tsx"),
                "description": "Current Button component implementation"
            },
            {
                "type": "directory",
                "path": os.path.join(tmpdir, "src", "components"),
                "description": "List of existing components"
            }
        ]
        
        # Gather information
        result = gather_information(instruction_id, sources)
        
        # Verify the response
        assert result["success"] is True
        assert "gathered_information" in result["instruction"]
        assert len(result["instruction"]["gathered_information"]["sources"]) == 2
        assert result["instruction"]["workflow_step"] == "INFORMATION_GATHERING"
        
        # Verify source content was collected
        button_file_info = result["instruction"]["gathered_information"]["sources"][0]
        assert button_file_info["success"] is True
        assert "interface ButtonProps" in button_file_info["content"]
    
    def test_analyze_and_orchestrate(self, tmpdir):
        """Test step 4: ANALYSIS_AND_ORCHESTRATION - Analyzing information and creating an execution plan."""
        # Set up test environment
        os.chdir(tmpdir)
        os.makedirs(os.path.join(tmpdir, ".aerith", "instructions"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, "src", "components"), exist_ok=True)
        
        # Set up an instruction with gathered information
        instruction_result = create_instruction(
            title="Add tooltip component",
            description="Create a reusable tooltip component",
            goal="Implement a tooltip that can be attached to any element",
            priority="medium"
        )
        
        instruction_id = instruction_result["instruction_id"]
        
        # Create a task plan
        subtasks = [{"title": "Design tooltip API", "complexity": 2}]
        create_task_plan(instruction_id, subtasks)
        
        # Gather some information
        sources = [{"type": "directory", "path": os.path.join(tmpdir, "src", "components")}]
        gather_information(instruction_id, sources)
        
        # Define analysis and execution plan
        analysis = {
            "findings": [
                "No existing tooltip implementation found",
                "Button component provides a good pattern to follow"
            ],
            "recommendations": [
                "Create a new Tooltip.tsx component",
                "Use React portals for proper positioning"
            ],
            "decision_points": [
                {"question": "Should tooltip support HTML content?", "decision": "Yes"}
            ]
        }
        
        execution_plan = [
            {
                "id": "step-1",
                "title": "Create Tooltip component file",
                "type": "file_creation",
                "description": "Create the initial Tooltip component file"
            },
            {
                "id": "step-2",
                "title": "Create tooltip positioning logic",
                "type": "file_modification",
                "description": "Add positioning logic to the tooltip component"
            }
        ]
        
        # Analyze and orchestrate
        result = analyze_and_orchestrate(instruction_id, analysis, execution_plan)
        
        # Verify the response
        assert result["success"] is True
        assert "analysis" in result["instruction"]
        assert "execution_plan" in result["instruction"]
        assert len(result["instruction"]["execution_plan"]["steps"]) == 2
        assert result["instruction"]["workflow_step"] == "ANALYSIS_AND_ORCHESTRATION"
    
    def test_execute_step(self, tmpdir):
        """Test step 5: RESULT_SYNTHESIS - Executing steps and generating reports."""
        # Set up test environment
        os.chdir(tmpdir)
        os.makedirs(os.path.join(tmpdir, ".aerith", "instructions"), exist_ok=True)
        
        # Set up an instruction with an execution plan
        instruction_result = create_instruction(
            title="Add README section",
            description="Add a new section to the README file",
            goal="Document the new tooltip component",
            priority="low"
        )
        
        instruction_id = instruction_result["instruction_id"]
        
        # Create a basic task plan
        subtasks = [{"title": "Write documentation", "complexity": 1}]
        create_task_plan(instruction_id, subtasks)
        
        # Skip information gathering for simplicity
        sources = []
        gather_information(instruction_id, sources)
        
        # Create an analysis and execution plan
        analysis = {"findings": ["README needs a new component section"]}
        
        # Create a temporary README for the test
        readme_path = os.path.join(tmpdir, "README.md")
        with open(readme_path, "w") as f:
            f.write("# Test Project\n\n## Components\n\n")
        
        execution_plan = [
            {
                "id": "step-1",
                "title": "Update README.md",
                "type": "file_modification",
                "description": "Add tooltip documentation to README"
            }
        ]
        
        analyze_and_orchestrate(instruction_id, analysis, execution_plan)
        
        # Execute the step with absolute path
        execution_details = {
            "file_path": readme_path,
            "content": "# Test Project\n\n## Components\n\n### Tooltip\n\nThe Tooltip component provides contextual information on hover."
        }
        
        result = execute_step(instruction_id, "step-1", execution_details)
        
        # Verify the response
        assert result["success"] is True
        assert result["result"]["success"] is True
        assert len(result["result"]["artifacts"]) == 1
        assert result["result"]["artifacts"][0]["action"] == "modified"
        
        # Verify file was actually modified
        with open(readme_path, "r") as f:
            content = f.read()
            assert "### Tooltip" in content
    
    def test_generate_final_report(self, tmpdir):
        """Test the final report generation for a completed instruction."""
        # Set up test environment
        os.chdir(tmpdir)
        os.makedirs(os.path.join(tmpdir, ".aerith", "instructions"), exist_ok=True)
        
        # Set up a completed instruction
        instruction_result = create_instruction(
            title="Add simple test feature",
            description="Add a test feature for report generation",
            goal="Test report generation",
            priority="low"
        )
        
        instruction_id = instruction_result["instruction_id"]
        
        # Create a basic task plan
        subtasks = [{"title": "Test task", "complexity": 1}]
        create_task_plan(instruction_id, subtasks)
        
        # Skip information gathering for simplicity
        sources = []
        gather_information(instruction_id, sources)
        
        # Create an analysis and execution plan
        analysis = {"findings": ["Test finding"]}
        execution_plan = [
            {
                "id": "step-1",
                "title": "Test step",
                "type": "file_creation",
                "description": "Create a test file"
            }
        ]
        
        analyze_and_orchestrate(instruction_id, analysis, execution_plan)
        
        # Execute the step
        execution_details = {
            "file_path": os.path.join(tmpdir, "test-file.txt"),
            "content": "This is a test file"
        }
        
        execute_step(instruction_id, "step-1", execution_details)
        
        # Generate final report
        result = generate_final_report(instruction_id, include_details=True)
        
        # Verify the response
        assert result["success"] is True
        assert "final_report" in result["instruction"]
        assert result["instruction"]["status"] == "completed"
        assert "artifacts" in result["report"]["summary"]
        assert "details" in result["report"]
    
    def test_build_feature_high_level(self, tmpdir):
        """Test the high-level build_feature function."""
        # Set up test environment
        os.chdir(tmpdir)
        os.makedirs(os.path.join(tmpdir, ".aerith", "instructions"), exist_ok=True)
        
        # Use the build_feature high-level function
        result = build_feature(
            title="Test feature", 
            description="Test the build_feature function",
            goal="Validate high-level orchestration",
            priority="medium"
        )
        
        # Verify the response
        assert result["success"] is True
        assert "instruction_id" in result
        assert "next_steps" in result
        assert len(result["next_steps"]) == 5  # Should suggest all 5 workflow steps 