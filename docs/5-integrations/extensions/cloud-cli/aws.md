# AWS

The AWS CLI is a single tool with a consistent interface to AWS from the command line. This component of the Cloud CLI Extension lets you interact with AWS directly from LimaCharlie.

This extension uses [AWS's native CLI tool](https://awscli.amazonaws.com/v2/documentation/api/latest/index.html).

## Example

This example runs in response to AWS telemetry that 1) matches certain criteria and 2) has an `instance_id` for one or more EC2 instances. The response action uses the `.event.instance_id` value to stop those EC2 instances.

```yaml
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    tool: '{{ "aws" }}'
    command_tokens:
      - ec2
      - stop-instances
      - '--instance-ids'
      - '{{ .event.instance_id  }}'
      - '--region'
      - us-east-1
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To use the AWS CLI capabilities, you need:

- An AWS access key ID and an AWS secret access key
- Create a secret in the secrets manager in this format:

  ```text
  accessKeyID/secretAccessKey
  ```

AWS supplies [documentation about how to create and manage access keys and other IAM components](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).
