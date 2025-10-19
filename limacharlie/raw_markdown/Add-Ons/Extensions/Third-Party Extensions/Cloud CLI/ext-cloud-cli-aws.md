# AWS

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
