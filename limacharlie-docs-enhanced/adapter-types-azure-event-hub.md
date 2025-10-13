# Azure Event Hub Specific Docs: https://docs.limacharlie.io/docs/adapter-types-azure-event-hub
sensor_type: "azure_event_hub"
  azure_event_hub:
    connection_string: "Endpoint=sb://your-eventhub-namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=YOUR_EVENT_HUB_SHARED_ACCESS_K
  EY_HERE;EntityPath=your-actual-event-hub-name"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_FOR_AZURE"
      hostname: "azure-eventhub-adapter"
      platform: "json"
      sensor_seed_key: "azure-eventhub-prod-sensor"
      indexing: []
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.