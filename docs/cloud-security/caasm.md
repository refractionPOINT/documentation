# CAASM — Cyber Asset Attack Surface Management

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Your tools already know what you own: the EDR sees devices, the identity
provider sees users and their devices, MDM and scanners see more. CAASM
merges those third-party views into one entity-resolved asset inventory and
evaluates your *expected-coverage* policy over it — surfacing the assets a
required tool does **not** see.

## The merged asset inventory

Records from connected sources are normalized and entity-resolved
(**merge-on-read**) into one canonical asset per real device. Resolution is a
union-find that joins records sharing a strong identifier, in priority order —
serial, then MAC address, then cloud id, then hostname, then email — so the
same laptop seen by the EDR, the IdP, and MDM collapses to a single row with
per-source provenance retained:

```bash
limacharlie cloudsec caasm assets -q laptop --limit 50
```

Supported sources: `sentinelone`, `crowdstrike`, `defender`, `okta`,
`entraid`, `ms_graph`, `wiz`, plus two **native** sources — `limacharlie`
(your own LimaCharlie sensors, capability `edr`) and `google_workspace`
(managed devices from the Workspace directory, capability `mdm`). The native
sources feed automatically once the corresponding provider or sensor telemetry
is connected — no ingest needed. Other telemetry the organization already
pulls through USP adapters also feeds the inventory automatically; anything
else can be pushed through the ingest endpoint below.

### Managed devices and device posture

Because assets are resolved per real device, CAASM can reason about **managed
device posture**. When a source positively asserts a non-compliant state on an
asset, CAASM raises a `device_posture` finding:

| Asserted state | Severity |
|---|---|
| `compromised` | High |
| `encryption` off | Medium |
| `screen_lock` off | Low |
| `developer_mode` on | Low |
| `auto_update` off / OS past end-of-life | Medium |

Posture checks fire only on a positive assertion — an asset that simply never
reported a field is not flagged. A device owned by a privileged identity
raises the finding rather than swallowing it, and `owns-device` edges
(identity → device) join owners to their devices in the
[security graph](graph.md), so "who owns this at-risk laptop" is one hop away.

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
- `kinds` — asset kinds the rule applies to; defaults to `["device"]`.
- `capability` **or** `sources` **(one required)** — either a required
  capability (`edr`, `idp`, `mdm`, `vuln_scanner`, or `cloud_scanner`) or an
  explicit list of source names that must see the asset.
- `severity` — severity of the gap finding; defaults to `MEDIUM`.
- `max_age_days` / `source_max_age_days` — staleness gates: an asset (or a
  source's view of it) older than the window is treated as no longer covered,
  so a stale sensor does not silently count as coverage.

With no policy set, there are **no gap findings** — coverage expectations are
entirely user-declared. The policy is validated on write; an invalid policy is
rejected loudly rather than silently ignored.

!!! note "Distinct from the `coverage` cloudsec_policy"
    This CAASM expected-coverage policy evaluates **third-party assets** (the
    merged device inventory: "seen by the IdP, no EDR"). It is separate from
    the `coverage`-typed `cloudsec_policy`, which declares an EDR expectation
    over **cloud workloads** — see
    [Coverage — workload coverage expectations](configuration.md#coverage-workload-coverage-expectations).
    The two are not synced.

## Coverage gaps

Assets observed by at least one source but missing a required capability
become `coverage_gap` findings — same shape and triage verbs as every other
finding, pre-filtered here:

```bash
limacharlie cloudsec caasm coverage --status open --severity HIGH
```

"Seen by Okta, no EDR" is the canonical example: the asset exists, a human
uses it, and your endpoint tooling is blind to it.

## Pushing records in

For sources without a live adapter, push raw vendor-shaped records directly.
Ingestion is idempotent — re-sending identical records is a no-op:

```bash
# A batch from a file (chunk large imports; the request body caps at 1 MiB).
limacharlie cloudsec caasm ingest --source okta --records-file users.json

# A single record inline (the shape D&R-driven feeders use).
limacharlie cloudsec caasm ingest --source crowdstrike --record-json '{...}'
```

The response carries the reconcile counters — `received`, `normalized`,
`skipped`, `assets`, `created`, `updated`, `deleted` — so a feeder can
observe exactly what its batch changed.

!!! info "Permissions"
    Reading assets and coverage requires `cloudsec.get`; setting the policy
    and ingesting records require `cloudsec.set`.
