---
title: Microsoft Defender
slug: adapter-types-microsoft-defender
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-microsoft-defender
articleId: fac103ba-a528-4c5a-ba72-d91756cc5bf2
---

* * *

Microsoft Defender

  *  __07 Aug 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Microsoft Defender

  *  __Updated on 07 Aug 2025
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

## Overview

LimaCharlie can ingest [Microsoft 365 Defender logs](https://learn.microsoft.com/en-us/microsoft-365/security/defender/microsoft-365-defender?view=o365-worldwide) via three methods [Azure Event Hub](/v2/docs/adapter-types-azure-event-hub) Adapter, the [Microsoft Defender API](https://learn.microsoft.com/en-us/defender-endpoint/api/exposed-apis-create-app-nativeapp), or a Custom Webhook

Documentation for creating an event hub can be found here [here](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-create).

Telemetry Platform: `msdefender`

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

  * `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
  * `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
  * `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
  * `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.



### Adapter-specific Options

  * `connection_string` \- The connection string provided in Azure for connecting to the Azure Event Hub, including the `EntityPath=...` at the end which identifies the Hub Name (this component is sometimes now shown in the connection string provided by Azure).




## Guided Deployment

In the LimaCharlie web app, you can find a Microsoft Defender helper for connecting to an existing Azure Event Hub and ingesting Microsoft Defender logs.

### CLI Deployment

The following example configuration ingests Microsoft Defender logs from an Azure Event Hub to LimaCharlie.
    
    
    ./lc_adapter azure_event_hub client_options.identity.installation_key=<INSTALLATION_KEY> \
    client_options.identity.oid=<OID> \
    client_options.platform=msdefender \
    client_options.sensor_seed_key=<SENSOR_SEED_KEY> \
    client_options.hostname=msdefender \
    "connection_string=Endpoint=sb://mynamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=fnaaaaaaaaaaaaaaak0g54alYbbbbbbbbbbbbbbbALQ=;EntityPath=lc-stream"
    

### Infrastructure as Code Deployment
    
    
    # Adapter Documentation: https://docs.limacharlie.io/docs/adapter-types
    # For cloud sensor deployment, store credentials as hive secrets:
    
    #   tenant_id: "hive://secret/azure-tenant-id"
    #   client_id: "hive://secret/defender-client-id"
    #   client_secret: "hive://secret/defender-client-secret"
    
    sensor_type: "defender"
    defender:
      tenant_id: "hive://secret/azure-tenant-id"
      client_id: "hive://secret/azure-defender-client-id"
      client_secret: "hive://secret/azure-defender-client-secret"
      client_options:
        identity:
          oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          installation_key: "YOUR_LC_INSTALLATION_KEY_DEFENDER"
        hostname: "ms-defender-adapter"
        platform: "json"
        sensor_seed_key: "defender-sensor"
        mapping:
          sensor_hostname_path: "machineDnsName"
          event_type_path: "alertType"
          event_time_path: "lastUpdateTime"
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

  * [ Ingesting Defender Event Logs ](/docs/ingesting-defender-event-logs)
  * [ Azure Event Hub ](/docs/adapter-types-azure-event-hub)
  * [ Windows Event Logs ](/docs/adapter-examples-windows-event-logs)



* * *

###### What's Next

  * [ Microsoft Entra ID ](/docs/adapter-types-microsoft-entra-id) __



Table of contents

    * Overview 
    * Deployment Configurations 
    * Guided Deployment 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ azure ](/docs/en/tags/azure)
  * [ sensors ](/docs/en/tags/sensors)


