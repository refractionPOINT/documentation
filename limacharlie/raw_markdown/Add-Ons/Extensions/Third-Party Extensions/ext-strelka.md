---
title: Strelka
slug: ext-strelka
breadcrumb: Add-Ons > Extensions > Third-Party Extensions
source: https://docs.limacharlie.io/docs/ext-strelka
articleId: 1c313b77-9183-434f-a041-3da07b497400
---

* * *

Strelka

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Strelka

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

Strelka Extension Pricing

Note that usage of ext-strelka will incur usage of Artifact Exporting (applied to processed artifacts at a rate of $0.02/GB) as well as webhook data received in LimaCharlie and the related costs on top of the ext-strelka specific pricing.

[Strelka](https://github.com/target/strelka) is a real-time file scanning system used for threat hunting, threat detection, and incident response.

The Strelka extension receives files using Artifacts by specifying an `artifact_id` in the `run_on` request. The extension will then process the file and return the results to the caller as well as send the results to its related Sensor.

### Configuration

Example  rule that processes all Artifacts ingested with the type `zeek-extract`:

**Detect:**
    
    
    event: ingest
    op: is
    path: routing/log_type
    target: artifact_event
    value: zeek-extract
    

**Respond:**
    
    
    - action: extension request
      extension action: run_on
      extension name: ext-strelka
      extension request:
        artifact_id: '{{ .routing.log_id }}'
    

### Usage

If you use the LimaCharlie [Zeek](https://beta.app.limacharlie.io/add-ons/extension-detail/ext-zeek) extension, a good use case would be to trigger a Zeek analysis upon ingestion of a PCAP artifact, which will generate the necessary Zeek artifacts to trigger the Strelka extension in the above example.

**Detect:**
    
    
    op: exists
    event: ingest
    artifact type: pcap
    path: /
    target: artifact_event
    

**Respond:**
    
    
    - action: extension request
      extension action: run_on
      extension name: ext-zeek
      extension request:
        artifact_id: '{{ .routing.log_id }}'
        retention: 30
    

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

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

###### What's Next

  * [ Twilio ](/docs/ext-twilio) __



Table of contents




Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


