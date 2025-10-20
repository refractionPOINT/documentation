# LimaCharlie Documentation Repository

This repository contains LLM-optimized documentation for the [LimaCharlie SecOps Cloud Platform](https://limacharlie.io), designed to be consumed programmatically by Large Language Models and other automated tools.

## Overview

LimaCharlie is a SecOps Cloud Platform that provides comprehensive enterprise protection through unified telemetry, detection & response rules, and automated security operations. This repository serves as a machine-readable documentation source, containing:

- **275+ markdown documents** covering the entire LimaCharlie platform
- **SDK documentation** for Go and Python client libraries
- **Automated pipeline** to fetch and convert documentation from docs.limacharlie.io
- **Structured metadata** with YAML frontmatter for programmatic access

## Repository Structure

```
documentation/
├── limacharlie/                    # LimaCharlie platform documentation
│   ├── doc/                        # Organized markdown documentation
│   │   ├── Add-Ons/               # Extensions, integrations, services
│   │   ├── Connecting/            # Connectivity and networking
│   │   ├── Detection_and_Response/ # D&R rules and automation
│   │   ├── Events/                # Event types and telemetry
│   │   ├── FAQ/                   # Frequently asked questions
│   │   ├── Getting_Started/       # Onboarding guides
│   │   ├── LimaCharlie.io_REST_API/ # REST API documentation
│   │   ├── Outputs/               # Data outputs and integrations
│   │   ├── Platform_Management/   # Organization and user management
│   │   ├── Query_Console/         # LCQL query language
│   │   ├── Sensors/               # Sensor deployment and management
│   │   ├── Telemetry/             # Telemetry data structures
│   │   └── Tutorials/             # Step-by-step tutorials
│   ├── pipeline/                  # Documentation fetching pipeline
│   │   ├── fetch_docs.py         # Main fetcher script
│   │   ├── clean_raw.py          # Data cleaning utilities
│   │   ├── test_fetch.py         # Test script (fetches 3 articles)
│   │   ├── run_pipeline.sh       # Pipeline automation script
│   │   └── README.md             # Pipeline documentation
│   └── raw_markdown/              # Raw fetched markdown (generated)
├── go-sdk/                        # Go SDK documentation
│   ├── README.md                 # Comprehensive Go SDK guide
│   └── REGENERATION_RECIPE.md    # SDK regeneration instructions
├── python-sdk/                    # Python SDK documentation
│   ├── README.md                 # Comprehensive Python SDK guide
│   └── REGENERATION_RECIPE.md    # SDK regeneration instructions
└── LICENSE                        # Apache 2.0 License
```

## Using This Documentation

### For LLMs and AI Systems

This documentation is optimized for consumption by Large Language Models:

- **Markdown format**: All content is in clean, semantic markdown
- **Hierarchical organization**: Documents are organized by topic in a clear directory structure
- **Plain text content**: No JavaScript, complex HTML, or dynamic content

### For Developers

The documentation can be:

1. **Indexed and searched** using standard text search tools (grep, ripgrep, etc.)
2. **Parsed programmatically** using markdown parsers
3. **Embedded in RAG systems** for context-aware assistance
4. **Converted to other formats** using pandoc or similar tools

#### Example: Search for specific topics

```bash
# Find all documents about detection rules
grep -r "detection rule" limacharlie/doc/

# Find documents mentioning sensors
rg "sensor" limacharlie/doc/ -l

# Search for API endpoints
grep -r "/api/" limacharlie/doc/LimaCharlie.io_REST_API/
```

## Regenerating Documentation

The documentation pipeline automatically fetches and converts documentation from docs.limacharlie.io.

### Prerequisites

```bash
pip3 install requests beautifulsoup4 markdownify
```

### Full Documentation Fetch

```bash
cd limacharlie/pipeline
python3 fetch_docs.py
```

This will:
1. Extract Algolia API credentials from docs.limacharlie.io
2. Fetch all ~612 public articles via Algolia API
3. Convert HTML to clean markdown using markdownify
4. Organize files by breadcrumb hierarchy
5. Add YAML metadata headers to each file
6. Support resume capability (skips already downloaded files)

### Test Fetch (First 3 Articles)

```bash
cd limacharlie/pipeline
python3 test_fetch.py
```

### Pipeline Script

```bash
cd limacharlie/pipeline
./run_pipeline.sh
```

### Pipeline Configuration

The fetch script can be configured via constants in `fetch_docs.py`:

- `MAX_WORKERS`: Number of concurrent download threads (default: 10)
- `RATE_LIMIT_DELAY`: Delay between requests in seconds (default: 0.05)
- `MAX_RETRIES`: Maximum retry attempts for failed requests (default: 3)
- `OUTPUT_DIR`: Where to save markdown files (default: `./limacharlie/raw_markdown`)

## SDK Documentation

This repository includes comprehensive documentation for LimaCharlie's official SDKs.

### Go SDK

Location: `go-sdk/README.md`

The Go SDK documentation covers:
- Installation and authentication
- Sensor management and tasking
- Detection & Response rule management
- Artifact collection and export
- Real-time event streaming
- Organization management

**Installation:**
```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie
```

**Quick Example:**
```go
import "github.com/refractionPOINT/go-limacharlie/limacharlie"

client := limacharlie.NewClient()
org := client.Organization(limacharlie.ClientOptions{})
sensors, err := org.ListSensors()
```

See [go-sdk/README.md](go-sdk/README.md) for full documentation.

### Python SDK

Location: `python-sdk/README.md`

The Python SDK documentation covers:
- Multiple authentication methods
- Sensor operations and tasking
- Real-time data streaming (Firehose and Spout)
- Detection rule management via Hive
- Event ingestion and querying
- Artifact and payload management

**Installation:**
```bash
pip install limacharlie
```

**Quick Example:**
```python
import limacharlie

manager = limacharlie.Manager(oid='ORG_ID', secret_api_key='API_KEY')
sensors = manager.sensors()
```

See [python-sdk/README.md](python-sdk/README.md) for full documentation.

## Document Format

### Metadata Structure

Each documentation file includes YAML frontmatter:

```yaml
---
title: Article Title                # Human-readable title
slug: article-slug                   # URL-friendly identifier
breadcrumb: Category > Subcategory   # Hierarchical location
source: https://docs.limacharlie.io/docs/article-slug  # Original URL
articleId: uuid-here                 # Unique identifier
---
```

### Content Organization

- **Hierarchical categories**: Documents are organized by functional area
- **Cross-references**: Links between related documents preserved
- **Code examples**: Inline code blocks with syntax highlighting
- **API schemas**: JSON/YAML structures for API requests/responses

## Contributing

### Adding Documentation

To add new documentation:

1. Add markdown files to the appropriate directory in `limacharlie/doc/`
2. Include YAML frontmatter with required metadata
3. Use relative links for cross-references
4. Follow existing naming conventions (lowercase, hyphens)

### Updating Pipeline

The pipeline scripts are in `limacharlie/pipeline/`:

- `fetch_docs.py`: Main fetcher (modify for new sources)
- `clean_raw.py`: Post-processing utilities
- `test_fetch.py`: Test harness

### SDK Documentation Updates

SDK documentation lives in:
- `go-sdk/README.md` - Update for Go SDK changes
- `python-sdk/README.md` - Update for Python SDK changes

## Use Cases

This repository is designed for:

### 1. LLM Context Injection
Embed documentation in prompts for AI-assisted development, security operations, and automation.

### 2. RAG (Retrieval-Augmented Generation)
Index documentation for semantic search and context-aware assistance.

### 3. Documentation Portals
Convert markdown to HTML, PDF, or other formats for internal documentation sites.

### 4. Automation & Tooling
Parse documentation programmatically to generate code, tests, or validation scripts.

### 5. Offline Reference
Clone repository for offline access to complete LimaCharlie documentation.

## Technical Details

### Fetching Mechanism

The pipeline uses the Algolia API that powers docs.limacharlie.io:

1. Extracts API credentials from page source (algoliaAppId, algoliaSearchKey, algoliaArticlesIndexId)
2. Queries Algolia for all public articles (excludes drafts, deleted, hidden)
3. Fetches article content in plain text format
4. Converts HTML remnants to clean markdown using markdownify
5. Organizes by breadcrumb path

### Filters Applied

Articles are automatically filtered to exclude:
- `isDeleted: true` - Deleted articles
- `isHidden: true` - Hidden articles
- `isDraft: true` - Draft articles
- `exclude: true` - Explicitly excluded articles
- `isCategory: true` - Category entries (not actual content)
- `isUnpublished: true` - Unpublished articles

### Statistics

As of last fetch:
- **Total Algolia entries**: 680
- **Filtered articles**: 612
- **Categories (excluded)**: 68
- **Markdown files**: 275+

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Resources

- **LimaCharlie Platform**: https://limacharlie.io
- **Documentation Site**: https://docs.limacharlie.io
- **REST API Docs**: https://api.limacharlie.io/openapi
- **Go SDK Repository**: https://github.com/refractionPOINT/go-limacharlie
- **Python SDK Repository**: https://github.com/refractionPOINT/python-limacharlie
- **Support**: support@limacharlie.io
- **Community Slack**: https://slack.limacharlie.io

## Maintained By

[refractionPOINT](https://github.com/refractionPOINT) - The team behind LimaCharlie

---

**Note**: This documentation is automatically generated from docs.limacharlie.io. For the latest information, always refer to the official documentation site or regenerate using the pipeline.
