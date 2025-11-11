# Azure Network Security Group

Azure Network security groups help filter network traffic between Azure resources in an Azure virtual network. More information on Azure network security groups can be found [here](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview).

LimaCharlie can ingest and natively parse Azure Network Security Group logs.

## Log Ingestion

Azure Network Security Group logs can be ingested via:

* [Azure Event Hub](../adapter-types-azure-event-hub.md)
* LimaCharlie [Webhooks](../../Adapter_Tutorials/tutorial-creating-a-webhook-adapter.md)

Upon ingestion, the log `category` field is used to define the Event Type.
