# Azure Event Hub

## Overview

This adapter connects to an Azure Event Hub and fetches the structured data in the hub.

[Azure Event Hubs](https://azure.microsoft.com/en-us/products/event-hubs) are fully managed, real-time data ingestion services. They stream events from Microsoft Azure services. LimaCharlie can ingest known structured data, such as JSON or XML, *or* known Microsoft data types. The Microsoft data types include:

- Azure Monitor (Platform: `azure_monitor`)
- Entra ID [formerly Azure AD] (Platform: `azure_ad`)
- Microsoft Defender (Platform: `msdefender`)
- Azure Key Vault (Platform: `azure_key_vault`)
- Azure Kubernetes Service (Platform: `azure_kubernetes_service`)
- Azure Network Security Group (Platform: `azure_network_security_group`)
- Azure SQL Audit (Platform: `azure_sql_audit`)

> **Choosing the platform:** the Event Hub is only a transport. `client_options.platform` selects the LimaCharlie parser, and it must match the data that streams **into** the hub (see the list above). Use `json` only for custom or unknown data. With `json`, you must supply your own `mapping`. `azure_event_hub_namespace` is **not** a generic value for "data that arrives through an Event Hub". It ingests only the diagnostic logs of an Event Hub namespace.

Microsoft has [documentation for creating an Event Hub](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-create).

## Configuring Data Streams

When you use an Azure Event Hub, you must configure the source service to stream data to your Event Hub. The data that you receive depends on your configuration in Azure.

### For Entra ID (`azure_ad`)

Configure **Azure AD Diagnostic Settings** to stream to your Event Hub:

1. In Azure Portal, go to **Entra ID** > **Diagnostic settings**
2. Add a diagnostic setting and select your Event Hub
3. Choose which logs to stream (SignInLogs, AuditLogs, etc.)

See: [Stream Entra ID logs to Event Hub](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-stream-logs-to-event-hub)

### For Microsoft Defender (`msdefender`)

Configure **Defender Streaming API** to export raw telemetry:

1. In Microsoft Defender portal, go to **Settings** > **Streaming API**
2. Add your Event Hub connection
3. Select which event types to stream (DeviceProcessEvents, DeviceNetworkEvents, etc.)

See: [Defender XDR streaming event types](https://learn.microsoft.com/en-us/defender-xdr/supported-event-types)

### For Azure Monitor (`azure_monitor`)

Configure **Diagnostic Settings** on individual Azure resources:

1. Go to the Azure resource that you want to monitor
2. Go to **Diagnostic settings** and add a setting
3. Select your Event Hub and choose logs/metrics to stream

See: [Stream Azure platform logs to Event Hub](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/stream-monitoring-data-event-hubs)

## Deployment Configurations

All adapters support the same `client_options`. Always specify them when you use the binary adapter or create a webhook adapter. If you use an adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter uses.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, such as `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name that you choose for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name. See below.

### Adapter-specific Options

- With a binary adapter, the ingestion type is `azure_event_hub`.
- `connection_string` - The connection string that Azure supplies for the Azure Event Hub. It includes the `EntityPath=...` part at the end, which identifies the hub name (this component is sometimes now shown in the connection string provided by Azure).

## Guided Deployment

A cloud adapter or a binary adapter can pull Azure Event Hub data.

### Cloud-to-Cloud

The LimaCharlie web app has helpers that ingest Microsoft data, such as Entra ID or Microsoft Defender, from Azure Event Hubs.

### CLI Deployment

This example configures a binary adapter that collects Microsoft Defender data from an Azure Event Hub:

```bash
./lc_adapter azure_event_hub client_options.identity.installation_key=<INSTALLATION_KEY> \
client_options.identity.oid=<OID> \
client_options.platform=msdefender \
client_options.sensor_seed_key=<SENSOR_SEED_KEY> \
client_options.hostname=<HOSTNAME> \
"connection_string=Endpoint=sb://mynamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=fnaaaaaaaaaaaaaaak0g54alYbbbbbbbbbbbbbbbALQ=;EntityPath=lc-stream"
```

### Infrastructure as Code Deployment

```python
sensor_type: "azure_event_hub"
azure_event_hub:
  connection_string: "Endpoint=sb://your-eventhub-namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=YOUR_EVENT_HUB_SHARED_ACCESS_KEY_HERE;EntityPath=your-actual-event-hub-name"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_FOR_AZURE"
    hostname: "azure-eventhub-adapter"
    # Match the feed streamed into the hub: msdefender, azure_ad, azure_monitor, etc.
    # Only use "json" for custom data, together with a manual mapping.
    platform: "msdefender"
    sensor_seed_key: "azure-eventhub-prod-sensor"
    indexing: []
```
