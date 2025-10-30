# AWS Security Monitoring with LimaCharlie

Complete guide for implementing AWS security monitoring using LimaCharlie adapters, detection rules, and managed rulesets.

## Overview

LimaCharlie provides comprehensive AWS security monitoring through:
- CloudTrail audit log ingestion via S3 or SQS
- GuardDuty findings integration
- Pre-built detection rules (Soteria)
- Custom threat detection
- Automated response actions

## AWS Data Sources

### 1. AWS CloudTrail

CloudTrail provides audit logs for all AWS API activity, essential for detecting:
- IAM abuse and privilege escalation
- Unauthorized access attempts
- Resource modifications
- Data exfiltration attempts

**Platform**: `aws`

#### CloudTrail via S3 Bucket

**Configuration**:
```yaml
s3:
  client_options:
    hostname: aws-cloudtrail-logs
    identity:
      installation_key: <INSTALLATION_KEY>
      oid: <OID>
    platform: aws
    sensor_seed_key: aws-cloudtrail-production
  bucket_name: <S3_BUCKET_NAME>
  secret_key: <S3_SECRET_KEY>
  access_key: <S3_ACCESS_KEY>
```

**CLI Command**:
```bash
./lc_adapter s3 \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=aws \
  client_options.hostname=aws-cloudtrail-logs \
  client_options.sensor_seed_key=aws-cloudtrail-production \
  bucket_name=<S3_BUCKET_NAME> \
  access_key=<ACCESS_KEY> \
  secret_key=<SECRET_KEY>
```

**When to Use**:
- Cost-effective for lower-volume environments
- Acceptable latency (5-15 minutes)
- S3 bucket already configured for CloudTrail

#### CloudTrail via SQS Queue

**Configuration**:
```yaml
sqs:
  client_options:
    hostname: aws-cloudtrail-logs
    identity:
      installation_key: <INSTALLATION_KEY>
      oid: <OID>
    platform: aws
    sensor_seed_key: aws-cloudtrail-production
  region: <SQS_REGION>
  secret_key: <SQS_SECRET_KEY>
  access_key: <SQS_ACCESS_KEY>
  queue_url: <SQS_QUEUE_URL>
```

**CLI Command**:
```bash
./lc_adapter sqs \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=aws \
  client_options.hostname=aws-cloudtrail-logs \
  client_options.sensor_seed_key=aws-cloudtrail-production \
  region=<SQS_REGION> \
  access_key=<ACCESS_KEY> \
  secret_key=<SECRET_KEY> \
  queue_url=<SQS_QUEUE_URL>
```

**When to Use**:
- Near real-time monitoring required
- Event-driven architecture preferred
- Lower latency critical (seconds vs minutes)

**AWS Setup**:
1. Configure CloudTrail to send to S3
2. Create SNS topic
3. Configure S3 bucket to publish to SNS on new object
4. Create SQS queue
5. Subscribe SQS to SNS topic
6. Set appropriate IAM permissions

### 2. AWS GuardDuty

GuardDuty provides intelligent threat detection with pre-analyzed security findings, including:
- Reconnaissance attempts
- Instance compromise indicators
- Account compromise patterns
- Cryptocurrency mining
- Data exfiltration

**Platform**: `guard_duty`

#### GuardDuty via S3 Bucket

**CLI Command**:
```bash
./lc_adapter s3 \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=guard_duty \
  client_options.hostname=guardduty-logs \
  bucket_name=<BUCKET_NAME> \
  access_key=<ACCESS_KEY> \
  secret_key=<SECRET_KEY>
```

**AWS Setup**:
1. Enable GuardDuty in AWS Console
2. Export findings to S3 via CloudWatch Events/EventBridge
3. Configure IAM permissions for adapter

#### GuardDuty via SQS Queue

**CLI Command**:
```bash
./lc_adapter sqs \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=guard_duty \
  client_options.sensor_seed_key=<SENSOR_SEED_KEY> \
  client_options.hostname=guardduty-logs \
  access_key=<ACCESS_KEY> \
  secret_key=<SECRET_KEY> \
  queue_url=<QUEUE_URL> \
  region=<AWS_REGION>
```

**AWS Setup**:
1. Enable GuardDuty
2. Create EventBridge rule for GuardDuty findings
3. Target SNS topic
4. Subscribe SQS queue to SNS
5. Configure IAM permissions

## AWS Detection Rules

### Detect Root Account Usage

