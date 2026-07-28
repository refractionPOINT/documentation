# JSON

## Overview

This Adapter lets you ingest JSON-formatted logs from a file. It uses the [File](file.md) adapter with `client_options.platform` set to `json`.

Each line of the file must contain one complete JSON object. If a JSON object spans multiple lines, use the `multi_line_json: true` option.

Adapter type: `file`

## Configuration

All adapters support the same `client_options`. Always specify these options if you use the binary adapter or create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself with LimaCharlie.
- `client_options.platform`: set to `json` for JSON-formatted logs.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter. Sensor IDs (SID) are generated from this name.

This adapter uses the file adapter, so all [File adapter options](file.md) are available. These options include `no_follow`, `backfill`, `poll`, `multi_line_json`, and more.

### Configuration File Example

```yaml
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "json"
    sensor_seed_key: "json-logs"
    hostname: "app-server-01"
    mapping:
      event_type_path: "event_type"
      event_time_path: "timestamp"
  file_path: "/var/log/app/*.json"
```

For multi-line JSON (where a single JSON object spans multiple lines):

```yaml
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "json"
    sensor_seed_key: "json-logs"
    mapping:
      event_type_path: "action"
  file_path: "/var/log/app/events.json"
  multi_line_json: true
```

## CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter file client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
file_path=/path/to/file
```
