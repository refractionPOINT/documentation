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

Records from connected sources are normalized and entity-resolved (by
hostname, serial, MAC addresses, email, …) into one row per real asset,
with per-source provenance retained:

```bash
limacharlie cloudsec caasm assets -q laptop --limit 50
```

Supported sources: `sentinelone`, `crowdstrike`, `defender`, `okta`,
`entraid`, `ms_graph`, `wiz`. Telemetry the organization already ingests
through USP adapters feeds the inventory automatically; anything else can be
pushed through the ingest endpoint below.

## Declare expected coverage

Coverage evaluation is a no-op until you declare expectations — a labeled
list of "assets of these kinds must be seen by a tool with this capability":

```bash
cat > coverage.json <<EOF
{
  "expect": [
    {"label": "edr-on-devices", "capability": "edr", "kinds": ["device"]}
  ]
}
EOF

limacharlie cloudsec caasm policy set --input-file coverage.json
limacharlie cloudsec caasm policy get
```

The policy is validated on write; an invalid policy is rejected loudly
rather than silently ignored.

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
