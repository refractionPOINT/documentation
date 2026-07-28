# Microsoft Response

The Microsoft Response LimaCharlie Extension gives D&R rules and AI agents the incident-response and investigation surface of two Microsoft cloud security platforms. **Microsoft Graph** supplies Entra ID identities, Identity Protection, groups, Intune devices, and audit logs. It also supplies the Defender XDR security API for cross-product alerts, incidents, and advanced hunting. **Microsoft Defender for Endpoint** supplies machine isolation, scans, forensics, file quarantine, alerts, file intelligence, and custom indicators. With the extension, you can investigate and contain a compromised account or endpoint directly from a detection.

The extension provides two layers:

- **Typed actions** for the common containment, triage, and investigation workflows. They use clear parameter names and have built-in safety limits.
- A generic **`api_call`** passthrough for any Graph or Defender endpoint that no typed action covers.

Authentication uses OAuth2 **client credentials** against an Entra app registration. There is no user interaction and there are no delegated tokens.

## Setup

### 1. Create an Entra app registration

In the Azure portal, go to **Entra ID → App registrations → New registration** and create an app registration. Record its **Application (client) ID** and your **Directory (tenant) ID**. Create a **client secret** under *Certificates & secrets*.

### 2. Grant application permissions

Under *API permissions*, add **application** permissions, not delegated permissions, and grant **admin consent**. The least-privilege set for each capability:

| Capability | Permission | API |
| --- | --- | --- |
| List/read users | `User.Read.All` | Microsoft Graph |
| Disable / enable account | `User.EnableDisableAccount.All` | Microsoft Graph |
| Revoke sign-in sessions | `User.RevokeSessions.All` | Microsoft Graph |
| Reset password | `User-PasswordProfile.ReadWrite.All` | Microsoft Graph |
| List authentication methods | `UserAuthenticationMethod.Read.All` | Microsoft Graph |
| User group/role memberships (`list_user_groups`) | `Directory.Read.All` | Microsoft Graph |
| Risky users (read / confirm / dismiss) | `IdentityRiskyUser.ReadWrite.All` (`IdentityRiskyUser.Read.All` is enough for reads) | Microsoft Graph |
| Risk detections (`list_risk_detections`) | `IdentityRiskEvent.Read.All` | Microsoft Graph |
| Groups read / membership change | `GroupMember.ReadWrite.All` (`GroupMember.Read.All` is enough for reads) | Microsoft Graph |
| Sign-in & directory audit logs | `AuditLog.Read.All` | Microsoft Graph |
| Defender XDR alerts (read / update + comment) | `SecurityAlert.Read.All` / `SecurityAlert.ReadWrite.All` | Microsoft Graph |
| Defender XDR incidents (read / update) | `SecurityIncident.Read.All` / `SecurityIncident.ReadWrite.All` | Microsoft Graph |
| Advanced hunting (`run_hunting_query`) | `ThreatHunting.Read.All` | Microsoft Graph |
| Intune device actions | `DeviceManagementManagedDevices.PrivilegedOperations.All` (+ `DeviceManagementManagedDevices.Read.All` to list/get) | Microsoft Graph |
| Machine isolation | `Machine.Isolate` | WindowsDefenderATP |
| Antivirus scan | `Machine.Scan` | WindowsDefenderATP |
| Restrict app execution | `Machine.RestrictExecution` | WindowsDefenderATP |
| Collect investigation package | `Machine.CollectForensics` | WindowsDefenderATP |
| Stop & quarantine file | `Machine.StopAndQuarantine` | WindowsDefenderATP |
| List/get machines, machine actions, find-by-IP, package URI | `Machine.ReadWrite.All` | WindowsDefenderATP |
| Defender alerts (list/get/update) | `Alert.ReadWrite.All` (no app-only read-only permission exists) | WindowsDefenderATP |
| Logged-on users (`list_machine_logon_users`) | `User.Read.All` | WindowsDefenderATP |
| File profiles (`get_file_info`, file machines/alerts) | `File.Read.All` | WindowsDefenderATP |
| Advanced hunting (`run_advanced_query`) | `AdvancedQuery.Read.All` | WindowsDefenderATP |
| Custom indicators (IoCs) | `Ti.ReadWrite.All` | WindowsDefenderATP |

Add only the permissions that you use. If a permission is missing, only the action that needs it fails, with a `403`.

