---
title: Ingesting MacOS Unified Logs
slug: ingesting-macos-unified-logs
breadcrumb: Getting Started > Tutorials > Telemetry
source: https://docs.limacharlie.io/docs/ingesting-macos-unified-logs
articleId: 4e3a2253-84ee-4d53-8eb2-79a35ae5b1b3
---

* * *

Ingesting MacOS Unified Logs

  *  __07 Oct 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Ingesting MacOS Unified Logs

  *  __Updated on 07 Oct 2025
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

You can enable real-time MacOS Unified Logs (MUL) ingestion using the LimaCharlie EDR Sensor.

First, navigate to the Exfil Control section of LimaCharlie and ensure that `MUL` events are enabled for your Mac rules.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ingest-mac-1.png)

Next, navigate to the `Artifact Collection` section and set up an artifact collection rule for the MacOS Unified Log(s) of interest.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ingest-mac-2.png)

To ingest MUL real-time events in the timeline, use the `mul://[Predicate]` format, where the predicate is a standard [MacOS MUL predicate](https://www.macminivault.com/faq/introduction-to-macos-unified-logs/). For example, to ingest the Safari logs, you'd use the following pattern:

`mul://process == "Safari"`

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ingest-mac-3.png)

If you ingest MacOS Unified Logs with a `mul://` pattern, they are streamed in real-time as first-class telemetry alongside the native EDR events, and are included in the flat rate price of the sensor.

After you apply those, you should start seeing your MacOS Unified Logs data coming through for your endpoints within 10 minutes. You can verify this by going into the Timeline view and choosing `MUL` event type.

Endpoint Detection & Response

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

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

  * [ macOS Agent Installation ](/docs/macos-agent-installation)
  * [ Mac Unified Logging ](/docs/adapter-types-mac-unified-logging)
  * [ Artifacts ](/docs/artifacts)



* * *

###### What's Next

  * [ Log Collection Guide ](/docs/logcollectionguide) __



Tags

  * [ endpoint agent ](/docs/en/tags/endpoint%20agent)
  * [ macos ](/docs/en/tags/macos)
  * [ sensors ](/docs/en/tags/sensors)
  * [ telemetry ](/docs/en/tags/telemetry)
  * [ tutorial ](/docs/en/tags/tutorial "Tutorial")


