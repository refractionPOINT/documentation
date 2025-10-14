# AWS Integration

LimaCharlie provides comprehensive AWS integration capabilities for security monitoring, threat detection, and compliance across your AWS infrastructure.

## Overview

The AWS integration enables organizations to ingest, analyze, and respond to security events from AWS services. This includes CloudTrail logs, GuardDuty findings, and other AWS service logs, providing centralized visibility and automated threat detection across your AWS environment.

## Available AWS Integrations

### CloudTrail

AWS CloudTrail records AWS API calls and related events made by or on behalf of your AWS account. The LimaCharlie CloudTrail adapter ingests these logs for security monitoring, compliance, and incident response.

**Key Features:**
- API activity monitoring across all AWS services
- User and resource change tracking
- Compliance auditing
- Operational troubleshooting

**Key Event Fields:**
- `eventName`: API action performed
- `eventSource`: AWS service
- `userIdentity`: Who made the request
- `sourceIPAddress`: Origin IP
- `requestParameters`: API call parameters
- `responseElements`: API response details
- `eventTime`: When the event occurred

**Log Structure:**
```
s3://bucket-name/AWSLogs/account-id/CloudTrail/region/YYYY/MM/DD/
```

### GuardDuty

AWS GuardDuty is a threat detection service that continuously monitors for malicious activity and unauthorized behavior. The LimaCharlie adapter ingests GuardDuty findings for centralized analysis, correlation, and response.

**Finding Types:**
- **Reconnaissance**: Port scanning, unusual API calls
- **Instance Compromise**: Malware, cryptocurrency mining, command and control
- **Account Compromise**: Credential access, privilege escalation
- **Bucket Compromise**: Suspicious S3 access patterns
- **IAM**: Unusual authentication patterns, policy changes

**Integration Methods:**

1. **S3 Export**: GuardDuty exports findings to S3, LimaCharlie S3 adapter ingests them
2. **CloudWatch Events + SQS**: Real-time delivery via EventBridge to SQS queue

### S3 Adapter

The S3 adapter allows LimaCharlie to ingest data from Amazon S3 buckets automatically.

**Processing Modes:**
- **Polling Mode**: Periodically checks for new files in the bucket
- **Event-Driven Mode**: S3 event notifications trigger immediate processing

**Supported File Formats:**
- JSON (single events or arrays)
- JSONL (JSON Lines)
- CSV (with header row)
- Plain text (line-delimited)
- Compressed files (.gz, .zip)

**Configuration Parameters:**

| Parameter | Description | Required |
|-----------|-------------|----------|
| Bucket Name | Name of your S3 bucket | Yes |
| Region | AWS region where bucket is located | Yes |
| Access Key ID | AWS access key ID | Yes |
| Secret Access Key | AWS secret access key | Yes |
| Path Prefix | Optional prefix to filter objects | No |
| File Pattern | Optional regex pattern for file names | No |

**Required IAM Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

**Common Use Cases:**
- Processing AWS service logs (VPC Flow Logs, CloudTrail, etc.)
- Ingesting third-party security tool exports
- Batch processing of security events
- Historical log analysis

### SQS Adapter

The SQS adapter allows LimaCharlie to ingest events from Amazon Simple Queue Service (SQS).

**Configuration Parameters:**

| Parameter | Description |
|-----------|-------------|
| Queue URL | Full URL of your SQS queue |
| Region | AWS region where queue is located |
| Access Key ID | AWS access key ID |
| Secret Access Key | AWS secret access key |

