# Check Point Harmony

## Overview

This Adapter ingests events from [Check Point Harmony](https://www.checkpoint.com/harmony/) into LimaCharlie via the Infinity Portal APIs. Two independent sources are supported:

- **Infinity Events** — the unified Logs-as-a-Service stream covering Harmony Endpoint, Harmony Email & Collaboration, Harmony Mobile, Harmony Connect, and Harmony Browse.
- **Restore Requests** — polls the Harmony Email & Collaboration (HEC) entity API to surface emails with pending, restored, or declined restore requests.

Both sources share a single set of Infinity Portal API credentials. At least one source must be enabled or the adapter will refuse to start.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `harmony`

**Top-level credentials (always required):**

- `client_id`: Infinity Portal Client ID. Create under *Global Settings → API Keys*. For Infinity Events the key must include the *Logs as a Service* service; for Restore Requests it must include the *Harmony Email & Collaboration* service. A single key with both services attached is supported.
- `access_key`: Infinity Portal Access Key paired with the Client ID above.
- `url` *(optional)*: Infinity Portal gateway base URL. Defaults to `https://cloudinfra-gw.portal.checkpoint.com`. Use the regional variant (for example `https://cloudinfra-gw-us.portal.checkpoint.com`) if your tenant lives in a regional data center. Both `/app/laas-logs-api` and `/app/hec-api` share the same hostname per region.

**`events` block — Infinity Events source:**

- `events.enabled`: set to `true` to turn the source on.
- `events.cloud_services` *(optional)*: list of cloud services to pull events for. Names must match the gateway exactly — the Email service is `Harmony Email & Collaboration` (ampersand, not the word "and"), and the gateway rejects the "and" spelling. Defaults to the full Harmony suite: `Harmony Endpoint`, `Harmony Email & Collaboration`, `Harmony Mobile`, `Harmony Connect`, `Harmony Browse`.
- `events.filter` *(optional)*: Infinity Events query filter applied to every cloud service.
- `events.poll_interval` *(optional)*: polling cadence. Defaults to `60s`.
- `events.page_limit` *(optional)*: page size for the records-retrieval API. Defaults to `100`. The gateway rejects values below `10` with HTTP 400.
- `events.limit` *(optional)*: cap on records returned per cloud service per poll. Defaults to `5000`.

**`restore_requests` block — HEC Restore Requests source:**

- `restore_requests.enabled`: set to `true` to turn the source on.
- `restore_requests.saas` *(optional)*: SaaS platforms to query. Only `office365_emails` and `google_mail` are supported by HEC for the restore-request flags. Defaults to both.
- `restore_requests.poll_interval` *(optional)*: polling cadence. Defaults to `5m`.
- `restore_requests.lookback` *(optional)*: how far back to search for restore-requested emails. Defaults to `720h` (30 days) — the typical quarantine retention window.
- `restore_requests.include_resolved` *(optional)*: when `true`, also issues queries filtered on `isRestored` and `isRestoreDeclined`. The default (`false`) only queries `isRestoreRequested=true`, which assumes the flag stays set after the admin acts on the request. Enable this if your tenant clears the flag on resolution so the "restored" / "declined" transitions are still captured. Dedup eliminates any overlap.

Each record emitted by the adapter carries adapter-added annotations to make filtering easier downstream:

- `_lc_harmony_source` — `infinity_events` or `restore_requests`.
- `_lc_harmony_service` — the Infinity Events cloud service (events source only).
- `_lc_harmony_saas` — the HEC SaaS platform (restore_requests source only).
- `_lc_harmony_state` — `pending`, `restored`, or `declined` (restore_requests source only).

### CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page. The adapter accepts dot-notation flags for the nested `events.*` and `restore_requests.*` fields.

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
restore_requests.enabled=true
```

### Infrastructure as Code Deployment

```python
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
  restore_requests:
    enabled: true
    # Optional — defaults shown
    saas:
      - "office365_emails"
      - "google_mail"
    include_resolved: false
```

## Configuring a Check Point Harmony Adapter in the Web UI

### Preparing Infinity Portal credentials

1. Sign in to the [Infinity Portal](https://portal.checkpoint.com/) with an account that can manage API keys.
2. Navigate to *Global Settings → API Keys → New*.
3. Attach the services your adapter needs:
    - *Logs as a Service* for the Infinity Events source.
    - *Harmony Email & Collaboration* for the Restore Requests source.
    - A single key with both services attached is fine.
4. Copy the resulting **Client ID** and **Access Key**. The Access Key is shown only once — save it somewhere safe.
5. Note the **Authentication URL** shown next to the key. If it points at a regional gateway (`cloudinfra-gw-us.portal.checkpoint.com`, `cloudinfra-gw-eu.portal.checkpoint.com`, etc.) you will need to supply that hostname as the adapter's `url` value.

### Setting up the Adapter

Within the LimaCharlie web application, select `+ Add Sensor`, and then choose **Check Point Harmony**.

Pick or create an Installation Key for this adapter, then fill in the form:

| Field | Value |
| --- | --- |
| Client ID | Infinity Portal Client ID |
| Access Key | Infinity Portal Access Key |
| URL | *(optional)* Regional gateway base URL, if your tenant is not on the global gateway |
| Events Enabled | Toggle on to ingest Infinity Events. Defaults to on. |
| Events Cloud Services | *(optional)* Comma-separated cloud services. Leave blank for the full Harmony suite. |
| Events Filter | *(optional)* Infinity Events query filter |
| Restore Requests Enabled | Toggle on to poll HEC for restore requests |
| Restore Requests Saas | *(optional)* Comma-separated SaaS platforms (`office365_emails`, `google_mail`) |
| Restore Requests Include Resolved | Toggle on if your tenant clears `isRestoreRequested` once resolved |

At least one of *Events Enabled* or *Restore Requests Enabled* must be on or the adapter will refuse to start.

Click `Complete Cloud Installation`. LimaCharlie will authenticate against the Infinity Portal and begin polling.

## Sample Rule

When ingested, Harmony events can be referenced directly in D&R rules. The adapter annotates every record with `_lc_harmony_source` so you can pivot on the originating API:

```yaml
# Detection — flag any HEC restore request that lands in a declined state
event: harmony_record
op: and
rules:
  - op: is
    path: event/_lc_harmony_source
    value: restore_requests
  - op: is
    path: event/_lc_harmony_state
    value: declined

# Response
- action: report
  name: Harmony Email Restore Request Declined
```

## API Docs

- Infinity Events (Logs-as-a-Service): [Check Point Infinity Events Reference](https://app.swaggerhub.com/apis-docs/Check-Point/infinity-events)
- Harmony Email & Collaboration entity API: [HEC API Reference](https://sc1.checkpoint.com/documents/Infinity_Portal/WebAdminGuides/EN/Harmony-Email-and-Collaboration-Admin-Guide/Default.htm)
- Infinity Portal authentication: [Infinity Portal API Authentication](https://app.swaggerhub.com/apis-docs/Check-Point/infinity-portal-auth/1.0)
