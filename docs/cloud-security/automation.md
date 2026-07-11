# Automation & Infrastructure-as-Code

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Everything Cloud Security does is scriptable: configuration is Hive records,
the query/triage surface is the [REST API](api-reference.md) and
[CLI](cli.md), and findings flow through the standard event pipeline. This
page collects the operator recipes.

## Onboarding a tenant

```bash
# 1. Subscribe the org to the extension (billing/enable gate).
limacharlie extension subscribe --name ext-cloud-security --oid $OID

# 2. Store the collector credential as a secret (hive set reads
#    record data from --input-file or piped stdin).
echo '{"secret": "<service-account-key-json>"}' | \
  limacharlie hive set --hive-name secret --key gcp-collector-sa \
    --oid $OID --enabled

# 3. Connect the provider.
cat > provider.json <<EOF
{
  "provider_type": "gcp",
  "gcp_scope": "organizations/123456789",
  "credentials": "hive://secret/gcp-collector-sa",
  "internal_domains": ["acme.com"]
}
EOF
limacharlie hive set --hive-name cloudsec_provider --key acme-gcp \
  --oid $OID --input-file provider.json --enabled

# 4. Declare the crown jewels (nothing is sensitive without a policy).
cat > classification.json <<EOF
{
  "policy_type": "classification",
  "classification": {
    "data_stores": [
      {"name_contains": ["customer", "pii"], "classes": ["pii"]}
    ]
  }
}
EOF
limacharlie hive set --hive-name cloudsec_policy --key classification \
  --oid $OID --input-file classification.json --enabled
```

## Multi-tenant policy push

The same records applied to N organizations is the MSSP fleet-policy story:

```bash
for OID in $(cat tenant-oids.txt); do
  limacharlie hive set --hive-name cloudsec_policy --key classification \
    --oid "$OID" --input-file classification.json --enabled
done
```

## Suppression rules (finding disposition policy)

A `suppression`-typed `cloudsec_policy` record dispositions matching
findings automatically — the "accept this known risk in the sandbox for 90
days" mechanic. An operator's own disposition always wins; deleting a rule
releases exactly its own findings on the next cycle; criticals are never
auto-suppressed unless a rule's `max_severity` says `critical` explicitly.

```json
{
  "policy_type": "suppression",
  "suppression": {
    "rules": [{
      "name": "sandbox-key-age",
      "match": {
        "rule": ["stale-user-managed-sa-key"],
        "account": ["proj-sandbox-*"],
        "max_severity": "high"
      },
      "effect": {
        "kind": "accepted",
        "reason": "sandbox accepted risk (SEC-123)",
        "ttl_days": 90
      }
    }]
  }
}
```

## Saved queries

Save a graph query as a `cloudsec_query` record and it appears in every
teammate's query console:

```json
{
  "version": 1,
  "name": "Exposed VMs reaching sensitive data",
  "query": {"text": "..."},
  "tags": ["weekly"]
}
```

See [Configuration](configuration.md#cloudsec_query) for the full record
shape.

## CSV export

Add `?format=csv` to `findings`, `inventory`, `compliance`, or `query` to
stream the result as a CSV attachment instead of JSON. The server walks the
full filtered set itself (filter parameters apply; paging parameters are
ignored), capped at 100,000 rows with a trailing `#`-comment row as the
truncation notice:

```bash
curl -H "Authorization: Bearer $JWT" \
  "https://api.limacharlie.io/v1/cloudsec/$OID/findings?severity=CRITICAL&severity=HIGH&format=csv" \
  -o findings.csv
```

The compliance CSV carries one row per control including the proving finding
ids — the auditor-facing evidence export.

!!! note "CLI `--output csv` is per-page"
    The CLI's global `--output csv` formats the rows the command returned —
    one page. For a full-estate export use the `?format=csv` server-side
    walk above.

## Findings ↔ Cases automation

Cloud findings emit lifecycle events into the organization's own event
stream (see the [`emission` policy](configuration.md#emission-the-event-feed)):
`cloud_finding.created` (carries the full finding under `finding`),
`cloud_finding.closed` (`{finding_id, fingerprint, finding_class}`), and
`cloud_finding.still_open` (re-asserted at most once per day for open
findings with a linked ticket). D&R rules match these like any event; the
Cases extension actions close the loop.

**Auto-case on high/critical findings** (async, grouped, storm-safe — one
case per rule category per window, and first-sync floods are summarized
upstream):

```yaml
detect:
  event: cloud_finding.created
  op: in
  path: event/finding/severity
  values: [CRITICAL, HIGH]
respond:
  - action: extension request
    extension name: ext-cases
    extension action: ingest_detection
    extension request:
      detect_id: "{{ .event.finding.fingerprint }}"
      cat: "cloudsec:{{ .event.finding.rule_id }}"
      source: cloudsec
      detect: "{{ .event.finding }}"
```

**Resolve the case when the sweep confirms the fix:**

```yaml
detect:
  event: cloud_finding.closed
  op: exists
  path: event/fingerprint
respond:
  - action: extension request
    extension name: ext-cases
    extension action: update_case
    extension request:
      detect_id: "{{ .event.fingerprint }}"
      status: resolved
      note: "Finding closed: condition no longer detected by sweep"
```

**Reopen a case that was closed while the cloud wasn't actually fixed:**

```yaml
detect:
  event: cloud_finding.still_open
  op: exists
  path: event/fingerprint
respond:
  - action: extension request
    extension name: ext-cases
    extension action: update_case
    extension request:
      detect_id: "{{ .event.fingerprint }}"
      reopen_if_closed: true
      note: "Linked cloud finding is still open — verified by latest sweep"
```

`update_case` resolves the case through the detection index (`detect_id` =
the finding fingerprint), so the rules never need a case number; a finding
with no linked case is a no-op. Cases never close findings — findings are
detection truth and close when the sweep confirms the fix (or via
operator/policy disposition).

**Non-Cases shops:** route the same `cloud_finding.*` events to
Jira/ServiceNow via an Output and key your tickets on `fingerprint` the same
way.
