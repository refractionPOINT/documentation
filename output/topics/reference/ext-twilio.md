# Twilio Extension

## Overview

The [Twilio](https://www.twilio.com/) Extension allows you to send SMS messages through Twilio's messaging service directly from LimaCharlie. This extension requires you to configure Twilio authentication credentials in the **Secrets Manager** section of your Organization.

Additional information about Twilio's messaging capabilities is available in the [Twilio SMS documentation](https://www.twilio.com/docs/sms/send-messages).

## Setup

### Subscribe to the Extension

To start leveraging the Twilio extension, first subscribe to the `ext-twilio` add-on from the LimaCharlie **Marketplace**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/twilio.png)

### Configure Authentication

After subscribing to the extension, set up Twilio authentication in the `Secrets Manager` section of your organization.

Authentication in Twilio uses two components: a SID (Account SID) and an authentication token. The LimaCharlie Twilio secret combines both components in a single field using the format: `SID/TOKEN`

For example, if your Twilio Account SID is `AC1234567890abcdef` and your Auth Token is `your_auth_token_here`, you would enter:
```
AC1234567890abcdef/your_auth_token_here
```

## Detection & Response Integration

The Twilio extension can be used as a response action in Detection & Response rules to send SMS notifications when security events are detected.

### Example Response Rule

Here is an example of the Response portion of a D&R rule that sends an SMS message via Twilio:

```yaml
- action: extension request
  extension action: run
  extension name: ext-twilio
  extension request:
    body: '{{ .event }}'
    from: '{{ "+10123456789" }}'
    to: '{{ "+10123456789" }}'
```

### Parameters

- **body**: The message content to send. Use `{{ .event }}` to include the actual event data in the message body.
- **from**: The Twilio phone number sending the message (must be in E.164 format, e.g., `+10123456789`)
- **to**: The destination phone number receiving the message (must be in E.164 format, e.g., `+10123456789`)

**Note**: The `{{ .event }}` template variable in the example above represents the actual event data that will be sent as the SMS message text. You can customize the message body to include specific fields or formatted text as needed.

## Related Concepts

**Extensions**: LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing.

**Organization**: In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations.