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
`login.microsoftonline.us`. Pick **GCC** if your tenant is Microsoft 365 GCC
(moderate); the test cannot detect that choice for you. The provider list then shows the cloud next to the
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
`Exchange.ManageAsApp` and **Global Reader**. The Power BI / Fabric security
group and its Fabric admin setting are needed only in Commercial: the Fabric
controls are [not assessed](#checks-that-are-not-assessed-in-a-cloud) in GCC,
GCC High and DoD, so skip that step there. In GCC High and DoD the Teams controls
are not assessed either, so `Connect-MicrosoftTeams` is never needed for them.

## What the connection test says

Run **Test Provider** (or `limacharlie cloudsec provider test`) before saving.
The test asks the tenant's public Microsoft sign-in metadata which cloud the
tenant is in and compares the answer with `microsoft_cloud`. When they differ, it
fails and the message names the cloud the tenant is in and the value to set:

> this tenant is in Microsoft's US Government (GCC High) cloud, but the connection
> is set to Commercial; set Microsoft cloud to GCC High

The check is named `microsoft_cloud` ("Tenant is in the declared Microsoft
cloud"). On a mismatch the `auth` check fails with the same message, because no
token request can succeed against the wrong cloud. It works in both directions:
a commercial tenant saved as GCC High is refused too, with a message that names
Commercial as the value to set.

Fix the field and test again. The test never changes the field for you. When
Microsoft's metadata cannot be read or its values are not recognized, the check
fails as optional and the test goes on to the credential checks, so only a
confirmed mismatch blocks the connection.

A GCC tenant is not told apart from a commercial one: Microsoft reports no
separate sub-scope for it, so the test does not flag a `commercial` / `gcc`
choice. Choosing between those two is your declaration.

For an `entra` connection in GCC High or DoD, the test also requests an Exchange
Online token, so a tenant that cannot be read there fails the test with a clear
message instead of passing and leaving Exchange checks empty. An `azure`
connection does not read Exchange Online.

## Checks that are not assessed in a cloud

A check that depends on a Microsoft service LimaCharlie has no supported read
for in the connection's cloud reports **NOT_ASSESSED**, with a reason such as
*Microsoft does not offer this service in GCC High*. It is never an error and
never a pass.

| Plane (`provider test` check) | Commercial | GCC | GCC High | DoD |
|---|:--:|:--:|:--:|:--:|
| Entra ID, Conditional Access, Intune, SharePoint sharing settings (Microsoft Graph) | ✅ | ✅ | ✅ | ✅ |
| Microsoft 365 admin center org settings: Office Store and trials, Forms phishing protection (`m365_m365-org`) | ✅ | ✅ | Not assessed | Not assessed |
| Exchange Online, Defender for Office 365 (`m365_exo`) | ✅ | ✅ | ✅ | ✅ |
| Zero-hour auto purge for Teams, CIS Microsoft 365 2.4.4 (part of `m365_exo`) | ✅ | Not assessed | Not assessed | Not assessed |
| Purview (`m365_scc`) | ✅ | ✅ | ✅ | ✅ |
| Teams policies (`m365_teams`) | ✅ | ✅ | Not assessed | Not assessed |
| Power BI / Fabric tenant settings (`m365_fabric`) | ✅ | Not assessed | Not assessed | Not assessed |

Microsoft documents Power BI itself in every US Government cloud, but not a Teams
admin read or a Fabric admin API that a service principal can call there, so the
controls built on them stay NOT_ASSESSED until Microsoft documents one. The
sign-in addresses for Power BI in each cloud are in Microsoft's
[Power BI for US Government](https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-government-us-overview)
overview.

The Microsoft 365 admin center org settings come from the Microsoft Graph
[apps and services](https://learn.microsoft.com/en-us/graph/api/adminappsandservices-get?view=graph-rest-beta)
and [Forms](https://learn.microsoft.com/en-us/graph/api/adminforms-get?view=graph-rest-beta)
settings APIs. Microsoft offers those APIs only on the global service, not in
GCC High or DoD. So in those two clouds, CIS Microsoft 365 controls 1.3.4 (users
cannot use the Office Store or start trials) and 1.3.5 (Forms internal phishing
protection) are not assessed. Their findings also give no PowerShell fix, only
the admin center steps. GCC uses the global service, so they are assessed there.

In GCC High and DoD, a service principal's last sign-in is also unknown. It comes from
Microsoft Graph's
[service principal sign-in activity report](https://learn.microsoft.com/en-us/graph/api/reportroot-list-serviceprincipalsigninactivities?view=graph-rest-beta),
which Microsoft offers only on the global service. Users' last sign-in is not
affected.

Zero-hour auto purge (ZAP) for Microsoft Teams is not available in GCC, GCC High
or DoD
([Microsoft Learn](https://learn.microsoft.com/en-us/defender-office-365/zero-hour-auto-purge)).
In those clouds LimaCharlie does not read the Teams protection policy, CIS
Microsoft 365 control 2.4.4 is not assessed, and no finding is raised for it. The
other Defender for Office 365 controls (Safe Links, Safe Attachments,
anti-phishing, anti-spam, anti-malware) are assessed as usual.

Each Defender for Office 365 and Exchange Online Protection policy type is read on
its own. If one policy read fails, only the controls that depend on it are not
assessed, and the rest are still graded.

Everything else reads in the same way as in commercial.

The same `m365_exo`, `m365_scc`, `m365_teams` and `m365_fabric` checks only run on
an Entra connection, in every cloud. See
[Verify](entra.md#verify).

### Azure subscriptions in Azure Government

GCC High and DoD subscriptions run in Azure Government. GCC subscriptions run in
global Azure, so everything below applies to them as in commercial.

| Defender for Cloud plan or feature | Commercial, GCC | GCC High, DoD |
|---|:--:|:--:|
| Defender for App Service plan | Checked | Not checked: not offered |
| Defender for APIs plan | Checked | Not checked: not offered |
| Other Defender plans (Servers, CSPM, Containers, Storage, databases, Key Vault, Resource Manager, AI services) | Checked | Checked |
| VM vulnerability scanning (Defender for Servers or Defender CSPM) | Counted as coverage | Counted as coverage |

Microsoft lists Defender for App Service and Defender for APIs as not available in
Azure Government
([Defender for Cloud support matrix](https://learn.microsoft.com/en-us/azure/defender-for-cloud/support-matrix-cloud-environment)).
A subscription there is not told to turn them on, and an older finding for
either plan closes on the next scan.

The same matrix lists Defender Vulnerability Management (agentless scanning and
the Defender for Endpoint sensor) as available in Azure Government. So in GCC High
and DoD, as in commercial, a subscription with a paid Defender for Servers or
Defender CSPM plan counts as having a VM vulnerability source. Microsoft's
[feature availability](https://learn.microsoft.com/en-us/azure/security/fundamentals/feature-availability)
page lists "Integrated vulnerability assessment for machines" as not available
there. That row refers to the older built-in scanner, not to Defender
Vulnerability Management.
