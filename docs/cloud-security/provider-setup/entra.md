# Microsoft Entra ID

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

A **directory-only** connection for organizations that use Entra ID or
Microsoft 365 but have no Azure infrastructure to enumerate. It collects the
tenant-global identity surface over Microsoft Graph: users, groups and
membership, service principals and app registrations (with their long-lived
credentials), directory roles and PIM eligibility, Conditional Access policies,
and administrative units.

**Auth model:** an **Entra ID app registration** (service principal) with a
**client secret** and **Microsoft Graph application permissions**. There is no
ARM/subscription setup at all.

!!! tip "Already connecting Azure?"
    The [Azure](azure.md) provider collects this same directory as part of its
    sweep. You only need a standalone Entra record when there is no Azure
    subscription to connect — or when you want the directory collected
    independently of the infrastructure connection. Holding **both** for one
    tenant is supported and safe: the Azure connection detects the standalone
    record and defers its tenant-global directory collectors to it, so the
    directory is never collected twice.

## Prerequisites

- Permission to create an app registration (**Application Developer** or
  higher).
- Permission to **grant tenant-wide admin consent** (**Privileged Role
  Administrator** or **Global Administrator**).
- Your **tenant ID** (Entra ID → Overview).

## Required permissions

| Grant | Type | Why | Preflight check |
|---|---|---|---|
| **Directory.Read.All** | Microsoft Graph — **Application** | Users, groups, service principals, app registrations, domains, directory roles | `graph_directory` |

## Optional permissions

| Grant | Unlocks | Preflight check |
|---|---|---|
| **AuditLog.Read.All** | Last-sign-in / dormancy enrichment. **Requires Entra ID P1 or P2** | `signin_activity` |
| **Policy.Read.All** | Conditional Access policy posture | *(collected during the sweep)* |
| **RoleManagement.Read.Directory** | Directory role assignments and PIM eligibility | *(collected during the sweep)* |
| **Application.Read.All** | Fuller app-registration / service-principal credential detail | *(collected during the sweep)* |
| **AdministrativeUnit.Read.All** | Administrative-unit scoping | *(collected during the sweep)* |
| **AgentIdentity.Read.All** | Source-asserted AI-agent identities in the directory | *(collected during the sweep)* |

## Create the app registration

```bash
TENANT_ID=$(az account show --query tenantId -o tsv)

APP_ID=$(az ad app create --display-name lc-entra --query appId -o tsv)
az ad sp create --id "$APP_ID"

az ad app credential reset --id "$APP_ID" --years 2 \
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

!!! note "In the portal"
    **Microsoft Entra ID → App registrations → New registration** →
    **Certificates & secrets → New client secret** (copy the *Value*) →
    **API permissions → Add a permission → Microsoft Graph → Application
    permissions** → add the permissions above → **Grant admin consent for
    \<tenant\>**.

!!! danger "Application permissions, not delegated"
    Graph permissions must be **Application** permissions. Delegated
    permissions need a signed-in user and leave `graph_directory` failing even
    after consent.

## Create the credentials secret

```json
{"client_id": "<application-client-id>", "client_secret": "<the-secret-value>"}
```

```bash
limacharlie hive set --hive-name secret --key entra-sp \
    --input-file entra-secret.json --enabled
```

## Create the provider record

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

In the web app: **Add provider → Entra ID**, then set **Tenant ID**, **Client
ID**, **Credentials**, and **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The client ID/secret pair was rejected, or the secret expired. |
| `graph_directory` | ✅ | `Directory.Read.All` not consented — no identity inventory. |
| `signin_activity` | — | Last-sign-in and dormancy enrichment unavailable (usually a missing Entra ID P1/P2 licence). |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails with `invalid_client` | Stored the secret **ID** instead of its **Value**, or the secret expired | Re-mint the secret and update the hive secret |
| `graph_directory` fails after consent | Permissions added as *Delegated*, or consent not actually granted | Add them under *Application permissions* and grant tenant-wide admin consent |
| `signin_activity` fails with a licence error | Sign-in activity needs Entra ID P1/P2 | Accept the degrade, or add the licence |
| Renewal reminder | Client secrets expire; when one does, every check fails at `auth` | Re-mint before expiry and update the secret record — nothing else changes |
