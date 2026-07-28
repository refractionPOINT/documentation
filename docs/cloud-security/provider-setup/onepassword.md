# 1Password

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

This connector collects the account directory of 1Password into the identity
graph. The directory contains the users, the groups, and the members of each
group. The graph joins these identities to your cloud identities and IdP
identities by email address. A **1Password Connect** server can also add an
inventory of the vaults, which are the stores for your secrets.

**Auth model:** the **SCIM bridge** of the account and its **bearer token**. Your
identity provider uses this same provisioning endpoint. The collector only reads
from it.

## Prerequisites

- **1Password Business**, with **automated provisioning** in operation. Use
  hosted provisioning or a self-hosted SCIM bridge.
- The **SCIM base URL** and its **bearer token**.
- *(Optional)* a **1Password Connect** server that runs, and a Connect token.
  These are necessary only for an inventory of the vaults.

## Get the SCIM URL and bearer token

1. As an owner or an administrator, sign in to your 1Password account on the web.
2. Open **Integrations** (the provisioning setup page).
3. Copy the **SCIM URL** and the **bearer token** that the page shows.

| Deployment | SCIM base URL |
|---|---|
| Hosted provisioning | `https://provisioning.1password.com/scim/v2` |
| Self-hosted SCIM bridge | The URL of your bridge, such as `https://scim.example.com` |

Do not put a slash at the end. Use the same URL that you configured in your
identity provider. The collector adds `/Users` and `/Groups` to this URL.
A base path that is not correct therefore makes the `scim_users` check fail
immediately.

!!! info "Why the two forms differ"
    Hosted provisioning gives SCIM at a `/scim/v2` path. A self-hosted bridge
    gives SCIM at the **root** of its own domain. The root is the address that you
    open in a browser to see the status page of the bridge. Each form is correct
    for its deployment. Copy the form that your Integrations page shows.

!!! info "This is the provisioning credential, not a new one"
    Cryptography links the bearer token and the `scimsession` file. If you make
    new credentials from the Integrations page, you must update your identity
    provider **and** this secret.

!!! tip "Read-only by construction"
    The collector sends only `GET /Users` and `GET /Groups`. The scope of the
    SCIM token is the full account, and you cannot reduce it. 1Password does not
    give a read-only token with a smaller scope.

## Optional: 1Password Connect for vault inventory

[1Password Connect](https://developer.1password.com/docs/connect/) is a
self-hosted server that you deploy with your account. Obey the Connect
documentation of 1Password to deploy the server and to make an access token. Then
put `connect_url` and `connect_token` in the secret. The collector reads only
`GET /v1/vaults`. This gives the names and the metadata of the vaults, and never
the contents of an item. If you do not configure Connect, the collector does not
inventory the vaults.

## Create the credentials secret

```json
{
  "scim_url": "https://provisioning.1password.com/scim/v2",
  "scim_token": "<bearer-token>",
  "connect_url": "https://connect.example.com",
  "connect_token": "<connect-token>"
}
```

`connect_url` and `connect_token` are optional. If you do not run Connect, leave
out both.

```bash
limacharlie hive set --hive-name secret --key onepassword-scim \
    --input-file op-secret.json --enabled
```

## Create the provider record

`provider.yaml`:

```yaml
provider_type: 1password
onepassword_scim_url: "https://provisioning.1password.com/scim/v2"
credentials: hive://secret/onepassword-scim
internal_domains: [example.com]
refresh: 6h
```

In the web app, click **Add provider → 1Password**. Then set **SCIM URL**,
**Credentials**, and **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `scim_users` | ✅ | 1Password rejected the bearer token, or the SCIM URL is not correct. This check both authenticates the token and reads the user directory. If it fails, the collector does not do the other checks. |
| `scim_groups` | ✅ | No inventory of the groups and their members. |
| `connect_vaults` | — | No inventory of the vaults, which are the stores for your secrets. This check passes with a note if you did not configure Connect. |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `scim_users` fails with 404 | The base URL does not have the `/scim/v2` path, or it has the path when it must not | Copy the SCIM URL exactly from the Integrations page |
| `scim_users` fails with 401 | The bearer token is not correct, or you made new credentials | Copy the current token from the Integrations page |
| `scim_users` cannot connect | The public internet cannot reach the SCIM bridge, or an allowlist blocks it | A self-hosted bridge must be reachable. Check the DNS records and the TLS certificate |
| `connect_vaults` fails | The Connect URL or the Connect token is not correct, or the token has no access to the vaults | Check that the Connect server runs. Also check that the token gives read access to the vaults that you want in the inventory |
