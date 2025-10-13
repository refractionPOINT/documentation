# Google Cloud Pub/Sub Specific Docs: https://docs.limacharlie.io/docs/adapter-types-google-cloud-pubsub
sensor_type: "pubsub"
pubsub:
  sub_name: "your-pubsub-subscription-name"
  project_name: "your-gcp-project-id"
  service_account_creds: "hive://secret/gcp-pubsub-service-account"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_PUBSUB"
    platform: "json"
    sensor_seed_key: "gcp-pubsub-sensor"
    mapping:
      # Map Pub/Sub message to sensor fields
      sensor_hostname_path: "attributes.hostname"
      event_type_path: "attributes.eventType"
      event_time_path: "publishTime"
    indexing: []
  # Optional configuration
  max_ps_buffer: 1048576  # 1MB buffer (optional)
```

## API Doc

See the [official documentation](https://cloud.google.com/pubsub).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Google Cloud Platform

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.