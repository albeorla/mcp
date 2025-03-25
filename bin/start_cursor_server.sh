#!/bin/bash
# Script to start the MCP server for Cursor integration
# This ensures the correct environment and configuration for Cursor to connect

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the parent directory (mcp root)
MCP_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Default port
PORT=8090
SSE=true

# Process arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --stdio)
      SSE=false
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Aerith Admin MCP Server for Cursor Integration${NC}"
echo "============================================================"

# Activate virtual environment if needed
if [[ -z "$VIRTUAL_ENV" ]]; then
  echo -e "${YELLOW}Activating virtual environment...${NC}"
  
  # Check if venv exists
  if [ ! -d "$MCP_DIR/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    cd "$MCP_DIR"
    python3 -m venv venv
    
    # Activate venv
    source "$MCP_DIR/venv/bin/activate"
    
    # Install dependencies
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip
    pip install -r "$MCP_DIR/requirements.txt"
  else
    # Activate existing venv
    source "$MCP_DIR/venv/bin/activate"
  fi
else
  echo -e "${GREEN}Using existing virtual environment: $VIRTUAL_ENV${NC}"
fi

# Verify key dependencies
echo -e "${YELLOW}Verifying MCP server dependencies...${NC}"
if ! python -c "import mcp" &> /dev/null; then
  echo -e "${RED}Error: MCP package not found in environment.${NC}"
  echo -e "${YELLOW}Installing dependencies...${NC}"
  pip install -r "$MCP_DIR/requirements.txt"
fi

# Set environment variables
export PYTHONPATH="$MCP_DIR:$PYTHONPATH"
export MCP_DEBUG=true

# Go to MCP directory
cd "$MCP_DIR"

# Check if .cursor/mcp.json exists in parent directory
if [ ! -f "$MCP_DIR/../.cursor/mcp.json" ]; then
  echo -e "${YELLOW}Warning: .cursor/mcp.json not found in parent directory.${NC}"
  echo -e "${YELLOW}Creating basic configuration...${NC}"
  
  mkdir -p "$MCP_DIR/../.cursor"
  cat > "$MCP_DIR/../.cursor/mcp.json" << EOF
{
  "mcpServers": {
    "aerith-admin-mcp": {
      "url": "http://localhost:${PORT}/sse"
    }
  }
}
EOF
  echo -e "${GREEN}Created Cursor MCP configuration.${NC}"
else
  echo -e "${GREEN}Cursor MCP configuration exists.${NC}"
fi

# Start the server
if [ "$SSE" = true ]; then
  echo -e "${GREEN}Starting MCP server in HTTP mode on port ${PORT}...${NC}"
  echo -e "${YELLOW}Connect Cursor to http://localhost:${PORT}/sse${NC}"
  
  # Check if we should run in resilient mode
  if [ "$1" = "--resilient" ] || [ "$2" = "--resilient" ] || [ "$3" = "--resilient" ]; then
    echo -e "${GREEN}Running in resilient mode with automatic restart${NC}"
    exec "$SCRIPT_DIR/run_resilient_server.sh" --mode http --port $PORT
  else
    python server.py --port $PORT
  fi
else
  echo -e "${GREEN}Starting MCP server in STDIO mode...${NC}"
  
  # Check if we should run in resilient mode
  if [ "$1" = "--resilient" ] || [ "$2" = "--resilient" ] || [ "$3" = "--resilient" ]; then
    echo -e "${GREEN}Running in resilient mode with automatic restart${NC}"
    exec "$SCRIPT_DIR/run_resilient_server.sh" --mode stdio
  else
    python server.py --stdio
  fi
fi 