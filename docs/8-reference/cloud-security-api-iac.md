# Cloud Security: API, Infrastructure-as-Code, and Case Automation

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. The features, APIs, and
    configuration formats on this page can change before general
    availability. Contact LimaCharlie to request access.

This page is the operator reference for the automation of LimaCharlie Cloud
Security. It describes the public REST API surface, the Hive records that are the
Infrastructure-as-Code surface (providers, policies, and saved queries), and the
D&R recipes that connect cloud findings to Cases.

## The REST API

All Cloud Security routes are under `https://api.limacharlie.io/v1/cloudsec/{oid}/…`
and appear in the public OpenAPI spec at
[`/openapi`](https://api.limacharlie.io/openapi). Reads need the `cloudsec.get`
permission. Writes that triage findings need `cloudsec.set`. Every route needs the
organization to have a subscription to the `ext-cloud-security` extension. A `403`
response tells you to subscribe.

The read surface includes these routes:

- `findings` — the risk-ranked worklist, with keyset pagination and server-side
  filters
- `findings/facets` and `findings/classes` — the facets and the canonical enum of
  finding classes
- `attack-paths` — the same filter selectors apply
- `chokepoints` — includes the metrics for the exposure of principals
- `ciem/public-access`, `ciem/facets`, and `ciem/identity` — the Identity 360 view
  uses `?urn=`
- `inventory`, `inventory/facets`, and `data-security/facets`
- `topology` — server-side aggregates for the estate
- `compliance`, `compliance/frameworks`, and `compliance/assignments`
- `policy/vocabulary` — the vocabulary for the classification policy
- `providers/manifest` — what a provider collects
- `caasm/assets`, `caasm/coverage`, and `caasm/policy`
- `overview` — includes the `usage` metering block for each tenant
- `risk-trend`, `changes`, and `scan-status`
- `query` — the graph DSL
- `graph/neighbors`

The `fleet/overview` route is a multi-org route with no `{oid}`. It totals the risk
across every tenant that you manage.

Three read-only preview POSTs help you write a policy before you commit it:

- `simulate/resources` — test a matcher for classification, coverage, or exclusion
  against the stored inventory
- `simulate/findings` — test a suppression matcher against open findings
- `policy/suggest` — live autocomplete of matcher values from the tenant estate

For the full route list and the response shapes, see the
[API Reference](../cloud-security/api-reference.md).

### CSV export

Add `?format=csv` to `findings`, `inventory`, `compliance`, or `query`. The route
then streams the result as a CSV attachment instead of JSON. The server reads the
full filtered set itself. Your filter query parameters apply, but the server ignores
the paging parameters. The limit is 100,000 rows, with a `#`-comment row at the end
as the truncation notice.

```bash
curl -H "Authorization: Bearer $JWT" \
  "https://api.limacharlie.io/v1/cloudsec/$OID/findings?severity=CRITICAL&severity=HIGH&format=csv" \
  -o findings.csv
```

The compliance CSV has one row for each control, and includes the ids of the
findings that prove the control. This is the evidence export for auditors.

## Hive is the IaC surface

You configure Cloud Security fully through Hive records. Every setting that you can
click in the web app, you can also set with `limacharlie hive set`. Tenant
onboarding and policy management for many tenants are therefore a script, not a
workflow in the web app.

| Hive | Record | Purpose |
|---|---|---|
| `cloudsec_provider` | one for each connection | what to collect — one of thirteen connectors for cloud infrastructure, identity and IdP, SaaS, AI, and LimaCharlie self-inventory (for the full list, see [Providers](../cloud-security/providers.md)) |
| `cloudsec_policy` | many, typed by `policy_type` | `classification` (sensitive resources), `coverage` (EDR expectation), `emission` (event feed), `exclusions` (resources to exclude), `suppression` (rules for the disposition of findings), `compliance` (scoped framework assignment) |
| `cloudsec_query` | one for each saved query | saved graph queries that the organization shares (the Query Console library) |

### Onboarding a tenant (recipe)

```bash
# 1. Subscribe the org to the extension (billing/enable gate).
limacharlie extension subscribe --name ext-cloud-security --oid $OID

# 2. Connect a provider.
cat > provider.json <<EOF
{
  "provider_type": "gcp",
  "gcp_scope": "organizations/123456789",
  "credentials": "hive://secret/gcp-collector-sa",
  "internal_domains": ["acme.com"],
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

Apply the same records to many organizations to get an MSSP fleet policy:

```bash
for OID in $(cat tenant-oids.txt); do
  limacharlie hive set --hive-name cloudsec_policy --key classification \
    --oid "$OID" --input-file classification.json --enabled
done
```

### Suppression rules (finding disposition policy)

A `cloudsec_policy` record with the `suppression` type dispositions matching
findings automatically. Use it to accept a known risk in the sandbox for 90 days.
The disposition of an operator always has priority. If you delete a rule, the next
cycle releases only the findings of that rule. Critical findings are never
auto-suppressed unless the `max_severity` of a rule is `critical`.

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

Save it as a `cloudsec_query` record. It then appears in the Query Console of every
teammate, and as an Explore lens that you can pin. The API accepts the `schedule`
and `detection` blocks, but they are inert. IaC that you write today therefore stays
valid in the scheduled-query phase.

## Findings ↔ Cases automation

Cloud findings send lifecycle events into the event stream of the organization. The
`cloudsec` webhook adapter, which LimaCharlie provisions internally, carries these
events:

- `cloud_finding.created` — carries the full finding under `finding`
- `cloud_finding.closed` — carries `{finding_id, fingerprint, finding_class}`
- `cloud_finding.still_open` — re-asserted at most one time each day, for open
  findings with a linked ticket

D&R rules match these events like any other event, and the actions of the Cases
extension complete the automation. For more automation, the same stream also
carries these events:

- `cloud_finding.updated` — the content of an open finding changed in a material
  way, such as a change of severity or of the vulnerability set
- `cloud_finding.resolved`, `.dismissed`, `.reopened`, and `.assigned` — the
  disposition verbs of an operator, for the audit of human triage decisions

The web app installs these three rules for you (Settings → Cloud Security →
Cases, an opt-in). You can also write them yourself:

**Auto-case on high/critical findings** (asynchronous and grouped, safe against
storms — one case for each rule category in each window. Upstream code summarizes
the floods of findings from the first sync):

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

**Reopen a case that was closed but the cloud is not fixed:**

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

`update_case` finds the case through the detection index, where `detect_id` is the
fingerprint of the finding. The rules therefore never need a case number. If a
finding has no linked case, the action does nothing. Cases never close findings.
Findings are the truth of detection, and they close when the sweep confirms the fix,
or through a disposition by an operator or a policy.

**Non-Cases shops:** send the same `cloud_finding.*` events to Jira or ServiceNow
with an Output on the stream of the `cloudsec` adapter. Key your tickets on
`fingerprint` in the same way.
