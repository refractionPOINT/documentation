# API Reference

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and
    configuration formats on this page can change before general
    availability. Contact LimaCharlie to request access.

All Cloud Security routes are under
`https://api.limacharlie.io/v1/cloudsec/{oid}/…`. They appear in the public
OpenAPI spec at [`/openapi`](https://api.limacharlie.io/openapi).
Authentication uses the standard `Authorization: Bearer <JWT>` header.

!!! info "Permissions & enable gate"
    Reads need `cloudsec.get`. The read-only preview `POST`s (`query`,
    `simulate/resources`, `simulate/findings`, `policy/suggest`) also need
    `cloudsec.get`. Every other write needs `cloudsec.set`. For every
    route, the organization must subscribe to `ext-cloud-security`. A `403`
    on any route means that you must subscribe first. The `oid` always
    comes from the authorized path. Provider *records* are not `/cloudsec`
    routes: their CRUD goes through Hive (`cloudsec_provider` hive, gated
    by `cloudsec_provider.get/set/del`).

Shared behaviors:

- **Repeatable filters** (`severity`, `finding_class`, `status`, `account`,
  `sid`, `urn`) go in the URL as repeated query keys: `?severity=CRITICAL&severity=HIGH`.
  Values in one key are OR. Different keys are AND. Each filter key accepts
  at most 100 values.
- **Keyset pagination**: pages carry `next_cursor`; pass it back as
  `?cursor=`. `limit` is clamped to 1000.
- **CSV export**: exactly four routes accept `?format=csv` to stream the
  full filtered set as a CSV attachment — `findings`, `inventory`, and
  `compliance` (`GET`), and `query` (`POST`). The stream is a server-side
  keyset walk with a cap of 100,000 rows. If the export reaches the cap,
  the stream includes a truncation notice as a `#` comment.

## Reads

| Route | Returns |
|---|---|
| `GET /findings` | `{findings, next_cursor}` — the risk-ranked worklist. Filters: `severity[]`, `finding_class[]`, `status[]`, `account[]`, `reachable`, `kev`, `q`, `sort`, `order`, `cursor`, `limit`. |
| `GET /findings/facets` | `{facets}` — cross-filtered facet counts under the same selectors. |
| `GET /findings/classes` | `{classes}` — the canonical `finding_class` enum (the 11 values), to build selectors. |
| `GET /findings/{finding_id}` | `{finding}` — one finding in full. |
| `GET /attack-paths` | `{paths}` — the main toxic-combination paths. Filters: `severity[]`, `account[]`, `status[]`, `q`. |
| `GET /chokepoints` | `{chokepoints, total_paths}` — shared attack-path hops ranked by paths broken, including the principal-exposure metrics. |
| `GET /ciem/public-access` | `{access}` — public/external access to sensitive resources. |
| `GET /ciem/facets` | `{facets}` — identity facet counts. |
| `GET /ciem/identity?urn=` | `{identity}` — the Identity 360 single-identity rollup for one principal URN: its grants, reachable sensitive resources, access levels, and escalation paths. |
| `GET /inventory` | `{resources, next_cursor}`. Filters: `type`, `provider`, `account`, `region`, `q`, paging. |
| `GET /inventory/facets` | Inventory facet counts by type/account/region. |
| `GET /data-security/facets` | `{facets}` — DSPM data-store rollup. |
| `GET /resource?urn=` | `{resource}` — the canonical record for any URN (null when unknown). |
| `GET /graph/neighbors?urn=` | `{graph: {nodes, edges}}` — 1-hop expansion; `limit` default 200, cap 500; `truncated` flag. |
| `GET /topology` | `{scopes, edges, available}` — the server-side estate aggregate behind the Topology diagram (scope nodes + the edges between them). The `available` flag is `false` when the estate is too large to aggregate inline. |
| `GET /policy/vocabulary` | `{vocabulary}` — the classification-policy vocabulary: the matcher-capability table for each surface, closed vocabularies (resource types, content classes), and the org's in-use value histograms. |
| `GET /providers/manifest?type=` | `{manifest}` — the coverage manifest for each provider ("what you get"): the resource kinds, edges, and checks that a given `provider_type` produces. |
| `GET /queries` | `{queries}` — the named query pack (name, title, description, query). |
| `POST /query` | `{rows}` — run a graph query. Body: exactly one of `named` / `text` / `query` (DSL object), optional `project`. |
| `GET /compliance` | `{report}` — the assessment for each control. Params: `framework` (default `cis-gcp`) or `assignment` (overrides `framework`). |
| `GET /compliance/frameworks` | `{frameworks}` — id, name, version, control counts. |
| `GET /compliance/assignments` | `{assignments}` — scoped assignments with a score for each assignment. |
| `GET /overview` | Composed risk overview (`score`, distributions, top paths, coverage, trend, changes, and the `usage` metering block for each tenant). Param: `trend_days` (default 30). |
| `GET /changes` | `{changes}` — created/closed feed, newest first. Param: `limit` (default 50). |
| `GET /risk-trend` | `{trend}` — score history, oldest first. Param: `trend_days`. |
| `GET /scan-status` | `{status}` — collection run state. Param: `provider` (default `gcp`; ids are lowercase — the lookup is case-sensitive and an unknown or miscased id reads as never-scanned). |
| `GET /resolve/sensors?sid=…` | `{resolved, unresolved}` — sensor → cloud asset, in bulk with repeated `sid` (server cap 500 for each request; keep URLs under about 8KB — the CLI/SDK chunks automatically). |
| `GET /resolve/assets?urn=…` | `{resolved, unresolved}` — cloud asset → sensors, in bulk with repeated `urn` (same caps and chunking). |
| `GET /caasm/assets` | `{resources, next_cursor}` — the merged third-party asset inventory. Params: `q`, paging. |
| `GET /caasm/coverage` | `{findings, next_cursor}` — coverage-gap findings. Params: `status[]`, `severity[]`, `q`, `sort`, `order`, paging. |
| `GET /caasm/policy` | Resource-list shape: zero rows (no policy) or one row whose `props` is the policy. |

!!! note "`ciem/*` and `providers/*` families"
    `ciem/*` has three members — `public-access`, `facets`, and
    `identity`. `providers/*` has two — `test` (`POST`, below) and `manifest`
    (`GET`, above). To create, edit, or delete provider *records*, use the
    `cloudsec_provider` Hive. These operations are not `/cloudsec` routes.

## Fleet (multi-org)

One route is outside the `{oid}` path — the MSSP cross-tenant board:

| Route | Returns |
|---|---|
| `GET /cloudsec/fleet/overview` | `{orgs, rollups, total_orgs, skipped, next_cursor}` — risk posture rolled up across many organizations. The tenants that the route cannot include are counted in `skipped`. Params: `oids[]` (repeat to select tenants), `group` (a saved fleet group), `trend_days`, `cursor`, `limit`. Needs `cloudsec.get` on each tenant in scope. |

## Writes

All writes are `POST` with a JSON body and need `cloudsec.set`.

| Route | Body | Returns |
|---|---|---|
| `/findings/{finding_id}/status` | `{resolution: {kind, reason, expires_at}}` — `kind` is `mitigated` \| `accepted` \| `false_positive`, or `open` to clear the disposition and reopen. `expires_at` is unix seconds (meaningful with `accepted`). | `{ok}` |
| `/findings/bulk/status` | `{finding_ids: [...], resolution: {...}}` — one resolution applied to many findings. Different from the single-finding route, `kind` must be `mitigated` \| `accepted` \| `false_positive` — the bulk route does **not** accept `open` (reopen findings one at a time). | `{updated}` |
| `/findings/{finding_id}/owner` | `{owner}` — an empty string clears the value. | `{ok}` |
| `/findings/{finding_id}/ticket` | `{ticket}` — an empty string clears the value. | `{ok}` |
| `/chokepoints/dismiss` | `{urn, reason?}` | `{ok}` |
| `/chokepoints/restore` | `{urn}` | `{ok}` |
| `/caasm/policy` | `{policy: {expect: [{label, capability, kinds}]}}` — validated before storage. | `{ok}` |
| `/caasm/ingest` | `{source, records?: [...], record?: {...}, policy?: {...}}` — `source` is required; a single `record` is a batch of one element. The body has a cap of 1 MiB; ingestion is idempotent. | `{result: {received, normalized, skipped, assets, created, updated, deleted}}` |
| `/providers/test` | `{provider: <cloudsec_provider record>}` — credential inline (ephemeral, never stored) or a `hive://secret/<name>` reference. | `{supported, report: {provider, ok, checks: [{id, name, required, ok, detail}]}}` |

Example — disposition a finding:

```bash
curl -X POST -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
  "https://api.limacharlie.io/v1/cloudsec/$OID/findings/fnd_0a1b.../status" \
  -d '{"resolution": {"kind": "accepted", "reason": "SEC-123", "expires_at": 1767225600}}'
```

## Policy authoring: Simulate & vocabulary

These `POST` routes supply the policy-authoring aids in the web app
(matcher preview and value autocomplete). They never mutate state, so they
need only `cloudsec.get`. On the CLI they are `limacharlie cloudsec simulate
resources` / `simulate findings`, `limacharlie cloudsec policy suggest`,
and `limacharlie cloudsec policy vocabulary`.

| Route | Body | Returns |
|---|---|---|
| `POST /simulate/resources` | `{rules, target, resource_types?, sample_limit?}` — `rules` is a list of matcher rules, `target` scopes the walked surface (`data_store`, `compute`, `identity`, or `any` — the default). | `{evaluated, matched, indeterminate, truncated, sample}` — preview a classification / coverage / exclusion matcher against stored inventory. |
| `POST /simulate/findings` | `{match, sample_limit?}` — a suppression matcher. | `{evaluated, matched, indeterminate, truncated, sample}` — preview it against findings that are open now. |
| `POST /policy/suggest` | `{dimension, q, target, limit?}` — `dimension` is `name` or `account`. | `{suggestions}` — live matcher-value autocomplete drawn from the tenant estate. |

Pair these with `GET /policy/vocabulary` (the closed vocabularies and the
capability table for each surface) and `GET /findings/classes` (the
`finding_class` enum) when you build a classification or suppression policy.

## Finding shape

The finding object (list, get, and the `cloud_finding.created` event all
carry the same shape) — key fields:

| Field | Meaning |
|---|---|
| `finding_id`, `fingerprint` | Stable identity of the condition (`fnd_` + fingerprint prefix). |
| `rule_id`, `finding_class`, `classification` | What detected it and its class — one of: `toxic_combination`, `public_exposure`, `ciem_risk`, `privilege_escalation`, `vulnerability`, `misconfig`, `coverage_gap`, `device_posture`. |
| `severity`, `lc_risk`, `risk_breakdown` | `CRITICAL`–`INFO`, the 0–1000 composite, and its explanation. |
| `title`, `resource_urn`, `resource_name`, `resource_type`, `account`, `region` | The affected resource. |
| `related_urns`, `path`, `path_kind` | Related resources; the hop list for path findings and the kind of path that it represents. |
| `source_scope`, `target_scope` | For attack-path / toxic findings, the durable workload group at each end (GKE/EKS/AKS node pool, MIG, ASG, VMSS) — `group_urn`, `group_kind`, `member_count`, `affected_count`, `members` — so the finding shows the shared-fix group, not an ephemeral node that changes often. |
| `reachable`, `in_kev`, `vulns`, `epss`, `epss_percentile` | Exposure and exploit intelligence; `vulns` entries carry `cve`, `package`, `package_version`, `fix_version`, `cvss_score`. |
| `evidence`, `remediation` | The offending configuration and the fix. |
| `ciem_access` | For identity findings: role, identity kind, public/external/privileged flags, grant path, and the classified data-plane **access level** / capability (`data_admin` > `data_write` > `data_read` > `metadata` > `none`) that the grant confers. |
| `runtime_sids` | Sensors resolved onto the affected asset. |
| `status`, `resolution`, `resolved_by`, `resolution_expires_at`, `owner`, `ticket` | The triage overlay. |
| `first_seen`, `last_seen` | Lifecycle timestamps. |

## Events

If you enable emission of findings and resources (see the
[`emission` policy](configuration.md#emission-the-event-feed)), the cloud
emits events into the organization's event stream.

**Detection-truth lifecycle** (from the projector):

- `cloud_finding.created` — the full finding (including `runtime_sids`)
  under `event/finding`.
- `cloud_finding.updated` — an open finding materially changed (severity
  flip, vuln set). Payload `{finding_id, fingerprint, finding_class,
  changed, old_severity, new_severity, finding}`.
- `cloud_finding.closed` — `{finding_id, fingerprint, finding_class}`.
- `cloud_finding.still_open` — re-asserted at most once a day for open
  findings with a linked ticket (the case-sync verb).

**Operator disposition** (from the triage write handlers) — flat payload
`{finding_id, fingerprint, finding_class, actor, note?}`:

- `cloud_finding.resolved`, `cloud_finding.dismissed`,
  `cloud_finding.reopened`, `cloud_finding.assigned`.

**Summary & inventory:**

- `cloudsec.sync_completed` — emitted one time on the first-ever (or
  rebuilt) projection in place of a flood of `created` events, one for each
  finding; payload `{total, by_class, by_severity}`.
- `cloud_resource.created`, `cloud_resource.updated`,
  `cloud_resource.deleted` — inventory change events (off by default).

Every payload also carries `event_type` and `oid`.

See [Automation & IaC](automation.md#findings-cases-automation) for D&R
rules that consume them.
