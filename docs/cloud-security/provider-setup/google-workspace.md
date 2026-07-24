# Google Workspace

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Collects identity posture from Google Workspace — users, groups and
membership, admin roles, user security posture, devices, and inbound-SSO
profiles — via the Admin SDK and Cloud Identity APIs.

**Auth model:** a **Google Cloud service account** with **domain-wide
delegation (DWD)** that **impersonates a Workspace super admin** to read
directory data.

## Prerequisites

1. A GCP **service account** with a JSON key (a dedicated one, or reuse your
   GCP collector service account).
2. In that service account's GCP project, **enable**:
    - **Admin SDK API** (`admin.googleapis.com`)
    - **Cloud Identity API** (`cloudidentity.googleapis.com`) — needed for
      inbound-SSO and Cloud Identity device surfaces.
3. A real **Workspace Super Admin** account to impersonate
   (e.g. `admin@example.com`).

## Required OAuth scopes

| Capability | Scope |
|---|---|
| Directory users (read) | `https://www.googleapis.com/auth/admin.directory.user.readonly` |
| Groups & membership | `https://www.googleapis.com/auth/admin.directory.group.readonly` |
| Group members | `https://www.googleapis.com/auth/admin.directory.group.member.readonly` |
| User security posture | `https://www.googleapis.com/auth/admin.directory.user.security` |
| Admin roles | `https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly` |
| Inbound SSO profiles | `https://www.googleapis.com/auth/cloud-identity.inboundsso.readonly` |
| Mobile devices | `https://www.googleapis.com/auth/admin.directory.device.mobile.readonly` |
| ChromeOS devices | `https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly` |
| Cloud Identity devices | `https://www.googleapis.com/auth/cloud-identity.devices.readonly` |

Copy-paste block for the DWD scopes field (one comma-separated line):

```text
https://www.googleapis.com/auth/admin.directory.user.readonly,https://www.googleapis.com/auth/admin.directory.group.readonly,https://www.googleapis.com/auth/admin.directory.group.member.readonly,https://www.googleapis.com/auth/admin.directory.user.security,https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly,https://www.googleapis.com/auth/cloud-identity.inboundsso.readonly,https://www.googleapis.com/auth/admin.directory.device.mobile.readonly,https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly,https://www.googleapis.com/auth/cloud-identity.devices.readonly
```

## Register domain-wide delegation

In the **Google Admin console** → **Security → Access and data control → API
controls → Manage Domain-Wide Delegation → Add new**:

- **Client ID** = the service account's **numeric OAuth client ID** (from the
  service-account JSON key's `client_id`, or GCP Console → IAM & Admin →
  Service Accounts → the service account → *Unique ID*).
- **OAuth scopes** = the full comma-separated list above.

!!! warning "Register the entire scope list, exactly"
    Two Google behaviors bite here:

    - **All-or-nothing token mint:** when LimaCharlie requests a token, if
      *any* requested scope is not authorized for the client, Google rejects
      the **whole** request. Registering only
      `admin.directory.user.readonly` will still fail because other surfaces
      request additional scopes.
    - **Literal string match:** the broader `…/admin.directory.user` does
      **not** satisfy the narrower `…/admin.directory.user.readonly`. No
      typos or trailing spaces.
    - DWD changes can take ~10 minutes (occasionally up to 24h) to propagate.

## Create the credentials secret

The Workspace provider record has **no field for the impersonation admin** —
it lives **inside the secret**, which is a **wrapper** around the
service-account key:

```json
{
  "service_account_json": { "type": "service_account", "project_id": "...", "private_key": "...", "client_email": "...", "...": "..." },
  "admin_email": "admin@example.com",
  "domain": "example.com"
}
```

- `service_account_json` — the **entire raw Google service-account key JSON**,
  nested as this key's value.
- `admin_email` — the Super Admin to impersonate.
- `domain` — your primary Workspace domain.

!!! danger "Do not flatten the wrapper"
    Do **not** place `admin_email` / `domain` at the top level next to the
    service-account-key fields. LimaCharlie reads the key but finds no admin
    to impersonate, mints a token with no subject, and Google returns
    **`HTTP 400: Invalid Input`** on the first directory call.

Store it:

```bash
limacharlie hive set --hive-name secret --key gw-credentials \
    --input-file gw-secret.json
```

Or in the web app: **Organization Settings → Secrets Manager → Add**, name it
`gw-credentials`, and paste the JSON.

## Create the provider record

`provider.yaml`:

```yaml
provider_type: google_workspace
workspace_customer_id: my_customer          # or an explicit customer ID
credentials: hive://secret/gw-credentials
internal_domains: [example.com]
```

In the web app: **Add provider → Google Workspace**, then set **Customer ID**
(`my_customer`), **Credentials** (`gw-credentials`), and **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `core` | ✅ | Authentication plus the directory user read. A failure here means the delegation is wrong — nothing else can be probed meaningfully. |
| `groups` | ✅ | Groups and membership unavailable — the group edges that complete the GCP IAM picture are missing. |
| `security` | — | Per-user security posture (2SV enrolment/enforcement) unavailable. |
| `roles` | — | Admin-role assignments unavailable. |
| `sso` | — | Inbound-SSO profile posture unavailable. |
| `devices_mobile` | — | Mobile device inventory unavailable. |
| `devices_chromeos` | — | ChromeOS device inventory unavailable. |
| `devices_ci` | — | Cloud Identity device inventory unavailable. |

## Troubleshooting

| `provider test` error | Cause | Fix |
|---|---|---|
| `HTTP 400: Invalid input` on the user check | Secret is missing or mis-nested the impersonation admin → token has no subject → `my_customer` unresolvable | Use the **wrapper** envelope above: nest the key under `service_account_json`, with `admin_email` / `domain` as siblings |
| `token mint failed (HTTP 401): scope not granted to the delegated admin` | DWD missing scopes (all-or-nothing mint), a non-`.readonly` variant, or not yet propagated | Register the **full** scope list exactly; wait for propagation; confirm the service account's client ID matches |
| `HTTP 403: … API has not been used in project …` | Admin SDK / Cloud Identity API not enabled | Enable the named API in the service account's project |
