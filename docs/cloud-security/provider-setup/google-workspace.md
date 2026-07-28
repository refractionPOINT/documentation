# Google Workspace

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

This connector collects the identity posture from Google Workspace with the
Admin SDK API and the Cloud Identity API. It collects the users, the groups and
their members, the admin roles, the security posture of each user, the devices,
and the profiles for inbound SSO.

**Auth model:** a **Google Cloud service account** with **domain-wide delegation
(DWD)**. The service account impersonates a Workspace super admin to read the
directory data.

## Prerequisites

1. A GCP **service account** with a JSON key. Create a new service account, or
   use the service account of your GCP collector.
2. In that service account's GCP project, **enable**:
    - **Admin SDK API** (`admin.googleapis.com`)
    - **Cloud Identity API** (`cloudidentity.googleapis.com`). This API is
      necessary for the inbound-SSO profiles and the Cloud Identity devices.
3. An actual **Workspace Super Admin** account to impersonate, such as
   `admin@example.com`.

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

Copy this block into the field for the DWD scopes. It is one line, and commas separate the scopes:

```text
https://www.googleapis.com/auth/admin.directory.user.readonly,https://www.googleapis.com/auth/admin.directory.group.readonly,https://www.googleapis.com/auth/admin.directory.group.member.readonly,https://www.googleapis.com/auth/admin.directory.user.security,https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly,https://www.googleapis.com/auth/cloud-identity.inboundsso.readonly,https://www.googleapis.com/auth/admin.directory.device.mobile.readonly,https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly,https://www.googleapis.com/auth/cloud-identity.devices.readonly
```

## Register domain-wide delegation

In the **Google Admin console**, go to **Security → Access and data control →
API controls → Manage Domain-Wide Delegation → Add new**. Then give these
values:

- **Client ID**: the **numeric OAuth client ID** of the service account. Take
  this value from the `client_id` field of the JSON key. You can also find it in
  the GCP Console at **IAM & Admin → Service Accounts →** the service account
  **→ *Unique ID***.
- **OAuth scopes**: the full list above, with commas between the scopes.

!!! warning "Register the entire scope list, exactly"
    Two behaviors of Google cause problems here:

    - **Google gives all the scopes or none of them.** When LimaCharlie asks for
      a token, Google rejects the **full** request if the client does not have
      authorization for *any one* of the scopes. If you register only
      `admin.directory.user.readonly`, the request still fails, because other
      surfaces ask for more scopes.
    - **Google matches the scope string exactly.** The larger
      `…/admin.directory.user` scope does **not** satisfy the smaller
      `…/admin.directory.user.readonly` scope. Make no spelling errors, and put
      no spaces at the end.
    - A change to DWD can need about 10 minutes to propagate, and sometimes as
      much as 24 hours.

## Create the credentials secret

The provider record for Workspace has **no field for the admin to
impersonate**. That value is **inside the secret**. The secret is a **wrapper**
around the key of the service account:

```json
{
  "service_account_json": { "type": "service_account", "project_id": "...", "private_key": "...", "client_email": "...", "...": "..." },
  "admin_email": "admin@example.com",
  "domain": "example.com"
}
```

- `service_account_json`: the **full JSON key of the Google service account**,
  as the value of this key.
- `admin_email`: the Super Admin to impersonate.
- `domain`: your primary Workspace domain.

!!! danger "Do not flatten the wrapper"
    Do **not** put `admin_email` and `domain` at the top level with the fields
    of the service-account key. LimaCharlie then reads the key but finds no admin
    to impersonate. It makes a token with no subject, and Google returns
    **`HTTP 400: Invalid Input`** on the first call to the directory.

Store it:

```bash
limacharlie hive set --hive-name secret --key gw-credentials \
    --input-file gw-secret.json
```

You can also do this in the web app. Go to **Organization Settings → Secrets
Manager → Add**. Give the secret the name `gw-credentials`, then paste the
JSON.

## Create the provider record

`provider.yaml`:

```yaml
provider_type: google_workspace
workspace_customer_id: my_customer          # or an explicit customer ID
credentials: hive://secret/gw-credentials
internal_domains: [example.com]
```

In the web app, click **Add provider → Google Workspace**. Then set **Customer
ID** (`my_customer`), **Credentials** (`gw-credentials`), and **Refresh
interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `core` | ✅ | This check authenticates the service account and reads the directory users. If it fails, the delegation is not correct, and the other checks give no useful result. |
| `groups` | ✅ | No groups and no members. The graph then has no group edges, which are necessary to complete the view of GCP IAM. |
| `security` | — | No security posture for each user, such as the enrolment in 2SV and the enforcement of 2SV. |
| `roles` | — | No assignments of admin roles. |
| `sso` | — | No posture for the inbound-SSO profiles. |
| `devices_mobile` | — | No inventory of the mobile devices. |
| `devices_chromeos` | — | No inventory of the ChromeOS devices. |
| `devices_ci` | — | No inventory of the Cloud Identity devices. |

## Troubleshooting

| `provider test` error | Cause | Fix |
|---|---|---|
| `HTTP 400: Invalid input` on the check of the users | The secret has no admin to impersonate, or the admin is at the wrong level. The token then has no subject, and Google cannot resolve `my_customer` | Use the **wrapper** shown above. Put the key under `service_account_json`, and put `admin_email` and `domain` beside it |
| `token mint failed (HTTP 401): scope not granted to the delegated admin` | DWD does not have all the scopes, or a scope is not the `.readonly` form, or the change did not propagate | Register the **full** list of scopes exactly. Wait for the change to propagate. Check that the client ID of the service account is correct |
| `HTTP 403: … API has not been used in project …` | The Admin SDK API or the Cloud Identity API is not enabled | Enable the API that the message names, in the project of the service account |
