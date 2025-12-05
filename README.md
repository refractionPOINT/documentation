# LimaCharlie Documentation for AI/LLM Integration

This repository contains comprehensive markdown documentation for **LimaCharlie**, the SecOps Cloud Platform. The documentation has been specifically formatted and structured for optimal consumption by AI assistants, Large Language Models (LLMs), and automated tools to enable better integration and code generation.

## What is LimaCharlie?

LimaCharlie is a SecOps Cloud Platform that delivers comprehensive enterprise security protection. It provides:

- **Endpoint Detection & Response (EDR)**: Deploy sensors across Windows, Linux, macOS, Chrome, and more
- **Detection & Response Rules**: Build custom detection logic with automated response actions
- **Real-time Telemetry**: Centralized event streaming and data collection
- **API Integrations**: Connect with threat intelligence, SIEM, and security tools
- **Extensions & Add-ons**: Expand capabilities with purpose-built integrations
- **Cloud-native Architecture**: Scalable, API-first platform for modern security operations

## Repository Purpose

This repository serves multiple audiences:

### For AI Assistants & LLMs
- Provides structured, markdown-formatted documentation optimized for context consumption
- Enables code generation for LimaCharlie integrations (SDKs, API calls, detection rules)
- Includes complete SDK documentation with examples for Go and Python
- Offers detailed API specifications and data structure definitions

### For Developers
- Quick reference for LimaCharlie platform features and capabilities
- Comprehensive SDK documentation with practical examples
- Detection rule patterns and best practices
- Integration guides for third-party tools

### For Security Engineers
- Detection and response rule examples
- Sensor deployment and management guides
- Output configuration for SIEM/logging platforms
- Incident response workflows

### For Documentation Site
- **Official documentation site**: This repository is the source for the official LimaCharlie documentation website
- Built with **MkDocs Material** for a modern, searchable documentation experience
- Automatically deployed to GitHub Pages with every commit
- Custom branding matching LimaCharlie's visual identity

## Documentation Website

