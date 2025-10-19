# Azure Monitor

Azure Monitor Logs are a feature of Azure Monitor that collect and organize log and performance data from monitored resources. More information on Azure Monitor Logs can be found [here](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-platform-logs).

LimaCharlie can ingest and natively parse Azure Monitor Logs.

## Log Ingestion

Azure Monitor logs can be ingested via:

  * [Azure Event Hub](../adapter-types-azure-event-hub.md)

  * LimaCharlie [Webhooks](../../Adapter%20Tutorials/tutorial-creating-a-webhook-adapter.md)

Upon ingestion, the log `category` field is used to define the Event Type.
