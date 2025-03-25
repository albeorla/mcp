#!/bin/bash
# Script to activate the virtual environment for MCP

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the parent directory (mcp root)
MCP_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Go to MCP directory
cd "$MCP_DIR"

# Check if virtual environment exists in MCP directory
if [ ! -d "$MCP_DIR/venv" ]; then
  echo -e "${YELLOW}Virtual environment not found in $MCP_DIR. Creating one...${NC}"
  python3 -m venv "$MCP_DIR/venv"
  
  # Activate the new venv to install packages
  source "$MCP_DIR/venv/bin/activate"
  
  # Install dependencies immediately
  echo -e "${YELLOW}Installing dependencies...${NC}"
  pip install --upgrade pip
  pip install -r "$MCP_DIR/requirements.txt"
  
  echo -e "${GREEN}Virtual environment created and dependencies installed at $MCP_DIR/venv.${NC}"
else
  # Activate the virtual environment
  source "$MCP_DIR/venv/bin/activate"
  echo -e "${GREEN}MCP virtual environment activated at $MCP_DIR/venv${NC}"
fi

# Verify essential packages
echo -e "${YELLOW}Verifying essential packages...${NC}"
if ! python -c "import mcp" &> /dev/null; then
  echo -e "${RED}Warning: MCP package not found in environment.${NC}"
  echo -e "${YELLOW}Installing dependencies...${NC}"
  pip install -r "$MCP_DIR/requirements.txt"
else
  echo -e "${GREEN}MCP package verified.${NC}"
fi

# Display activation information
echo -e "${GREEN}Python: $(which python)${NC}"
echo -e "${GREEN}Working directory: $(pwd)${NC}"
echo ""
echo "You can run tests with: python bin/run_tests.py"
echo "You can run the server with: python server.py"
echo "For Cursor integration: ./bin/start_cursor_server.sh"
echo ""
echo "To deactivate the virtual environment, run: deactivate"

# Add MCP_DIR to PYTHONPATH if needed
export PYTHONPATH="$MCP_DIR:$PYTHONPATH"
export MCP_DEBUG=true