> **Privileged user writes need a directory role too.** Graph permissions alone are not enough for `disable_user`, `enable_user`, and `reset_user_password`. The service principal of the app must also hold an Entra **directory role** (for example *User Administrator*) that covers the target user. A `403` on these actions is a problem with consent or roles, not a bug.
>
> **Identity Protection needs Entra ID P2.** `list_risky_users`, `get_user_risk`, `confirm_user_compromised`, and `dismiss_user_risk` return `403` on a tenant without a P2 license. `list_risk_detections` and the sign-in log (`list_sign_ins`, `get_signin_history`) need P1 or P2.

### 3. Subscribe to the extension

Subscribe to `ext-microsoft-response` from the LimaCharlie **Marketplace** (Extensions → Add-Ons).

### 4. Store the client secret

In **Secrets Manager**, create a new secret, for example `msft-response-client-secret`. Paste the client secret as its value.

### 5. Configure the extension

In **Extensions → ext-microsoft-response → Configuration**, fill in:

| Field | Required | Value |
| --- | --- | --- |
| `tenant_id` | yes | Entra (Azure AD) tenant ID (GUID) or a verified domain name. |
| `client_id` | yes | App registration Application (client) ID. |
| `client_secret` | yes | Reference to the secret from step 4, for example `hive://secret/msft-response-client-secret`. |
| `login_base_url` | no | OAuth endpoint override for sovereign clouds. Default `https://login.microsoftonline.com`. |
| `graph_base_url` | no | Microsoft Graph base override. Default `https://graph.microsoft.com/v1.0`. |
| `defender_base_url` | no | Defender for Endpoint base override. Default `https://api.securitycenter.microsoft.com/api`. |

The three base-URL overrides support sovereign clouds (US Government GCC High / DoD, China 21Vianet). Leave them empty for the public cloud.

## Actions

Every action that targets an entity needs an explicit selector (`user_id`, `device_id`, `machine_id`, …). The extension does not run without one. This stops accidental containment of the full fleet.

### Common list parameters

The `list_*` actions share an OData query schema and return `{data: [...], pagination: {next_link}}`:

| Field | Type | Notes |
| --- | --- | --- |
| `filter` | string | OData `$filter`, for example `accountEnabled eq false`. |
| `select` | string | OData `$select`. Fields are separated by commas. |
| `search` | string | Free-text `$search`, for example `displayName:alex` (Graph sets `ConsistencyLevel: eventual` automatically). |
| `order_by` | string | OData `$orderby`, for example `createdDateTime desc`. |
| `top` | int | Page size, default `100`, clamped to `999`. |
| `count` | bool | Request a `$count`. |
| `next_link` | string | Opaque `@odata.nextLink` from a previous response. Pass it back to get the next page. |
| `extra_query` | object | Raw query parameters merged into the request, for parameters that the fields above do not cover. |

### Generic

#### `api_call`

Generic passthrough to Graph or Defender for Endpoint.

| Field | Type | Notes |
| --- | --- | --- |
| `service` | enum | `graph` (default) or `defender`. The token audience is handled automatically. |
| `method` | enum | `GET` (default), `POST`, `PATCH`, `PUT`, `DELETE`. |
| `path` | string | **Required.** Path relative to the service base (for example `users/{id}/revokeSignInSessions`) or a full `@odata.nextLink` URL. |
| `query` | object | Query-string parameters (`$filter`, `$select`, `$top`, …). |
| `headers` | object | Extra request headers, for example `{"ConsistencyLevel": "eventual"}`. |
| `body` | object | JSON body for `POST`/`PATCH`/`PUT`. Defender bodies use PascalCase keys (`IsolationType`, `Comment`, …). |

