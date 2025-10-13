# Zendesk Specific Docs: https://docs.limacharlie.io/docs/adapter-types-zendesk
# For cloud sensor deployment, store credentials as hive secrets:
#   api_token: "hive://secret/zendesk-api-token"
#   zendesk_email: "hive://secret/zendesk-email"

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

See the official [documentation](https://developer.zendesk.com/api-reference/ticketing/account-configuration/audit_logs/#list-audit-logs).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.