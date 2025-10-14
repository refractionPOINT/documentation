These documents are **UNRELATED** - they cover different AWS integration topics in LimaCharlie. They should be kept separate.

---

# Soteria AWS Rules

**Last Updated:** 10 Oct 2025

AWS-specific detection rules for cloud security monitoring in LimaCharlie's Soteria platform.

Soteria AWS Rules provide pre-built detection logic designed to identify security threats, misconfigurations, and suspicious activities within AWS environments. These rules are tailored to AWS-specific telemetry and events ingested through LimaCharlie's various AWS adapters.

**Key Features:**
- Pre-configured detection rules for common AWS security threats
- Cloud-native threat detection patterns
- Integration with AWS services through LimaCharlie adapters
- Continuous monitoring of AWS infrastructure

**Use Cases:**
- Detect unauthorized AWS API calls
- Identify misconfigured security groups or IAM policies
- Monitor for unusual resource provisioning patterns
- Alert on suspicious access patterns to S3 buckets
- Track privilege escalation attempts in AWS environments

For detailed rule configurations and deployment instructions, refer to the [Soteria AWS Rules documentation](/docs/en/soteria-aws-rules).

---

# Amazon S3 Output Destination

**Last Updated:** 07 Oct 2025

Configure Amazon S3 as an output destination to export LimaCharlie telemetry, detection alerts, and other data for long-term storage, compliance, or downstream analysis.

**Configuration Overview:**

When configuring S3 as an output destination, you'll need to provide:
- **S3 Bucket Name**: The target bucket where data will be written
- **AWS Credentials**: IAM access key and secret key with appropriate permissions
- **Region**: The AWS region where your bucket resides
- **Prefix/Path**: Optional path prefix for organizing exported data
- **Data Format**: JSON, JSONL, or other supported formats

**Required IAM Permissions:**

Your IAM user or role must have permissions to write to the target S3 bucket:

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

**Data Organization:**

Exported data is typically organized by timestamp and data type:
- Events are partitioned by date for efficient querying
- File naming conventions support integration with tools like AWS Athena
- Data can be compressed to reduce storage costs

**Common Use Cases:**
- Long-term archival of security telemetry
- Compliance and audit trail retention
- Integration with AWS analytics services (Athena, Redshift, EMR)
- Backup and disaster recovery
- Cost-effective cold storage

For complete setup instructions, see the [Amazon S3 Output Destination documentation](/docs/en/outputs-destinations-amazon-s3).

---

# AWS SQS Adapter

**Last Updated:** 07 Aug 2025

The AWS Simple Queue Service (SQS) adapter enables LimaCharlie to ingest events from SQS queues, allowing you to collect and process messages from AWS services and applications.

**Adapter Configuration:**

