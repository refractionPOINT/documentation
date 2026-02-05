# LimaCharlie Documentation

Official documentation for **LimaCharlie**, the SecOps Cloud Platform.

**Live Site:** [https://refractionpoint.github.io/documentation/](https://refractionpoint.github.io/documentation/)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Preview locally with live reload
mkdocs serve

# Open http://127.0.0.1:8000/documentation/
```

---

## Contributing to Documentation

### Adding New Documentation

1. **Create the markdown file** in the appropriate folder:
   ```
   docs/2-sensors-deployment/adapters/types/my-new-adapter.md
   ```

2. **Add to navigation** in `mkdocs.yml`:
   ```yaml
   - Adapters:
       - My New Adapter: 2-sensors-deployment/adapters/types/my-new-adapter.md
   ```

3. **Preview locally** to verify:
   ```bash
   mkdocs serve
   # Open http://127.0.0.1:8000/documentation/
   ```

4. **Commit and push** (or create a PR):
   ```bash
   git add docs/ mkdocs.yml
   git commit -m "Add documentation for My New Adapter"
   git push
   ```

### Modifying Documentation

1. **Edit the markdown file** directly

2. **Preview locally** to verify changes:
   ```bash
   mkdocs serve
   ```

3. **Commit and push**:
   ```bash
   git add docs/path/to/modified-file.md
   git commit -m "Update documentation for XYZ"
   git push
   ```

No need to modify `mkdocs.yml` unless changing the page title in navigation.

### Deleting Documentation

1. **Delete the markdown file**

2. **Remove from navigation** in `mkdocs.yml`

3. **Search for broken links** - check if other pages link to the deleted page:
   ```bash
   grep -r "deleted-file.md" docs/
   ```

4. **Commit and push**:
   ```bash
   git add -A
   git commit -m "Remove deprecated XYZ documentation"
   git push
   ```

### Pull Request Workflow

When you open a PR:

1. **Automated checks run:**
   - Documentation builds with `--strict` mode
   - Link checker scans for broken links
   - Markdown linting validates formatting

2. **Preview deployment** is created automatically at:
   ```
   https://refractionpoint.github.io/documentation/pr-preview/pr-{NUMBER}/
   ```

3. **Review and merge** - changes deploy automatically to the live site

### Code Block Syntax Highlighting

Use language-specific code fences for syntax highlighting:

~~~markdown
```yaml
detect:
  op: is
  path: event/FILE_PATH
  value: malware.exe
```

```bash
limacharlie sensor list --json
```

```python
import limacharlie
manager = limacharlie.Manager(oid='...', secret_api_key='...')
```
~~~

Supported languages: `yaml`, `bash`, `python`, `go`, `json`, `powershell`

---

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

## GitHub Actions

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `docs.yml` | Push to master | Build & deploy to GitHub Pages |
| `pr-preview.yml` | Pull request | Deploy preview, add PR comment with link |
| `link-checker.yml` | PR, push, weekly | Check for broken links, lint markdown |

## Resources

- **Live Docs**: https://refractionpoint.github.io/documentation/
- **Platform**: https://limacharlie.io
- **Web Console**: https://app.limacharlie.io
- **Community**: https://community.limacharlie.io

