# CrowdStrike Falcon (Cloud / Event Streams)

## Overview

This Adapter connects to the [CrowdStrike Falcon Streaming API](https://www.falconpy.io/Service-Collections/Event-Streams.html) (Event Streams) to fetch detections, audit events, and other event-stream data directly from the CrowdStrike Falcon cloud.

> This is the **cloud / API** CrowdStrike adapter (`falconcloud`). It is distinct from the on-host [CrowdStrike](crowdstrike.md) EDR sensor adapter — use this one when you want to pull events from the Falcon cloud over the Streaming API rather than from an endpoint sensor.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `falconcloud`

- `client_id`: your CrowdStrike Falcon API client ID.
- `client_secret`: your CrowdStrike Falcon API client secret.
- `is_using_offset`: if `true`, resume the stream from the explicit `offset` below instead of from a point in time.
- `offset`: stream offset to resume from (used only when `is_using_offset` is `true`).
- `not_before`: only consume events at or after this time (RFC3339, e.g. `2026-06-01T00:00:00Z`). Used when `is_using_offset` is `false`; if omitted, the adapter starts from the current time.
- `write_timeout_sec`: write timeout in seconds (defaults to `600`).

The adapter authenticates with the CrowdStrike OAuth2 API credentials, discovers the available event stream, and consumes it. A unique consumer name is generated automatically per run.

> ⚠️ **One consumer per stream.** CrowdStrike allows only a single active consumer per app for a given event stream. Run only **one** instance of this adapter against a given Falcon tenant — a second concurrent consumer will fail to find an available stream.

### Getting Your Credentials

1. In the CrowdStrike Falcon console, go to **Support and resources → API Clients and Keys**.
2. Create an **API client** and grant it the **Event streams: Read** scope.
3. Copy the **Client ID** and **Client Secret** shown on creation.

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   client_id: "hive://secret/falconcloud-client-id"
#   client_secret: "hive://secret/falconcloud-client-secret"

sensor_type: "falconcloud"
falconcloud:
  client_id: "hive://secret/falconcloud-client-id"
  client_secret: "hive://secret/falconcloud-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_FALCONCLOUD"
    hostname: "falconcloud-adapter"
    platform: "falconcloud"
    sensor_seed_key: "falconcloud-sensor"
```

## API Doc

See the official [CrowdStrike Event Streams documentation](https://www.falconpy.io/Service-Collections/Event-Streams.html).
