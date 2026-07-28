# ThreatLocker

## Overview

This Adapter ingests events from the [ThreatLocker](https://threatlocker.com) Portal API into LimaCharlie. The adapter sends the events in their original ThreatLocker JSON form. It does not change the payloads.

The adapter is **generic by design**. The ThreatLocker Portal API is uniform: each resource that you can query has a `<Resource>GetByParameters` endpoint that takes a `POST` with a JSON filter body. The adapter models each such endpoint as a *feed*. To add a new event type, you change the configuration, not the code.

The adapter works with the [ThreatLocker extension](../../../5-integrations/extensions/third-party/threatlocker.md). The adapter delivers Application Control approval-request events into LimaCharlie. The extension supplies the actions that an AI agent, or a Playbook, calls to enrich those events and to write the decision back.

## Deployment Configurations

All adapters support the same `client_options`. Always set these options when you use the binary adapter or when you create a webhook adapter. If you use an Adapter helper in the web app, you do not set these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself with LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, such as `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name that you choose for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name, as described below.

### Adapter-specific Options

Adapter Type: `threatlocker`

| Key | Required | Description |
| --- | --- | --- |
| `api_key` | yes | ThreatLocker API token (see [Authentication](#authentication) below). Sent verbatim in the `Authorization` header — no `Bearer` prefix. |
| `instance` | yes* | ThreatLocker instance letter (`b`, `c`, …, `g`, `h`, …). *Required unless `base_url` is set. |
| `base_url` | no | Full API root override, e.g. `https://portalapi.g.threatlocker.com/portalapi`. Use to point the adapter at a non-standard endpoint; otherwise prefer `instance`. |
| `managed_organization_id` | no | UUID of the managed (child) organization. Sent as the `managedOrganizationId` header — used by MSP **parent** tokens to scope every request to a specific child tenant. |
| `feeds` | no | List of feeds to poll (see [Feed fields](#feed-fields) below). When omitted the adapter polls the three default feeds described under [Default feeds](#default-feeds). |
| `page_size` | no | Records for each page. Default `100`, maximum `1000`. |
| `poll_interval` | no | Wait between polls of a feed, as a Go duration in **nanoseconds**. Default `60000000000` (1 minute). |
| `dedupe_ttl` | no | The time that the adapter keeps a record id, to stop the adapter from sending the record again. Default 7 days. |
| `retry_base_delay` / `max_retry_delay` / `max_retry_attempts` | no | Retry settings for transient failures. |

### Feed fields

Each entry in `feeds` describes one ThreatLocker `*GetByParameters` endpoint to poll.

| Key | Required | Description |
| --- | --- | --- |
| `name` | yes | Labels the feed and becomes the `EventType` of every shipped event. Must be unique within `feeds`. |
| `url` | yes | API path of the `*GetByParameters` endpoint, **relative to the API root** (e.g. `ApprovalRequest/ApprovalRequestGetByParameters`). |
| `parameters` | no | JSON object merged into the request body — resource-specific filters such as `statusId`, `showChildOrganizations`, ThreatLocker query DTOs. |
| `order_by` | no | Sort field. Default `dateTime`. The default request is newest-first (`isAscending = false`). |
| `items_path` | no | Key that holds the records array when the response is an object envelope. Auto-detected (`data`, `pageItems`, …) when empty. |
| `timestamp_field` | no | Path to the record's event time. Supports `/`-separated nested paths. Default `dateTime`. |
| `id_field` | no | Path to the record's stable identifier, used for deduplication. Falls back to common id fields, then to a content hash. |
| `max_pages` | no | Limits the pages that each poll fetches. Default `100`. |
| `window` | no | When set (for example, `5m`), rewrites `startDate` / `endDate` in the request body on every poll to a rolling `[now-window-poll_interval, now]` range. **Required** for endpoints that need a date range (`ActionLog`, `SystemAudit`). The deduper removes the overlap with the previous poll. |
| `start_date_field` / `end_date_field` | no | Override the request-body field names used by `window`. Defaults: `startDate` / `endDate`. |

### Default feeds

If you do not configure `feeds`, the adapter polls three feeds. Together, these feeds cover the primary telemetry of ThreatLocker:

| Default feed | ThreatLocker endpoint | What it carries |
| --- | --- | --- |
| `approval_request` | `ApprovalRequest/ApprovalRequestGetByParameters` (`statusId = 1`) | Pending Application Control whitelist requests. The adapter sends one event for each new request, exactly once. This is the input to AI-driven triage with the [ThreatLocker extension](../../../5-integrations/extensions/third-party/threatlocker.md). |
| `unified_audit` | `ActionLog/ActionLogGetByParametersV2` | The **Unified Audit** — the combined event stream of ThreatLocker for `execute` / `install` / `network` / `registry` / `read` / `write` / `move` / `delete` / `baseline` / `powershell` / `elevate` / web activity across every module. The adapter polls it on a 5-minute rolling window. |
| `system_audit` | `SystemAudit/SystemAuditGetByParameters` | Portal and administrator activity — logins, policy edits, approval decisions, organization changes. The adapter polls it on a 5-minute rolling window. |

`unified_audit` and `system_audit` both *need* a `startDate`/`endDate` filter on every request. The adapter sets these fields automatically with the feed's `window`. The deduper for each feed removes the overlap between two windows, and delivery stays at-least-once.

## Authentication

Create an API token under **Portal → Administration → API Users** in the ThreatLocker Portal. The adapter sends the token verbatim in the `Authorization` header. There is no `Bearer` prefix and no OAuth handshake.

### Finding your instance

ThreatLocker hosts each tenant on one of several lettered instances (`b`, `c`, `d`, …, `g`, `h`, …). An API token is scoped to the instance that made it. To find your instance:

1. Open the ThreatLocker Portal.
2. Click the **Help** button in the top-right corner of any page.
3. Read the letter in parentheses next to **ThreatLocker Access**. For example, `ThreatLocker Access (C)` gives `instance: c`.

> ⚠️ **A token from one instance returns `403 TOKEN_REVOKED` on every other instance.** The API does not show the difference between a wrong instance and a token that is revoked. If the token is active but you still see `TOKEN_REVOKED`, check the instance letter first. An authentication failure stops the adapter, which makes the incorrect configuration visible.

## How polling works

On every poll, the adapter reads the pages of a feed (`pageNumber` / `pageSize`). It stops at the end of the result set (a short page or an empty page), or at the feed's `max_pages` limit. An in-memory deduper, keyed for each feed, sends each record to LimaCharlie exactly once, although the adapter fetches the pages again on every poll.

The adapter retries transient API failures (HTTP 5xx, 429, network errors) with exponential backoff. An authentication failure (401/403) stops the adapter, so that repeated retries do not burn the token.

The adapter reads all the pages again. It does not stop at the first page of records that it saw before. The Portal API paginates by offset over a live list that can change, so a record can move across a page boundary between two page fetches. To read all the pages again costs more requests, but it is correct.

For a large feed, or a feed that changes quickly, limit the work of each poll. Use the feed's `parameters` (for example, a date-range filter) and a `max_pages` value that is larger than the expected size of the feed. A newest-first query (`isAscending = false`, the default) keeps the most recent records when `max_pages` truncates the result.

## CLI Deployment

You can get the [Adapter downloads](../deployment.md) on the deployment page. The defaults are usually enough. Supply `api_key` and `instance` to pull the three default feeds.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter threatlocker \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$INSTALLATION_KEY \
  client_options.platform=json \
  client_options.sensor_seed_key=threatlocker \
  api_key=$THREATLOCKER_API_TOKEN \
  instance=g
```

## Infrastructure as Code Deployment

```yaml
# For cloud sensor deployment, store credentials as hive secrets:
#
#   api_key: "hive://secret/threatlocker-api-token"

sensor_type: "threatlocker"
threatlocker:
  api_key: "hive://secret/threatlocker-api-token"
  instance: "g"
  # Optional: MSP parent tokens — scope every request to a child tenant
  # managed_organization_id: "00000000-0000-0000-0000-000000000000"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_THREATLOCKER"
    hostname: "threatlocker-adapter"
    platform: "json"
    sensor_seed_key: "threatlocker-sensor"
    mapping:
      event_type_path: "_lc_threatlocker_feed"
      event_time_path: "dateTime"
    indexing: []
```

### Custom feeds

Override `feeds` to add new feeds or to replace all the defaults. The list **replaces** the defaults, it does not merge with them. Declare again each default that you want to keep with your custom feeds.

The example below keeps the three defaults and adds a fourth feed that sends *denied* approval requests:

```yaml
threatlocker:
  api_key: "hive://secret/threatlocker-api-token"
  instance: "g"
  feeds:
    - name: approval_request
      url: ApprovalRequest/ApprovalRequestGetByParameters
      parameters:
        statusId: 1            # pending
        showChildOrganizations: false
      id_field: approvalRequestId
    - name: unified_audit
      url: ActionLog/ActionLogGetByParametersV2
      window: 5m
      parameters:
        paramsFieldsDto: []
        groupBys: []
        exportMode: false
        showTotalCount: false
        showChildOrganizations: false
        onlyTrueDenies: false
        simulateDeny: false
      id_field: actionLogId
    - name: system_audit
      url: SystemAudit/SystemAuditGetByParameters
      window: 5m
      parameters:
        viewChildOrganizations: false
      id_field: systemAuditId
    - name: approval_request_denied
      url: ApprovalRequest/ApprovalRequestGetByParameters
      parameters:
        statusId: 3            # denied
        showChildOrganizations: false
      id_field: approvalRequestId
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_THREATLOCKER"
    platform: "json"
    sensor_seed_key: "threatlocker-sensor"
```

## Configuring a ThreatLocker Adapter in the Web UI

In the LimaCharlie web app, select `+ Add Sensor`. Then select **ThreatLocker**.

Select or create an Installation Key for this adapter. Then complete these fields:

| Field | Value |
| --- | --- |
| API Key | ThreatLocker Portal API token (from *Administration → API Users*). |
| Instance | Single instance letter from *Help → ThreatLocker Access (X)*, e.g. `g`. |
| Managed Organization ID | *(optional)* Child-tenant UUID for MSP parent tokens. |
| Feeds | *(optional)* JSON / YAML array of custom feeds. Leave empty to use the three defaults. |

Click `Complete Cloud Installation`. LimaCharlie authenticates with the Portal and starts to poll.

## Sample Rule

The adapter sends each record with an `EventType` that matches the `name` of the feed. The default set of feeds gives `approval_request`, `unified_audit`, and `system_audit`. D&R rules can thus route directly on the feed:

```yaml
# Detection — flag every new pending approval request so an AI agent
# can pick it up and call the ext-threatlocker enrichment actions.
event: approval_request

# Response
- action: report
  name: ThreatLocker Approval Request
```

To chain the enrichment and the decision from a rule on this event, dispatch to a [Playbook](../../../5-integrations/extensions/limacharlie/playbook.md) or to an AI agent. The [ThreatLocker extension](../../../5-integrations/extensions/third-party/threatlocker.md) page describes the available actions.

## API Docs

- ThreatLocker Portal Swagger: `https://portalapi.<instance>.threatlocker.com/swagger` (replace `<instance>` with your tenant's instance letter).
