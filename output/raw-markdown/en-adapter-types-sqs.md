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

SQS

* 07 Aug 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# SQS

* Updated on 07 Aug 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## Overview

This Adapter allows you to ingest events received from an AWS SQS instance.

## Configurations

Adapter Type: `sqs`

* `client_options`: common configuration for adapter as defined [here](/v2/docs/adapters#usage).
* `access_key`: an Access Key from AWS used to access the queue.
* `secret_key`: the secret key associated with the `access_key` used to access the queue.
* `queue_url`: the queue URL for the SQS instance.

### Infrastructure as Code Deployment

```
# AWS SQS Specific Docs: https://docs.limacharlie.io/docs/adapter-types-sqs

sensor_type: "sqs"
sqs:
  queue_url: "https://sqs.us-east-1.amazonaws.com/123456789012/your-security-logs-queue"
  aws_access_key_id: "hive://secret/aws-access-key-id"
  aws_secret_access_key: "hive://secret/aws-secret-access-key"
  aws_region: "us-east-1"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_SQS"
    platform: "json"
    sensor_seed_key: "aws-sqs-sensor"
    mapping:
      sensor_hostname_path: "source.instance_id"
      event_type_path: "detail.eventName"
      event_time_path: "time"
    indexing: []
  # Optional SQS-specific configuration
  max_messages: 10                       # Default: 10 (max messages per poll)
  wait_time_seconds: 20                  # Default: 20 (long polling)
  visibility_timeout: 300                # Default: 300 seconds
  delete_after_processing: true          # Default: true
```

## API Doc

See the [official documentation](https://aws.amazon.com/sqs/).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Amazon Web Services

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

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

* [AWS](/docs/ext-cloud-cli-aws)
* [AWS GuardDuty](/docs/adapter-types-aws-guardduty)
* [AWS CloudTrail](/docs/adapter-types-aws-cloudtrail)
* [Soteria AWS Rules](/docs/soteria-aws-rules)
* [Amazon S3](/docs/outputs-destinations-amazon-s3)
* [S3](/docs/adapter-types-s3)

---

###### What's Next

* [IIS Logs](/docs/adapter-types-iis)

Table of contents

+ [Overview](#overview)
+ [Configurations](#configurations)
+ [API Doc](#api-doc)

Tags

* [adapters](/docs/en/tags/adapters)
* [aws](/docs/en/tags/aws)
* [sensors](/docs/en/tags/sensors)
