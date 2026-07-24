# LimaCharlie

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Inventories your **own LimaCharlie tenancy** as an estate, like any other SaaS
platform: org members as identities (with MFA state), API keys as machine
identities, sensors as assets, installation keys, telemetry outputs, extension
subscriptions, and configuration stores. Posture findings cover org MFA
enforcement, unrestricted privileged API keys, insecure telemetry-output
transports, stale enrollment keys, and non-expiring secrets.

**Auth model:** a LimaCharlie **API key** — either an **org** key (one
organization) or a **user** key (every organization that user can reach, which
is the MSSP fleet case).

## Choose a key mode

| Mode | Record field | Enumerates | Use when |
|---|---|---|---|
| **Org key** | `limacharlie_oid` | That one organization | You want a single tenant inventoried |
| **User key** | `limacharlie_uid` | Every organization the user can reach, one account each | You run a fleet and want them all in one connection |

Org-level MFA/SSO enforcement posture is observable **only in user-key mode** —
the underlying endpoint rejects org identities.

## Required permissions

Set these on the API key. Each maps to a preflight check of the same name.

| Permission | Gives | Preflight check |
|---|---|---|
| `org.get` | The Account node and org info | `org` |
| `sensor.list` | Sensors as assets, and enrollment-key usage | `sensors` |
| `user.ctrl` | Org members as identities, with MFA state | `users` |
| `apikey.ctrl` | API keys as machine identities | `api_keys` |
| `ikey.list` | Installation/enrollment key posture | `ikeys` |
| `output.list` | Telemetry-output posture | `outputs` |

!!! warning "`user.ctrl` and `apikey.ctrl` are broader than read-only"
    LimaCharlie has no read-only permission for users or API keys, so these two
    are the narrowest permissions that expose the data. The collector uses them
    strictly for listing. If that is not acceptable, omit them and accept that
    org members and API keys are not inventoried — but note both checks are
    marked **required**, so `provider test` will report the connection as not
    OK.

## Optional permissions

| Permission | Unlocks | Preflight check |
|---|---|---|
| `ext.conf.get` | Extension subscriptions as applications | `extensions` |
| `replicant.get` | Extension configuration detail | `replicant` |
| `billing.ctrl` | Org-level MFA/SSO enforcement posture *(user-key mode only)* | `billing` |
| `secret.get.mtd` | The secret config store + non-expiring-secret findings | `secret_mtd` |
| `lookup.get.mtd` | The lookup config store | `lookup_mtd` |
| `yara.get.mtd` | The YARA config store | `yara_mtd` |
| `query.get.mtd` | The query config store | `query_mtd` |
| `playbook.get.mtd` | The playbook config store | `playbook_mtd` |

All `*.get.mtd` permissions read **metadata only** — record names and
attributes, never secret values or rule bodies.

## Create the API key

See [API Keys](../../7-administration/access/api-keys.md) for the full
reference; both key types are managed from the organization view of the web
interface.

### Org key

1. Open the organization's **REST API** section.
2. Create a new API key, name it (e.g. `cloudsec-collector`), and select the
   permissions above.
3. Copy the key value.
4. Note the **organization ID** (a lowercase UUID) — `limacharlie org list`
   maps org names to IDs.

### User key

1. Retrieve your **user API key** from the web interface.
2. Note your **user ID**, also shown in the web interface. It is a free-form,
   **case-sensitive** identifier, not a UUID — copy it verbatim.

!!! warning "User keys are powerful"
    A user API key carries the same access as the user across **every**
    organization they can reach. Prefer an org key unless you specifically want
    fleet-wide inventory.

## Create the credentials secret

```json
{"api_key": "<the-api-key>"}
```

A bare key string is also accepted and wrapped automatically.

```bash
limacharlie hive set --hive-name secret --key limacharlie-collector \
    --input-file lc-secret.json --enabled
```

## Create the provider record

Org-key mode:

```yaml
provider_type: limacharlie
limacharlie_oid: "00000000-0000-0000-0000-000000000000"
credentials: hive://secret/limacharlie-collector
internal_domains: [example.com]
refresh: 6h
```

User-key mode:

```yaml
provider_type: limacharlie
limacharlie_uid: "<your-user-id>"
credentials: hive://secret/limacharlie-collector
internal_domains: [example.com]
refresh: 6h
```

!!! danger "Exactly one of the two"
    Set `limacharlie_oid` **or** `limacharlie_uid`, never both and never
    neither — the pair selects the key's mode as well as the scope, so the
    record is rejected otherwise.

In the web app: **Add provider → LimaCharlie**, then choose the scope mode, set
**Credentials**, and set the **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The API key was rejected. Nothing else is probed. |
| `scope` | ✅ | The key's identity does not match the configured org/user, or cannot reach it. |
| `org`, `sensors`, `users`, `api_keys`, `ikeys`, `outputs` | ✅ | That permission is not granted — see the table above for what each one covers. |
| `extensions`, `replicant`, `billing`, `secret_mtd`, `lookup_mtd`, `yara_mtd`, `query_mtd`, `playbook_mtd` | — | That surface is unobserved; everything else still collects. |

Each permission check reports the concrete consequence in its `detail`, whether
it passes or fails.

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails | Key revoked, mistyped, or an org key used in user mode (or vice versa) | Re-copy the key; confirm the mode matches the field you set |
| `scope` fails | `limacharlie_oid` is not the org the key belongs to, or the user ID is wrong | Confirm the org UUID / user ID; the user ID is case-sensitive |
| A permission check fails after granting it | Permission changes need the key's effective permissions to refresh | Re-run the test; re-issue the key if it persists |
| `billing` fails in org-key mode | Expected — org MFA/SSO posture is only observable with a user key | Use user-key mode if you want that posture |
| Only some orgs appear in user-key mode | The user does not have the required permissions in the missing orgs | Grant the same permission set in each org you want inventoried |
