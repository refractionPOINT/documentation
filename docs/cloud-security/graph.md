# Security Graph & Queries

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Every sweep builds a graph of the estate. The nodes are resources, identities,
and data stores. The edges are reachability, exposure, permission, and
vulnerability relationships. The graph combines three unremarkable facts into
one critical finding, and you can explore it directly.

## The graph model

A URN addresses each node — the same `lcrn:` identifiers that the API uses.
Each node carries properties for its type:

- Exposure (`is_public`).
- Sensitivity (`is_sensitive`).
- Vulnerability context (`cve`, `severity`, `in_kev`, `cvss_score`).
- Identity insight: human or service kind, external flag, MFA posture,
  dormancy, escalation potential, and suggestions for least privilege.

Each edge carries the meaning of the relationship:

| Edge | Meaning |
|---|---|
| `can_reach` | Network reachability between workloads |
| `exposed_to` | Exposure to the internet or an external boundary |
| `has_vulnerability` | Workload → CVE (with package and fix version) |
| `has_permission_on` | Identity → resource. The edge carries the classified **access level** — the capability that the grant gives (`data_admin` › `data_write` › `data_read` › `metadata` › `none`). The web app shows this level as the edge verb |
| `can_assume` | Identity → identity (role assumption or impersonation) |
| `is_member_of` | Identity → group or account membership |
| `has_app_access` | Identity → application assignment (IdP surfaces) |

## Attack paths

The main analytic finds an internet-exposed workload that has a
known-exploited vulnerability and can reach a sensitive resource. Each path
gets a score and shows both as a `toxic_combination` finding and in the
dedicated view:

```bash
limacharlie cloudsec attack-path list --severity CRITICAL
```

## Exploring the graph

Expand outward from any resource, one hop at a time. This is the API behind
click-to-expand on the graph canvas in the web app:

```bash
limacharlie cloudsec graph neighbors "lcrn:gcp:...instance/web-1" --limit 200
```

The result is an induced subgraph (`nodes` + `edges`). The rank puts sensitive
and public neighbors first. If the node has more neighbors than the cap, the
result sets `truncated`. The hard cap is 500.

## Topology

The interactive **Security graph** above (the Explore page canvas) is for
traversal. It expands one hop at a time from a start node. **Topology** is the
other view: an aggregated, explorable diagram of the whole estate, laid out
Provider → Account → Region → Resource. A declutter filter for node types hides
the classes that you do not want. A shareable URL holds the current view
(filters and expansion), so a colleague opens the same view that you see.

**Server-side aggregates** supply the counts on every node, so the counts are
exact at any scale. Topology never walks a capped page and then guesses.
`GET /topology` serves it (see [API Reference](api-reference.md)), and
`limacharlie cloudsec topology` serves it on the CLI.

## Graph queries

Ask questions of the whole graph. There are three input forms and one endpoint:

```bash
# A named query from the built-in query pack:
limacharlie cloudsec query list
limacharlie cloudsec query run --named public_data_stores

# The text form — a compact MATCH ... RETURN pattern:
limacharlie cloudsec query run --text 'MATCH (d:DataStore {is_sensitive: true})<-[:has_permission_on]-(i:Identity {is_external: true}) RETURN i, d'

# The raw query DSL:
limacharlie cloudsec query run --query-json '{...}' --project a,b
```

The text form is a compact graph-pattern grammar, not natural language:

- Nodes are `(alias:Label {prop: value, ...})`.
- Edges are `<-[:edge_name]-` (inbound to the previous node) or
  `-[:edge_name]->` (outbound).
- Edge names use underscores.
- The query ends with `RETURN alias, alias...`.

Inline predicates are equalities that the query combines with AND.

