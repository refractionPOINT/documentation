# Anthropic

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Collects your Anthropic organization as an AI-security surface: the member
directory, workspaces, and API keys from the Console plane, plus — for Claude
Enterprise organizations — enforced security settings and a per-key/per-user
activity feed that powers dormancy findings.

**Auth model:** two independent credential planes, **either of which can stand
alone**:

| Plane | Credential | Gives |
|---|---|---|
| **Console Admin API** | Admin key `sk-ant-admin01-…` | Members, workspaces, API keys |
| **Enterprise Compliance API** | Compliance key `sk-ant-api01-…` with read-only scopes | Enforced-settings posture, activity feed (last-used per key/user) |

Connect one or both. Findings degrade gracefully to whatever plane is
connected.

## Prerequisites

- For the Console plane: the **admin** role in the Anthropic Console
  organization.
- For the Compliance plane: a **Claude Enterprise** organization (the
  Compliance API is not available on Team or Pro plans) and your
  **organization UUID**.

## Create the Console Admin key

1. Open **console.anthropic.com → Organization settings → Admin keys**
   (`https://console.anthropic.com/settings/admin-keys`).
2. Click **Create admin key** and copy the value (`sk-ant-admin01-…`) — it is
   shown once.

!!! warning "Admin keys are not scopeable"
    Anthropic Console Admin keys carry no scopes — every Admin key is full
    read/write on the organization. The collector uses it **strictly
    read-only** and stores it only as a secret reference, but there is no
    narrower key to issue. If that is not acceptable, connect the Compliance
    plane alone.

## Create the Compliance key (Claude Enterprise)

Request a Compliance API key from your Anthropic account contact with these
read-only scopes:

| Scope | Unlocks |
|---|---|
| `read:compliance_org_data` | Enforced organization security settings |
| `read:compliance_activities` | The activity feed — per-key and per-user last-used, which drives dormancy findings |
| `read:analytics` | Usage analytics |

You will also need the **organization UUID** (8-4-4-4-12 hex), which addresses
the Compliance API.

## Create the credentials secret(s)

**Console plane** — `anthropic-admin`:

```json
{"admin_api_key": "sk-ant-admin01-..."}
```

**Compliance plane** — a *separate* secret, `anthropic-compliance`:

```json
{"compliance_api_key": "sk-ant-api01-..."}
```

Bare key strings are accepted for both and wrapped into these shapes
automatically. Keep the two in separate secrets — the provider record
references them independently and they are merged at runtime.

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
| `anthropic_org_uuid` | Optional when the Console key is present (it is discovered). **Required** for a Compliance-only connection — the Compliance API is addressed by org UUID. |
| `credentials` | The Console Admin key secret. May be omitted **only** when `compliance_credentials` is set. |
| `compliance_credentials` | The Compliance key secret. Only valid for `provider_type: anthropic`. |

In the web app: **Add provider → Anthropic**, then supply either or both
credentials plus the **Organization UUID** where required.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | Neither plane's key authenticated. |
| `directory` | ✅ *(Console)* | Member directory unreadable. |
| `workspaces` | ✅ *(Console)* | Workspace inventory unreadable. |
| `api_keys` | ✅ *(Console)* | API-key inventory unreadable. |
| `compliance_settings` | ✅ only when Compliance is the **sole** plane | Enforced organization security-settings posture unavailable. |
| `activity_feed` | — | Per-key/per-user last-used (dormancy) unavailable. |
| `console` | — | Informational: reports that the Console plane is not configured and what that costs. |
| `compliance` | — | Informational: reports that the Compliance plane is not configured and what that costs. |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails on the Console key | A workspace key (`sk-ant-api01-…`) was used as the Admin key | Create an Admin key (`sk-ant-admin01-…`) under *Organization settings → Admin keys* |
| Compliance checks fail with 401/403 | The key lacks a required scope, or the org is not on Claude Enterprise | Confirm the scopes above with your Anthropic contact |
| *"anthropic_org_uuid is required"* | Compliance-only connection with no org UUID | Set `anthropic_org_uuid` |
| Dormancy findings never appear | The activity feed is unavailable, or covers only part of the window | Connect the Compliance plane. A partial feed never asserts "unused" — absence of data is treated as unknown, not as dormant |

## Optional: workload identity federation inventory

The Console secret may additionally carry an `org_oauth_token` — an
`org:admin`-scoped OAuth bearer token that unlocks the workload identity
federation admin plane (service accounts, federation issuers and rules), which
Admin API keys cannot reach:

```json
{"admin_api_key": "sk-ant-admin01-...", "org_oauth_token": "..."}
```

These tokens are short-lived by design. Organizations that want this surface
keep it live by refreshing the secret from their own automation; an expired
token degrades the federation inventory to last-known values rather than
failing the sweep.
