# LimaCharlie Documentation Pipeline

Automated pipeline for fetching, converting, and optimizing LimaCharlie documentation for LLM consumption.

## Overview

This pipeline transforms the LimaCharlie documentation website into clean, structured markdown optimized for Large Language Models. It provides:

- **Dynamic Discovery**: Automatically finds all documentation pages
- **Content-Aware Processing**: Detects structural and content changes
- **LLM Optimization**: Metadata extraction, API indexing, cross-references
- **Verification**: Ensures correctness against source content
- **Change Tracking**: Git-based diff reporting

## Features

### Automated Discovery & Fetching
- Crawls docs.limacharlie.io navigation
- Discovers all pages automatically
- Handles rate limiting and retries
- Fallback discovery for reliability

### Clean Conversion
- HTML → Markdown using markitdown
- Removes Document360 UI artifacts
- Preserves code blocks, links, structure
- Normalizes formatting for consistency

### Content Analysis
- Extracts metadata (summary, keywords, complexity)
- Identifies API signatures and endpoints
- Detects CLI commands
- Builds comprehensive API index

### LLM Optimizations
- Adds cross-references between related pages
- Optimizes heading hierarchy
- Enhances code blocks with language tags
- Consistent formatting throughout

### Verification
- Validates content completeness
- Detects hallucinated or missed APIs
- Verifies metadata accuracy
- Checks cross-references
- Generates detailed reports

### Change Detection
- Git-based tracking
- Categorizes structural vs content changes
- Identifies significant updates
- Human-readable diff reports

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

Requirements:
- Python 3.8+
- Git (for change tracking)
- Internet connection (for fetching)

## Usage

### Quick Start

```bash
# Run full pipeline (from parent directory containing doc-pipeline/)
python3 -m doc-pipeline

# Or run CLI directly from inside doc-pipeline/
cd doc-pipeline
python3 cli.py

# Output will be in: limacharlie-docs-markdown/
```

**Note**: When using `python3 -m doc-pipeline`, run from the directory that contains the `doc-pipeline/` folder.

### Command Line Options

```bash
# Discover structure only (dry run)
python3 -m doc-pipeline --dry-run

# Skip git commit
python3 -m doc-pipeline --no-commit

# Skip verification
python3 -m doc-pipeline --no-verify

# Custom output directory
python3 -m doc-pipeline --output-dir ./my-docs

# Fail on critical verification issues
python3 -m doc-pipeline --fail-on-critical

# Slower rate limiting
python3 -m doc-pipeline --rate-limit 1.0
```

### Programmatic Usage

```python
from doc_pipeline.config import Config
from doc_pipeline.pipeline import run_pipeline

config = Config(
    output_dir="my-docs",
    rate_limit_delay=1.0,
    extract_api_signatures=True,
    verify_content=True,
    fail_on_critical=True,
)

success = run_pipeline(config)
```

## Architecture

### Pipeline Phases

```
Input: docs.limacharlie.io
  ↓
[FETCH] → Discover structure + Download HTML
  ↓
[CONVERT] → HTML to markdown + Clean artifacts
  ↓
[ANALYZE] → Extract metadata + API signatures
  ↓
[ENHANCE] → Add cross-refs + Optimize structure
  ↓
[VERIFY] → Validate correctness
  ↓
[DETECT] → Git diff + Change report
  ↓
Output: Optimized markdown + Reports
```

### Project Structure

```
doc-pipeline/
├── config.py           # Configuration
├── models.py           # Data structures
├── pipeline.py         # Main orchestrator
├── cli.py             # Command-line interface
├── lib/
│   ├── fetch.py       # Fetching & discovery
│   ├── convert.py     # HTML → Markdown
│   ├── analyze.py     # Metadata extraction
│   ├── enhance.py     # LLM optimizations
│   ├── verify.py      # Correctness checking
│   └── detect.py      # Change detection
└── tests/
    ├── test_fetch.py
    ├── test_convert.py
    ├── test_analyze.py
    ├── test_verify.py
    └── test_integration.py
```

## Output Files

### Generated Documentation

- `limacharlie-docs-markdown/<category>/<page>.md` - Individual pages
- `limacharlie-docs-markdown/COMBINED.md` - All docs in one file
- `limacharlie-docs-markdown/API_INDEX.md` - Searchable API reference
- `limacharlie-docs-markdown/METADATA_INDEX.json` - Structured metadata

### Pipeline State

- `.doc-pipeline-state/01-fetch.json` - After fetch phase
- `.doc-pipeline-state/02-convert.json` - After conversion
- `.doc-pipeline-state/03-analyze.json` - After analysis
- `.doc-pipeline-state/04-enhance.json` - After enhancement
- `.doc-pipeline-state/05-verify.json` - Final state
- `.doc-pipeline-state/verification_report.json` - Verification results
- `.doc-pipeline-state/change_report.json` - Git diff analysis

## Configuration

Edit `config.py` or pass custom `Config` object:

```python
@dataclass
class Config:
    # Source
    base_url: str = "https://docs.limacharlie.io"
    docs_path: str = "/docs"

    # Output
    output_dir: Path = Path("limacharlie-docs-markdown")
    state_dir: Path = Path(".doc-pipeline-state")

    # Behavior
    rate_limit_delay: float = 0.5
    request_timeout: int = 30
    retry_attempts: int = 3

    # Features
    extract_api_signatures: bool = True
    generate_summaries: bool = True
    add_cross_references: bool = True
    optimize_headings: bool = True

    # Verification
    verify_content: bool = True
    verify_apis: bool = True
    verify_metadata: bool = True
    fail_on_critical: bool = False

    # Git
    git_commit_changes: bool = True
    git_commit_message: str = "Update LimaCharlie documentation"
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_fetch.py -v

# Run integration tests
pytest tests/test_integration.py -v
```

## Troubleshooting

### Pipeline Fails During FETCH
- Check internet connection
- Verify docs.limacharlie.io is accessible
- Try slower rate limiting: `--rate-limit 2.0`

### Verification Shows Critical Issues
- Review `.doc-pipeline-state/verification_report.json`
- Check specific pages mentioned
- Use `--no-verify` to skip if needed

### Git Commit Fails
- Ensure you're in a git repository
- Check git status and resolve conflicts
- Use `--no-commit` to skip git integration

## Contributing

Contributions welcome! Please:
1. Write tests for new features
2. Update documentation
3. Follow existing code style
4. Add type hints

## License

See LICENSE file in repository root.

## See Also

- `PIPELINE_USAGE.md` - Detailed usage guide
- `tests/` - Test examples
- `lib/` - Module documentation
