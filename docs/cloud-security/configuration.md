# Configuration Reference

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and
    configuration formats on this page can change before general
    availability. Contact LimaCharlie to request access.

You configure Cloud Security completely through three Hive types.
`limacharlie hive set` can configure anything that the web app can
configure. Tenant onboarding and fleet-wide policy are thus a script, not a
manual workflow (see [Automation & IaC](automation.md) for recipes).

| Hive | Records | Purpose |
|---|---|---|
| `cloudsec_provider` | one for each cloud / IdP / SaaS / AI connection | what to collect and with which credential |
| `cloudsec_policy` | many, discriminated by `policy_type` | classification, coverage, emission, exclusions, suppression, compliance assignments |
| `cloudsec_query` | one for each saved query | shared saved graph queries |

!!! info "Permissions"
    The dedicated `cloudsec_provider.get/set/del` permissions gate
    `cloudsec_provider` records. `cloudsec_policy` and `cloudsec_query` obey
    `cloudsec.get`/`cloudsec.set`.

## cloudsec_provider

One record for each provider connection. `provider_type` discriminates; each
type reads its own scope fields. [Connecting Providers](providers.md) has
the full walkthrough for each provider, including the credential shape. This
page is the field reference.

Common fields (all provider types):

| Field | Meaning |
|---|---|
| `provider_type` | `gcp` \| `aws` \| `azure` \| `okta` \| `entra` \| `google_workspace` \| `1password` \| `auth0` \| `cloudflare` \| `github` \| `openai` \| `anthropic` \| `limacharlie` |
| `credentials` | A `hive://secret/<name>` reference. The credential itself is in the secret Hive — it is **not** stored inline. |
| `compliance_credentials` | Optional second `hive://secret/<name>` reference for providers with a second credential plane (today: the compliance/analytics key of Anthropic). |
| `internal_domains` | Your own email domains (bare domains, no `@`) beyond the discoverable primary — human identities outside this set are classified external. |
| `sync_now` | Opaque nonce; change its value to trigger an on-demand sweep. |
| `refresh` | Periodic re-enumeration cadence as a duration string (e.g. `"6h"`); if empty, the service default applies. |
| `feed_subscription` | Optional fully-qualified Pub/Sub subscription that carries a cloud change feed, for event-driven freshness between full sweeps. |

Scope fields for each provider:

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