To configure the SQS adapter, you'll need:
- **Queue URL**: The full URL of your SQS queue
- **AWS Credentials**: IAM access key and secret key with queue read permissions
- **Region**: The AWS region hosting your queue
- **Polling Interval**: How frequently to check for new messages
- **Message Format**: Expected message structure (JSON, raw text, etc.)

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
      "Resource": "arn:aws:sqs:region:account-id:queue-name"
    }
  ]
}
```

**Message Processing:**
- Messages are retrieved via long polling for efficiency
- Successfully processed messages are automatically deleted from the queue
- Failed messages can be configured to return to the queue or move to a dead-letter queue
- Message visibility timeout prevents duplicate processing

**Common Use Cases:**
- Ingesting AWS service notifications (S3 event notifications, SNS messages)
- Collecting application logs sent to SQS
- Processing AWS Config changes
- Receiving security alerts from third-party tools
- Decoupling data ingestion from data sources

For detailed configuration steps, visit the [SQS Adapter documentation](/docs/en/adapter-types-sqs).

---

# AWS S3 Adapter

**Last Updated:** 07 Aug 2025

The AWS S3 adapter allows LimaCharlie to ingest data from S3 buckets, enabling automated collection of logs, events, and other security-relevant data stored in S3.

**Adapter Configuration:**

Configure the S3 adapter with:
- **Bucket Name**: The S3 bucket to monitor
- **AWS Credentials**: IAM access key and secret key with bucket read permissions
- **Region**: The AWS region hosting your bucket
- **Prefix Filter**: Optional path prefix to limit which objects are ingested
- **File Pattern**: Regex or glob pattern to match specific files
- **Ingestion Schedule**: How often to scan for new objects
- **Processing Mode**: Stream new objects only, or process historical data

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

**File Processing:**
- Supports compressed files (gzip, zip)
- Handles various log formats (JSON, CSV, plain text)
- Tracks processed objects to avoid duplication
- Can parse structured and semi-structured data

**Event Notification Integration:**

For real-time ingestion, configure S3 event notifications to trigger processing:
1. Set up S3 bucket notifications for object creation events
2. Send notifications to SNS or SQS
3. Connect the SQS adapter to process notifications immediately

**Common Use Cases:**
- Ingesting AWS service logs (VPC Flow Logs, CloudTrail, ELB logs)
- Processing CloudWatch Logs exports
- Collecting application logs stored in S3
- Importing third-party security data
- Historical log analysis and backfill

For complete setup instructions, see the [S3 Adapter documentation](/docs/en/adapter-types-s3).

---

# AWS GuardDuty Adapter

**Last Updated:** 06 Jun 2025

The AWS GuardDuty adapter ingests security findings from AWS GuardDuty, enabling centralized threat detection and response across your AWS infrastructure through LimaCharlie.

**Adapter Configuration:**

To set up the GuardDuty adapter:
- **AWS Region**: The region(s) where GuardDuty is enabled
- **AWS Credentials**: IAM access key and secret key with GuardDuty read permissions
- **Finding Filters**: Optional filters to include/exclude specific finding types
- **Polling Interval**: How often to check for new findings
- **Severity Threshold**: Minimum severity level to ingest (Low, Medium, High, Critical)

**Required IAM Permissions:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "guardduty:ListDetectors",
        "guardduty:ListFindings",
        "guardduty:GetFindings"
      ],
      "Resource": "*"
    }
  ]
}
```

**Finding Types:**

GuardDuty findings ingested include:
- **Reconnaissance**: Port scanning, unusual API activity
- **Instance Compromise**: Malware, cryptocurrency mining, backdoors
- **Account Compromise**: Credential exposure, unusual login patterns
- **Bucket Compromise**: Suspicious S3 access patterns
- **IAM Abuse**: Privilege escalation, policy changes

**Data Enrichment:**

The adapter enriches GuardDuty findings with:
- Resource metadata (instance IDs, IP addresses, account details)
- Severity and confidence scores
- Finding timestamps and update history
- Related resources and entities

**Integration Benefits:**
- Correlate GuardDuty findings with endpoint telemetry
- Create unified detection and response workflows
- Aggregate AWS security alerts with other data sources
- Apply custom detection rules to GuardDuty findings
- Automate response actions based on findings

For detailed configuration, visit the [AWS GuardDuty Adapter documentation](/docs/en/adapter-types-aws-guardduty).

---

# AWS CloudTrail Adapter

**Last Updated:** 01 Nov 2024

The AWS CloudTrail adapter ingests AWS API activity logs from CloudTrail, providing visibility into user actions, resource changes, and administrative activities across your AWS accounts.

**Adapter Configuration:**

