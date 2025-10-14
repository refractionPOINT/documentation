# 1Password

[1Password](https://1password.com/) provides an events API to fetch audit logs. Events can be ingested directly via a cloud-to-cloud or CLI Adapter.

See 1Password's official API documentation [here](https://developer.1password.com/docs/events-api/reference/).

1Password telemetry can be addressed via the `1password` platform.

## Adapter Deployment

1Password events can be collected directly from the 1Password API, via a cloud-to-cloud Adapter, or via the CLI Adapter. 1Password adapters require the following options:

* `token`: the API token provisioned through 1password.
* `endpoint`: the API endpoint to use, depending on your 1password plan, see their documentation below.

You can generate an access token from 1Password at [this link](https://support.1password.com/events-reporting/).

## Cloud-to-Cloud Adapter

LimaCharlie offers a 1Password guided configuration in the web UI. From your 1Password instance, you will need:

* 1Password API Access Token
* Endpoint; one of the following:
  + 1Password.com (Business)
  + 1Password.com (Enterprise)
  + 1Password.ca
  + 1Password.eu

After providing an [Installation Key](/v2/docs/installation-keys), provide the required values and LimaCharlie will establish a Cloud Adapter for 1Password events

### Infrastructure as Code Deployment

LimaCharlie IaC Adapter can also be used to ingest 1Password events.

```yaml
# 1Password Specific Docs: https://docs.limacharlie.io/docs/adapter-types-1password

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

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.