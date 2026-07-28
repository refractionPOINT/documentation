# IT Glue

## Overview

This Adapter connects to IT Glue and gets activity logs.

## Deployment Configurations

All adapters support the same `client_options`. Always set them when you use the binary adapter or create a webhook adapter. If you use an Adapter helper in the web app, you do not need to set these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) for this adapter.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, such as `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name for this adapter. LimaCharlie generates Sensor IDs (SID) from this name. See below.

### Adapter-specific Options

Adapter Type: `itglue`

- `token`: your API key/token for IT Glue

### Infrastructure as Code Deployment

```python
# For Cloud Sensor configurations, use:
#        token: "hive://secret/itglue-api-token"

sensor_type: "itglue"
itglue:
  token: "hive://secret/itglue-api-token"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_ITGLUE"
    hostname: "itglue-adapter"
    platform: "json"
    sensor_seed_key: "itglue-audit-sensor"
    mapping:
      sensor_hostname_path: "attributes.resource_name"
      event_type_path: "attributes.action"
      event_time_path: "attributes.created_at"
    indexing: []
```

## API Doc

See the official [documentation](https://api.itglue.com/developer/).
