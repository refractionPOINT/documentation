# Microsoft Response

The Microsoft Response LimaCharlie Extension exposes the incident-response surface of Microsoft's cloud security platforms — **Microsoft Graph** (Entra ID identities, Identity Protection, groups, Intune devices, audit logs) and **Microsoft Defender for Endpoint** (machine isolation, scans, forensics, file quarantine, custom indicators) — to D&R rules and AI agents. It enables automated containment of account and endpoint compromise directly from detections.

The extension provides two layers:

- **Typed actions** for the common containment and triage workflows, with friendly parameter names and built-in safety rails.
- A generic **`api_call`** passthrough for any Graph or Defender endpoint not covered by a typed action.

Authentication is OAuth2 **client credentials** against an Entra app registration — no user interaction, no delegated tokens.

## Setup

### 1. Create an Entra app registration

In the Azure portal (**Entra ID → App registrations → New registration**), create an app registration and note its **Application (client) ID** and your **Directory (tenant) ID**. Create a **client secret** under *Certificates & secrets*.

### 2. Grant application permissions

Under *API permissions*, add **application** permissions (not delegated) and grant **admin consent**. The least-privilege set per capability:

| Capability | Permission | API |
| --- | --- | --- |
| List/read users | `User.Read.All` | Microsoft Graph |
| Disable / enable account | `User.EnableDisableAccount.All` | Microsoft Graph |
| Revoke sign-in sessions | `User.RevokeSessions.All` | Microsoft Graph |
| Reset password | `User-PasswordProfile.ReadWrite.All` | Microsoft Graph |
| List authentication methods | `UserAuthenticationMethod.Read.All` | Microsoft Graph |
| Risky users (read / confirm / dismiss) | `IdentityRiskyUser.ReadWrite.All` | Microsoft Graph |
| Groups read / membership change | `GroupMember.ReadWrite.All` | Microsoft Graph |
| Sign-in & directory audit logs | `AuditLog.Read.All` | Microsoft Graph |
| Intune device actions | `DeviceManagementManagedDevices.PrivilegedOperations.All` (+ `DeviceManagementManagedDevices.Read.All` to list) | Microsoft Graph |
| Machine isolation | `Machine.Isolate` | WindowsDefenderATP |
| Antivirus scan | `Machine.Scan` | WindowsDefenderATP |
| Restrict app execution | `Machine.RestrictExecution` | WindowsDefenderATP |
| Collect investigation package | `Machine.CollectForensics` | WindowsDefenderATP |
| Stop & quarantine file | `Machine.StopAndQuarantine` | WindowsDefenderATP |
| List machines / machine actions | `Machine.ReadWrite.All` | WindowsDefenderATP |
| Custom indicators (IoCs) | `Ti.ReadWrite.All` | WindowsDefenderATP |

Only add what you will use — every action degrades independently with a `403` if its permission is missing.

> **Privileged user writes need a directory role too.** For `disable_user`, `enable_user`, and `reset_user_password`, Graph permissions alone are not sufficient: the app's service principal must also hold an Entra **directory role** (e.g. *User Administrator*) covering the target user. A `403` on these actions is a consent/role problem, not a bug.
>
> **Identity Protection requires Entra ID P2.** `list_risky_users`, `confirm_user_compromised`, and `dismiss_user_risk` return `403` on tenants without a P2 license.

### 3. Subscribe to the extension

Subscribe to `ext-microsoft-response` from the LimaCharlie **Marketplace** (Extensions → Add-Ons).

### 4. Store the client secret

In **Secrets Manager**, create a new secret (for example `msft-response-client-secret`) and paste the client secret as its value.

### 5. Configure the extension

In **Extensions → ext-microsoft-response → Configuration**, fill in:

| Field | Required | Value |
| --- | --- | --- |
| `tenant_id` | yes | Entra (Azure AD) tenant ID (GUID) or a verified domain name. |
| `client_id` | yes | App registration Application (client) ID. |
| `client_secret` | yes | Reference to the secret created in step 4, e.g. `hive://secret/msft-response-client-secret`. |
| `login_base_url` | no | OAuth endpoint override for sovereign clouds. Default `https://login.microsoftonline.com`. |
| `graph_base_url` | no | Microsoft Graph base override. Default `https://graph.microsoft.com/v1.0`. |
| `defender_base_url` | no | Defender for Endpoint base override. Default `https://api.securitycenter.microsoft.com/api`. |

The three base-URL overrides support sovereign clouds (US Government GCC High / DoD, China 21Vianet); leave them empty for the public cloud.

## Actions

Every action that targets an entity requires an explicit selector (`user_id`, `device_id`, `machine_id`, …) — the extension refuses to run without one, preventing accidental fleet-wide containment.

### Common list parameters

The `list_*` actions share an OData query schema and return `{data: [...], pagination: {next_link}}`:

| Field | Type | Notes |
| --- | --- | --- |
| `filter` | string | OData `$filter`, e.g. `accountEnabled eq false`. |
| `select` | string | OData `$select` — comma-separated fields. |
| `search` | string | Free-text `$search`, e.g. `displayName:alex` (Graph sets `ConsistencyLevel: eventual` automatically). |
| `order_by` | string | OData `$orderby`, e.g. `createdDateTime desc`. |
| `top` | int | Page size, default `100`, clamped to `999`. |
| `count` | bool | Request a `$count`. |
| `next_link` | string | Opaque `@odata.nextLink` from a previous response — pass it back to fetch the next page. |
| `extra_query` | object | Raw query params merged into the request (escape hatch). |

### Generic

#### `api_call`

Generic passthrough to Graph or Defender for Endpoint.

| Field | Type | Notes |
| --- | --- | --- |
| `service` | enum | `graph` (default) or `defender`. Token audience is handled automatically. |
| `method` | enum | **Required.** `GET`, `POST`, `PATCH`, `PUT`, `DELETE`. |
| `path` | string | **Required.** Path relative to the service base (e.g. `users/{id}/revokeSignInSessions`) or a full `@odata.nextLink` URL. |
| `query` | object | Query-string parameters (`$filter`, `$select`, `$top`, …). |
| `headers` | object | Extra request headers, e.g. `{"ConsistencyLevel": "eventual"}`. |
| `body` | object | JSON body for `POST`/`PATCH`/`PUT`. Note Defender bodies use PascalCase keys (`IsolationType`, `Comment`, …). |

### Entra ID identities

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_users` | common list params | List/search users. Add `accountEnabled` to `select` to read it (not returned by default). |
| `disable_user` | `user_id` | Set `accountEnabled=false` — blocks new sign-ins immediately. Reverse with `enable_user`. |
| `enable_user` | `user_id` | Re-enable a disabled user. |
| `revoke_sign_in_sessions` | `user_id` | Invalidate all refresh tokens / sessions, forcing re-authentication everywhere. Takes a few minutes to fully propagate. |
| `reset_user_password` | `user_id`, `password`, `force_change_password_next_sign_in` (default `true`) | Set a new password via `passwordProfile`. Requires a directory role (see Setup). |
| `list_auth_methods` | `user_id` | List registered authentication methods — spot attacker-registered MFA. |

`user_id` accepts either the user object ID (GUID) or the userPrincipalName (UPN).

For full account containment, combine `disable_user` with `revoke_sign_in_sessions`: disabling blocks new sign-ins, revoking kills existing sessions.

### Identity Protection (Entra ID P2)

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_risky_users` | common list params | Users flagged by Identity Protection (`riskLevel`, `riskState`, `riskDetail`). |
| `confirm_user_compromised` | `user_ids` (list of GUIDs) | Mark users confirmed-compromised, raising risk to high (drives risk-based Conditional Access). |
| `dismiss_user_risk` | `user_ids` (list of GUIDs) | Clear the risk on users. Max 60 per call. |