### Entra ID identities

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_users` | common list params | List users or search users. To read `accountEnabled`, add it to `select`; it is not returned by default. |
| `get_user` | `user_id`, `select` | Get one user. Defaults to an investigation-oriented `$select` (`accountEnabled`, `createdDateTime`, `lastPasswordChangeDateTime`, `signInSessionsValidFromDateTime`, `proxyAddresses`, `otherMails`, ...). |
| `disable_user` | `user_id` | Set `accountEnabled=false`. This blocks new sign-ins immediately. To reverse it, use `enable_user`. |
| `enable_user` | `user_id` | Enable a disabled user again. |
| `revoke_sign_in_sessions` | `user_id` | Invalidate all refresh tokens and sessions. The user must authenticate again everywhere. Full propagation takes a few minutes. |
| `reset_user_password` | `user_id`, `password`, `force_change_password_next_sign_in` (default `true`) | Set a new password with `passwordProfile`. Needs a directory role (see Setup). |
| `list_auth_methods` | `user_id` | List the registered authentication methods. Use it to find MFA that an attacker registered. |
| `list_user_groups` | `user_id` + common list params | List the groups, directory roles, and administrative units that the user is a direct member of. Use it to check if a compromised user holds privileged roles. |

`user_id` accepts either the user object ID (GUID) or the userPrincipalName (UPN).

For full account containment, combine `disable_user` with `revoke_sign_in_sessions`. `disable_user` blocks new sign-ins, and `revoke_sign_in_sessions` ends the existing sessions.

### Identity Protection (Entra ID P2)

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_risky_users` | common list params | Users flagged by Identity Protection (`riskLevel`, `riskState`, `riskDetail`). |
| `get_user_risk` | `user_id` | The riskyUser record of one user. Accepts a GUID or a UPN; a UPN needs one more lookup. A `404` means that the user has no risk record. |
| `list_risk_detections` | common list params | Individual risk detections (`riskEventType` such as `passwordSpray`, `impossibleTravel`, `leakedCredentials`; `ipAddress`, `location`, `detectedDateTime`). On a P1 tenant, premium detections show as `riskEventType=generic`. The page size caps at 500. |
| `confirm_user_compromised` | `user_ids` (list of GUIDs) | Mark users as confirmed-compromised. This raises the risk to high and drives risk-based Conditional Access. |
| `dismiss_user_risk` | `user_ids` (list of GUIDs) | Clear the risk on users. Maximum 60 for each call. |

### Directory & audit reads

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_groups` | common list params | List groups, for example to find a quarantine group or a privileged group. |
| `get_group` | `group_id`, `select` | Get one group by object id. |
| `list_group_members` | `group_id` + common list params | List the direct members of a group. Use it to enumerate the members of a privileged group. |
| `list_sign_ins` | common list params | Entra sign-in events. Always scope with a `createdDateTime` filter. |
| `get_signin_history` | `user_id`, `days` (default 7), `filter`, `top`, `next_link` | The sign-ins of one user over a trailing window, newest first. The action builds the `$filter` for you (GUID → `userId`, otherwise `userPrincipalName`). Your `filter` is AND-ed on top, for example `status/errorCode eq 0`. Key fields: `createdDateTime`, `ipAddress`, `location`, `deviceDetail`, `status.errorCode`, `riskLevelDuringSignIn`. |
| `list_directory_audits` | common list params | Directory audit log. It shows who changed what. |

### Microsoft Defender XDR (Graph security API)

Cross-product alerts and incidents from Defender for Endpoint / Office 365 / Identity / Cloud Apps, Entra ID Protection, and Sentinel. The enum values here are **camelCase** (`new`, `inProgress`, `resolved`). The Defender for Endpoint API below uses a different form.

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_security_alerts` | `filter`, `top`, `next_link`, `extra_query` | List XDR alerts (`security/alerts_v2`). You can filter on `createdDateTime`, `severity`, `status`, `serviceSource`, `classification`, `determination`, and `assignedTo`. Each alert contains its evidence. |
| `get_security_alert` | `alert_id` | One XDR alert with evidence (devices, files, processes, IPs, users), MITRE techniques, comments. |
| `update_security_alert` | `alert_id`, `status`, `classification`, `determination`, `assigned_to` | Triage an alert. Only the fields that you give change. Returns the updated alert. |
| `add_security_alert_comment` | `alert_id`, `comment` | Append a comment, for example to record the automated response. Returns the full comment list of the alert. |
| `list_security_incidents` | `filter`, `top`, `next_link`, `extra_query` | List XDR incidents. Add `extra_query: {"$expand": "alerts"}` to embed the alerts of each incident. |
| `get_security_incident` | `incident_id` | One incident (numeric-string id, for example `"29"`). |
| `update_security_incident` | `incident_id`, `status` (`active`/`resolved`/`redirected`), `classification`, `determination`, `assigned_to`, `resolving_comment`, `custom_tags` | Triage an incident. `custom_tags` **replaces** the tag list (an explicit empty list clears it). |
| `run_hunting_query` | `query`, `timespan` | Run a KQL query against the XDR advanced-hunting tables. Returns `{schema, results}`. The default lookback is 30 days, and the maximum is 100,000 rows. |