**Threat**: Root account provides unrestricted access. Usage indicates potential compromise or poor security practices.

```yaml
# Detection
event: AwsApiCall
op: and
rules:
  - op: is
    path: event/userIdentity/type
    value: Root
  - op: exists
    path: event/eventName

# Response
- action: report
  name: AWS Root Account Activity Detected
  metadata:
    severity: critical
    account: "{{ .event.userIdentity.accountId }}"
    event: "{{ .event.eventName }}"
    region: "{{ .event.awsRegion }}"
```

**Tuning Tips**:
- Exclude known automated root actions (if any exist)
- Alert immediately - root usage should be rare
- Consider blocking programmatic root access entirely

### Detect IAM Policy Changes

**Threat**: Policy changes can grant unauthorized access, escalate privileges, or establish persistence.

```yaml
# Detection
event: AwsApiCall
op: or
rules:
  - op: is
    path: event/eventName
    value: PutUserPolicy
  - op: is
    path: event/eventName
    value: PutRolePolicy
  - op: is
    path: event/eventName
    value: PutGroupPolicy
  - op: is
    path: event/eventName
    value: AttachUserPolicy
  - op: is
    path: event/eventName
    value: AttachRolePolicy
  - op: is
    path: event/eventName
    value: AttachGroupPolicy

# Response
- action: report
  name: AWS IAM Policy Modification
  metadata:
    user: "{{ .event.userIdentity.principalId }}"
    event: "{{ .event.eventName }}"
```

**Tuning Tips**:
- Exclude known IaC service accounts (Terraform, CloudFormation)
- Add time-based suppression for change windows
- Monitor for unusual actors making changes

### Detect S3 Bucket Exposure

**Threat**: Public S3 buckets can lead to data exposure and compliance violations.

```yaml
# Detection
event: AwsApiCall
op: and
rules:
  - op: or
    rules:
      - op: is
        path: event/eventName
        value: PutBucketPublicAccessBlock
      - op: is
        path: event/eventName
        value: DeleteBucketPublicAccessBlock
      - op: is
        path: event/eventName
        value: PutBucketAcl
  - op: contains
    path: event/requestParameters
    value: public

# Response
- action: report
  name: S3 Bucket Public Access Configuration Changed
  metadata:
    bucket: "{{ .event.requestParameters.bucketName }}"
    user: "{{ .event.userIdentity.principalId }}"
```

**Tuning Tips**:
- Always alert on public access block removal
- Maintain allow-list of intentionally public buckets
- Consider automated remediation

### Detect EC2 Instance Launched from Unusual Region

**Threat**: Cryptojacking often involves launching instances in unexpected regions to avoid detection.

```yaml
# Detection
event: AwsApiCall
op: and
rules:
  - op: is
    path: event/eventName
    value: RunInstances
  - op: not in
    path: event/awsRegion
    values:
      - us-east-1
      - us-west-2
      - eu-west-1

# Response
- action: report
  name: EC2 Instance Launched in Unusual Region
  metadata:
    region: "{{ .event.awsRegion }}"
    user: "{{ .event.userIdentity.principalId }}"
    instance_type: "{{ .event.requestParameters.instanceType }}"
```

**Tuning Tips**:
- Customize region allow-list based on your usage
- Alert on expensive instance types (p3, g4, etc.)
- Track instance launch patterns by user

### Detect Security Group Modifications

**Threat**: Security group changes can expose services to internet or enable lateral movement.

```yaml
# Detection
event: AwsApiCall
op: or
rules:
  - op: is
    path: event/eventName
    value: AuthorizeSecurityGroupIngress
  - op: is
    path: event/eventName
    value: AuthorizeSecurityGroupEgress
  - op: is
    path: event/eventName
    value: RevokeSecurityGroupIngress
  - op: is
    path: event/eventName
    value: RevokeSecurityGroupEgress

# Response
- action: report
  name: AWS Security Group Modified
  metadata:
    group: "{{ .event.requestParameters.groupId }}"
    user: "{{ .event.userIdentity.principalId }}"
```

**Enhanced Detection - 0.0.0.0/0 Exposure**:
```yaml
# Detection
event: AwsApiCall
op: and
rules:
  - op: is
    path: event/eventName
    value: AuthorizeSecurityGroupIngress
  - op: contains
    path: event/requestParameters
    value: 0.0.0.0/0

# Response
- action: report
  name: Security Group Opened to Internet
  metadata:
    severity: high
    group: "{{ .event.requestParameters.groupId }}"
```

