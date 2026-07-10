# API Reference

All Cloud Security routes live under
`https://api.limacharlie.io/v1/cloudsec/{oid}/…` and appear in the public
OpenAPI spec at [`/openapi`](https://api.limacharlie.io/openapi).
Authentication is the standard `Authorization: Bearer <JWT>` header.

!!! info "Permissions & enable gate"
    Reads require `cloudsec.get`; writes require `cloudsec.set`. Every route
    requires the organization to be subscribed to `ext-cloud-inventory` — a
    `403` on any route means subscribe first. The `oid` is always taken from
    the authorized path.

Shared behaviors:

- **Repeatable filters** (`severity`, `finding_class`, `status`, `account`,
  `sid`, `urn`) are passed as repeated query keys: `?severity=CRITICAL&severity=HIGH`.
  OR within a key, AND across keys. At most 100 values per filter key.
- **Keyset pagination**: pages carry `next_cursor`; pass it back as
  `?cursor=`. `limit` is clamped to 1000.
- **CSV export**: `findings`, `inventory`, `compliance`, and `query` accept
  `?format=csv` to stream the full filtered set as a CSV attachment
  (server-side walk, capped at 100,000 rows, in-band `#` truncation notice).

## Reads

| Route | Returns |
|---|---|
| `GET /findings` | `{findings, next_cursor}` — the risk-ranked worklist. Filters: `severity[]`, `finding_class[]`, `status[]`, `account[]`, `reachable`, `kev`, `q`, `sort`, `order`, `cursor`, `limit`. |
| `GET /findings/facets` | `{facets}` — cross-filtered facet counts under the same selectors. |
| `GET /findings/{finding_id}` | `{finding}` — one finding in full. |
| `GET /attack-paths` | `{paths}` — marquee toxic-combination paths. Filters: `severity[]`, `account[]`, `status[]`, `q`. |
| `GET /chokepoints` | `{chokepoints, total_paths}` — shared attack-path hops ranked by paths broken, including the principal-exposure metrics. |
| `GET /ciem/public-access` | `{access}` — public/external access to sensitive resources. |
| `GET /ciem/facets` | `{facets}` — identity facet counts. |
| `GET /inventory` | `{resources, next_cursor}`. Filters: `type`, `account`, `region`, `q`, paging. |
| `GET /inventory/facets` | Inventory facet counts by type/account/region. |
| `GET /data-security/facets` | `{facets}` — DSPM data-store rollup. |
| `GET /resource?urn=` | `{resource}` — the canonical record for any URN (null when unknown). |
| `GET /graph/neighbors?urn=` | `{graph: {nodes, edges}}` — 1-hop expansion; `limit` default 200, cap 500; `truncated` flag. |
| `GET /queries` | `{queries}` — the named query pack (name, title, description, query). |
| `POST /query` | `{rows}` — run a graph query. Body: exactly one of `named` / `text` / `query` (DSL object), optional `project`. |
| `GET /compliance` | `{report}` — per-control assessment. Params: `framework` (default `cis-gcp`) or `assignment` (overrides `framework`). |
| `GET /compliance/frameworks` | `{frameworks}` — id, name, version, control counts. |
| `GET /compliance/assignments` | `{assignments}` — scoped assignments with per-assignment scores. |
| `GET /overview` | Composed risk overview (`score`, distributions, top paths, coverage, trend, changes, and the per-tenant `usage` metering block). Param: `trend_days` (default 30). |
| `GET /changes` | `{changes}` — created/closed feed, newest first. Param: `limit` (default 50). |
| `GET /risk-trend` | `{trend}` — score history, oldest first. Param: `trend_days`. |
| `GET /scan-status` | `{status}` — collection run state. Param: `provider` (default `gcp`; ids are lowercase — the lookup is case-sensitive and an unknown/miscased id reads as never-scanned). |
| `GET /resolve/sensors?sid=…` | `{resolved, unresolved}` — sensor → cloud asset, bulk via repeated `sid` (server cap 500/request; keep URLs under ~8KB — the CLI/SDK chunks automatically). |
| `GET /resolve/assets?urn=…` | `{resolved, unresolved}` — cloud asset → sensors, bulk via repeated `urn` (same caps and chunking). |
| `GET /caasm/assets` | `{resources, next_cursor}` — the merged third-party asset inventory. Params: `q`, paging. |
| `GET /caasm/coverage` | `{findings, next_cursor}` — coverage-gap findings. Params: `status[]`, `severity[]`, `q`, `sort`, `order`, paging. |
| `GET /caasm/policy` | Resource-list shape: zero rows (no policy) or one row whose `props` is the policy. |

## Writes

All writes are `POST` with a JSON body and require `cloudsec.set`.

| Route | Body | Returns |
|---|---|---|
| `/findings/{finding_id}/status` | `{resolution: {kind, reason, expires_at}}` — `kind` is `mitigated` \| `accepted` \| `false_positive`, or `open` to clear the disposition and reopen. `expires_at` is unix seconds (meaningful with `accepted`). | `{ok}` |
| `/findings/bulk/status` | `{finding_ids: [...], resolution: {...}}` — one resolution applied to many findings. Unlike the single-finding route, `kind` must be `mitigated` \| `accepted` \| `false_positive` — the bulk route does **not** accept `open` (reopen findings one at a time). | `{updated}` |
| `/findings/{finding_id}/owner` | `{owner}` — empty string clears. | `{ok}` |
| `/findings/{finding_id}/ticket` | `{ticket}` — empty string clears. | `{ok}` |
| `/chokepoints/dismiss` | `{urn, reason?}` | `{ok}` |
| `/chokepoints/restore` | `{urn}` | `{ok}` |
| `/caasm/policy` | `{policy: {expect: [{label, capability, kinds}]}}` — validated before storing. | `{ok}` |
| `/caasm/ingest` | `{source, records?: [...], record?: {...}, policy?: {...}}` — `source` required; a single `record` is treated as a one-element batch. Body capped at 1 MiB; ingestion is idempotent. | `{result: {received, normalized, skipped, assets, created, updated, deleted}}` |
| `/providers/test` | `{provider: <cloudsec_provider record>}` — credential inline (ephemeral, never stored) or a `hive://secret/<name>` reference. | `{supported, report: {provider, ok, checks: [{id, name, required, ok, detail}]}}` |

Example — disposition a finding:

```bash
curl -X POST -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
  "https://api.limacharlie.io/v1/cloudsec/$OID/findings/fnd_0a1b.../status" \
  -d '{"resolution": {"kind": "accepted", "reason": "SEC-123", "expires_at": 1767225600}}'
```

## Finding shape

The finding object (list, get, and the `cloud_finding.created` event all
carry the same shape) — key fields:

| Field | Meaning |
|---|---|
| `finding_id`, `fingerprint` | Stable identity of the condition (`fnd_` + fingerprint prefix). |
| `rule_id`, `finding_class`, `classification` | What detected it and its class (`toxic_combination`, `public_exposure`, `ciem_risk`, `privilege_escalation`, `vulnerability`, `misconfig`, `malware`, `secret`, `scan_finding`, `coverage_gap`). |
| `severity`, `lc_risk`, `risk_breakdown` | `CRITICAL`–`INFO`, the 0–1000 composite, and its explanation. |
| `title`, `resource_urn`, `resource_name`, `resource_type`, `account`, `region` | The affected resource. |
| `related_urns`, `path` | Related resources; the hop list for path findings. |
| `reachable`, `in_kev`, `vulns`, `epss`, `epss_percentile` | Exposure and exploit intelligence; `vulns` entries carry `cve`, `package`, `package_version`, `fix_version`, `cvss_score`. |
| `evidence`, `remediation` | The offending configuration and the fix. |
| `ciem_access` | For identity findings: role, identity kind, public/external/privileged flags, grant path. |
| `runtime_sids` | Sensors resolved onto the affected asset. |
| `status`, `resolution`, `resolved_by`, `resolution_expires_at`, `owner`, `ticket` | The triage overlay. |
| `first_seen`, `last_seen` | Lifecycle timestamps. |

## Events

With finding/resource emission enabled (see the
[`emission` policy](configuration.md#emission-the-event-feed)), the
platform emits into the organization's event stream:

- `cloud_finding.created` — full finding under `event/finding`.
- `cloud_finding.closed` — `{finding_id, fingerprint, finding_class}`.
- `cloud_finding.still_open` — re-asserted at most daily for open findings
  with a linked ticket.
- `cloud_resource.*` — inventory change events.

See [Automation & IaC](automation.md#findings-cases-automation) for D&R
rules that consume them.
