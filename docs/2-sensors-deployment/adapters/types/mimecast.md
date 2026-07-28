# Mimecast

## Overview

This Adapter lets you connect to the Mimecast API and stream audit events when they occur.

## Deployment Configurations

All adapters support the same `client_options`. Always specify these options if you use the binary adapter or create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself with LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, for example `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter. Sensor IDs (SID) are generated from this name, see below.

### Adapter-specific Options

Adapter Type: `mimecast`

- `client_id`: your Mimecast client ID
- `client_secret`: your Mimecast client secret

### CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter mimecast client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
client_options.mappings.event_type_path=category \
client_id=$CLIENT_ID client_secret=$CLIENT_SECRET
```

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   client_id: "hive://secret/mimecast-client-id"
#   client_secret: "hive://secret/mimecast-client-secret"

sensor_type: "mimecast"
mimecast:
  client_id: "hive://secret/mimecast-client-id"
  client_secret: "hive://secret/mimecast-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_MIMECAST"
    hostname: "mimecast-logs-adapter"
    platform: "json"
    sensor_seed_key: "mimecast-audit-sensor"
    mapping:
      sensor_hostname_path: "sender"
      event_type_path: "eventType"
      event_time_path: "eventTime"
    indexing: []
```

## API Doc

See the official [Mimecast audit events API documentation](https://developer.services.mimecast.com/docs/auditevents/1/routes/api/audit/get-audit-events/post).