The first node is the **anchor**. Every query must anchor on a *selective* set
and traverse inward. Bounded node types (data stores, vulnerabilities, public
endpoints, applications, accounts) anchor as-is. Dense types (workloads,
identities) need a selective predicate: `is_sensitive: true`, `is_public:
true`, `is_external: true`, `in_kev: true`, or an exact `email` or `sid`. A
query that fans out from the dense fabric is rejected by design. Restructure it
to start from the selective end — the sensitive store, the known-exploited
vulnerability, or the specific identity — and walk toward the dense side.

Results are rows of alias → URN bindings. Use
`limacharlie cloudsec resource get <urn>` to expand any URN into its full
canonical record. This also works for derived nodes, such as vulnerabilities
and identities, that have no inventory row.

Save a query that you want to keep as a `cloudsec_query` Hive record. These
records are shared, versioned, and manageable as IaC (see
[Configuration](configuration.md#cloudsec_query)).

## Identity: CIEM views

The web app calls this area **Identity & Access**. Two identity reads work on
top of the graph:

```bash
# Public / external access to sensitive resources — the headline CIEM view.
limacharlie cloudsec ciem public-access

# Identity facet counts (kinds, external/public splits).
limacharlie cloudsec ciem facets
```

The score for access comes from the **capability** that a grant gives, not from
the existence of the grant. The effective action set is classified to an access
level: `data_admin` › `data_write` › `data_read` › `metadata` › `none`.
"Reaches sensitive data" needs `data_read` or higher. A `metadata` or `none`
grant is a reconnaissance signal of lower severity, not a top data-access risk.
The `has_permission_on` edge carries that level, and the web app shows it as
the verb.

Identity findings show in the main worklist under the `ciem_risk` and
`privilege_escalation` classes. They cover dormant privileged identities,
escalation edges, and unused privileges. The `internal_domains` field on the
provider record drives the classification of external against internal. Keep
that field complete.

### Identity 360

For a single identity, **Identity 360** shows on one screen everything that the
identity can reach: direct grants, group-inherited permissions, identities that
it can assume, and application assignments. A **devices** lane adds the
endpoints that are associated with that identity. Each reach edge carries its
classified access level, so the full effective reach is visible in one place.
In the web app it is the Identity & Access → *(an identity)* drill-down.
`GET /cloudsec/{oid}/ciem/identity?urn=<identity-urn>` serves it (see
[API Reference](api-reference.md)), and
`limacharlie cloudsec ciem identity "<identity-urn>"` serves it on the CLI.

## Data security: DSPM facets

```bash
limacharlie cloudsec data-security facets
```

The command returns the posture rollup for data stores: total stores, and
counts of sensitive, public, and public-*and*-sensitive stores. It also returns
histograms for store kind, sensitivity, and exposure.

You declare sensitivity. The `content_class` rule and the name or
`resource_type` rules in the `classification` policy decide what counts as
sensitive. The retired `auto_classify` boolean is gone. The agentless scanner
still detects content classes and reports them as facts on a resource, but only
a matching `content_class` rule turns a detection into a sensitivity claim —
see [Configuration](configuration.md#classification-crown-jewels).

## Inventory

You can query the system-of-record behind the graph directly. Filter it with
`--type`, `--provider`, `--account`, `--region`, and the free-text `-q`:

```bash
limacharlie cloudsec inventory list \
  --type <resource-type> --provider gcp --region us-central1 -q prod
limacharlie cloudsec inventory facets
```

This is the first-party cloud inventory. **Third-party (CAASM) assets** are the
entity-resolved devices and identities merged from EDR, IdP, MDM, and scanner
sources. They live in their own inventory tab and have their own reads; see
[CAASM](caasm.md).

## Sensors ↔ cloud assets

The fusion mapping resolves both directions in bulk between runtime (sensors)
and posture (cloud assets):

```bash
# Which cloud asset does each sensor run on?
limacharlie cloudsec resolve sensors $SID1 $SID2

# Which sensors run on this asset?
limacharlie cloudsec resolve assets "lcrn:...instance/web-1"
```

Each response splits `resolved` and `unresolved`. A pivot from a cloud finding
to live endpoint telemetry, or the reverse, is one call.
