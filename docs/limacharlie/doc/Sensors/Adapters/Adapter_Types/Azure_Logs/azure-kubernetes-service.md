# Azure Kubernetes Service (AKS)

[Azure Kubernetes Service](https://azure.microsoft.com/en-us/products/kubernetes-service) (AKS) is a quick way to start developing and deploying cloud-native apps in Azure. LimaCharlie can ingest Azure Kubernetes Service logs.

More information about Azure Kubernetes logs and metrics can be found [here](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-livedata-overview).

## Log Ingestion

AKS logs can be ingested via:

* [Azure Event Hub](../adapter-types-azure-event-hub.md)
* LimaCharlie [Webhooks](../../Adapter_Tutorials/tutorial-creating-a-webhook-adapter.md)

Upon ingestion, the log `category` field is used to define the Event Type.
