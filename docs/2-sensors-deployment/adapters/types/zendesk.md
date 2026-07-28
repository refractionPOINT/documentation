# Zendesk

## Overview

This Adapter connects to Zendesk and gets [account activity logs](https://developer.zendesk.com/api-reference/ticketing/account-configuration/audit_logs/#list-audit-logs).

## Deployment Configurations

All adapters support the same `client_options`. Always set these options when you use the binary adapter or when you create a webhook adapter. If you use an Adapter helper in the web app, you do not set these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself with LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, such as `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name that you choose for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name, as described below.

### Adapter-specific Options

Adapter Type: `zendesk`

- `api_token`: your Zendesk API token
- `zendesk_domain`: your Zendesk domain, such as `initech.zendesk.com`
- `zendesk_email`: the Zendesk email address that created the API token

### CLI Deployment

You can get the [Adapter binaries](../deployment.md#adapter-binaries) on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter zendesk client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
client_options.mappings.event_type_path=action \
api_token=$API_TOKEN \
zendesk_domain='$YOUR_COMPANY.zendesk.com' \
zendesk_email=you@yourcompany.com
```

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:
#   api_token: "hive://secret/zendesk-api-token"
#   zendesk_email: "hive://secret/zendesk-email"

sensor_type: "zendesk"
zendesk:
  api_token: "hive://secret/zendesk-api-token"
  zendesk_domain: "yourcompany.zendesk.com"
  zendesk_email: "hive://secret/zendesk-api-email"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_ZENDESK"
    hostname: "zendesk-support-adapter"
    platform: "json"
    sensor_seed_key: "zendesk-audit-sensor"
    mapping:
      sensor_hostname_path: "actor_name"
      event_type_path: "action"
      event_time_path: "created_at"
    indexing: []
```

## API Doc

See the official [Zendesk audit logs API reference](https://developer.zendesk.com/api-reference/ticketing/account-configuration/audit_logs/#list-audit-logs).
