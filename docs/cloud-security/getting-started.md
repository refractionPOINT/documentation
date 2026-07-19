# Getting Started with Cloud Security

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

This guide takes an organization from zero to a populated Cloud Security
dashboard: enable the product, connect a provider, run the first sweep, and
declare what matters. You can do all of it in the console or entirely as code —
both are shown.

## 1. Enable Cloud Security

Cloud Security is enabled per organization by subscribing to the
`ext-cloud-security` extension — the subscription is both the enable gate and
the billing hook. In the web console, open the extension from the Add-Ons
marketplace and click **Subscribe**, or from the CLI:

```bash
limacharlie extension subscribe --name ext-cloud-security --oid $OID
```

Until the organization is subscribed, every Cloud Security API route and
console view returns `403`.

Once enabled, **Cloud Security** appears as a workspace in the organization
sidebar.

## 2. Connect a provider

A provider connection is one `cloudsec_provider` record. Each provider needs a
scope (which account/tenant/org to enumerate) and a read-only credential. The
[Connecting Providers](providers.md) page has the full per-provider setup — the
steps below use Google Cloud as the worked example.

### In the console

1. Open **Cloud Security → Settings → Providers** and click **+ Add provider**.
2. Give the connection a **name**, pick the **provider type**, and fill the
   type-specific connection fields (for GCP, the scope — a project, folder, or
   organization).
3. Supply the **credential**: either reference an existing
   [secret](../7-administration/config-hive/secrets.md) by
   `hive://secret/<name>`, or paste the credential to have the console store it
   as a new secret for you. Credentials are always stored as a secret and
   referenced — never inlined into the provider record.
4. Click **Test Provider** to run the read-only preflight (see below), then
   save. Saving an enabled connection starts collection.

The provider row then shows its sync status, resource count, and per-row actions
(**What you get**, **Sync now**, **Edit**, **Delete**).

### As code

The credential lives in the secret Hive; the provider record references it:

```bash
# Store the collector credential as a secret (hive set reads the record
# data from --input-file or piped stdin).
echo '{"secret": "<service-account-key-json>"}' | \
  limacharlie hive set --hive-name secret --key gcp-collector-sa \
    --oid $OID --enabled

# Connect the provider.
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

The full field reference is in
[Configuration](configuration.md#cloudsec_provider), and every provider's scope
fields and credential shape are in [Connecting Providers](providers.md).

!!! tip "internal_domains matters for CIEM"
    List every email domain your own people use. A human identity whose domain
    is not in the internal set is classified *external*, and external access to
    sensitive resources is one of the highest-signal finding classes. The
    collector discovers the primary cloud-org domain on its own; secondary
    domains must be declared.

### Test the credential before saving

The provider test connects with the supplied credential and probes every
permission surface a sweep needs, without storing anything — the same check the
console's **Test Provider** button runs:

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

## 3. Watch the first sweep

Saving an enabled provider record starts collection. Check progress:

```bash
limacharlie cloudsec scan-status --provider gcp
```

The status carries whether a sweep is running, when the last one started and
completed, the diff stats of the last run, and any error. To force an immediate
re-enumeration later, change the record's `sync_now` value (any new value
triggers a sweep) or use **Sync now** on the provider row; `refresh` sets the
periodic cadence.

## 4. Declare what matters

Out of the box, **nothing is classified sensitive** — sensitivity is your
declaration, made with a `classification`-typed `cloudsec_policy` record (your
crown jewels). Rules match resources by account, name, resource type, label, or
tag and assign classes:

```bash
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

Sensitivity drives the attack-path and CIEM analytics: "exposed workload that
can reach *sensitive* data" and "external identity with access to *sensitive*
store" both need to know what sensitive means in your estate.

!!! tip "Content-based classification"
    Beyond declaring crown jewels by name/label, you can add `content_class`
    rules so that data stores where the agentless scanner samples sensitive
    content (`pii`, `pci`, `phi`, `financial`) are treated as sensitive. Detected
    content classes are always surfaced as facts on a resource; a `content_class`
    rule is what turns a detection into a sensitivity claim. See
    [Configuration](configuration.md#classification-crown-jewels). (The former
    `auto_classify` boolean has been replaced by these explicit, previewable
    rules.)

In the console, the same policy is authored on **Cloud Security → Policies →
Data classification**, where a live **Simulate** panel shows exactly which
resources a rule matches before you save it.

## 5. Look at the result

In the console, the **Overview** page is the at-a-glance risk layer and
**Risks** is the worklist. From the CLI:

```bash
# The composed risk overview: score, severity distribution, top paths.
limacharlie cloudsec overview

# The findings worklist, worst first.
limacharlie cloudsec finding list --severity CRITICAL --severity HIGH

# What you own.
limacharlie cloudsec inventory facets
```

From here, continue with [Findings & Triage](findings.md) for the day-to-day
workflow, [Connecting Providers](providers.md) to add more of your estate, or
[Automation & IaC](automation.md) to wire findings into Cases and onboard more
tenants as code.
