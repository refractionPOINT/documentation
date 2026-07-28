# CrowdStrike Falcon Cloud

## Overview

This Adapter connects to CrowdStrike Falcon Cloud. It streams events as they occur in the CrowdStrike Falcon Console.

## Deployment Configurations

All adapters support the same `client_options`. Always specify them when you use the binary adapter or create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, for example `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name that you choose for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name. See below.

### Adapter-specific Options

Adapter Type: `falconcloud`

- `client_id`: your CrowdStrike Falcon Cloud client ID
- `client_secret`: your CrowdStrike Falcon Cloud client secret

### Manual Deployment

Get the [Adapter downloads](../deployment.md) from the deployment page.

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
```

## API Doc

See the official [CrowdStrike OpenAPI documentation](https://developer.crowdstrike.com/docs/openapi/) and the [documentation for the library that accesses the Falcon APIs](https://github.com/CrowdStrike/gofalcon).
