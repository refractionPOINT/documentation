---
title: AWS
slug: ext-cloud-cli-aws
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-aws
articleId: 53566b72-080d-4f58-bfa1-00694cf3e364
---

* * *

AWS

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# AWS

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

AWS CLI is a unified tool that provides a consistent interface for interacting with AWS from the command line. With this component of the Cloud CLI Extension, you can interact with AWS directly from LimaCharlie.

This extension makes use of AWS's native CLI tool, which can be found [here](https://awscli.amazonaws.com/v2/documentation/api/latest/index.html).

## Example

The following example would execute in response to AWS telemetry that 1) met certain criteria and 2) had an `instance_id` for an EC2 instance(s). The following response action would utilize the `.event.instance_id` to stop the corresponding EC2 instances.
    
    
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
    

## Credentials

To utilize AWS CLI capabilities, you will need:

  * You will need an AWS access key ID and AWS secret access key

  * Create a secret in the secrets manager in the following format:
    
        accessKeyID/secretAccessKey
    




Documentation on creating and managing AWS access keys and other IAM components can be found [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).

Amazon Web Services

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

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

  * [ AWS GuardDuty ](/docs/adapter-types-aws-guardduty)
  * [ AWS CloudTrail ](/docs/adapter-types-aws-cloudtrail)
  * [ Soteria AWS Rules ](/docs/soteria-aws-rules)
  * [ Amazon S3 ](/docs/outputs-destinations-amazon-s3)
  * [ SQS ](/docs/adapter-types-sqs)
  * [ S3 ](/docs/adapter-types-s3)



* * *

###### What's Next

  * [ Azure ](/docs/ext-cloud-cli-azure) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ aws ](/docs/en/tags/aws)
  * [ extensions ](/docs/en/tags/extensions)


