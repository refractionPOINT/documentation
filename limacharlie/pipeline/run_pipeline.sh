#!/bin/bash
set -e
set -o pipefail

# LimaCharlie Documentation Pipeline Runner
# This script orchestrates the full documentation processing pipeline:
# 0. Clean existing doc directory from git
# 1. Fetch docs from docs.limacharlie.io
# 2. Clean raw markdown files
# 3. Move cleaned files to final output directory
# 4. Add new doc files to git

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

# Step 0: Clean existing doc directory from git
echo -e "${BLUE}Step 0/5: Removing existing doc files from git...${NC}"
if [ -d "limacharlie/doc" ] && [ "$(ls -A limacharlie/doc 2>/dev/null)" ]; then
    git rm -r limacharlie/doc/* || true
    echo -e "${GREEN}✓ Existing doc files removed from git${NC}"
else
    echo "No existing doc files to remove"
fi
echo ""

# Step 1: Fetch documentation
echo -e "${BLUE}Step 1/5: Fetching documentation from docs.limacharlie.io...${NC}"
python3 limacharlie/pipeline/fetch_docs.py
echo -e "${GREEN}✓ Documentation fetched successfully${NC}"
echo ""

# Step 2: Clean raw markdown
echo -e "${BLUE}Step 2/5: Cleaning raw markdown files...${NC}"
python3 limacharlie/pipeline/clean_raw.py
echo -e "${GREEN}✓ Markdown files cleaned successfully${NC}"
echo ""

# Step 3: Move to final output directory
echo -e "${BLUE}Step 3/5: Moving cleaned files to final output directory...${NC}"

# Create doc directory if it doesn't exist
mkdir -p limacharlie/doc

# Clear the doc directory (remove all contents)
echo "Clearing destination directory..."
rm -rf limacharlie/doc/*

# Move all files from raw_markdown to doc
echo "Moving files from raw_markdown to doc..."
if [ -d "limacharlie/raw_markdown" ] && [ "$(ls -A limacharlie/raw_markdown 2>/dev/null)" ]; then
    # Simple move since filenames no longer contain spaces (replaced with underscores in fetch_docs.py)
    mv limacharlie/raw_markdown/* limacharlie/doc/
    echo -e "${GREEN}✓ Files moved successfully${NC}"
else
    echo "Warning: raw_markdown directory is empty or doesn't exist"
fi
echo ""

# Step 4: Add new doc files to git
echo -e "${BLUE}Step 4/5: Adding new doc files to git...${NC}"
if [ -d "limacharlie/doc" ] && [ "$(ls -A limacharlie/doc 2>/dev/null)" ]; then
    # Add all files recursively (no spaces in filenames since fetch_docs.py replaces them with underscores)
    git add limacharlie/doc/
    echo -e "${GREEN}✓ New doc files added to git${NC}"
else
    echo "Warning: No doc files to add to git"
fi

echo ""
echo "========================================"
echo -e "${GREEN}Pipeline completed successfully!${NC}"
echo "========================================"
echo "Output location: limacharlie/doc/"
echo "Next: Review changes and commit with: git commit -m 'Update documentation'"
echo ""
