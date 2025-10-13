# Duo Security Specific Docs: https://docs.limacharlie.io/docs/adapter-types-duo
# For cloud sensor deployment, store credentials as hive secrets:
#   integration_key: "hive://secret/duo-integration-key"
#   secret_key: "hive://secret/duo-secret-key"

sensor_type: "duo"
  duo:
    integration_key: "YOUR_DUO_INTEGRATION_KEY_DIXXXXXXXXXXXXXXXXXX"
    secret_key: "YOUR_DUO_SECRET_KEY_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    api_hostname: "api-xxxxxxxx.duosecurity.com"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_DUO"
      hostname: "duo-security-adapter"
      platform: "duo"
      sensor_seed_key: "duo-sensor-prod"
```

## API Doc

See the [official documentation](https://duo.com/docs/adminapi).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.