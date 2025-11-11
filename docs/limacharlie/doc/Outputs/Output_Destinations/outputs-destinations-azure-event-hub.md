# Azure Event Hub

Output events and detections to an Azure Event Hub (similar to PubSub and Kafka).

* `connection_string`: the connection string provided by Azure.

Note that the connection string should end with `;EntityPath=your-hub-name` which is sometimes missing from the "Connection String" provided by Azure.

Example:

```
connection_string: Endpoint=sb://lc-test.servicebus.windows.net/;SharedAccessKeyName=lc;SharedAccessKey=jidnfisnjfnsdnfdnfjd=;EntityPath=test-hub
```

## Related articles

* [Azure Kubernetes Service (AKS)](../../Sensors/Adapters/Adapter_Types/Azure_Logs/azure-kubernetes-service.md)
* [Azure Monitor](../../Sensors/Adapters/Adapter_Types/Azure_Logs/azure-monitor.md)
* [Azure Network Security Group](../../Sensors/Adapters/Adapter_Types/Azure_Logs/azure-network-security-group.md)
* [Azure SQL Audit Logs](../../Sensors/Adapters/Adapter_Types/Azure_Logs/azure-sql-audit-logs.md)
* [Azure Event Hub](../../Sensors/Adapters/Adapter_Types/adapter-types-azure-event-hub.md)
* [Microsoft Entra ID](../../Sensors/Adapters/Adapter_Types/adapter-types-microsoft-entra-id.md)
* [Azure](../../Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-azure.md)

## What's Next

* [Azure Storage Blob](outputs-destinations-azure-storage-blob.md)
