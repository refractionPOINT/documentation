[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v2

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Using Extensions

* 01 Nov 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Using Extensions

* Updated on 01 Nov 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

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

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### Related articles

* [Extensions](/docs/extensions)
* [Usage Alerts](/docs/ext-usage-alerts)
* [REnigma](/docs/ext-renigma)

---

###### What's Next

* [Building Extensions](/docs/building-extensions)

Table of contents

+ [Components](#components)
+ [Interacting](#interacting)

Tags

* [add-ons](/docs/en/tags/add-ons)
* [extensions](/docs/en/tags/extensions)
