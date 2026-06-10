# ServiceNow

[ServiceNow](https://www.servicenow.com/) is an IT service management platform. The ServiceNow LimaCharlie Extension provides **bidirectional mirroring between LimaCharlie Cases and ServiceNow incidents**, plus a set of outbound incident-management actions for D&R rules and AI agents: incident lifecycle (create/update/get/search), work notes and comments, attachments, CMDB lookups, and a read-only Table API escape hatch.

The sync model is stateless on the LimaCharlie side:

- **LC → ServiceNow**: `mirror_case` idempotently upserts a ServiceNow incident from a LimaCharlie Case, anchored on the incident's standard `correlation_id` / `correlation_display` fields. Repeated calls update the same incident.
- **ServiceNow → LC**: `pull_incident_changes` returns incidents updated since a watermark, normalized for feeding back into Cases. Changes made by the integration's own user are excluded, breaking echo loops.

## Setup

### 1. Create a ServiceNow integration user

Create a dedicated ServiceNow user (for example `lc.integration`) with permissions to read/create/update records on the `incident` table (including `work_notes`, `comments`, `correlation_id`, and `correlation_display`), attach files, and read whatever other tables you intend to query (`cmdb_ci` for `lookup_ci`, etc.). Using a dedicated user matters: its username is how the extension recognizes — and filters out — its own writes.

### 2. Choose an authentication mode

| Mode | `auth_mode` | Credentials needed | Notes |
| --- | --- | --- | --- |
| HTTP Basic | `basic` | `username`, `password` | Simplest; credentials sent on every request. |
| OAuth password grant | `oauth_password` | `client_id`, `client_secret`, `username`, `password` | Token obtained then auto-refreshed. |
| OAuth client credentials | `oauth_client_credentials` | `client_id`, `client_secret` | True server-to-server. Requires the instance property `glide.oauth.inbound.client.credential.grant_type.enabled` to be `true`. |

For the OAuth modes, create an OAuth API endpoint client in ServiceNow (**System OAuth → Application Registry**).

### 3. Subscribe to the extension

Subscribe to `ext-servicenow` from the LimaCharlie **Marketplace** (Extensions → Add-Ons).

### 4. Store the secrets

In **Secrets Manager**, store the password and/or client secret (for example `servicenow-password`, `servicenow-client-secret`).

### 5. Configure the extension

In **Extensions → ext-servicenow → Configuration**, fill in:

| Field | Required | Value |
| --- | --- | --- |
| `instance_url` | yes | ServiceNow instance base URL, e.g. `https://acme.service-now.com`. |
| `auth_mode` | no | `basic` (default), `oauth_password`, or `oauth_client_credentials`. |
| `username` | for `basic` / `oauth_password` | The integration user's username. |
| `password` | for `basic` / `oauth_password` | Reference to the stored secret, e.g. `hive://secret/servicenow-password`. |
| `client_id` | for OAuth modes | OAuth client ID. |
| `client_secret` | for OAuth modes | Reference to the stored secret, e.g. `hive://secret/servicenow-client-secret`. |
| `correlation_display` | no | Label stamped on mirrored incidents' `correlation_display`. Default `LimaCharlie`. Scopes both upserts and polling, so multiple integrations can coexist. |
| `integration_user` | no | The ServiceNow username the extension authenticates as. `pull_incident_changes` excludes changes by this user to break echo loops. |
| `close_code` | no | Incident `close_code` applied when mirroring a case into Resolved/Closed (data policies usually require one). Default `Solved (Permanently)`. |

## Actions

### Incident lifecycle

#### `create_incident`

Create a new incident. Only `short_description` is required.

| Field | Type | Notes |
| --- | --- | --- |
| `short_description` | string | **Required.** Incident subject line. |
| `description` | string | Incident body. |
| `state` | int | `1` New, `2` In Progress, `3` On Hold, `6` Resolved, `7` Closed, `8` Canceled. |
| `urgency` / `impact` | int | `1` High … `3` Low. |
| `priority` | int | Usually derived from urgency × impact; set to override. |
| `category` | string | Category. |
| `assignment_group` | string | Assignment group **sys_id** (display names are not resolved). |
| `assigned_to` | string | Assignee user **sys_id**. |
| `caller_id` | string | Caller user **sys_id**. |
| `correlation_id` | string | External correlation id (e.g. an LC case id). |
| `correlation_display` | string | External system label. |
| `extra` | object | Raw ServiceNow incident fields to merge — escape hatch for fields not modeled above. |

Returns the created record, including `sys_id` and `number`.

#### `update_incident`

Update an incident by `sys_id`. Accepts the same fields as `create_incident` (minus `short_description` being required), plus:

| Field | Type | Notes |
| --- | --- | --- |
| `sys_id` | string | **Required.** Incident to update. |
| `work_note` | string | Internal (IT-only) work note to append. |
| `comment` | string | Customer-visible comment to append. |

#### `get_incident`

Fetch a single incident by `sys_id` or human-readable `number` (e.g. `INC0010023`). Optional `fields` (comma-separated `sysparm_fields`) and `display_value` (`false` / `true` / `all`).

#### `search_incidents`

Search incidents with a ServiceNow encoded query.

| Field | Type | Notes |
| --- | --- | --- |
| `query` | string | Encoded query (`sysparm_query`), e.g. `active=true^state=2^ORDERBYDESCsys_updated_on`. |
| `fields` | string | Comma-separated fields to return. |
| `limit` | int | Default `50`. |
| `offset` | int | Pagination offset. |
| `display_value` | enum | `false` / `true` / `all`. |

Returns `{ "count": N, "incidents": [...] }`.

### Notes & attachments

#### `add_note`

Append an internal work note and/or a customer-visible comment to a record. Journal fields append — they never overwrite.

| Field | Type | Notes |
| --- | --- | --- |
| `sys_id` | string | **Required.** Record sys_id. |
| `table` | string | Table name. Default `incident`. |
| `note` | string | Internal (IT-only) work note. |
| `comment` | string | Customer-visible comment. |

#### `add_attachment`

Upload a file onto a record.

| Field | Type | Notes |
| --- | --- | --- |
| `sys_id` | string | **Required.** Record sys_id. |
| `file_name` | string | **Required.** Attachment file name. |
| `table` | string | Default `incident`. |
| `content_type` | string | MIME type. Default `application/octet-stream`. |
| `content` | string | File content — text, or base64 when `content_base64` is `true`. |
| `content_base64` | bool | Set for binary content. |

### Reads

#### `query_table`

Read-only Table API query against any table (`incident`, `problem`, `change_request`, `cmdb_ci`, `sys_user`, …) — the escape hatch for data the typed actions don't cover, and the way to resolve display names to the sys_ids the write actions expect. Takes `table` (required), `query`, `fields`, `limit` (default `50`), `offset`, `display_value`. Returns `{ "count": N, "records": [...] }`.

#### `lookup_ci`

Resolve a CMDB configuration item — bridges LC sensor hostnames to the ServiceNow CMDB. Takes `name` (LIKE match), or a custom `query`; optional `class` (default `cmdb_ci`) and `limit` (default `50`). Returns `{ "count": N, "cis": [...] }`.

### Case mirroring

#### `mirror_case`

Idempotently upsert a ServiceNow incident from a LimaCharlie Case. The incident is matched on `correlation_id = case_id` (scoped to this integration's `correlation_display`), so repeated calls update the same incident.

| Field | Type | Notes |
| --- | --- | --- |
| `case_id` | string | **Required.** LimaCharlie case id — stored as `correlation_id`. |
| `case_number` | int | LC case number, used in the incident subject (`LimaCharlie Case #N: …`). |
| `status` | enum | `new`, `in_progress`, `resolved`, `closed`. |
| `severity` | enum | `critical`, `high`, `medium`, `low`, `info`. |
| `classification` | string | Case classification (appended to the description). |
| `summary` | string | Case summary — becomes the incident subject (first line, truncated to 160 chars) and description. |
| `conclusion` | string | Case conclusion — appended to the description; used as `close_notes` on terminal states. |
| `assignees` / `tags` | list of string | Appended to the description. |
| `correlation_display` | string | Override the configured label for this mirror. |
| `sync_note` | string | Optional work note recording the sync on the incident. |

Mappings applied:

- Status → incident `state`: `new` → 1, `in_progress` → 2, `resolved` → 6, `closed` → 7. Terminal states also set `close_code` (from config) and `close_notes`.
- Severity → `urgency`/`impact`: `critical` → 1/1, `high` → 1/2, `medium` → 2/2, `low` and `info` → 3/3.

Returns `{ "created": bool, "sys_id": "...", "number": "...", "incident": {...} }`.

#### `pull_incident_changes`

Return incidents belonging to this integration (matched on `correlation_display`) updated at or after a watermark, normalized for feeding back into LC Cases.

| Field | Type | Notes |
| --- | --- | --- |
| `since` | string | ServiceNow datetime watermark (`YYYY-MM-DD HH:MM:SS`, UTC). Empty bootstraps from the most recent changes; pass the returned watermark back on the next call. |
| `limit` | int | Default `100`. Keep it above the largest expected same-second burst of updates. |
| `include_own_changes` | bool | Disable the echo-loop guard (changes by `integration_user` are excluded by default). |

Returns `{ "count": N, "changes": [...], "watermark": "YYYY-MM-DD HH:MM:SS" }`. Each change carries `sys_id`, `number`, `case_id` (from `correlation_id`), `state`, a normalized `case_status` (`new` / `in_progress` / `resolved` / `closed` — On Hold maps to `in_progress`, Canceled to `closed`), `short_description`, `sys_updated_on`, and `sys_updated_by`.

The watermark boundary is **inclusive** (≥ `since`) so records sharing the watermark's second are never missed; de-duplicate by `sys_id` when applying changes.

## Wiring up the bidirectional sync

Both directions are driven from D&R rules — the extension holds no schedule of its own:

- **LC → ServiceNow**: a D&R rule on Case events calls `mirror_case` with the case fields, pushing changes as they happen.
- **ServiceNow → LC**: a scheduled D&R rule periodically calls `pull_incident_changes`, passing back the watermark from the previous run, and applies the returned changes to Cases.

Because `pull_incident_changes` excludes the integration user's own writes, the LC → SN → LC round trip does not re-import what the extension itself mirrored.

## Detection & Response

Example response action that opens a ServiceNow incident for a detection:

```yaml
- action: extension request
  extension action: create_incident
  extension name: ext-servicenow
  extension request:
    short_description: '{{ .cat }} - {{ .routing.hostname }}'
    description: '{{ .event }}'
    urgency: 2
    impact: 2
    correlation_display: '{{ "LimaCharlie" }}'
```

> **Wrap literal strings in `{{ "..." }}`.**
> Values under `extension request` are evaluated as templates. A bare string without `{{ }}` is interpreted as a [gjson](https://github.com/tidwall/gjson) path against the event and, if it doesn't resolve, the key is silently dropped from the payload.

`extension request` actions are fire-and-forget — the rule engine does not surface the response back into the rule's evaluation context, so the freshly-created incident `sys_id` is not available to a subsequent action in the same rule. Workflows that need to chain (create an incident, attach a file, add notes) belong in a [Playbook](../limacharlie/playbook.md) or an AI agent, which can hold the `sys_id` between calls.

## Notes

- Reference fields (`assignment_group`, `assigned_to`, `caller_id`) take **sys_ids**, not display names — resolve names first with `query_table`.
- ServiceNow rate limiting (`429`) is honored once per request with a `Retry-After` cap of 5 seconds; a persistent `429` surfaces to the caller.
- ServiceNow can return HTTP `200` with a `{"status": "failure"}` envelope when a business rule or data policy aborts the operation — the extension treats this as an error, not a success.
- `correlation_id` and `correlation_display` values are sanitized (encoded-query delimiters stripped) on both the write and the lookup path, keeping upserts idempotent even for hostile values.
- OAuth tokens are refreshed automatically; rotating a secret in Secrets Manager takes effect after the next surfaced `401` evicts the cached client.
- Errors are surfaced as `servicenow api <status> on <path>: <message>`.
