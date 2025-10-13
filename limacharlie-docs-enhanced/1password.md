# 1Password Specific Docs: https://docs.limacharlie.io/docs/adapter-types-1password
sensor_type: "1password"
  1password:
    token: "hive://secret/your-1password-api-token-secret"
    endpoint: "business"  # or "enterprise", "ca", "eu"
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

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.