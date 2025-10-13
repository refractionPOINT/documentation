# Sophos Central Specific Docs: https://docs.limacharlie.io/docs/adapter-types-sophos-central
# For cloud sensor deployment, store credentials as hive secrets:

#   clientid: "hive://secret/sophos-client-id"
#   clientsecret: "hive://secret/sophos-client-secret"
#   tenantid: "hive://secret/sophos-tenant-id"

sensor_type: "sophos"
sophos:
  clientid: "hive://secret/sophos-client-id"
  clientsecret: "hive://secret/sophos-client-secret"
  tenantid: "hive://secret/sophos-tenant-id"
  url: "https://api-us01.central.sophos.com"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_SOPHOS"
    hostname: "sophos-central-adapter"
    platform: "json"
    sensor_seed_key: "sophos-siem-sensor"
    mapping:
      sensor_hostname_path: "endpoint.hostname"
      event_type_path: "type"
      event_time_path: "raisedAt"
    indexing: []
```

## API Doc

See the official [documentation](https://developer.sophos.com/docs/siem-v1/1/overview).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.