# SentinelOne

[SentinelOne](https://www.sentinelone.com/) is an endpoint protection (EDR/XDR) platform. Its Management REST API drives agents (endpoints), threats, and the tenant's site/account/group inventory.

The SentinelOne LimaCharlie Extension exposes that API to D&R rules and AI agents — both as typed high-level actions for the common EDR/SecOps flows (triage and mitigate threats, isolate/scan endpoints, set verdict and incident status, record notes, blocklist hashes, read inventory) and as a generic `api_call` passthrough that reaches the entire API.

It pairs naturally with the [SentinelOne adapter](../../../2-sensors-deployment/adapters/types/sentinelone.md): the adapter streams SentinelOne activities, threats, and alerts **into** LimaCharlie, and this extension provides the write-back actions an AI agent (or a Playbook) calls to act on them.

## Setup

### 1. Create a SentinelOne API token

In the SentinelOne console, create a **Service User** (Settings → Users → Service Users) scoped to the sites/accounts the extension should manage, and generate its **API token**. A Service User token is API-only with a configurable expiry — prefer it over a 30-day user token, which expires quickly and carries a human's full permissions.

Note your **management console URL** (e.g. `https://usea1-partners.sentinelone.net`) — you'll need it in the configuration step.

### 2. Subscribe to the extension

Subscribe to `ext-sentinelone` from the LimaCharlie **Marketplace** (Extensions → Add-Ons).

### 3. Store the API token

In **Secrets Manager**, create a new secret (for example `sentinelone-api-token`) and paste the SentinelOne API token as its value.

### 4. Configure the extension

In **Extensions → ext-sentinelone → Configuration**, fill in:

| Field | Required | Value |
| --- | --- | --- |
| `console_url` | yes | Management console URL, e.g. `https://usea1-partners.sentinelone.net`. |
| `api_token` | yes | Reference to the secret created in step 3, e.g. `hive://secret/sentinelone-api-token`. |
| `api_version` | no | API version path segment. Defaults to `v2.1`. |

The token is sent as `Authorization: ApiToken <token>`. SentinelOne tokens are **not refreshable**, so a `401` is surfaced as a real auth failure. Rotating the token in the secret store and re-running recovers without a redeploy — the cached client is evicted on the next surfaced `401`.

## Actions

All actions accept a JSON request body when invoked from a D&R rule via `extension request`.

Every action that selects entities (isolate / scan / mitigate / verdict / incident / note) accepts a convenient list of ids **or** a raw `filter` object for advanced selection — and **refuses to run with no selector**, so a fleet-wide action can never fire by accident.

List actions return a stable `{data, pagination}` shape — see [Pagination](#pagination).

### Generic passthrough

#### `api_call`

Generic passthrough to the SentinelOne REST API. Use for any endpoint not covered by a typed action.

| Field | Type | Notes |
| --- | --- | --- |
| `method` | enum | **Required.** `GET` (default), `POST`, `PUT`, `DELETE`. |
| `path` | string | **Required.** Endpoint path relative to `/web/api/<version>` (e.g. `agents`, `threats/mitigate/kill`, `system/info`). |
| `query` | object | Query-string parameters as a flat object of string values. |
| `body` | object | JSON request body (for `POST`/`PUT`). Action endpoints expect `{filter:{...}, data:{...}}`. |

### Agents (endpoints)

#### `list_agents`

List/search agents with optional filters. Use the returned agent ids with `isolate_agent` / `scan_agent`.

| Field | Type | Notes |
| --- | --- | --- |
| `query` | string | Free-text search (computer name, IP, etc.). |
| `computer_name` | string | Filter by computer name (substring match). |
| `site_ids` | list of string | Restrict to site ids. |
| `group_ids` | list of string | Restrict to group ids. |
| `account_ids` | list of string | Restrict to account ids. |
| `uuid` | string | Filter by agent UUID. |
| `is_active` | bool | Only active (`true`) / inactive (`false`) agents. |
| `network_status` | enum | `connected`, `connecting`, `disconnected`, `disconnecting`. |
| `infected` | bool | Only agents with (`true`) / without (`false`) active threats. |
| `os_types` | list of string | `windows`, `linux`, `macos`, `windows_legacy`. |
| `limit` | int | Page size (1–1000, default 100). |
| `cursor` | string | Pagination cursor from a previous response. |
| `extra_query` | object | Raw query params merged into the request. |

#### `isolate_agent` / `deisolate_agent` / `scan_agent`

`isolate_agent` network-isolates (disconnects) the selected agents; `deisolate_agent` reverses it; `scan_agent` triggers an on-demand full-disk scan. All three take the same selector:

| Field | Type | Notes |
| --- | --- | --- |
| `agent_ids` | list of string | Agent ids to act on. |
| `filter` | object | Raw SentinelOne agent filter (advanced; alternative to `agent_ids`). |
| `data` | object | Extra fields merged into the action's `data` payload. |

### Threats

#### `list_threats`

List/search threats with optional filters. Use the returned threat ids with `mitigate_threat` / `set_threat_verdict` / `set_threat_incident` / `add_threat_note`.

| Field | Type | Notes |
| --- | --- | --- |
| `query` | string | Free-text search (file path, hash, computer name, …). |
| `content_hashes` | list of string | Filter by file content SHA1 hashes. |
| `mitigation_statuses` | list of string | `mitigated`, `active`, `blocked`, `suspicious`, … |
| `incident_statuses` | list of string | `unresolved`, `in_progress`, `resolved`. |
| `analyst_verdicts` | list of string | `true_positive`, `false_positive`, `suspicious`, `undefined`. |
| `classifications` | list of string | `Malware`, `PUA`, `Ransomware`, … |
| `site_ids` | list of string | Restrict to site ids. |
| `account_ids` | list of string | Restrict to account ids. |
| `created_at__gte` | string | Only threats created at/after this ISO-8601 UTC time. |
| `created_at__lte` | string | Only threats created at/before this ISO-8601 UTC time. |
| `resolved` | bool | Only resolved (`true`) / unresolved (`false`) threats. |
| `limit` | int | Page size (1–1000, default 100). |
| `cursor` | string | Pagination cursor from a previous response. |
| `extra_query` | object | Raw query params merged into the request. |

#### `mitigate_threat`

Apply a mitigation to the selected threats.

| Field | Type | Notes |
| --- | --- | --- |
| `action` | enum | **Required.** `kill`, `quarantine`, `remediate`, `rollback-remediation`, `un-quarantine`, `network-quarantine`. |
| `threat_ids` | list of string | Threat ids to mitigate. |
| `filter` | object | Raw SentinelOne threat filter (advanced; alternative to `threat_ids`). |
| `data` | object | Extra fields merged into the action's `data` payload. |

#### `set_threat_verdict`

Set the analyst verdict on the selected threats.

| Field | Type | Notes |
| --- | --- | --- |
| `verdict` | enum | **Required.** `true_positive`, `false_positive`, `suspicious`, `undefined`. |
| `threat_ids` | list of string | Threat ids. |
| `filter` | object | Raw threat filter (advanced; alternative to `threat_ids`). |

#### `set_threat_incident`

Set the incident status on the selected threats.

| Field | Type | Notes |
| --- | --- | --- |
| `status` | enum | **Required.** `unresolved`, `in_progress`, `resolved`. |
| `threat_ids` | list of string | Threat ids. |
| `filter` | object | Raw threat filter (advanced; alternative to `threat_ids`). |

#### `add_threat_note`

Append a note to the selected threats. Useful for AI agents to record triage findings.

| Field | Type | Notes |
| --- | --- | --- |
| `text` | string | **Required.** Note text. |
| `threat_ids` | list of string | Threat ids. |
| `filter` | object | Raw threat filter (advanced; alternative to `threat_ids`). |

### Blocklist

#### `blocklist_hash`

Add a SHA1 file hash to the SentinelOne blocklist (restrictions). Scope it to the whole tenant or to specific sites/groups/accounts.

| Field | Type | Notes |
| --- | --- | --- |
| `hash` | string | **Required.** SHA1 hash to block. |
| `os_type` | enum | **Required.** `windows`, `windows_legacy`, `macos`, `linux`. |
| `description` | string | Reason / description for the blocklist entry. |
| `tenant` | bool | Apply tenant-wide (global). If `false`, set `site_ids`/`group_ids`/`account_ids`. |
| `site_ids` | list of string | Scope to site ids. |
| `group_ids` | list of string | Scope to group ids. |
| `account_ids` | list of string | Scope to account ids. |
| `data` | object | Extra fields merged into the restriction's `data` payload. |

### Inventory and audit

#### `list_activities`

List activity-log events (audit trail).

| Field | Type | Notes |
| --- | --- | --- |
| `activity_types` | list of string | Numeric activity type codes (see `/activities/types`). |
| `agent_ids` | list of string | Filter by agent ids. |
| `site_ids` | list of string | Filter by site ids. |
| `created_at__gte` | string | Only events at/after this ISO-8601 UTC time. |
| `created_at__lte` | string | Only events at/before this ISO-8601 UTC time. |
| `limit` | int | Page size (1–1000, default 100). |
| `cursor` | string | Pagination cursor from a previous response. |
| `extra_query` | object | Raw query params merged into the request. |

#### `list_sites` / `list_accounts` / `list_groups`

List the sites, accounts, or groups in the tenant. All three take the same parameters:

| Field | Type | Notes |
| --- | --- | --- |
| `query` | string | Free-text search (name match). |
| `account_ids` | list of string | Restrict to account ids. |
| `site_ids` | list of string | Restrict to site ids. |
| `limit` | int | Page size (1–1000, default 100). |
| `cursor` | string | Pagination cursor from a previous response. |
| `extra_query` | object | Raw query params merged into the request. |

## Pagination

List endpoints return `{data, pagination: {nextCursor, totalItems}}`. The client caps `limit` at 1000 (default 100). The typed list actions return a single page plus the cursor; pass `cursor` back to fetch the next page.

> SentinelOne cursors are **not self-contained** — when paging, re-send the original filters on each page alongside the `cursor`.

## Detection & Response

Example response action that network-isolates the endpoint named in a detection:

```yaml
- action: extension request
  extension action: isolate_agent
  extension name: ext-sentinelone
  extension request:
    filter:
      computerName: '{{ .routing.hostname }}'
```

> **Wrap literal strings in `{{ "..." }}`.**
> Values under `extension request` are evaluated as templates. A bare string without `{{ }}` is interpreted as a [gjson](https://github.com/tidwall/gjson) path against the event and, if it doesn't resolve, the key is silently dropped from the payload.

`extension request` actions are fire-and-forget — the rule engine does not surface the response back into the rule's evaluation context, so a threat list returned by `list_threats` is not available to a subsequent action in the same rule. Workflows that chain (list → decide → mitigate) belong in a [Playbook](../limacharlie/playbook.md) or an AI agent, which can hold the intermediate results between calls.

## Notes

- Use a SentinelOne **Service User** token (API-only, configurable expiry) rather than a 30-day user token.
- Tokens are not refreshable: a `401` is a real auth failure. Rotating the secret in Secrets Manager evicts the cached client on the next surfaced `401`.
- Entity-selecting actions refuse to run with no selector (`*_ids` or `filter`) — there is no implicit "all".
- A few endpoint paths historically varied between API versions/tenants (e.g. `restart-machine` vs `reboot`). The typed actions cover the verified-stable flows; anything else is reachable via `api_call`. The `blocklist_hash` `restrictions` payload field names are confirmed against the XSOAR/Postman integrations but should be validated against a live tenant before heavy use.
