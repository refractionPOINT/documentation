# Okta

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

This connector collects the Okta directory as identity posture. It collects the
users, with their MFA factors and admin roles. It collects the groups and their
members, an inventory of the applications, and the application assignments for
each user. It also collects the external identity providers, which give federation
and social trust. The connector can also collect the condition of the API tokens
of the organization and the registry of AI agents.

**Auth model:** an Okta **API Services** app integration. The app uses OAuth 2.0
client credentials with a **private-key JWT**. An **SSWS API token** that a user
owns also works, but use the service app if you can. A service app has no owner,
no lifecycle for a password or MFA, and it does not expire after 30 days without
use.

## Prerequisites

- **Super Administrator** access to the Okta organization. You need this access
  to create an API Services app and to give the app an admin role.
- The base URL of your organization, such as `https://example.okta.com`. Use the
  URL that you sign in to. The *name* of an organization and its *subdomain* can
  be different.

## Required scopes

Grant these scopes on the **Okta API Scopes** tab of the app:

| Scope | Why | Preflight check |
|---|---|---|
| `okta.users.read` | The user directory, which is the primary inventory of identities | `users` |
| `okta.groups.read` | The groups and their members | `groups` |
| `okta.apps.read` | The inventory of the applications and their assignments | `apps` |
| `okta.roles.read` | The admin roles that the connector adds to each user | `roles` |
| `okta.idps.read` | The external identity providers, which give federation and social trust | `idps` |

!!! danger "`okta.roles.read` is not optional"
    The user collector adds the admin roles to each user as it works. If Okta
    denies the roles, the collector stops. Without this scope, the connector makes
    **no inventory of any user**. You do not get "users without roles".

The collector asks for these optional scopes only when you list them. See
[Requesting extra scopes](#requesting-extra-scopes).

| Scope | Unlocks | Preflight check |
|---|---|---|
| `okta.apiTokens.read` | The condition of the API tokens of the organization, which are permanent SSWS credentials | `api_tokens` |
| `okta.aiAgents.read` | The registry of Okta for AI Agents. The source asserts the classification of each AI agent. This scope needs the paid subscription to Okta for AI Agents | `ai_agents` |

## Create the API Services app

1. In the **Admin console**, go to **Applications → Applications → Create App
   Integration → API Services**. Give the app a name, such as `LimaCharlie Cloud
   Security`, then save it.
2. On the app's **General** tab, set **Client authentication** to
   **Public key / Private key**.
3. Under **PUBLIC KEYS**, click **Add key → Generate new key**. Then copy the
   **private key in JWK format**. Okta shows this key one time only, so keep
   it.
4. On the **Okta API Scopes** tab, **Grant** each of the five necessary scopes.
   Also grant the optional scopes that you want.
5. On the **Admin roles** tab of the app, **give the app an admin role**. The
   **Read-only Administrator** role is enough for the five necessary scopes.
6. Copy the app's **Client ID** from the General tab.

!!! danger "Scopes *and* an admin role are both required"
    An API Services app that has the scopes but **no admin role** authenticates
    correctly. It then returns 403 for the groups and for the roles of each user.
    A `.read` scope alone does not give read access to the directory.

!!! danger "Private-key JWT is mandatory"
    The **org authorization server of Okta rejects authentication with a client
    secret** for the `okta.*` scopes. It needs `private_key_jwt`. If you configure
    the app with a client secret, the request for a token fails with *"Client
    Credentials requests to the Org Authorization Server must use the
    private_key_jwt token_endpoint_auth_method"*. Use **Public key / Private
    key**.

!!! info "DPoP is handled for you"
    On a new API Services app, the switch for sender-constrained tokens
    (**DPoP**) can be on, and you cannot change it. This state is correct, and it
    needs no field in the credential. When the token endpoint needs DPoP, the
    collector finds this condition and changes to DPoP automatically.

## Create the credentials secret

**API Services app (recommended).** Paste the private JWK as a JSON object
inside the secret. You do not need to escape the string:

```json
{
  "org_url": "https://example.okta.com",
  "client_id": "<app-client-id>",
  "private_key": { "kty": "RSA", "kid": "...", "n": "...", "e": "AQAB", "d": "...", "p": "...", "q": "..." }
}
```

A PEM string also works for `private_key`. If you use a PEM string, add
`"key_id"` with the `kid` of the key.

**SSWS token (alternative)**:

```json
{"org_url": "https://example.okta.com", "api_token": "<SSWS-token>"}
```

Store it:

```bash
limacharlie hive set --hive-name secret --key okta-credentials \
    --input-file okta-secret.json --enabled
```

### Requesting extra scopes

By default, the collector asks for the five necessary scopes only. To use an
optional scope, grant the scope on the app **and** list the full set of scopes in
the secret:

```json
{
  "org_url": "https://example.okta.com",
  "client_id": "<app-client-id>",
  "private_key": { "...": "..." },
  "scopes": ["okta.users.read", "okta.roles.read", "okta.groups.read",
             "okta.apps.read", "okta.idps.read", "okta.apiTokens.read"]
}
```

!!! warning "`scopes` replaces the default set"
    The collector uses your list exactly. You **must grant each scope in the
    list on the app**, or the request for a token fails. Always put the five
    necessary scopes in the list with the optional scopes.

## Create the provider record

`provider.yaml`:

```yaml
provider_type: okta
okta_org_url: "https://example.okta.com"
credentials: hive://secret/okta-credentials
internal_domains: [example.com]
refresh: 6h
```

In the web app, click **Add provider → Okta**. Then set **Org URL**,
**Credentials**, and **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | Okta rejected the credential. The key, the client ID, or the org URL is not correct. The collector does not do the other checks. |
| `users` | ✅ | Okta denied `okta.users.read`. You get no inventory of identities. |
| `groups` | ✅ | Okta denied `okta.groups.read`. The graph gets no groups and no membership edges. |
| `apps` | ✅ | Okta denied `okta.apps.read`. You get no inventory of the applications, and the graph gets no app-access edges. |
| `roles` | ✅ | Okta denied `okta.roles.read`. The connector makes **no inventory of any user**, because the user collector stops when it cannot read the roles. |
| `idps` | — | No posture for the external identity providers. |
| `api_tokens` | — | No report on the condition of the API tokens of each user. |
| `ai_agents` | — | No classification of the AI agents from the source. This check needs Okta for AI Agents and the `okta.aiAgents.read` scope. |

!!! info "401 vs 403"
    A **401** means that Okta rejected the credential. The report then shows one
    failed `auth` check only. A **403** means that you authenticated, but you do
    not have that scope or that admin permission. The `auth` check then passes,
    and only that one surface fails.

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails: *must use the private_key_jwt token_endpoint_auth_method* | You configured the app with a client secret | Change the app to **Public key / Private key**, then store the private JWK |
| `groups` or `roles` returns 403 but `auth` passes | The app has no admin role | Give the app the **Read-only Administrator** role on its *Admin roles* tab |
| A scope that you granted continues to return 403 | The org authorization server **removes a scope that you did not grant** when it makes the token, and gives no message. The token then does not have the scope | Check the *Okta API Scopes* tab again. The `WWW-Authenticate` header of the 403 response names the scope that is absent |
| The request for a token fails after you add `scopes` | The app does not have one of the scopes in your list | Grant that scope, or remove it from the list |
| `auth` fails because the host is unreachable | The subdomain is not correct, because the *name* of the organization is not its *subdomain* | Use the exact URL that you sign in to |
| The SSWS token stops to work | An SSWS token expires after 30 days without use, and it also stops when its owner is removed | Change to an API Services app |
