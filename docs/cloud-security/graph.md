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
| `has_permission_on` | Identity → resource; carries the classified **access level** (the capability the grant confers — `data_admin` › `data_write` › `data_read` › `metadata` › `none`), which is the edge verb the UI shows |
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

## Topology

The interactive **Security graph** above (the Explore page canvas) is for
traversal — expanding one hop at a time from a starting node. **Topology** is
the other view: an aggregated, explorable diagram of the whole estate,
laid out Provider → Account → Region → Resource. A node-type declutter filter
hides the classes you don't care about, and the current view (filters,
expansion) is captured in a shareable URL so a colleague opens exactly what
you're looking at.

Because it is backed by **server-side aggregates**, the counts on every node
are exact at any scale — Topology never walks a capped page and then guesses.
It is served by `GET /topology` (see [API Reference](api-reference.md)); there
is no CLI command for it.

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

The console calls this area **Identity & Access**. Two dedicated identity
reads sit on top of the graph:

```bash
# Public / external access to sensitive resources — the headline CIEM view.
limacharlie cloudsec ciem public-access

# Identity facet counts (kinds, external/public splits).
limacharlie cloudsec ciem facets
```

Access is scored by the **capability** a grant confers, not the mere existence
of a grant: the effective action set is classified to an access level —
`data_admin` › `data_write` › `data_read` › `metadata` › `none`. "Reaches
sensitive data" gates on `data_read`-or-higher; `metadata`/`none` grants are a
lower-severity reconnaissance signal rather than a top data-access risk. That
level is stamped on the `has_permission_on` edge and is the verb the UI shows.

Identity findings (dormant privileged identities, escalation edges, unused
privileges) surface in the main worklist under the `ciem_risk` and
`privilege_escalation` classes. External-vs-internal classification is
driven by the provider record's `internal_domains` — keep it complete.

### Identity 360

For a single identity, **Identity 360** is the one-screen view of everything
it can reach — direct grants, group-inherited permissions, identities it can
assume, and application assignments — plus a **devices** lane pulling in the
endpoints associated with that identity. Each reach edge carries its classified
access level, so the whole effective blast radius is visible in one place. It
is the console's Identity & Access → *(an identity)* drill-down, served by
`GET /cloudsec/{oid}/ciem/identity?urn=<identity-urn>` (see
[API Reference](api-reference.md)); there is no CLI command for it.

## Data security: DSPM facets

```bash
limacharlie cloudsec data-security facets
```

Returns the data-store posture rollup: total stores, sensitive, public, and
public-*and*-sensitive counts, plus store-kind / sensitivity / exposure
histograms. Sensitivity is your declaration: `classification`-policy
`content_class` and name/`resource_type` rules decide what counts as sensitive
(the retired `auto_classify` boolean is gone). The agentless scanner still
detects content classes and surfaces them as facts on a resource, but only a
matching `content_class` rule turns a detection into a sensitivity claim — see
[Configuration](configuration.md#classification-crown-jewels).

## Inventory

The system-of-record behind the graph is queryable directly, filtered by
`--type`, `--provider`, `--account`, `--region`, and free-text `-q`:

```bash
limacharlie cloudsec inventory list \
  --type <resource-type> --provider gcp --region us-central1 -q prod
limacharlie cloudsec inventory facets
```

This is the first-party cloud inventory. **Third-party (CAASM) assets** — the
entity-resolved devices and identities merged from EDR, IdP, MDM, and scanner
sources — live in their own inventory tab and have their own reads; see
[CAASM](caasm.md).

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
