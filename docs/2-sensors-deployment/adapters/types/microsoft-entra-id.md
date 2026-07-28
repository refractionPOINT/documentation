# Microsoft Entra ID

[Microsoft Entra ID](https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id), formerly Azure Active Directory, is an identity and access management solution from Microsoft that helps organizations secure and manage identities for hybrid and multicloud environments.

The Entra ID API Adapter polls Microsoft Graph directly. It can collect three streams: Identity Protection **risk detections**, **sign-in logs** and **directory audit logs**. It needs only an Entra app registration, and no Azure subscription or Event Hub. Therefore, it is the least complex method to standardize the collection of Entra telemetry across tenants. Data that you receive through an Azure Event Hub or Webhook is unique to your custom output parameters.

Entra ID data uses one of two platform values, which depend on the ingestion method. The two values are **not** interchangeable:

- **Azure Event Hub / Webhook** (diagnostic settings log stream — SignInLogs, AuditLogs, etc.): `client_options.platform: azure_ad`
- **Entra ID API** (risk detections, sign-in logs and directory audit logs polled from Microsoft Graph): `client_options.platform: entraid`

> **Note on naming:** The platform identifier `azure_ad` comes from the legacy product name (Azure Active Directory). Microsoft renamed this product to Microsoft Entra ID in 2023. The two identifiers name the same product, but they select different parsers. `azure_ad` parses the Azure diagnostic-stream `records` envelope (event type from `category`, timestamp from `time`). `entraid` parses the Graph objects directly (event type from `activity`/`category`, or `SignIn` for sign-in records; timestamp from `detectedDateTime`/`activityDateTime`/`createdDateTime`, which depends on the stream). If you cross the two, the extraction of the event type and the timestamp breaks without an error.
>
> **Choosing by data need:** Directory audit events include app consent (`Consent to application`), OAuth2 permission grants (`Add OAuth2PermissionGrant`), app role assignments, and changes to users, groups and roles. Three sources give these events: the API adapter's `audit_logs` stream, the diagnostic-stream **AuditLogs** category (Event Hub, platform `azure_ad`), and the Microsoft 365 unified audit log ([`office365` adapter](microsoft-365.md), `Audit.AzureActiveDirectory` content type, where operation names have a trailing period). For Entra streams, use `azure_ad` and not `azure_monitor`. Both parse the same envelope, but the platform value tags the sensor. The tag then controls `is platform` and LCQL targeting, and shared detection rules.

## Data Collected

### API vs Event Hub vs Webhook Comparison

| Method | Data Source | What You Get | Platform |
|--------|-------------|--------------|----------|
| **Entra ID API** | Microsoft Graph API | Risk detections, sign-in logs, directory audit logs (selectable streams) | `entraid` |
| **Azure Event Hub** | Azure Diagnostic Settings | Whatever logs you configure (sign-in, audit, etc.) | `azure_ad` |
| **Webhook** | Your configuration | Whatever you send to the webhook URL | `azure_ad` (if relaying the diagnostic-stream format) |

### Entra ID API

The API adapter polls Microsoft Graph every 30 seconds. The `streams` option selects which collections it polls, as comma separated values:

| Stream | Graph endpoint | What You Get | LimaCharlie event type |
|--------|----------------|--------------|------------------------|
| `risk_detections` (default) | `/identityProtection/riskDetections` | Identity Protection risk detection alerts (risky sign-ins, leaked credentials, anonymous IPs, malware-linked IPs, …) | the detection's `activity` (e.g. `signin`) |
| `sign_ins` | `/auditLogs/signIns` | Interactive sign-in events (user, app, IP, location, device, conditional access result) | `SignIn` |
| `audit_logs` | `/auditLogs/directoryAudits` | Directory changes: user/group/role management, app registrations, app consent and OAuth2 permission grants | the audit's `category` (e.g. `UserManagement`, `ApplicationManagement`) |

For example, `streams: risk_detections,sign_ins,audit_logs` collects all three streams. If you leave the option empty, the adapter collects risk detections only. This is the historical behavior of existing deployments.

