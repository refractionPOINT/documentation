# Microsoft US Government clouds (GCC, GCC High, DoD)

Tenants in Microsoft's US Government clouds sign in at different Microsoft
addresses than commercial tenants, so a connection has to say which cloud its
tenant lives in. This page covers that choice for the
[Azure](azure.md) and [Microsoft Entra ID / Microsoft 365](entra.md) providers.
Everything else in those two guides applies unchanged.

## Choose the Microsoft cloud

Set **Microsoft cloud** on the connection (web app: **Configuration** step), or
`microsoft_cloud` on the provider record.

In the web app, **Microsoft cloud** is a select on the Azure and Entra ID
**Configuration** step. It defaults to **Commercial**, which writes nothing to the
record. Pick **GCC High** or **DoD** if your tenant signs in at
`login.microsoftonline.us`. The provider list then shows the cloud next to the
tenant, and the setup instructions and generated PowerShell follow your choice.

| Value | Web app label | Use it when |
|---|---|---|
| `commercial` (or empty, the default) | Commercial | Your tenant signs in at `login.microsoftonline.com`: any commercial Microsoft 365 or Azure tenant. |
| `gcc` | GCC | Your tenant is Microsoft 365 GCC (moderate). |
| `gcc_high` | GCC High | Your tenant is Microsoft 365 GCC High (Azure Government). |
| `dod` | DoD | Your tenant is Microsoft 365 DoD (Azure Government). |

- The field is valid only on `azure` and `entra` connections. Any other provider
  type with a value is rejected, and so is a value that is not in the table.
- A record without the field is a commercial connection. Existing connections
  are not changed.
