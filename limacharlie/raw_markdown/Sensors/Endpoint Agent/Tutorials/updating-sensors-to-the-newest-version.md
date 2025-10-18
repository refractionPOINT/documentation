---
title: Updating Sensors to the Newest Version
slug: updating-sensors-to-the-newest-version
breadcrumb: Sensors > Endpoint Agent > Tutorials
source: https://docs.limacharlie.io/docs/updating-sensors-to-the-newest-version
articleId: e236cd63-1543-4720-8bf8-e3a8e8fb327a
---

* * *

Updating Sensors to the Newest Version

  *  __25 Apr 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Updating Sensors to the Newest Version

  *  __Updated on 25 Apr 2025
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

LimaCharlie releases a new version of the Sensor frequently - often every few weeks. However, we give you full control over what sensor version is running in your Organization. Sensors are not updated by default.

There are two methods for updating sensors in your organization to the latest version.

## Manual Update

Upgrading sensors is done transparently for you once you click the "Update to Latest" button, located at `Sensors > Deployed Versions`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image\(316\).png)

The new version should be in effect across the organization within about 20 minutes.

## Automated Update

You can also configure sensors in your organization to auto-update to the new version when it's released. To do it, tag applicable (or all) sensors in your fleet with the `lc:stable` tag (`lc:stable` tag means that the package it provides rarely changes).

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image\(315\).png)

This will ensure that when a new sensor version is released, it will be in effect across the organization within about 20 minutes.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

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

  * [ Endpoint Agent Versioning and Upgrades ](/docs/endpoint-agent-versioning-and-upgrades)
  * [ Test a New Sensor Version ](/docs/test-a-new-sensor-version)
  * [ Endpoint Agent Installation ](/docs/endpoint-agent-installation)



* * *

###### What's Next

  * [ Ingesting Sysmon Event Logs ](/docs/ingesting-sysmon-event-logs) __



Table of contents

    * Manual Update 
    * Automated Update 



Tags

  * [ endpoint agent ](/docs/en/tags/endpoint%20agent)
  * [ sensors ](/docs/en/tags/sensors)
  * [ tutorial ](/docs/en/tags/tutorial "Tutorial")


