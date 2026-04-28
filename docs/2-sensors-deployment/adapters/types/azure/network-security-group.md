# Azure Network Security Group

Azure Network security groups help filter network traffic between Azure resources in an Azure virtual network. See Microsoft's [Network security groups overview](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview) for more detail.

LimaCharlie can ingest and natively parse Azure Network Security Group logs.

## Log Ingestion

Azure Network Security Group logs can be ingested via:

- [Azure Event Hub](../azure-event-hub.md)
- LimaCharlie [Webhooks](../../tutorials/webhook-adapter.md)

Upon ingestion, the log `category` field is used to define the Event Type.
