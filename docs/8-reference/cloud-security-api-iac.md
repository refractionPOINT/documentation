# Cloud Security: API, Infrastructure-as-Code, and Case Automation

This page is the operator reference for automating LimaCharlie Cloud Security: the
public REST API surface, the Hive records that ARE the Infrastructure-as-Code
surface (providers, policies, saved queries), and the D&R recipes that close the
loop between cloud findings and Cases.

## The REST API

All Cloud Security routes live under `https://api.limacharlie.io/v1/cloudsec/{oid}/…`
and appear in the public OpenAPI spec at
[`/openapi`](https://api.limacharlie.io/openapi). Reads require the `cloudsec.get`
permission, finding-triage writes require `cloudsec.set`, and every route requires
the organization to be subscribed to the cloud security extension (a `403` tells
you to subscribe).

The read surface includes: `findings` (risk-ranked worklist with keyset pagination
and server-side filters), `findings/facets`, `attack-paths` (with the same filter
selectors), `chokepoints` (incl. the principal-exposure metrics), `ciem/public-access`,
`inventory` (+`inventory/facets`), `compliance` (+`compliance/frameworks`),
`overview` (incl. the per-tenant `usage` metering block), `risk-trend`, `changes`,
`scan-status`, `query` (the graph DSL), and `graph/neighbors`.

### CSV export

Add `?format=csv` to `findings`, `inventory`, `compliance`, or `query` to stream the
result as a CSV attachment instead of JSON. The server walks the full filtered set
itself (your filter query parameters apply; paging parameters are ignored), capped
at 100,000 rows with a trailing `#`-comment row as the truncation notice.

```bash
curl -H "Authorization: Bearer $JWT" \
  "https://api.limacharlie.io/v1/cloudsec/$OID/findings?severity=CRITICAL&severity=HIGH&format=csv" \
  -o findings.csv
```

The compliance CSV carries one row per control including the proving finding ids —
the auditor-facing evidence export.

## Hive is the IaC surface

Cloud Security is configured entirely through Hive records. Anything you can click
in the console you can `limacharlie hive set` — which makes tenant onboarding and
multi-tenant policy management a script, not a UI workflow.

| Hive | Record | Purpose |
|---|---|---|
| `cloudsec_provider` | one per cloud/IdP connection | what to collect (GCP / AWS / Azure / Okta / Google Workspace) |
| `cloudsec_policy` | many, typed by `policy_type` | `classification` (crown jewels), `coverage` (EDR expectation), `scanning` (agentless YARA), `emission` (event feed), `exclusions` (resource escape hatch), `suppression` (finding disposition rules) |
| `cloudsec_query` | one per saved query | org-shared saved graph queries (the Query Console library) |

### Onboarding a tenant (recipe)

```bash
# 1. Subscribe the org to the extension (billing/enable gate).
limacharlie extension subscribe --name ext-cloud-security --oid $OID

# 2. Connect a provider.
cat > provider.json <<EOF
{
  "provider_type": "gcp",
  "scope": "organizations/123456789",
  "secret": {"secret_name": "hive://secret/gcp-collector-sa"},
  "sync_now": "onboard-1"
}
EOF
limacharlie hive set --hive-name cloudsec_provider --key ${ORG_CODE}-gcp \
  --oid $OID --input-file provider.json --enabled

# 3. Declare the crown jewels (nothing is sensitive without a policy).
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

### Multi-tenant policy push (recipe)

The same records applied to N organizations is the MSSP fleet-policy story:

```bash
for OID in $(cat tenant-oids.txt); do
  limacharlie hive set --hive-name cloudsec_policy --key classification \
    --oid "$OID" --input-file classification.json --enabled
done
```

### Suppression rules (finding disposition policy)

A `suppression`-typed `cloudsec_policy` record dispositions matching findings
automatically — the "accept this known risk in the sandbox for 90 days" mechanic.
An operator's own disposition always wins, deleting a rule releases exactly its own
findings on the next cycle, and criticals are never auto-suppressed unless a rule's
`max_severity` says `critical` explicitly.

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

### Saved queries

```json
{
  "version": 1,
  "name": "Exposed VMs reaching sensitive data",
  "query": {"text": "MATCH (t:ComputeInstance {is_sensitive:true})<-[:can_reach]-(s:ComputeInstance) RETURN s, t"},
  "project": "rows",
  "tags": ["weekly"]
}
```

Save it as a `cloudsec_query` record and it appears in every teammate's Query
Console and as a pinnable Explore lens. The `schedule` and `detection` blocks are
accepted (so IaC written today survives the scheduled-query phase) but inert.

## Findings ↔ Cases automation

Cloud findings emit lifecycle events into the organization's own event stream via
the internally-provisioned `cloudsec` webhook adapter: `cloud_finding.created`
(carries the full finding under `finding`), `cloud_finding.closed`
(`{finding_id, fingerprint, finding_class}`), and `cloud_finding.still_open`
(re-asserted at most once per day for open findings with a linked ticket). D&R
rules match these like any event; the Cases extension actions close the loop.

The console installs these three rules with one click (Settings → Cloud Security →
Cases, an opt-in), or write them yourself:

**Auto-case on high/critical findings** (async, grouped, storm-safe — one case per
rule category per window, and first-sync floods are summarized upstream):

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

`update_case` resolves the case through the detection index (`detect_id` = the
finding fingerprint), so the rules never need a case number; a finding with no
linked case is a no-op. Cases never close findings — findings are detection truth
and close when the sweep confirms the fix (or via operator/policy disposition).

**Non-Cases shops:** route the same `cloud_finding.*` events to Jira/ServiceNow via
an Output on the `cloudsec` adapter's stream and key your tickets on `fingerprint`
the same way.
