#!/bin/bash
# Script to run the MCP server in a resilient way
# This script ensures the server keeps running even if it crashes

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate the virtual environment if it exists
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    echo "Activated virtual environment"
else
    echo "Warning: No virtual environment found at $PROJECT_ROOT/venv"
fi

# Ensure the .aerith/logs directory exists
mkdir -p "$PROJECT_ROOT/.aerith/logs"

# Log file for this script
LOG_FILE="$PROJECT_ROOT/.aerith/logs/resilient_server.log"

# Default parameters
MODE="http"
PORT=8090
RESTART_DELAY=5  # seconds to wait between restart attempts
MAX_RESTARTS=100 # maximum number of automatic restarts before giving up
MONITOR_INTERVAL=30 # seconds between health checks

# Process command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --restart-delay)
            RESTART_DELAY="$2"
            shift 2
            ;;
        --max-restarts)
            MAX_RESTARTS="$2"
            shift 2
            ;;
        --monitor-interval)
            MONITOR_INTERVAL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--mode http|stdio] [--port PORT] [--restart-delay SECONDS] [--max-restarts COUNT] [--monitor-interval SECONDS]"
            exit 1
            ;;
    esac
done

echo "Starting resilient MCP server in $MODE mode on port $PORT" | tee -a "$LOG_FILE"
echo "$(date) - Starting resilient server monitoring" >> "$LOG_FILE"

# Function to check if the MCP server is healthy
check_server_health() {
    # Run the monitor script in check-only mode
    "$SCRIPT_DIR/monitor_server.py" --check-only --mode "$MODE" --port "$PORT"
    return $?
}

# Function to (re)start the MCP server
restart_server() {
    echo "$(date) - (Re)starting MCP server" | tee -a "$LOG_FILE"
    "$SCRIPT_DIR/monitor_server.py" --force-restart --mode "$MODE" --port "$PORT"
    return $?
}

# Main monitoring loop
restart_count=0
while true; do
    # Check if the server is healthy
    if ! check_server_health; then
        # Server is not healthy, need to restart it
        echo "$(date) - MCP server is not healthy (restart #$restart_count)" | tee -a "$LOG_FILE"
        
        # Check if we've reached the maximum number of restarts
        if [ $restart_count -ge $MAX_RESTARTS ]; then
            echo "$(date) - Maximum number of restarts ($MAX_RESTARTS) reached, giving up" | tee -a "$LOG_FILE"
            exit 1
        fi
        
        # Restart the server
        if restart_server; then
            echo "$(date) - MCP server restarted successfully" | tee -a "$LOG_FILE"
        else
            echo "$(date) - Failed to restart MCP server" | tee -a "$LOG_FILE"
        fi
        
        # Increment restart counter
        restart_count=$((restart_count + 1))
        
        # Wait before checking health again
        sleep $RESTART_DELAY
    else
        # Server is healthy, reset restart counter
        if [ $restart_count -gt 0 ]; then
            echo "$(date) - MCP server is healthy, resetting restart counter" | tee -a "$LOG_FILE"
            restart_count=0
        fi
        
        # Wait before checking health again
        sleep $MONITOR_INTERVAL
    fi
done 