### Detect Console Login Without MFA

**Threat**: Console access without MFA increases risk of account compromise.

```yaml
# Detection
event: AwsApiCall
op: and
rules:
  - op: is
    path: event/eventName
    value: ConsoleLogin
  - op: is
    path: event/responseElements/ConsoleLogin
    value: Success
  - op: or
    rules:
      - not: true
        op: exists
        path: event/additionalEventData/MFAUsed
      - op: is
        path: event/additionalEventData/MFAUsed
        value: "No"

# Response
- action: report
  name: AWS Console Login Without MFA
  metadata:
    user: "{{ .event.userIdentity.principalId }}"
    ip: "{{ .event.sourceIPAddress }}"
```

**Tuning Tips**:
- Enforce MFA at IAM policy level
- Alert on all non-MFA logins
- Track repeat offenders

### Detect CloudTrail Disabled or Modified

**Threat**: Attackers disable logging to hide their activities.

```yaml
# Detection
event: AwsApiCall
op: or
rules:
  - op: is
    path: event/eventName
    value: StopLogging
  - op: is
    path: event/eventName
    value: DeleteTrail
  - op: is
    path: event/eventName
    value: UpdateTrail

# Response
- action: report
  name: AWS CloudTrail Configuration Changed
  metadata:
    severity: critical
    trail: "{{ .event.requestParameters.name }}"
    user: "{{ .event.userIdentity.principalId }}"
    event: "{{ .event.eventName }}"
```

### Detect KMS Key Deletion or Rotation

**Threat**: KMS key operations can impact data access and indicate potential attack.

```yaml
# Detection
event: AwsApiCall
op: or
rules:
  - op: is
    path: event/eventName
    value: ScheduleKeyDeletion
  - op: is
    path: event/eventName
    value: DisableKey
  - op: is
    path: event/eventName
    value: DeleteAlias

# Response
- action: report
  name: AWS KMS Key Deletion Initiated
  metadata:
    key: "{{ .event.requestParameters.keyId }}"
    user: "{{ .event.userIdentity.principalId }}"
```

### Detect Secrets Manager Access

**Threat**: Monitor access to secrets for potential credential theft.

```yaml
# Detection
event: AwsApiCall
op: is
path: event/eventName
value: GetSecretValue

# Response
- action: report
  name: AWS Secrets Manager Secret Retrieved
  metadata:
    secret: "{{ .event.requestParameters.secretId }}"
    user: "{{ .event.userIdentity.principalId }}"
  suppression:
    is_global: false
    keys:
      - "{{ .event.userIdentity.principalId }}"
      - "{{ .event.requestParameters.secretId }}"
    max_count: 1
    period: 3600
```

### Detect Failed Authentication Attempts

**Threat**: Multiple failed logins indicate brute force or credential stuffing.

```yaml
# Detection
event: AwsApiCall
op: and
rules:
  - op: is
    path: event/eventName
    value: ConsoleLogin
  - op: is
    path: event/responseElements/ConsoleLogin
    value: Failure

# Response
- action: report
  name: AWS Console Login Failure
  metadata:
    user: "{{ .event.userIdentity.principalId }}"
    ip: "{{ .event.sourceIPAddress }}"
```

### Detect Unusual API Call Volume

**Threat**: Spike in API calls may indicate automated attack or compromise.

```yaml
# Detection
event: AwsApiCall
op: exists
path: event/eventName

# Response
- action: report
  name: AWS API Call Activity
  suppression:
    is_global: false
    keys:
      - "{{ .event.userIdentity.principalId }}"
      - "{{ .event.eventName }}"
    max_count: 100
    period: 300
  metadata:
    user: "{{ .event.userIdentity.principalId }}"
    event: "{{ .event.eventName }}"
```

## Soteria AWS Rules

LimaCharlie offers managed detection rules from Soteria specifically for AWS environments.

**Setup**:
1. Navigate to Add-Ons > Extensions in LimaCharlie
2. Subscribe to the `soteria-rules-aws` extension
3. Subscribe to the `tor` lookup (free, required dependency)
4. Configure AWS CloudTrail and GuardDuty adapters

**Coverage**:
- AWS CloudTrail event analysis
- AWS GuardDuty finding correlation
- IAM abuse patterns
- Data exfiltration detection
- Resource misconfiguration alerts
- Privilege escalation attempts
- Lateral movement indicators
- Persistence mechanisms

