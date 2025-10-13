## Overview

The [Twilio](https://www.twilio.com/) Extension allows you to send messages within Twilio. It requires you to setup the Twilio authentication in the **Integrations** section of your Organization.

Some more detailed information is available [here](https://www.twilio.com/docs/sms/send-messages).

## Setup

To start leveraging the Twilio extension, first subscribe to the `ext-twilio` add-on that can be accessed from the LimaCharlie **Marketplace**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/twilio.png)

After you have subscribed to the extension, setup the Twilio authentication in the `Secrets Manager` section of your organization.

Authentication in Twilio uses two components--a SID and a token. The LimaCharlie Twilio secret will combine both components in a single field like `SID/TOKEN`.

#### Detection & Response

Example Response portion of a  rule that sends a message out via Twilio as the response action:

```
- action: extension request
  extension action: run
  extension name: ext-twilio
  extension request:
    body: '{{ .event }}'
    from: '{{ "+10123456789" }}'
    to: '{{ "+10123456789" }}'
```

*Note that the* `{{ .event }}` *in the example above is the actual text that would be sent to the number you specify.*

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.