- LimaCharlie never switches cloud for you. The record says which Microsoft
  cloud to use, and a [connection test](#what-the-connection-test-says) tells you
  when that does not match the tenant.
- Choose the cloud for the **tenant**. If you hold both an `azure` and an `entra`
  connection for the same tenant, give both the same value.

### What changes per cloud

| | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Sign-in authority | `login.microsoftonline.com` | `login.microsoftonline.com` | `login.microsoftonline.us` | `login.microsoftonline.us` |
| Microsoft Graph | `graph.microsoft.com` | `graph.microsoft.com` | `graph.microsoft.us` | `dod-graph.microsoft.us` |
| Azure portal | `portal.azure.com` | `portal.azure.com` | `portal.azure.us` | `portal.azure.us` |
| Microsoft Entra admin center | `entra.microsoft.com` | `entra.microsoft.com` | `entra.microsoft.us` | `entra.microsoft.us` |
| Azure Resource Manager | `management.azure.com` | `management.azure.com` | `management.usgovcloudapi.net` | `management.usgovcloudapi.net` |

Microsoft documents these in
[Microsoft Graph and Graph Explorer service root endpoints](https://learn.microsoft.com/en-us/graph/deployments),
[National clouds](https://learn.microsoft.com/en-us/entra/identity-platform/authentication-national-cloud)
and
[Compare Azure Government and global Azure](https://learn.microsoft.com/en-us/azure/azure-government/compare-azure-government-global-azure).
GCC uses the worldwide endpoints.

## Configuration examples

=== "Azure, GCC High"

    ```yaml
    provider_type: azure
    microsoft_cloud: gcc_high
    azure_tenant_id: "<tenant-id>"
    azure_client_id: "<application-client-id>"
    azure_subscription_id: "<azure-government-subscription-id>"
    credentials: hive://secret/azure-sp
    refresh: 6h
    ```

=== "Entra ID / Microsoft 365, GCC High"

    ```yaml
    provider_type: entra
    microsoft_cloud: gcc_high
    entra_tenant_id: "<tenant-id>"
    entra_client_id: "<application-client-id>"
    entra_auth_mode: certificate
    credentials: hive://secret/cloudsec-m365-entra-gcch
    refresh: 6h
    ```

=== "Entra ID / Microsoft 365, DoD"

    ```yaml
    provider_type: entra
    microsoft_cloud: dod
    entra_tenant_id: "<tenant-id>"
    entra_client_id: "<application-client-id>"
    entra_auth_mode: certificate
    credentials: hive://secret/cloudsec-m365-entra-dod
    refresh: 6h
    ```

=== "Entra ID / Microsoft 365, GCC"

    ```yaml
    provider_type: entra
    microsoft_cloud: gcc
    entra_tenant_id: "<tenant-id>"
    entra_client_id: "<application-client-id>"
    entra_auth_mode: certificate
    credentials: hive://secret/cloudsec-m365-entra-gcc
    refresh: 6h
    ```

The rest of each record (certificate fields, `internal_domains`, `refresh`)
is the same as in the [Azure](azure.md#create-the-provider-record) and
[Entra ID](entra.md#without-the-web-app) guides. The field also works in
[infrastructure as code](../configuration.md) and through the API and CLI.

## Set up the app registration in a government cloud

The connection still uses an app registration in **your** tenant, with the
permissions the [Azure](azure.md#required-permissions) and
[Entra ID](entra.md#permissions) guides list. Create it in the cloud's own
portals:

- **GCC High and DoD:** sign in to the
  [Azure Government portal](https://portal.azure.us) and open **Microsoft Entra
  ID**, or go to the Microsoft Entra admin center for US Government at
  `https://entra.microsoft.us` (Microsoft lists it in the
  [Entra FAQ](https://learn.microsoft.com/en-us/entra/fundamentals/faq)). Use the same menus the guides describe
  (**App registrations**, **API permissions**, **Certificates & secrets**).
  Azure subscriptions and the **Reader** role assignment are made in
  `https://portal.azure.us`.
- **GCC:** the commercial portals (`https://portal.azure.com`,
  `https://entra.microsoft.com`) are the right ones.

Pick **Microsoft Graph** under **API permissions** exactly as in the
commercial guides. In an Azure CLI session, run `az cloud set --name
AzureUSGovernment` before `az login` for GCC High and DoD, and look up each Graph
permission ID with `az ad sp show --id 00000003-0000-0000-c000-000000000000
--query "appRoles[?value=='<permission>'].id"` in that session rather than copying
IDs from another cloud.

### Setup script for certificate mode (Entra ID / Microsoft 365)

The web app picks the right PowerShell environment names into the generated
script from the **Microsoft cloud** you chose. If you run the steps by hand,
connect with these values:

| Cloud | `Connect-MgGraph` | `Connect-ExchangeOnline` | `Connect-MicrosoftTeams` |
|---|---|---|---|
| Commercial, GCC | default (`Global`) | default | default |
| GCC High | `-Environment USGov` | `-ExchangeEnvironmentName O365USGovGCCHigh` | `-TeamsEnvironmentName TeamsGCCH` |
| DoD | `-Environment USGovDoD` | `-ExchangeEnvironmentName O365USGovDoD` | `-TeamsEnvironmentName TeamsDOD` |

Microsoft documents these in
[Connect-MgGraph environments](https://learn.microsoft.com/en-us/powershell/microsoftgraph/authentication-commands),
[Connect to Exchange Online PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-exchange-online-powershell)
and
[Connect-MicrosoftTeams](https://learn.microsoft.com/powershell/module/teams/connect-microsoftteams).
A GCC tenant uses the commercial defaults.

Everything else in the script is unchanged: the application permissions,
`Exchange.ManageAsApp`, **Global Reader**, and the Power BI / Fabric security
group.

## What the connection test says

Run **Test Provider** (or `limacharlie cloudsec provider test`) before saving.
The test asks Microsoft which cloud the tenant is in and compares the answer with
`microsoft_cloud`. When they differ, it fails and the message names the cloud the
tenant is in and the value to set. For example, a GCC High tenant saved with no
`microsoft_cloud` is refused with a message telling you to set Microsoft cloud to
GCC High. Fix the field and test again. The test never changes the field for you.

A GCC tenant is not told apart from a commercial one: Microsoft reports no
separate sub-scope for it, so the test does not flag a `commercial` / `gcc`
choice. Choosing between those two is your declaration.

For GCC High and DoD, the test also requests an Exchange Online token, so a
tenant that cannot be read there fails the test with a clear message instead of
passing and leaving Exchange checks empty.

## Checks that are not assessed in a cloud

A check that depends on a Microsoft service LimaCharlie has no supported read
for in the connection's cloud reports **NOT_ASSESSED** with a reason that says
so. It is never an error and never a pass.

| Plane (`provider test` check) | Commercial | GCC | GCC High | DoD |
|---|:--:|:--:|:--:|:--:|
| Entra ID, Conditional Access, Intune, Microsoft 365 admin center, SharePoint sharing settings (Microsoft Graph) | ✅ | ✅ | ✅ | ✅ |
| Exchange Online, Defender for Office 365 (`m365_exo`) | ✅ | ✅ | ✅ | ✅ |
| Purview (`m365_scc`) | ✅ | ✅ | ✅ | ✅ |
| Teams policies (`m365_teams`) | ✅ | ✅ | Not assessed | Not assessed |
| Power BI / Fabric tenant settings (`m365_fabric`) | ✅ | Not assessed | Not assessed | Not assessed |

Microsoft documents Power BI itself in every US Government cloud, but not a Teams
admin read or a Fabric admin API that a service principal can call there, so the
controls built on them stay NOT_ASSESSED until Microsoft documents one. The
sign-in addresses for Power BI in each cloud are in Microsoft's
[Power BI for US Government](https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-government-us-overview)
overview. Everything else reads in the same way as in commercial.

The same `m365_exo`, `m365_scc`, `m365_teams` and `m365_fabric` checks only run on
an Entra connection, in every cloud. See
[Verify](entra.md#verify).
