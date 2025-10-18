---
title: Soteria M365 Rules
slug: soteria-m365-rules
breadcrumb: Detection and Response > Managed Rulesets > Soteria Rules
source: https://docs.limacharlie.io/docs/soteria-m365-rules
articleId: 011df9d3-3f9f-47bb-a939-bba534ec5785
---

* * *

Soteria M365 Rules

  *  __09 Oct 2025
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Soteria M365 Rules

  *  __Updated on 09 Oct 2025
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

Soteria's O365 ruleset provides coverage across O365 (aka M365) telemetry streams. The ruleset is designed for in-depth analysis of the Office 365 ecosystem which includes:

  * Teams

  * Word

  * Excel

  * PowerPoint

  * Outlook

  * OneDrive

  * ...and other productivity applications.




Data access

Please note that Soteria won’t get access to your data, and you won’t be able to see or edit their rules - LimaCharlie acts as a broker between the two parties.

To leverage detection logic provided by the ruleset:

  1. Subscribe your tenant to the [Soteria Office 365 ruleset extension](https://app.limacharlie.io/add-ons/extension-detail/soteria-rules-o365)

  2. Subscribe your tenant to [tor](https://app.limacharlie.io/add-ons/detail/tor-ips) lookup (provided at no cost).

  3. Configure Office 365 Sensor to start collecting [Office 365 audit logs](/v2/docs/adapter-types-microsoft-365).




## Enabling Soteria's O365 Rules

Soteria's O365 rules can be activated via two means.

### Activating via the Web UI

To enable Soteria's O365 ruleset, navigate to the Extensions section of the Add-On Marketplace and search for Soteria. You can also directly select `soteria-rules-o365`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-o365-1.png)

_Please note: Pricing may reflect when the screenshot was taken, not the actual pricing_

Under the Organization dropdown, select a tenant (organization) you want to subscribe to Soteria O365 rules and click **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-o365-2.png)

You can also manage add-ons from the **Subscriptions** menu under **Billing**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-o365-3.png)

### Infrastructure as Code

Alternatively, to manage tenants and LimaCharlie functionality at scale, you can leverage our Infrastructure as Code functionality.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

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

  * [ Soteria AWS Rules ](/docs/soteria-aws-rules)
  * [ Soteria Rules ](/docs/soteria-rules)
  * [ Soteria EDR Rules ](/docs/soteria-edr-rules)
  * [ Managed Rulesets ](/docs/managed-rulesets)
  * [ Microsoft 365 ](/docs/adapter-types-microsoft-365)
  * [ Microsoft 365 ](/docs/ext-cloud-cli-microsoft365)
  * [ Cloud CLI ](/docs/ext-cloud-cli)



* * *

###### What's Next

  * [ SOC Prime Rules ](/docs/soc-prime-rules) __



Table of contents

    * Enabling Soteria's O365 Rules 



Tags

  * [ azure ](/docs/en/tags/azure)
  * [ detection and response ](/docs/en/tags/detection%20and%20response)
  * [ m365 ](/docs/en/tags/m365)


