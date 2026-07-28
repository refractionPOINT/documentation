# Microsoft Azure

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and configuration
    formats on this page can change before general availability. Contact us to
    request access.

This provider collects the Azure estate: VMs and scale sets, storage, Key
Vault, SQL/Cosmos, AKS, networking and NSGs, and Azure OpenAI. It also
collects the Entra ID directory of the tenant (users, groups, service
principals, app registrations, roles). With the correct licence, it collects
Conditional Access and sign-in activity.

**Auth model:** an **Entra ID app registration** (service principal) with a
**client secret**. Give it the **Reader** RBAC role on your subscriptions and
**Microsoft Graph application permissions** on the tenant.

!!! tip "Directory only, no Azure subscription?"
    If you have Entra ID / Microsoft 365 but no Azure infrastructure to
    enumerate, use the [Entra ID](entra.md) provider. It uses the same app
    registration and needs no ARM setup.

## Prerequisites

- Permission to create an app registration in the tenant (**Application
  Developer** or higher).
- Permission to **grant tenant-wide admin consent** for Graph application
  permissions (**Privileged Role Administrator** or **Global Administrator**).
- **Owner** or **User Access Administrator** on each subscription that you
  want to read, to assign Reader.

## Required permissions

| Grant | Where | Why | Preflight check |
|---|---|---|---|
| **Reader** RBAC role | On each subscription (or a management group above them) | Reads every resource in the subscription, and the Defender/Resource Graph security views | `arm_reader` |
| **Directory.Read.All** (application) | Microsoft Graph | Users, groups, service principals, app registrations, domains, directory roles | `graph_directory` |

## Optional permissions

| Grant | Unlocks | Preflight check |
|---|---|---|
| **Policy.Read.All** (application) | Conditional Access policy posture | *(collected during the sweep)* |
| **AuditLog.Read.All** (application) | Last-sign-in / dormancy enrichment on identities. **Needs an Entra ID P1 or P2 licence**. Without the licence, the report is unavailable, even with consent | `signin_activity` |
| **RoleManagement.Read.Directory** (application) | Directory role assignments and PIM eligibility | *(collected during the sweep)* |
| **Application.Read.All** (application) | More credential detail for app registrations and service principals | *(collected during the sweep)* |
| **AdministrativeUnit.Read.All** (application) | Administrative-unit scoping | *(collected during the sweep)* |
| **AgentIdentity.Read.All** (application) | Source-asserted AI-agent identities in the directory | *(collected during the sweep)* |
| *(covered by Reader)* | Defender for Cloud vulnerability assessments through Azure Resource Graph | `defender_vuln` |

If Graph denies one permission, only its own collector gets a 403 error. That
surface is not collected, but all other collectors continue.

## Create the app registration

```bash
TENANT_ID=$(az account show --query tenantId -o tsv)
SUB_ID=<your-subscription-id>

# 1. App registration + service principal
APP_ID=$(az ad app create --display-name lc-cloudsec --query appId -o tsv)
az ad sp create --id "$APP_ID"

# 2. Client secret (note the expiry you choose; --append preserves existing ones)
az ad app credential reset --id "$APP_ID" --years 2 --append \
  --display-name lc-cloudsec --query password -o tsv     # capture this once

# 3. RBAC Reader on the subscription (repeat per subscription)
az role assignment create --assignee "$APP_ID" --role Reader \
  --scope "/subscriptions/${SUB_ID}"

# 4. Microsoft Graph application permissions
GRAPH=00000003-0000-0000-c000-000000000000
az ad app permission add --id "$APP_ID" --api "$GRAPH" --api-permissions \
  7ab1d382-f21e-4acd-a863-ba3e13f7da61=Role   # Directory.Read.All
az ad app permission add --id "$APP_ID" --api "$GRAPH" --api-permissions \
  246dd0d5-5bd0-4def-940b-0421030a5b68=Role   # Policy.Read.All
az ad app permission add --id "$APP_ID" --api "$GRAPH" --api-permissions \
  b0afded3-3588-46d8-8b3d-9842eff778da=Role   # AuditLog.Read.All

# 5. Tenant-wide admin consent (needs a privileged admin)
az ad app permission admin-consent --id "$APP_ID"
```

