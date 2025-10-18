---
title: Azure Event Hub
slug: adapter-types-azure-event-hub
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-azure-event-hub
articleId: ced5df43-7d7d-4659-b39f-4cf2912cf34a
---

* * *

Azure Event Hub

  *  __16 Jul 2025
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Azure Event Hub

  *  __Updated on 16 Jul 2025
  *  __ 2 Minutes to read 



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

## Overview

This Adapter allows you to connect to an Azure Event Hub to fetch structured data stored there.

[Azure Event Hubs](https://azure.microsoft.com/en-us/products/event-hubs) are fully managed, real-time data ingestion services that allow for event streaming from various Microsoft Azure services. LimaCharlie can ingest either structured known data (such as JSON or XML) _or_ known Microsoft data types, including:

  * Azure Monitor (Platform: `azure_monitor`)

  * Entra ID [formerly Azure AD] (Platform: `azure_ad`)

  * Microsoft Defender (Platform: `msdefender`)




Documentation for creating an event hub can be found here [here](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-create).

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

  * `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
  * `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
  * `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
  * `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.



### Adapter-specific Options

  * If using a binary Adapter, `azure_event_hub` will be the ingestion type.

  * `connection_string` \- The connection string provided in Azure for connecting to the Azure Event Hub, including the `EntityPath=...` at the end which identifies the Hub Name (this component is sometimes now shown in the connection string provided by Azure).




## Guided Deployment

Azure Event Hub data can be pulled via either a cloud or binary Adapter.

### Cloud-to-Cloud

LimaCharlie offers several helpers within the webapp that allow you to ingest Microsoft data, such as Entra ID or Microsoft Defender, from Azure Event Hubs.

### CLI Deployment

The following example configures a binary Adapter to collect Microsoft Defender data from an Azure Event Hub:
    
    
    ./lc_adapter azure_event_hub client_options.identity.installation_key=<INSTALLATION_KEY> \
    client_options.identity.oid=<OID> \
    client_options.platform=msdefender \
    client_options.sensor_seed_key=<SENSOR_SEED_KEY> \
    client_options.hostname=<HOSTNAME> \
    "connection_string=Endpoint=sb://mynamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=fnaaaaaaaaaaaaaaak0g54alYbbbbbbbbbbbbbbbALQ=;EntityPath=lc-stream"
    

### Infrastructure as Code Deployment
    
    
    # Azure Event Hub Specific Docs: https://docs.limacharlie.io/docs/adapter-types-azure-event-hub
    
    sensor_type: "azure_event_hub"
      azure_event_hub:
        connection_string: "Endpoint=sb://your-eventhub-namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=YOUR_EVENT_HUB_SHARED_ACCESS_K
      EY_HERE;EntityPath=your-actual-event-hub-name"
        client_options:
          identity:
            oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            installation_key: "YOUR_LC_INSTALLATION_KEY_FOR_AZURE"
          hostname: "azure-eventhub-adapter"
          platform: "json"
          sensor_seed_key: "azure-eventhub-prod-sensor"
          indexing: []
    

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

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

  * [ Azure Network Security Group ](/docs/azure-network-security-group)
  * [ Azure Storage Blob ](/docs/outputs-destinations-azure-storage-blob)
  * [ Azure Monitor ](/docs/azure-monitor)
  * [ Azure ](/docs/ext-cloud-cli-azure)
  * [ Azure SQL Audit Logs ](/docs/azure-sql-audit-logs)
  * [ Azure Kubernetes Service (AKS) ](/docs/azure-kubernetes-service)
  * [ Azure Key Vault ](/docs/azure-logs-key-vault)
  * [ Azure Event Hub ](/docs/outputs-destinations-azure-event-hub)
  * [ Microsoft Defender ](/docs/adapter-types-microsoft-defender)
  * [ Microsoft Entra ID ](/docs/adapter-types-microsoft-entra-id)



* * *

###### What's Next

  * [ Canarytokens ](/docs/adapter-types-canarytokens) __



Table of contents

    * Overview 
    * Deployment Configurations 
    * Guided Deployment 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ azure ](/docs/en/tags/azure)
  * [ sensors ](/docs/en/tags/sensors)


