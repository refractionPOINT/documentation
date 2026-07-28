# Automation & Infrastructure-as-Code

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and
    configuration formats on this page can change before general
    availability. Contact LimaCharlie to request access.

You can script everything that Cloud Security does. Configuration is Hive
records. The query and triage surface is the [REST API](api-reference.md)
and the [CLI](cli.md). Findings go through the standard event pipeline.
This page collects the operator recipes.

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

For MSSP fleet policy, apply the same records to N organizations:

```bash
for OID in $(cat tenant-oids.txt); do
  limacharlie hive set --hive-name cloudsec_policy --key classification \
    --oid "$OID" --input-file classification.json --enabled
done
```

!!! tip "Fleet-wide roll-up"
    The cross-tenant fleet board also rolls risk up across every org that
    you manage. Use `limacharlie cloudsec fleet overview` (see the
    [CLI](cli.md)), the multi-org `fleet/overview` route (see the
    [API Reference](api-reference.md)), or the Cloud Security Fleet view in
    the web app. This is the read half of the same fleet workflow for an
    MSSP.

## Suppression rules (finding disposition policy)

A `suppression`-typed `cloudsec_policy` record dispositions matching
findings automatically — the "accept this known risk in the sandbox for 90
days" mechanic. The disposition of an operator always wins. If you delete a
rule, it releases only its own findings on the next cycle. The cloud
auto-suppresses critical findings only when the `max_severity` of a rule is
`critical`. The `account` matcher takes globs, including leading-`!`
negation — `"account": ["!prod-*"]` scopes a rule to every account
**outside** `prod-*` (see [Glob syntax](configuration.md#glob-syntax)).

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

Save a graph query as a `cloudsec_query` record. It then appears in the
query console of every teammate:

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
full filtered set itself (filter parameters apply; the server ignores paging
parameters). The cap is 100,000 rows, with a trailing `#`-comment row as the
truncation notice:

```bash
curl -H "Authorization: Bearer $JWT" \
  "https://api.limacharlie.io/v1/cloudsec/$OID/findings?severity=CRITICAL&severity=HIGH&format=csv" \
  -o findings.csv
```

The compliance CSV carries one row for each control, including the finding
ids that prove it. This is the evidence export for auditors.

!!! note "CLI `--output csv` is per-page"
    The global `--output csv` of the CLI formats the rows that the command
    returned — one page. For a full-estate export, use the `?format=csv`
    server-side walk above, or the `limacharlie cloudsec export` subgroup
    (`export findings|inventory|compliance|query [-o file]`). The subgroup
    drives the same server-side full-set walk and writes the CSV to a file.

## Findings ↔ Cases automation

Cloud findings emit lifecycle events into the organization's own event
stream (see the [`emission` policy](configuration.md#emission-the-event-feed)):
`cloud_finding.created` (carries the full finding under `finding`),
`cloud_finding.closed` (`{finding_id, fingerprint, finding_class}`), and
`cloud_finding.still_open` (re-asserted at most once a day for open
findings with a linked ticket). D&R rules match these like any event. The
actions of the Cases extension complete the workflow.

**Auto-case on high/critical findings** (async, grouped, storm-safe — one
case for each rule category in each window, and the cloud summarizes
first-sync floods upstream):

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

**Reopen a case that was closed but the cloud was not fixed:**

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
the finding fingerprint), so the rules never need a case number. A finding
with no linked case is a no-op. Cases never close findings — findings are
detection truth and close when the sweep confirms the fix, or by an
operator or policy disposition.

!!! info "More lifecycle events for richer automation"
    The `created` / `closed` / `still_open` verbs above are the Cases loop,
    but D&R rules can key on more of the finding lifecycle:

    - `cloud_finding.updated` — the content of an **open** finding
      materially changed (a severity flip or a change to its vuln set),
      without a new event on every sweep. The payload carries `changed[]`
      (the fields that moved), `old_severity`, `new_severity`, and the full
      `finding`. Use it to react to escalation, for example to re-notify
      only when a finding becomes CRITICAL.
    - `cloud_finding.resolved` / `.dismissed` / `.reopened` / `.assigned` —
      the operator-disposition verbs, flat payload with an `actor` field,
      to audit human triage decisions (who accepted, muted, or reopened
      what).
    - `cloudsec.sync_completed` — the first-sync summary
      (`{total, by_class, by_severity}`) emitted one time instead of a
      flood of `created` events, one for each finding. A large estate then
      gives one event at onboarding, not thousands.
    - `cloud_resource.created` / `.updated` / `.deleted` — inventory-level
      change events. The `resource_events` flag of the [`emission`
      policy](configuration.md#emission-the-event-feed) gates them
      (**off by default**).

**Non-Cases shops:** route the same `cloud_finding.*` events to Jira or
ServiceNow through an Output. Key your tickets on `fingerprint` the same
way.
