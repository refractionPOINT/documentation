# Check Point Harmony

## Overview

This Adapter ingests events from [Check Point Harmony](https://www.checkpoint.com/harmony/) into LimaCharlie through the Infinity Portal APIs. The adapter supports two independent sources:

- **Infinity Events** — the unified Logs-as-a-Service stream that covers Harmony Endpoint, Harmony Email & Collaboration, Harmony Mobile, Harmony Connect, and Harmony Browse.
- **Entities** — polls the Harmony Email & Collaboration (HEC) `search/query` entity API. This one source runs a list of *named queries*. Each query is one feed that the server filters. Restore requests on quarantined mail, watches on recipient, subject, or DLP, and the unfiltered email firehose are all different queries on the same engine. A new scenario needs no change to the Go code.

Both sources share one set of Infinity Portal API credentials. You must turn on at least one source. If both sources are off, the adapter does not start.

The previous `emails` firehose source is now a preset in `entities`. See [Migrating from `emails`](#migrating-from-emails) below.

## Deployment Configurations

All adapters support the same `client_options`. Always specify them when you use the binary adapter or create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, for example `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name that you choose for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name. See below.

### Adapter-specific Options

Adapter Type: `harmony`

**Top-level credentials (always required):**

- `client_id`: Infinity Portal Client ID. Create it under *Global Settings → API Keys*. For Infinity Events, the key must include the *Logs as a Service* service. For the Entities source, the key must include the *Harmony Email & Collaboration* service. One key with both services attached is supported.
- `access_key`: Infinity Portal Access Key paired with the Client ID above.
- `url` *(optional)*: Infinity Portal gateway base URL. Defaults to `https://cloudinfra-gw.portal.checkpoint.com`. If your tenant is in a regional data center, use the regional variant, for example `https://cloudinfra-gw-us.portal.checkpoint.com`. In each region, `/app/laas-logs-api` and `/app/hec-api` share the same hostname.

[`time.ParseDuration`](https://pkg.go.dev/time#ParseDuration) parses all the duration fields below — for example `"60s"`, `"5m"`, `"1h30m"`, `"360h"`.

**`events` block — Infinity Events source:**

- `events.enabled`: set to `true` to turn on the source.
- `events.cloud_services` *(optional)*: list of the cloud services to pull events for. The names must match the gateway exactly. The Email service is `Harmony Email & Collaboration` with an ampersand, and the gateway rejects the spelling with the word "and". Defaults to the full Harmony suite: `Harmony Endpoint`, `Harmony Email & Collaboration`, `Harmony Mobile`, `Harmony Connect`, `Harmony Browse`.
- `events.filter` *(optional)*: Infinity Events query filter that applies to every cloud service.
- `events.poll_interval` *(optional)*: time between polls. Defaults to `60s`.
- `events.page_limit` *(optional)*: page size for the records-retrieval API. Defaults to `100`. The gateway rejects values below `10` with HTTP 400.
- `events.limit` *(optional)*: maximum number of records returned for each cloud service in each poll. Defaults to `5000`.

If a configured `cloud_service` is not provisioned for the tenant, the gateway returns the query in state `Canceled`. The adapter writes one warning for each poll and continues. This condition is not an error. To stop the warning, remove the service from `cloud_services`.

**`entities` block — HEC entity-query source:**

- `entities.enabled`: set to `true` to turn on the source.
- `entities.queries`: list of named queries. Each entry is one independent feed. Each feed has its own dedup state and its own `_lc_harmony_query` annotation downstream.

Each `entities.queries` entry supports the following fields:

| Field | Default | Notes |
| --- | --- | --- |
| `name` | — (required) | Identifier for the feed. Must be unique within `entities.queries`. Appears in errors and as `_lc_harmony_query`. |
| `saas` | `[office365_emails, google_mail]` | The SaaS platforms to query. The adapter queries each one independently. Only `office365_emails` and `google_mail` are supported. |
| `filter` | `[]` | List of `{attr, op, value}` predicates that pass through as `entityExtendedFilter`. The gateway combines them with AND. An empty list is allowed. The entity window then bounds the query, plus the injected cursor predicate in cursor mode. |
| `cursor_field` | `""` | Empty → window mode. Set to `entityPayload.<k>` or `entityInfo.<k>` (must reference a timestamp-typed field) → cursor mode. See [Two cursor modes](#two-cursor-modes) below. |
| `include_splits` | `false` | If `true`, send `entityPayload.emailSplit == "split"` master records with their child copies (firehose semantics). The default skips them, so one query does not emit the same email twice. |
| `lookback` | `1h` (window) / `360h` (cursor) | Floor on `entityFilter.startDate` (received time). Duration string. |
| `initial_lookback` | `1h` | Cursor mode only: how far back the cursor starts on the first poll. Duration string. |
| `poll_interval` | `5m` | Time between polls. Duration string. |

Each predicate in `filter` is one server-side `entityExtendedFilter` clause:

```yaml
filter:
  - {attr: <saasAttrName>, op: <saasAttrOp>, value: "<saasAttrValue>"}
```

`attr` is a Check Point [saasAttrName](https://sc1.checkpoint.com/documents/Harmony_Email_and_Collaboration_API_Reference/Topics-HEC-Avanan-API-Reference-Guide/Managing-Secured-Entities/Search-query.htm), for example `entityPayload.subject`, `entityPayload.recipients`, or `entityPayload.isRestoreRequested`. `op` is one of `is`, `isNot`, `contains`, `notContains`, `startsWith`, `isEmpty`, `isNotEmpty`, `greaterThan`, `lessThan`. `value` is a string. Write a boolean as the string `"true"` or `"false"`. The adapter rejects an unknown op at startup, so a typo fails immediately instead of matching nothing.

#### Two cursor modes

| Mode | When to use | `entityFilter` sent | Cursor |
| --- | --- | --- | --- |
| **Window mode** (`cursor_field` empty) | The matching email is itself recent — content/recipient/detection filters, or the unfiltered firehose. | `saas` + `startDate` + `endDate` + `saasEntity` (received-time window). | Rolling window + dedup. |
| **Cursor mode** (`cursor_field` set) | The event of interest is separated in time from the receipt of the email — for example a restore request on an old quarantined email. | `saas` + wide `startDate` only — no `endDate`, no `saasEntity`. | The adapter injects `{cursor_field} greaterThan {cursor}` and moves `cursor` to the newest value that it sees. |

The predicates of a *filtered* query (non-empty `filter`) bound it on the server, so its cost does not change with total mail volume. The **unfiltered firehose preset** (window mode, no `filter`, `include_splits: true`) is the exception. Only the received-time window bounds it. On a tenant with very high mail volume, a long `lookback` can reach the record ceiling of the gateway for each query (about 10,000 records, oldest first). Keep `lookback` short for that preset (the 1h default is intentional), or use a filtered query.

> **Restore requests require cursor mode.** A window-mode query (or the firehose preset) cannot show a restore request. The window filters on the *received* time of the email. The quarantined email can arrive hours, days, or months before the restore request, so it is not in a recent received-time window. Use the `restore_requests` preset below.

#### Annotations

The adapter adds annotations to every record. Use them to route the record downstream:

- `_lc_harmony_source` — `infinity_events` or `entities`.
- `_lc_harmony_service` — the Infinity Events cloud service (events source only).
- `_lc_harmony_query` — the entities query's `name` (entities source only).
- `_lc_harmony_saas` — the HEC SaaS platform (entities source only).

#### Example presets

Restore requests for quarantined email — the canonical cursor-mode preset. It is the same as the Check Point XSOAR `restore_requests` preset:

```yaml
harmony:
  entities:
    enabled: true
    queries:
      - name: restore_requests
        saas: [office365_emails, google_mail]
        filter:
          - {attr: entityPayload.isRestoreRequested, op: is, value: "true"}
        cursor_field: entityPayload.restoreRequestTime
        lookback: 360h          # 15 days — how old the underlying email may be
        initial_lookback: 1h    # how far back the cursor starts on first poll
        poll_interval: 5m
```

Email firehose (window mode, no filter, splits included) — equivalent to the old `emails` source:

```yaml
harmony:
  entities:
    enabled: true
    queries:
      - name: emails
        saas: [office365_emails, google_mail]
        include_splits: true
        lookback: 1h
        poll_interval: 5m
```

Subject / sender watch (window mode):

```yaml
harmony:
  entities:
    enabled: true
    queries:
      - name: invoice_subject_watch
        saas: [office365_emails]
        filter:
          - {attr: entityPayload.subject,    op: contains, value: "INVOICE"}
          - {attr: entityPayload.fromDomain, op: is,       value: "example.com"}
        lookback: 1h
        poll_interval: 5m
```

You can list many queries under one source. Each query runs independently, with its own dedup state and its own `_lc_harmony_query` annotation.

### CLI Deployment

Get the [Adapter downloads](../deployment.md) from the deployment page. The adapter accepts dot-notation flags for the nested `events.*` and `entities.*` fields. Pass `entities.queries` as one JSON string.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter harmony client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
client_id=$CHECKPOINT_CLIENT_ID \
access_key=$CHECKPOINT_ACCESS_KEY \
events.enabled=true \
'events.cloud_services=Harmony Endpoint,Harmony Email & Collaboration' \
entities.enabled=true \
'entities.queries=[{"name":"restore_requests","filter":[{"attr":"entityPayload.isRestoreRequested","op":"is","value":"true"}],"cursor_field":"entityPayload.restoreRequestTime","lookback":"360h","initial_lookback":"1h","poll_interval":"5m"}]'
```

### Infrastructure as Code Deployment

```yaml
# For cloud sensor deployment, store credentials as hive secrets:
#
#   client_id: "hive://secret/checkpoint-harmony-client-id"
#   access_key: "hive://secret/checkpoint-harmony-access-key"

sensor_type: "harmony"
harmony:
  client_id: "hive://secret/checkpoint-harmony-client-id"
  access_key: "hive://secret/checkpoint-harmony-access-key"
  # Optional: regional gateway (defaults to the global one if omitted)
  # url: "https://cloudinfra-gw-us.portal.checkpoint.com"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_HARMONY"
    hostname: "checkpoint-harmony-adapter"
    platform: "json"
    sensor_seed_key: "checkpoint-harmony-sensor"
    mapping:
      event_type_path: "_lc_harmony_source"
      event_time_path: "time"
    indexing: []
  events:
    enabled: true
    # Optional — defaults to the full Harmony suite if omitted
    cloud_services:
      - "Harmony Endpoint"
      - "Harmony Email & Collaboration"
      - "Harmony Mobile"
      - "Harmony Connect"
      - "Harmony Browse"
  entities:
    enabled: true
    queries:
      - name: restore_requests
        saas: [office365_emails, google_mail]
        filter:
          - {attr: entityPayload.isRestoreRequested, op: is, value: "true"}
        cursor_field: entityPayload.restoreRequestTime
        lookback: 360h
        initial_lookback: 1h
        poll_interval: 5m
```

## Configuring a Check Point Harmony Adapter in the Web UI

### Preparing Infinity Portal credentials

1. Sign in to the [Infinity Portal](https://portal.checkpoint.com/) with an account that can manage API keys.
2. Go to *Global Settings → API Keys → New*.
3. Attach the services that your adapter needs:
    - *Logs as a Service* for the Infinity Events source.
    - *Harmony Email & Collaboration* for the Entities source.
    - One key with both services attached is supported.
4. Copy the **Client ID** and the **Access Key**. The portal shows the Access Key one time only. Keep it in a safe location.
5. Record the **Authentication URL** that the portal shows next to the key. If it points at a regional gateway (`cloudinfra-gw-us.portal.checkpoint.com`, `cloudinfra-gw-eu.portal.checkpoint.com`, etc.), give that hostname as the `url` value of the adapter.

### Setting up the Adapter

In the LimaCharlie web app, select `+ Add Sensor`. Then choose **Check Point Harmony**.

Select or create an Installation Key for this adapter. Then complete the form:

| Field | Value |
| --- | --- |
| Client ID | Infinity Portal Client ID |
| Access Key | Infinity Portal Access Key |
| URL | *(optional)* Regional gateway base URL, if your tenant is not on the global gateway |
| Events Enabled | Toggle on to ingest Infinity Events. Defaults to on. |
| Events Cloud Services | *(optional)* Comma-separated cloud services. Leave blank for the full Harmony suite. |
| Events Filter | *(optional)* Infinity Events query filter |
| Entities Enabled | Toggle on to poll the HEC entity-query source |
| Entities Queries | *(optional)* JSON array of named entity queries. For the schema and the presets, see [Adapter-specific Options](#adapter-specific-options) above. |

Turn on *Events Enabled*, *Entities Enabled*, or both. If both are off, the adapter does not start.

Click `Complete Cloud Installation`. LimaCharlie authenticates against the Infinity Portal and starts to poll.

## Sample Rule

After ingestion, D&R rules can reference Harmony events directly. The adapter annotates every record with `_lc_harmony_source`, so you can pivot on the source API. Entities records also carry `_lc_harmony_query`, so you can route each query separately:

```yaml
# Detection — flag restore requests from the entities source
event: harmony_record
op: and
rules:
  - op: is
    path: event/_lc_harmony_source
    value: entities
  - op: is
    path: event/_lc_harmony_query
    value: restore_requests

# Response
- action: report
  name: Harmony Restore Request
```

For the unfiltered firehose query, narrow the detection with the verdict and lifecycle fields on each entity (under `event/entityInfo` and the entity payload). Match only the cases that you need — for example a quarantined message or a declined restore request.

## Migrating from `emails`

The previous `emails` source is removed. An adapter config with `harmony.emails: {enabled: true}` fails Validate at startup. The message points to this guide.

**Before:**

```yaml
harmony:
  emails:
    enabled: true
    saas: [office365_emails, google_mail]
    lookback: 1h
    poll_interval: 5m
```

**After:**

```yaml
harmony:
  entities:
    enabled: true
    queries:
      - name: emails              # pick any name; appears as _lc_harmony_query
        saas: [office365_emails, google_mail]
        include_splits: true      # matches the old firehose semantics
        lookback: 1h
        poll_interval: 5m
```

Update the downstream rules and dashboards that filter on `_lc_harmony_source: emails`. They must filter on `_lc_harmony_source: entities`. You can also add `_lc_harmony_query: emails` to limit the filter to this feed.

## API Docs

- Infinity Events (Logs-as-a-Service): [Check Point Infinity Events Reference](https://app.swaggerhub.com/apis-docs/Check-Point/infinity-events)
- Harmony Email & Collaboration entity API: [HEC API Reference](https://sc1.checkpoint.com/documents/Infinity_Portal/WebAdminGuides/EN/Harmony-Email-and-Collaboration-Admin-Guide/Default.htm)
- HEC `search/query` endpoint: [Search query reference](https://sc1.checkpoint.com/documents/Harmony_Email_and_Collaboration_API_Reference/Topics-HEC-Avanan-API-Reference-Guide/Managing-Secured-Entities/Search-query.htm)
- Infinity Portal authentication: [Infinity Portal API Authentication](https://app.swaggerhub.com/apis-docs/Check-Point/infinity-portal-auth/1.0)