The documentation is published as a searchable website at: [https://refractionpoint.github.io/documentation/](https://refractionpoint.github.io/documentation/)

### Local Development

To preview the documentation website locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Serve with live reload at http://127.0.0.1:8000
mkdocs serve

# Build static site
mkdocs build
```

For detailed setup information, see [DOCS_SETUP.md](DOCS_SETUP.md).

### Contributing to Documentation

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Repository Structure

```
documentation/
├── README.md                       # This file
├── LICENSE                         # Apache 2.0 License
├── limacharlie/                    # Platform documentation
│   ├── doc/                        # 275+ markdown documentation files
│   │   ├── Getting_Started/        # Platform introduction and quickstart
│   │   ├── Sensors/                # Sensor deployment and management
│   │   ├── Detection_and_Response/ # D&R rules, detection logic
│   │   ├── Events/                 # Event types and telemetry
│   │   ├── Outputs/                # SIEM, webhook, and data outputs
│   │   ├── Add-Ons/                # Extensions, integrations, API add-ons
│   │   ├── Platform_Management/    # Organization and configuration
│   │   ├── Query_Console/          # LCQL query language
│   │   ├── Telemetry/              # Event schemas and data formats
│   │   ├── Connecting/             # API and connectivity
│   │   ├── FAQ/                    # Frequently asked questions
│   │   └── Tutorials/              # Step-by-step guides
│   └── pipeline/                   # Documentation generation tools
│       ├── fetch_docs.py           # Fetch docs from docs.limacharlie.io
│       ├── clean_raw.py            # Process raw documentation
│       └── README.md               # Pipeline documentation
├── go-sdk/                         # Go SDK Documentation
│   ├── README.md                   # Complete Go SDK reference
│   └── REGENERATION_RECIPE.md      # Instructions for updating docs
└── python-sdk/                     # Python SDK Documentation
    ├── README.md                   # Complete Python SDK reference
    └── REGENERATION_RECIPE.md      # Instructions for updating docs
```

## Quick Navigation

### Getting Started with LimaCharlie
- [What is LimaCharlie?](limacharlie/doc/Getting_Started/what-is-limacharlie.md)
- [Quickstart Guide](limacharlie/doc/Getting_Started/quickstart.md)
- [Core Concepts](limacharlie/doc/Getting_Started/limacharlie-core-concepts.md)

### Detection & Response
- [Detection & Response Overview](limacharlie/doc/Detection_and_Response/)
- [Detection Rule Examples](limacharlie/doc/Detection_and_Response/detection-and-response-examples.md)
- [Detection on Alternate Targets](limacharlie/doc/Detection_and_Response/detection-on-alternate-targets.md)

### Sensor Management
- [Sensor Installation](limacharlie/doc/Sensors/)
- [Installation Keys](limacharlie/doc/Sensors/installation-keys.md)
- [Sensor Connectivity](limacharlie/doc/Sensors/sensor-connectivity.md)
- [Sensor Tags](limacharlie/doc/Sensors/sensor-tags.md)

### API Integrations
- [VirusTotal Integration](limacharlie/doc/Add-Ons/API_Integrations/api-integrations-virustotal.md)
- [GreyNoise Integration](limacharlie/doc/Add-Ons/API_Integrations/api-integrations-greynoise.md)
- [Hybrid Analysis Integration](limacharlie/doc/Add-Ons/API_Integrations/api-integrations-hybrid-analysis.md)

### Query & Analysis
- [Query with CLI](limacharlie/doc/Query_Console/query-with-cli.md)

## SDK Documentation

### Go SDK
The Go SDK provides a comprehensive client library for programmatic interaction with LimaCharlie.

**Features:**
- Sensor management (list, task, isolate, tag)
- Detection & Response rule management
- Artifact collection and export
- Organization administration
- Real-time event streaming via Firehose

**Documentation:** [go-sdk/README.md](go-sdk/README.md)

**Installation:**
```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie@latest
```

### Python SDK
The Python SDK offers a full-featured interface for LimaCharlie platform operations.

**Features:**
- Manager class for all platform operations
- Sensor tasking and management
- Real-time streaming (Firehose/Spout)
- Detection rule management via Hive
- LCQL query support
- Artifact and payload management

**Documentation:** [python-sdk/README.md](python-sdk/README.md)

**Installation:**
```bash
pip install limacharlie
```

## For AI/LLM Assistants

### How to Use This Documentation

When helping users with LimaCharlie integrations:

1. **Start with Context**: Reference [What is LimaCharlie?](limacharlie/doc/Getting_Started/what-is-limacharlie.md) to understand the platform

2. **SDK Selection**:
   - For Go projects → Use [go-sdk/README.md](go-sdk/README.md)
   - For Python projects → Use [python-sdk/README.md](python-sdk/README.md)

3. **Code Generation**:
   - Both SDK READMEs contain complete examples with proper error handling
   - All code examples are production-ready and include authentication patterns
   - Use the exact method signatures and data structures documented

4. **Detection Rules**:
   - Reference [Detection & Response Examples](limacharlie/doc/Detection_and_Response/detection-and-response-examples.md)
   - Detection rules use YAML format with `op` operators and `path` selectors
   - Include both detection and response actions

5. **Data Structures**:
   - Event schemas are documented in [Telemetry](limacharlie/doc/Telemetry/)
   - SDK READMEs include complete struct/class definitions
   - All field names, types, and required/optional indicators are specified

### Common Integration Patterns

**Authentication:**
```python
# Python
import limacharlie
manager = limacharlie.Manager(oid='ORG_ID', secret_api_key='API_KEY')
```

```go
// Go
client := limacharlie.NewClientFromLoader(
    limacharlie.ClientOptions{
        OID:    "your-oid",
        APIKey: "your-api-key",
    },
)
```

**Sensor Operations:**
- Listing sensors: Both SDKs provide `ListSensors()` or `sensors()` methods
- Tasking sensors: Use `task()` method with command strings
- Real-time events: Python uses `Spout`/`Firehose`, Go uses firehose package

**Detection Rules:**
- Rules are YAML-based with detection criteria and response actions
- Use operators like `is`, `contains`, `matches`, `greater than`
- Responses include `report`, `task`, `add tag`, `isolate network`

## Documentation Pipeline

The `limacharlie/pipeline/` directory contains scripts for fetching and processing documentation from the official LimaCharlie documentation site.

### Fetching Documentation

```bash
# Install dependencies
pip3 install requests beautifulsoup4 html2text

# Fetch all documentation
python3 limacharlie/pipeline/fetch_docs.py
```

The pipeline:
1. Extracts Algolia API credentials from docs.limacharlie.io
2. Fetches all public, non-deleted articles (~612 articles)
3. Creates directory structure based on article breadcrumbs
4. Saves articles as markdown with metadata headers

**Output:** Articles are saved to `limacharlie/doc/` with proper categorization.

See [limacharlie/pipeline/README.md](limacharlie/pipeline/README.md) for details.

## Regenerating SDK Documentation

Both SDKs include regeneration recipes for AI assistants to update documentation when SDK code changes:

- **Go SDK**: [go-sdk/REGENERATION_RECIPE.md](go-sdk/REGENERATION_RECIPE.md)
- **Python SDK**: [python-sdk/REGENERATION_RECIPE.md](python-sdk/REGENERATION_RECIPE.md)

These recipes provide step-by-step instructions for analyzing SDK source code and generating comprehensive documentation.

## Contributing

### Documentation Updates

Platform documentation is primarily sourced from https://docs.limacharlie.io and should be updated via the pipeline scripts.

### SDK Documentation Updates

SDK documentation should be regenerated when the SDK code changes. Follow the regeneration recipes in each SDK directory.

### Improvements

For improvements to documentation structure, formatting, or AI/LLM optimization:
1. Fork this repository
2. Make your changes
3. Submit a pull request

## Statistics

- **Platform Documentation**: 275+ markdown files
- **SDK Documentation**: 2 comprehensive SDK references
- **Content Coverage**: Complete platform documentation including getting started, sensors, detection, APIs, outputs, and more
- **Target Audience**: AI assistants, LLMs, developers, security engineers

## Additional Resources

### Official Links
- **LimaCharlie Platform**: https://limacharlie.io
- **Web Console**: https://app.limacharlie.io
- **API Documentation**: https://api.limacharlie.io/openapi
- **Official Documentation**: https://docs.limacharlie.io
- **Community Slack**: https://slack.limacharlie.io

### SDK Repositories
- **Go SDK**: https://github.com/refractionPOINT/go-limacharlie
- **Python SDK**: https://github.com/refractionPOINT/python-limacharlie

### Support
- **Support Email**: support@limacharlie.io
- **GitHub Issues**: Use the respective SDK repository for SDK-specific issues

## License

This documentation is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for the full license text.

## Acknowledgments

LimaCharlie is developed and maintained by refractionPOINT. This documentation repository is designed to make the platform more accessible to AI assistants and automated tools, enabling better security integrations and code generation.

---

**Repository Maintained By**: refractionPOINT
**Last Updated**: 2025
**Documentation Format**: Markdown (AI/LLM optimized)
