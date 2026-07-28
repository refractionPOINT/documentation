# Anthropic

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Collects your Anthropic organization as an AI-security surface: the member
directory, workspaces, and API keys from the Console plane. For Claude
Enterprise organizations it also collects enforced security settings and an
activity feed for each key and user, which drives dormancy findings.

**Auth model:** two independent credential planes, **either of which can stand
alone**:

| Plane | Credential | Gives |
|---|---|---|
| **Console Admin API** | Admin key `sk-ant-admin01-…` | Members, workspaces, API keys |
| **Enterprise Compliance API** | Compliance key `sk-ant-api01-…` with read-only scopes | Enforced-settings posture, activity feed (last-used per key/user) |

Connect one plane or both. Findings degrade gracefully to the plane that is
connected.

## Prerequisites

- For the Console plane: the **admin** role in the Anthropic Console
  organization.
- For the Compliance plane: a **Claude Enterprise** organization (the
  Compliance API is not available on Team or Pro plans) and your
  **organization UUID**.

!!! info "Two products, two places to create a key"
    The console where you create a key depends on the product. A key created
    in one organization cannot manage another. If your company uses both
    Claude Console and Claude Enterprise, create one key in each.

## Create the Console Admin key

1. Sign in as an organization **admin**.
2. Open **Claude Console → Settings → Admin keys**
   (`https://platform.claude.com/settings/admin-keys`).
3. Click **Create key**.
4. Give the key a name and choose a key expiration.
5. Click **Create**.
6. Copy the value (`sk-ant-admin01-…`). The full secret is shown one time.

!!! warning "Console Admin keys are not scopeable"
    Claude Console Admin keys have no selectable scopes. Every key carries
    full access to all endpoints that accept Admin API keys. The collector
    uses it **strictly read-only** and stores it only as a secret reference,
    but there is no narrower Console key to issue. If that is not acceptable,
    connect the Compliance plane alone.

## Create the Compliance key (Claude Enterprise)

1. Sign in to **claude.ai → Organization settings → API**
   (`https://claude.ai/admin-settings/api-access`).
2. Find the **Keys** section.
3. Click **+ Create key**.
4. Name the key and select the scopes below.
5. Copy the value (`sk-ant-api01-…`). It is shown one time.

The **primary owner** of the parent organization can create a key that reaches
every linked organization. An **organization owner** can create a key that
carries Compliance scopes only, restricted to their own organization.

| Scope | Unlocks |
|---|---|
| `read:compliance_org_data` | Enforced organization security settings |
| `read:compliance_activities` | The activity feed — per-key and per-user last-used, which drives dormancy findings |
| `read:analytics` | Usage analytics |

!!! tip "One scope covers it"
    Anthropic also offers `read:org_audit`. This single read-only scope covers
    the Admin API read endpoints and every Compliance API read endpoint, and
    it is intended for security-audit integrations. It is the simplest choice
    for this connector. It does **not** include the Analytics API, so add
    `read:analytics` with it if you want usage analytics.

!!! warning "Scopes are fixed at creation"
    To add a scope later, create a new key. The Compliance and Analytics APIs
    must also be **enabled for your organization** before a key that carries
    those scopes works.

You also need the **organization UUID** (8-4-4-4-12 hex), which addresses the
Compliance API.

## Create the credentials secret(s)

**Console plane** — `anthropic-admin`:

```json
{"admin_api_key": "sk-ant-admin01-..."}
```

**Compliance plane** — a *separate* secret, `anthropic-compliance`:

```json
{"compliance_api_key": "sk-ant-api01-..."}
```

Bare key strings are accepted for both, and LimaCharlie wraps them into these
shapes automatically. Keep the two in separate secrets. The provider record
references them independently, and they are merged at runtime.

```bash
limacharlie hive set --hive-name secret --key anthropic-admin \
    --input-file anthropic-admin.json --enabled
limacharlie hive set --hive-name secret --key anthropic-compliance \
    --input-file anthropic-compliance.json --enabled
```

## Create the provider record

Both planes:

```yaml
provider_type: anthropic
anthropic_org_uuid: "00000000-0000-0000-0000-000000000000"
credentials: hive://secret/anthropic-admin
compliance_credentials: hive://secret/anthropic-compliance
internal_domains: [example.com]
refresh: 6h
```

Console plane only:

```yaml
provider_type: anthropic
credentials: hive://secret/anthropic-admin
```

Compliance plane only (Enterprise organizations with no Console plane):

```yaml
provider_type: anthropic
anthropic_org_uuid: "00000000-0000-0000-0000-000000000000"
compliance_credentials: hive://secret/anthropic-compliance
```

| Field | Rule |
|---|---|
| `anthropic_org_uuid` | Optional when the Console key is present, because it is discovered. **Required** for a Compliance-only connection — the Compliance API is addressed by org UUID. |
| `credentials` | The Console Admin key secret. Omit it **only** when `compliance_credentials` is set. |
| `compliance_credentials` | The Compliance key secret. Only valid for `provider_type: anthropic`. |

In the web app: **Add provider → Anthropic**, then give one or both
credentials, plus the **Organization UUID** where it is needed.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | No key from either plane authenticated. |
| `directory` | ✅ *(Console)* | Member directory unreadable. |
| `workspaces` | ✅ *(Console)* | Workspace inventory unreadable. |
| `api_keys` | ✅ *(Console)* | API-key inventory unreadable. |
| `compliance_settings` | ✅ only when Compliance is the **sole** plane | Enforced organization security-settings posture unavailable. |
| `activity_feed` | — | Per-key/per-user last-used (dormancy) unavailable. |
| `console` | — | Informational. It reports that the Console plane is not configured, and what that costs. |
| `compliance` | — | Informational. It reports that the Compliance plane is not configured, and what that costs. |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails on the Console key | A workspace key (`sk-ant-api01-…`) was used as the Admin key | Create an Admin key (`sk-ant-admin01-…`) under *Claude Console → Settings → Admin keys* |
| Compliance checks fail with 401/403 | The key lacks a required scope, the scope set is fixed at creation, or the Compliance API is not enabled for the organization | A 403 lists the scopes that the key has and the scopes that the endpoint needs. Create a new key with the missing scope |
| *"anthropic_org_uuid is required"* | Compliance-only connection with no org UUID | Set `anthropic_org_uuid` |
| Dormancy findings never appear | The activity feed is unavailable, or covers only part of the window | Connect the Compliance plane. A partial feed never asserts "unused" — no data is treated as unknown, not as dormant |

## Optional: workload identity federation inventory

The Console secret can also carry an `org_oauth_token`. This is an
`org:admin`-scoped OAuth bearer token that opens the admin plane for workload
identity federation: service accounts, federation issuers, and rules. Admin API
keys cannot reach that plane.

```json
{"admin_api_key": "sk-ant-admin01-...", "org_oauth_token": "..."}
```

These tokens are short-lived by design. An organization that wants this surface
keeps it live by refreshing the secret from its own automation. An expired
token degrades the federation inventory to the last known values; it does not
fail the sweep.
