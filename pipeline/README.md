# LimaCharlie Documentation Transformation Pipeline

A robust, LLM-powered pipeline for transforming docs.limacharlie.io documentation into clean, LLM-optimized markdown.

## Philosophy

**No more brittle regex and assumptions!** This pipeline uses:
- **Algolia API** for comprehensive discovery (not web scraping guesswork)
- **markitdown** for reliable HTML→MD conversion
- **Claude sub-agents** for intelligent content cleaning (not regex)
- **Parallel processing** for speed
- **Verification** for completeness

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Discovery (01_discover.py)                        │
│  Uses Algolia API + fallback crawling to find ALL pages     │
│  Output: discovered_pages.json                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Fetch (02_fetch.py)                               │
│  Downloads raw HTML for each discovered page                │
│  Output: raw-html/*.html                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Convert (03_convert.py)                           │
│  Uses markitdown to convert HTML → raw Markdown             │
│  Output: raw-markdown/*.md                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: Transform (04_transform.py) ★ KEY INNOVATION      │
│  Parallel Claude sub-agents clean each page                 │
│  Removes UI chrome, keeps documentation content             │
│  Output: cleaned-markdown/*.md                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: Verify (05_verify.py)                             │
│  Checks completeness, generates INDEX.md & COMBINED.md      │
│  Output: INDEX.md, COMBINED.md, verification_report.json    │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

```bash
# Python 3.8+
python3 --version

# Required packages
pip install requests beautifulsoup4 markitdown

# Claude CLI (must be in PATH and authenticated)
claude --version
```

## Quick Start

```bash
# Run the complete pipeline
cd pipeline
python3 run_pipeline.py
```

That's it! The pipeline will:
1. Discover all documentation pages (~5-10 min)
2. Download HTML (~5-10 min)
3. Convert to markdown (~2-5 min)
4. Clean with Claude (~30-60 min depending on doc size)
5. Verify and generate outputs (~1-2 min)

## Usage

### Run Complete Pipeline

```bash
python3 run_pipeline.py
```

### Run Individual Phases

```bash
# Only discovery
python3 run_pipeline.py --start 1 --end 1

# Only transformation (assumes previous phases done)
python3 run_pipeline.py --start 4 --end 4

# Resume from phase 3
python3 run_pipeline.py --start 3
```

### Run Individual Scripts

```bash
cd pipeline

# Phase 1: Discovery
python3 01_discover.py

# Phase 2: Fetch
python3 02_fetch.py

# Phase 3: Convert
python3 03_convert.py

# Phase 4: Transform
python3 04_transform.py

# Phase 5: Verify
python3 05_verify.py
```

## Configuration

Edit `config.py` to customize:

```python
# Parallel workers
MAX_PARALLEL_WORKERS = 10

# Fetch delay (be respectful to servers)
FETCH_DELAY_SECONDS = 0.5

# Claude model
CLAUDE_MODEL = "sonnet"  # or set via env var
```

Environment variables:
```bash
export MAX_PARALLEL_WORKERS=5
export CLAUDE_MODEL="opus"
export VERBOSE=true
```

## Output Structure

```
output/
├── raw-html/              # Downloaded HTML files
├── raw-markdown/          # Initial markitdown conversion
├── cleaned-markdown/      # Claude-cleaned markdown (main output)
├── topics/                # (Future) Organized by type
│   ├── tasks/
│   ├── concepts/
│   └── reference/
├── metadata/
│   ├── discovered_pages.json
│   ├── transformation_log.json
│   └── verification_report.json
├── INDEX.md               # Navigation file
└── COMBINED.md            # All docs in one file
```

## Key Features

### 1. Comprehensive Discovery
- Uses Algolia search API (Document360's backend)
- Fallback web crawling if Algolia fails
- Discovers ALL pages, not just known ones

### 2. Reliable Conversion
- Uses `markitdown` CLI tool (Microsoft's converter)
- No manual HTML parsing
- Preserves code blocks, tables, links

### 3. Intelligent Cleaning (The Innovation!)
- Each page processed by Claude sub-agent
- Removes navigation, footers, UI chrome
- Preserves documentation content
- No brittle regex patterns
- Adapts to HTML structure changes

### 4. Parallel Processing
- Multiple Claude instances run simultaneously
- Configurable worker count
- Progress tracking

### 5. Verification
- Checks all discovered pages were processed
- Reports missing pages
- Generates organized outputs

## Troubleshooting

### "Claude CLI not found"
```bash
# Check Claude is installed and in PATH
which claude
claude --version

# Make sure you're authenticated
claude auth login
```

### "No pages discovered"
- Check internet connection
- Verify docs.limacharlie.io is accessible
- Check Algolia API keys in config.py (may need updating)

### "Transformation too slow"
```bash
# Reduce parallel workers to avoid rate limits
export MAX_PARALLEL_WORKERS=3
python3 run_pipeline.py --start 4 --end 4
```

### "Some pages failed to transform"
- Check transformation_log.json for details
- Pages with very little content may be skipped
- Rerun phase 4 to retry failed pages

## Advanced Usage

### Custom Cleaning Prompt

Edit `prompts/clean_page.md` to customize how Claude cleans pages.

### Skip Already Processed Files

The pipeline automatically skips files that already exist. To reprocess:

```bash
# Clear outputs
rm -rf output/cleaned-markdown/*

# Rerun transformation
python3 run_pipeline.py --start 4 --end 4
```

### Process Subset of Pages

Edit the discovered_pages.json to remove pages you don't want:

```bash
# Edit discovered pages
nano output/metadata/discovered_pages.json

# Run from fetch phase
python3 run_pipeline.py --start 2
```

## Maintenance

### Update Discovery

When new documentation pages are added:

```bash
# Clear old discovery
rm output/metadata/discovered_pages.json

# Rediscover and process new pages
python3 run_pipeline.py
```

### Update Algolia Keys

If Algolia API keys change, update `config.py`:

```python
ALGOLIA_APP_ID = "new_app_id"
ALGOLIA_API_KEY = "new_api_key"
```

## Pipeline Design Principles

1. **Separation of Concerns**: Each phase does one thing well
2. **Idempotent**: Can rerun phases safely (skips existing files)
3. **Observable**: Detailed logging and progress tracking
4. **Verifiable**: Completeness checks ensure nothing is missed
5. **Maintainable**: No regex soup, clear code, documented prompts
6. **Extensible**: Easy to add new phases (e.g., topic synthesis)

## Future Enhancements

- [ ] Topic synthesis (merge/split pages by semantic meaning)
- [ ] Incremental updates (only process changed pages)
- [ ] Quality scoring (detect poorly cleaned pages)
- [ ] Multi-language support
- [ ] Integration with vector databases

## Performance

Typical run time for ~100 documentation pages:

- **Discovery**: 2-5 minutes
- **Fetch**: 5-10 minutes
- **Convert**: 2-5 minutes
- **Transform**: 30-60 minutes (depends on Claude API)
- **Verify**: 1-2 minutes

**Total**: ~45-80 minutes for complete pipeline

## File Structure

```
pipeline/
├── run_pipeline.py         # Main orchestrator
├── 01_discover.py          # Phase 1: Discovery
├── 02_fetch.py             # Phase 2: Fetch HTML
├── 03_convert.py           # Phase 3: Convert to MD
├── 04_transform.py         # Phase 4: Clean with Claude
├── 05_verify.py            # Phase 5: Verify & generate
├── config.py               # Configuration
├── utils.py                # Shared utilities
├── prompts/
│   ├── clean_page.md       # Cleaning prompt
│   └── synthesize_topics.md # (Future) Topic synthesis
└── README.md               # This file
```

## Contributing

To add new features:

1. Add phase script: `06_your_phase.py`
2. Update `run_pipeline.py` to include new phase
3. Add prompt template if using Claude
4. Update this README

## License

Same as parent repository.

## Support

For issues or questions about the pipeline:
1. Check the logs in stderr
2. Review `metadata/transformation_log.json`
3. Check `metadata/verification_report.json`
4. Open an issue with relevant log excerpts
