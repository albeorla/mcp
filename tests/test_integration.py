#!/usr/bin/env python3
"""
Integration test for the Aerith Admin MCP server implementing the Manus-inspired workflow.
This test validates the complete development flow from instruction creation to final report.
"""
import os
import json
import shutil
import pytest
import tempfile
from pathlib import Path

# Import the MCP server components
from server import FastMCP, create_instruction, get_instruction, create_task_plan, \
    gather_information, analyze_and_orchestrate, execute_step, generate_final_report


@pytest.fixture
def test_environment():
    """Set up a temporary test environment."""
    # Create temp directory for the test
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    
    # Create .aerith directory structure
    os.makedirs(os.path.join(test_dir, ".aerith", "instructions"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, ".aerith", "logs"), exist_ok=True)
    
    # Create a basic file structure for testing
    os.makedirs(os.path.join(test_dir, "src", "components"), exist_ok=True)
    
    # Create a simple component for testing
    with open(os.path.join(test_dir, "src", "components", "Button.tsx"), "w") as f:
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
    
    # Return working directory and test directory for use in tests
    yield {"test_dir": test_dir}
    
    # Cleanup after test
    os.chdir(original_cwd)
    shutil.rmtree(test_dir)


def test_complete_workflow(test_environment):
    """Test the complete MCP workflow from instruction to final report."""
    test_dir = test_environment["test_dir"]
    
    # STEP 1: USER_INSTRUCTION - Create a new instruction
    create_result = create_instruction(
        title="Add Hover Effect to Button Component",
        description="Enhance the Button component to have a hover effect that changes color",
        goal="Improve user experience with visual feedback",
        priority="medium"
    )
    
    assert create_result["success"] is True
    instruction_id = create_result["instruction_id"]
    
    # Verify instruction was created and saved
    instruction_path = os.path.join(test_dir, ".aerith", "instructions", f"{instruction_id}.json")
    assert os.path.exists(instruction_path)
    
    # Verify get_instruction works
    get_result = get_instruction(instruction_id)
    assert get_result["success"] is True
    assert get_result["instruction"]["title"] == "Add Hover Effect to Button Component"
    assert get_result["instruction"]["workflow_step"] == "USER_INSTRUCTION"
    
    # STEP 2: TASK_PLANNING - Break down into subtasks
    plan_result = create_task_plan(
        instruction_id=instruction_id,
        subtasks=[
            {
                "id": "st-1",
                "title": "Analyze current Button component",
                "description": "Review the existing Button component code",
                "complexity": 1
            },
            {
                "id": "st-2",
                "title": "Implement hover effect styles",
                "description": "Add CSS styles for hover effect",
                "complexity": 2,
                "dependencies": ["st-1"]
            },
            {
                "id": "st-3",
                "title": "Test the hover effect",
                "description": "Verify the hover effect works correctly",
                "complexity": 1,
                "dependencies": ["st-2"]
            }
        ]
    )
    
    assert plan_result["success"] is True
    assert len(plan_result["instruction"]["task_plan"]["subtasks"]) == 3
    assert plan_result["instruction"]["workflow_step"] == "TASK_PLANNING"
    
    # STEP 3: INFORMATION_GATHERING - Gather relevant information
    gather_result = gather_information(
        instruction_id=instruction_id,
        sources=[
            {
                "type": "file",
                "path": "src/components/Button.tsx"
            },
            {
                "type": "search",
                "query": "className"
            }
        ]
    )
    
    assert gather_result["success"] is True
    assert gather_result["instruction"]["workflow_step"] == "INFORMATION_GATHERING"
    
    # STEP 4: ANALYSIS_AND_ORCHESTRATION - Analyze information and create execution plan
    analysis_result = analyze_and_orchestrate(
        instruction_id=instruction_id,
        analysis={
            "findings": [
                "Button component uses a 'btn' class for styling",
                "No hover effect is currently implemented"
            ],
            "recommendations": [
                "Add a CSS hover style for the btn class",
                "Consider using styled-components for more dynamic styling"
            ],
            "decision_points": [
                "Use inline CSS or external stylesheet"
            ]
        },
        execution_plan=[
            {
                "id": "step-1",
                "title": "Create CSS file for Button",
                "type": "file_creation",
                "description": "Create a CSS file for the Button component"
            },
            {
                "id": "step-2",
                "title": "Modify Button component",
                "type": "file_modification",
                "description": "Update Button component to import and use the CSS"
            }
        ]
    )
    
    assert analysis_result["success"] is True
    assert len(analysis_result["instruction"]["execution_plan"]["steps"]) == 2
    assert analysis_result["instruction"]["workflow_step"] == "ANALYSIS_AND_ORCHESTRATION"
    
    # STEP 5: RESULT_SYNTHESIS - Execute steps and generate report
    
    # Execute step 1: Create CSS file
    step1_result = execute_step(
        instruction_id=instruction_id,
        step_id="step-1",
        execution_details={
            "file_path": "src/components/Button.css",
            "content": """
.btn {
    padding: 8px 16px;
    border-radius: 4px;
    background-color: #3498db;
    color: white;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.btn:hover {
    background-color: #2980b9;
}
"""
        }
    )
    
    assert step1_result["success"] is True
    assert os.path.exists(os.path.join(test_dir, "src", "components", "Button.css"))
    
    # Execute step 2: Modify Button component
    step2_result = execute_step(
        instruction_id=instruction_id,
        step_id="step-2",
        execution_details={
            "file_path": "src/components/Button.tsx",
            "patches": [
                {
                    "type": "replace",
                    "old_text": "import React from 'react';",
                    "new_text": "import React from 'react';\nimport './Button.css';"
                }
            ]
        }
    )
    
    assert step2_result["success"] is True
    
    # Verify file was modified correctly
    with open(os.path.join(test_dir, "src", "components", "Button.tsx"), "r") as f:
        content = f.read()
        assert "import './Button.css';" in content
    
    # Generate final report
    report_result = generate_final_report(
        instruction_id=instruction_id,
        include_details=True
    )
    
    assert report_result["success"] is True
    assert report_result["instruction"]["status"] == "completed"
    assert "artifacts" in report_result["report"]["summary"]
    
    # Verify report contains all workflow steps
    assert "RESULT_SYNTHESIS" in report_result["report"]["workflow_steps_completed"]
    
    # Verify artifacts include the CSS file and modified component
    artifacts = report_result["report"]["summary"]["artifacts"]
    artifact_paths = [a["path"] for a in artifacts]
    assert "src/components/Button.css" in artifact_paths


