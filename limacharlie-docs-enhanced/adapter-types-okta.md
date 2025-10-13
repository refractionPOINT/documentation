# Okta Specific Docs: https://docs.limacharlie.io/docs/adapter-types-okta
# For cloud sensor deployment, store credentials as hive secrets:

#   apikey: "hive://secret/okta-api-token"

sensor_type: "okta"
okta:
  apikey: "hive://secret/okta-api-key"
  url: "https://your-company.okta.com"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_OKTA"
    hostname: "okta-systemlog-adapter"
    platform: "json"
    sensor_seed_key: "okta-system-logs-sensor"
    mapping:
      sensor_hostname_path: "client.device"
      event_type_path: "eventType"
      event_time_path: "published"
    indexing: []
```

## API Doc

See the official [documentation](https://developer.okta.com/docs/reference/api/system-log/).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.