---
title: Ingesting Defender Event Logs
slug: ingesting-defender-event-logs
breadcrumb: Sensors > Endpoint Agent > Tutorials
source: https://docs.limacharlie.io/docs/ingesting-defender-event-logs
articleId: 835788a0-5570-4db1-8e38-2016d589f514
---

* * *

Ingesting Defender Event Logs

  *  __01 Nov 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Ingesting Defender Event Logs

  *  __Updated on 01 Nov 2024
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

The Windows Sensor can listen, alert, and automate based on various Defender events.

This is done by ingesting [artifacts from the Defender Event Log Source](/v2/docs/artifacts) and using [Detection & Response rules](/v2/docs/detection-and-response) to take the appropriate action.

A config template to alert on the common Defender events of interest is available [here](https://github.com/refractionPOINT/templates/blob/master/anti-virus/windows-defender.yaml). The template can be used in conjunction with [Infrastructure Extension](/v2/docs/ext-infrastructure) or its user interface in the [web app](https://app.limacharlie.io).

Specifically, the template alerts on the following Defender events:

  * windows-defender-malware-detected (`event ID 1006`)

  * windows-defender-history-deleted (`event ID 1013`)

  * windows-defender-behavior-detected (`event ID 1015`)

  * windows-defender-activity-detected (`event ID 1116`)




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

  * [ Ingesting Windows Event Logs ](/docs/ingesting-windows-event-logs)
  * [ Artifacts ](/docs/artifacts)
  * [ Ingesting Sysmon Event Logs ](/docs/ingesting-sysmon-event-logs)
  * [ Microsoft Defender ](/docs/adapter-types-microsoft-defender)



* * *

###### What's Next

  * [ Test a New Sensor Version ](/docs/test-a-new-sensor-version) __



Tags

  * [ artifacts ](/docs/en/tags/artifacts)
  * [ endpoint agent ](/docs/en/tags/endpoint%20agent)
  * [ sensors ](/docs/en/tags/sensors)
  * [ telemetry ](/docs/en/tags/telemetry)
  * [ windows ](/docs/en/tags/windows)