For the full list of risk detection types, see [Microsoft's documentation](https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks).

**Requirements per stream:**

- `risk_detections` needs the `IdentityRiskEvent.Read.All` application permission. The tenant produces risk detections only with Entra ID Identity Protection (P2 for the full detection set).
- `sign_ins` needs the `AuditLog.Read.All` and `Directory.Read.All` application permissions. The tenant must also hold an Entra ID P1 (or P2) license. This is a Microsoft Graph requirement, the same one that applies when you stream SignInLogs to an Event Hub.
- `audit_logs` needs the `AuditLog.Read.All` application permission.

### Azure Event Hub

When you use Event Hub, you receive the data that you configure Azure to stream. You must configure **Azure Diagnostic Settings** in Entra ID to send logs to your Event Hub. Common log types include:

- **Sign-in logs** - Interactive and non-interactive authentication events
- **Audit logs** - Directory changes (user/group management, app registrations, app consent and OAuth2 permission grants)
- **Provisioning logs** - User provisioning to SaaS apps
- **Risky users/sign-ins** - Identity Protection detections (alternative to API)

In the `azure_ad` stream, the LimaCharlie event type is the log *category* (e.g. `AuditLogs`, `SignInLogs`). Therefore, a detection rule that targets a specific operation matches on the `event/operationName` field.

See [Microsoft's documentation on streaming Entra ID logs](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-stream-logs-to-event-hub).

## Adapter Deployment

LimaCharlie ingests Microsoft Entra ID logs with these methods:

1. Azure Event Hub
2. Entra ID API
3. Webhooks

### Azure Event Hub

The LimaCharlie web app has a helper. Use it to configure how LimaCharlie receives Entra ID events through an Azure Event Hub.

If you use the helper, only two fields are required:

- Name for the adapter
- Connection string to the Azure Event Hub

See the [Azure Event Hub Adapter documentation](azure-event-hub.md) for more information.

Microsoft has [documentation for creating an Event Hub](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-create).

### Entra ID API

To collect data through the Entra ID API, configure an App Registration in Azure. Make sure that it has the correct permissions.

1. In Azure, go to the Entra ID Overview page. Select **App Registrations** and click `+ New Registration`.
2. Name the application, and select the **Supported account types**.
3. After you register an App, Azure shows metadata for that application. Record the `Application (client) ID` and `Directory (tenant) ID` fields. You need them for the configuration.
4. Select **Add a certificate or secret,** and create a new client secret. Give a description and select an applicable Expiration time. *Note: You must refresh the Secret in LimaCharlie after it expires!*
5. After you create the secret, copy the `Secret Value`. You need it to configure the LimaCharlie Adapter.
6. Go to the **Manage** > **API permissions** menu for your new application. Grant the **Application** permissions that the streams you plan to collect need (see [Requirements per stream](#entra-id-api)):

   1. IdentityRiskEvent.Read.All (`risk_detections`)
   2. AuditLog.Read.All (`sign_ins`, `audit_logs`)
   3. Directory.Read.All (`sign_ins`)
   4. User.Read (default)

7. Click **Grant admin consent** for the tenant. Application permissions have no effect until an admin consents.

Create a new Adapter within LimaCharlie, and select Microsoft Entra ID. Select `Microsoft Entra ID API` as the ingestion method.

1. Name the Adapter and give these details:

   1. Tenant ID
   2. Client ID
   3. Client Secret
   4. Streams (optional): comma separated values among `risk_detections`, `sign_ins` and `audit_logs`; empty means `risk_detections` only
   5. *Note: You can use the Secrets Manager for these values.*

Click **Complete Cloud Installation**. LimaCharlie then creates the Adapter. Monitor the **Platform Logs** for errors.

**Note:** Collection starts when you create the Adapter (there is no historical backfill). A stream gives events only when new events occur. For `risk_detections`, no data after creation usually means that no risky events occurred yet.

### Webhooks

The LimaCharlie web app has a helper. Use it to configure how LimaCharlie receives Entra ID events.

If you use the helper, only two fields are required:

- Name for the adapter
- Secret component of the URL for the webhook

For more information about how to create a webhook and get the completed URL with the secret component, see the [webhook adapter tutorial](../tutorials/webhook-adapter.md).
