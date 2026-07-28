# ThreatLocker

[ThreatLocker](https://threatlocker.com) is an Application Control platform. Its **approval-request queue** is the largest source of manual work in a rollout. In this queue, end users ask for permission to run an unknown binary.

The ThreatLocker LimaCharlie Extension is a thin proxy over the [ThreatLocker Portal API](https://portalapi.g.threatlocker.com/swagger). It works with the [ThreatLocker adapter](../../../2-sensors-deployment/adapters/types/threatlocker.md), which delivers approval-request events into LimaCharlie.

An AI agent or a Playbook reads each event and calls this extension to enrich the event against the Portal API. The enrichment matches the built-in app, the computer and group context, and the existing policies. The agent then calls this extension again with the decision: **permit**, **reject**, or **ignore**. The extension makes no decisions. It forwards the JSON body verbatim and returns the Portal response verbatim.

## Setup

### 1. Create a Portal API token

In the ThreatLocker Portal, go to **Administration → API Users** and create a new API user. Copy the **API token**. You need the token in the next step. ThreatLocker shows the token one time only.

### 2. Find your instance letter

ThreatLocker hosts each tenant on a lettered instance (`b`, `c`, `d`, …, `g`, `h`, …). An API token is scoped to the instance that made it. To find your letter, click the **Help** button in the top-right corner of any Portal page. Read the letter in parentheses next to **ThreatLocker Access**. For example, `ThreatLocker Access (G)` gives `instance_letter: g`.

> ⚠️ **A token from one instance returns `403 TOKEN_REVOKED` on every other instance.** The API does not show a difference between a wrong instance and a revoked token. If you are sure that the token is active but you still see `TOKEN_REVOKED`, check the instance letter. Check it before you decide that the token is revoked.

### 3. Subscribe to the extension

Subscribe to `ext-threatlocker` from the LimaCharlie **Marketplace** (Extensions → Add-Ons).

### 4. Store the API token

In **Secrets Manager**, create a new secret (for example `threatlocker-api-token`) and paste the Portal API token as its value.

### 5. Configure the extension

In **Extensions → ext-threatlocker → Configuration**, fill in:

| Field | Required | Value |
| --- | --- | --- |
| `api_token` | yes | Reference to the secret that you created in step 4, for example `hive://secret/threatlocker-api-token`. |
| `instance_letter` | yes | The one lowercase letter from step 2, for example `g`. |
| `managed_organization_id` | no | UUID of the managed (child) organization. The extension sends it as the `ManagedOrganizationId` header. MSP **parent** tokens use it to scope each call to one child tenant. |

The extension sends the API token **verbatim** in the `Authorization` header. There is no `Bearer` prefix and no OAuth flow. The extension validates the instance letter when you save. The Portal API rejects all other bad values at request time.

## Actions

The extension gives thirteen actions. Each `POST` action takes one `body` parameter — the JSON object that the extension forwards verbatim as the request body for the Portal API. `GET` actions take typed parameters: an `id` for single-id endpoints, or named flags for the computer-group inspector.

The extension does **not** shadow the set of body fields for each endpoint. The Portal API is large and changes with time, so the extension does not constrain the body. For the exact set of fields for each endpoint, see the ThreatLocker Portal Swagger spec at `https://portalapi.<instance>.threatlocker.com/swagger`.

### Approval-request reads

#### `approval_request_search`

`POST ApprovalRequest/ApprovalRequestGetByParameters` — list the approval requests that match a filter.

| Field | Type | Notes |
| --- | --- | --- |
| `body` | object | **Required.** The extension forwards it as the JSON request body. Common fields: `statusId` (1=pending, 4=approved, …), `searchText`, `requestTypeId`, `actionType` (array), `pageNumber`, `pageSize`, `orderBy`, `isAscending`. |

#### `approval_request_get`

`GET ApprovalRequest/ApprovalRequestGetById` — fetch one approval request.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | **Required.** `approvalRequestId` (UUID). |

### Application reads

#### `application_get_matching`

`POST Application/ApplicationGetMatchingList` — the **primary enrichment call**. For a file (`sha256`, path, certificates, …), it returns the built-in or custom ThreatLocker applications that the file matches. An empty result means that there is no built-in match. The file is then unknown to the curated catalog of ThreatLocker, and an AI policy decision must give weight to this fact.

| Field | Type | Notes |
| --- | --- | --- |
| `body` | object | **Required.** Common fields: `sha256`, `hash`, `path`, `certs`, `organizationIds`, `osType`, `approvalRequestId`. |

#### `application_get`

`GET Application/ApplicationGetById` — full details for one application.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | **Required.** `applicationId` (UUID). |

#### `application_get_research`

`GET Application/ApplicationGetResearchDetailsById` — the curated threat-research information from ThreatLocker for an application (Living-Off-The-Land flags, common abuse, reputation notes). Use it when you decide if the matched application is sensitive enough to reject.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | **Required.** `applicationId` (UUID). |

### Computer reads

#### `computer_get`

`GET Computer/ComputerGetForEditById` — fetch the full record of one computer (group, OS, tags, last check-in). This is the fastest path from the `computerId` in an approval-request event to the device context.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | **Required.** `computerId` (UUID). |

#### `computer_search`

`POST Computer/ComputerGetByAllParameters` — computer search by free text, or scoped by group or mode.

| Field | Type | Notes |
| --- | --- | --- |
| `body` | object | **Required.** Common fields: `searchText`, `computerGroup`, `computerId`, `action`, `kindOfAction`, `showLastCheckIn`, `showDeleted`, `childOrganizations`, `pageNumber`, `pageSize`, `orderBy`, `isAscending`, `searchBy`. |

### Computer-group reads

#### `computer_group_list_for_permit`

`GET ComputerGroup/ComputerGroupGetForPermitApplication` — list the computer groups that can receive an approval or permit decision. Start with this action when you select the scope for a new permit policy.

| Field | Type | Notes |
| --- | --- | --- |
| `os_type` | int | `0` = All (default), `1` = Windows, `2` = Mac, `3` = Linux. |

#### `computer_group_get_full`

`GET ComputerGroup/ComputerGroupGetGroupAndComputer` — one-call inspector. It returns a group and, optionally, each policy attached to the group and each computer in the group, in one round trip.

| Field | Type | Notes |
| --- | --- | --- |
| `computer_group_id` | string | **Required.** `ComputerGroupId` (UUID). |
| `os_type` | int | `0` = All, `1` = Windows, `2` = Mac, `3` = Linux. |
| `include_all_policies` | bool | Include the policies attached to the group. **Recommended** — the default is `true`. |
| `include_all_computers` | bool | Include the computers in the group. **Recommended** — the default is `true`. |
| `include_global` | bool | Include the global "All Computers" group. |
| `include_organizations` | bool | Include parent and child orgs. |
| `include_parent_groups` | bool | Include parent groups. |
| `include_logged_in_objects` | bool | Include logged-in objects. |
| `include_access_devices` | bool | Include access devices. |
| `include_removed_computers` | bool | Include removed computers. |
| `portal_module_type_id` | int | Optional `PortalModuleTypeId`. |

Set `include_all_policies=true` and `include_all_computers=true` to get the full group context in one call. The response shows the other computers in the group and the policies that are already attached. Use it to find a conflict between those policies and a new permit policy.

### Policy reads

#### `policy_get`

`GET Policy/PolicyGetById` — fetch the full record of one policy by id. The Portal API has no endpoint that lists policies by parameters. Instead, call `computer_group_get_full` with `include_all_policies=true`, then resolve each policy by id with `policy_get`.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | **Required.** `policyId` (UUID). |

### Decisions

The three write actions complete an approval request. They are the only actions in this extension that change the state of ThreatLocker.

#### `approval_request_permit`

`POST ApprovalRequest/ApprovalRequestPermitApplication` — **approve**. It creates or updates a permit policy and lets the blocked application of the requestor run.

| Field | Type | Notes |
| --- | --- | --- |
| `body` | object | **Required.** The full `PermitApplicationDto` body. Set `body.adminNotes` to the reasoning of the AI. The value goes into the Portal audit trail, so a person can later find *why* an automated decision was made. |

#### `approval_request_reject`

`POST ApprovalRequest/ApprovalRequestUpdateForReject` — **deny**. It sends a reason to the requestor.

| Field | Type | Notes |
| --- | --- | --- |
| `body` | object | **Required.** Set `body.rejectReason` (the message that the requestor sees) and `body.responseReason` (the internal note for the audit trail). |

#### `approval_request_ignore`

`POST ApprovalRequest/ApprovalRequestUpdateForIgnore` — **soft-dismiss**. It keeps the request in the queue for human review and does not notify the requestor. Use this action when the AI cannot permit or reject with confidence.

| Field | Type | Notes |
| --- | --- | --- |
| `body` | object | **Required.** The extension forwards it as the JSON request body. |

## Detection & Response

This example response action enriches a ThreatLocker approval-request event that the [ThreatLocker adapter](../../../2-sensors-deployment/adapters/types/threatlocker.md) delivers. It calls `application_get_matching` with the SHA-256 hash of the file:

```yaml
- action: extension request
  extension action: application_get_matching
  extension name: ext-threatlocker
  extension request:
    body:
      sha256: '{{ .event/hash }}'
      osType: 1
      approvalRequestId: '{{ .event/approvalRequestId }}'
```

> **Wrap literal strings in `{{ "..." }}`.**
> Values under `extension request` are evaluated as templates. A bare string without `{{ }}` is read as a [gjson](https://github.com/tidwall/gjson) path into the event. If the path does not resolve, the key is removed from the payload without a message.

`extension request` actions do not return a result to the rule. The rule engine does not put the response into the evaluation context of the rule. Thus the enrichment result is not available to a later action in the same rule. For a chain of steps (enrich, decide, write back), use a [Playbook](../limacharlie/playbook.md) or an AI agent. These can hold the intermediate results between calls.

## Authentication and tenancy

- The extension sends the Portal API token **verbatim** in the `Authorization` header. There is no `Bearer` prefix. Do not add a prefix to the token, because the API rejects it.
- The token is scoped to the instance that made it. `403 TOKEN_REVOKED` means that the token was revoked **or** that the `instance_letter` is wrong. Check the instance letter first.
- For **MSPs**, one parent-tenant token can drive many child organizations. Set `managed_organization_id` to the UUID of the child organization. The extension then adds the `ManagedOrganizationId` header to each request, and the Portal scopes the response to that child. You need one extension subscription for each parent tenant, not for each child.

## Notes

- The extension caches the HTTP client for each `(org, instance_letter, token, managed_organization_id)`. When you rotate the secret in Secrets Manager, the extension removes the cached client at the next `403 TOKEN_REVOKED`.
- The extension does not transform the request or the response. The caller sees exactly what ThreatLocker returns. New Portal fields need no change to the code.
- You can retry read actions safely. Write actions (`approval_request_permit` / `_reject` / `_ignore`) are not idempotent in the Portal. If you send one again for the same `approvalRequestId` after the first success, the Portal returns an error.
