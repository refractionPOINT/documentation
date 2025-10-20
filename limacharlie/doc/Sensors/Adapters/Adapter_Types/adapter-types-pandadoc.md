# PandaDoc

## Overview

This Adapter allows you to connect to PandaDoc to fetch [API logs](https://developers.pandadoc.com/reference/list-api-logs).

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

* `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
* `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
* `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
* `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `pandadoc`

* `api_key`: your PandaDoc API key

### CLI Deployment

Adapter downloads can be found [here](../adapter-deployment.md#adapter-binaries).

```
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

```
# PandaDoc Specific Docs: https://docs.limacharlie.io/docs/adapter-types-pandadoc
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

See the official [documentation](https://developers.pandadoc.com/reference/list-api-logs).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.
