# Documentation Pipeline Usage Guide

This guide explains how to use the LimaCharlie documentation pipeline to generate LLM-optimized documentation.

## Quick Start

```bash
# Install dependencies
pip install -r doc-pipeline/requirements.txt

# Run full pipeline (from parent directory containing doc-pipeline/)
python3 -m doc-pipeline
```

**Important**: The `python3 -m doc-pipeline` command must be run from the directory that **contains** the `doc-pipeline/` folder, not from inside it.

## Understanding the Pipeline

The pipeline runs in 6 phases:

### 1. FETCH
- Discovers all documentation pages from docs.limacharlie.io
- Downloads HTML for each page
- Organizes into categories based on URL patterns

### 2. CONVERT
- Converts HTML to Markdown using markitdown
- Removes Document360 UI artifacts
- Normalizes formatting

### 3. ANALYZE
- Extracts metadata (summary, keywords, complexity)
- Identifies API signatures, endpoints, CLI commands
- Builds comprehensive API index

### 4. ENHANCE
- Adds cross-references between related pages
- Optimizes heading hierarchy
- Enhances code blocks with language tags
- LLM-specific formatting improvements

### 5. VERIFY
- Validates content completeness (word count, code blocks, headings)
- Checks for hallucinated or missed APIs
- Verifies metadata accuracy
- Validates cross-references
- Generates verification report

### 6. DETECT
- Commits changes to git
- Generates change report with categorization
- Identifies structural vs content changes
- Highlights significant updates

## Common Workflows

### First-Time Setup

```bash
# Clone and install
git clone <repo>
cd documentation
pip install -r doc-pipeline/requirements.txt

# Run pipeline
python -m doc_pipeline

# Check output
ls limacharlie-docs-markdown/
cat limacharlie-docs-markdown/COMBINED.md
```

### Regular Updates

```bash
# Pull latest
git pull

# Run pipeline (generates diff report)
python -m doc_pipeline

# Review changes
git log -1 -p
cat .doc-pipeline-state/change_report.json
```

### Debugging Issues

```bash
# Dry run to check discovery
python -m doc_pipeline --dry-run

# Run without commit to inspect output
python -m doc_pipeline --no-commit

# Check intermediate state
cat .doc-pipeline-state/02-convert.json

# Review verification report
cat .doc-pipeline-state/verification_report.json
```

### Custom Configuration

Create a Python script:

```python
from doc_pipeline.config import Config
from doc_pipeline.pipeline import run_pipeline

config = Config(
    output_dir="my-docs",
    rate_limit_delay=1.0,
    fail_on_critical=True,
)

run_pipeline(config)
```

## Output Files Explained

### Individual Markdown Files
`limacharlie-docs-markdown/<category>/<page-slug>.md`
- One file per documentation page
- Clean markdown optimized for LLM consumption
- Preserved code blocks, links, structure

### Combined Documentation
`limacharlie-docs-markdown/COMBINED.md`
- All documentation in a single file
- Organized by category
- Useful for feeding entire context to LLM

### API Index
`limacharlie-docs-markdown/API_INDEX.md`
- Searchable reference of all APIs
- REST endpoints, Python SDK, CLI commands
- Links back to source pages

### Metadata Index
`limacharlie-docs-markdown/METADATA_INDEX.json`
- Structured metadata for all pages
- Summaries, keywords, complexity levels
- Use cases and categorization
- Useful for semantic search

### Verification Report
`.doc-pipeline-state/verification_report.json`
- Lists all verification issues found
- Categorized by severity (critical/warning/info)
- Details of content loss, missing APIs, etc.

### Change Report
`.doc-pipeline-state/change_report.json`
- Git diff analysis
- Structural vs content changes
- Significant updates highlighted
- Useful for understanding what changed upstream

## Troubleshooting

### Pipeline fails during FETCH
- Check internet connection
- Verify docs.limacharlie.io is accessible
- Try slower rate limiting: `--rate-limit 2.0`

### Verification shows critical issues
- Review `.doc-pipeline-state/verification_report.json`
- Check specific pages mentioned in report
- Consider if issues are false positives
- Use `--no-verify` to skip if needed

### Git commit fails
- Ensure you're in a git repository
- Check git status and resolve conflicts
- Use `--no-commit` to skip git integration

### Missing dependencies
```bash
pip install requests beautifulsoup4 markitdown
```

### Rate limiting / timeout errors
```bash
python -m doc_pipeline --rate-limit 2.0
```

## Integration with LLMs

The generated documentation is optimized for LLM consumption:

### For Context Loading
Use `COMBINED.md` to load full documentation context:
```python
with open('limacharlie-docs-markdown/COMBINED.md') as f:
    docs = f.read()

response = llm.query(f"Based on these docs:\n\n{docs}\n\nHow do I...?")
```

### For Semantic Search
Use `METADATA_INDEX.json` for embeddings:
```python
import json

with open('limacharlie-docs-markdown/METADATA_INDEX.json') as f:
    metadata = json.load(f)

# Create embeddings from summaries
for slug, info in metadata.items():
    embedding = create_embedding(info['metadata']['summary'])
    store_embedding(slug, embedding)
```

### For API Reference
Use `API_INDEX.md` for specific API queries:
```python
# Load API index
with open('limacharlie-docs-markdown/API_INDEX.md') as f:
    api_docs = f.read()

# Query specific API
response = llm.query(f"API reference:\n{api_docs}\n\nHow to use sensor.task()?")
```

## Maintenance

### Updating from Upstream
Run the pipeline periodically to stay in sync with docs.limacharlie.io:

```bash
# Weekly/monthly cron job
0 2 * * 1 cd /path/to/documentation && python -m doc_pipeline
```

### Reviewing Changes
After each run, review the change report:

```bash
# View latest commit
git show

# View change report
cat .doc-pipeline-state/change_report.json

# View verification issues
cat .doc-pipeline-state/verification_report.json
```

### Customizing Categories
Edit `doc-pipeline/lib/fetch.py` function `_categorize_page()` to adjust category mappings.

### Adding Custom Enhancements
Extend `doc-pipeline/lib/enhance.py` to add your own LLM optimizations.

## Architecture

See `doc-pipeline/README.md` for detailed architecture documentation.

## Contributing

Found a bug or want to improve the pipeline? See `CONTRIBUTING.md` for guidelines.
