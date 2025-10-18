---
title: Reference: Schedule Events
slug: reference-schedule-events
breadcrumb: Events > Platform Events Overview
source: https://docs.limacharlie.io/docs/reference-schedule-events
articleId: 8f9ab347-5e94-4bbd-9aff-a0563f78f7db
---

* * *

Reference: Schedule Events

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Reference: Schedule Events

  *  __Updated on 05 Oct 2024
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

Schedule events are triggered automatically at various intervals per Organization or per Sensor, observable in  rules via the `schedule` target.

Scheduling events have a very similar structure whether they are per-sensor or per-org.

The `event` component contains a single key, `frequency` which is the number of seconds frequency this scheduling event is for. The event type also contains the human readable version of the frequency.

The following frequencies are currently emitted:

  * `30m`: `30m_per_org` and `30m_per_sensor`

  * `1h`: `1h_per_org` and `1h_per_sensor`

  * `3h`: `3h_per_org` and `3h_per_sensor`

  * `6h`: `6h_per_org` and `6h_per_sensor`

  * `12h`: `12h_per_org` and `12h_per_sensor`

  * `24h`: `24h_per_org` and `24h_per_sensor`

  * `168h` (7 days): `168h_per_org` and `168h_per_sensor`




Scheduling events are generated for each org that meets the following criteria:

  * Has had at least 1 sensor online in the last 7 days.




Scheduling events are generated for each sensor that meets the following criteria:

  * Has been online at least once in the last 30 days.




Scheduling events are not retained as part of the year retention in LimaCharlie. To leverage them, create D&R rules that target the `schedule` target and take the relevant `action` when matched. For example to issue an `os_packages` once per week on Windows hosts:
    
    
    detect:
      target: schedule
      event: 168h_per_sensor
      op: is platform
      name: windows
    respond:
      - action: task
        command: os_packages
        investigation: weekly-package-list
    

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

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

  * [ Detection on Alternate Targets ](/docs/detection-on-alternate-targets)
  * [ Detection and Response Examples ](/docs/detection-and-response-examples)
  * [ Detection and Response ](/docs/detection-and-response)
  * [ Platform Events Overview ](/docs/platform-events-overview)
  * [ Reference: Platform Events ](/docs/reference-platform-events)



* * *

###### What's Next

  * [ Query Console ](/docs/query-console) __



Tags

  * [ detection and response ](/docs/en/tags/detection%20and%20response)
  * [ events ](/docs/en/tags/events)
  * [ platform ](/docs/en/tags/platform)


