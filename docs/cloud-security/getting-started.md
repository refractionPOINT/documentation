# Getting Started with Cloud Security

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

This page takes an organization from zero to a populated Cloud Security
dashboard: subscribe the extension, store a credential, connect a provider,
and run the first sweep.

## 1. Subscribe the extension

Cloud Security is enabled per organization by subscribing to the
`ext-cloud-security` extension — the subscription is both the enable gate
and the billing hook. In the web console, open the extension from the
Add-Ons marketplace and click **Subscribe**, or from the CLI:

```bash
limacharlie extension subscribe --name ext-cloud-security --oid $OID
```

Until the organization is subscribed, every Cloud Security API route and
console view returns `403`.

## 2. Store the provider credential as a secret

Collector credentials are never stored inline in the provider record — the
record references a [secret](../7-administration/config-hive/secrets.md) by
`hive://secret/<name>`:

```bash
echo '{"secret": "<service-account-key-json>"}' | \
  limacharlie hive set --hive-name secret --key gcp-collector-sa \
    --oid $OID --enabled
```

(`hive set` reads the record data from `--input-file` or piped stdin.)

What the credential must be able to do depends on the provider — the
credential test in the next step tells you exactly which permission surfaces
are missing.

## 3. Connect a provider

A provider connection is one `cloudsec_provider` Hive record. The full field
reference is in [Configuration](configuration.md#cloudsec_provider); the
short version per provider:

| Provider | `provider_type` | Scope fields |
|---|---|---|
| Google Cloud | `gcp` | `gcp_scope` (`projects/{id}`, `folders/{id}`, or `organizations/{id}`) |
| AWS | `aws` | `aws_role_arn` + `aws_external_id`, optional `aws_regions`, optional `aws_member_role_name` for AWS Organizations |
| Azure | `azure` | `azure_tenant_id`, `azure_client_id`, `azure_subscription_id` |
| Okta | `okta` | `okta_org_url` (e.g. `https://acme.okta.com`) |
| Google Workspace | `google_workspace` | `workspace_customer_id` (`my_customer` or an explicit id) |
| 1Password | `1password` | `onepassword_scim_url` |
| Cloudflare | `cloudflare` | `cloudflare_account_id` |

Example — a GCP organization:

```bash
cat > provider.json <<EOF
{
  "provider_type": "gcp",
  "gcp_scope": "organizations/123456789",
  "credentials": "hive://secret/gcp-collector-sa",
  "internal_domains": ["acme.com", "acme.io"]
}
EOF

limacharlie hive set --hive-name cloudsec_provider --key acme-gcp \
  --oid $OID --input-file provider.json --enabled
```

!!! tip "internal_domains matters for CIEM"
    List every email domain your own people use. A human identity whose
    domain is not in the internal set is classified *external*, and external
    access to sensitive resources is one of the highest-signal finding
    classes. The collector discovers the primary cloud-org domain on its
    own; secondary domains must be declared.

### Test the credential before saving

The provider test connects with the supplied credential and probes every
permission surface a sweep needs, without storing anything:

```bash
limacharlie cloudsec provider test --input-file provider.json
```

The response is a per-check report: each check carries `id`, `name`,
`required`, `ok`, and a human-readable `detail`. `report.ok` is the verdict
over the *required* checks only — a failed optional check means that surface
degrades gracefully (e.g. one inventory type missing) rather than the
connection failing.

!!! info "Permissions"
    The provider test requires `cloudsec.set` — testing a credential is as
    sensitive as saving one. For the test (and only the test) the credential
    may be passed inline instead of as a `hive://secret/` reference; it is
    used ephemerally and never stored or logged.

## 4. Watch the first sweep

Saving an enabled provider record starts collection. Check progress:

```bash
limacharlie cloudsec scan-status --provider gcp
```

The status carries whether a sweep is running, when the last one started and
completed, the diff stats of the last run, and any error. To force an
immediate re-enumeration later, change the record's `sync_now` value (any
new value triggers a sweep); `refresh` sets the periodic cadence.

## 5. Declare what matters

Out of the box, **nothing is classified sensitive** — sensitivity is your
declaration, made with a `classification`-typed `cloudsec_policy` record
(crown jewels), optionally augmented by content-based auto-classification:

```bash
cat > classification.json <<EOF
{
  "policy_type": "classification",
  "classification": {
    "data_stores": [
      {"name_contains": ["customer", "pii"], "classes": ["pii"]}
    ],
    "auto_classify": true
  }
}
EOF

limacharlie hive set --hive-name cloudsec_policy --key classification \
  --oid $OID --input-file classification.json --enabled
```

Sensitivity drives the attack-path and CIEM analytics: "exposed workload
that can reach *sensitive* data" and "external identity with access to
*sensitive* store" both need to know what sensitive means in your estate.

## 6. Look at the result

```bash
# The composed risk overview: score, severity distribution, top paths.
limacharlie cloudsec overview

# The findings worklist, worst first.
limacharlie cloudsec finding list --severity CRITICAL --severity HIGH

# What you own.
limacharlie cloudsec inventory facets
```

From here, continue with [Findings & Triage](findings.md) for the day-to-day
workflow, or [Automation & IaC](automation.md) to wire findings into Cases
and onboard more tenants as code.
