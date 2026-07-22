# Provider Setup

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

[Getting Started](getting-started.md) walks the end-to-end flow with a GCP
example. This page is the per-provider companion: the **exact scopes /
permissions** each provider needs, the **credential-secret format** for each,
and the **first-run failures** and how to fix them.

It assumes the organization is already subscribed to the `ext-cloud-security`
extension (step 1 of [Getting Started](getting-started.md#1-enable-cloud-security)).

## The common model

Every provider connection is **two Hive records**:

| Piece | Hive | Holds |
|---|---|---|
| **Provider record** | `cloudsec_provider` | Non-secret config (scope, account/subscription IDs, regions) plus a **reference** to the credential. |
| **Credential secret** | `secret` | The actual credential (key/token). Referenced from the provider record as `hive://secret/<name>` — **never inlined**. |

The full field reference for the provider record is in
[Configuration](configuration.md#cloudsec_provider).

!!! tip "Always preflight before saving"
    `provider test` connects with the credential *ephemerally* (it is never
    stored) and probes every permission surface a sweep needs:

    ```bash
    limacharlie cloudsec provider test --input-file provider.yaml
    ```

    `report.ok` is the verdict over the **required** checks. A failed
    **optional** check just means that surface is gracefully degraded (e.g. a
    data source you did not grant), not a setup failure.

Once a record passes preflight, save it:

```bash
limacharlie hive set --hive-name cloudsec_provider --key <name> \
    --input-file provider.yaml --enabled
```

!!! note "In the web app"
    Everything below can also be done in the LimaCharlie web app under
    **Cloud Security → Providers → Add provider**, with secrets managed under
    **Organization Settings → Secrets Manager**.

---

## Google Workspace

Collects identity posture from Google Workspace — users, groups and
membership, admin roles, user security posture, devices, and inbound-SSO
profiles — via the Admin SDK and Cloud Identity APIs.

**Auth model:** a **Google Cloud service account** with **domain-wide
delegation (DWD)** that **impersonates a Workspace super admin** to read
directory data.

### Prerequisites

1. A GCP **service account** with a JSON key (a dedicated one, or reuse your
   GCP collector service account).
2. In that service account's GCP project, **enable**:
    - **Admin SDK API** (`admin.googleapis.com`)
    - **Cloud Identity API** (`cloudidentity.googleapis.com`) — needed for
      inbound-SSO and Cloud Identity device surfaces.
3. A real **Workspace Super Admin** account to impersonate
   (e.g. `admin@example.com`).

### Required OAuth scopes

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

### Register domain-wide delegation

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

### Create the credentials secret

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

### Create the provider record

`provider.yaml`:

```yaml
provider_type: google_workspace
workspace_customer_id: my_customer          # or an explicit customer ID
credentials: hive://secret/gw-credentials
internal_domains: [example.com]
```

In the web app: **Add provider → Google Workspace**, then set **Customer ID**
(`my_customer`), **Credentials** (`gw-credentials`), and **Refresh interval**.

### Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

Expect `report.ok: true` with the `core` (users) and `groups` checks green.

### Troubleshooting

| `provider test` error | Cause | Fix |
|---|---|---|
| `HTTP 400: Invalid input` on the user check | Secret is missing or mis-nested the impersonation admin → token has no subject → `my_customer` unresolvable | Use the **wrapper** envelope above: nest the key under `service_account_json`, with `admin_email` / `domain` as siblings |
| `token mint failed (HTTP 401): scope not granted to the delegated admin` | DWD missing scopes (all-or-nothing mint), a non-`.readonly` variant, or not yet propagated | Register the **full** scope list exactly; wait for propagation; confirm the service account's client ID matches |
| `HTTP 403: … API has not been used in project …` | Admin SDK / Cloud Identity API not enabled | Enable the named API in the service account's project |

---

## Cloudflare

The lightest provider: a **scoped, read-only API token** plus your **account
ID**. No infrastructure to stand up.

### Create the API token

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

### Get the account ID

The 32-hex string in the dashboard's right-hand sidebar (Overview), or in the
dashboard URL.

### Create the credentials secret

```json
{"api_token": "<the-scoped-read-only-token>"}
```

```bash
limacharlie hive set --hive-name secret --key cloudflare-credentials \
    --input-file cf-secret.json
```

### Create the provider record

`provider.yaml`:

```yaml
provider_type: cloudflare
cloudflare_account_id: "<32-hex-account-id>"
credentials: hive://secret/cloudflare-credentials
```

In the web app: **Add provider → Cloudflare**, then set **Account ID**,
**Credentials**, and **Refresh interval**.

### Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

`auth` and `zones` are required; `access` / `security_center` / `r2` pass only
if you added those optional scopes. The account-members surface needs a
*user-scoped* token and is skipped gracefully otherwise.

---

## AWS

Read-only inventory via an IAM identity that **assumes a read-only role**.
Two topologies:

- **Single account** (below): one IAM user plus one role in that account.
- **AWS Organization:** deploy the same role to every account via a
  service-managed CloudFormation StackSet and set `aws_member_role_name`; the
  base user additionally needs `organizations:List*` / `Describe*`.

### Architecture (least-privilege)

An IAM **user** whose only permission is `sts:AssumeRole` on a read-only
**role** (`SecurityAudit` + `ViewOnlyAccess`), gated by an **external ID**.
LimaCharlie stores the user's access key, assumes the role, and reads. The
user itself can do nothing but assume that one role.

### Create the identity (CLI, single account)

Run as an IAM admin (never the root user):

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
EXTERNAL_ID=$(openssl rand -hex 16)          # save this

aws iam create-user --user-name lc-cloudsec

cat > trust.json <<EOF
{ "Version": "2012-10-17", "Statement": [{
  "Effect": "Allow",
  "Principal": { "AWS": "arn:aws:iam::${ACCOUNT_ID}:user/lc-cloudsec" },
  "Action": "sts:AssumeRole",
  "Condition": { "StringEquals": { "sts:ExternalId": "${EXTERNAL_ID}" } }
}] }
EOF
aws iam create-role --role-name LimaCharlieCloudSecRO \
  --assume-role-policy-document file://trust.json
aws iam attach-role-policy --role-name LimaCharlieCloudSecRO \
  --policy-arn arn:aws:iam::aws:policy/SecurityAudit
aws iam attach-role-policy --role-name LimaCharlieCloudSecRO \
  --policy-arn arn:aws:iam::aws:policy/job-function/ViewOnlyAccess

cat > assume.json <<EOF
{ "Version": "2012-10-17", "Statement": [{
  "Effect": "Allow", "Action": "sts:AssumeRole",
  "Resource": "arn:aws:iam::${ACCOUNT_ID}:role/LimaCharlieCloudSecRO"
}] }
EOF
aws iam put-user-policy --user-name lc-cloudsec \
  --policy-name lc-assume-ro --policy-document file://assume.json

aws iam create-access-key --user-name lc-cloudsec   # capture AccessKeyId + SecretAccessKey
```

!!! note "In the web app (AWS console)"
    IAM → Users → create `lc-cloudsec`; IAM → Roles → create
    `LimaCharlieCloudSecRO` (custom trust policy → the user plus the
    external-ID condition; attach `SecurityAudit` + `ViewOnlyAccess`); add an
    inline policy on the user allowing `sts:AssumeRole` on the role; then
    create an access key.

### Create the credentials secret

```json
{"access_key_id": "AKIA...", "secret_access_key": "..."}
```

!!! warning "No `aws_` prefix"
    `aws_access_key_id` / `aws_secret_access_key` are silently ignored — the
    SDK then falls back to the default credential chain and the auth check
    fails with `no EC2 IMDS role found`. Use the bare `access_key_id` /
    `secret_access_key` keys. (Optional third key: `session_token` for
    temporary credentials.)

```bash
limacharlie hive set --hive-name secret --key aws-credentials \
    --input-file aws-secret.json
```

### Create the provider record

`provider.yaml`:

```yaml
provider_type: aws
aws_role_arn: "arn:aws:iam::<ACCOUNT_ID>:role/LimaCharlieCloudSecRO"
aws_external_id: "<EXTERNAL_ID>"
credentials: hive://secret/aws-credentials
# aws_regions: [us-east-1, ...]                 # optional; omit = all enabled regions
# aws_member_role_name: LimaCharlieCloudSecRO   # ONLY for AWS Organization member accounts
```

### Verify & coverage

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

`auth`, `ec2`, `iam`, and `s3` are required. With `SecurityAudit` +
`ViewOnlyAccess`, the optional surfaces also pass — regions, Organizations,
Inspector (vulnerabilities), Secrets Manager, data stores
(RDS/DynamoDB/Redshift), and AI services (SageMaker/Bedrock) — with no extra
policies needed.

!!! note "Propagation"
    Fresh IAM keys and role trust can take a few seconds to propagate; retry
    once on a transient `AccessDenied` / `InvalidClientTokenId`.

### Troubleshooting

| `provider test` error | Cause | Fix |
|---|---|---|
| `auth` fails: `… no EC2 IMDS role found` | Secret used the wrong key names → no static creds → default chain → IMDS | Use `access_key_id` / `secret_access_key` (no `aws_` prefix) |
| `AccessDenied` on `sts:AssumeRole` | External ID mismatch, wrong trust-policy principal, or propagation | Confirm `aws_external_id` matches the trust condition; retry after a few seconds |

---

## Credential-secret quick reference

The credential secret is stored in the `secret` hive and referenced from the
provider record as `hive://secret/<name>`.

| Provider | `secret` value |
|---|---|
| **Google Workspace** | `{"service_account_json": {<raw SA key>}, "admin_email": "...", "domain": "..."}` |
| **Cloudflare** | `{"api_token": "..."}` |
| **AWS** | `{"access_key_id": "...", "secret_access_key": "..."}` *(optional `session_token`)* |

For GCP, see [Getting Started](getting-started.md#as-code).
Field-level details for every provider type — including Okta, Azure, and
1Password — are in [Configuration](configuration.md#cloudsec_provider).
