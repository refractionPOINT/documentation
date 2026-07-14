# Configuration Reference

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

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
| `provider_type` | `gcp` \| `aws` \| `azure` \| `okta` \| `entra` \| `google_workspace` \| `1password` \| `cloudflare` \| `openai` \| `anthropic` \| `auth0` \| `github` \| `limacharlie` |
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
| `entra` | `entra_tenant_id` (optional `entra_client_id`) — Microsoft Entra ID directory ingestion |
| `google_workspace` | `workspace_customer_id` — `my_customer` or an explicit customer id; the credential is a service-account key with domain-wide delegation plus the admin subject to impersonate |
| `1password` | `onepassword_scim_url` — the SCIM bridge URL; the credential is the SCIM bearer token |
| `cloudflare` | `cloudflare_account_id` — the 32-hex account id |
| `openai` | optional `openai_org_id` (`org-...`) — the Admin API key in the credential already implies the org; when set it is cross-checked. The credential is an Admin API key created with the read-only `api.management.read` scope |
| `anthropic` | optional `anthropic_org_uuid` — discovered from the Console Admin key; **required** when only `compliance_credentials` (an optional second `hive://secret/<name>` for the Compliance API plane) is provided |
| `auth0` | `auth0_domain` — the canonical tenant domain (e.g. `acme.us.auth0.com`; custom domains are not usable) |
| `github` | `github_org` (the organization slug) + `github_app_id` and `github_installation_id` (GitHub App auth) |
| `limacharlie` | exactly one of `limacharlie_oid` (org API key) or `limacharlie_uid` (user API key) — self-inventory of your LimaCharlie estate |

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

### `coverage` — workload coverage expectations

Declares which **cloud workloads** are expected to run a LimaCharlie
sensor, with `required` and `exempt` resource-rule lists — the "EDR on
production VMs" expectation, evaluated over the cloud inventory.

!!! note "Distinct from the CAASM expected-coverage policy"
    `limacharlie cloudsec caasm policy set` manages a **separate**
    policy with a different shape (`{expect: [{label, capability,
    kinds}]}`) evaluated over the merged *third-party asset* inventory
    ("seen by the IdP, no EDR") — see
    [CAASM](caasm.md#declare-expected-coverage). The two are not synced:
    this hive record drives cloud-workload coverage findings; the CAASM
    policy drives `coverage_gap` findings over third-party assets.

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
results.

### Scheduled queries

A saved query with a `schedule` block whose `scheduled` is `true` is
evaluated automatically — after each projection cycle by default, or on at
most one of `interval` (`"1h"`, `"24h"`, …) / `cron` (5-field expression,
optional IANA `timezone`). Evaluation emits a `cloud_query.match` event per
*new* anchor entering the match-set and `cloud_query.resolved` when an
anchor leaves, flowing through the org's `emission` policy (above) like
every other cloudsec event. Scheduled queries must be **enabled** records.
`emit_suppressed: true` opts anchors suppressed by the org's suppression
policy into emission anyway.

```json
{
  "version": 1,
  "name": "Exposed VMs reaching sensitive data",
  "query": {"text": "..."},
  "schedule": {"scheduled": true, "interval": "24h"}
}
```

The `detection` block remains reserved for the promote-to-detection phase:
it is validated for shape but nothing consumes it yet.