**Benefits**:
- Pre-tuned detection logic
- Regular updates for new threats
- Reduced false positives
- Community-driven improvements
- Professional SOC-grade rules

**Best Practice**: Start with Soteria rules as your baseline, then add custom rules for organization-specific needs.

## Complete AWS Setup

### Step 1: Enable CloudTrail

1. Navigate to CloudTrail in AWS Console
2. Create Trail or use existing
3. Enable for all regions
4. Log to dedicated S3 bucket
5. Enable log file validation

**Recommended Settings**:
- Management events: Read and Write
- Data events: Initially disabled (high volume/cost)
- Insights events: Optional (additional cost)

### Step 2: Configure S3 to SQS Pipeline

**For real-time monitoring**:

1. Create SNS Topic:
```bash
aws sns create-topic --name cloudtrail-notifications
```

2. Create SQS Queue:
```bash
aws sqs create-queue --queue-name cloudtrail-logs
```

3. Subscribe Queue to Topic:
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT:cloudtrail-notifications \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:ACCOUNT:cloudtrail-logs
```

4. Configure S3 Bucket Notifications:
```json
{
  "TopicConfigurations": [
    {
      "TopicArn": "arn:aws:sns:us-east-1:ACCOUNT:cloudtrail-notifications",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "AWSLogs/"
            }
          ]
        }
      }
    }
  ]
}
```

### Step 3: Create IAM User for Adapter

**Minimum Permissions**:
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
      "Resource": "arn:aws:sqs:*:*:cloudtrail-logs"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::cloudtrail-bucket/*"
    }
  ]
}
```

### Step 4: Deploy CloudTrail Adapter

```bash
# Download adapter
curl -L https://downloads.limacharlie.io/adapter/linux/64 -o lc_adapter
chmod +x lc_adapter

# Run adapter
./lc_adapter sqs \
  client_options.identity.installation_key=<YOUR_INSTALLATION_KEY> \
  client_options.identity.oid=<YOUR_OID> \
  client_options.platform=aws \
  client_options.hostname=aws-cloudtrail-production \
  client_options.sensor_seed_key=aws-ct-prod \
  region=us-east-1 \
  access_key=<IAM_ACCESS_KEY> \
  secret_key=<IAM_SECRET_KEY> \
  queue_url=https://sqs.us-east-1.amazonaws.com/ACCOUNT/cloudtrail-logs
```

**Using Hive Secrets**:
```bash
./lc_adapter sqs \
  client_options.identity.installation_key=<YOUR_INSTALLATION_KEY> \
  client_options.identity.oid=<YOUR_OID> \
  client_options.platform=aws \
  client_options.hostname=aws-cloudtrail-production \
  client_options.sensor_seed_key=aws-ct-prod \
  region=us-east-1 \
  access_key=hive://secret/aws-access-key \
  secret_key=hive://secret/aws-secret-key \
  queue_url=https://sqs.us-east-1.amazonaws.com/ACCOUNT/cloudtrail-logs
```

### Step 5: Enable and Configure GuardDuty

1. Enable GuardDuty in AWS Console
2. Create EventBridge Rule for findings
3. Configure SQS queue for findings
4. Deploy GuardDuty adapter

**GuardDuty Adapter**:
```bash
./lc_adapter sqs \
  client_options.identity.installation_key=<YOUR_INSTALLATION_KEY> \
  client_options.identity.oid=<YOUR_OID> \
  client_options.platform=guard_duty \
  client_options.hostname=aws-guardduty-production \
  client_options.sensor_seed_key=aws-gd-prod \
  region=us-east-1 \
  access_key=<IAM_ACCESS_KEY> \
  secret_key=<IAM_SECRET_KEY> \
  queue_url=https://sqs.us-east-1.amazonaws.com/ACCOUNT/guardduty-findings
```

### Step 6: Subscribe to Soteria Rules

1. Navigate to Add-Ons > Extensions
2. Subscribe to `soteria-rules-aws`
3. Subscribe to `tor` lookup

### Step 7: Deploy Custom Detection Rules

Deploy the detection rules from this guide, prioritizing:
1. Root account monitoring
2. IAM policy changes
3. Security group modifications
4. S3 public access
5. Console login without MFA
6. CloudTrail tampering

### Step 8: Configure Outputs

Set up outputs to your SIEM, Slack, or incident response platform:

1. Navigate to Outputs in LimaCharlie
2. Create output (Slack, Webhook, Syslog, etc.)
3. Configure filters to match AWS detections
4. Test with known detection

