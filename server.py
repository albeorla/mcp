#!/usr/bin/env python3
"""
MCP server for Aerith Admin implementing the Manus-inspired development flow,
with browser-use integration.
"""
import os
import json
import sys
import logging
import time
import signal
from typing import Dict, List, Any, Literal, Optional
from pathlib import Path

# Create log directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".aerith", "logs")
os.makedirs(log_dir, exist_ok=True)

# Setup logging - check for debug mode
log_level = logging.DEBUG if os.environ.get("MCP_DEBUG") == "true" else logging.INFO

# Create a log file in a standard location
log_file = os.path.join(log_dir, "mcp_server.log")

# Setup logging to both stderr and file
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stderr),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("aerith-mcp")

# Log initialization message with timestamp to help track starts/stops
logger.info(f"================ MCP SERVER STARTING {time.strftime('%Y-%m-%d %H:%M:%S')} ================")

# Log Python path at startup to help debug imports
logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Script location: {__file__}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Log file: {log_file}")

# Check if we're in stdio mode
use_stdio = "--stdio" in sys.argv
logger.info(f"Using stdio mode: {use_stdio}")

# Setup signal handlers for graceful shutdown
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    # Import MCP package - try different import paths
    try:
        from mcp.server import FastMCP
        logger.info("Successfully imported FastMCP from mcp.server")
    except ImportError:
        try:
            from mcp.fastmcp import FastMCP
            logger.info("Successfully imported FastMCP from mcp.fastmcp")
        except ImportError:
            # Try other potential locations
            from mcp import MCP as FastMCP
            logger.info("Successfully imported MCP as FastMCP from mcp")
except ImportError as e:
    logger.error(f"Failed to import FastMCP: {e}")
    logger.error("Make sure the MCP package is installed with: pip install mcp>=1.5.0")
    sys.exit(1)

# Log available methods on the MCP class
logger.info("Available methods in the FastMCP class:")
import inspect
for method_name in dir(FastMCP):
    if not method_name.startswith('_'):
        logger.info(f"  - {method_name}")

# Create MCP server with appropriate metadata
mcp = FastMCP(
    name="Aerith Admin",
    description="MCP server implementing the Manus-inspired development workflow for RBAC dashboard applications",
    version="1.0.0"
)

# Log available methods on the mcp instance
logger.info("Available methods on the mcp instance:")
for method_name in dir(mcp):
    if not method_name.startswith('_'):
        logger.info(f"  - {method_name}")

# Helper functions
def get_project_root() -> Path:
    """Get the root directory of the project."""
    return Path(os.getcwd())

def read_file(path: str) -> str:
    """Read file contents."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(path: str, content: str) -> bool:
    """Write content to a file."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing file: {str(e)}")
        return False

def run_command(cmd: List[str]) -> Dict[str, Any]:
    """Run a shell command and return the result."""
    import subprocess
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "returncode": -1
        }

# ==========================================
# STEP 1: USER_INSTRUCTION
# ==========================================

@mcp.tool()
def create_instruction(
    title: str,
    description: str,
    goal: str,
    priority: Literal["low", "medium", "high"] = "medium"
) -> Dict[str, Any]:
    """
    Create a new development instruction (Step 1 in the Manus workflow).
    
    Args:
        title: Brief title for the instruction
        description: Detailed description of what needs to be done
        goal: The specific goal or outcome to achieve
        priority: Instruction priority level
    
    Returns:
        Dict with instruction details and unique ID
    """
    logger.info(f"Creating instruction: {title}")
    
    import uuid
    
    instruction_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time())
    
    instruction = {
        "id": instruction_id,
        "title": title,
        "description": description,
        "goal": goal,
        "priority": priority,
        "status": "created",
        "created_at": timestamp,
        "workflow_step": "USER_INSTRUCTION"
    }
    
    # Save instruction to file
    instructions_dir = os.path.join(get_project_root(), ".aerith", "instructions")
    os.makedirs(instructions_dir, exist_ok=True)
    
    instruction_path = os.path.join(instructions_dir, f"{instruction_id}.json")
    with open(instruction_path, 'w') as f:
        json.dump(instruction, f, indent=2)
    
    return {
        "success": True,
        "instruction_id": instruction_id,
        "message": f"Instruction {instruction_id} created successfully",
        "instruction": instruction
    }

