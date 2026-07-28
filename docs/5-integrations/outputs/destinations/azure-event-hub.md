# Azure Event Hub

Output events and detections to an Azure Event Hub (similar to PubSub and Kafka).

- `connection_string`: the connection string provided by Azure.

The connection string must end with `;EntityPath=your-hub-name`. The "Connection String" from Azure sometimes does not include this part.

Example:

```text
connection_string: Endpoint=sb://lc-test.servicebus.windows.net/;SharedAccessKeyName=lc;SharedAccessKey=jidnfisnjfnsdnfdnfjd=;EntityPath=test-hub
```

## Related articles

- [Azure Kubernetes Service (AKS)](../../../2-sensors-deployment/adapters/types/azure/kubernetes-service.md)
- [Azure Monitor](../../../2-sensors-deployment/adapters/types/azure/monitor.md)
- [Azure Network Security Group](../../../2-sensors-deployment/adapters/types/azure/network-security-group.md)
- [Azure SQL Audit Logs](../../../2-sensors-deployment/adapters/types/azure/sql-audit-logs.md)
- [Azure Event Hub](../../../2-sensors-deployment/adapters/types/azure-event-hub.md)
- [Microsoft Entra ID](../../../2-sensors-deployment/adapters/types/microsoft-entra-id.md)
- [Azure](../../extensions/cloud-cli/azure.md)

## What's Next

- [Azure Storage Blob](azure-storage-blob.md)
