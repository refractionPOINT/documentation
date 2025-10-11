# LimaCharlie Documentation Pipeline

Automated pipeline for fetching, converting, and optimizing LimaCharlie documentation for LLM consumption.

## Features

- Dynamic structure discovery from docs.limacharlie.io
- Content-aware change detection
- LLM-optimized markdown generation
- API signature extraction
- Git-based change tracking
- Verification for correctness

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Full pipeline run
python -m doc-pipeline.cli

# Dry run
python -m doc-pipeline.cli --dry-run

# Skip git commit
python -m doc-pipeline.cli --no-commit
```

## Architecture

```
FETCH → CONVERT → ANALYZE → ENHANCE → VERIFY → DETECT
```

Each phase saves intermediate state for debugging/resumption.
