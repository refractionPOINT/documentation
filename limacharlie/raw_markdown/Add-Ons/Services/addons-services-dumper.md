---
title: Dumper
slug: addons-services-dumper
breadcrumb: Add-Ons > Services
source: https://docs.limacharlie.io/docs/addons-services-dumper
articleId: 6c5598dc-fd74-4490-ae14-98e0936ff54f
---

* * *

Dumper

  *  __12 Nov 2024
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Dumper

  *  __Updated on 12 Nov 2024
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

The Dumper Extension provides the ability to do dumping of several forensic artifacts on Windows hosts. It supports a single action, which is to dump.

It supports multiple targets -- `memory` to dump the memory of the host, and `mft` to dump the MFT of the file system to CSV. The extension then automates the ingestion of the resulting dump (and dump metadata) to LimaCharlie's [Artifact Ingestion system](/v2/docs/artifacts) where it can be downloaded or analyzed, and where you can create  rules to automate detections of characteristics of those dumps.

### Usage

When enabled, dumper will be added to the Extensions view inside your Organization. It will accept the following parameters:

  * `sid` \- a Sensor ID for the host to perform the memory dump

  * `target` \- memory or mft

  * `retention` \- the number of days the memory dump should be retained for (default is 30)

  * `ignore_cert` \- ignore cert errors for payload and collection purposes (default `false`)




Upon submission of a request, the extension will perform a full memory dump of a host and upload the resulting dumps to LimaCharlie's artifact ingestion system and delete the local dumps afterwards.

Dumper requests can also be made via D&R rules. Here is is example of a D&R rule action that makes a request to Dumper:
    
    
    - action: extension request
      extension name: ext-dumper
      extension action: request_dump
      extension request:
        target: memory
        sid: <<routing.sid>> 
        retention: 30 #default 30
        ignore_cert: true # default false
    

**Notes:**

The dumper extension does not currently validate that the host has enough available disc space for the memory dump. Although the dumper extension is free, the resulting memory dumps uploaded to LimaCharlie are subject to external logs pricing. This add-on relies on other paid resources (payloads) billed based on usage.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

In LimaCharlie, a Sensor ID is a unique identifier assigned to each deployed endpoint agent (sensor). It distinguishes individual sensors across an organization's infrastructure, allowing LimaCharlie to track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as sending commands, collecting telemetry, and monitoring activity, ensuring that actions and data are accurately linked to specific devices or endpoints.

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

  * [ Plaso ](/docs/ext-plaso)
  * [ Sleeper Deployment ](/docs/sleeper)



* * *

###### What's Next

  * [ Endpoint Protection ](/docs/ext-epp) __



Table of contents




Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ dfir ](/docs/en/tags/dfir)
  * [ extensions ](/docs/en/tags/extensions)


