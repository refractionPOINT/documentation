# CrowdStrike Falcon ("falconcloud") Specific Docs: https://docs.limacharlie.io/docs/adapter-types-crowdstrike

sensor_type: "falconcloud"
  falconcloud:
    client_id: "YOUR_CROWDSTRIKE_FALCON_API_CLIENT_ID"
    client_secret: "YOUR_CROWDSTRIKE_FALCON_API_CLIENT_SECRET"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_FALCONCLOUD"
      hostname: "crowdstrike-falcon-adapter"
      platform: "falconcloud"
      sensor_seed_key: "falcon-cloud-sensor"
      indexing: []
    # Optional configuration
    write_timeout_sec: 600  # Default: 10 minutes
    is_using_offset: false  # Default: false (recommended)
    offset: 0               # Only used if is_using_offset is true
```

## API Doc

See the official [documentation](https://developer.crowdstrike.com/docs/openapi/) and [additional docs on the library used to access the Falcon APIs](https://github.com/CrowdStrike/gofalcon).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.