# OpenAI

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

This connector collects your OpenAI platform organization as a surface for AI
security. It collects projects, members, service accounts, and API keys. The API
keys include the time of last use, which shows you the keys that are dormant or
have too many permissions. The connector also collects the Admin API keys of the
organization, the mTLS certificates, and the availability of the audit log.

**Auth model:** an **Admin API key** with the read-only `api.management.read`
scope. The connector uses the key with the OpenAI Administration API.

## Prerequisites

- **Organization Owner** on the OpenAI platform account. Only an owner can
  create an Admin API key.

## Create the Admin API key

1. Go to **platform.openai.com → Settings → Organization → Admin keys**
   (`https://platform.openai.com/settings/organization/admin-keys`).
2. Click **Create admin key**.
3. **Select the `api.management.read` scope at creation time.**
4. Copy the key (`sk-admin-…`) — it is displayed once.

!!! danger "Scope the key when you create it"
    Select `api.management.read` **when you create the key**. A key whose scopes
    you change later can continue to fail with *"Missing scopes:
    api.management.read"*. If a key fails, delete it. Then create a new key and
    select the scope at creation.

!!! tip "Read-only by design"
    `api.management.read` is a read-only scope. The collector does not write to
    your organization. It only lists projects, users, keys, certificates, and the
    availability of the audit log.

## Optional: enable audit logging

The audit log of the organization is a separate setting in the OpenAI
organization settings. The connection does not need it. But without the audit
log, you have no forensic record of changes to the configuration. The
`audit_logs` check reports this condition.

## Create the credentials secret

```json
{"admin_api_key": "sk-admin-..."}
```

You can also paste the key string alone. LimaCharlie then puts the key into
this shape for you.

```bash
limacharlie hive set --hive-name secret --key openai-admin-key \
    --input-file openai-secret.json --enabled
```

## Create the provider record

`provider.yaml`:

```yaml
provider_type: openai
credentials: hive://secret/openai-admin-key
internal_domains: [example.com]
refresh: 6h
```

`openai_org_id` (`org-…`) is **optional**. The Admin key already identifies its
organization, and the collector finds that organization. If you set
`openai_org_id`, the collector checks the value. A value that does not match
makes the connection fail immediately, instead of a sweep of the wrong
organization. Set this value when one team manages more than one OpenAI
organization.

In the web app, click **Add provider → OpenAI**. Then set **Credentials** and
**Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | OpenAI rejected the Admin key, or the key does not have `api.management.read`. The collector does not do the other checks. |
| `projects` | ✅ | OpenAI denied the list of projects. The sweep then has no accounts to examine. |
| `project_keys` | ✅ | OpenAI denied the inventory of API keys for each project. You then get no report on dormant keys or keys with too many permissions. This check passes with a note if the organization has no projects. |
| `admin_keys` | — | No report on the Admin API keys of the organization, such as dormant keys and keys that do not expire. |
| `certificates` | — | No report on the mTLS certificates. This check passes with a note if the organization uses no certificates. |
| `audit_logs` | — | No report on the availability of the audit log. This check passes with a note if audit logging is not enabled. |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails: *Missing scopes: api.management.read* | You created the key without the scope, or you added the scope later | Create a **new** Admin key and select the scope at creation |
| `auth` fails: 401 | The key is not an Admin key (you used a project key `sk-…`), or the key is revoked | As an Organization Owner, create an Admin key (`sk-admin-…`) |
| The connection fails because the organization does not match | `openai_org_id` is not the organization of the key | Correct `openai_org_id`, or remove it |
| The inventory of keys is empty | The organization has no projects, or the keys are in projects that the key cannot read | Check that projects exist in **Settings → Organization → Projects** |

## Known limitations

The Administration API does not give access to the settings for MFA and SSO
enforcement, IP allow-lists, and the connector registry. These settings are
available only in the console, so the connector does not collect them. Data-plane
objects, such as vector stores, files, and assistants, need a separate credential
for each project. They are not part of this connector.
