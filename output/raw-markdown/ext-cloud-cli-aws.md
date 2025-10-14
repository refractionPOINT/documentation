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

AWS

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# AWS

* Updated on 05 Oct 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

AWS CLI is a unified tool that provides a consistent interface for interacting with AWS from the command line. With this component of the Cloud CLI Extension, you can interact with AWS directly from LimaCharlie.

This extension makes use of AWS's native CLI tool, which can be found [here](https://awscli.amazonaws.com/v2/documentation/api/latest/index.html).

## Example

The following example would execute in response to AWS telemetry that 1) met certain criteria and 2) had an `instance_id` for an EC2 instance(s). The following response action would utilize the `.event.instance_id` to stop the corresponding EC2 instances.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "aws" }}'
    command_tokens:
      - ec2
      - stop-instances
      - '--instance-ids'
      - '{{ .event.instance_id  }}'
      - '--region'
      - us-east-1
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To utilize AWS CLI capabilities, you will need:

* You will need an AWS access key ID and AWS secret access key
* Create a secret in the secrets manager in the following format:

  ```
  accessKeyID/secretAccessKey
  ```

Documentation on creating and managing AWS access keys and other IAM components can be found [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).

Amazon Web Services

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

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

* [AWS GuardDuty](/docs/adapter-types-aws-guardduty)
* [AWS CloudTrail](/docs/adapter-types-aws-cloudtrail)
* [Soteria AWS Rules](/docs/soteria-aws-rules)
* [Amazon S3](/docs/outputs-destinations-amazon-s3)
* [SQS](/docs/adapter-types-sqs)
* [S3](/docs/adapter-types-s3)

---

###### What's Next

* [Azure](/docs/ext-cloud-cli-azure)

Table of contents

+ [Example](#example)
+ [Credentials](#credentials)

Tags

* [add-ons](/docs/en/tags/add-ons)
* [aws](/docs/en/tags/aws)
* [extensions](/docs/en/tags/extensions)