### Group containment

| Action | Parameters | What it does |
| --- | --- | --- |
| `add_group_member` | `group_id`, `user_id` | Add a user to a group, for example to put a compromised user into a Conditional-Access block or quarantine group. |
| `remove_group_member` | `group_id`, `user_id` | Remove a user from a group, for example to take a compromised user out of a privileged group. |

### Intune devices

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_managed_devices` | common list params | List Intune-managed devices (`deviceName`, `complianceState`, `userPrincipalName`, …). |
| `get_managed_device` | `device_id`, `select` | Get one managed device (`osVersion`, `isEncrypted`, `lastSyncDateTime`, `azureADDeviceId`, …). |
| `wipe_device` | `device_id`, `keep_enrollment_data`, `keep_user_data`, `data` | Factory-reset a device. **Destructive.** |
| `retire_device` | `device_id` | Remove the company data and the MDM policies. The personal data stays. |
| `remote_lock_device` | `device_id` | Remote-lock the device. |
| `reset_device_passcode` | `device_id` | Reset the device passcode. |
| `reboot_device` | `device_id` | Immediate reboot. |

`device_id` is the Intune `managedDevice` id from `list_managed_devices`.

### Defender for Endpoint investigation

Read-side actions against the Defender for Endpoint API. The enum values here are **PascalCase** (`New`, `InProgress`, `Resolved`). The Graph security API above uses a different form.

| Action | Parameters | What it does |
| --- | --- | --- |
| `get_machine` | `machine_id` | One machine (`computerDnsName`, `lastIpAddress`, `lastExternalIpAddress`, `healthStatus`, `riskScore`, `exposureLevel`, `machineTags`). |
| `find_machines_by_ip` | `ip`, `timestamp` (default now) | Machines seen with an **internal** IP within ±15 minutes of the timestamp (last 30 days only). |
| `list_alerts` | `filter`, `top`, `next_link`, `extra_query` | List Defender for Endpoint alerts. You can filter on `alertCreationTime`, `status`, `severity`, `category`, `detectionSource`, and `machineId`. Add `extra_query: {"$expand": "evidence"}` to embed evidence. |
| `get_alert` | `alert_id` | One alert (`title`, `severity`, `status`, `machineId`, `relatedUser`, `comments`, `mitreTechniques`). |
| `update_alert` | `alert_id`, `status`, `classification`, `determination`, `assigned_to`, `comment` | Triage an alert, add a comment, or do both. Only the fields that you give change. |
| `list_machine_alerts` | `machine_id` | All alerts related to one machine. |
| `list_machine_logon_users` | `machine_id` | The users that Defender saw log on to the machine (`accountName`, `firstSeen`/`lastSeen`, `logonTypes`, `isDomainAdmin`). Use it to find who else can be compromised. |
| `get_file_info` | `file_hash` (SHA1 or SHA256) | The file profile from Defender: `globalPrevalence`, `signer`/`issuer`, `isValidCertificate`, `determinationType`/`determinationValue`. |
| `list_file_machines` | `sha1` | The machines where a file was seen. Use it to find how far the file spread. **SHA1 only**; an unknown hash returns an empty list. |
| `list_file_alerts` | `sha1` | Alerts related to a file. **SHA1 only**. |
| `run_advanced_query` | `query` | Run a KQL query against the Defender for Endpoint hunting tables. Returns `{Schema, Results}`. The window is 30 days, and the maximum is 100,000 rows. For cross-product tables, use `run_hunting_query`. |
| `list_indicators` | `filter`, `top`, `next_link`, `extra_query` | The custom indicators (IoCs) of the tenant. Use a returned `id` with `delete_indicator`. |

### Defender for Endpoint machines

Machine actions are **asynchronous**. They return a `machineAction` object with `status: Pending`, and the work completes in the background. Poll with `get_machine_action` until the status is `Succeeded` or `Failed`. Each action takes an optional `comment` that goes into the Defender action audit; the default is `Automated response via LimaCharlie`. Each action also takes an optional `data` object that is merged into the payload.

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_machines` | common list params | List Defender machines (`computerDnsName`, `riskScore`, `exposureLevel`, …). |
| `isolate_machine` | `machine_id`, `isolation_type` (`Full` default, or `Selective`) | Isolate a machine from the network. `Selective` keeps Teams and Outlook operational. |
| `unisolate_machine` | `machine_id` | Release from isolation. |
| `run_antivirus_scan` | `machine_id`, `scan_type` (`Quick` default, or `Full`) | Trigger a Defender AV scan. |
| `restrict_app_execution` | `machine_id` | Let only Microsoft-signed binaries run. |
| `unrestrict_app_execution` | `machine_id` | Remove the execution restriction. |
| `collect_investigation_package` | `machine_id` | Collect a forensics package. |
| `stop_and_quarantine_file` | `machine_id`, `sha1` | Stop the running instances of a file (by SHA-1) and quarantine it. |
| `list_machine_actions` | common list params | The audit and queue of response actions. |
| `get_machine_action` | `action_id` | Poll the status of one machine action (`Pending` / `InProgress` / `Succeeded` / `Failed`). |
| `get_investigation_package_uri` | `action_id` | Short-lived SAS download URL for a **succeeded** `collect_investigation_package` action. A `404` usually means that the collection is not complete. The rate limit is 2 calls for each minute. |

### Custom indicators

#### `create_indicator`

Create a Defender custom threat indicator to block or alert on an IoC across the tenant.

| Field | Type | Notes |
| --- | --- | --- |
| `indicator_value` | string | **Required.** The IoC value. |
| `indicator_type` | enum | **Required.** `FileSha1`, `FileSha256`, `FileMd5`, `IpAddress`, `DomainName`, `Url`, `CertificateThumbprint`. |
| `action` | enum | **Required.** `Alert`, `Warn`, `Block`, `Audit`, `BlockAndRemediate`, `AlertAndBlock`, `Allowed`. |
| `title` | string | **Required.** Indicator title. |
| `description` | string | **Required.** Indicator description. |
| `severity` | enum | `Informational`, `Low`, `Medium` (default), `High`. |
| `expiration_time` | string | ISO-8601 UTC expiry; omit for no expiry. |
| `recommended_actions` | string | Recommended-actions text shown with the alert. |
| `generate_alert` | bool | Generate an alert on match. **Required `true` when `action` is `Audit`.** |
| `data` | object | Extra fields merged into the payload, for example `rbacGroupNames`. |

#### `delete_indicator`

Delete one custom indicator by its `indicator_id`, for example to remove a block. The `indicator_id` comes from `list_indicators` or from the `create_indicator` response.

## Detection & Response

This example response action isolates the Defender machine that a detection names:

```yaml
- action: extension request
  extension action: isolate_machine
  extension name: ext-microsoft-response
  extension request:
    machine_id: '{{ .event/machine_id }}'
    isolation_type: '{{ "Full" }}'
    comment: '{{ "Isolated by LimaCharlie D&R rule" }}'
```

> **Wrap literal strings in `{{ "..." }}`.**
> The values under `extension request` are evaluated as templates. A bare string without `{{ }}` is read as a [gjson](https://github.com/tidwall/gjson) path into the event. If the path does not resolve, the key is dropped from the payload without a message.

`extension request` actions do not return a result. The rule engine does not put the response into the evaluation context of the rule. A `machineAction` id is therefore not available to a later action in the same rule. A workflow that chains steps (look up the machine, isolate it, poll the action, collect forensics) belongs in a [Playbook](../limacharlie/playbook.md) or in an AI agent. A Playbook or an AI agent can hold ids between calls.

## Notes

- The extension gives two surfaces for alerts and hunting on purpose. The **Graph security API** actions (`*_security_alert`, `*_security_incident`, `run_hunting_query`) cover all of Defender XDR and use camelCase enums. The **Defender for Endpoint API** actions (`list_alerts`, `get_alert`, `update_alert`, `run_advanced_query`) cover endpoints only. They use PascalCase enums and machine-centric fields (`machineId`, `computerDnsName`).
- Graph and Defender use **separate token audiences**. The extension caches one token for each service and renews it before it expires. If the other service rejects a token, the result is a `403`, not a `401`.
- One `401` is treated as a race with the token expiry. The cached token is dropped, and the request runs one more time with a new token. A rotation of `client_secret` in Secrets Manager recovers in the same way. The next authentication failure evicts the cached client and reads the secret again.
- The extension does **not** retry Microsoft Graph throttling (`429`). A throttled request goes back to the caller.
- Error messages are formatted `microsoft <service> api <status> on <path>: <code>: <message>`, with query strings redacted.
- If you unsubscribe from the extension, its saved configuration stays. If you subscribe again, the configuration returns and you do not configure it again.
