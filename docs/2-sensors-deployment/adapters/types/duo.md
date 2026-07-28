# Duo

## Overview

This Adapter connects to the Duo Admin API and fetches logs from it.

## Configurations

Adapter Type: `duo`

- `client_options`: see [common adapter configuration](../usage.md).
- `integration_key`: an integration key that you create in Duo and associate with your "app".
- `secret_key`: the secret key for your "app".
- `api_hostname`: the DNS name for your "app". Duo gives you this value.

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:
#   integration_key: "hive://secret/duo-integration-key"
#   secret_key: "hive://secret/duo-secret-key"

sensor_type: "duo"
  duo:
    integration_key: "YOUR_DUO_INTEGRATION_KEY_DIXXXXXXXXXXXXXXXXXX"
    secret_key: "YOUR_DUO_SECRET_KEY_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    api_hostname: "api-xxxxxxxx.duosecurity.com"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_DUO"
      hostname: "duo-security-adapter"
      platform: "duo"
      sensor_seed_key: "duo-sensor-prod"
```

## API Doc

See the [official documentation](https://duo.com/docs/adminapi).
