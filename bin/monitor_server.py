#!/usr/bin/env python3
"""
Monitor script for the MCP server.
This script checks if the MCP server is running and restarts it if necessary.
It's designed to be run periodically from a cron job or scheduled task.
"""
import os
import sys
import subprocess
import time
import signal
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".aerith", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "monitor.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("monitor")

def get_project_root():
    """Get the root directory of the project."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def find_server_pid():
    """Find the PID of the running MCP server."""
    try:
        # Check for running Python processes
        result = subprocess.run(
            ["pgrep", "-f", "python.*server.py"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            logger.info(f"Found {len(pids)} potential MCP server processes: {pids}")
            return pids
        else:
            logger.warning("No MCP server process found")
            return []
    except Exception as e:
        logger.error(f"Error finding server PID: {e}")
        return []

def check_server_health(pid):
    """Check if the server process is healthy by analyzing logs."""
    try:
        # Check if the process is still running
        os.kill(int(pid), 0)  # This doesn't actually send a signal, just checks if the process exists
        
        # Check if there has been a heartbeat in the last 10 minutes
        server_log_file = os.path.join(log_dir, "mcp_server.log")
        if os.path.exists(server_log_file):
            # Look for recent heartbeat or log activity
            result = subprocess.run(
                ["tail", "-n", "100", server_log_file],
                capture_output=True,
                text=True,
                check=False
            )
            
            log_content = result.stdout
            
            # First check for heartbeat
            if "MCP Server Heartbeat:" in log_content:
                logger.info(f"Server {pid} has recent heartbeat")
                return True
                
            # Then check for any recent activity
            log_lines = log_content.splitlines()
            if log_lines:
                # Check the timestamp of the most recent log entry
                try:
                    last_log_time_str = log_lines[-1].split(" - ")[0]
                    last_log_time = datetime.strptime(last_log_time_str, "%Y-%m-%d %H:%M:%S,%f")
                    now = datetime.now()
                    minutes_since_last_log = (now - last_log_time).total_seconds() / 60
                    
                    if minutes_since_last_log < 10:  # Less than 10 minutes
                        logger.info(f"Server {pid} has recent log activity ({minutes_since_last_log:.1f} minutes ago)")
                        return True
                    else:
                        logger.warning(f"Server {pid} last log was {minutes_since_last_log:.1f} minutes ago")
                except Exception as e:
                    logger.error(f"Error parsing log timestamp: {e}")
        
        # If we can't confirm health through logs, assume it's unhealthy
        logger.warning(f"Server {pid} may be unhealthy (no recent logs)")
        return False
    except (ProcessLookupError, ValueError):
        logger.warning(f"Server process {pid} not found")
        return False
    except Exception as e:
        logger.error(f"Error checking server health: {e}")
        return False

def restart_server(mode="http", port=8090):
    """Start or restart the MCP server."""
    try:
        logger.info(f"Starting MCP server in {mode} mode on port {port}")
        
        # Get the path to the virtual environment python
        venv_python = os.path.join(get_project_root(), "venv", "bin", "python")
        if not os.path.exists(venv_python):
            venv_python = sys.executable  # Fall back to the current Python interpreter
            logger.warning(f"Virtual environment python not found, using {venv_python}")
        
        # Get the path to the server script
        server_script = os.path.join(get_project_root(), "server.py")
        
        # Set up environment variables
        env = os.environ.copy()
        env["MCP_DEBUG"] = "true"
        
        # Build the command
        cmd = [venv_python, server_script]
        if mode == "http":
            cmd.extend(["--port", str(port)])
        else:
            cmd.append("--stdio")
        
        # Start the server in the background
        with open(os.path.join(log_dir, "monitor_stdout.log"), "a") as stdout_log:
            with open(os.path.join(log_dir, "monitor_stderr.log"), "a") as stderr_log:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                stdout_log.write(f"\n\n==== SERVER RESTART {timestamp} ====\n\n")
                stderr_log.write(f"\n\n==== SERVER RESTART {timestamp} ====\n\n")
                
                process = subprocess.Popen(
                    cmd,
                    cwd=get_project_root(),
                    env=env,
                    stdout=stdout_log,
                    stderr=stderr_log,
                    start_new_session=True  # This makes the process independent of this script
                )
                
                logger.info(f"Started MCP server with PID {process.pid}")
                
                # Wait a moment to see if the process immediately crashes
                time.sleep(3)
                try:
                    # Check if the process is still running
                    exit_code = process.poll()
                    if exit_code is not None:
                        logger.error(f"Server process exited immediately with code {exit_code}")
                        return False
                    
                    logger.info(f"Server process {process.pid} is running")
                    return True
                except Exception as e:
                    logger.error(f"Error checking if server started: {e}")
                    return False
    except Exception as e:
        logger.error(f"Error restarting server: {e}")
        return False

def terminate_server(pid):
    """Gracefully terminate the server process."""
    try:
        logger.info(f"Attempting to gracefully terminate server process {pid}")
        
        # Send SIGTERM to allow graceful shutdown
        os.kill(int(pid), signal.SIGTERM)
        
        # Wait up to 10 seconds for the process to exit
        for _ in range(10):
            try:
                # Check if the process still exists
                os.kill(int(pid), 0)
                # Process still exists, wait a bit
                time.sleep(1)
            except ProcessLookupError:
                # Process has exited
                logger.info(f"Server process {pid} has terminated gracefully")
                return True
        
        # If we get here, the process didn't exit gracefully, try SIGKILL
        logger.warning(f"Server process {pid} didn't terminate gracefully, using SIGKILL")
        os.kill(int(pid), signal.SIGKILL)
        return True
    except (ProcessLookupError, ValueError):
        logger.info(f"Server process {pid} not found (may have already exited)")
        return True
    except Exception as e:
        logger.error(f"Error terminating server process {pid}: {e}")
        return False

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Monitor and manage the MCP server")
    
    parser.add_argument(
        "--mode", 
        choices=["http", "stdio"], 
        default="http",
        help="Server mode (http or stdio)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8090,
        help="Port for HTTP mode"
    )
    parser.add_argument(
        "--force-restart", 
        action="store_true",
        help="Force restart the server even if it's already running"
    )
    parser.add_argument(
        "--check-only", 
        action="store_true",
        help="Only check if the server is running, don't start it"
    )
    
    return parser.parse_args()

def main():
    """Main function to check server status and restart if necessary."""
    args = parse_arguments()
    
    logger.info(f"Starting MCP server monitor (mode={args.mode}, port={args.port})")
    
    # Find any running MCP server processes
    server_pids = find_server_pid()
    
    # If the server is running, check if it's healthy
    healthy = False
    if server_pids:
        for pid in server_pids:
            if check_server_health(pid):
                healthy = True
                logger.info(f"Server is running with PID {pid} and appears healthy")
                
                # Handle force-restart
                if args.force_restart:
                    logger.info("Force restart requested, terminating existing server")
                    terminate_server(pid)
                    healthy = False
                
                # No need to check other processes if we found a healthy one
                if healthy and not args.force_restart:
                    break
    
    # If check-only mode, just exit with appropriate status code
    if args.check_only:
        logger.info("Check-only mode, exiting")
        return 0 if healthy else 1
    
    # If the server is not running or not healthy (or force-restart was specified),
    # terminate any existing processes and start a new one
    if not healthy:
        logger.info("Server is not running or not healthy, restarting")
        
        # Terminate any existing server processes
        for pid in server_pids:
            terminate_server(pid)
        
        # Start a new server
        if restart_server(mode=args.mode, port=args.port):
            logger.info("Server successfully restarted")
            return 0
        else:
            logger.error("Failed to restart server")
            return 1
    
    logger.info("Monitor check complete, server is running properly")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 