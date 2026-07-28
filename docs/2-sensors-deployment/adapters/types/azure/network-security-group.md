# Azure Network Security Group

Azure network security groups filter network traffic between Azure resources in an Azure virtual network. For more detail, see the Microsoft [Network security groups overview](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview).

LimaCharlie can ingest and parse Azure Network Security Group logs directly.

## Log Ingestion

You can ingest Azure Network Security Group logs through:

- [Azure Event Hub](../azure-event-hub.md)
- LimaCharlie [Webhooks](../../tutorials/webhook-adapter.md)

When you configure the adapter, set `client_options.platform: azure_network_security_group` to select the dedicated parser. At ingestion, the log `category` field sets the event type, and the `time` field supplies the event timestamp.
