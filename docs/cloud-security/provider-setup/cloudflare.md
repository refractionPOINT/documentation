# Cloudflare

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and configuration
    formats on this page can change before general availability. Contact us to
    request access.

This is the smallest provider. It needs a **scoped, read-only API token** and
your **account ID**. It needs no infrastructure.

## Create the API token

Cloudflare has two types of token, and you create them in two different
places. Use an **Account API token**. The account owns this token, not a
person, so the token stays valid when that person leaves:

**Cloudflare dashboard → Manage Account → API Tokens → Create Token → Create
Custom Token.**

!!! note "User tokens live elsewhere"
    A *user* owns each token that you create under **My Profile → API
    Tokens**. A user token with account scope also works for the surfaces
    below, but it belongs to one person. You need a user token only for the
    optional
    [account-members and API-token surfaces](#optional-account-members-and-api-tokens).

**Minimum permissions** (for the required checks: authentication plus the
zones/DNS inventory):

| Type | Permission | Access |
|---|---|---|
| Account | Account Settings | Read |
| Zone | Zone | Read |

**Optional permissions**. Each one adds one more inventory surface. Omit the
ones that you do not want:

| Surface | Add (all Account-scope, Read) |
|---|---|
| Zero Trust Access (apps, IdPs, service tokens) | Access: Apps and Policies · Access: Service Tokens · Access: Organizations, Identity Providers, and Groups |
| Security Center findings | Security Center Insights |
| R2 storage inventory | Workers R2 Storage |

Set the resource scope of the token:

- **Account Resources:** Include → your account.
- **Zone Resources:** Include → All zones.

Copy the token. Cloudflare shows it one time only. To check the token, run
this command:

```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  https://api.cloudflare.com/client/v4/user/tokens/verify
# "status":"active" confirms it is valid
```

## Get the account ID

The account ID is the 32-hex string in the right sidebar of the dashboard
(Overview). It is also in the dashboard URL.

## Create the credentials secret

```json
{"api_token": "<the-scoped-read-only-token>"}
```

```bash
limacharlie hive set --hive-name secret --key cloudflare-credentials \
    --input-file cf-secret.json
```

## Create the provider record

`provider.yaml`:

```yaml
provider_type: cloudflare
cloudflare_account_id: "<32-hex-account-id>"
credentials: hive://secret/cloudflare-credentials
```

In the web app, select **Add provider → Cloudflare**. Then set **Account ID**,
**Credentials**, and **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The token was rejected, or it cannot see the configured account. |
| `zones` | ✅ | Zone and DNS inventory unavailable. |
| `access` | — | Zero Trust Access apps, identity providers, and service tokens unavailable. |
| `security_center` | — | Security Center findings unavailable. |
| `r2` | — | R2 storage inventory unavailable. |
| `user_scoped` | — | Account members and API-token enumeration unavailable. These endpoints are user-scoped and need `user_api_token` in the secret. |

The optional checks pass only if you added the matching token permissions.

### Optional: account members and API tokens

**User-scoped** endpoints supply account membership and API-token
enumeration. An account-owned token cannot reach these endpoints. To collect
them, create a second token under **My Profile → API Tokens**, then add it to
the same secret:

```json
{"api_token": "<account-scoped-token>", "user_api_token": "<user-owned-token>"}
```

Without this second token, LimaCharlie does not collect those two surfaces.
