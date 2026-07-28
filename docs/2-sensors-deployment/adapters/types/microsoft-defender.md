# Microsoft Defender

## Overview

LimaCharlie can ingest [Microsoft 365 Defender logs](https://learn.microsoft.com/en-us/microsoft-365/security/defender/microsoft-365-defender?view=o365-worldwide) with three methods: the [Azure Event Hub](azure-event-hub.md) Adapter, the [Microsoft Defender API](https://learn.microsoft.com/en-us/defender-endpoint/api/exposed-apis-create-app-nativeapp), or a Custom Webhook

Microsoft has [documentation for creating an Event Hub](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-create).

Telemetry Platform: `msdefender`

> Use `client_options.platform: msdefender` for **both** ingestion methods. The `msdefender` parser reads the Streaming API `records` envelope (Event Hub) and also bare Graph `alerts_v2` alert objects (API adapter). It extracts event types and timestamps automatically. It maps raw device telemetry to native LimaCharlie event types (`NEW_PROCESS`, `NETWORK_CONNECTIONS`, and others), with one sensor for each Defender device. Do not use `json` instead. The `json` platform does not use this parser and needs manual field mappings.

## Data Collected

### API vs Event Hub Comparison

| Method | Data Source | What You Get | Use Case |
|--------|-------------|--------------|----------|
| **Defender API** | Microsoft Graph API | Security Alerts only | Alert-focused monitoring |
| **Azure Event Hub** | Defender Streaming API | Raw telemetry events | Full visibility into endpoint activity |

### Microsoft Defender API

The API adapter polls Microsoft Graph's `/security/alerts_v2` endpoint every 30 seconds. It gives **security alerts** from Microsoft Defender products, which include:

- Defender for Endpoint
- Defender for Office 365
- Defender for Identity
- Defender for Cloud Apps

These are curated, high-fidelity alerts that Microsoft correlated and enriched.

For alert schema details, see [Microsoft's alerts_v2 API documentation](https://learn.microsoft.com/en-us/graph/api/resources/security-alert).

### Azure Event Hub (Streaming API)

When you use Event Hub with Defender, you receive **raw telemetry** through the Defender Streaming API. The telemetry includes event tables such as:

- **DeviceProcessEvents** - Process creation and execution
- **DeviceNetworkEvents** - Network connections
- **DeviceFileEvents** - File operations
- **DeviceLogonEvents** - Authentication events
- **DeviceRegistryEvents** - Registry modifications
- **DeviceEvents** - Miscellaneous security events

This method gives full endpoint telemetry for custom detection rules and threat hunting.

For the complete list of supported streaming event types, see [Microsoft's Defender XDR streaming event types documentation](https://learn.microsoft.com/en-us/defender-xdr/supported-event-types).

### Defender API Configuration

To collect data through the Microsoft Defender API, configure an App Registration in Azure with this permission:

- `SecurityAlert.Read.All`

Then create a Defender adapter in LimaCharlie with:

- Tenant ID
- Client ID
- Client Secret

## Deployment Configurations

All adapters support the same `client_options`. Always specify these options if you use the binary adapter or create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself with LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, for example `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter. Sensor IDs (SID) are generated from this name, see below.

### Adapter-specific Options

- `connection_string` - The connection string that Azure gives you to connect to the Azure Event Hub. It includes the `EntityPath=...` at the end, which identifies the Hub Name (this component is sometimes now shown in the connection string provided by Azure).

## Guided Deployment

The LimaCharlie web app has a Microsoft Defender helper. Use it to connect to an existing Azure Event Hub and to ingest Microsoft Defender logs.

### CLI Deployment

The example configuration below ingests Microsoft Defender logs from an Azure Event Hub into LimaCharlie.

```bash
./lc_adapter azure_event_hub client_options.identity.installation_key=<INSTALLATION_KEY> \
client_options.identity.oid=<OID> \
client_options.platform=msdefender \
client_options.sensor_seed_key=<SENSOR_SEED_KEY> \
client_options.hostname=msdefender \
"connection_string=Endpoint=sb://mynamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=fnaaaaaaaaaaaaaaak0g54alYbbbbbbbbbbbbbbbALQ=;EntityPath=lc-stream"
```

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   tenant_id: "hive://secret/azure-tenant-id"
#   client_id: "hive://secret/defender-client-id"
#   client_secret: "hive://secret/defender-client-secret"

sensor_type: "defender"
defender:
  tenant_id: "hive://secret/azure-tenant-id"
  client_id: "hive://secret/azure-defender-client-id"
  client_secret: "hive://secret/azure-defender-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_DEFENDER"
    hostname: "ms-defender-adapter"
    platform: "msdefender"
    sensor_seed_key: "defender-sensor"
    indexing: []
```
