---
title: JSON
slug: adapter-types-json
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-json
articleId: 1fa9a3fe-8fa0-4654-a969-ea9d1e51fc5b
---

* * *

JSON

  *  __06 Jun 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# JSON

  *  __Updated on 06 Jun 2025
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

This Adapter allows you to ingest logs from a file as JSON.

Adapter type: `file`

## Configuration

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

  * `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
  * `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
  * `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
  * `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.



## Deployment

Adapter downloads can be found [here](/v2/docs/adapter-deployment).
    
    
    chmod +x /path/to/lc_adapter
    
    /path/to/lc_adapter file client_options.identity.installation_key=$INSTALLATION_KEY \
    client_options.identity.oid=$OID \
    client_options.platform=json \
    client_options.sensor_seed_key=$SENSOR_NAME \
    client_options.hostname=$SENSOR_NAME \
    file_path=/path/to/file
    

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

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

  * [ Stdin JSON ](/docs/adapter-examples-stdin-json)



* * *

###### What's Next

  * [ Kubernetes Pods Logs ](/docs/adapter-types-kubernetes-pods-logs) __



Table of contents

    * Overview 
    * Configuration 
    * Deployment 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ sensors ](/docs/en/tags/sensors)