**Required IAM Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:*:*:your-queue-name"
    }
  ]
}
```

**Message Format:**
Messages should be JSON formatted. The adapter will parse incoming messages and create events in LimaCharlie.

**Common Use Cases:**
- Ingesting AWS service notifications
- Receiving events from custom applications
- Integration with AWS Lambda functions
- CloudWatch alarm notifications

### S3 as Output Destination

LimaCharlie supports Amazon S3 as an output destination for events, detections, and other data.

**Output Format:**
Data sent to S3 is organized by:
- Organization ID
- Date (YYYY/MM/DD)
- Event type
- Files are compressed (gzip)

**File Naming Convention:**
```
<org-id>/<year>/<month>/<day>/<event-type>/<timestamp>-<uuid>.json.gz
```

**Configuration Parameters:**

| Parameter | Description | Required |
|-----------|-------------|----------|
| Bucket Name | S3 bucket name | Yes |
| Region | AWS region | Yes |
| Access Key ID | AWS access key | Yes |
| Secret Access Key | AWS secret key | Yes |
| Path Prefix | Optional prefix for objects | No |

**Required IAM Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

**Use Cases:**
- Long-term event storage
- Compliance and audit requirements
- Data lake integration
- Historical analysis
- Backup and disaster recovery

## Soteria AWS Rules

LimaCharlie's Soteria service provides automated security monitoring and threat detection rules specifically designed for AWS environments. These rules analyze CloudTrail logs and other AWS service events to identify suspicious activities, misconfigurations, and potential security threats.

**Detection Categories:**

### IAM Security
- Detection of IAM user creation without MFA
- Identification of overly permissive IAM policies
- Monitoring for root account usage
- Tracking privilege escalation attempts

### Network Security
- Security group rule changes
- VPC configuration modifications
- Network ACL changes
- Unusual outbound traffic patterns

### Data Protection
- S3 bucket policy changes
- Encryption setting modifications
- Public access enablement
- Cross-region replication changes

### Compliance
- Detection of non-compliant resource configurations
- Monitoring for policy violations
- Tracking of configuration drift

**Configuration:**
Soteria AWS Rules are automatically enabled when you configure AWS CloudTrail ingestion into LimaCharlie. The rules work by analyzing CloudTrail events in real-time and generating alerts when suspicious patterns are detected.

**Response Actions:**
When Soteria AWS Rules detect threats, you can configure automated responses:
- Send alerts to your SIEM or incident response platform
- Trigger automated remediation workflows
- Generate tickets in your ticketing system
- Send notifications to security team members

## AWS CLI Integration

The AWS extension is included in the LimaCharlie CLI, allowing you to manage AWS-related configurations and automations.

### Installation

```bash
pip install limacharlie --upgrade
```

### Authentication

Configure AWS credentials for use with LimaCharlie:

```bash
limacharlie ext aws configure
```

You'll be prompted for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region

### Available Commands

**Configure AWS Integration:**
```bash
limacharlie ext aws configure
```

**Test Connection:**
```bash
limacharlie ext aws test
```

**List Configured Adapters:**
```bash
limacharlie ext aws list-adapters
```

**Deploy CloudTrail Integration:**
```bash
limacharlie ext aws setup-cloudtrail --bucket <bucket-name>
```

**Deploy GuardDuty Integration:**
```bash
limacharlie ext aws setup-guardduty
```

### Configuration File

AWS settings are stored in your LimaCharlie configuration:

```yaml
aws:
  access_key_id: YOUR_ACCESS_KEY
  secret_access_key: YOUR_SECRET_KEY
  region: us-east-1
```

## Setup Steps

### CloudTrail Integration

1. Ensure CloudTrail is logging to an S3 bucket
2. Navigate to Adapters in LimaCharlie
3. Add S3 adapter configured for your CloudTrail bucket
4. Configure path prefix to match CloudTrail structure: `AWSLogs/<account-id>/CloudTrail/`
5. Apply CloudTrail parsing rules

### GuardDuty Integration

**Option 1: S3 Export Method**

1. Configure GuardDuty to export findings to S3
2. Set up S3 adapter in LimaCharlie pointing to the GuardDuty findings bucket
3. Configure parsing rules for GuardDuty finding format

**Option 2: Real-Time via SQS**

1. Create an EventBridge rule for GuardDuty findings
2. Configure SQS queue as target
3. Set up SQS adapter in LimaCharlie
4. GuardDuty findings will be delivered in real-time

**Required IAM Permissions (S3-based ingestion):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::guardduty-findings-bucket",
        "arn:aws:s3:::guardduty-findings-bucket/*"
      ]
    }
  ]
}
```

### Prerequisites

- An active AWS account
- AWS credentials with appropriate permissions
- For CloudTrail: CloudTrail enabled and configured
- For GuardDuty: GuardDuty enabled in your account
- S3 buckets configured for log/finding storage
- Optional: S3 event notifications or CloudWatch Events configured for real-time processing

## Use Cases

- **Centralized threat visibility**: Aggregate security events across multiple AWS accounts
- **Compliance monitoring**: Track API activities and resource changes for audit requirements
- **Incident response**: Correlate GuardDuty findings with endpoint telemetry
- **Threat hunting**: Historical analysis of AWS activity patterns
- **Automated response**: Trigger remediation workflows based on AWS security events
- **Long-term retention**: Archive events to S3 for compliance and analysis

## Best Practices

1. **Use IAM roles with least privilege**: Grant only necessary permissions
2. **Rotate credentials regularly**: Implement credential rotation policies
3. **Enable CloudTrail in all regions**: Ensure complete visibility
4. **Configure S3 bucket lifecycle policies**: Manage storage costs
5. **Use separate AWS accounts for production/development**: Isolate environments
6. **Enable encryption**: Encrypt data at rest and in transit
7. **Monitor integration health**: Track adapter connectivity and processing status
8. **Implement alerting**: Configure notifications for critical findings
9. **Regular review**: Periodically audit configurations and permissions
10. **Test integrations**: Validate ingestion with sample events before production deployment