### Directory & audit reads

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_groups` | common list params | List groups (e.g. find a quarantine or privileged group). |
| `list_sign_ins` | common list params | Entra sign-in events. Always scope with a `createdDateTime` filter. |
| `list_directory_audits` | common list params | Directory audit log — who changed what. |

### Group containment

| Action | Parameters | What it does |
| --- | --- | --- |
| `add_group_member` | `group_id`, `user_id` | Add a user to a group — e.g. drop a compromised user into a Conditional-Access block/quarantine group. |
| `remove_group_member` | `group_id`, `user_id` | Remove a user from a group — e.g. strip a compromised user out of a privileged group. |

### Intune devices

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_managed_devices` | common list params | List Intune-managed devices (`deviceName`, `complianceState`, `userPrincipalName`, …). |
| `wipe_device` | `device_id`, `keep_enrollment_data`, `keep_user_data`, `data` | Factory-reset a device. **Destructive.** |
| `retire_device` | `device_id` | Remove company data and MDM policies, leave personal data. |
| `remote_lock_device` | `device_id` | Remote-lock the device. |
| `reset_device_passcode` | `device_id` | Reset the device passcode. |
| `reboot_device` | `device_id` | Immediate reboot. |

`device_id` is the Intune `managedDevice` id from `list_managed_devices`.

### Defender for Endpoint machines

Machine actions are **asynchronous**: they return a `machineAction` object with `status: Pending`, and the work completes in the background. Poll with `get_machine_action` until `Succeeded` / `Failed`. All take an optional `comment` recorded in the Defender action audit (default `Automated response via LimaCharlie`) and an optional `data` object merged into the payload.

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_machines` | common list params | List Defender machines (`computerDnsName`, `riskScore`, `exposureLevel`, …). |
| `isolate_machine` | `machine_id`, `isolation_type` (`Full` default, or `Selective`) | Network-isolate a machine. `Selective` keeps Teams/Outlook working. |
| `unisolate_machine` | `machine_id` | Release from isolation. |
| `run_antivirus_scan` | `machine_id`, `scan_type` (`Quick` default, or `Full`) | Trigger a Defender AV scan. |
| `restrict_app_execution` | `machine_id` | Only Microsoft-signed binaries may run. |
| `unrestrict_app_execution` | `machine_id` | Remove the execution restriction. |
| `collect_investigation_package` | `machine_id` | Collect a forensics package; fetch the download URL via `get_machine_action` once complete. |
| `stop_and_quarantine_file` | `machine_id`, `sha1` | Stop running instances of a file (by SHA-1) and quarantine it. |
| `list_machine_actions` | common list params | The response-action audit/queue. |
| `get_machine_action` | `action_id` | Poll one machine action's status (`Pending` / `InProgress` / `Succeeded` / `Failed`). |

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
| `data` | object | Extra fields merged into the payload (e.g. `rbacGroupNames`). |

## Detection & Response

Example response action that isolates the Defender machine named in a detection:

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
> Values under `extension request` are evaluated as templates. A bare string without `{{ }}` is interpreted as a [gjson](https://github.com/tidwall/gjson) path against the event and, if it doesn't resolve, the key is silently dropped from the payload.

`extension request` actions are fire-and-forget — the rule engine does not surface the response back into the rule's evaluation context, so a `machineAction` id is not available to a subsequent action in the same rule. Workflows that chain (look up the machine, isolate it, poll the action, collect forensics) belong in a [Playbook](../limacharlie/playbook.md) or an AI agent, which can hold ids between calls.

## Notes

- Graph and Defender use **separate token audiences**; the extension caches one token per service and renews it before expiry. A token rejected by the other service surfaces as `403`, not `401`.
- A single `401` is treated as a token-expiry race: the cached token is dropped and the request retried once with a fresh token. Rotating `client_secret` in Secrets Manager recovers the same way — the next auth failure evicts the cached client and re-reads the secret.
- Microsoft Graph throttling (`429`) is **not** retried by the extension; throttled requests surface to the caller.
- Error messages are formatted `microsoft <service> api <status> on <path>: <code>: <message>`, with query strings redacted.
- Unsubscribing from the extension preserves its saved configuration; re-subscribing restores it without reconfiguration.
