# Auth0

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Collects the Auth0 tenant as identity posture: the user directory (with MFA
state), roles and role membership, and applications with their machine (M2M)
identities. It also collects client grants as entitlement edges, APIs (resource
servers), and inbound connections and identity providers. Tenant-level posture
includes MFA policy, attack protection, and session lifetimes.

**Auth model:** a **Machine-to-Machine application** that is authorized against
the **Auth0 Management API** with read-only scopes and uses client credentials.

## Prerequisites

- Auth0 tenant admin access.
- Your **canonical tenant domain**, e.g. `example.us.auth0.com` (or the legacy
  `example.auth0.com`).

!!! danger "Custom domains are not usable"
    Use the **canonical** `*.auth0.com` domain as the Management API audience.
    A custom domain (`login.example.com`) is rejected. Find the tenant domain
    in **Settings → Custom Domains → your Auth0 domain**, or in the
    application's *Domain* field.

## Required scopes

Authorize these on the M2M application against the **Auth0 Management API**:

| Scope | Why | Preflight check |
|---|---|---|
| `read:users` | The user directory (identity nodes) | `read:users` |
| `read:clients` | Applications and machine (NHI) identities | `read:clients` |
| `read:connections` | Inbound identity-provider / social-trust posture | `read:connections` |
| `read:roles` | Roles and role membership | `read:roles` |

## Optional scopes

| Scope | Unlocks | Preflight check |
|---|---|---|
| `read:client_grants` | Machine-identity entitlement edges (which API each M2M app can call) | `read:client_grants` |
| `read:resource_servers` | The API (resource-server) inventory | `read:resource_servers` |
| `read:tenant_settings` | Tenant session-lifetime posture | `read:tenant_settings` |
| `read:attack_protection` | Breached-password / brute-force / suspicious-IP posture | `read:attack_protection` |
| `read:guardian_factors` | MFA factor posture | `read:guardian_factors` |
| `read:mfa_policies` | Org MFA-required posture | `read:mfa_policies` |

!!! info "Secret-bearing scopes are deliberately never requested"
    Do **not** grant `read:client_keys`, `read:client_credentials`, or
    `read:connections_options`. These scopes return client secrets and
    connection secrets. The collector never asks for them, so it never fetches
    secret material.

## Create the M2M application

1. Open **Auth0 Dashboard → Applications → Applications → Create
   Application**.
2. Choose **Machine to Machine Applications**, then click **Create**.
3. Select the **Auth0 Management API** as the API to authorize.
4. In the scope picker, select the four required scopes and any optional ones.
   Filter on `read:` and pick them one at a time. Do **not** select all.
5. Click **Create**.
6. Copy the **Client ID** and **Client Secret** from the application's
   *Settings* tab.

To change the scopes later, open the **Machine to Machine Applications** tab
under **Applications → APIs → Auth0 Management API**. Expand your application,
change the checkboxes, and click **Update**.

!!! danger "Do not use the API Explorer's test-application button"
    Create the application from the Applications page and pick the scopes
    explicitly. The Management API's **API Explorer** tab offers *Create &
    Authorize a Test Application*. That shortcut grants the application
    **every** Management API scope, including the write and secret-bearing
    scopes that this connector avoids.

## Create the credentials secret

```json
{"client_id": "<m2m-client-id>", "client_secret": "<m2m-client-secret>"}
```

```bash
limacharlie hive set --hive-name secret --key auth0-m2m \
    --input-file auth0-secret.json --enabled
```

## Create the provider record

`provider.yaml`:

```yaml
provider_type: auth0
auth0_domain: "example.us.auth0.com"
credentials: hive://secret/auth0-m2m
internal_domains: [example.com]
refresh: 6h
```

In the web app: **Add provider → Auth0**, then set **Tenant domain**,
**Credentials**, and **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

The report contains one check for each scope, named `Scope read:<name>`, plus:

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The client credentials were rejected, or the domain is wrong. No token could be minted. |
| `reachability` | ✅ | A token was minted, but the Management API is not reachable or not usable. |
| `read:users` | ✅ | The user directory cannot be enumerated. |
| `read:clients` | ✅ | Applications and machine identities cannot be enumerated. |
| `read:connections` | ✅ | Inbound identity-provider posture unavailable. |
| `read:roles` | ✅ | Roles and role membership cannot be enumerated. |
| `read:client_grants` | — | Entitlement edges unavailable. |
| `read:resource_servers` | — | API inventory unavailable. |
| `read:tenant_settings` | — | Session-lifetime posture unavailable. |
| `read:attack_protection` | — | Attack-protection posture unavailable. |
| `read:guardian_factors` | — | MFA factor posture unavailable. |
| `read:mfa_policies` | — | Org MFA-required posture unavailable. |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails: `access_denied` / `unauthorized_client` | The application is not authorized on the **Auth0 Management API** | Authorize it under *APIs → Auth0 Management API → Machine to Machine Applications* |
| `auth` fails: `service not found` | Wrong domain — usually a custom domain, or a missing region segment (`example.us.auth0.com`) | Use the canonical tenant domain |
| A scope check fails but `auth` passes | That scope is not selected on the M2M authorization | Add it in the scope picker and click **Update** |
| Sweeps are slow on a free tenant | Free Auth0 tenants are rate-limited to about 2 requests/second tenant-wide | Expected. The collector paces itself. Raise `refresh` if necessary |
| Large directories | The Management API caps the `/users` results for each query. The collector segments the directory by creation time to read past the cap | No action needed. A segment that it cannot split is reported as an error, not truncated silently |
