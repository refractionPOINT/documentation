# Configuration Reference

Cloud Security is configured entirely through three Hive types. Anything the
console can configure, `limacharlie hive set` can configure — which makes
tenant onboarding and fleet-wide policy a script, not a UI workflow (see
[Automation & IaC](automation.md) for recipes).

| Hive | Records | Purpose |
|---|---|---|
| `cloudsec_provider` | one per cloud / IdP connection | what to collect and with which credential |
| `cloudsec_policy` | many, discriminated by `policy_type` | classification, coverage, scanning, emission, exclusions, suppression, compliance assignments |
| `cloudsec_query` | one per saved query | shared saved graph queries |

!!! info "Permissions"
    `cloudsec_provider` records are gated by the dedicated
    `cloudsec_provider.get/set/del` permissions; `cloudsec_policy` and
    `cloudsec_query` follow `cloudsec.get`/`cloudsec.set`.

## cloudsec_provider

One record per provider connection. `provider_type` discriminates; each type
reads its own scope fields.

Common fields:

| Field | Meaning |
|---|---|
| `provider_type` | `gcp` \| `aws` \| `azure` \| `okta` \| `1password` \| `google_workspace` \| `cloudflare` |
| `credentials` | A `hive://secret/<name>` reference. The credential itself lives in the secret hive — it is **not** stored inline. |
| `internal_domains` | Your own email domains (bare domains, no `@`) beyond the discoverable primary — identities outside this set are classified external. |
| `sync_now` | Opaque nonce; change its value to trigger an on-demand sweep. |
| `refresh` | Periodic re-enumeration cadence as a duration string (e.g. `"6h"`); empty uses the service default. |
| `feed_subscription` | Optional fully-qualified Pub/Sub subscription carrying a cloud change feed, for event-driven freshness between full sweeps. |

Per-provider scope fields:

| `provider_type` | Fields |
|---|---|
| `gcp` | `gcp_scope`: `projects/{id}`, `folders/{id}`, or `organizations/{id}` (optional `gcp_project`) |
| `aws` | `aws_role_arn` (the read-only role to assume), `aws_external_id`, optional `aws_regions`, optional `aws_member_role_name` — the role *name* assumed in each member account of an AWS Organization (defaults to the name in `aws_role_arn`, the common StackSet pattern) |
| `azure` | `azure_tenant_id`, `azure_client_id`, `azure_subscription_id` (service-principal auth) |
| `okta` | `okta_org_url` — the org base URL; the credential is an SSWS API token or an API Services app (client credentials) |
| `google_workspace` | `workspace_customer_id` — `my_customer` or an explicit customer id; the credential is a service-account key with domain-wide delegation plus the admin subject to impersonate |
| `1password` | `onepassword_scim_url` — the SCIM bridge URL; the credential is the SCIM bearer token |
| `cloudflare` | `cloudflare_account_id` — the 32-hex account id |

Use `limacharlie cloudsec provider test` to preflight a record before saving
it — see [Getting Started](getting-started.md#test-the-credential-before-saving).

## cloudsec_policy

Each record declares exactly one `policy_type` and fills the matching
sub-object.

### `classification` — crown jewels

Declares which resources are sensitive (nothing is sensitive by default).
Rules match resources by account/name/label/tag and assign classes:

```json
{
  "policy_type": "classification",
  "classification": {
    "data_stores": [
      {"name_contains": ["customer", "pii"], "classes": ["pii"]}
    ],
    "compute": [
      {"label": {"tier": "crown-jewel"}, "classes": ["critical-infra"]}
    ],
    "auto_classify": true
  }
}
```

`auto_classify: true` opts into content-based detection of sensitive data
(sampled during agentless scanning); the explicit policy always remains
authoritative.

Rule matchers (shared by every policy type that scopes over resources):
`account_contains`, `account_glob`, `name_contains`, `name_glob`,
`label` (key→value), `label_key_present`, `tag`.

### `coverage` — CAASM expectations

The expected-coverage declaration, with `required` and `exempt` rule lists.
Equivalent to (and kept in sync with) `limacharlie cloudsec caasm policy set`
— see [CAASM](caasm.md#declare-expected-coverage).

### `scanning` — agentless content scanning

Names the YARA rules to run against snapshot-scanned workloads and the
classification each match assigns, plus an optional resource `scope`:

```json
{
  "policy_type": "scanning",
  "scanning": {
    "rules": [{"yara_rule": "hive://yara/crypto-miners", "classification": "malware"}],
    "scope": [{"account_glob": ["proj-prod-*"]}]
  }
}
```

### `emission` — the event feed

Controls which Cloud Security events reach the organization's event stream:

| Field | Meaning |
|---|---|
| `resource_events` | `cloud_resource.*` inventory change events |
| `finding_events` | `cloud_finding.*` lifecycle events |
| `ops_events` | operational events (sweep start/complete, errors) |
| `severity_floor` | drop finding events below this severity |
| `suppress_first_sync` | don't flood the stream with the initial enumeration |

### `exclusions` — the escape hatch

Excludes matching resources from `collection`, `scanning`, or `emission`
(three independent rule lists; rules add `services` and `resource_types`
matchers on top of the shared resource matchers). Use it for the
million-object bucket that should not be enumerated, or the noisy account
that should not emit events. Removal takes effect on the next sweep.

### `suppression` — finding disposition policy

Auto-dispositions matching findings — see
[Automation & IaC](automation.md#suppression-rules-finding-disposition-policy)
for semantics and a worked example. Match fields: `finding_class`, `rule`,
`account`, `urn_prefix`, `max_severity`; effect: `kind`
(`accepted`/`false_positive`/`mitigated`), `reason`, `ttl_days`.

### `compliance` — scoped assignments

A named framework assignment over a scoped subset of the estate — see
[Compliance](compliance.md#scoped-assignments). Fields: `framework_id`
(required, lowercase slug), `description`, `scope` (v1 supports the
account/name matchers only).

## cloudsec_query

A saved graph query, shared org-wide:

```json
{
  "version": 1,
  "name": "Exposed VMs reaching sensitive data",
  "description": "Weekly review lens",
  "query": {"text": "..."},
  "project": "rows",
  "tags": ["weekly"]
}
```

`query` takes one of `named` (a query-pack reference), `text`, or `ast` (the
raw DSL). Optional `ui` hints (view, columns) shape how the console renders
results. `schedule` and `detection` blocks are accepted so IaC written today
survives the scheduled-query phase, but are not yet active.
