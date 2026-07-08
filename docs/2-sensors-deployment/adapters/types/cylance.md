# Cylance

## Overview

This Adapter allows you to connect to the Cylance (BlackBerry Protect) [ProtectAPI](https://developer.blackberry.com/) to fetch detections, threats, and memory-protection events.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `cylance`

- `tenant_id`: your Cylance Tenant API key (the tenant the application belongs to).
- `app_id`: your Cylance Application ID.
- `app_secret`: your Cylance Application Secret.
- `logging_base_url`: ProtectAPI base URL for your region. Defaults to `https://protectapi.cylance.com` (US). Set it to your shard, e.g. `https://protectapi-euc1.cylance.com` (EU), `https://protectapi-apne1.cylance.com` (APAC-NE), `https://protectapi-au.cylance.com` (AU), or `https://protectapi-sae1.cylance.com` (SAE).

The adapter mints a short-lived JWT from `tenant_id` / `app_id` / `app_secret`, exchanges it at `<logging_base_url>/auth/v2/token`, and polls the `/detections/v2`, `/threats/v2`, and `/memoryprotection/v2` endpoints.

### Getting Your Credentials

1. In the Cylance console, go to **Settings → Integrations** and add a new application.
2. Grant it read access to **Detections**, **Threats**, and **Memory Protection**.
3. On creation, copy the **Application ID** (`app_id`), **Application Secret** (`app_secret`), and your **Tenant API key** (`tenant_id`).

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   tenant_id: "hive://secret/cylance-tenant-id"
#   app_id: "hive://secret/cylance-app-id"
#   app_secret: "hive://secret/cylance-app-secret"

sensor_type: "cylance"
cylance:
  tenant_id: "hive://secret/cylance-tenant-id"
  app_id: "hive://secret/cylance-app-id"
  app_secret: "hive://secret/cylance-app-secret"
  logging_base_url: "https://protectapi.cylance.com"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_CYLANCE"
    hostname: "cylance-adapter"
    platform: "cylance"
    sensor_seed_key: "cylance-sensor"
```

## API Doc

See the official [BlackBerry / Cylance developer documentation](https://developer.blackberry.com/).
