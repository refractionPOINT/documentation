# Mimecast Specific Docs: https://docs.limacharlie.io/docs/adapter-types-mimecast
# For cloud sensor deployment, store credentials as hive secrets:

#   client_id: "hive://secret/mimecast-client-id"
#   client_secret: "hive://secret/mimecast-client-secret"

sensor_type: "mimecast"
mimecast:
  client_id: "hive://secret/mimecast-client-id"
  client_secret: "hive://secret/mimecast-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_MIMECAST"
    hostname: "mimecast-logs-adapter"
    platform: "json"
    sensor_seed_key: "mimecast-audit-sensor"
    mapping:
      sensor_hostname_path: "sender"
      event_type_path: "eventType"
      event_time_path: "eventTime"
    indexing: []
```

## API Doc

See the official [documentation](https://developer.services.mimecast.com/docs/auditevents/1/routes/api/audit/get-audit-events/post).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.