!!! note "In the portal"
    1. Go to **Microsoft Entra ID → App registrations → New registration**.
    2. Go to **Certificates & secrets → New client secret**. Copy the
       *Value*, not the ID.
    3. Go to **API permissions → Add a permission → Microsoft Graph →
       Application permissions** and add the permissions above.
    4. Select **Grant admin consent for \<tenant\>**. The status column must
       read *Granted*.
    5. Go to **Subscriptions → \<sub\> → Access control (IAM) → Add role
       assignment → Reader → your app**.

!!! danger "`credential reset` clears existing secrets"
    Always use `--append` when the app holds credentials that other systems
    need. Without `--append`, `az ad app credential reset` **removes every
    existing password and certificate** on the app before it adds the new
    one.

!!! danger "Application permissions, not delegated"
    Add the Graph permissions under **Application permissions**. Delegated
    permissions need a signed-in user. With delegated permissions, the
    `graph_directory` check continues to fail, even after consent.

## Create the credentials secret

```json
{"client_id": "<application-client-id>", "client_secret": "<the-secret-value>"}
```

```bash
limacharlie hive set --hive-name secret --key azure-sp \
    --input-file azure-secret.json --enabled
```

## Create the provider record

`provider.yaml`:

```yaml
provider_type: azure
azure_tenant_id: "<tenant-id>"
azure_client_id: "<application-client-id>"
azure_subscription_id: "<subscription-id>"
credentials: hive://secret/azure-sp
internal_domains: [example.com, example.onmicrosoft.com]
refresh: 6h
```

!!! info "`azure_subscription_id` is an anchor, not a limit"
    The collector enumerates **every subscription that the service principal
    can see** (`subscriptions` check). Assign Reader on each subscription that
    you want to sweep. The subscription named here is only the anchor for
    scoping and probing. If the tenant-wide `subscriptions` read is denied,
    the sweep covers the one configured subscription.

In the web app, select **Add provider → Azure**. Then set **Tenant ID**,
**Client ID**, **Subscription ID**, **Credentials**, and **Refresh
interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The client ID/secret pair was rejected, or the secret expired. |
| `arm_reader` | ✅ | Reader is not assigned on the configured subscription. There is no resource inventory. |
| `graph_directory` | ✅ | `Directory.Read.All` has no consent. There is no identity inventory. |
| `subscriptions` | — | Subscription fan-out is disabled. The sweep covers only the configured subscription. |
| `defender_vuln` | — | Workload vulnerability findings unavailable. |
| `signin_activity` | — | Last-sign-in and dormancy enrichment unavailable. The usual cause is a missing Entra ID P1/P2 licence. |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails with `invalid_client` | The secret **ID** was stored instead of the secret **Value**, or the secret expired | Create a new secret with `az ad app credential reset` and store the new value |
| `graph_directory` fails after you add the permissions | Admin consent not granted, or permissions added as *Delegated* | Grant tenant-wide admin consent. Check that the permissions are under *Application* |
| `arm_reader` fails | Reader assigned at the wrong scope, or not yet propagated | Assign Reader on the subscription (or a management group above it). Try again after a minute |
| `signin_activity` fails with a licence error | Sign-in activity needs Entra ID P1/P2 | Accept the reduced data, or add the licence |
| Directory data appears twice | An `azure` **and** an `entra` record both cover the tenant | LimaCharlie handles this automatically. The Azure connection defers its tenant-global directory collectors to the standalone [Entra](entra.md) record |
| A scale set / App Service is missing | The resource type can need quota or a supported SKU in that subscription | Check that the SP can see the resource. Run `az resource list` under the same identity |