Use `limacharlie cloudsec provider test` to preflight a record before you
save it — see
[Getting Started](getting-started.md#test-the-credential-before-saving).

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
    In a single-valued dimension, the listed patterns are OR alternatives
    (`account_glob: ["a-*", "b-*"]` matches either). Set-valued dimensions
    (`label`, `tag`) need **all** entries. A **rule with no matcher matches
    nothing**. If a populated dimension cannot be evaluated for a resource, it
    **fails** the rule; the rule does not ignore it. Separate rules in a list
    compose with OR.

    (This is a change from earlier behavior, where dimensions within a rule were
    ORed. The `store_kind` matcher is now part of `resource_type`.)

#### Glob syntax

Every glob dimension (`account_glob`, `name_glob`, `region`, and suppression
`account` matchers) shares one dialect:

| Pattern | Matches |
|---|---|
| `*` | any run of characters (not `/`) |
| `?` | one character (not `/`) |
| `[abc]`, `[a-z]` | a character class; `[^…]` or `[!…]` negates the class |
| `{a,b}` | alternation — `proj-{prod,staging}-*` |
| `**` | any run **including** `/` (only differs from `*` on values containing `/`) |
| `\c` | the literal character `c` |

A pattern whose **first character is `!` is a negation**. In one list the
positive patterns OR together as before, and any matching negation **vetoes**
the whole list. A list with only negations matches everything that it does not
exclude — `account_glob: ["!legion-*"]` means "every account **without** the
`legion-` prefix". `\!` matches a literal leading `!`. Case-insensitive
dimensions stay case-insensitive under negation.

```yaml
account_glob: ["*-prod", "!legion-*"]   # every -prod account except legion ones
region: ["!eu-*"]                        # everywhere outside the EU
```

Not every dimension is honored on every surface — `tag` is compute-only,
`content_class`/`public`/`classes` apply to data stores, and the `exclusions`
emission list honors only account/name/provider. The policy editors in the web
app enforce this for each surface. They also give live value **autocomplete**
from your real estate, and a **Simulate** preview that shows which resources a
rule matches before you save (see [Previewing policies](#previewing-policies)).

Assign-side fields (not matchers): `name` (provenance), `classes` (the classes
that a `classification` data-store rule assigns), and `tier`
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

`content_class` rules express content-based sensitivity. The agentless scanner
samples data stores and shows the detected content classes (`pii`, `pci`,
`phi`, `financial`) as facts on the resource. A `content_class` rule turns a
detection into a sensitivity claim. Your explicit policy always stays
authoritative.

!!! note "auto_classify has been replaced"
    Earlier versions accepted an `auto_classify: true` boolean. It is retired,
    and explicit, previewable `content_class` rules replace it — the same
    detection, but visible in the policy and testable with Simulate. Remove
    `auto_classify` from any existing record.

### `coverage` — workload coverage expectations

Declares which **cloud workloads** must run a LimaCharlie sensor, with
`required` and `exempt` resource-rule lists — the "EDR on production VMs"
expectation, evaluated over the cloud inventory. An empty `required` means that
every compute resource must be covered; `exempt` wins.

!!! note "Distinct from the CAASM expected-coverage policy"
    `limacharlie cloudsec caasm policy set` manages a **separate** policy with a
    different shape (`{expect: [{label, capability, kinds}]}`) evaluated over the
    merged *third-party asset* inventory ("seen by the IdP, no EDR") — see
    [CAASM](caasm.md#declare-expected-coverage). The two are not synced: this
    hive record drives cloud-workload coverage findings; the CAASM policy drives
    `coverage_gap` findings over third-party assets.

### `emission` — the event feed

Controls which Cloud Security events reach the organization's event stream:

| Field | Meaning | Default |
|---|---|---|
| `resource_events` | `cloud_resource.*` inventory change events | off |
| `finding_events` | `cloud_finding.*` lifecycle events | on |
| `ops_events` | operational events (sweep failures) | off |
| `severity_floor` | drop finding events below this severity | none |
| `suppress_first_sync` | emit one summary instead of a flood of events, one for each finding, on the first / rebuild sweep | on |

See [Findings are events too](findings.md#findings-are-events-too) for the full
event taxonomy.

### `exclusions` — the escape hatch

Excludes matching resources from `collection` or `emission` (two
independent rule lists; collection rules add `services` and `resource_types`
matchers to the shared resource matchers). Use it for the bucket with a million
objects that must not be enumerated, or the noisy account that must not emit
events. A removal takes effect on the next sweep.

### `suppression` — finding disposition policy

Auto-dispositions matching findings — see
[Automation & IaC](automation.md#suppression-rules-finding-disposition-policy)
for semantics and a worked example. Ordered `rules`; the `match` of each rule
accepts `finding_class`, `rule`, `account`, `urn_prefix`, `max_severity`; the
`effect` is `kind` (`accepted`/`false_positive`), `reason` (required),
`ttl_days`.

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
DSL). Optional `ui` hints (view, columns) shape how the web app renders results.
The query appears in the [Query console and as an Explore lens](graph.md#graph-queries).
`schedule` and `detection` blocks are accepted for forward-compatibility. A
saved query that becomes a scheduled detection source, and emits `cloud_query.*`
events, is an emerging capability.

## Previewing policies

Two read-only aids, gated by `cloudsec.get`, make policy authoring safe. Both
are in the policy editors of the web app, on the API, and on the CLI
(`limacharlie cloudsec simulate` / `limacharlie cloudsec policy`):

- **Simulate** evaluates an in-progress matcher against your real data before you
  save. It previews a resource matcher (classification / coverage / exclusions)
  against stored inventory, and a suppression matcher against open findings. The
  result is a match count and a bounded sample.
- **Vocabulary & autocomplete** feed the editors the closed vocabularies
  (resource types, providers, tiers, content classes) and live value suggestions
  drawn from the real accounts and names in your estate.

See the [API Reference](api-reference.md#policy-authoring-simulate-vocabulary)
for the underlying routes.
