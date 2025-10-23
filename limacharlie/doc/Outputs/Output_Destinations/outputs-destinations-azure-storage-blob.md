# Azure Storage Blob

Output events and detections to a Blob Container in Azure Storage Blobs.

* `secret_key`: the secret access key for the Blob Container.
* `blob_container`: the name of the Blob Container to upload to.
* `account_name`: the account name used to authenticate in Azure.

Example:

```
blob_container: testlcdatabucket
account_name: lctestdata
secret_key: dkndsgnlngfdlgfd
```

## Related articles

* [Azure Kubernetes Service (AKS)](../../Sensors/Adapters/Adapter_Types/Azure_Logs/azure-kubernetes-service.md)
* [Azure Monitor](../../Sensors/Adapters/Adapter_Types/Azure_Logs/azure-monitor.md)
* [Azure Network Security Group](../../Sensors/Adapters/Adapter_Types/Azure_Logs/azure-network-security-group.md)
* [Azure SQL Audit Logs](../../Sensors/Adapters/Adapter_Types/Azure_Logs/azure-sql-audit-logs.md)
* [Azure Event Hub](../../Sensors/Adapters/Adapter_Types/adapter-types-azure-event-hub.md)
* [Microsoft Entra ID](../../Sensors/Adapters/Adapter_Types/adapter-types-microsoft-entra-id.md)
* [Azure](../../Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-azure.md)
* [Elastic](outputs-destinations-elastic.md)
