# Proofpoint TAP

## Overview

This Adapter allows you to connect to the [Proofpoint Targeted Attack Protection (TAP) SIEM API](https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/SIEM_API) to fetch email security events — blocked and delivered messages with threats, and blocked and permitted URL clicks.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `proofpoint_tap`

- `principal`: your Proofpoint TAP **Service Principal**.
- `secret`: the **Secret** paired with the Service Principal.

The adapter authenticates with HTTP Basic auth (`principal` / `secret`) and polls `https://tap-api-v2.proofpoint.com/v2/siem/all`.

### Getting Your Credentials

1. In the Proofpoint TAP dashboard, go to **Settings → Connected Applications**.
2. Create a **Service Principal**.
3. Copy the **Service Principal** (`principal`) and its **Secret** (`secret`).

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   principal: "hive://secret/proofpoint-principal"
#   secret: "hive://secret/proofpoint-secret"

sensor_type: "proofpoint_tap"
proofpoint_tap:
  principal: "hive://secret/proofpoint-principal"
  secret: "hive://secret/proofpoint-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_PROOFPOINT"
    hostname: "proofpoint-tap-adapter"
    platform: "proofpoint"
    sensor_seed_key: "proofpoint-tap-sensor"
```

## API Doc

See the official [Proofpoint TAP SIEM API documentation](https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/SIEM_API).
