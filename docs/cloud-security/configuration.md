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
| `cloudsec_provider` | one per cloud / IdP / SaaS / AI connection | what to collect and with which credential |
| `cloudsec_policy` | many, discriminated by `policy_type` | classification, coverage, scanning, emission, exclusions, suppression, compliance assignments |
| `cloudsec_query` | one per saved query | shared saved graph queries |

!!! info "Permissions"
    `cloudsec_provider` records are gated by the dedicated
    `cloudsec_provider.get/set/del` permissions; `cloudsec_policy` and
    `cloudsec_query` follow `cloudsec.get`/`cloudsec.set`.

## cloudsec_provider

One record per provider connection. `provider_type` discriminates; each type
reads its own scope fields. The full per-provider walkthrough — including the
credential shape for each — is in [Connecting Providers](providers.md); this is
the field reference.

Common fields (all provider types):

| Field | Meaning |
|---|---|
| `provider_type` | `gcp` \| `aws` \| `azure` \| `okta` \| `entra` \| `google_workspace` \| `1password` \| `auth0` \| `cloudflare` \| `github` \| `openai` \| `anthropic` \| `limacharlie` |
| `credentials` | A `hive://secret/<name>` reference. The credential itself lives in the secret Hive — it is **not** stored inline. |
| `compliance_credentials` | Optional second `hive://secret/<name>` reference for providers with a second credential plane (today: Anthropic's compliance/analytics key). |
| `internal_domains` | Your own email domains (bare domains, no `@`) beyond the discoverable primary — human identities outside this set are classified external. |
| `sync_now` | Opaque nonce; change its value to trigger an on-demand sweep. |
| `refresh` | Periodic re-enumeration cadence as a duration string (e.g. `"6h"`); empty uses the service default. |
| `feed_subscription` | Optional fully-qualified Pub/Sub subscription carrying a cloud change feed, for event-driven freshness between full sweeps. |

Per-provider scope fields:

| `provider_type` | Fields |
|---|---|
| `gcp` | `gcp_scope`: `projects/{id}`, `folders/{id}`, or `organizations/{id}` (optional `gcp_project`) |
| `aws` | `aws_role_arn` (the read-only role to assume), `aws_external_id`, optional `aws_regions`, optional `aws_member_role_name` — the role *name* assumed in each member account of an AWS Organization (defaults to the name in `aws_role_arn`) |
| `azure` | `azure_tenant_id`, `azure_client_id`, `azure_subscription_id` (service-principal auth) |
| `okta` | `okta_org_url` — the org base URL; the credential is an SSWS API token or an API Services app (client credentials) |
| `entra` | `entra_tenant_id`, `entra_client_id` — a standalone Entra directory connection (no Azure subscription); service-principal auth |
| `google_workspace` | `workspace_customer_id` — `my_customer` or an explicit customer id; the credential is a service-account key with domain-wide delegation plus the admin subject to impersonate |
| `1password` | `onepassword_scim_url` — the SCIM bridge URL; the credential is the SCIM bearer token |
| `auth0` | `auth0_domain` — the canonical tenant domain (`*.auth0.com`); the credential is an M2M app authorized for the Management API |
| `cloudflare` | `cloudflare_account_id` — the 32-hex account id |
| `github` | `github_org`, `github_app_id`, `github_installation_id` — a GitHub App installed on the org; the App private key is the credential |
| `openai` | optional `openai_org_id` (`org-...`); the credential is an Admin API key with `api.management.read` |
| `anthropic` | optional `anthropic_org_uuid` (required when only the compliance plane is connected); Console Admin key in `credentials`, optional compliance key in `compliance_credentials` |
| `limacharlie` | exactly one of `limacharlie_oid` (org key) or `limacharlie_uid` (user key — the MSSP fleet case) |

Use `limacharlie cloudsec provider test` to preflight a record before saving it
— see [Getting Started](getting-started.md#test-the-credential-before-saving).

## cloudsec_policy

Each record declares exactly one `policy_type` and fills the matching
sub-object.

### Rule matchers — read this first

Several policy types scope over resources with **rules**, and every rule shares
the same matcher grammar:

| Matcher | Matches |
|---|---|
| `account_contains` / `account_glob` | the resource's account (substring / glob) |
| `name_contains` / `name_glob` | the resource's name (substring / glob) |
| `resource_type` | the normalized resource type (e.g. `bucket`, `compute_instance`, `service_account`) |
| `provider` | the producing provider (`gcp`, `aws`, `okta`, …) |
| `region` | the region (globs) |
| `label` | a set of `key: value` label pairs — **all** must be present |
| `label_key_present` | a set of label keys — **all** must be present |
| `tag` | a set of tags (compute only) — **all** must be present |
| `public` | tri-state exposure (`true` / `false`) |
| `content_class` | detected sensitive-content classes on a data store (`pii`, `pci`, `phi`, `financial`) |

!!! warning "Matchers within a rule are ANDed"
    A rule matches a resource only when **every populated dimension matches**.
    Within a single-valued dimension the listed patterns are OR alternatives
    (`account_glob: ["a-*", "b-*"]` matches either); set-valued dimensions
    (`label`, `tag`) require **all** entries. A **rule with no matcher matches
    nothing**, and a populated dimension that cannot be evaluated for a given
    resource **fails** the rule rather than being ignored. Separate rules in a
    list compose with OR.

    (This is a change from earlier behavior, where dimensions within a rule were
    ORed. The `store_kind` matcher has been folded into `resource_type`.)

Not every dimension is honored on every surface — `tag` is compute-only,
`content_class`/`public`/`classes` apply to data stores, and the `exclusions`
emission list honors only account/name/provider. The console's policy editors
enforce this per surface and offer live value **autocomplete** from your actual
estate, plus a **Simulate** preview that shows which resources a rule matches
before you save (see [Previewing policies](#previewing-policies)).

Assign-side fields (not matchers): `name` (provenance), `classes` (the classes a
`classification` data-store rule assigns), and `tier`
(`critical`/`high`/`medium`/`low`).

### `classification` — crown jewels

Declares which resources are sensitive (nothing is sensitive by default). Rules
match resources and assign classes and/or a criticality tier, in three sections
— `data_stores`, `compute`, `identities`:

```json
{
  "policy_type": "classification",
  "classification": {
    "data_stores": [
      {"name_contains": ["customer", "pii"], "classes": ["pii"]},
      {"content_class": ["pci"], "classes": ["pci"]}
    ],
    "compute": [
      {"label": {"tier": "crown-jewel"}, "tier": "critical"}
    ]
  }
}
```

Content-based sensitivity is expressed with `content_class` rules: the agentless
scanner samples data stores and surfaces detected content classes (`pii`, `pci`,
`phi`, `financial`) as facts on the resource, and a `content_class` rule is what
turns a detection into a sensitivity claim. Your explicit policy always remains
authoritative.

!!! note "auto_classify has been replaced"
    Earlier versions accepted an `auto_classify: true` boolean. It has been
    retired in favor of explicit, previewable `content_class` rules — the same
    detection, but visible in the policy and testable with Simulate. Remove
    `auto_classify` from any existing record.

### `coverage` — workload coverage expectations

Declares which **cloud workloads** are expected to run a LimaCharlie sensor,
with `required` and `exempt` resource-rule lists — the "EDR on production VMs"
expectation, evaluated over the cloud inventory. An empty `required` means every
compute resource is expected to be covered; `exempt` wins.

!!! note "Distinct from the CAASM expected-coverage policy"
    `limacharlie cloudsec caasm policy set` manages a **separate** policy with a
    different shape (`{expect: [{label, capability, kinds}]}`) evaluated over the
    merged *third-party asset* inventory ("seen by the IdP, no EDR") — see
    [CAASM](caasm.md#declare-expected-coverage). The two are not synced: this
    hive record drives cloud-workload coverage findings; the CAASM policy drives
    `coverage_gap` findings over third-party assets.

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

| Field | Meaning | Default |
|---|---|---|
| `resource_events` | `cloud_resource.*` inventory change events | off |
| `finding_events` | `cloud_finding.*` lifecycle events | on |
| `ops_events` | operational events (sweep/scan failures) | off |
| `severity_floor` | drop finding events below this severity | none |
| `suppress_first_sync` | emit one summary instead of a per-finding flood on the first / rebuild sweep | on |

See [Findings are events too](findings.md#findings-are-events-too) for the full
event taxonomy.

### `exclusions` — the escape hatch

Excludes matching resources from `collection`, `scanning`, or `emission` (three
independent rule lists; collection rules add `services` and `resource_types`
matchers on top of the shared resource matchers). Use it for the million-object
bucket that should not be enumerated, or the noisy account that should not emit
events. Removal takes effect on the next sweep.

### `suppression` — finding disposition policy

Auto-dispositions matching findings — see
[Automation & IaC](automation.md#suppression-rules-finding-disposition-policy)
for semantics and a worked example. Ordered `rules`; each rule's `match` accepts
`finding_class`, `rule`, `account`, `urn_prefix`, `max_severity`; the `effect`
is `kind` (`accepted`/`false_positive`), `reason` (required), `ttl_days`.

### `compliance` — scoped assignments

A named framework assignment over a scoped subset of the estate — see
[Compliance](compliance.md#scoped-assignments). Fields: `framework_id`
(required, lowercase slug), `description`, `scope` (the account/name matchers).

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

`query` takes one of `named` (a query-pack reference), `text`, or `ast` (the raw
DSL). Optional `ui` hints (view, columns) shape how the console renders results;
the query appears in the [Query console and as an Explore lens](graph.md#graph-queries).
`schedule` and `detection` blocks are accepted for forward-compatibility;
turning a saved query into a scheduled detection source (emitting `cloud_query.*`
events) is an emerging capability.

## Previewing policies

Two read-only, `cloudsec.get`-gated aids make policy authoring safe — both are
in the console policy editors and on the API (there is no CLI command for them):

- **Simulate** evaluates an in-progress matcher against your real data before you
  save. A resource matcher (classification / coverage / exclusions) is previewed
  against stored inventory; a suppression matcher is previewed against open
  findings. The result is a match count plus a bounded sample.
- **Vocabulary & autocomplete** feed the editors the closed vocabularies
  (resource types, providers, tiers, content classes) and live value suggestions
  drawn from your estate's actual accounts and names.

See the [API Reference](api-reference.md#policy-authoring-simulate-vocabulary)
for the underlying routes.
