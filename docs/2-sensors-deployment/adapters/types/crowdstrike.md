# CrowdStrike Falcon Cloud

## Overview

This Adapter allows you to connect to CrowdStrike Falcon Cloud to stream events as they happen in the CrowdStrike Falcon Console.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `falconcloud`

- `client_id`: your CrowdStrike Falcon Cloud client ID
- `client_secret`: your CrowdStrike Falcon Cloud client secret
- `is_using_offset`: if `true`, start reading the stream at `offset` and apply no time filter. Defaults to `false`.
- `offset`: the stream offset to start from. Only used when `is_using_offset` is `true`.
- `not_before`: RFC 3339 timestamp such as `2026-06-01T00:00:00Z`. Events created before it are dropped. Only used when `is_using_offset` is `false`. If omitted, the adapter uses the time it started.
- `write_timeout_sec`: how long, in seconds, the adapter waits to hand an event to LimaCharlie. Defaults to `600`.

### Credentials

Create an API client in the Falcon console (**Support and resources > API clients and keys**) with the **Event streams: Read** scope. The adapter uses it to list the available event streams.

### One adapter per API client

CrowdStrike allows only one consumer per stream. Run a single adapter instance per API client, and don't point two adapters, or an adapter and another integration, at the same stream. If the adapter finds no available stream it stops with an error telling you to make sure no other instance is running.

### Resume behavior

The adapter does not store its position between runs. Each start opens every stream CrowdStrike lists for the API client and works out where to resume:

- **Default (`is_using_offset: false`)**: the adapter reads from offset `0`, which is the beginning of the window CrowdStrike retains (about 30 days), and drops every event whose creation time is before `not_before`, or before the adapter's start time when `not_before` is unset. The adapter still receives the whole retained window on every start and discards what the filter rejects, so on a busy tenant expect a long catch-up after each restart.
- **After a restart**: with no `not_before`, events created while the adapter was down are dropped, because the start time moves forward on each run. To cover a gap, set `not_before` to a time before the outage. Events already delivered after that time are delivered again.
- **Explicit offset (`is_using_offset: true`)**: the adapter starts reading at `offset` and filters nothing by time. Record the offset yourself if you want to continue from a known position. `offset: 0` replays the entire retained window.

Delivered events are timestamped with the time the adapter received them, not the time CrowdStrike created them. The original creation time stays in the event's `metadata` field.

### Manual Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter falconcloud client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
client_options.mappings.event_type_path=metadata/eventType \
client_id=$CLIENT_ID \
client_secret=$CLIENT_SECRET
```

### Infrastructure as Code Deployment

```python
sensor_type: "falconcloud"
  falconcloud:
    client_id: "YOUR_CROWDSTRIKE_FALCON_API_CLIENT_ID"
    client_secret: "YOUR_CROWDSTRIKE_FALCON_API_CLIENT_SECRET"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_FALCONCLOUD"
      hostname: "crowdstrike-falcon-adapter"
      platform: "falconcloud"
      sensor_seed_key: "falcon-cloud-sensor"
      indexing: []
    # Optional configuration
    write_timeout_sec: 600  # Default: 10 minutes
    is_using_offset: false  # Default: false (recommended)
    offset: 0               # Only used if is_using_offset is true
    not_before: "2026-06-01T00:00:00Z"  # Only used if is_using_offset is false
```

## API Doc

See the official [documentation](https://developer.crowdstrike.com/docs/openapi/) and [additional docs on the library used to access the Falcon APIs](https://github.com/CrowdStrike/gofalcon).
