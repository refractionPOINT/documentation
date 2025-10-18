---
title: Installation Keys
slug: installation-keys
breadcrumb: Sensors
source: https://docs.limacharlie.io/docs/installation-keys
articleId: 7ae76b22-e388-45d4-95a9-7ce0334f2ca2
---

* * *

Installation Keys

  *  __05 Oct 2024
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Installation Keys

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

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

There are four components of an Installation Key:

  * Organization ID**(** OID**)** : The Organization ID that this key should enroll into.

  * **Installer ID (IID)** : Installer ID that is generated and associated with every Installation Key.

  * **Tags** : A list of Tags automatically applied to sensors enrolling with the key.

  * **Description** : The description used to help you differentiate uses of various keys.




## Management

Installation keys can be managed on the **Sensors > Installation Keys** page in the web app.

On this page, under the `Connectivity` section, you will see the various URLs associated with Sensor and Adapter connectivity.

### Pinned Certificates

Typically, Sensors require access over port 443 and use pinned SSL certificates. This is the default deployment option, and does not support traffic interception.

If you need to install sensors without pinned certificates, an installation key must be created with a specific flag. This must be done via the REST API, by setting the `use_public_root_ca` flag to `true`.

More details can be found [here](https://github.com/refractionPOINT/python-limacharlie/blob/master/limacharlie/Manager.py#L1386).

## Use of Tags

Generally speaking, we use at least one Installation Key per organization. Then we use different keys to help differentiate parts of our infrastructure. For example, you may create a key with Tag "server" that you will use to install on your servers, a key with "vip" for executives in your organization, or a key with "sales" for the sales department, etc. This way you can use the tags on various sensors to figure out different detection and response rules for different types of hosts on your infrastructure.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

  
  


In LimaCharlie, an Organization ID (OID) is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

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

  * [ macOS Agent Installation via Jamf Now ](/docs/installing-macos-agents-via-jamf-now)
  * [ Docker Agent Installation ](/docs/docker-agent-installation)
  * [ macOS Agent Installation ](/docs/macos-agent-installation)
  * [ FAQ - Sensor Installation ](/docs/faq-sensor-installation)
  * [ Chrome Agent Installation ](/docs/chrome-agent-installation)
  * [ Windows Agent Installation ](/docs/windows-agent-installation)
  * [ Linux Agent Installation ](/docs/linux-agent-installation)
  * [ Endpoint Agent Installation ](/docs/endpoint-agent-installation)
  * [ macOS Agent Installation - MDM Configuration Profiles ](/docs/macos-agent-installation-mdm-configuration-profiles)
  * [ Agent Deployment via Microsoft Intune ](/docs/agent-deployment-microsoft-intune)
  * [ Endpoint Agent ](/docs/endpoint-agent)
  * [ Endpoint Agent Commands ](/docs/endpoint-agent-commands)
  * [ Adapter Deployment ](/docs/adapter-deployment)
  * [ Adapters ](/docs/adapters)
  * [ Adapter Usage ](/docs/adapter-usage)



* * *

###### What's Next

  * [ Adapters ](/docs/adapters) __



Table of contents

    * Management 
    * Use of Tags 



Tags

  * [ sensors ](/docs/en/tags/sensors)


