# Azure Kubernetes Service (AKS)

[Azure Kubernetes Service](https://azure.microsoft.com/en-us/products/kubernetes-service) (AKS) is a quick way to start the development and deployment of cloud-native apps in Azure. LimaCharlie can ingest Azure Kubernetes Service logs.

Microsoft has [more information about Azure Kubernetes logs and metrics](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-livedata-overview).

## Log Ingestion

You can ingest AKS logs through:

- [Azure Event Hub](../azure-event-hub.md)
- LimaCharlie [Webhooks](../../tutorials/webhook-adapter.md)

When you configure the adapter, set `client_options.platform: azure_kubernetes_service` to select the dedicated parser. At ingestion, the log `category` field sets the event type, and the `time` field supplies the event timestamp.