@mcp.tool()
def get_instruction(instruction_id: str) -> Dict[str, Any]:
    """
    Retrieve an existing instruction by ID.
    
    Args:
        instruction_id: The unique identifier for the instruction
    
    Returns:
        Dict with instruction details
    """
    logger.info(f"Getting instruction: {instruction_id}")
    
    instruction_path = os.path.join(get_project_root(), ".aerith", "instructions", f"{instruction_id}.json")
    
    if not os.path.exists(instruction_path):
        return {
            "success": False,
            "message": f"Instruction {instruction_id} not found"
        }
    
    try:
        with open(instruction_path, 'r') as f:
            instruction = json.load(f)
        
        return {
            "success": True,
            "instruction": instruction
        }
    except Exception as e:
        logger.error(f"Error getting instruction: {str(e)}")
        return {
            "success": False,
            "message": f"Error getting instruction: {str(e)}"
        }

# ==========================================
# STEP 2: TASK_PLANNING
# ==========================================

@mcp.tool()
def create_task_plan(
    instruction_id: str,
    subtasks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Break down an instruction into specific subtasks (Step 2 in the Manus workflow).
    
    Args:
        instruction_id: The unique identifier for the instruction
        subtasks: List of subtasks, each with title, description, and complexity
    
    Returns:
        Dict with updated instruction including task plan
    """
    logger.info(f"Creating task plan for instruction: {instruction_id}")
    
    result = get_instruction(instruction_id)
    if not result["success"]:
        return result
    
    instruction = result["instruction"]
    
    # Create task plan
    task_plan = {
        "subtasks": subtasks,
        "total_subtasks": len(subtasks),
        "created_at": int(time.time()),
        "estimated_complexity": sum(subtask.get("complexity", 1) for subtask in subtasks) / len(subtasks)
    }
    
    # Add subtask IDs if not provided
    for i, subtask in enumerate(task_plan["subtasks"]):
        if "id" not in subtask:
            subtask["id"] = f"st-{i+1}"
        if "status" not in subtask:
            subtask["status"] = "pending"
    
    # Add dependencies if provided
    if any("dependencies" in subtask for subtask in subtasks):
        task_plan["has_dependencies"] = True
    
    # Update instruction with task plan
    instruction["task_plan"] = task_plan
    instruction["status"] = "planned"
    instruction["workflow_step"] = "TASK_PLANNING"
    
    # Save updated instruction
    instruction_path = os.path.join(get_project_root(), ".aerith", "instructions", f"{instruction_id}.json")
    with open(instruction_path, 'w') as f:
        json.dump(instruction, f, indent=2)
    
    return {
        "success": True,
        "message": f"Task plan created for instruction {instruction_id}",
        "instruction": instruction
    }

# ==========================================
# STEP 3: INFORMATION_GATHERING
# ==========================================

@mcp.tool()
def gather_information(
    instruction_id: str,
    sources: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Gather information for an instruction from various sources (Step 3 in the Manus workflow).
    
    Args:
        instruction_id: The unique identifier for the instruction
        sources: List of information sources to gather from
    
    Returns:
        Dict with gathered information
    """
    logger.info(f"Gathering information for instruction: {instruction_id}")
    
    result = get_instruction(instruction_id)
    if not result["success"]:
        return result
    
    instruction = result["instruction"]
    
    # Initialize information gathering result
    gathered_info = []
    
    # Process each information source
    for source in sources:
        source_type = source.get("type")
        source_path = source.get("path", "")
        source_query = source.get("query", "")
        
        info = {
            "source_type": source_type,
            "source_path": source_path,
            "source_query": source_query,
            "content": None,
            "success": False,
            "error": None
        }
        
        try:
            if source_type == "file" and source_path:
                # Get information from a file
                content = read_file(source_path)
                info["content"] = content
                info["success"] = True
                
            elif source_type == "directory" and source_path:
                # List directory contents
                if os.path.exists(source_path) and os.path.isdir(source_path):
                    content = os.listdir(source_path)
                    info["content"] = content
                    info["success"] = True
                else:
                    info["error"] = f"Directory not found: {source_path}"
                
            elif source_type == "command" and source_query:
                # Run command to get information
                result = run_command(source_query.split())
                info["content"] = result["output"]
                info["success"] = result["success"]
                if not result["success"]:
                    info["error"] = result["error"]
                
            elif source_type == "search" and source_query:
                # Search for files containing the query
                search_result = []
                for root, _, files in os.walk(get_project_root()):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r') as f:
                                content = f.read()
                                if source_query in content:
                                    search_result.append({
                                        "path": file_path,
                                        "line_count": len(content.splitlines())
                                    })
                        except Exception:
                            # Skip files that can't be read as text
                            pass
                
                info["content"] = search_result
                info["success"] = True
            
            else:
                info["error"] = f"Unsupported source type: {source_type}"
        
        except Exception as e:
            info["error"] = str(e)
        
        gathered_info.append(info)
    
    # Create a summary of the gathered information
    summary = {
        "total_sources": len(sources),
        "successful_sources": sum(1 for info in gathered_info if info["success"]),
        "source_types": {}
    }
    
    # Count source types
    for info in gathered_info:
        source_type = info["source_type"]
        if source_type in summary["source_types"]:
            summary["source_types"][source_type] += 1
        else:
            summary["source_types"][source_type] = 1
    
    # Update instruction with gathered information
    instruction["gathered_information"] = {
        "sources": gathered_info,
        "summary": summary,
        "gathered_at": int(time.time())
    }
    
    instruction["status"] = "information_gathered"
    instruction["workflow_step"] = "INFORMATION_GATHERING"
    
    # Update instruction file
    instruction_path = os.path.join(get_project_root(), ".aerith", "instructions", f"{instruction_id}.json")
    with open(instruction_path, 'w') as f:
        json.dump(instruction, f, indent=2)
    
    return {
        "success": True,
        "message": f"Gathered information from {len(sources)} sources for instruction {instruction_id}",
        "instruction": instruction,
        "summary": summary
    }

# ==========================================
# STEP 4: ANALYSIS_AND_ORCHESTRATION
# ==========================================

@mcp.tool()
def analyze_and_orchestrate(
    instruction_id: str,
    analysis: Dict[str, Any],
    execution_plan: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze gathered information and create an execution plan (Step 4 in the Manus workflow).
    
    Args:
        instruction_id: The unique identifier for the instruction
        analysis: Analysis of the gathered information
        execution_plan: List of execution steps derived from analysis
    
    Returns:
        Dict with analysis and execution plan
    """
    logger.info(f"Analyzing and orchestrating for instruction: {instruction_id}")
    
    result = get_instruction(instruction_id)
    if not result["success"]:
        return result
    
    instruction = result["instruction"]
    
    if "gathered_information" not in instruction:
        return {
            "success": False,
            "message": "No gathered information found. Complete information gathering first."
        }
    
    # Add analysis
    instruction["analysis"] = {
        "findings": analysis.get("findings", []),
        "recommendations": analysis.get("recommendations", []),
        "decision_points": analysis.get("decision_points", []),
        "analyzed_at": int(time.time())
    }
    
    # Add execution plan
    instruction["execution_plan"] = {
        "steps": execution_plan,
        "total_steps": len(execution_plan),
        "current_step": 0,
        "created_at": int(time.time())
    }
    
    # Add step IDs if not provided
    for i, step in enumerate(instruction["execution_plan"]["steps"]):
        if "id" not in step:
            step["id"] = f"step-{i+1}"
        if "status" not in step:
            step["status"] = "pending"
    
    instruction["status"] = "analyzed"
    instruction["workflow_step"] = "ANALYSIS_AND_ORCHESTRATION"
    
    # Update instruction file
    instruction_path = os.path.join(get_project_root(), ".aerith", "instructions", f"{instruction_id}.json")
    with open(instruction_path, 'w') as f:
        json.dump(instruction, f, indent=2)
    
    return {
        "success": True,
        "message": f"Analysis completed and execution plan created with {len(execution_plan)} steps for instruction {instruction_id}",
        "instruction": instruction
    }

# ==========================================
# STEP 5: RESULT_SYNTHESIS
# ==========================================

@mcp.tool()
def execute_step(
    instruction_id: str,
    step_id: str,
    execution_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a specific step in the execution plan (Step 5 in the Manus workflow).
    
    Args:
        instruction_id: The unique identifier for the instruction
        step_id: The identifier of the step to execute
        execution_details: Details of how to execute the step
    
    Returns:
        Dict with execution results
    """
    logger.info(f"Executing step {step_id} for instruction: {instruction_id}")
    
    result = get_instruction(instruction_id)
    if not result["success"]:
        return result
    
    instruction = result["instruction"]
    
    if "execution_plan" not in instruction:
        return {
            "success": False,
            "message": "No execution plan found. Complete analysis and orchestration first."
        }
    
    # Find the step to execute
    step_to_execute = None
    step_index = -1
    
    for i, step in enumerate(instruction["execution_plan"]["steps"]):
        if step["id"] == step_id:
            step_to_execute = step
            step_index = i
            break
    
    if step_to_execute is None:
        return {
            "success": False,
            "message": f"Step {step_id} not found in execution plan"
        }
    
    # Execute step based on its type
    step_type = step_to_execute.get("type", "unknown")
    result = {
        "step_id": step_id,
        "step_type": step_type,
        "success": False,
        "output": None,
        "error": None,
        "artifacts": []
    }
    
    try:
        if step_type == "file_creation":
            # Create a file
            file_path = execution_details.get("file_path")
            file_content = execution_details.get("content")
            
            if file_path and file_content:
                success = write_file(file_path, file_content)
                result["success"] = success
                if success:
                    result["artifacts"].append({"type": "file", "path": file_path, "action": "created"})
                    result["output"] = f"File created: {file_path}"
                else:
                    result["error"] = f"Failed to create file: {file_path}"
            else:
                result["error"] = "Missing file_path or content"
        
        elif step_type == "file_modification":
            # Modify an existing file
            file_path = execution_details.get("file_path")
            
            if not os.path.exists(file_path):
                result["error"] = f"File not found: {file_path}"
            else:
                original_content = read_file(file_path)
                
                # Apply modifications
                new_content = execution_details.get("content")
                if new_content:
                    # Full content replacement
                    success = write_file(file_path, new_content)
                else:
                    # Apply patches
                    patches = execution_details.get("patches", [])
                    new_content = original_content
                    
                    for patch in patches:
                        patch_type = patch.get("type")
                        if patch_type == "replace":
                            old_text = patch.get("old_text")
                            new_text = patch.get("new_text")
                            if old_text and new_text:
                                new_content = new_content.replace(old_text, new_text)
                        elif patch_type == "insert":
                            position = patch.get("position")
                            text = patch.get("text")
                            if position is not None and text:
                                new_content = new_content[:position] + text + new_content[position:]
                        elif patch_type == "delete":
                            start = patch.get("start")
                            end = patch.get("end")
                            if start is not None and end is not None:
                                new_content = new_content[:start] + new_content[end:]
                    
                    success = write_file(file_path, new_content)
                
                result["success"] = success
                if success:
                    result["artifacts"].append({"type": "file", "path": file_path, "action": "modified"})
                    result["output"] = f"File modified: {file_path}"
                else:
                    result["error"] = f"Failed to modify file: {file_path}"
        
        elif step_type == "command_execution":
            # Execute a command
            command = execution_details.get("command")
            if command:
                cmd_result = run_command(command if isinstance(command, list) else command.split())
                result["success"] = cmd_result["success"]
                result["output"] = cmd_result["output"]
                if not cmd_result["success"]:
                    result["error"] = cmd_result["error"]
            else:
                result["error"] = "Missing command"
        
        elif step_type == "dependency_installation":
            # Install dependencies
            packages = execution_details.get("packages", [])
            package_manager = execution_details.get("package_manager", "npm")
            
            if packages:
                if package_manager == "npm":
                    cmd = ["npm", "install", "--save"] + packages
                elif package_manager == "pip":
                    cmd = ["pip", "install"] + packages
                else:
                    result["error"] = f"Unsupported package manager: {package_manager}"
                    return result
                
                cmd_result = run_command(cmd)
                result["success"] = cmd_result["success"]
                result["output"] = cmd_result["output"]
                if not cmd_result["success"]:
                    result["error"] = cmd_result["error"]
            else:
                result["error"] = "No packages specified"
        
        else:
            result["error"] = f"Unsupported step type: {step_type}"
    
    except Exception as e:
        result["error"] = str(e)
    
    # Update step result in the execution plan
    instruction["execution_plan"]["steps"][step_index]["result"] = result
    instruction["execution_plan"]["steps"][step_index]["status"] = "completed" if result["success"] else "failed"
    
    # Update current step if this was successful
    if result["success"] and instruction["execution_plan"]["current_step"] == step_index:
        instruction["execution_plan"]["current_step"] = step_index + 1
    
    # Check if all steps are completed
    all_completed = all(step.get("status") == "completed" for step in instruction["execution_plan"]["steps"])
    if all_completed:
        instruction["status"] = "completed"
    
    instruction["workflow_step"] = "RESULT_SYNTHESIS"
    
    # Update instruction file
    instruction_path = os.path.join(get_project_root(), ".aerith", "instructions", f"{instruction_id}.json")
    with open(instruction_path, 'w') as f:
        json.dump(instruction, f, indent=2)
    
    return {
        "success": result["success"],
        "message": result["output"] if result["success"] else result["error"],
        "instruction": instruction,
        "result": result
    }

@mcp.tool()
def generate_final_report(
    instruction_id: str,
    include_details: bool = True
) -> Dict[str, Any]:
    """
    Generate a final report for the instruction execution (Final part of Step 5 in the Manus workflow).
    
    Args:
        instruction_id: The unique identifier for the instruction
        include_details: Whether to include full execution details
    
    Returns:
        Dict with the final report
    """
    logger.info(f"Generating final report for instruction: {instruction_id}")
    
    result = get_instruction(instruction_id)
    if not result["success"]:
        return result
    
    instruction = result["instruction"]
    
    # Collect all artifacts
    artifacts = []
    for step in instruction.get("execution_plan", {}).get("steps", []):
        if "result" in step and step["result"].get("success", False):
            artifacts.extend(step["result"].get("artifacts", []))
    
    # Generate report
    report = {
        "instruction_id": instruction_id,
        "title": instruction.get("title"),
        "status": instruction.get("status"),
        "created_at": instruction.get("created_at"),
        "completed_at": int(time.time()),
        "workflow_steps_completed": [instruction.get("workflow_step", "USER_INSTRUCTION")],
        "summary": {
            "planned_subtasks": len(instruction.get("task_plan", {}).get("subtasks", [])),
            "executed_steps": sum(1 for step in instruction.get("execution_plan", {}).get("steps", []) 
                                if step.get("status") in ["completed", "failed"]),
            "successful_steps": sum(1 for step in instruction.get("execution_plan", {}).get("steps", []) 
                                if step.get("status") == "completed"),
            "artifacts": artifacts
        }
    }
    
    # Include full details if requested
    if include_details:
        report["details"] = {
            "user_instruction": {
                "description": instruction.get("description"),
                "goal": instruction.get("goal")
            },
            "task_planning": instruction.get("task_plan", {}),
            "information_gathering": instruction.get("gathered_information", {}).get("summary", {}),
            "analysis_and_orchestration": {
                "findings": instruction.get("analysis", {}).get("findings", []),
                "recommendations": instruction.get("analysis", {}).get("recommendations", [])
            },
            "result_synthesis": {
                "executed_steps": [
                    {
                        "id": step.get("id"),
                        "title": step.get("title"),
                        "type": step.get("type"),
                        "status": step.get("status"),
                        "output": step.get("result", {}).get("output")
                    }
                    for step in instruction.get("execution_plan", {}).get("steps", [])
                    if "result" in step
                ]
            }
        }
    
    # Add report to instruction
    instruction["final_report"] = report
    instruction["status"] = "completed" if instruction["status"] != "failed" else "failed"
    
    # Update instruction file
    instruction_path = os.path.join(get_project_root(), ".aerith", "instructions", f"{instruction_id}.json")
    with open(instruction_path, 'w') as f:
        json.dump(instruction, f, indent=2)
    
    return {
        "success": True,
        "message": f"Generated final report for instruction {instruction_id}",
        "instruction": instruction,
        "report": report
    }

# ==========================================
# HIGHER LEVEL ORCHESTRATION
# ==========================================

@mcp.tool()
def build_feature(
    title: str,
    description: str,
    goal: str,
    priority: Literal["low", "medium", "high"] = "medium"
) -> Dict[str, Any]:
    """
    High-level orchestration tool to build a complete feature using the Manus workflow.
    This tool will create an instruction and guide you through the 5-step process.
    
    Args:
        title: Brief title for the feature
        description: Detailed description of the feature requirements
        goal: The specific goal or outcome to achieve
        priority: Feature priority level
    
    Returns:
        Dict with instruction details and steps to follow
    """
    logger.info(f"Starting build feature workflow: {title}")
    
    # Create a new instruction
    instruction_result = create_instruction(
        title=title,
        description=description,
        goal=goal,
        priority=priority
    )
    
    if not instruction_result["success"]:
        return instruction_result
    
    instruction_id = instruction_result["instruction_id"]
    
    # Return guidance for the next steps
    next_steps = [
        "1. Use create_task_plan to break down this feature into subtasks",
        "2. Use gather_information to collect necessary information for implementation",
        "3. Use analyze_and_orchestrate to analyze the info and create an execution plan",
        "4. Use execute_step for each step in your execution plan",
        "5. Use generate_final_report to summarize the implementation"
    ]
    
    return {
        "success": True,
        "instruction_id": instruction_id,
        "message": f"Feature '{title}' has been initialized with instruction ID: {instruction_id}",
        "next_steps": next_steps,
        "instruction": instruction_result["instruction"]
    }

# ==========================================
# BROWSER-USE INTEGRATION
# ==========================================

@mcp.tool()
def run_browser_agent(goal: str) -> Dict[str, Any]:
    """
    Run a browser-use agent to achieve a specified goal.
    This tool integrates the browser-use library to perform browser automation.

    Args:
        goal: The goal or query that the agent should address.
    
    Returns:
        A dict with the final result of the browser automation task.
    """
    logger.info(f"Running browser agent with goal: {goal}")
    try:
        from browser_use import BrowserContext, Agent  # Import the browser-use library
    except ImportError as e:
        logger.error("Failed to import browser-use library. Ensure it's installed.", exc_info=True)
        return {"success": False, "error": "browser-use library not installed."}
        
    try:
        # Initialize browser context (set headless=False if you wish to see the browser window)
        context = BrowserContext(headless=True)
        # Create an agent with the given goal
        agent = Agent(context=context, initial_goal=goal)
        
        # Run the agent loop.
        # Depending on the implementation, you might have a generator (e.g., run_generator())
        # or simply call run() to execute and get the final result.
        result = agent.run()  # Replace with run_generator() if you want streaming updates
        
        logger.info("Browser agent completed successfully.")
        return {
            "success": True,
            "result": result,
            "message": f"Browser agent completed goal: {goal}"
        }
    except Exception as e:
        logger.error(f"Error running browser agent: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

# ==========================================
# RESOURCES
# ==========================================

@mcp.resource("file://{path}")
def get_file(path: str) -> str:
    """Get file contents by path."""
    full_path = os.path.join(get_project_root(), path)
    
    if os.path.exists(full_path):
        return read_file(full_path)
    else:
        return f"File not found: {path}"

@mcp.resource("project://structure")
def get_project_structure() -> Dict[str, Any]:
    """Get the project structure as a dictionary."""
    def build_structure(path, max_depth=3, current_depth=0):
        result = {}
        
        if current_depth > max_depth:
            return {"truncated": True, "type": "directory"}
        
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                
                if os.path.isdir(full_path):
                    result[item] = build_structure(full_path, max_depth, current_depth + 1)
                    result[item]["type"] = "directory"
                else:
                    # For files, just add size information
                    try:
                        size = os.path.getsize(full_path)
                        result[item] = {"type": "file", "size": size}
                    except Exception as e:
                        result[item] = {"type": "file", "error": str(e)}
        except Exception as e:
            return {"error": str(e), "type": "directory"}
            
        return result
    
    project_root = get_project_root()
    return build_structure(project_root)

@mcp.resource("instructions://list")
def get_instructions() -> List[Dict[str, Any]]:
    """Get list of all instructions."""
    instructions_dir = os.path.join(get_project_root(), ".aerith", "instructions")
    
    if not os.path.exists(instructions_dir):
        return []
    
    instructions = []
    for filename in os.listdir(instructions_dir):
        if filename.endswith(".json"):
            instruction_path = os.path.join(instructions_dir, filename)
            try:
                with open(instruction_path, 'r') as f:
                    instruction = json.load(f)
                instructions.append(instruction)
            except Exception:
                pass
    
    return instructions

# ==========================================
# SERVER STARTUP
# ==========================================

if __name__ == "__main__":
    # Parse command line arguments
    port = None
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
                logger.info(f"Using port: {port}")
            except ValueError:
                logger.error(f"Invalid port number: {sys.argv[i + 1]}")
    
    if use_stdio:
        # Run in stdio mode
        logger.info("Starting MCP server in stdio mode")
        try:
            # Log detailed info about the environment
            logger.info(f"Python executable: {sys.executable}")
            logger.info(f"Arguments: {sys.argv}")
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info("Environment variables:")
            for key, value in sorted(os.environ.items()):
                if key.startswith("PYTHON") or key.startswith("MCP"):
                    logger.info(f"  {key}={value}")
            
            logger.info(f"stdin isatty: {sys.stdin.isatty()}")
            logger.info(f"stdout isatty: {sys.stdout.isatty()}")
            
            import asyncio
            
            logger.info("Testing if stderr is working (this should appear in logs)")
            logger.info("About to write a test message to stdout (for JSON-RPC protocol)")
            test_msg = '{"jsonrpc":"2.0","method":"test","params":{},"id":"test-1"}'
            content_length = len(test_msg.encode('utf-8'))
            sys.stdout.write(f"Content-Length: {content_length}\r\n\r\n{test_msg}")
            sys.stdout.flush()
            logger.info("Test message written to stdout")
            
            if os.environ.get("MCP_DEBUG") == "true":
                logger.info("Enabling asyncio debug mode")
                asyncio.get_event_loop().set_debug(True)
            
            stdin_has_buffer = hasattr(sys.stdin, 'buffer')
            stdout_has_buffer = hasattr(sys.stdout, 'buffer')
            logger.info(f"sys.stdin has buffer: {stdin_has_buffer}, type: {type(sys.stdin)}")
            logger.info(f"sys.stdout has buffer: {stdout_has_buffer}, type: {type(sys.stdout)}")
            
            if not stdin_has_buffer or not stdout_has_buffer:
                logger.error("stdin/stdout don't have buffer attributes, which is required for stdio mode")
                logger.error("Trying to continue with current stdin/stdout anyway...")
            
            try:
                logger.info("Trying direct synchronous run_stdio mode first...")
                if hasattr(mcp, 'run_stdio'):
                    logger.info("Found run_stdio method, calling it directly")
                    mcp.run_stdio()
                    logger.info("run_stdio completed")
                    sys.exit(0)
                else:
                    logger.info("run_stdio method not found, will try async mode")
            except Exception as e:
                logger.error(f"Error in synchronous run_stdio: {e}", exc_info=True)
                logger.info("Falling back to async mode...")
            
            logger.info("Running MCP server with run_stdio_async")
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                asyncio_task = mcp.run_stdio_async()
                logger.info("Got asyncio task, running it now...")
                
                async def run_with_error_handling():
                    try:
                        logger.info("Starting asyncio task execution")
                        await asyncio_task
                        logger.info("Asyncio task completed successfully")
                    except Exception as e:
                        logger.error(f"Error in asyncio task: {e}", exc_info=True)
                        raise
                
                logger.info("Running asyncio task with proper error handling")
                loop.run_until_complete(run_with_error_handling())
                logger.info("Async task completed")
                
                logger.info("Entering keep-alive loop")
                while True:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error in asyncio event loop: {e}", exc_info=True)
                raise
                
            logger.info("Server completed successfully")
        except Exception as e:
            logger.error(f"Error running MCP server in stdio mode: {e}", exc_info=True)
            logger.info("Sleeping for 10 seconds before exit to keep logs visible...")
            time.sleep(10)
            sys.exit(1)
    else:
        # Run in HTTP mode
        try:
            host = "0.0.0.0"  # Listen on all interfaces
            port = port or 8090  # Default port
            
            logger.info(f"Starting MCP server on {host}:{port}")
            
            app = mcp.sse_app()
            
            import uvicorn
            uvicorn.run(
                app, 
                host=host, 
                port=port,
                log_level="info"
            )
        except Exception as e:
            logger.error(f"Error running MCP server in HTTP mode: {e}", exc_info=True)
            sys.exit(1)