def test_failed_execution(test_environment):
    """Test handling of errors in the workflow."""
    # Create instruction
    create_result = create_instruction(
        title="Test Error Handling",
        description="Test how the workflow handles errors",
        goal="Verify error resilience",
        priority="low"
    )
    
    instruction_id = create_result["instruction_id"]
    
    # Create task plan
    create_task_plan(
        instruction_id=instruction_id,
        subtasks=[
            {
                "title": "Test error handling",
                "description": "Execute a command that will fail",
                "complexity": 1
            }
        ]
    )
    
    # Create minimal information gathering
    gather_information(
        instruction_id=instruction_id,
        sources=[{"type": "directory", "path": "."}]
    )
    
    # Create execution plan with a step that will fail
    analyze_and_orchestrate(
        instruction_id=instruction_id,
        analysis={"findings": ["Test error handling"]},
        execution_plan=[
            {
                "id": "error-step",
                "title": "Execute invalid command",
                "type": "command_execution",
                "description": "Run a command that doesn't exist"
            }
        ]
    )
    
    # Execute step that will fail
    error_result = execute_step(
        instruction_id=instruction_id,
        step_id="error-step",
        execution_details={
            "command": "non_existent_command_xyz"
        }
    )
    
    # Verify the error is handled gracefully
    assert error_result["success"] is False
    assert "error" in error_result["result"]
    
    # Generate report even after failure
    report_result = generate_final_report(instruction_id=instruction_id)
    
    # Verify report reflects the failure
    assert report_result["success"] is True  # Report generation succeeds
    assert report_result["instruction"]["status"] in ["completed", "failed"] 