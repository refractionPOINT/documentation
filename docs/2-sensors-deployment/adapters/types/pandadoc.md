# PandaDoc

## Overview

This Adapter lets you connect to PandaDoc and fetch [API logs](https://developers.pandadoc.com/reference/list-api-logs).

## Deployment Configurations

All adapters support the same `client_options`. Always specify these options if you use the binary adapter or create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself with LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, for example `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter. Sensor IDs (SID) are generated from this name, see below.

### Adapter-specific Options

Adapter Type: `pandadoc`

- `api_key`: your PandaDoc API key

### CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter pandadoc client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
client_options.mappings.event_type_path=method \
api_key=$API_KEY
```

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   api_key: "hive://secret/pandadoc-api-key"

sensor_type: "pandadoc"
pandadoc:
  api_key: "hive://secret/pandadoc-api-key"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_PANDADOC"
    hostname: "pandadoc-events-adapter"
    platform: "json"
    sensor_seed_key: "pandadoc-logs-sensor"
    mapping:
      sensor_hostname_path: "ip"
      event_type_path: "method"
      event_time_path: "request_time"
    indexing: []
```

## API Doc

See the official [PandaDoc API logs documentation](https://developers.pandadoc.com/reference/list-api-logs).
