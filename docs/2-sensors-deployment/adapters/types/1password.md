# 1Password

[1Password](https://1password.com/) has an events API that supplies audit logs. A cloud-to-cloud adapter or a CLI adapter can ingest these events.

See [1Password's official Events API documentation](https://developer.1password.com/docs/events-api/reference/).

You address 1Password telemetry with the `1password` platform.

## Adapter Deployment

A cloud-to-cloud adapter or a CLI adapter collects 1Password events directly from the 1Password API. 1Password adapters need these options:

- `token`: the API token that you create in 1Password.
- `endpoint`: the API endpoint to use. The endpoint depends on your 1Password plan. See the 1Password documentation.

Create an access token in the [1Password events reporting documentation](https://support.1password.com/events-reporting/).

## Cloud-to-Cloud Adapter

LimaCharlie has a guided configuration for 1Password in the web app. From your 1Password instance, you need:

- 1Password API Access Token
- Endpoint; one of the following:

  - 1Password.com (Business)
  - 1Password.com (Enterprise)
  - 1Password.ca
  - 1Password.eu

Give an [Installation Key](../../installation-keys.md) and the required values. LimaCharlie then creates a cloud adapter for 1Password events.

### Infrastructure as Code Deployment

The LimaCharlie IaC adapter can also ingest 1Password events.

```python
sensor_type: "1password"
  1password:
    token: "hive://secret/your-1password-api-token-secret"
    endpoint: "business"  # or "enterprise", "ca", "eu"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_1PASSWORD"
      hostname: "1password-audit-adapter"
      platform: "json"
      sensor_seed_key: "1password-sensor-unique-name"
```
