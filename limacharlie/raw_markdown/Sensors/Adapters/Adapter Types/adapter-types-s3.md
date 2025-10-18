---
title: S3
slug: adapter-types-s3
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-s3
articleId: 7081166b-e5ee-403a-b9df-bd3c1a13b005
---

* * *

S3

  *  __07 Aug 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# S3

  *  __Updated on 07 Aug 2025
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

This Adapter allows you to ingest files/blobs stored in AWS S3.

Note that this adapter operates as a sink by default, meaning it will "consume" files from the S3 bucket by deleting them once ingested.

### AWS S3 Requirements

Required IAM Permissions:
    
    
    {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": [
              "s3:ListBucket",
              "s3:GetObject",
              "s3:DeleteObject"
            ],
            "Resource": [
              "arn:aws:s3:::your-bucket-name",
              "arn:aws:s3:::your-bucket-name/*"
            ]
          }
        ]
      }

## Configurations

Adapter Type: `s3`

  * `client_options`: common configuration for adapter as defined [here](/v2/docs/adapters#usage).

  * `bucket_name`: the name of the bucket to ingest from.

  * `access_key`: an Access Key from S3 used to access the bucket.

  * `secret_key`: the secret key associated with the `access_key` used to access the bucket.

  * `prefix`: only ingest files with a given path prefix. **Do not include a leading**`/`**in the prefix.**

  * `single_load`: if `true`, the adapter will not operate as a sink, it will ingest all files in the bucket once and will then exit.




### Infrastructure as Code Deployment
    
    
    # AWS S3 Specific Docs: https://docs.limacharlie.io/docs/adapter-types-s3
    # For cloud sensor deployment, store credentials as hive secrets:
    
    #   access_key: "hive://secret/aws-access-key"
    #   secret_key: "hive://secret/aws-secret-key"
    
    sensor_type: "s3"
    s3:
      bucket_name: "your-s3-bucket-name-for-logs"
      access_key: "hive://secret/aws-s3-access-key"
      secret_key: "hive://secret/aws-s3-secret-key"
      client_options:
        identity:
          oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          installation_key: "YOUR_LC_INSTALLATION_KEY_S3"
        hostname: "aws-s3-adapter"
        platform: "json"
        sensor_seed_key: "s3-log-processor"
        mapping:
          sensor_hostname_path: "source_host"
          event_type_path: "event_category"
          event_time_path: "timestamp"
        indexing: []
      # Optional S3-specific configuration
      prefix: "logs/application_xyz/"              # Filter by object prefix
      parallel_fetch: 5                           # Parallel downloads
      single_load: false                          # Continuous processing

## API Doc

See the [official documentation](https://aws.amazon.com/s3/).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

Amazon Web Services

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

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

  * [ AWS ](/docs/ext-cloud-cli-aws)
  * [ AWS GuardDuty ](/docs/adapter-types-aws-guardduty)
  * [ AWS CloudTrail ](/docs/adapter-types-aws-cloudtrail)
  * [ Amazon S3 ](/docs/outputs-destinations-amazon-s3)
  * [ SQS ](/docs/adapter-types-sqs)



* * *

###### What's Next

  * [ Slack Audit Logs ](/docs/adapter-types-slack-audit-logs) __



Table of contents

    * Overview 
    * Configurations 
    * API Doc 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ aws ](/docs/en/tags/aws)
  * [ sensors ](/docs/en/tags/sensors)


