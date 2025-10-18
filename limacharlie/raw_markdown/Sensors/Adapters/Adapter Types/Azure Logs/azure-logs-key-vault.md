---
title: Azure Key Vault
slug: azure-logs-key-vault
breadcrumb: Sensors > Adapters > Adapter Types > Azure Logs
source: https://docs.limacharlie.io/docs/azure-logs-key-vault
articleId: 3e599842-c87f-416b-838c-09a428957a9f
---

* * *

Azure Key Vault

  *  __31 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Azure Key Vault

  *  __Updated on 31 Oct 2024
  *  __ 1 Minute to read 



  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




* * *

Article summary

 __

Did you find this summary helpful? __ __ __ __

__

Thank you for your feedback!

Azure [Key Vault](https://azure.microsoft.com/en-us/products/key-vault) is a product that helps safeguard cryptographic keys and other secrets used by cloud apps and services. LimaCharlie can ingest and natively parse Key Vault logs.

## Log Ingestion

Azure Key Vault logs can be ingested via:

  * [Azure Event Hub](/v2/docs/adapter-types-azure-event-hub)

  * LimaCharlie [Webhooks](/v2/docs/tutorial-creating-a-webhook-adapter)




Upon ingestion, the log `category` field is used to define the Event Type.

## Sample Event

The following sample event is taken from Microsoft Azure documentation:
    
    
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
    

* * *

Was this article helpful?

__Yes __No

 __

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change  


Please enter a valid email

Cancel

* * *

###### Related articles

  * [ Azure SQL Audit Logs ](/docs/azure-sql-audit-logs)
  * [ Azure Event Hub ](/docs/adapter-types-azure-event-hub)
  * [ Azure Storage Blob ](/docs/outputs-destinations-azure-storage-blob)
  * [ Azure Monitor ](/docs/azure-monitor)
  * [ Azure ](/docs/ext-cloud-cli-azure)
  * [ Azure Kubernetes Service (AKS) ](/docs/azure-kubernetes-service)
  * [ Azure Network Security Group ](/docs/azure-network-security-group)
  * [ Azure Event Hub ](/docs/outputs-destinations-azure-event-hub)
  * [ Microsoft Entra ID ](/docs/adapter-types-microsoft-entra-id)



* * *

###### What's Next

  * [ Azure Kubernetes Service (AKS) ](/docs/azure-kubernetes-service) __



Table of contents

    * Log Ingestion 
    * Sample Event 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ azure ](/docs/en/tags/azure)
  * [ sensors ](/docs/en/tags/sensors)


