---
title: Ingesting Windows Event Logs
slug: ingesting-windows-event-logs
breadcrumb: Sensors > Endpoint Agent > Tutorials
source: https://docs.limacharlie.io/docs/ingesting-windows-event-logs
articleId: 8b5d911e-d348-4d62-9ace-74a82e2026a1
---

* * *

Ingesting Windows Event Logs

  *  __07 Oct 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Ingesting Windows Event Logs

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

You can enable real-time Windows Event Log (WEL) ingestion using the LimaCharlie EDR Sensor.

First, navigate to the Exfil Control section of LimaCharlie and ensure that `WEL` events are enabled for your Windows rules.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ingest-wel-1.png)

Next, navigate to the `Artifact Collection` section and set up an artifact collection rule for the Windows Event Log(s) of interest.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ingest-wel-2.png)

To ingest WEL real-time events in the timeline, use the `wel://[Log Name]` format. For example, to ingest the System event log, you'd use the following pattern:

`wel://system:*`

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ingest-wel-3.png)

Difference between `.evtx` versus `wel://` ingestion

If you specify the file on disk, via the `evtx` file extension (as seen in the image above), LimaCharlie will upload the entire Windows Event Log file from disk. This will be represented as a collected artifact, not as real-time events on the sensor's timeline. This method incurs regular artifact ingestion costs for "Telemetry Sources" as seen on our [pricing](https://limacharlie.io/pricing) page.

If you ingest Windows Event Logs with a `wel://` pattern, they are streamed in real-time as first-class telemetry alongside the native EDR events, and are included in the flat rate price of the sensor.

After you apply those, you should start seeing your Windows Event Log data coming through for your endpoints. You can verify this by going into the Timeline view and choosing `WEL` event type.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ingest-wel-4.png)

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

  * [ Windows Event Log ](/docs/adapter-types-windows-event-log)
  * [ Windows Agent Installation ](/docs/windows-agent-installation)
  * [ Windows Event Logs ](/docs/adapter-examples-windows-event-logs)
  * [ EVTX ](/docs/adapter-types-evtx)
  * [ Ingesting Sysmon Event Logs ](/docs/ingesting-sysmon-event-logs)
  * [ Ingesting Defender Event Logs ](/docs/ingesting-defender-event-logs)
  * [ Hayabusa ](/docs/ext-hayabusa)



* * *

###### What's Next

  * [ Ingesting MacOS Unified Logs ](/docs/ingesting-macos-unified-logs) __



Tags

  * [ endpoint agent ](/docs/en/tags/endpoint%20agent)
  * [ sensors ](/docs/en/tags/sensors)
  * [ telemetry ](/docs/en/tags/telemetry)
  * [ tutorial ](/docs/en/tags/tutorial "Tutorial")
  * [ windows ](/docs/en/tags/windows)


