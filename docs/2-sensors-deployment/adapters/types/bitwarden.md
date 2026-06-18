# Bitwarden

## Overview

This Adapter allows you to connect to the [Bitwarden Public API](https://bitwarden.com/help/public-api/) to fetch your organization's event logs (member, group, collection, vault item and policy events).

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `bitwarden`

- `client_id`: your Bitwarden organization API `client_id`.
- `client_secret`: your Bitwarden organization API `client_secret`.
- `region`: `us` (default) or `eu` — selects the Bitwarden cloud the adapter talks to. Leave unset for `us`.
- `token_endpoint_url`: (self-hosted only) custom OAuth2 token endpoint URL. Must be set together with `events_base_url`.
- `events_base_url`: (self-hosted only) custom events API base URL. Must be set together with `token_endpoint_url`.

> `region` and the custom-URL pair are mutually exclusive: set `region` for Bitwarden Cloud (US/EU), or set both `token_endpoint_url` and `events_base_url` for a self-hosted instance — not both.

The adapter authenticates with the OAuth2 `client_credentials` grant against the Bitwarden identity endpoint (`https://identity.bitwarden.com/connect/token` for US, `https://identity.bitwarden.eu/connect/token` for EU) and polls `<events_base_url>/public/events`.

### Getting Your Credentials

The organization API key is found in the Bitwarden web vault under **Admin Console → Settings → Organization info → View API Key** (organization owner required). Copy the `client_id` and `client_secret`.

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   client_id: "hive://secret/bitwarden-client-id"
#   client_secret: "hive://secret/bitwarden-client-secret"

sensor_type: "bitwarden"
bitwarden:
  client_id: "hive://secret/bitwarden-client-id"
  client_secret: "hive://secret/bitwarden-client-secret"
  region: "us"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_BITWARDEN"
    hostname: "bitwarden-adapter"
    platform: "bitwarden"
    sensor_seed_key: "bitwarden-sensor"
```

## API Doc

See the official [documentation](https://bitwarden.com/help/public-api/).
