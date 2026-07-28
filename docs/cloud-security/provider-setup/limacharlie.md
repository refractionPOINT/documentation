# LimaCharlie

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

This connector makes an inventory of your **own LimaCharlie tenancy**, in the
same way as any other SaaS platform. It collects the members of the organization
as identities, with their MFA state. It collects the API keys as machine
identities and the sensors as assets. It also collects the installation keys, the
telemetry outputs, the extension subscriptions, and the configuration stores. The
posture findings cover the enforcement of MFA in the organization, privileged API
keys with no restrictions, insecure transports for telemetry outputs, stale
enrollment keys, and secrets that do not expire.

**Auth model:** a LimaCharlie **API key**. Use an **org** key for one
organization, or a **user** key for each organization that the user can reach.
The user key is the option for an MSSP fleet.

## Choose a key mode

| Mode | Record field | Enumerates | Use when |
|---|---|---|---|
| **Org key** | `limacharlie_oid` | That one organization | You want an inventory of one tenant |
| **User key** | `limacharlie_uid` | Each organization that the user can reach, with one account for each | You operate a fleet and want all of it in one connection |

The connector can see the posture for MFA and SSO enforcement at the level of
the organization **only in user-key mode**. The endpoint rejects the identity of
an organization.

## Required permissions

Set these permissions on the API key. Each permission has a preflight check with the same name.

| Permission | Gives | Preflight check |
|---|---|---|
| `org.get` | The Account node and the information about the organization | `org` |
| `sensor.list` | The sensors as assets, and the use of the enrollment keys | `sensors` |
| `user.ctrl` | The members of the organization as identities, with their MFA state | `users` |
| `apikey.ctrl` | The API keys as machine identities | `api_keys` |
| `ikey.list` | The posture of the installation keys and the enrollment keys | `ikeys` |
| `output.list` | The posture of the telemetry outputs | `outputs` |

!!! warning "`user.ctrl` and `apikey.ctrl` are broader than read-only"
    LimaCharlie has no read-only permission for users or for API keys. These two
    permissions are therefore the smallest permissions that give the data. The
    collector uses them only to list the records. If you cannot accept these
    permissions, leave them out. The connector then makes no inventory of the
    members of the organization and of the API keys. Both checks are
    **required**, so `provider test` reports that the connection is not OK.

## Optional permissions

| Permission | Unlocks | Preflight check |
|---|---|---|
| `ext.conf.get` | The extension subscriptions as applications | `extensions` |
| `replicant.get` | The details of the extension configuration | `replicant` |
| `billing.ctrl` | The posture for MFA and SSO enforcement in the organization *(user-key mode only)* | `billing` |
| `secret.get.mtd` | The secret configuration store, and the findings about secrets that do not expire | `secret_mtd` |
| `lookup.get.mtd` | The lookup configuration store | `lookup_mtd` |
| `yara.get.mtd` | The YARA configuration store | `yara_mtd` |
| `query.get.mtd` | The query configuration store | `query_mtd` |
| `playbook.get.mtd` | The playbook configuration store | `playbook_mtd` |

Each `*.get.mtd` permission reads **only the metadata**. This metadata is the
name and the attributes of a record. These permissions never read the value of a
secret or the body of a rule.

## Create the API key

[API Keys](../../7-administration/access/api-keys.md) gives the full reference.
You manage both types of key from the organization view of the web app.

### Org key

1. Open the organization's **REST API** section.
2. Create a new API key. Give it a name, such as `cloudsec-collector`. Then
   select the permissions above.
3. Copy the key value.
4. Record the **organization ID**, which is a lowercase UUID. The command
   `limacharlie org list` shows the ID for each organization name.

### User key

1. Get your **user API key** from the web app.
2. Record your **user ID**, which the web app also shows. The user ID is not a
   UUID. It is a free-form identifier, and it is **case-sensitive**, so copy it
   exactly.

!!! warning "User keys are powerful"
    A user API key has the same access as the user, in **each** organization
    that the user can reach. Use an org key, unless you want an inventory of the
    full fleet.

## Create the credentials secret

```json
{"api_key": "<the-api-key>"}
```

You can also give the key string alone. LimaCharlie then puts it into this shape for you.

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
    Set `limacharlie_oid` **or** `limacharlie_uid`. Do not set both, and do not
    leave out both. These two fields select the mode of the key and also the
    scope. LimaCharlie rejects a record that does not have exactly one of
    them.

In the web app, click **Add provider → LimaCharlie**. Then select the scope
mode, set **Credentials**, and set the **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | LimaCharlie rejected the API key. The collector does not do the other checks. |
| `scope` | ✅ | The identity of the key is not the organization or the user that you configured, or the key cannot reach it. |
| `org`, `sensors`, `users`, `api_keys`, `ikeys`, `outputs` | ✅ | The key does not have that permission. The table above shows what each permission covers. |
| `extensions`, `replicant`, `billing`, `secret_mtd`, `lookup_mtd`, `yara_mtd`, `query_mtd`, `playbook_mtd` | — | The collector does not see that surface. It continues to collect all the other data. |

Each permission check gives the exact result in its `detail` field. It does this
when the check passes and when the check fails.

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails | The key is revoked, or you typed it incorrectly. You can also have used an org key in user mode, or a user key in org mode | Copy the key again. Check that the mode agrees with the field that you set |
| `scope` fails | `limacharlie_oid` is not the organization of the key, or the user ID is not correct | Check the UUID of the organization and the user ID. The user ID is case-sensitive |
| A permission check fails after you give the permission | The effective permissions of the key must refresh first | Run the test again. If the check continues to fail, make a new key |
| `billing` fails in org-key mode | This result is correct. The connector can see the MFA and SSO posture of the organization only with a user key | Use user-key mode to get that posture |
| Only some organizations show in user-key mode | The user does not have the necessary permissions in the organizations that are absent | Give the same set of permissions in each organization that you want in the inventory |
