# Azure Kubernetes Service (AKS)

[Azure Kubernetes Service](https://azure.microsoft.com/en-us/products/kubernetes-service) (AKS) is a quick way to start developing and deploying cloud-native apps in Azure. LimaCharlie can ingest Azure Kubernetes Service logs.

More information about Azure Kubernetes logs and metrics can be found [here](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-livedata-overview).

## Log Ingestion

AKS logs can be ingested via:

  * [Azure Event Hub](/v2/docs/adapter-types-azure-event-hub)

  * LimaCharlie [Webhooks](/v2/docs/tutorial-creating-a-webhook-adapter)




Upon ingestion, the log `category` field is used to define the Event Type.
