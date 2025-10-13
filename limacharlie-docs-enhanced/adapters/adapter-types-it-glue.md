# Adapter Documentation: https://docs.limacharlie.io/docs/adapter-types
# For Cloud Sensor configurations, use:
#        token: "hive://secret/itglue-api-token"

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

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.