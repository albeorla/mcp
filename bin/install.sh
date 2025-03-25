#!/bin/bash
# Installation script for MCP server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the parent directory (mcp root)
MCP_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Set error handling
set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Aerith Admin MCP Server - Installation${NC}"
echo "==========================================="

# Check if python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$MCP_DIR/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    cd "$MCP_DIR"
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created.${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists.${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$MCP_DIR/venv/bin/activate"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r "$MCP_DIR/requirements-dev.txt"

# Install playwright browsers if needed
if pip list | grep -q "playwright"; then
    echo -e "${YELLOW}Installing Playwright browsers...${NC}"
    python -m playwright install
fi

echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "source bin/activate_venv.sh"
echo ""
echo "To run tests:"
echo "bin/run_tests.py"
echo ""
echo "To run the server:"
echo "python server.py"
