---
title: Agent Deployment via Microsoft Intune
slug: agent-deployment-microsoft-intune
breadcrumb: Sensors > Endpoint Agent > Endpoint Agent Installation > Enterprise-Wide Agent Deployment
source: https://docs.limacharlie.io/docs/agent-deployment-microsoft-intune
articleId: 1c850194-293e-4f4f-9c58-52fca63c993b
---

* * *

Agent Deployment via Microsoft Intune

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Agent Deployment via Microsoft Intune

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

[Microsoft Intune](https://learn.microsoft.com/en-us/mem/) is a cloud-based endpoint management solution that integrates with Microsoft Azure. It allows for simplified app and device management across a wide range of devices, including mobile devices, desktop computers, and virtual endpoints.

Intune can be used to simplify LimaCharlie Sensor deployment within enterprise environments. To add a custom App to Intune, select the `+ Add` button within the Intune admin center:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2861%29.png)

InTune supports Windows and macOS package deployment.

### Windows Deployment via Intune

Deploying Windows applications via Intune requires creating an Intune application package (`.intunewin` file extension). To do this, please utilize Microsoft's IntuneWinAppUtil.exe file. Usage and documentation on creating an `.intunewin` file can be found [here](https://learn.microsoft.com/en-us/mem/intune/apps/apps-win32-prepare).

Intune Package Contents

Intune packages may need to be created for each Organization, as the Installation Key must be provided at the time of installation.

We recommend first creating a [custom MSI installer](/v2/docs/building-a-custom-msi-installer-for-windows), bundled with the appropriate installation key, and then including that in your `.intunewin` file.

After clicking `+ Add`, choose `Windows app (Win32)`:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2863%29.png)

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

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

  * [ Windows Agent Installation ](/docs/windows-agent-installation)
  * [ Building a custom MSI installer for Windows ](/docs/building-a-custom-msi-installer-for-windows)



* * *

###### What's Next

  * [ ChromeOS with Google Chrome Enterprise ](/docs/chrome-enterprise) __



Table of contents




Tags

  * [ endpoint agent ](/docs/en/tags/endpoint%20agent)
  * [ sensors ](/docs/en/tags/sensors)
  * [ windows ](/docs/en/tags/windows)


