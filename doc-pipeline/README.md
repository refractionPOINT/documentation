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

### Command Line Options

```bash
# Full pipeline run (default)
python -m doc_pipeline

# Discover structure only (dry run)
python -m doc_pipeline --dry-run

# Skip git commit
python -m doc_pipeline --no-commit

# Skip verification phase
python -m doc_pipeline --no-verify

# Custom output directory
python -m doc_pipeline --output-dir ./my-docs

# Fail on critical verification issues
python -m doc_pipeline --fail-on-critical

# Slower rate limiting (1 second between requests)
python -m doc_pipeline --rate-limit 1.0
```

### Output Files

After a successful run, you'll find:

**Generated Documentation:**
- `limacharlie-docs-markdown/` - Individual markdown files organized by category
- `limacharlie-docs-markdown/COMBINED.md` - All documentation in one file
- `limacharlie-docs-markdown/API_INDEX.md` - Searchable API reference
- `limacharlie-docs-markdown/METADATA_INDEX.json` - Metadata for all pages

**Pipeline State:**
- `.doc-pipeline-state/01-fetch.json` - State after fetch phase
- `.doc-pipeline-state/02-convert.json` - State after conversion
- `.doc-pipeline-state/03-analyze.json` - State after analysis
- `.doc-pipeline-state/04-enhance.json` - State after enhancement
- `.doc-pipeline-state/05-verify.json` - Final state
- `.doc-pipeline-state/verification_report.json` - Verification results
- `.doc-pipeline-state/change_report.json` - Git change analysis

## Architecture

```
FETCH → CONVERT → ANALYZE → ENHANCE → VERIFY → DETECT
```

Each phase saves intermediate state for debugging/resumption.
