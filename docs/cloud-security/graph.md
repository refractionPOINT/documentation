# Security Graph & Queries

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Every sweep builds a graph of the estate: resources, identities, and data
stores as nodes; reachability, exposure, permissions, and vulnerability
relationships as edges. The graph is what turns three individually-boring
facts into one critical finding — and it is directly explorable.

## The graph model

Nodes are addressed by URN (the same `lcrn:` identifiers used across the
API) and carry type-specific properties: exposure (`is_public`), sensitivity
(`is_sensitive`), vulnerability context (`cve`, `severity`, `in_kev`,
`cvss_score`), and identity insight (human/service kind, external flag, MFA
posture, dormancy, escalation potential, least-privilege suggestions).

Edges carry the relationship semantics:

| Edge | Meaning |
|---|---|
| `can_reach` | Network reachability between workloads |
| `exposed_to` | Exposure to the internet / an external boundary |
| `has_vulnerability` | Workload → CVE (with package and fix version) |
| `has_permission_on` | Identity → resource (with role and effect) |
| `can_assume` | Identity → identity (role assumption / impersonation) |
| `is_member_of` | Identity → group / account membership |
| `has_app_access` | Identity → application assignment (IdP surfaces) |

## Attack paths

The headline analytic: an internet-exposed workload with a known-exploited
vulnerability that can reach a sensitive resource. Each path is scored and
surfaced both as a `toxic_combination` finding and in the dedicated view:

```bash
limacharlie cloudsec attack-path list --severity CRITICAL
```

## Exploring the graph

Expand outward from any resource, one hop at a time — the API behind
click-to-expand on the console's graph canvas:

```bash
limacharlie cloudsec graph neighbors "lcrn:gcp:...instance/web-1" --limit 200
```

The result is an induced subgraph (`nodes` + `edges`), ranked so sensitive
and public neighbors surface first, with `truncated` set when the node has
more neighbors than the cap (hard cap 500).

## Graph queries

Ask questions of the whole graph. Three input forms, one endpoint:

```bash
# A named query from the built-in query pack:
limacharlie cloudsec query list
limacharlie cloudsec query run --named public-buckets

# Free-text:
limacharlie cloudsec query run --text "public bucket with sensitive data"

# The raw query DSL:
limacharlie cloudsec query run --query-json '{...}' --project a,b
```

Results are rows of alias → URN bindings; use
`limacharlie cloudsec resource get <urn>` to hydrate any URN into its full
canonical record (this also works for derived nodes — vulnerabilities,
identities — that have no inventory row).

Queries worth keeping become `cloudsec_query` Hive records — shared,
versioned, and IaC-manageable (see
[Configuration](configuration.md#cloudsec_query)).

## Identity: CIEM views

Two dedicated identity reads sit on top of the graph:

```bash
# Public / external access to sensitive resources — the headline CIEM view.
limacharlie cloudsec ciem public-access

# Identity facet counts (kinds, external/public splits).
limacharlie cloudsec ciem facets
```

Identity findings (dormant privileged identities, escalation edges, unused
privileges) surface in the main worklist under the `ciem_risk` and
`privilege_escalation` classes. External-vs-internal classification is
driven by the provider record's `internal_domains` — keep it complete.

## Data security: DSPM facets

```bash
limacharlie cloudsec data-security facets
```

Returns the data-store posture rollup: total stores, sensitive, public, and
public-*and*-sensitive counts, plus store-kind / sensitivity / exposure
histograms. Sensitivity is your declaration (the `classification` policy)
optionally augmented by content-based auto-classification — see
[Getting Started](getting-started.md#5-declare-what-matters).

## Inventory

The system-of-record behind the graph is queryable directly:

```bash
limacharlie cloudsec inventory list --type <resource-type> --region us-central1 -q prod
limacharlie cloudsec inventory list --provider okta   # scope to one provider's sweep
limacharlie cloudsec inventory facets
```

## Sensors ↔ cloud assets

The fusion mapping resolves both directions between runtime (sensors) and
posture (cloud assets), in bulk:

```bash
# Which cloud asset does each sensor run on?
limacharlie cloudsec resolve sensors $SID1 $SID2

# Which sensors run on this asset?
limacharlie cloudsec resolve assets "lcrn:...instance/web-1"
```

Each response splits `resolved` and `unresolved`, so a pivot from a cloud
finding to live endpoint telemetry (or the reverse) is one call.
