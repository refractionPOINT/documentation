# Google Workspace

Collects identity posture from Google Workspace — users, groups and
membership, admin roles, user security posture, devices, inbound-SSO profiles,
and Gemini-in-Workspace usage — via the Admin SDK and Cloud Identity APIs.

**Auth model:** a **Google Cloud service account**, in one of two setups:

- **Domain-wide delegation (DWD)** — the service account **impersonates a
  Workspace super admin** to read directory data. This is the recommended
  setup and the rest of this page assumes it.
- **No delegation** — the service account calls the Admin SDK directly, and
  must itself hold a Workspace admin role in the Admin console. See
  [Alternative: no delegation](#alternative-no-delegation).

## Prerequisites

1. A GCP **service account** with a JSON key (a dedicated one, or reuse your
   GCP collector service account).
2. In that service account's GCP project, **enable**:
    - **Admin SDK API** (`admin.googleapis.com`)
    - **Cloud Identity API** (`cloudidentity.googleapis.com`) — needed for
      inbound-SSO and Cloud Identity device surfaces.
3. A real **Workspace Super Admin** account to impersonate
   (e.g. `admin@example.com`) — DWD setup only.

## OAuth scopes

Only the user and group scopes are required. Each remaining scope unlocks one
surface, and leaving it out degrades only that surface.

| Capability | Required | Scope |
|---|:--:|---|
| Directory users (read) | ✅ | `https://www.googleapis.com/auth/admin.directory.user.readonly` |
| Groups & membership | ✅ | `https://www.googleapis.com/auth/admin.directory.group.readonly` |
| Group members | ✅ | `https://www.googleapis.com/auth/admin.directory.group.member.readonly` |
| User security posture | — | `https://www.googleapis.com/auth/admin.directory.user.security` |
| Admin roles | — | `https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly` |
| Inbound SSO profiles | — | `https://www.googleapis.com/auth/cloud-identity.inboundsso.readonly` |
| Mobile devices | — | `https://www.googleapis.com/auth/admin.directory.device.mobile.readonly` |
| ChromeOS devices | — | `https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly` |
| Cloud Identity devices | — | `https://www.googleapis.com/auth/cloud-identity.devices.readonly` |
| Gemini-in-Workspace usage | — | `https://www.googleapis.com/auth/admin.reports.audit.readonly` |

Copy-paste block for the DWD scopes field (one comma-separated line):

```text
https://www.googleapis.com/auth/admin.directory.user.readonly,https://www.googleapis.com/auth/admin.directory.group.readonly,https://www.googleapis.com/auth/admin.directory.group.member.readonly,https://www.googleapis.com/auth/admin.directory.user.security,https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly,https://www.googleapis.com/auth/cloud-identity.inboundsso.readonly,https://www.googleapis.com/auth/admin.directory.device.mobile.readonly,https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly,https://www.googleapis.com/auth/cloud-identity.devices.readonly,https://www.googleapis.com/auth/admin.reports.audit.readonly
```

!!! info "Gemini usage has no preflight check"
    `admin.reports.audit.readonly` reads the Admin SDK **Reports** audit stream
    to land Gemini-in-Workspace usage as an application with per-user access
    edges — only the set of users seen in the trailing window, never any
    prompt or response content. It is the one surface `provider test` does not
    probe: if the scope is missing (or the Admin SDK API is not enabled) the
    connection still reports OK and Gemini usage is simply left uncollected.

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
  "admin_email": "admin@example.com"
}
```

- `service_account_json` — the **entire raw Google service-account key JSON**,
  nested as this key's value.
- `admin_email` — the Super Admin to impersonate. Omit it only for the
  no-delegation setup below.
- `domain` — **optional**, and a filter rather than a label. Most connections
  should leave it out entirely.

!!! warning "`domain` narrows what is collected"
    Setting `domain` enumerates that **one** domain instead of the whole
    customer. On a tenant with secondary or additional domains, every user and
    group outside it is silently absent from the inventory — the sweep succeeds
    and the connection looks healthy. Leave `domain` out unless you
    deliberately want a single-domain inventory.

    To declare which domains count as internal (for external-collaborator
    detection), use the provider record's `internal_domains` instead. That is a
    classification list and does not restrict collection.

!!! danger "Do not flatten the wrapper"
    Do **not** place `admin_email` / `domain` at the top level next to the
    service-account-key fields. A secret that looks like a bare service-account
    key is read as the **no-delegation** form: the impersonation admin is
    ignored, the token is minted with no subject, and Google returns
    **`HTTP 400: Invalid Input`** on the first directory call — unless the
    service account itself holds a Workspace admin role.

Store it:

```bash
limacharlie secret set --key gw-credentials \
    --value "$(cat gw-secret.json)" --enabled
```

`secret set` wraps the value into the secret record's `{"secret": "..."}`
envelope for you.

Or in the web app: **Organization Settings → Secrets Manager → Add**, name it
`gw-credentials`, and paste the JSON.

### Alternative: no delegation

If you would rather not register domain-wide delegation, the **raw
service-account key JSON** is accepted as the secret on its own — the file GCP
hands you, stored verbatim with no wrapper and no `admin_email`:

```bash
limacharlie secret set --key gw-credentials \
    --value "$(cat sa-key.json)" --enabled
```

In this form the service account calls the Admin SDK as itself instead of
impersonating an admin, so it must **hold a Workspace admin role** granted in
the Google Admin console — assign the service account a read-only or custom
admin role covering the directory surfaces you want. No DWD registration is
needed, and there is no way to set `domain`: the whole customer is enumerated.

Everything else on this page is unchanged; `provider test` reports the same
checks, and a surface the role does not cover fails exactly as an unregistered
scope would.

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
| `core` | ✅ | Authentication plus the directory user read. A failure here means the delegation (or, in the no-delegation setup, the service account's admin role) is wrong — nothing else can be probed meaningfully. |
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
| `HTTP 400: Invalid input` on the user check | Secret is missing or mis-nested the impersonation admin → token has no subject → `my_customer` unresolvable | Use the **wrapper** envelope above: nest the key under `service_account_json`, with `admin_email` as a sibling. If you meant the no-delegation setup, grant the service account a Workspace admin role instead |
| Users or groups from a secondary domain are missing | `domain` is set in the secret, narrowing collection to that one domain | Remove `domain` from the secret; declare internal domains with `internal_domains` on the record |
| `token mint failed (HTTP 401): scope not granted to the delegated admin` | DWD missing scopes (all-or-nothing mint), a non-`.readonly` variant, or not yet propagated | Register the **full** scope list exactly; wait for propagation; confirm the service account's client ID matches |
| `HTTP 403: … API has not been used in project …` | Admin SDK / Cloud Identity API not enabled | Enable the named API in the service account's project |
