---
title: OTX
slug: ext-otx
breadcrumb: Add-Ons > Extensions > Third-Party Extensions
source: https://docs.limacharlie.io/docs/ext-otx
articleId: a2cd200e-b2d7-4d73-9240-9cda4dcb0f63
---

* * *

OTX

  *  __16 Jan 2025
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# OTX

  *  __Updated on 16 Jan 2025
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

AlienVault’s Open Threat Exchange (OTX) is the “neighborhood watch of the global intelligence community.” It enables private companies, independent security researchers, and government agencies to openly collaborate and share the latest information about emerging threats, attack methods, and malicious actors, promoting greater security across the entire community.

More information about OTX can be found [here](https://otx.alienvault.com/).

## Enabling the OTX Extension

Before utilizing the OTX extension, you will need an AlienVault OTX API Key. This can be found in your AlienVault OTX account [here](https://otx.alienvault.com/).

To enable the OTX extension, navigate to the [OTX extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-otx). Select the Organization you wish to enable the extension for, and select **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image\(236\).png)

Once the extension is enabled, navigate to Extensions > OTX. You will need to provide your OTX API Key, which can be done directly in the form or via LimaCharlie’s [Secrets Manager](/v2/docs/config-hive-secrets). Click Save.

Pulses will be synced to rules and lookups automatically every 3 hours.

## Using the OTX Extension

After providing a valid API key, the Extension will automatically create [Detection & Response rules](/v2/docs/detection-and-response) for your organization. The OTX  rules make use of the following events:

  * Process Events

    * [CODE_IDENTITY](/v2/docs/reference-edr-events#codeidentity)

    * [EXISTING_PROCESS](/v2/docs/reference-edr-events#existingprocess)

    * [MEM_HANDLES_REP](/v2/docs/reference-edr-events#memhandlesrep) (response to the[ mem_handles](/v2/docs/endpoint-agent-commands#memhandles) Sensor command)

    * [NEW_PROCESS](/v2/docs/reference-edr-events#newprocess)

  * Network Events

    * [DNS_REQUEST](/v2/docs/reference-edr-events#dnsrequest)

    * [HTTP_REQUEST](/v2/docs/reference-edr-events#httprequest)

    * [NETWORK_CONNECTIONS](/v2/docs/reference-edr-events#networkconnections)

    * [NEW_TCP4_CONNECTION](/v2/docs/reference-edr-events#newtcp4connection)

    * [NEW_TCP6_CONNECTION](/v2/docs/reference-edr-events#newtcp6connection)

    * [NEW_UDP4_CONNECTION](/v2/docs/reference-edr-events#newudp4connection)

    * [NEW_UDP6_CONNECTION](/v2/docs/reference-edr-events#newudp6connection)




Please ensure that the events you are interested in using with OTX lookups are enabled in the **Sensors > **Event Collection menu.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

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

###### What's Next

  * [ PagerDuty ](/docs/ext-pagerduty) __



Table of contents

    * Enabling the OTX {{glossary.Extension}} 
    * Using the OTX Extension 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


