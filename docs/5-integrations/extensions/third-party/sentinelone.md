# SentinelOne

[SentinelOne](https://www.sentinelone.com/) is an endpoint protection platform. The SentinelOne LimaCharlie Extension gives D&R rules and AI agents access to the SentinelOne Management API. With the extension, you can list agents and act on them (isolate, scan). You can also triage threats (mitigate, verdict, incident status, notes), blocklist file hashes, and read the org hierarchy and the activity log of the tenant.

The extension has two layers:

- **Typed actions** for the common EDR/SecOps workflows. These actions have clear parameter names and built-in safety limits.
- A generic **`api_call`** passthrough for each SentinelOne endpoint that a typed action does not cover.

## Setup

### 1. Create a SentinelOne API token

In the SentinelOne management console, create an API token. A **Service User** token (Settings → Users → Service Users) is the recommended type. It is an API-only credential with a configurable expiry. Regular user tokens expire after 30 days. Scope the token to the sites and accounts that the extension manages.

### 2. Subscribe to the extension

Subscribe to `ext-sentinelone` from the LimaCharlie **Marketplace** (Extensions → Add-Ons).

### 3. Store the API token

In **Secrets Manager**, create a new secret (for example `sentinelone-api-token`). Paste the API token as the value of the secret.

### 4. Configure the extension

In **Extensions → ext-sentinelone → Configuration**, fill in:

| Field | Required | Value |
| --- | --- | --- |
| `console_url` | yes | Your SentinelOne management console URL, e.g. `https://usea1-partners.sentinelone.net` |
| `api_token` | yes | Reference to the secret that you created in step 3, e.g. `hive://secret/sentinelone-api-token` |
| `api_version` | no | API version path segment. Defaults to `v2.1`. |
| `site_ids` | no | List of SentinelOne site ids. If you set this field, the extension restricts **every** call to these sites. See [Org scoping](#org-scoping). |
| `account_ids` | no | List of SentinelOne account ids. If you set this field, the extension restricts every call to these accounts. If you set `site_ids` too, the extension combines the two fields. |

The extension sends the token as `Authorization: ApiToken <token>` on each request. If you rotate the secret in Secrets Manager, the change takes effect on the next request after a surfaced `401`.

## Org scoping

One SentinelOne console can hold many customers, split across **accounts** and **sites**. For this MSSP or multi-tenant pattern, set `site_ids` or `account_ids` in the configuration. These fields pin one LimaCharlie organization to one SentinelOne customer. The extension then restricts each call from the organization to that scope. For example, `list_agents` returns only the endpoints of that customer, and a mitigation can act only inside the scope.

The scope is a **hard cap**, not a default:

- **List actions** (`list_agents`, `list_threats`, `list_activities`, `list_sites` / `list_accounts` / `list_groups`) apply the scope to the `site_ids` / `account_ids` filters. The extension **intersects** a per-request `site_ids` / `account_ids` with the configured scope. A request can narrow the scope but cannot widen it. The extension **rejects** a request that targets ids fully outside the scope.
- **Mutating actions** (isolate / scan / mitigate / verdict / incident / note) put the scope into the target filter of the action. An entity that you select only by id stays inside the configured sites and accounts. You cannot act on the agent or threat of another tenant if you guess its id.
- **`blocklist_hash`** cannot apply `tenant`-wide for a scoped organization. If the request gives no scope, the extension uses the configured scope.
- **`api_call`** (the generic passthrough): the extension cannot constrain a **write** (`POST` / `PUT` / `DELETE`) that carries no target `filter`, and it **refuses** that write for a scoped organization. Use a typed action, or include a filter. For a **read** (`GET`), the extension puts the scope into the query. It cannot constrain a read of a single resource by path (for example `sites/<id>`), so the typed actions are the fully-enforced surface.

!!! note "Scope by the right dimension"
    Scope by `account_ids` when a customer maps to a SentinelOne *account*, and by `site_ids` when it maps to a *site*. The hierarchy-list actions can filter only by a dimension that the endpoint supports. `list_accounts` filters by `account_ids` only, because an account has no parent site, so an organization scoped by `site_ids` alone does not constrain `list_accounts`. Use `account_ids`, or set both fields, if the list of the account hierarchy must also be scoped. Scope the API token itself to the intended sites and accounts in SentinelOne. The extension enforces the configuration scope on top of the permissions of the token, not instead of them.

## Actions

Each action that changes state (isolate, scan, mitigate, verdict, incident, note) selects its targets in one of two ways. Give an explicit id list (`agent_ids` / `threat_ids`), or give a raw SentinelOne `filter` object. **The extension refuses an empty selector.** It does not run an action that targets each entity in the tenant.

List actions return one page and a cursor: `{data: [...], pagination: {nextCursor, totalItems}}`. To get the next page, send `cursor` back with the same filters. `limit` defaults to `100` (max `1000`).

### Generic

#### `api_call`

Call any SentinelOne Management API endpoint. Use this action for endpoints that have no typed action.

| Field | Type | Notes |
| --- | --- | --- |
| `method` | enum | `GET` (default), `POST`, `PUT`, `DELETE`. |
| `path` | string | **Required.** Endpoint path relative to `/web/api/<version>`, e.g. `agents`, `threats/mitigate/kill`, `system/info`. |
| `query` | object | Query-string parameters as a flat object. |
| `body` | object | JSON request body for `POST`/`PUT`. Action endpoints expect `{filter: {...}, data: {...}}`. |

Returns the full SentinelOne response envelope.

### Agents

#### `list_agents`

List/search agents (endpoints).

| Field | Type | Notes |
| --- | --- | --- |
| `query` | string | Free-text search (computer name, IP, …). |
| `computer_name` | string | Substring match on computer name. |
| `uuid` | string | Filter by agent UUID. |
| `is_active` | bool | Only active (`true`) / inactive (`false`) agents. |
| `network_status` | enum | `connected`, `connecting`, `disconnected`, `disconnecting`. |
| `infected` | bool | Only agents with (`true`) / without (`false`) active threats. |
| `os_types` | list of enum | `windows`, `linux`, `macos`, `windows_legacy`. |
| `site_ids` / `group_ids` / `account_ids` | list of string | Restrict to sites / groups / accounts. |
| `limit` / `cursor` | int / string | Pagination. |
| `extra_query` | object | Raw query params merged into the request (escape hatch). |

#### `isolate_agent` / `deisolate_agent` / `scan_agent`

Network-isolate (disconnect), reconnect, or start a full-disk scan on selected agents.

| Field | Type | Notes |
| --- | --- | --- |
| `agent_ids` | list of string | Agent ids to act on (the common case). |
| `filter` | object | Raw SentinelOne agent filter (advanced alternative to `agent_ids`). |
| `data` | object | Extra fields merged into the action's data payload. |

At least one of `agent_ids` or `filter` is required. Returns `{data: {affected: N}}`.

### Threats

#### `list_threats`

List/search threats.

| Field | Type | Notes |
| --- | --- | --- |
| `query` | string | Free-text search (file path, hash, computer name, …). |
| `content_hashes` | list of string | Filter by file SHA-1 hashes. |
| `mitigation_statuses` | list of string | e.g. `mitigated`, `active`, `blocked`, `suspicious`. |
| `incident_statuses` | list of string | `unresolved`, `in_progress`, `resolved`. |
| `analyst_verdicts` | list of string | `true_positive`, `false_positive`, `suspicious`, `undefined`. |
| `classifications` | list of string | e.g. `Malware`, `PUA`, `Ransomware`. |
| `resolved` | bool | Only resolved (`true`) / unresolved (`false`) threats. |
| `created_at__gte` / `created_at__lte` | string | ISO-8601 UTC bounds, e.g. `2026-06-01T00:00:00.000000Z`. |
| `site_ids` / `account_ids` | list of string | Restrict to sites / accounts. |
| `limit` / `cursor` / `extra_query` | — | Pagination and raw-params escape hatch. |

#### `mitigate_threat`

Apply a mitigation action to selected threats.

| Field | Type | Notes |
| --- | --- | --- |
| `action` | enum | **Required.** `kill`, `quarantine`, `remediate`, `rollback-remediation`, `un-quarantine`, `network-quarantine`. |
| `threat_ids` | list of string | Threat ids to mitigate. |
| `filter` | object | Raw SentinelOne threat filter (advanced alternative). |
| `data` | object | Extra fields merged into the action's data payload. |

#### `set_threat_verdict`

Set the analyst verdict on selected threats.

| Field | Type | Notes |
| --- | --- | --- |
| `verdict` | enum | **Required.** `true_positive`, `false_positive`, `suspicious`, `undefined`. |
| `threat_ids` / `filter` | — | Target selection, at least one required. |

#### `set_threat_incident`

Set the incident status on selected threats.

| Field | Type | Notes |
| --- | --- | --- |
| `status` | enum | **Required.** `unresolved`, `in_progress`, `resolved`. |
| `threat_ids` / `filter` | — | Target selection, at least one required. |

#### `add_threat_note`

Append a note to selected threats. AI agents can use this action to record triage findings in the SentinelOne console.

| Field | Type | Notes |
| --- | --- | --- |
| `text` | string | **Required.** Note text. |
| `threat_ids` / `filter` | — | Target selection, at least one required. |

### Blocklist

#### `blocklist_hash`

Add a SHA-1 file hash to the SentinelOne blocklist.

| Field | Type | Notes |
| --- | --- | --- |
| `hash` | string | **Required.** SHA-1 hash to block. |
| `os_type` | enum | **Required.** `windows`, `windows_legacy`, `macos`, `linux`. |
| `description` | string | Reason for the blocklist entry. |
| `tenant` | bool | Apply tenant-wide. Default `false`. |
| `site_ids` / `group_ids` / `account_ids` | list of string | Scope the entry when `tenant` is not set. |
| `data` | object | Extra fields merged into the restriction's data payload. |

A scope is required: set `tenant: true` or at least one of `site_ids` / `group_ids` / `account_ids`.

### Tenant reads

#### `list_sites` / `list_accounts` / `list_groups`

List the org hierarchy. Use these actions to find the ids for the scope parameters above.

| Field | Type | Notes |
| --- | --- | --- |
| `query` | string | Free-text name match. |
| `site_ids` / `account_ids` | list of string | Restrict by id. |
| `limit` / `cursor` / `extra_query` | — | Pagination and raw-params escape hatch. |

#### `list_activities`

List the activity / audit log.

| Field | Type | Notes |
| --- | --- | --- |
| `activity_types` | list of string | Numeric activity type codes (see the SentinelOne `/activities/types` endpoint). |
| `agent_ids` / `site_ids` | list of string | Restrict by agent / site. |
| `created_at__gte` / `created_at__lte` | string | ISO-8601 UTC bounds. |
| `limit` / `cursor` / `extra_query` | — | Pagination and raw-params escape hatch. |

## Detection & Response

Example response action that network-isolates the SentinelOne agent named in a detection:

```yaml
- action: extension request
  extension action: isolate_agent
  extension name: ext-sentinelone
  extension request:
    agent_ids:
      - '{{ .event/agent_id }}'
```

> **Wrap literal strings in `{{ "..." }}`.**
> Values under `extension request` are evaluated as templates. A bare string without `{{ }}` is read as a [gjson](https://github.com/tidwall/gjson) path into the event. If the path does not resolve, the key is dropped from the payload.

`extension request` actions do not return a result to the rule. The rule engine does not put the response into the evaluation context of the rule. For a chain of steps (find the agent, isolate it, annotate the threat), use a [Playbook](../limacharlie/playbook.md) or an AI agent. A Playbook and an AI agent can hold ids between calls.

## Notes

- The extension sends the token as `Authorization: ApiToken <token>`. SentinelOne API tokens are static, not OAuth, and you cannot refresh them. A `401` is surfaced as a real auth failure. The extension then removes its cached client, so the next request reads the secret again after a rotation.
- SentinelOne cursors are not self-contained. Send the same filters with `cursor` for each page.
- You can paste `console_url` with or without a trailing `/web/api[/version]` suffix. The extension normalizes both forms.
- Errors are surfaced as `sentinelone api <status> on <path>: <message>`. The message holds the flattened error envelope from SentinelOne.
- If you unsubscribe from the extension, the saved configuration stays. If you subscribe again, the extension restores the configuration, and you do not configure it a second time.
