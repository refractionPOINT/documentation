# Command Line Interface

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

The `limacharlie cloudsec` command group (Python SDK/CLI v2) covers the full
Cloud Security API surface. Every command supports the global options
(`--oid`, `--output json|yaml|csv|table`, `--filter <jmespath>`), and every
command and subgroup answers `--ai-help` with task-oriented guidance.

```bash
pip install limacharlie
limacharlie cloudsec --help
```

Configuration (providers, policies, saved queries) is managed with the
standard `limacharlie hive` commands — see
[Configuration](configuration.md); this group is the query and triage
surface.

## At a glance

```bash
# Posture
limacharlie cloudsec overview --trend-days 90
limacharlie cloudsec changes --limit 100
limacharlie cloudsec risk-trend
limacharlie cloudsec scan-status --provider gcp

# Multi-org fleet posture (MSSP) — spans every org your credentials can see,
# narrowable with repeatable --oid and/or an org --group
limacharlie cloudsec fleet overview
limacharlie cloudsec fleet overview --group <GROUP_ID> --trend-days 90

# Findings worklist + triage
limacharlie cloudsec finding list --severity CRITICAL --class toxic_combination --kev
limacharlie cloudsec finding facets --status open
limacharlie cloudsec finding get fnd_0a1b...
limacharlie cloudsec finding resolve fnd_0a1b... --kind mitigated --reason "SG tightened"
limacharlie cloudsec finding resolve fnd_0a1b... --kind open          # reopen
limacharlie cloudsec finding bulk-resolve --finding-id fnd_a --finding-id fnd_b --kind accepted
limacharlie cloudsec finding set-owner fnd_0a1b... --owner alice@acme.com
limacharlie cloudsec finding set-ticket fnd_0a1b... --ticket JIRA-1234

# Attack paths, chokepoints
limacharlie cloudsec attack-path list --severity CRITICAL
limacharlie cloudsec chokepoint list
limacharlie cloudsec chokepoint dismiss "lcrn:..." --reason "bastion by design"
limacharlie cloudsec chokepoint restore "lcrn:..."

# Identity & data
limacharlie cloudsec ciem public-access
limacharlie cloudsec ciem facets
limacharlie cloudsec data-security facets

# Inventory & graph
limacharlie cloudsec inventory list --type <resource-type> -q prod --limit 50
limacharlie cloudsec inventory list --provider okta      # scope to one provider's sweep
limacharlie cloudsec inventory facets
limacharlie cloudsec resource get "lcrn:..."
limacharlie cloudsec graph neighbors "lcrn:..." --limit 200
limacharlie cloudsec query list
limacharlie cloudsec query run --named public-buckets
limacharlie cloudsec query run --text "public bucket with sensitive data"

# Compliance
limacharlie cloudsec compliance report --framework cis-gcp
limacharlie cloudsec compliance report --assignment prod-cis
limacharlie cloudsec compliance frameworks
limacharlie cloudsec compliance assignments

# Sensors <-> cloud assets
limacharlie cloudsec resolve sensors $SID1 $SID2
limacharlie cloudsec resolve assets "lcrn:..."

# CAASM
limacharlie cloudsec caasm assets -q laptop
limacharlie cloudsec caasm coverage --status open
limacharlie cloudsec caasm policy get
limacharlie cloudsec caasm policy set --input-file coverage.json
limacharlie cloudsec caasm ingest --source okta --records-file users.json

# Providers: credential preflight + coverage manifests
limacharlie cloudsec provider test --input-file provider.json
limacharlie cloudsec provider manifest --type gcp

# CSV exports (server walks the FULL filtered set, 100k-row cap)
limacharlie cloudsec export findings -o findings.csv --severity CRITICAL
limacharlie cloudsec export inventory -o inventory.csv --provider gcp
limacharlie cloudsec export compliance -o cis-gcp.csv
limacharlie cloudsec export query --named public-buckets -o rows.csv
```

## Filtering and pagination

List commands accept repeatable filters (OR within a key, AND across keys),
free-text search, sorting, and keyset pagination:

```bash
limacharlie cloudsec finding list \
  --severity CRITICAL --severity HIGH \
  --status open -q payment \
  --sort lc_risk --order desc \
  --limit 50
# ...then pass the returned next_cursor back:
limacharlie cloudsec finding list --cursor "<next_cursor>" --limit 50
```

Boolean tri-state flags (`--kev/--no-kev`, `--reachable/--no-reachable`)
send the filter only when given, so the server default applies otherwise.
Findings sort keys: `lc_risk` (the default), `severity`, `first_seen`;
`--order` is `desc` by default.

## Scripting

The SDK class behind the CLI is available directly:

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.cloudsec import CloudSec

cs = CloudSec(Organization(Client(oid="...")))
page = cs.list_findings(severity=["CRITICAL"], kev=True, limit=100)
for f in page["findings"]:
    print(f["lc_risk"], f["title"], f["resource_urn"])
```

Each method mirrors one API route and returns the raw response dict; see the
[API Reference](api-reference.md) for response shapes.
