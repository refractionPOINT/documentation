#!/bin/bash
set -e
set -o pipefail

# boot.sh - LimaCharlie CLI Setup Script
# This script creates a virtual environment and installs the LimaCharlie CLI

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "LimaCharlie CLI Setup"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3 and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${BLUE}Using: ${PYTHON_VERSION}${NC}"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install LimaCharlie CLI
echo -e "${BLUE}Installing LimaCharlie CLI...${NC}"
if pip install limacharlie --quiet; then
    echo -e "${GREEN}✓ LimaCharlie CLI installed successfully${NC}"

    # Verify installation
    if command -v limacharlie &> /dev/null; then
        LC_VERSION=$(limacharlie version 2>/dev/null || echo "installed")
        echo -e "${GREEN}✓ LimaCharlie CLI is ready: ${LC_VERSION}${NC}"
    fi
else
    echo -e "${RED}Error: Failed to install LimaCharlie CLI${NC}"
    exit 1
fi
echo ""

# Install project requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}Installing project requirements...${NC}"
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓ Project requirements installed${NC}"
    echo ""
fi

echo "========================================"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "========================================"
echo ""
echo "Virtual environment is activated and ready to use."
echo ""
echo "To use LimaCharlie CLI, run commands like:"
echo "  limacharlie --help"
echo "  limacharlie login"
echo ""
echo "To deactivate the virtual environment later, run:"
echo "  deactivate"
echo ""
echo "To activate the virtual environment in a new terminal session, run:"
echo "  source venv/bin/activate"
echo ""

# Activate the virtual environment for the current shell
source venv/bin/activate
