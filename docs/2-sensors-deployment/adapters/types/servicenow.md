# ServiceNow

## Overview

This Adapter polls the [ServiceNow REST Table API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_TableAPI.html) and ingests ServiceNow audit and system logs into LimaCharlie. The adapter sends the events in their original ServiceNow JSON form. It does not reshape the payloads.

ServiceNow keeps its audit telemetry in plain platform tables, so the adapter is **generic by design**. Each *feed* is one table and an optional [encoded query](https://www.servicenow.com/docs/r/zurich/platform-user-interface/c_EncodedQueryStrings.html) filter. To collect one more table is a change of configuration, not a change of code.

By default, the adapter collects **`sys_audit`**, the field-level change history of ServiceNow. This table holds one record for each field change on an audited table. Each record shows the user that made the change and the old and new values. You can add other security-relevant tables as feeds:

| Table | What it carries | Caveat |
| --- | --- | --- |
| `sys_audit` | Field-level change history of audited records (the default feed). | Insert-only; no rotation. |
| `syslog_transaction` | Every transaction against the instance (UI, REST, scheduled jobs) with user, URL and source IP. | **High volume.** Rotates after ~8 weeks. |
| `sysevent` | The event log/queue, including login activity (`login`, `login.failed`, `external.authentication.succeeded`/`failed`, ...). | Rotates after ~7 days; filter with `query`. |
| `syslog` | System log (warnings/errors from instance processes). | Rotates after ~8 weeks. |
| `sys_outbound_http_log` | Outbound REST/SOAP requests made by the instance. | |

## Deployment Configurations

All adapters support the same `client_options`. Always specify these options if you use the binary adapter or if you create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, use `json`.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name.

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
| `poll_interval` | no | Wait between polls of a feed, as a Go duration in **nanoseconds** (like every duration below). Default `60000000000` (1 minute). |
| `backfill` | no | How far back the first poll reaches. Default 15 minutes. |
| `checkpoint_lag` | no | How long the incremental checkpoint stays behind the clock. This sets how late a record can become visible in the Table API (slow transactions, differences between node clocks) and still be collected. Default 5 minutes. |
| `dedupe_ttl` | no | How long the adapter remembers a record id, to stop it from shipping the record again. Default 7 days. |
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
| `max_pages` | no | Sets the maximum number of pages for each poll. Default `100`. The cap loses no data: the next poll continues from the checkpoint. |

## Authentication

The adapter authenticates with **HTTP Basic auth**. Create a dedicated service account on the instance for it.

The account must obey the ACLs of the polled tables. By default, the `admin` and `security_admin` roles can read `sys_audit` ([Exploring Auditing](https://www.servicenow.com/docs/r/zurich/platform-security/exploring-auditing.html)). Many deployments instead create a custom read-only role and ACL for the integration account. Work with your ServiceNow administrator.

Rejected credentials (HTTP 401) stop the adapter, so a bad configuration is visible immediately. An ACL denial on one table (HTTP 403) applies only to that feed. The feed ships nothing and retries at each `poll_interval`, so the adapter uses a fix to the ACL as soon as you make it. The other feeds continue to collect.

> ⚠️ ServiceNow applies `sysparm_limit` **before** it evaluates the ACLs, so an account with partial read access receives partial pages without a warning. The adapter uses the `Link: rel="next"` header of the API, not the page sizes, and is correct in both cases. But an account that can read the full table prevents unnecessary requests and unexpected results.

## How polling works

Each feed keeps its own **checkpoint** on its timestamp column (`sys_created_on`, a UTC `yyyy-MM-dd HH:mm:ss` value). Each poll queries the records at or after the checkpoint, oldest first, with the id column as a tiebreaker. Timestamps have a granularity of one second. Without a total order, a record can pass through a page boundary between two page requests. The poll reads pages until the API does not advertise a next page.

- A poll that fails in the middle does **not** advance the checkpoint. The adapter retries the same range at the next interval.
- A completed poll advances the checkpoint to `now - checkpoint_lag`. The lag gives time to records that become visible in the API after their timestamp. Later polls read the records inside the lag window again. A deduper in memory, keyed on `sys_id`, stops the adapter from shipping them two times.
- A poll that reaches the `max_pages` cap advances the checkpoint only to the newest record that it processed. The next poll continues at that point. If the checkpoint cannot advance at all, the adapter writes a clear warning. This occurs with more than `max_pages × page_size` records in one second.

Delivery is **at-least-once**. The checkpoint and the dedup state are in memory. After a restart, the adapter reads and ships up to `backfill` of recent history again. Downtime longer than `backfill` leaves a gap. Set `backfill` to more than your expected time from restart to recovery.

The adapter retries transient API failures (HTTP 5xx, 429, network errors) with exponential backoff, and obeys the `Retry-After` delay of a 429 response. ServiceNow instances have no default REST rate limit, but administrators can configure [rate limit rules](https://www.servicenow.com/docs/r/zurich/api-reference/rest-api-explorer/inbound-REST-API-rate-limiting.html).

The rotating tables (`syslog*` ~8 weeks, `sysevent` ~7 days — see [Log history](https://www.servicenow.com/docs/r/zurich/platform-security/r_LogHistory.html)) limit how far `backfill` can reach.

If you have a license for the ServiceNow [Log Export Service](https://www.servicenow.com/docs/r/zurich/platform-security/les-intro.html) (streaming export based on Kafka), you can bridge that push path into LimaCharlie instead. This adapter needs no Store app, entitlement, MID server, or Kafka consumer.

## What the data looks like

The adapter ships each record without change, under an `EventType` that matches the `name` of the feed. This is a `sys_audit` record:

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

The adapter requests database values (`sysparm_display_value=false`, always UTC) and plain sys_ids for reference fields (`sysparm_exclude_reference_link=true`). The payloads are therefore the same for each locale of the service account.

## CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page. The defaults are usually enough: give `instance`, `username`, and `password` to pull `sys_audit`.

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
```

### Custom feeds

Override `feeds` to add tables or to replace the default completely. The list **replaces** the default, it does not merge with it. Declare `sys_audit` again if you want to keep it. The example below keeps the default and adds login telemetry and the transaction log:

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

The adapter ships each record under an `EventType` that matches the `name` of the feed. D&R rules can therefore route directly on the feed:

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
