# Microsoft Entra ID / Microsoft 365

!!! tip "Connecting from the web app?"
    Open **Cloud Security → Settings → Providers → Add provider → Entra ID**.
    In certificate mode (the default) the wizard generates the certificate and a
    PowerShell setup script that does the tenant side for you. See
    [Certificate mode](#certificate-mode-recommended). In client-secret mode, follow
    the [client secret](#client-secret-mode) steps below, save the credential with
    **New secret** under **Permissions**, run **Test Provider**, and save.
    [First-time setup and verification](../getting-started.md) explains the full journey.

A connection for organizations that use Entra ID or Microsoft 365. It collects the
tenant-global identity surface over Microsoft Graph: users, groups and
membership, service principals and app registrations (with their long-lived
credentials), directory roles and PIM eligibility, Conditional Access policies,
administrative units, and the tenant's **federated domains**, which are the external
identity providers (ADFS and other SAML/WS-Fed trusts) that can assert
identities into the tenant.

It also reads the Microsoft 365 tenant settings that the
[`cis-m365-v7`](../compliance.md#cis-benchmark-versions) framework grades: Entra ID
policies, Intune, the Microsoft 365 admin center, SharePoint and OneDrive,
Exchange Online, Defender for Office 365, Purview, Teams and Power BI / Fabric.
Each of these needs its own grant. A setting LimaCharlie could not read makes the
controls that depend on it report NOT_ASSESSED with a reason; it never reports
them as PASS.

There is no ARM or subscription setup.

!!! tip "Already connecting Azure?"
    The [Azure](azure.md) provider collects this same directory as part of its
    sweep. You only need a standalone Entra record when there is no Azure
    subscription to connect, when you want the directory collected independently
    of the infrastructure connection, or when you want the Microsoft 365 settings
    beyond Microsoft Graph (Exchange Online, Purview, Teams, Power BI / Fabric),
    which only an Entra connection reads. Holding **both** for one tenant is
    supported and safe: the Azure connection detects the standalone record and
    defers its tenant-global directory collectors to it, so the directory is never
    collected twice.

## Authentication modes

The connection authenticates as an **Entra ID app registration** (service
principal) in your tenant, with **application** permissions. It supports two
credential types:

| | Certificate (recommended) | Client secret |
|---|---|---|
| Who creates the credential | LimaCharlie generates a key pair and a certificate for the connection. The private key stays in your organization's LimaCharlie secret store; you upload only the public certificate. | You create a client secret on the app registration. |
| Renewal | Automatic. LimaCharlie rotates the certificate itself. | You re-create the secret before it expires. |
| Microsoft Graph reads (Entra ID, Conditional Access, Intune, Microsoft 365 admin center, SharePoint sharing settings) | Yes | Yes |
| Exchange Online, Defender for Office 365, Purview | Yes | No: those controls report NOT_ASSESSED |
| SharePoint advanced settings ([opt-in](#sharepoint-advanced-settings-opt-in)) | Yes | No: Microsoft accepts only certificate credentials for them |

Existing client-secret connections keep working unchanged. To move one to
certificate mode, edit it in the web app, switch **Authentication** to the
certificate, and follow the steps below.

## Prerequisites

- Your **tenant ID** (Entra ID → Overview).
- A tenant administrator who can grant tenant-wide admin consent and assign
  directory roles: **Global Administrator**, or **Privileged Role Administrator**
  together with **Cloud Application Administrator**.
- In LimaCharlie, generating the certificate requires the `cloudsec.set` **and**
  `secret.set` permissions, because it writes the key pair to the organization's
  secret store.
- Certificate mode's setup script runs in **PowerShell 7** with the Microsoft
  Graph PowerShell SDK. The script installs the modules it needs for the current
  user if they are missing.

## Permissions

Every grant except `Directory.Read.All` is optional. Each optional grant feeds
specific collectors or `cis-m365-v7` controls. Without it, those controls report
NOT_ASSESSED and name what is missing; nothing else stops working. The setup
script grants all of them (the SharePoint one only when you
[opt in](#sharepoint-advanced-settings-opt-in)).

### Microsoft Graph application permissions

| Permission | Required | What it reads |
|---|:--:|---|
| **Directory.Read.All** | ✅ | Users, groups, service principals and role assignments: the directory inventory. |
| **AuditLog.Read.All** | — | Sign-in activity and the MFA registration report. Without it, activity reads as unobserved and the MFA-registration control is not assessed. Sign-in activity needs Entra ID P1 or P2. |
| **Policy.Read.All** | — | Conditional Access and tenant policies (Security Defaults, consent, guest access, authentication methods, per-user MFA). |
| **Application.Read.All** | — | App registrations and service principals, their owners and credentials. |
| **RoleManagement.Read.Directory** | — | Privileged role assignments and PIM eligibility. PIM needs Entra ID P2 or Entra ID Governance. |
| **AdministrativeUnit.Read.All** | — | Administrative units. |
| **Domain.Read.All** | — | Domains: federation and password expiry settings. |
| **OnPremDirectorySynchronization.Read.All** | — | On-premises directory synchronization settings (hybrid tenants). |
| **MailboxSettings.Read** | — | Inbox rules that forward mail outside the organization. |
| **Organization.Read.All** | — | The tenant's licences, branding and organization settings; Teams also requires it. Without it, licence-dependent controls are not assessed. |
| **Policy.Read.DeviceConfiguration** | — | The device registration policy. |
| **AccessReview.Read.All** | — | Access review definitions (guest and privileged-role reviews). |
| **RoleManagementPolicy.Read.Directory** | — | PIM role settings (activation approval, duration). |
| **DeviceManagementConfiguration.Read.All** | — | Intune device compliance settings. |
| **DeviceManagementServiceConfig.Read.All** | — | Intune enrollment restrictions. |
| **OrgSettings-AppsAndServices.Read.All** | — | Microsoft 365 admin center settings for apps and services. |
| **OrgSettings-Forms.Read.All** | — | Microsoft Forms settings (phishing protection, external sharing). |
| **SharePointTenantSettings.Read.All** | — | SharePoint and OneDrive sharing settings, through Microsoft Graph. |

### Grants outside Microsoft Graph

| Grant | Certificate mode only | What it reads |
|---|:--:|---|
| **Exchange.ManageAsApp** on *Office 365 Exchange Online* (application) | ✅ | Exchange Online and Defender for Office 365 settings (mail flow, auditing, anti-phishing, Safe Links). Also needs Global Reader. |
| **Exchange.ManageAsApp** on *Microsoft Exchange Online Protection* (application) | ✅ | Microsoft Purview policies (data loss prevention, sensitivity labels, alert policies). Also needs Global Reader. |
| **Global Reader** (Microsoft Entra directory role, assigned to the app) | — | A read-only role. Exchange Online, Purview and Teams accept an app only through a directory role. |
| Fabric admin setting **Service principals can access read-only admin APIs**, enabled for a security group that contains the app | — | Power BI / Fabric tenant settings. |
| **Sites.FullControl.All** on *Office 365 SharePoint Online* (application), **opt-in** | ✅ | SharePoint advanced settings. See [below](#sharepoint-advanced-settings-opt-in). |

!!! danger "Application permissions, not delegated"
    Graph permissions must be **Application** permissions. Delegated
    permissions need a signed-in user and leave `graph_directory` failing even
    after consent.

!!! warning "Do not give the app a Power BI Service API permission"
    Fabric refuses read-only admin API calls from a service principal that also
    holds a Power BI Service API permission. The security-group setting above is
    all the Power BI / Fabric read needs.

### SharePoint advanced settings (opt-in)

Some SharePoint and OneDrive tenant settings (OneDrive sharing, default link
types, guest access expiry) are readable only through SharePoint's admin API.
Microsoft offers no read-only application permission for that API. Reading them
requires **Sites.FullControl.All**, which also allows writing to every site.
LimaCharlie only reads with it, but the grant itself is broad, so it is **off by
default**:

- **Not granted:** the 8 `cis-m365-v7` SharePoint and OneDrive controls that
  depend on these settings report NOT_ASSESSED, with a reason saying the
  SharePoint admin API was not opted in. The sharing settings Microsoft Graph
  exposes are still read with `SharePointTenantSettings.Read.All`.
- **Granted:** tick **Also read SharePoint advanced settings** in the wizard
  before you download the setup script, or grant the permission yourself. It
  works in certificate mode only.

The grant is the opt-in. LimaCharlie has no separate switch for it. To opt out
later, remove the permission from the app registration.

### Licence-gated controls

Some `cis-m365-v7` controls grade a feature that exists only with a specific
Microsoft licence (Entra ID P1 or P2, Entra ID Governance, Intune, Defender for
Office 365, Safe Documents, Customer Lockbox, Purview Communications DLP).
LimaCharlie reads the tenant's licences with `Organization.Read.All`. When the
tenant does not hold the licence a control needs, the control reports
NOT_ASSESSED with a reason naming it, for example `no licence was observed for
the feature this control grades: Microsoft Entra ID P1`. Buying the licence and
configuring the feature makes the control graded on the next sweep. See
[Compliance](../compliance.md#cis-benchmark-versions).

## Certificate mode (recommended)

### 1. Generate the certificate

In the provider wizard, set **Authentication** to **Certificate generated by
LimaCharlie** and select **Generate certificate**. LimaCharlie creates a key pair
and a self-signed certificate valid for 12 months, and stores them in the
organization's secret store as `cloudsec-m365-<connection>`. The connection's
**Credentials** field then points at `hive://secret/cloudsec-m365-<connection>`.
You receive only the public certificate (a `.cer` download) and its thumbprint.

Generating again returns the same certificate. **Replace certificate** discards
the key pair and creates a new one. The connection then stops collecting until
you upload the new certificate, so use it only when the current one expired or was
removed from the app registration.

!!! warning "Tenants that only accept certificates from a trusted CA"
    If your tenant has an application management policy that only accepts
    certificates issued by a trusted certificate authority, Microsoft refuses
    this certificate because it is self-signed. Exempt the LimaCharlie app from
    that policy, or use client-secret mode.

### 2. Run the setup script

The wizard builds a PowerShell 7 script for this connection, with the certificate
and the permission lists above filled in. Choose:

- **App registration name**: the script reuses an app with this name, or creates
  it. To use an app you already have, enter its application (client) ID instead.
- **Create a security group for Power BI / Fabric** (and its name), if you want
  the Power BI controls graded.
- **Also read SharePoint advanced settings**, if you
  [opt in](#sharepoint-advanced-settings-opt-in).

Download the script and run it signed in as a Global Administrator of the tenant
(or a Privileged Role Administrator who is also a Cloud Application
Administrator). It connects with `Connect-MgGraph`, then:

1. finds or creates the app registration and its service principal;
2. uploads the public certificate to the app, next to any credential it already
   has;
3. grants the Microsoft Graph application permissions and the two
   `Exchange.ManageAsApp` permissions, and admin-consents them (plus
   `Sites.FullControl.All` when you opted in);
4. assigns the **Global Reader** role to the app;
5. if you asked for it, creates or reuses the security group, adds the app to it,
   and prints the Fabric step below.

Every step checks before it creates, and the script removes nothing, so you can
run it again safely. A permission whose resource is not provisioned in the tenant
yet (for example, no Exchange Online licence) is skipped with a warning.

**Power BI / Fabric, one manual step.** A Fabric administrator opens the Fabric
admin portal → **Tenant settings** → **Admin API settings**, enables **Service
principals can access read-only admin APIs**, applies it to specific security
groups, and adds the group the script created. Without it, the Power BI
controls report NOT_ASSESSED.

### 3. Enter the application (client) ID

The script prints the **Application (client) ID** at the end; it is also on the
app registration's Overview page. Enter it in the wizard, run **Test Provider**,
and save. Permissions can take up to an hour to reach Exchange Online, so an
Exchange or Purview check that fails right after the script usually passes later.

### Certificate rotation

LimaCharlie rotates the certificate automatically at 75% of its lifetime. It adds
the new certificate to the app registration through Microsoft Graph, using the
current certificate to prove possession, and then removes the old one. You do not
re-run anything. The provider page shows the certificate's expiry and thumbprint,
and any rotation problem reported by the last sweep.

If a certificate does expire (for example, because it was removed from the app
registration and rotation could not recover), every Microsoft 365 control reports
NOT_ASSESSED. Select **Replace certificate** and run the setup script again to
upload the new one.

### Without the web app

The certificate comes from an API route:

```bash
curl -X POST -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
  "https://api.limacharlie.io/v1/cloudsec/$OID/providers/m365/certificate" \
  -d '{"connection": "entra-prod"}'
```

`connection` is the name of the provider record you are about to create. The
optional `client_id` records the app registration's ID, and `"replace": true`
replaces an existing certificate. The response carries `credentials` (the
`hive://secret/...` reference), `certificate` (base64 DER, the `.cer` to upload),
`certificate_pem`, `thumbprint` (SHA-1), `not_before` and `not_after`. It never
carries the private key. Upload the certificate to your app registration
(**Certificates & secrets → Certificates → Upload certificate**), grant the
permissions above, then create the record:

```yaml
provider_type: entra
entra_tenant_id: "<tenant-id>"
entra_client_id: "<application-client-id>"
entra_auth_mode: certificate
entra_cert_thumbprint: "<thumbprint from the response>"
entra_cert_not_after: "<not_after from the response>"
credentials: hive://secret/cloudsec-m365-entra-prod
internal_domains: [example.com, example.onmicrosoft.com]
refresh: 6h
```

In certificate mode, `entra_client_id` is required on the record. LimaCharlie
keeps `entra_cert_thumbprint` and `entra_cert_not_after` up to date after each
rotation.

## Client secret mode

A client secret reads Microsoft Graph only. Exchange Online,
Defender for Office 365, Purview and the SharePoint advanced settings report
NOT_ASSESSED.

### Create the app registration

=== "Web console"

    1. Sign in to the [Microsoft Entra admin center](https://entra.microsoft.com/)
       and select the directory to inspect.
    2. Open **Entra ID → App registrations → New registration**. Name the app
       `LimaCharlie Cloud Security`, select accounts in this directory only, and
       register it.
    3. From **Overview**, copy **Application (client) ID** and **Directory (tenant)
       ID**. These identify the app and the directory in LimaCharlie.
    4. Open **Certificates & secrets → Client secrets → New client secret**. Set
       an expiry per your organization's policy and copy the **Value** immediately,
       not the Secret ID. Record the expiry for future rotation.
    5. Open **API permissions → Add a permission → Microsoft Graph → Application
       permissions**. Add **Directory.Read.All** and the optional
       [Microsoft Graph permissions](#microsoft-graph-application-permissions) you
       need.
    6. Have an authorized administrator select **Grant admin consent** for the
       directory. Confirm consent is granted, then save the credential below.

    See Microsoft's [app registration guide](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app).
    No Azure subscription or subscription Reader assignment is needed for this provider.

=== "Cloud Shell / CLI"

    Use Azure Cloud Shell with Bash, or sign in to the Azure CLI with `az login`.
    Confirm the directory with `az account show`, then run:

    ```bash
    TENANT_ID=$(az account show --query tenantId -o tsv)

    APP_ID=$(az ad app create --display-name lc-entra --query appId -o tsv)
    az ad sp create --id "$APP_ID"

    az ad app credential reset --id "$APP_ID" --years 2 --append \
      --display-name lc-entra --query password -o tsv      # capture this once

    GRAPH=00000003-0000-0000-c000-000000000000
    az ad app permission add --id "$APP_ID" --api "$GRAPH" --api-permissions \
      7ab1d382-f21e-4acd-a863-ba3e13f7da61=Role   # Directory.Read.All
    az ad app permission add --id "$APP_ID" --api "$GRAPH" --api-permissions \
      b0afded3-3588-46d8-8b3d-9842eff778da=Role   # AuditLog.Read.All   (optional)
    az ad app permission add --id "$APP_ID" --api "$GRAPH" --api-permissions \
      246dd0d5-5bd0-4def-940b-0421030a5b68=Role   # Policy.Read.All     (optional)

    az ad app permission admin-consent --id "$APP_ID"
    ```

    Add the other optional Graph permissions the same way. `az ad sp show --id
    00000003-0000-0000-c000-000000000000 --query "appRoles[?value=='<permission>'].id"`
    prints a permission's ID.

!!! danger "`credential reset` clears existing secrets"
    Without `--append`, `az ad app credential reset` **removes every existing
    password and certificate** on the app before adding the new one.

### Create the credentials secret

In the LimaCharlie wizard, use **New secret** under **Permissions** to save the
following JSON with your client ID and secret value. The command below is an
alternative for CLI setup.

```json
{"client_id": "<application-client-id>", "client_secret": "<the-secret-value>"}
```

```bash
jq -Rs '{secret: .}' entra-secret.json \
  | limacharlie secret set --key entra-sp --enabled \
  && rm -f entra-secret.json
```

`jq -Rs` builds the secret record's `{"secret": "..."}` envelope without
putting the credential in process arguments. The temporary file is removed only
after a successful write.

### Create the provider record

`provider.yaml`:

```yaml
provider_type: entra
entra_tenant_id: "<tenant-id>"
entra_client_id: "<application-client-id>"
credentials: hive://secret/entra-sp
internal_domains: [example.com, example.onmicrosoft.com]
refresh: 6h
```

The client ID may be carried either on the record (`entra_client_id`) or inside
the secret (`client_id`); the record wins when both are present.

In the web app: **Add provider → Entra ID**, set **Authentication** to **Client
secret**, then set **Tenant ID**, **Client ID**, **Credentials**, and **Refresh
interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The credential was rejected: wrong client ID, a secret that expired, or a certificate not uploaded to the app registration. |
| `certificate` | ✅ (certificate mode) | The certificate expired or is not valid yet. Nothing can be read until it is replaced. It also warns when the expiry is near and rotation has not replaced it yet. |
| `client_id` | — | The secret's `client_id` differs from the record's `entra_client_id`; the record's value is used. |
| `graph_directory` | ✅ | `Directory.Read.All` not consented: no identity inventory. |
| `graph_groups` | — | Groups or their members are unreadable, so group-based role assignments resolve to nobody. |
| `graph_applications` | — | `Application.Read.All` missing: no app-registration and service-principal detail. |
| `graph_pim` | — | `RoleManagement.Read.Directory` missing, or no PIM licence: no just-in-time role eligibility. |
| `graph_admin_units` | — | `AdministrativeUnit.Read.All` missing. |
| `graph_domains` | — | `Domain.Read.All` missing: no federated-domain inventory. |
| `graph_tenant_policy` | — | `Policy.Read.All` missing: tenant policy controls and Conditional Access are not assessed. |
| `graph_onprem_sync` | — | `OnPremDirectorySynchronization.Read.All` missing (matters for hybrid tenants). |
| `signin_activity` | — | Last-sign-in and dormancy enrichment unavailable (usually a missing Entra ID P1/P2 licence). |
| `m365_entra-ext` | — | Entra ID policies for `cis-m365-v7` (device registration, PIM settings, access reviews and others) are unreadable. |
| `m365_intune` | — | Intune settings are unreadable (permission or licence). |
| `m365_m365-org` | — | Microsoft 365 admin center settings are unreadable. |
| `m365_sharepoint` | — | SharePoint and OneDrive sharing settings are unreadable. |
| `m365_exo` | — | Exchange Online is unreadable: check `Exchange.ManageAsApp`, Global Reader, and certificate mode. |
| `m365_scc` | — | Purview is unreadable: check `Exchange.ManageAsApp` on Microsoft Exchange Online Protection, Global Reader, and certificate mode. |
| `m365_teams` | — | Teams policies are unreadable: check `Organization.Read.All` and Global Reader. |
| `m365_fabric` | — | Power BI / Fabric settings are unreadable: check the Fabric admin setting and the security group. |

Each `m365_*` failure names the controls that report NOT_ASSESSED without it.
The `m365_exo`, `m365_scc`, `m365_teams` and `m365_fabric` checks run only on an
Entra connection, not on the Entra half of an Azure one.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `auth` fails with `invalid_client` | Client secret: stored the secret **ID** instead of its **Value**, or the secret expired. Certificate: the certificate is not on the app registration. | Re-mint the secret and update the secret record, or run the setup script again. |
| The setup script fails at the certificate upload | The tenant only accepts certificates from a trusted CA. | Exempt the app from that application management policy, or use client-secret mode. |
| `graph_directory` fails after consent | Permissions added as *Delegated*, or consent not actually granted | Add them under *Application permissions* and grant tenant-wide admin consent |
| `m365_exo` or `m365_scc` fails right after the setup script | Permissions take up to an hour to reach Exchange Online. | Test again later. |
| `m365_fabric` fails | The Fabric admin setting is off, or the group does not contain the app, or the app holds a Power BI Service API permission. | Enable the setting for the group, and remove any Power BI Service permission from the app. |
| `signin_activity` fails with a licence error | Sign-in activity needs Entra ID P1/P2 | Accept the degrade, or add the licence |
| Renewal reminder (client secret) | Client secrets expire; when one does, every check fails at `auth` | Re-mint before expiry and update the secret record — nothing else changes |