### Step 9: Validate Setup

1. Check adapter connectivity:
   - Navigate to Sensors in LimaCharlie
   - Verify `aws-cloudtrail-production` and `aws-guardduty-production` are online

2. Generate test events:
   - Perform a console login
   - Create/delete a security group rule
   - View event in LimaCharlie Timeline

3. Test detection rules:
   - Trigger known detection (e.g., root account action)
   - Verify alert generated
   - Check output delivery

## AWS Best Practices

### Critical Events to Monitor

**High Priority**:
- Root account usage
- IAM policy changes
- Security group modifications
- S3 bucket permission changes
- Console logins without MFA
- CloudTrail configuration changes
- KMS key operations

**Medium Priority**:
- EC2 instance launches
- VPC changes
- Route table modifications
- Network ACL changes
- Secrets Manager access
- Parameter Store access

**Context-Dependent**:
- Lambda function changes
- RDS instance modifications
- EBS snapshot sharing
- AMI sharing
- Elastic IP allocation

### Cost Management

**Reduce CloudTrail Costs**:
1. Start with management events only
2. Add data events selectively (S3, Lambda)
3. Use CloudTrail Insights sparingly
4. Configure lifecycle policies on S3 bucket

**Reduce Ingestion Costs**:
1. Filter read-only operations if acceptable
2. Exclude high-volume services (if not critical)
3. Sample non-critical events
4. Use GuardDuty for automated analysis

**Example Filter**:
```yaml
# Exclude read-only operations
event: AwsApiCall
op: not contains
path: event/eventName
value: Describe
```

### Security Hygiene

**Protect Credentials**:
- Use Hive Secrets for all credentials
- Rotate IAM keys quarterly
- Use IAM roles when possible (EC2, Lambda)
- Enable MFA for adapter IAM user

**Principle of Least Privilege**:
- Grant only SQS read permissions
- Grant only S3 GetObject on specific prefix
- Use resource-based policies
- Audit permissions quarterly

**Monitor the Monitors**:
```yaml
# Detect adapter disconnection
target: deployment
event: sensor_disconnected
op: or
rules:
  - op: is platform
    name: aws
  - op: is platform
    name: guard_duty

# Response
- action: report
  name: AWS Adapter Disconnected
  metadata:
    severity: high
```

### Rule Tuning

**Start Simple, Add Complexity**:
```yaml
# Phase 1: Detect all IAM changes
event: AwsApiCall
op: contains
path: event/eventName
value: Policy

# Phase 2: Exclude known automation
event: AwsApiCall
op: and
rules:
  - op: contains
    path: event/eventName
    value: Policy
  - op: not in
    path: event/userIdentity/principalId
    values:
      - AIDAI123TERRAFORM
      - AIDAI456CLOUDFORMATION

# Phase 3: Add time-based context
event: AwsApiCall
op: and
rules:
  - op: contains
    path: event/eventName
    value: Policy
  - op: not in
    path: event/userIdentity/principalId
    values:
      - AIDAI123TERRAFORM
  - op: not in time window
    days:
      - monday
      - wednesday
    start: 18:00
    end: 20:00
    timezone: America/New_York
```

**Use Suppression Appropriately**:
```yaml
# Response
- action: report
  name: S3 Object Access
  suppression:
    is_global: false
    keys:
      - "{{ .event.requestParameters.bucketName }}"
      - "{{ .event.userIdentity.principalId }}"
    max_count: 1
    period: 3600
```

### Multi-Account Strategies

**Centralized Logging**:
1. Create dedicated security account
2. Configure CloudTrail organization trail
3. All accounts log to central S3 bucket
4. Deploy single adapter set in security account

**Per-Account Adapters**:
1. Deploy adapter in each account
2. Use account-specific sensor seed keys
3. Tag sensors with account ID
4. Aggregate in LimaCharlie

**Hybrid Approach**:
1. Organization trail for audit logs
2. Per-account adapters for high-value accounts
3. GuardDuty delegated administrator
4. Centralized detection rules

## AWS Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#aws) for AWS-specific troubleshooting guidance.

## Additional Resources

- [AWS CloudTrail Documentation](https://docs.aws.amazon.com/cloudtrail/)
- [AWS GuardDuty Documentation](https://docs.aws.amazon.com/guardduty/)
- [LimaCharlie AWS Adapter Documentation](/docs/adapter-types-aws-cloudtrail)
- [Soteria AWS Rules Documentation](/docs/soteria-aws-rules)
