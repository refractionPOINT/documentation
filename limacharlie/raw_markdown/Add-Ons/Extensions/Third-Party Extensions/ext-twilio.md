---
title: Twilio
slug: ext-twilio
breadcrumb: Add-Ons > Extensions > Third-Party Extensions
source: https://docs.limacharlie.io/docs/ext-twilio
articleId: d5f6e69a-60f8-4ce9-b037-7c9b2ecf65cf
---

* * *

Twilio

  *  __10 Oct 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Twilio

  *  __Updated on 10 Oct 2025
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

## Overview

The [Twilio](https://www.twilio.com/) Extension allows you to send messages within Twilio. It requires you to setup the Twilio authentication in the **Integrations** section of your Organization.

Some more detailed information is available [here](https://www.twilio.com/docs/sms/send-messages).

## Setup

To start leveraging the Twilio extension, first subscribe to the `ext-twilio` add-on that can be accessed from the LimaCharlie**Marketplace**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/twilio.png)

After you have subscribed to the extension, setup the Twilio authentication in the `Secrets Manager` section of your organization.

Authentication in Twilio uses two components--a SID and a token. The LimaCharlie Twilio secret will combine both components in a single field like `SID/TOKEN`.

#### Detection & Response

Example Response portion of a  rule that sends a message out via Twilio as the response action:
    
    
    - action: extension request
      extension action: run
      extension name: ext-twilio
      extension request:
        body: '{{ .event }}'
        from: '{{ "+10123456789" }}'
        to: '{{ "+10123456789" }}'
    

_Note that the_`{{ .event }}`_in the example above is the actual text that would be sent to the number you specify._

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

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

###### What's Next

  * [ Velociraptor ](/docs/ext-velociraptor) __



Table of contents

    * Overview 
    * Setup 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


