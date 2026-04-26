# LimaCharlie Documentation

Official documentation for **LimaCharlie**, the Agentic SecOps Workspace.

**Live Site:** [https://refractionpoint.github.io/documentation/](https://refractionpoint.github.io/documentation/)

## Repository Structure

```
docs/
├── 1-getting-started/      # Introduction, quickstart, use cases
├── 2-sensors-deployment/   # Sensors, adapters, installation
├── 3-detection-response/   # D&R rules, examples, managed rulesets
├── 4-data-queries/         # LCQL, query console, events
├── 5-integrations/         # Outputs, extensions, API integrations
├── 6-developer-guide/      # SDKs, CLI, building extensions
├── 7-administration/       # Access, billing, config hive
└── 8-reference/            # Commands, events, operators, FAQ
```

---

## What is LimaCharlie?

LimaCharlie is a Agentic SecOps Workspace providing:

- **Endpoint Detection & Response (EDR)** - Windows, Linux, macOS, Chrome, containers
- **Detection & Response Rules** - Custom detection logic with automated responses
- **Real-time Telemetry** - Centralized event streaming and data collection
- **Adapters** - Ingest logs from cloud providers, security tools, SaaS apps
- **Extensions** - Velociraptor, YARA, Zeek, and more
- **API-first Architecture** - Full platform control via REST API and SDKs

## Quick Navigation

| Section | Description |
|---------|-------------|
| [Getting Started](docs/1-getting-started/) | Introduction, quickstart, use cases |
| [Sensors](docs/2-sensors-deployment/) | Endpoint agents, adapters, installation |
| [Detection & Response](docs/3-detection-response/) | D&R rules, examples, managed rulesets |
| [Data & Queries](docs/4-data-queries/) | LCQL, query console, events |
| [Integrations](docs/5-integrations/) | Outputs, extensions, API integrations |
| [Developer Guide](docs/6-developer-guide/) | SDKs, CLI, building extensions |
| [Administration](docs/7-administration/) | Access, billing, config hive |
| [Reference](docs/8-reference/) | Commands, events, operators, FAQ |

## SDK Documentation

| SDK | Install | Docs |
|-----|---------|------|
| **Python** | `pip install limacharlie` | [Python SDK](docs/6-developer-guide/sdks/python-sdk.md) |
| **Go** | `go get github.com/refractionPOINT/go-limacharlie` | [Go SDK](docs/6-developer-guide/sdks/go-sdk.md) |

## AI / LLM Consumption

This site publishes an [`llms.txt`](https://llmstxt.org/) index at
[`https://docs.limacharlie.io/llms.txt`](https://docs.limacharlie.io/llms.txt) — a
machine-readable map of every documentation page, intended for LLMs, agents, and
other automated consumers.

It is generated at build time by the MkDocs hook in `hooks/llms_txt.py`
(wired in via `hooks:` in `mkdocs.yml`) and written directly into the built
`site/`. The file is **not** tracked in git — it is purely derived from
`mkdocs.yml`'s nav and each page's first H1, so it stays in sync automatically.

To preview it locally:

```bash
mkdocs build
cat site/llms.txt
```

`mkdocs serve` also runs the hook on every rebuild.

## Resources

- **Live Docs**: https://refractionpoint.github.io/documentation/
- **Platform**: https://limacharlie.io
- **Web Console**: https://app.limacharlie.io
- **Community**: https://community.limacharlie.com

