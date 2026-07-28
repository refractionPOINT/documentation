# Azure Key Vault

Azure [Key Vault](https://azure.microsoft.com/en-us/products/key-vault) protects cryptographic keys and other secrets that cloud apps and services use. LimaCharlie can ingest and parse Key Vault logs directly.

## Log Ingestion

You can ingest Azure Key Vault logs through:

- [Azure Event Hub](../azure-event-hub.md)
- LimaCharlie [Webhooks](../../tutorials/webhook-adapter.md)

When you configure the adapter, set `client_options.platform: azure_key_vault` to select the dedicated parser. At ingestion, the log `category` field sets the event type, and the `time` field supplies the event timestamp.

## Sample Event

This sample event comes from the Microsoft Azure documentation:

```json
{
        "records":
        [
            {
                "time": "2016-01-05T01:32:01.2691226Z",
                "resourceId": "/SUBSCRIPTIONS/361DA5D4-A47A-4C79-AFDD-XXXXXXXXXXXX/RESOURCEGROUPS/CONTOSOGROUP/PROVIDERS/MICROSOFT.KEYVAULT/VAULTS/CONTOSOKEYVAULT",
                "operationName": "VaultGet",
                "operationVersion": "2015-06-01",
                "category": "AuditEvent",
                "resultType": "Success",
                "resultSignature": "OK",
                "resultDescription": "",
                "durationMs": "78",
                "callerIpAddress": "104.40.82.76",
                "correlationId": "",
                "identity": {"claim":{"http://schemas.microsoft.com/identity/claims/objectidentifier":"d9da5048-2737-4770-bd64-XXXXXXXXXXXX","http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn":"live.com#username@outlook.com","appid":"1950a258-227b-4e31-a9cf-XXXXXXXXXXXX"}},
                "properties": {"clientInfo":"azure-resource-manager/2.0","requestUri":"https://control-prod-wus.vaultcore.azure.net/subscriptions/361da5d4-a47a-4c79-afdd-XXXXXXXXXXXX/resourcegroups/contosoresourcegroup/providers/Microsoft.KeyVault/vaults/contosokeyvault?api-version=2015-06-01","id":"https://contosokeyvault.vault.azure.net/","httpStatusCode":200}
            }
        ]
    }
```
