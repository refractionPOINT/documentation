# Getting Started with Cloud Security

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and
    configuration formats on this page can change before general
    availability. Contact LimaCharlie to request access.

This guide takes an organization from zero to a Cloud Security workspace
with data: enable the product, connect a provider, run the first sweep, and
declare what matters. You can do all of it in the web app or as code. This
page shows both.

## 1. Enable Cloud Security

To enable Cloud Security for an organization, subscribe to the
`ext-cloud-security` extension. The subscription is both the enable gate and
the billing hook. In the web app, open the extension from the Add-Ons
marketplace and click **Subscribe**. From the CLI:

```bash
limacharlie extension subscribe --name ext-cloud-security --oid $OID
```

Until the organization subscribes, every Cloud Security API route and view
in the web app returns `403`.

After you enable it, **Cloud Security** appears as a workspace in the
organization sidebar.

## 2. Connect a provider

A provider connection is one `cloudsec_provider` record. Each provider needs a
scope (which account/tenant/org to enumerate) and a read-only credential. The
[Connecting Providers](providers.md) page has the full setup for each
provider. The steps below use Google Cloud as the worked example.

### In the console

1. Open **Cloud Security → Settings → Providers**. Click **+ Add provider**.
2. Give the connection a **name**. Select the **provider type**. Fill the
   connection fields for that type (for GCP, the scope — a project, folder,
   or organization).
3. Supply the **credential**. Reference an existing
   [secret](../7-administration/config-hive/secrets.md) with
   `hive://secret/<name>`, or paste the credential and let the web app store
   it as a new secret. Credentials are always stored as a secret and
   referenced — never inlined into the provider record.
4. Click **Test Provider** to run the read-only preflight (see below). Save
   the connection. A save of an enabled connection starts collection.

The provider row then shows its sync status, resource count, and the actions
for that row (**What you get**, **Sync now**, **Edit**, **Delete**).

### As code

The credential is in the secret Hive. The provider record references it:

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

[Configuration](configuration.md#cloudsec_provider) has the full field
reference. [Connecting Providers](providers.md) has the scope fields and
credential shape of every provider.
[Provider Setup](provider-setup/index.md) has a full onboarding walkthrough
for **every** supported platform — exact scopes, how to create the credential
in that platform, credential-secret formats, and first-run troubleshooting.

!!! tip "internal_domains matters for CIEM"
    List every email domain your own people use. A human identity whose domain
    is not in the internal set is classified *external*, and external access to
    sensitive resources is one of the highest-signal finding classes. The
    collector discovers the primary cloud-org domain itself. You must declare
    secondary domains.

### Test the credential before saving

The provider test connects with the supplied credential and probes every
permission surface that a sweep needs. It stores nothing. It is the same check
that the **Test Provider** button in the web app runs:

```bash
limacharlie cloudsec provider test --input-file provider.json
```

The response is a report for each check: each check carries `id`, `name`,
`required`, `ok`, and a human-readable `detail`. `report.ok` is the verdict
over the *required* checks only. A failed optional check means that the
surface degrades (for example, one inventory type is missing); the connection
does not fail.

!!! info "Permissions"
    The provider test needs `cloudsec.set` — a test of a credential is as
    sensitive as a save of one. For the test, and only for the test, you can
    pass the credential inline instead of as a `hive://secret/` reference. The
    test uses it ephemerally and never stores or logs it.

## 3. Watch the first sweep

A save of an enabled provider record starts collection. Check progress:

```bash
limacharlie cloudsec scan-status --provider gcp
```

The status shows if a sweep is in progress, when the last sweep started and
completed, the diff stats of the last run, and any error. To force an
immediate re-enumeration later, change the `sync_now` value of the record (any
new value triggers a sweep), or use **Sync now** on the provider row.
`refresh` sets the periodic cadence.

## 4. Declare what matters

By default, **nothing is classified sensitive**. You declare sensitivity with
a `classification`-typed `cloudsec_policy` record (your crown jewels). Rules
match resources by account, name, resource type, label, or tag, and assign
classes:

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
    You can declare crown jewels by name or label. You can also add
    `content_class` rules, so that a data store where the agentless scanner
    samples sensitive content (`pii`, `pci`, `phi`, `financial`) counts as
    sensitive. Detected content classes always appear as facts on a resource.
    A `content_class` rule turns a detection into a sensitivity claim. See
    [Configuration](configuration.md#classification-crown-jewels). (These
    explicit, previewable rules replace the former `auto_classify` boolean.)

In the web app, you author the same policy on **Cloud Security → Policies →
Data classification**. A live **Simulate** panel shows which resources a rule
matches before you save it.

## 5. Look at the result

In the web app, the **Overview** page is the summary risk layer and **Risks**
is the worklist. From the CLI:

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
[Automation & IaC](automation.md) to connect findings to Cases and to onboard
more tenants as code.
