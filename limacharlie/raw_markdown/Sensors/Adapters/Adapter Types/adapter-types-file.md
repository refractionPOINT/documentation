---
title: File
slug: adapter-types-file
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-file
articleId: a564ff3b-633d-4802-b64a-54acd43ecb60
---

* * *

File

  *  __20 Aug 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# File

  *  __Updated on 20 Aug 2025
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

This Adapter allows you to ingest logs from a file, either as a one time operation or by following its output (like `tail -f`). A more detailed guide to file collection can be found in the [Log Collection Guide](/v2/docs/logcollectionguide).

### Configuration

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

  * `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
  * `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
  * `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
  * `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.



Adapter type `file`:

  * `file_path`: simple file pattern like `./files_*.txt`

  * `no_follow`: if `true`, the file content will be sent, but additions to the file will not be reported

  * `inactivity_threshold`: the number of seconds after which an unmodified file becomes ignored

  * `backfill`: if `true`, a single pass at all the matching files will be made to ingest them, useful for historical ingestion

  * `serialize_files`: if `true`, files will be ingested one at a time, useful for very large number of files that could blow up memory




### CLI Deployment

Adapter downloads can be found [here](/v2/docs/adapter-deployment).
    
    
    chmod +x /path/to/lc_adapter
    
    /path/to/lc_adapter file client_options.identity.installation_key=$INSTALLATION_KEY \
    client_options.identity.oid=$OID \
    client_options.platform=text \
    client_options.sensor_seed_key=$SENSOR_NAME \
    client_options.hostname=$SENSOR_NAME \
    file_path=/path/to/file
    

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

Command-line Interface

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

  * [ Google Cloud Pubsub ](/docs/adapter-types-google-cloud-pubsub) __



Table of contents

    * Overview 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ sensors ](/docs/en/tags/sensors)


