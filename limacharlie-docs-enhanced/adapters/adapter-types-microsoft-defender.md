# Adapter Documentation: https://docs.limacharlie.io/docs/adapter-types
# For cloud sensor deployment, store credentials as hive secrets:

#   tenant_id: "hive://secret/azure-tenant-id"
#   client_id: "hive://secret/defender-client-id"
#   client_secret: "hive://secret/defender-client-secret"

sensor_type: "defender"
defender:
  tenant_id: "hive://secret/azure-tenant-id"
  client_id: "hive://secret/azure-defender-client-id"
  client_secret: "hive://secret/azure-defender-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_DEFENDER"
    hostname: "ms-defender-adapter"
    platform: "json"
    sensor_seed_key: "defender-sensor"
    mapping:
      sensor_hostname_path: "machineDnsName"
      event_type_path: "alertType"
      event_time_path: "lastUpdateTime"
    indexing: []
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.