Configure the CloudTrail adapter with:
- **S3 Bucket**: The bucket where CloudTrail logs are delivered
- **AWS Credentials**: IAM access key and secret key with appropriate permissions
- **Trail Name**: Specific trail to monitor (optional)
- **Account Filter**: Filter logs by specific AWS account IDs
- **Event Filters**: Include/exclude specific AWS services or event types
- **Multi-Region Support**: Ingest from multiple AWS regions

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
        "arn:aws:s3:::cloudtrail-bucket-name",
        "arn:aws:s3:::cloudtrail-bucket-name/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudtrail:LookupEvents",
        "cloudtrail:GetTrailStatus"
      ],
      "Resource": "*"
    }
  ]
}
```

**Log Processing:**

The adapter handles:
- **Management Events**: API calls that modify AWS resources
- **Data Events**: S3 object-level operations, Lambda invocations
- **Insight Events**: Unusual API activity patterns detected by CloudTrail
- Log file validation and integrity checking
- Decompression and JSON parsing

**Key Fields Extracted:**
- Event name and type (API operation performed)
- User identity and credentials used
- Source IP address and user agent
- Request parameters and response elements
- Event time and AWS region
- Error codes and messages

**Detection Use Cases:**
- Unauthorized API calls or privilege escalation
- Configuration changes to security groups, IAM policies
- Resource creation/deletion by unauthorized users
- Root account usage
- Failed authentication attempts
- Data exfiltration patterns (unusual S3 downloads)
- Compliance monitoring (PCI-DSS, HIPAA requirements)

**Multi-Account Configuration:**

For AWS Organizations:
1. Configure CloudTrail organization trail
2. Centralize logs in a single S3 bucket
3. Point the adapter to the central bucket
4. Use account ID filters to segment data by account

For complete setup instructions, see the [AWS CloudTrail Adapter documentation](/docs/en/adapter-types-aws-cloudtrail).

---

# AWS CLI Extension

**Last Updated:** 05 Oct 2024

The AWS CLI extension for LimaCharlie provides command-line tools to manage AWS integrations, configure adapters, and orchestrate cloud security operations directly from your terminal.

**Installation:**

Install the AWS extension through the LimaCharlie CLI:

```bash
limacharlie extension install aws
```

**Configuration:**

Configure AWS credentials for the extension:

```bash
limacharlie aws configure
```

You'll be prompted for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region
- Output format

**Available Commands:**

**Adapter Management:**
```bash
# List configured AWS adapters
limacharlie aws adapter list

# Create a new S3 adapter
limacharlie aws adapter create --type s3 --bucket my-logs-bucket

# Create a CloudTrail adapter
limacharlie aws adapter create --type cloudtrail --bucket cloudtrail-logs

# Update adapter configuration
limacharlie aws adapter update <adapter-id> --config config.json

# Delete an adapter
limacharlie aws adapter delete <adapter-id>
```

**Output Destination Management:**
```bash
# Configure S3 as output destination
limacharlie aws output create --bucket my-output-bucket --region us-east-1

# List configured outputs
limacharlie aws output list

# Test output connectivity
limacharlie aws output test <output-id>
```

**GuardDuty Integration:**
```bash
# Connect GuardDuty detector
limacharlie aws guardduty connect --region us-east-1

# List GuardDuty findings
limacharlie aws guardduty findings --severity HIGH

# Sync findings to LimaCharlie
limacharlie aws guardduty sync
```

**CloudTrail Operations:**
```bash
# Verify CloudTrail configuration
limacharlie aws cloudtrail verify --trail-name my-trail

# Backfill historical logs
limacharlie aws cloudtrail backfill --start 2025-01-01 --end 2025-01-31
```

**IAM Policy Generation:**

Generate least-privilege IAM policies for adapters:

```bash
# Generate policy for S3 adapter
limacharlie aws iam policy --type s3 --bucket my-logs-bucket

# Generate policy for CloudTrail adapter
limacharlie aws iam policy --type cloudtrail --bucket cloudtrail-logs

# Generate combined policy for multiple services
limacharlie aws iam policy --services s3,cloudtrail,guardduty
```

**Credential Management:**

```bash
# Store credentials securely
limacharlie aws credentials store --profile prod

# List stored profiles
limacharlie aws credentials list

# Rotate credentials
limacharlie aws credentials rotate --profile prod
```

**Common Workflows:**

**Initial AWS Integration Setup:**
```bash
# 1. Configure credentials
limacharlie aws configure --profile production

# 2. Generate IAM policies
limacharlie aws iam policy --services s3,cloudtrail,guardduty > aws-policy.json

# 3. Create adapters
limacharlie aws adapter create --type cloudtrail --bucket my-cloudtrail-logs
limacharlie aws adapter create --type guardduty --region us-east-1

# 4. Configure output destination
limacharlie aws output create --bucket limacharlie-exports
```

**Troubleshooting:**

```bash
# Test AWS connectivity
limacharlie aws test-connection

# Validate adapter permissions
limacharlie aws adapter validate <adapter-id>

# View adapter ingestion statistics
limacharlie aws adapter stats <adapter-id>

# Check for configuration issues
limacharlie aws diagnose
```

For complete CLI reference, see the [AWS CLI Extension documentation](/docs/en/ext-cloud-cli-aws).