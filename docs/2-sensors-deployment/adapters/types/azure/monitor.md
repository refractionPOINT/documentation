# Azure Monitor

Azure Monitor Logs are a feature of Azure Monitor. They collect and organize log data and performance data from monitored resources. For more detail, see the Microsoft [Azure Monitor Logs reference](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-platform-logs).

LimaCharlie can ingest and parse Azure Monitor Logs directly.

## Log Ingestion

You can ingest Azure Monitor logs through:

- [Azure Event Hub](../azure-event-hub.md)
- LimaCharlie [Webhooks](../../tutorials/webhook-adapter.md)

When you configure the adapter, set `client_options.platform: azure_monitor` to select the dedicated parser. At ingestion, the log `category` field sets the event type, and the `time` field supplies the event timestamp.
