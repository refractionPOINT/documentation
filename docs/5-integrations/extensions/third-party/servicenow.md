# ServiceNow

[ServiceNow](https://www.servicenow.com/) is a platform for IT service management (ITSM) and security operations. Teams use it for ticketing, change and problem management, CMDB asset tracking, and security incident response.

The ServiceNow LimaCharlie Extension is mainly an **API bridge**. It lets automation on the LimaCharlie side (D&R rules, AI agents) drive a ServiceNow instance. The automation can create, read, update, and delete records on *any* table, append journal entries, manage attachments, count and query records, and resolve CMDB items. On top of that bridge, the extension adds typed incident actions and one optional, fully-configurable **Case-mirroring** recipe (LimaCharlie Cases ⇄ ServiceNow records).

The extension is not limited to the stock ITSM `incident` table. The same actions apply to Security Incident Response (`sn_si_incident`), to change and problem workflows, and to custom tables. Give a `table` value, or configure the mirror target.

The sync model is stateless on the LimaCharlie side:

- **LC → ServiceNow**: `mirror_case` upserts a ServiceNow record from a LimaCharlie Case. The upsert is idempotent, because it uses the standard `correlation_id` / `correlation_display` fields of the record. Repeated calls update the same record.
- **ServiceNow → LC**: `pull_incident_changes` returns the records that changed since a watermark, in a normalized form for Cases. It excludes the changes of its own integration user, which stops echo loops.

## Setup

### 1. Create a ServiceNow integration user

Create a dedicated ServiceNow **integration user** for the extension. Give the user the roles that the tables and the operations need (e.g. `itil` for incidents, `sn_si.analyst` for Security Incident Response, plus `rest_api_explorer` and table ACLs). The ACLs of the integration user control all that the extension can read, write, or delete.

A dedicated user is important for the Case-mirroring puller. `pull_incident_changes` removes the writes of this user to stop echo loops (see [Case mirroring](#case-mirroring-optional)).

### 2. Choose an authentication mode

The extension supports three modes (set `auth_mode`):

| Mode | Requires | Notes |
| --- | --- | --- |
| `basic` | `username`, `password` | Username/password sent on every request. Simplest for ServiceNow. |
| `oauth_password` | `client_id`, `client_secret`, `username`, `password` | OAuth2 Resource Owner Password Credentials grant, then `refresh_token` to renew. |
| `oauth_client_credentials` | `client_id`, `client_secret` | True server-to-server grant (no end-user password). Needs extra instance-side setup — see below. |

For the OAuth modes, register an OAuth application in ServiceNow (**System OAuth → Application Registry**). Copy its Client ID and Client Secret.

The **client credentials** grant needs two more steps on the instance, after the client registration:

1. Set the system property `glide.oauth.inbound.client.credential.grant_type.enabled` to `true`. If the property does not exist, create it under **System Properties**. Without the property, the token endpoint returns `access_denied` / `server_error`.
2. On the OAuth application record, set the **OAuth Application User** (the `user` field) to your integration user. The grant issues tokens **as this user**, so the user must hold the roles that the actions need (e.g. `itil` / `sn_incident_write` for incident writes). Without the user, the token endpoint returns `unauthorized_client` ("integration user is not configured"). Set `integration_user` (below) to this same username, so SN → LC polling can remove the echo of the extension's own writes.

The **basic** and **OAuth password** modes do not need these steps. They authenticate as the `username` that you configure.

### 3. Subscribe to the extension

Subscribe to `ext-servicenow` from the LimaCharlie **Marketplace** (Extensions → Add-Ons).

### 4. Store the credentials

In **Secrets Manager**, create secrets for the sensitive values. The extension resolves the `password` and `client_secret` fields as secret references at request time. For example, create a `servicenow-password` secret and reference it as `hive://secret/servicenow-password`.

### 5. Configure the extension

In **Extensions → ext-servicenow → Configuration**, fill in:

| Field | Required | Value |
| --- | --- | --- |
| `instance_url` | yes | ServiceNow instance base URL, e.g. `https://acme.service-now.com`. |
| `auth_mode` | no | `basic` (default), `oauth_password`, or `oauth_client_credentials`. |
| `username` | conditional | Required for `basic` / `oauth_password`. |
| `password` | conditional | Secret reference. Required for `basic` / `oauth_password`. |
| `client_id` | conditional | Required for `oauth_password` / `oauth_client_credentials`. |
| `client_secret` | conditional | Secret reference. Required for `oauth_password` / `oauth_client_credentials`. |
| `integration_user` | no | The ServiceNow user that the extension authenticates as. `pull_incident_changes` excludes the changes of this user. Set it to enable the echo-loop guard. |
| `correlation_display` | no | Label written to the `correlation_display` field of mirrored records (default `LimaCharlie`). It scopes upserts and SN→LC polling, so many integrations can work together. |
| `close_code` | no | `close_code` used when the extension mirrors a case into Resolved/Closed (default `Solution provided`). The value must be in the `close_code` choice list of your instance. This list changes with the ServiceNow version, and the legacy `Solved (Permanently)` is not in current releases. ServiceNow drops an invalid value without a message, and the mandatory-resolution-code data policy then fails. |
| `mirror_table` | no | Target table for case mirroring (default `incident`; set `sn_si_incident` for Security Incident Response, or any task-derived table). |
| `mirror_subject_prefix` | no | Prefix for the `short_description` of the mirrored record (default `LimaCharlie Case`). |
| `mirror_state_map` | no | Override of case-status→record-state mapping, e.g. `{"new":1,"in_progress":2,"resolved":6,"closed":7}`. Used in both directions. |
| `mirror_severity_map` | no | Override of case-severity→`{urgency,impact}` mapping, e.g. `{"critical":{"urgency":1,"impact":1}}`. |

Only `instance_url` is required. The extension validates the credential fields at request time against the selected `auth_mode`. The extension is stateless. The mirroring state is in ServiceNow (`correlation_id`) and in the returned `watermark`, so there is no database to provision.

## Actions

Each action accepts a JSON request body when a D&R rule calls it with `extension request`. The typed actions and the mirroring recipe are shortcuts. A customer who models ServiceNow in another way can ignore them and use `create_record` / `update_record` / `query_table` directly.

### Generic Table API bridge (any table)

These actions work on *any* table. They never assume `incident`.

#### `create_record`

Insert a record into any table with a field map that you choose. This action is the generic write counterpart to `query_table`. Use it for `change_request`, `problem`, `sc_task`, custom tables, and others.

| Field | Type | Notes |
| --- | --- | --- |
| `table` | string | **Required.** Table name. |
| `fields` | object | **Required.** Field name→value map to set on the new record. |

#### `get_record`

Fetch a single record from any table by `sys_id` or by its `number` field.

| Field | Type | Notes |
| --- | --- | --- |
| `table` | string | **Required.** Table name. |
| `sys_id` | string | Record sys_id. |
| `number` | string | Record number (alternative to `sys_id`). |
| `fields` | string | Comma-separated fields to return (`sysparm_fields`). |
| `display_value` | enum | `false` (raw, default), `true` (labels), or `all`. |

#### `update_record`

Patch a record on any table by `sys_id` with a field map that you choose. The extension does not change the fields that you do not give.

| Field | Type | Notes |
| --- | --- | --- |
| `table` | string | **Required.** Table name. |
| `sys_id` | string | **Required.** Record sys_id to update. |
| `fields` | object | **Required.** Field name→value map to change. |

#### `delete_record`

Delete a record on any table by `sys_id`. You cannot undo the deletion. The ACLs of the integration user control what the extension can delete.

| Field | Type | Notes |
| --- | --- | --- |
| `table` | string | **Required.** Table name. |
| `sys_id` | string | **Required.** Record sys_id to delete. |

#### `query_table`

Read-only Table API query against any table (`incident`, `problem`, `change_request`, `cmdb_ci`, `sys_user`, …). AI agents use it for data that the typed actions do not cover. Use it also to resolve display names to the sys_ids that the write actions need.

| Field | Type | Notes |
| --- | --- | --- |
| `table` | string | **Required.** Table name. |
| `query` | string | ServiceNow encoded query (`sysparm_query`). |
| `fields` | string | Comma-separated fields to return. |
| `limit` | int | Max records (default `50`). |
| `offset` | int | Pagination offset. |
| `display_value` | enum | `false` / `true` / `all`. |

Returns `{ "count": N, "records": [...] }`.

#### `count_records`

Return the number of records that match an encoded query, with the Aggregate API. The action pulls no rows. For example, count the open critical records before you escalate.

| Field | Type | Notes |
| --- | --- | --- |
| `table` | string | **Required.** Table name. |
| `query` | string | Encoded query (optional; empty counts all). |

### Typed incident conveniences

These table-aware shortcuts default to `incident`. Set `table` to `sn_si_incident`, for example, to work on Security Incident Response records. Each action also accepts an `extra` object. Use `extra` to merge raw ServiceNow fields that the typed schema does not model.

#### `create_incident`

Open a record with a typed subject and body, urgency and impact, and assignment. Returns the new record with its `sys_id` and `number`.

| Field | Type | Notes |
| --- | --- | --- |
| `short_description` | string | **Required.** Incident subject line. |
| `table` | string | Table to create in (default `incident`). |
| `description` | string | Incident body / description. |
| `state` | int | Incident state (1 New, 2 In Progress, 3 On Hold, 6 Resolved, 7 Closed, 8 Canceled). |
| `urgency` | int | Urgency (1 High … 3 Low). |
| `impact` | int | Impact (1 High … 3 Low). |
| `priority` | int | ServiceNow usually derives this from urgency×impact. Set it to override. |
| `category` | string | Category. |
| `assignment_group` | string | Assignment group **sys_id** (reference; display names are not auto-resolved). |
| `assigned_to` | string | Assignee user **sys_id**. |
| `caller_id` | string | Caller user **sys_id**. |
| `correlation_id` | string | External correlation id (e.g. an LC case id). |
| `correlation_display` | string | External system label (e.g. `LimaCharlie`). |
| `extra` | object | Raw ServiceNow fields to merge. |

#### `update_incident`

Update a record by `sys_id`. Set `state` to drive workflow transitions. You can also reassign the record, or append a work note or a comment.

| Field | Type | Notes |
| --- | --- | --- |
| `sys_id` | string | **Required.** Record sys_id to update. |
| `table` | string | Table to update (default `incident`). |
| `work_note` | string | Internal (IT-only) work note to append. |
| `comment` | string | Customer-visible comment to append. |
| `short_description`, `description`, `state`, `urgency`, `impact`, `priority`, `category`, `assignment_group`, `assigned_to`, `caller_id`, `extra` | | Same typed incident fields as `create_incident`. |

#### `get_incident`

Fetch a single record by `sys_id` or by human number (e.g. `INC0010023`, `SIR0001001`).

| Field | Type | Notes |
| --- | --- | --- |
| `table` | string | Table to read (default `incident`). |
| `sys_id` | string | Record sys_id. |
| `number` | string | Record number (e.g. `INC0010023`). |
| `fields` | string | Comma-separated fields to return. |
| `display_value` | enum | `false` / `true` / `all`. |

#### `search_incidents`

Search with a ServiceNow encoded query (`sysparm_query`), e.g. `active=true^state=2^ORDERBYDESCsys_updated_on`. Use it to remove duplicates before you create a record, or to find existing work.

| Field | Type | Notes |
| --- | --- | --- |
| `table` | string | Table to search (default `incident`). |
| `query` | string | ServiceNow encoded query. |
| `fields` | string | Comma-separated fields to return. |
| `limit` | int | Max records (default `50`). |
| `offset` | int | Pagination offset. |
| `display_value` | enum | `false` / `true` / `all`. |

Returns `{ "count": N, "incidents": [...] }`.

### Journal, attachments, CMDB

#### `add_note`

Append an internal work note, a customer-visible comment, or both, to a record (default table `incident`). Journal fields **append**. They never overwrite.

| Field | Type | Notes |
| --- | --- | --- |
| `sys_id` | string | **Required.** Record sys_id. |
| `table` | string | Table name (default `incident`). |
| `note` | string | Internal (IT-only) work note. |
| `comment` | string | Customer-visible additional comment. |

#### `add_attachment`

Upload a file as an attachment on a record (default table `incident`). Set `content_base64=true` to send binary content.

| Field | Type | Notes |
| --- | --- | --- |
| `sys_id` | string | **Required.** Record sys_id. |
| `file_name` | string | **Required.** Attachment file name. |
| `table` | string | Table name (default `incident`). |
| `content_type` | string | MIME type (default `application/octet-stream`). |
| `content` | string | File content (text, or base64 when `content_base64=true`). |
| `content_base64` | bool | `true` if `content` is base64-encoded binary. |

#### `list_attachments`

List the attachment metadata of a record (default table `incident`). Returns the `sys_id`, `file_name`, size, and content type of each attachment. To download an attachment, give its `sys_id` to `get_attachment`.

| Field | Type | Notes |
| --- | --- | --- |
| `sys_id` | string | **Required.** Record sys_id. |
| `table` | string | Table name (default `incident`). |

#### `get_attachment`

Download the bytes of an attachment by its attachment `sys_id` (from `list_attachments`). Returns `content_base64`, `content_type` and `size_bytes`.

| Field | Type | Notes |
| --- | --- | --- |
| `attachment_sys_id` | string | **Required.** sys_id of the attachment record (`sys_attachment`), not the parent record. |

#### `lookup_ci`

Resolve a CMDB configuration item (asset) by name or with a custom encoded query. This action maps LC sensor hostnames to the ServiceNow CMDB, so incidents can reference the correct asset.

| Field | Type | Notes |
| --- | --- | --- |
| `name` | string | CI name to match (LIKE). |
| `query` | string | Custom encoded query (overrides `name`). |
| `class` | string | CMDB table/class (default `cmdb_ci`). |
| `limit` | int | Max records (default `50`). |

Returns `{ "count": N, "cis": [...] }`.

### Case mirroring (optional)

This recipe is bidirectional and fully configurable. It keeps a [LimaCharlie Case](../limacharlie/index.md) and a ServiceNow record in sync. The mirror uses the external-link fields of ServiceNow: `correlation_id` holds the LimaCharlie case id, and `correlation_display` holds the label of each integration (default `LimaCharlie`).

#### `mirror_case`

**LC → ServiceNow.** Upsert a ServiceNow record from an LC Case. The action finds the record by `correlation_id=case_id`, in the scope of the `correlation_display` of this integration. Repeated calls update the same record and do not create duplicates. Connect this action to a D&R rule on case events.

| Field | Type | Notes |
| --- | --- | --- |
| `case_id` | string | **Required.** LimaCharlie case id (stored as `correlation_id`). |
| `case_number` | int | LimaCharlie case number (used in the record subject, `LimaCharlie Case #N: …`). |
| `status` | enum | `new`, `in_progress`, `resolved`, `closed`. Maps to `state` (configurable with `mirror_state_map`). |
| `severity` | enum | `critical`, `high`, `medium`, `low`, `info`. Maps to `urgency`/`impact` (configurable with `mirror_severity_map`; ServiceNow derives `priority`). |
| `classification` | string | Case classification (`true_positive`, `false_positive`, `pending`); appended to the description. |
| `summary` | string | Case summary. The first line, truncated to 160 chars, becomes the record subject. The summary also becomes the description. |
| `conclusion` | string | Case conclusion (appended to description, used as `close_notes` on terminal states). |
| `assignees` | list of string | Accepted, but not shown on the record at this time. |
| `tags` | list of string | Appended to the description. |
| `table` | string | Override the configured mirror target table for this call. |
| `correlation_display` | string | Override the `correlation_display` label for this mirror. |
| `sync_note` | string | Optional work note to record the sync on the record. |
| `extra` | object | Raw fields merged into (and overriding) the mapped record fields. |

Default mappings applied (you can override all of them in the configuration):

- Status → `state`: `new` → 1, `in_progress` → 2, `resolved` → 6, `closed` → 7. Terminal states (Resolved/Closed) also set `close_code` (from config) and `close_notes`.
- Severity → `urgency`/`impact`: `critical` → 1/1, `high` → 1/2, `medium` → 2/2, `low` and `info` → 3/3.

Returns `{ "created": bool, "sys_id": "...", "number": "...", "incident": {...} }`.

#### `pull_incident_changes`

**ServiceNow → LC.** Return the records on the mirror table that changed at or after a watermark, in the scope of the `correlation_display` of this integration. The action normalizes each record to `{case_id, case_status, …}`, ready to apply back to LC Cases. It **excludes changes made by the `integration_user`** to stop echo loops. It also returns a fresh `watermark` for the next pull. Call it from a D&R `schedule` rule (e.g. every 12h for each org), and pass the watermark back as rule state.

| Field | Type | Notes |
| --- | --- | --- |
| `since` | string | ServiceNow datetime watermark (`YYYY-MM-DD HH:MM:SS`, UTC). An empty value starts from the most recent changes (newest first). Pass the returned watermark back to move forward. |
| `limit` | int | Max records (default `100`). |
| `include_own_changes` | bool | Disable the echo-loop guard (include changes by the integration user). |

Returns `{ "count": N, "changes": [...], "watermark": "YYYY-MM-DD HH:MM:SS" }`. Each change carries `sys_id`, `number`, `case_id` (from `correlation_id`), `state`, a normalized `case_status`, `short_description`, `sys_updated_on`, and `sys_updated_by`. The `case_status` value is `new`, `in_progress`, `resolved`, or `closed`. On Hold maps to `in_progress`, and Canceled maps to `closed`.

> The watermark boundary is **inclusive** (≥ `since`). Remove the duplicates in the applied changes by `sys_id`. Keep `limit` above the largest number of updates that you expect in the same second.

#### Wiring up the bidirectional sync

D&R rules drive both directions. The extension holds no schedule of its own:

- **LC → ServiceNow**: a D&R rule on Case events calls `mirror_case` with the case fields. It sends each change when the change happens.
- **ServiceNow → LC**: a scheduled D&R rule calls `pull_incident_changes` at intervals. The rule sends back the watermark from the previous run, and applies the returned changes to Cases.

`pull_incident_changes` excludes the writes of the integration user. The LC → SN → LC round trip therefore does not import again what the extension mirrored.

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
    table: '{{ "incident" }}'
```

> **Wrap literal strings in `{{ "..." }}`.**
> Values under `extension request` are evaluated as templates. A bare string without `{{ }}` is read as a [gjson](https://github.com/tidwall/gjson) path into the event. If the path does not resolve, the key is dropped from the payload.

`extension request` actions do not return a result to the rule. The rule engine does not put the response into the evaluation context of the rule, so a later action in the same rule cannot use the new `sys_id`. For a chain of steps (open a record, attach a file, add a note), use a [Playbook](../limacharlie/playbook.md) or an AI agent. A Playbook and an AI agent can hold the `sys_id` between calls.

To append triage findings on an existing record (for example from a Playbook or AI agent that already knows the `sys_id`), use `add_note`:

```yaml
- action: extension request
  extension action: add_note
  extension name: ext-servicenow
  extension request:
    sys_id: '{{ "a1b2c3d4e5f6..." }}'
    note: '{{ .routing.hostname }}: suspicious process tree observed. See LC for details.'
```

## Notes

- The extension is **stateless**. The mirroring state is in ServiceNow (`correlation_id`) and in the returned `watermark`. There is no database.
- Reference fields (`assignment_group`, `assigned_to`, `caller_id`) take **sys_ids**, not display names. The extension does not resolve display names. First use `query_table` on `sys_user` / `sys_user_group` to resolve a name to its sys_id.
- The extension obeys ServiceNow rate limiting (`429`) one time for each request, with a `Retry-After` cap of 5 seconds. A `429` that continues is surfaced to the caller.
- An abort from a business rule or a data policy always surfaces as an error. ServiceNow can return a non-2xx status (e.g. `403`) or, for some aborts, HTTP `200` with a `{"status": "failure"}` envelope. The extension treats both as errors, never as success. A common cause is a record that you resolve with a `close_code` that is not in the choice list of the instance — see the `close_code` config note above.
- The extension sanitizes the `correlation_id` and `correlation_display` values on the write path and on the lookup path. It removes the encoded-query delimiters. Upserts stay idempotent, also for hostile values.
- The extension caches the OAuth access token and renews it with `refresh_token` (in `oauth_password` mode). If you rotate the secret in Secrets Manager, the extension removes the cached client on the next surfaced `401`.
- `pull_incident_changes` stops echo loops only if `integration_user` is the user that the extension authenticates as.
- Errors are surfaced as `servicenow api <status> on <path>: <message>`.
