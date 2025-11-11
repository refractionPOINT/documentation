# Azure Event Hub

## Overview

This Adapter allows you to connect to an Azure Event Hub to fetch structured data stored there.

[Azure Event Hubs](https://azure.microsoft.com/en-us/products/event-hubs) are fully managed, real-time data ingestion services that allow for event streaming from various Microsoft Azure services. LimaCharlie can ingest either structured known data (such as JSON or XML) *or* known Microsoft data types, including:

* Azure Monitor (Platform: `azure_monitor`)
* Entra ID [formerly Azure AD] (Platform: `azure_ad`)
* Microsoft Defender (Platform: `msdefender`)

Documentation for creating an event hub can be found here [here](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-create).

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

* `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
* `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
* `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
* `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

* If using a binary Adapter, `azure_event_hub` will be the ingestion type.
* `connection_string` - The connection string provided in Azure for connecting to the Azure Event Hub, including the `EntityPath=...` at the end which identifies the Hub Name (this component is sometimes now shown in the connection string provided by Azure).

## Guided Deployment

Azure Event Hub data can be pulled via either a cloud or binary Adapter.

### Cloud-to-Cloud

LimaCharlie offers several helpers within the webapp that allow you to ingest Microsoft data, such as Entra ID or Microsoft Defender, from Azure Event Hubs.

### CLI Deployment

The following example configures a binary Adapter to collect Microsoft Defender data from an Azure Event Hub:

```
./lc_adapter azure_event_hub client_options.identity.installation_key=<INSTALLATION_KEY> \
client_options.identity.oid=<OID> \
client_options.platform=msdefender \
client_options.sensor_seed_key=<SENSOR_SEED_KEY> \
client_options.hostname=<HOSTNAME> \
"connection_string=Endpoint=sb://mynamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=fnaaaaaaaaaaaaaaak0g54alYbbbbbbbbbbbbbbbALQ=;EntityPath=lc-stream"
```

### Infrastructure as Code Deployment

```
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
