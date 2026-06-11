# ServiceNow

## Overview

This Adapter ingests ServiceNow audit and system logs into LimaCharlie by polling the [ServiceNow REST Table API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_TableAPI.html). Events are forwarded in their original ServiceNow JSON form — the adapter does not reshape payloads.

ServiceNow keeps its audit telemetry in plain platform tables, so the adapter is **generic by design**: each *feed* is one table plus an optional [encoded query](https://www.servicenow.com/docs/r/zurich/platform-user-interface/c_EncodedQueryStrings.html) filter — collecting an additional table is a configuration change, not a code change.

By default the adapter collects **`sys_audit`**, ServiceNow's field-level change history: one record per field change on any audited table, carrying who made the change and the old/new values. Other security-relevant tables are easily added as feeds:

| Table | What it carries | Caveat |
| --- | --- | --- |
| `sys_audit` | Field-level change history of audited records (the default feed). | Insert-only; no rotation. |
| `syslog_transaction` | Every transaction against the instance (UI, REST, scheduled jobs) with user, URL and source IP. | **High volume.** Rotates away after ~8 weeks. |
| `sysevent` | The event log/queue, including login activity (`login`, `login.failed`, `external.authentication.succeeded`/`failed`, ...). | Rotates after ~7 days; filter with `query`. |
| `syslog` | System log (warnings/errors from instance processes). | Rotates after ~8 weeks. |
| `sys_outbound_http_log` | Outbound REST/SOAP requests made by the instance. | |

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, use `json`.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from.

### Adapter-specific Options

Adapter Type: `servicenow`

| Key | Required | Description |
| --- | --- | --- |
| `instance` | yes* | ServiceNow instance name; the adapter talks to `https://<instance>.service-now.com`. *Required unless `base_url` is set. |
| `base_url` | no | Full instance root override, e.g. `https://example.service-now.com`. |
| `username` | yes | Service-account user for HTTP Basic auth (see [Authentication](#authentication)). |
| `password` | yes | Service-account password. |
| `feeds` | no | List of tables to poll (see [Feed fields](#feed-fields) below). Default: the `sys_audit` table. |
| `page_size` | no | Records per page (`sysparm_limit`). Default `1000`, maximum `10000`. |
| `poll_interval` | no | Wait between polls of a feed, as a Go duration in **nanoseconds**. Default `60000000000` (1 minute). |
| `backfill` | no | How far back the first poll reaches. Default 15 minutes. |
| `dedupe_ttl` | no | How long a record id is remembered to suppress re-shipping. Default 7 days. |
| `retry_base_delay` / `max_retry_delay` / `max_retry_attempts` | no | Transient-failure retry tuning. |

### Feed fields

Each entry in `feeds` describes one ServiceNow table to poll.

| Key | Required | Description |
| --- | --- | --- |
| `table` | yes | ServiceNow table to read, e.g. `sys_audit`, `syslog_transaction`, `sysevent`. |
| `name` | no | Labels the feed and becomes the `EventType` of every shipped event. Defaults to `table`. Must be unique within `feeds`. |
| `query` | no | ServiceNow encoded query ANDed in front of the adapter's incremental time filter, e.g. `tablename=incident` or `name=login`. Column names, operators and values are case-sensitive. |
| `fields` | no | Comma-separated `sysparm_fields` restriction. Must include the feed's timestamp and id fields. |
| `timestamp_field` | no | Event-time column used for the incremental checkpoint and the shipped event time. Default `sys_created_on`. |
| `id_field` | no | Stable identifier used for deduplication. Default `sys_id`. |
| `max_pages` | no | Caps pages fetched per poll. Default `100`. The cap loses nothing: the next poll resumes from the advanced checkpoint. |

## Authentication

The adapter authenticates with **HTTP Basic auth**. Create a dedicated service account on the instance for it.

The account must satisfy the polled tables' ACLs. Out of the box, `sys_audit` is readable by the `admin` and `security_admin` roles ([Exploring Auditing](https://www.servicenow.com/docs/r/zurich/platform-security/exploring-auditing.html)); many deployments instead create a custom read-only role/ACL for the integration account — work with your ServiceNow administrator.

An authentication/authorization failure (HTTP 401/403) stops the adapter so a misconfiguration is surfaced loudly. Note that ServiceNow reports both bad credentials and missing table ACLs this way.

> ⚠️ ServiceNow applies `sysparm_limit` **before** ACL evaluation, so an account with partial read access silently receives partial pages. The adapter follows the API's `Link: rel="next"` header (not page sizes) and is correct either way, but an account that can read the whole table avoids wasted requests and surprises.

## How polling works

Each feed keeps a per-feed **checkpoint** on its timestamp column (`sys_created_on`, a UTC `yyyy-MM-dd HH:mm:ss` value). Every poll queries records at or after the checkpoint, oldest-first, walking pages until the API stops advertising a next page; the checkpoint then advances to the newest record processed.

- A poll that fails midway does **not** advance the checkpoint — the same range is retried on the next interval, so failures never open a gap.
- The checkpoint filter is inclusive, so boundary records are re-read; an in-memory deduper keyed on `sys_id` ships each record exactly once.
- A poll capped by `max_pages` still advances the checkpoint, so the next poll picks up exactly where it left off.

Transient API failures (HTTP 5xx, 429, network errors) are retried with exponential backoff, honoring a 429's `Retry-After` delay. ServiceNow instances have no default REST rate limit, but administrators can configure [rate limit rules](https://www.servicenow.com/docs/r/zurich/api-reference/rest-api-explorer/inbound-REST-API-rate-limiting.html).

The rotating tables (`syslog*` ~8 weeks, `sysevent` ~7 days — see [Log history](https://www.servicenow.com/docs/r/zurich/platform-security/r_LogHistory.html)) bound how far `backfill` can usefully reach.

For customers licensed for ServiceNow's [Log Export Service](https://www.servicenow.com/docs/r/zurich/platform-security/les-intro.html) (Kafka-based streaming export), that push path can be bridged into LimaCharlie instead; this adapter exists so no Store app, entitlement, MID server or Kafka consumer is required.

## What the data looks like

Each record ships verbatim under an `EventType` matching the feed's `name`. A `sys_audit` record:

```json
{
  "sys_id": "b1c3d2e4f5a601001a2b3c4d5e6f7a8b",
  "tablename": "incident",
  "fieldname": "assigned_to",
  "documentkey": "9d385017c611228701d22104cc95c371",
  "user": "jane.doe",
  "oldvalue": "46d44a5dc0a8010e0000c8b06e0b1971",
  "newvalue": "5137153cc611227c000bbd1bd8cd2007",
  "reason": "",
  "record_checkpoint": "7",
  "internal_checkpoint": "",
  "sys_created_on": "2026-06-11 09:14:33",
  "sys_created_by": "jane.doe"
}
```

The adapter requests database values (`sysparm_display_value=false`, always UTC) and plain sys_ids for reference fields (`sysparm_exclude_reference_link=true`), so payloads are stable regardless of the service account's locale.

## CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page. The defaults are usually sufficient — supplying `instance`, `username` and `password` is enough to pull `sys_audit`.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter servicenow \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$INSTALLATION_KEY \
  client_options.platform=json \
  client_options.sensor_seed_key=servicenow \
  instance=example \
  username=$SERVICENOW_USERNAME \
  password=$SERVICENOW_PASSWORD
```

## Infrastructure as Code Deployment

```yaml
# For cloud sensor deployment, store credentials as hive secrets:
#
#   password: "hive://secret/servicenow-password"

sensor_type: "servicenow"
servicenow:
  instance: "example"
  username: "lc.collector"
  password: "hive://secret/servicenow-password"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_SERVICENOW"
    hostname: "servicenow-adapter"
    platform: "json"
    sensor_seed_key: "servicenow-sensor"
    mapping:
      event_time_path: "sys_created_on"
    indexing: []
```

### Custom feeds

Override `feeds` to add tables or replace the default entirely. The list is **replacing**, not merging — re-declare `sys_audit` if you want to keep it. The example below keeps the default and adds login telemetry and the transaction log:

```yaml
servicenow:
  instance: "example"
  username: "lc.collector"
  password: "hive://secret/servicenow-password"
  feeds:
    - table: sys_audit
    - name: login_events
      table: sysevent
      query: "name=login^ORname=login.failed"
    - name: transactions
      table: syslog_transaction
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_SERVICENOW"
    platform: "json"
    sensor_seed_key: "servicenow-sensor"
```

## Sample Rule

The adapter ships each record under an `EventType` matching the feed's `name`, so D&R rules can route directly on the feed:

```yaml
# Detection — flag changes made to a user's roles in ServiceNow.
event: sys_audit
op: is
path: event/tablename
value: sys_user_has_role

# Response
- action: report
  name: ServiceNow user role change
```

## API Docs

- [Table API reference](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_TableAPI.html)
- [Sys Audit table](https://www.servicenow.com/docs/r/zurich/platform-security/c_UnderstandingTheSysAuditTable.html)
- [Transaction logs](https://www.servicenow.com/docs/r/zurich/platform-security/r_TransactionLogs.html)
- [Login events in the event queue](https://www.servicenow.com/docs/r/zurich/platform-security/authentication/r_EventQueueLoginEvents.html)
