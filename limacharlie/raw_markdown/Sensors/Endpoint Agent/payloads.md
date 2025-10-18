---
title: Payloads
slug: payloads
breadcrumb: Sensors > Endpoint Agent
source: https://docs.limacharlie.io/docs/payloads
articleId: b7368c23-789c-477e-b75c-11bd4b768ea4
---

* * *

Payloads

  *  __05 Oct 2024
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Payloads

  *  __Updated on 05 Oct 2024
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

Payloads are executables or scripts that can be delivered and executed through LimaCharlie's Endpoint Agent.

Those payloads can be any executable or script natively understood by the endpoint. The main use case is to run something with specific functionality not available in the main LimaCharlie functionality. For example: custom executables provided by another vendor to cleanup a machine, forensic utilities or firmware-related utilities.

We encourage you to look at LimaCharlie native functionality first as it has several advantages:

  * Usually has better performance.

  * Data returned is always well structured JSON.

  * Can be tasked automatically and [Detection & Response Rules](/v2/docs/detection-and-response) can be created from their data.

  * Data returned is indexed and searchable.




It is possible to set the Payload's file extension on the endpoint by making the Payload name end with that extension. For example, naming a Payload `extract_everything.bat`, the Payload will be sent as a batch file (`.bat`) and executed as such. This is also true for PowerShell files (`.ps1`).

## Lifecycle

Payloads are uploaded to the LimaCharlie platform and given a name. The task `run` can then be used with the `--payload-name MY-PAYLOAD --arguments "-v EulaAccepted"` can be used to run the payload with optional arguments.

The STDOUT and STDERR data will be returned in a related `RECEIPT` event, up to ~10 MB. If your payload generates more data, we recommend to pipe the data to a file on disk and use the `log_get` command to retrieve it.

The payload is retrieved by the endpoint agent over HTTPS to the Ingestion API DNS endpoint. This DNS entry is available from the Sensor Download section of the web app if you need to allow it.

## Upload / Download via REST

Creating and getting Payloads is done asynchronously. The relevant REST APIs will return specific signed URLs instead of the actual Payload. In the case of a retrieving an existing payload, simply doing an HTTP GET using the returned URL will download the payload content. When creating a Payload the returned URL should be used in an HTTP PUT using the URL like:
    
    
    curl -X PUT "THE-SIGNED-URL-HERE" -H "Content-Type: application/octet-stream" --upload-file your-file.exe
    

Note that the signed URLs are only valid for a few minutes.

## Permissions

Payloads are managed with two permissions:

  * `payload.ctrl` allows you to create and delete payloads.

  * `payload.use` allows you to run a given payload.




Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

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

###### Related articles

  * [ Endpoint Agent Commands ](/docs/endpoint-agent-commands)
  * [ Reference: Endpoint Agent Commands ](/docs/reference-endpoint-agent-commands)
  * [ Payload Manager ](/docs/payload-manager)



* * *

###### What's Next

  * [ Sleeper Deployment ](/docs/sleeper) __



Table of contents

    * Overview 
    * Lifecycle 
    * Upload / Download via REST 
    * Permissions 



Tags

  * [ endpoint agent ](/docs/en/tags/endpoint%20agent)
  * [ linux ](/docs/en/tags/linux)
  * [ macos ](/docs/en/tags/macos)
  * [ sensors ](/docs/en/tags/sensors)
  * [ windows ](/docs/en/tags/windows)


