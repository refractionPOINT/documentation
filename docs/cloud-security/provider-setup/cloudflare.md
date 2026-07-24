# Cloudflare

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

The lightest provider: a **scoped, read-only API token** plus your **account
ID**. No infrastructure to stand up.

## Create the API token

**Cloudflare dashboard → My Profile → API Tokens → Create Token → Create
Custom Token.**

**Minimum permissions** (the required checks — authenticate plus the
zones/DNS inventory):

| Type | Permission | Access |
|---|---|---|
| Account | Account Settings | Read |
| Zone | Zone | Read |

**Optional permissions** — each lights up an additional inventory surface
(skip any you do not want):

| Surface | Add (Account · … · Read) |
|---|---|
| Zero Trust Access (apps, IdPs, service tokens) | Access: Apps and Policies · Access: Service Tokens · Access: Organizations, Identity Providers, and Groups |
| Security Center findings | Security Center |
| R2 storage inventory | Workers R2 Storage |

Scope the token's resources:

- **Account Resources:** Include → your account.
- **Zone Resources:** Include → All zones.

Copy the token (it is shown once). You can confirm it independently:

```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  https://api.cloudflare.com/client/v4/user/tokens/verify
# "status":"active" confirms it is valid
```

## Get the account ID

The 32-hex string in the dashboard's right-hand sidebar (Overview), or in the
dashboard URL.

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

In the web app: **Add provider → Cloudflare**, then set **Account ID**,
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
| `user_scoped` | — | Account members and API-token enumeration unavailable — these are user-scoped endpoints and need `user_api_token` in the secret. |

The optional checks pass only if you added the matching token permissions.

### Optional: account members and API tokens

Account membership and API-token enumeration are served by **user-scoped**
endpoints that an account-owned token cannot reach. To cover them, add a
user-owned token to the same secret:

```json
{"api_token": "<account-scoped-token>", "user_api_token": "<user-owned-token>"}
```

Without it those two surfaces are simply unobserved.
