# LimaCharlie Documentation

Official documentation for **LimaCharlie**, the SecOps Cloud Platform.

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

LimaCharlie is a SecOps Cloud Platform providing:

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

## Resources

- **Live Docs**: https://refractionpoint.github.io/documentation/
- **Platform**: https://limacharlie.io
- **Web Console**: https://app.limacharlie.io
- **Community**: https://community.limacharlie.io

