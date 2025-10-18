---
title: EVTX
slug: adapter-types-evtx
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-evtx
articleId: 5f2ac308-c6f8-48de-b8b5-3029bf43327c
---

* * *

EVTX

  *  __07 Aug 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# EVTX

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

This Adapter allows you to ingest and convert a `.evtx` file into LimaCharlie. The `.evtx` files are the binary format used by Microsoft for Windows Event Logs. This is useful to ingest historical Windows Event Logs, for example during an Incident Response (IR) engagement.

For real-time collection of Windows Event Logs, see the [Windows Event Logs](/v2/docs/ingesting-windows-event-logs) documentation.

## Configurations

Adapter Type: `evtx`

  * `client_options`: common configuration for adapter as defined [here](/v2/docs/adapters#usage).

  * `file_path`: path to the `.evtx` file to ingest.




## API Doc

See the [unofficial documentation on EVTX](https://www.giac.org/paper/gcia/2999/evtx-windows-event-logging/115806).

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

  * [ Windows Event Logs ](/docs/adapter-examples-windows-event-logs)
  * [ Ingesting Windows Event Logs ](/docs/ingesting-windows-event-logs)
  * [ Hayabusa ](/docs/ext-hayabusa)
  * [ Artifact ](/docs/ext-artifact)



* * *

###### What's Next

  * [ File ](/docs/adapter-types-file) __



Table of contents

    * Overview 
    * Configurations 
    * API Doc 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ sensors ](/docs/en/tags/sensors)
  * [ windows ](/docs/en/tags/windows)


