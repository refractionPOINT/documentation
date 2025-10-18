---
title: VMWare Carbon Black
slug: adapter-types-vmware-carbon-black
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-vmware-carbon-black
articleId: 87cdc3ee-d215-43b5-a0ba-3f4f6e481a62
---

* * *

VMWare Carbon Black

  *  __06 Jun 2025
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# VMWare Carbon Black

  *  __Updated on 06 Jun 2025
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

LimaCharlie can ingest Carbon Black events from a number of storage locations. Typically, an organization would export Carbon Black data via the API to a storage mechanism, such as an S3 bucket, which would then be ingested by LimaCharlie.

Carbon Black events are observable in Detection & Response rules via the `carbon_black` platform.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

  * `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
  * `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
  * `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
  * `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.



## Config File

VMWare Carbon Black data can be exported via the API to an S3 bucket, and then ingested with LimaCharlie. The following command utilizes a CLI Adapter to ingest these events
    
    
    ./lc_adapter s3 client_options.identity.installation_key=<INSTALLATION_KEY> \
    client_options.identity.oid=<OID> \
    client_options.platform=carbon_black \
    client_options.sensor_seed_key=tests3 \
    bucket_name=lc-cb-test \
    access_key=YYYYYYYYYY \
    secret_key=XXXXXXXX  \
    "prefix=events/org_key=NKZAAAEM/"
    

Here's a breakdown of the above example:

  * `lc_adapter`: simply the CLI Adapter.

  * `s3`: the data will be collected from an AWS S3 bucket.

  * `client_options.identity.installation_key=....`: the Installation Key value from LimaCharlie.

  * `client_options.identity.oid=....`: the Organization ID from LimaCharlie the installation key above belongs to.

  * `client_options.platform=carbon_black`: this indicates the data received will be Carbon Black events from their API.

  * `client_options.sensor_seed_key=....`: this is the value that identifies this instance of the Adapter. Record it to re-use the Sensor IDs generated for the Carbon Black sensors from this Adapter later if you have to re-install the Adapter.

  * `bucket_name:....`: the name of the S3 bucket holding the data.

  * `access_key:....`: the AWS Access Key for the API key below.

  * `secret_key:....`: the API key for AWS that has access to this bucket.

  * `prefix=....`: the file/directory name prefix that holds the Carbon Black data within the bucket.




Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

Amazon Web Services

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

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

###### What's Next

  * [ Windows Event Log ](/docs/adapter-types-windows-event-log) __



Table of contents

    * Overview 
    * Deployment Configurations 
    * Config File 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ sensors ](/docs/en/tags/sensors)


