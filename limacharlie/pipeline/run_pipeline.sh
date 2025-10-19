#!/bin/bash
set -e
set -o pipefail

# LimaCharlie Documentation Pipeline Runner
# This script orchestrates the full documentation processing pipeline:
# 1. Fetch docs from docs.limacharlie.io
# 2. Clean raw markdown files
# 3. Move cleaned files to final output directory

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "========================================"
echo "LimaCharlie Documentation Pipeline"
echo "========================================"
echo ""

# Change to repository root
cd "$REPO_ROOT"

# Step 1: Fetch documentation
echo -e "${BLUE}Step 1/3: Fetching documentation from docs.limacharlie.io...${NC}"
python3 limacharlie/pipeline/fetch_docs.py
echo -e "${GREEN}✓ Documentation fetched successfully${NC}"
echo ""

# Step 2: Clean raw markdown
echo -e "${BLUE}Step 2/3: Cleaning raw markdown files...${NC}"
python3 limacharlie/pipeline/clean_raw.py
echo -e "${GREEN}✓ Markdown files cleaned successfully${NC}"
echo ""

# Step 3: Move to final output directory
echo -e "${BLUE}Step 3/3: Moving cleaned files to final output directory...${NC}"

# Create doc directory if it doesn't exist
mkdir -p limacharlie/doc

# Clear the doc directory (remove all contents)
echo "Clearing destination directory..."
rm -rf limacharlie/doc/*

# Move all files from raw_markdown to doc
echo "Moving files from raw_markdown to doc..."
if [ -d "limacharlie/raw_markdown" ] && [ "$(ls -A limacharlie/raw_markdown 2>/dev/null)" ]; then
    mv limacharlie/raw_markdown/* limacharlie/doc/
    echo -e "${GREEN}✓ Files moved successfully${NC}"
else
    echo "Warning: raw_markdown directory is empty or doesn't exist"
fi

echo ""
echo "========================================"
echo -e "${GREEN}Pipeline completed successfully!${NC}"
echo "========================================"
echo "Output location: limacharlie/doc/"
echo ""
