# CAASM — Cyber Asset Attack Surface Management

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and
    configuration formats on this page can change before general
    availability. Contact LimaCharlie to request access.

Your tools already know what you own: the EDR sees devices, the identity
provider sees users and their devices, and MDM and scanners see more. CAASM
merges those third-party views into one entity-resolved asset inventory. It
then evaluates your *expected-coverage* policy over that inventory and shows
the assets that a required tool does **not** see.

## The merged asset inventory

CAASM normalizes and entity-resolves the records from connected sources
(**merge-on-read**) into one canonical asset for each real device.
Resolution is a union-find that joins records with a shared strong
identifier, in priority order — serial, then MAC address, then cloud id,
then hostname, then email. The same laptop seen by the EDR, the IdP, and MDM
becomes a single row that keeps the provenance of each source:

```bash
limacharlie cloudsec caasm assets -q laptop --limit 50
```

Supported sources: `sentinelone`, `crowdstrike`, `defender`, `okta`,
`entraid`, `ms_graph`, `wiz`, plus two **native** sources — `limacharlie`
(your own LimaCharlie sensors, capability `edr`) and `google_workspace`
(managed devices from the Workspace directory, capability `mdm`). The native
sources feed automatically after you connect the corresponding provider or
sensor telemetry — no ingest is needed. Other telemetry that the
organization already pulls through USP adapters also feeds the inventory
automatically. You can push anything else through the ingest endpoint below.

### Managed devices and device posture

Because CAASM resolves assets for each real device, it can reason about
**managed device posture**. When a source positively asserts a non-compliant
state on an asset, CAASM raises a `device_posture` finding:

| Asserted state | Severity |
|---|---|
| `compromised` | High |
| `encryption` off | Medium |
| `screen_lock` off | Low |
| `developer_mode` on | Low |
| `auto_update` off / OS past end-of-life | Medium |

Posture checks fire only on a positive assertion. An asset that never
reported a field is not flagged. A device owned by a privileged identity
raises the finding instead of hiding it. `owns-device` edges
(identity → device) join owners to their devices in the
[security graph](graph.md), so the owner of an at-risk laptop is one hop
away.

## Declare expected coverage

Coverage evaluation is a no-op until you declare expectations — a labeled
list of "assets of these kinds must be seen by a tool with this capability":

```bash
cat > coverage.json <<EOF
{
  "expect": [
    {
      "label": "edr-on-devices",
      "capability": "edr",
      "kinds": ["device"],
      "severity": "HIGH",
      "max_age_days": 30,
      "source_max_age_days": 7
    }
  ]
}
EOF

limacharlie cloudsec caasm policy set --input-file coverage.json
limacharlie cloudsec caasm policy get
```

The policy shape is `{expect: [ ... ]}`, and each expectation rule takes:

- `label` **(required)** — names the expectation; it anchors the resulting
  finding.
- `kinds` — the asset kinds that the rule applies to; defaults to
  `["device"]`.
- `capability` **or** `sources` **(one required)** — either a required
  capability (`edr`, `idp`, `mdm`, `vuln_scanner`, or `cloud_scanner`) or an
  explicit list of source names that must see the asset.
- `severity` — severity of the gap finding; defaults to `MEDIUM`.
- `max_age_days` / `source_max_age_days` — staleness gates: an asset (or the
  view of it from one source) older than the window is no longer covered, so
  a stale sensor does not count as coverage.

If you set no policy, there are **no gap findings** — you declare all
coverage expectations. The cloud validates the policy on write. It rejects
an invalid policy instead of ignoring it.

!!! note "Distinct from the `coverage` cloudsec_policy"
    This CAASM expected-coverage policy evaluates **third-party assets** (the
    merged device inventory: "seen by the IdP, no EDR"). It is separate from
    the `coverage`-typed `cloudsec_policy`, which declares an EDR expectation
    over **cloud workloads** — see
    [Coverage — workload coverage expectations](configuration.md#coverage-workload-coverage-expectations).
    The two are not synced.

## Coverage gaps

Assets that at least one source sees, but that miss a required capability,
become `coverage_gap` findings — the same shape and triage verbs as every
other finding, pre-filtered here:

```bash
limacharlie cloudsec caasm coverage --status open --severity HIGH
```

"Seen by Okta, no EDR" is the canonical example: the asset exists, a human
uses it, and your endpoint tools do not see it.

## Pushing records in

If a source has no live adapter, push raw vendor-shaped records directly.
Ingestion is idempotent — if you send identical records again, nothing
changes:

```bash
# A batch from a file (chunk large imports; the request body caps at 1 MiB).
limacharlie cloudsec caasm ingest --source okta --records-file users.json

# A single record inline (the shape D&R-driven feeders use).
limacharlie cloudsec caasm ingest --source crowdstrike --record-json '{...}'
```

The response carries the reconcile counters — `received`, `normalized`,
`skipped`, `assets`, `created`, `updated`, `deleted` — so a feeder can see
what its batch changed.

!!! info "Permissions"
    To read assets and coverage, you need `cloudsec.get`. To set the policy
    and to ingest records, you need `cloudsec.set`.
