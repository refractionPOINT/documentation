---
title: Using Extensions
slug: using-extensions
breadcrumb: Add-Ons > Extensions
source: https://docs.limacharlie.io/docs/using-extensions
articleId: f9093796-b087-48ea-b80a-731561475c5c
---

* * *

Using Extensions

  *  __01 Nov 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Using Extensions

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

## Components

Extensions can be interacted with using two main components:

### Configurations

Extension Configurations are records in [Hive](/v2/docs/config-hive). Each Extension has its configuration in the Hive record of the same name in the `extension_configuration` Hive.

These configurations are manipulated by simply storing the value in the record, LimaCharlie takes care of validating and notifying the Extension with the new value.

Configurations are a great way of storing rarely-written settings for an Extension without the developer of the Extension having to manage secure storage for it.

The structure of the configuration for a given Extension is published by the Extension via its "schema".

Schemas are available through the [Schema API](https://api.limacharlie.io/static/swagger/#/Extension-Schema/getExtensionSchema) or the LimaCharlie CLI: `limacharlie extension get_schema --help`.

### Requests

Requests are, as the name implies, direct individual requests to an Extension. A request contains an "action" and a "payload" (JSON object) to be sent to the Extension. Some requests can be flagged to have the Extension impersonate the requester (identity and permissions) during execution.

The "action" and "payload" entirely depends on the Extension it is destined to. The list of actions and individual payload structures available for an Extension is documented by each Extension using the "schema" they publish.

Schemas are available through the [Schema API](https://api.limacharlie.io/static/swagger/#/Extension-Schema/getExtensionSchema) or the LimaCharlie CLI: `limacharlie extension get_schema --help`.

## Interacting

### Interactively

The LimaCharlie webapp automatically displays a machine-generated user interface for each Extension based on the schema it publishes.

### Automation

[Detection & Response Rules](/docs/detection-and-response), the main automation mechanism in LimaCharlie can interact with Extensions using the `extension request` action in the Response component.

### API

Extensions can be interacted with using a few different APIs:

  * Getting the schema for an Extension: [https://api.limacharlie.io/static/swagger/#/Extension-Schema](https://api.limacharlie.io/static/swagger/#/Extension-Request)

  * Making requests to an Extension: <https://api.limacharlie.io/static/swagger/#/Extension-Request>




LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Command-line Interface

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

  * [ Extensions ](/docs/extensions)
  * [ Usage Alerts ](/docs/ext-usage-alerts)
  * [ REnigma ](/docs/ext-renigma)



* * *

###### What's Next

  * [ Building Extensions ](/docs/building-extensions) __



Table of contents

    * Components 
    * Interacting 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


