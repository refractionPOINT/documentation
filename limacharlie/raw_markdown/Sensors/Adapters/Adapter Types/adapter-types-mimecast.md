---
title: Mimecast
slug: adapter-types-mimecast
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-mimecast
articleId: 59c9055e-c0f1-4903-bb93-60eb95250665
---

* * *

Mimecast

  *  __07 Aug 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Mimecast

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

This Adapter allows you to connect to the Mimecast API to stream audit events as they happen.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

  * `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
  * `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
  * `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
  * `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.



### Adapter-specific Options

Adapter Type: `mimecast`

  * `client_id`: your Mimecast client ID

  * `client_secret`: your Mimecast client secret




### CLI Deployment

Adapter downloads can be found [here](/v2/docs/adapter-deployment#adapter-binaries).
    
    
    chmod +x /path/to/lc_adapter
    
    /path/to/lc_adapter mimecast client_options.identity.installation_key=$INSTALLATION_KEY \
    client_options.identity.oid=$OID \
    client_options.platform=json \
    client_options.sensor_seed_key=$SENSOR_NAME \
    client_options.hostname=$SENSOR_NAME \
    client_options.mappings.event_type_path=category \
    client_id=$CLIENT_ID client_secret=$CLIENT_SECRET
    

### Infrastructure as Code Deployment
    
    
    # Mimecast Specific Docs: https://docs.limacharlie.io/docs/adapter-types-mimecast
    # For cloud sensor deployment, store credentials as hive secrets:
    
    #   client_id: "hive://secret/mimecast-client-id"
    #   client_secret: "hive://secret/mimecast-client-secret"
    
    sensor_type: "mimecast"
    mimecast:
      client_id: "hive://secret/mimecast-client-id"
      client_secret: "hive://secret/mimecast-client-secret"
      client_options:
        identity:
          oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          installation_key: "YOUR_LC_INSTALLATION_KEY_MIMECAST"
        hostname: "mimecast-logs-adapter"
        platform: "json"
        sensor_seed_key: "mimecast-audit-sensor"
        mapping:
          sensor_hostname_path: "sender"
          event_type_path: "eventType"
          event_time_path: "eventTime"
        indexing: []

## API Doc

See the official [documentation](https://developer.services.mimecast.com/docs/auditevents/1/routes/api/audit/get-audit-events/post).

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

  * [ Adapter Usage ](/docs/adapter-usage)
  * [ Adapter Deployment ](/docs/adapter-deployment)
  * [ Adapter Examples ](/docs/adapter-examples)
  * [ Okta ](/docs/ext-cloud-cli-okta)



* * *

###### What's Next

  * [ Okta ](/docs/adapter-types-okta) __



Table of contents

    * Overview 
    * Deployment Configurations 
    * API Doc 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ sensors ](/docs/en/tags/sensors)


