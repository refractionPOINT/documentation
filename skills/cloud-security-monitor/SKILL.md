---
name: cloud-security-monitor
description: Activate when users need help setting up cloud security monitoring for AWS, Azure, or GCP, including adapter configuration, detection rules, and threat response.
---

# LimaCharlie Cloud Security Monitor

You are an expert at implementing comprehensive cloud security monitoring using LimaCharlie for AWS, Azure, and GCP environments.

## Overview

LimaCharlie provides unified cloud security monitoring across multi-cloud environments, solving common challenges:

- **Visibility challenges**: Unified view across AWS, Azure, and GCP
- **Data volume challenges**: Efficient storage with 1 year of searchable retention included
- **Multi-cloud challenges**: Single platform for all cloud providers
- **Cost challenges**: Often cheaper than native cloud logging solutions

## Architecture

Cloud security monitoring in LimaCharlie consists of:

1. **Adapters**: Ingest cloud audit logs and security events
2. **Detection Rules**: Identify threats and misconfigurations
3. **Response Actions**: Automated remediation and alerting
4. **Managed Rulesets**: Pre-built detection logic (Soteria Rules)

---

# AWS Security Monitoring

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

### 2. AWS GuardDuty

GuardDuty provides intelligent threat detection with pre-analyzed security findings.

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

## AWS Detection Rules

### Detect Root Account Usage

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

### Detect IAM Policy Changes

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

### Detect S3 Bucket Exposure

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

### Detect EC2 Instance Launched from Unusual Region

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

### Detect Security Group Modifications

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

### Detect Console Login Without MFA

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

## Soteria AWS Rules

LimaCharlie offers managed detection rules from Soteria specifically for AWS environments.

**Setup**:
1. Subscribe to the `soteria-rules-aws` extension in the Add-On Marketplace
2. Subscribe to the `tor` lookup (free)
3. Configure AWS CloudTrail and GuardDuty adapters

**Coverage**:
- AWS CloudTrail event analysis
- AWS GuardDuty finding correlation
- IAM abuse patterns
- Data exfiltration detection
- Resource misconfiguration alerts

---

# Azure Security Monitoring

## Azure Data Sources

### 1. Azure Event Hub

Azure Event Hub is the primary method for ingesting Azure logs, supporting multiple data types.

**Supported Platforms**:
- `azure_monitor`: Azure Monitor logs
- `azure_ad`: Entra ID (formerly Azure AD) logs
- `msdefender`: Microsoft Defender events

#### Event Hub Configuration

**CLI Command**:
```bash
./lc_adapter azure_event_hub \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=azure_monitor \
  client_options.sensor_seed_key=<SENSOR_SEED_KEY> \
  client_options.hostname=<HOSTNAME> \
  "connection_string=Endpoint=sb://mynamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=<KEY>=;EntityPath=lc-stream"
```

**IaC Configuration**:
```yaml
sensor_type: "azure_event_hub"
azure_event_hub:
  connection_string: "Endpoint=sb://your-eventhub-namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=<KEY>;EntityPath=your-event-hub-name"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_FOR_AZURE"
    hostname: "azure-eventhub-adapter"
    platform: "azure_monitor"
    sensor_seed_key: "azure-eventhub-prod-sensor"
```

### 2. Microsoft Entra ID (Azure AD)

Monitor identity and access management events, including risky sign-ins and user activity.

**Platform**: `azure_ad`

**Setup Options**:
1. **Azure Event Hub**: Configure Event Hub connection (recommended)
2. **Entra ID API**: Direct API integration
3. **Webhooks**: Push-based event delivery

#### Entra ID API Setup

1. Create App Registration in Azure Portal
2. Required API Permissions:
   - IdentityRiskEvent.Read.All
   - IdentityRiskEvent.ReadWrite.All
   - IdentityRiskyServicePrincipal.Read
   - IdentityRiskyServicePrincipal.ReadWrite.All
   - IdentityRiskyUser.Read.All
   - IdentityRiskyUser.ReadWrite.All
   - User.Read

3. Create Client Secret
4. Configure in LimaCharlie with:
   - Tenant ID
   - Client ID
   - Client Secret

### 3. Microsoft 365

Monitor Office 365 audit events across the Microsoft 365 ecosystem.

**Platform**: `office365`

**Content Types**:
- `Audit.AzureActiveDirectory`: Azure AD events
- `Audit.Exchange`: Exchange/email events
- `Audit.SharePoint`: SharePoint activity
- `Audit.General`: General M365 events
- `DLP.All`: Data Loss Prevention events

#### M365 Configuration

**IaC Configuration**:
```yaml
sensor_type: "office365"
office365:
  tenant_id: "hive://secret/azure-o365-tenant-id"
  client_id: "hive://secret/azure-o365-client-id"
  client_secret: "hive://secret/azure-o365-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_O365"
    hostname: "ms-o365-adapter"
    platform: "json"
    sensor_seed_key: "office365-audit-sensor"
    mapping:
      sensor_hostname_path: "ClientIP"
      event_type_path: "Operation"
      event_time_path: "CreationTime"
  content_types:
    - "Audit.AzureActiveDirectory"
    - "Audit.Exchange"
    - "Audit.SharePoint"
    - "Audit.General"
    - "DLP.All"
```

### 4. Azure Monitor Logs

Collect logs and performance data from Azure resources.

**Platform**: `azure_monitor`

**Ingestion Methods**:
- Azure Event Hub
- LimaCharlie Webhooks

### 5. Azure Key Vault

Monitor access to cryptographic keys and secrets.

**Ingestion Methods**:
- Azure Event Hub
- LimaCharlie Webhooks

**Event Type**: Based on log `category` field

## Azure Detection Rules

### Detect Entra ID Risky Sign-In

```yaml
# Detection
target: artifact
op: and
rules:
  - op: is platform
    name: azure_ad
  - op: contains
    path: /riskLevel
    value: high

# Response
- action: report
  name: High-Risk Entra ID Sign-In Detected
  metadata:
    user: "{{ .artifact.userPrincipalName }}"
    risk: "{{ .artifact.riskLevel }}"
```

### Detect Azure Resource Deletion

```yaml
# Detection
event: AzureActivity
op: and
rules:
  - op: contains
    path: event/operationName
    value: Delete
  - op: is
    path: event/status/value
    value: Success

# Response
- action: report
  name: Azure Resource Deleted
  metadata:
    resource: "{{ .event.resourceId }}"
    user: "{{ .event.caller }}"
```

### Detect Key Vault Access from Unusual Location

```yaml
# Detection
event: AuditEvent
op: and
rules:
  - op: is platform
    name: azure_monitor
  - op: contains
    path: event/resourceId
    value: KEYVAULT
  - op: is public address
    path: event/callerIpAddress

# Response
- action: report
  name: Azure Key Vault Access from External IP
  metadata:
    ip: "{{ .event.callerIpAddress }}"
    operation: "{{ .event.operationName }}"
```

### Detect M365 File Access by Anonymous User

```yaml
# Detection
event: FileAccessed
op: contains
path: event/UserId
value: anon

# Response
- action: report
  name: OneDrive File Accessed by Anonymous User
  metadata:
    file: "{{ .event.ObjectId }}"
    user: "{{ .event.UserId }}"
```

### Detect Admin Role Assignment in Azure AD

```yaml
# Detection
event: AzureActiveDirectory
op: and
rules:
  - op: or
    rules:
      - op: contains
        path: event/Operation
        value: Add member to role
      - op: contains
        path: event/Operation
        value: Add eligible member to role
  - op: contains
    path: event/ModifiedProperties
    value: Admin

# Response
- action: report
  name: Azure AD Admin Role Assigned
  metadata:
    target: "{{ .event.TargetUserOrGroupName }}"
    role: "{{ .event.ModifiedProperties }}"
```

## Soteria M365 Rules

Managed detection rules for Microsoft 365 environments.

**Setup**:
1. Subscribe to the `soteria-rules-o365` extension
2. Subscribe to the `tor` lookup (free)
3. Configure Office 365 Adapter

**Coverage**:
- Teams activity monitoring
- Email/Exchange threats
- SharePoint data access
- OneDrive file operations
- DLP policy violations

---

# GCP Security Monitoring

## GCP Data Sources

### 1. Google Cloud Pub/Sub

Primary method for ingesting GCP Cloud Logging data.

**Platform**: `gcp`

#### Pub/Sub Configuration

**CLI Command**:
```bash
./lc_adapter pubsub \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=gcp \
  sub_name=<SUBSCRIPTION_NAME> \
  project_name=<GCP_PROJECT> \
  client_options.sensor_seed_key=gcplogs
```

**IaC Configuration**:
```yaml
sensor_type: "pubsub"
pubsub:
  sub_name: "your-pubsub-subscription-name"
  project_name: "your-gcp-project-id"
  service_account_creds: "hive://secret/gcp-pubsub-service-account"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_PUBSUB"
    platform: "gcp"
    sensor_seed_key: "gcp-pubsub-sensor"
    mapping:
      sensor_hostname_path: "attributes.hostname"
      event_type_path: "attributes.eventType"
      event_time_path: "publishTime"
```

## Setting Up GCP Log Ingestion

### Step 1: Create a Log Sink

1. Navigate to **Logging > Logs Router** in GCP Console
2. Click **Create Sink**
3. Select **Cloud Pub/Sub Topic** as sink service
4. Create new topic or select existing one
5. Define log filter (example):

```
logName:cloudaudit.googleapis.com
protoPayload.serviceName!="k8s.io"
protoPayload.serviceName!="compute.googleapis.com"
```

### Step 2: Create Subscription

1. Navigate to **Pub/Sub > Topics**
2. Select your topic
3. Click **Create Subscription**
4. Name the subscription (needed for adapter config)

### Step 3: Create Service Account

1. Navigate to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Assign **Pub/Sub Subscriber** role
4. Create JSON key for authentication

### Step 4: Deploy Adapter

**Option A: Using Default Credentials (on GCP)**
```bash
curl -L https://downloads.limacharlie.io/adapter/linux/64 -o lc_adapter
chmod +x lc_adapter

./lc_adapter pubsub \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=gcp \
  sub_name=<SUBSCRIPTION_NAME> \
  project_name=<PROJECT_NAME> \
  client_options.sensor_seed_key=gcplogs
```

**Option B: Using Service Account Credentials**
```bash
./lc_adapter pubsub \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=gcp \
  sub_name=<SUBSCRIPTION_NAME> \
  project_name=<PROJECT_NAME> \
  service_account_creds='<JSON_CREDENTIALS>' \
  client_options.sensor_seed_key=gcplogs
```

## GCP Detection Rules

### Detect IAM Policy Changes

```yaml
# Detection
event: google.iam.admin.v1.SetIamPolicy
op: exists
path: event/protoPayload/methodName

# Response
- action: report
  name: GCP IAM Policy Modified
  metadata:
    resource: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect GCS Bucket Permission Changes

```yaml
# Detection
event: storage.setIamPermissions
op: and
rules:
  - op: is
    path: event/protoPayload/serviceName
    value: storage.googleapis.com
  - op: contains
    path: event/protoPayload/methodName
    value: setIamPermissions

# Response
- action: report
  name: GCS Bucket Permissions Changed
  metadata:
    bucket: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect Compute Instance Created

```yaml
# Detection
event: v1.compute.instances.insert
op: is
path: event/protoPayload/methodName
value: v1.compute.instances.insert

# Response
- action: report
  name: GCP Compute Instance Created
  metadata:
    instance: "{{ .event.protoPayload.resourceName }}"
    zone: "{{ .event.resource.labels.zone }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect Firewall Rule Changes

```yaml
# Detection
op: or
rules:
  - event: v1.compute.firewalls.insert
    op: exists
    path: event/protoPayload
  - event: v1.compute.firewalls.delete
    op: exists
    path: event/protoPayload
  - event: v1.compute.firewalls.patch
    op: exists
    path: event/protoPayload

# Response
- action: report
  name: GCP Firewall Rule Modified
  metadata:
    rule: "{{ .event.protoPayload.resourceName }}"
    action: "{{ .event.protoPayload.methodName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect Service Account Key Creation

```yaml
# Detection
event: google.iam.admin.v1.CreateServiceAccountKey
op: is
path: event/protoPayload/methodName
value: google.iam.admin.v1.CreateServiceAccountKey

# Response
- action: report
  name: GCP Service Account Key Created
  metadata:
    account: "{{ .event.protoPayload.request.name }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

---

# Common Cloud Threats

## 1. IAM Abuse and Privilege Escalation

**Indicators**:
- Root/admin account usage
- Role/policy modifications
- Service account key creation
- Privilege elevation attempts

**Detection Strategy**:
- Monitor all IAM policy changes
- Alert on root account activity
- Track role assignments
- Baseline normal user behavior

## 2. Data Exfiltration

**Indicators**:
- Large data transfers
- Unusual database exports
- Bucket/blob public exposure
- External sharing permissions

**Detection Strategy**:
- Monitor storage permission changes
- Track data access patterns
- Alert on public access configurations
- Monitor egress traffic patterns

## 3. Resource Misconfigurations

**Indicators**:
- Public storage buckets
- Overly permissive security groups
- Disabled logging/monitoring
- Weak encryption settings

**Detection Strategy**:
- Alert on public access changes
- Monitor security group modifications
- Track audit log configuration
- Validate encryption status

## 4. Unauthorized Access

**Indicators**:
- Login from unusual locations
- Failed authentication attempts
- Access without MFA
- Impossible travel scenarios

**Detection Strategy**:
- Monitor authentication events
- Track geographic anomalies
- Enforce MFA requirements
- Correlate with threat intelligence

## 5. Cryptojacking and Resource Abuse

**Indicators**:
- Unexpected instance launches
- Unusual regions/instance types
- Sudden cost increases
- High CPU/GPU usage

**Detection Strategy**:
- Monitor instance creation
- Alert on unusual regions
- Track resource quotas
- Correlate with cost data

## 6. Lateral Movement

**Indicators**:
- Cross-account access
- Assume role operations
- Service account impersonation
- Resource access patterns

**Detection Strategy**:
- Monitor cross-account activity
- Track role assumption
- Correlate access patterns
- Map resource relationships

---

# Integration Strategies

## Combining Cloud and Endpoint Telemetry

### Correlate Cloud Identity with Endpoint Activity

```yaml
# Detection
event: AwsApiCall
op: and
rules:
  - op: is
    path: event/eventName
    value: ConsoleLogin
  - op: exists
    path: event/sourceIPAddress

# Response
- action: report
  name: AWS Console Login
- action: add tag
  tag: aws_user_{{ .event.userIdentity.principalId }}
  ttl: 3600
```

Then correlate with endpoint sensor:
```yaml
# Detection
event: NEW_PROCESS
op: and
rules:
  - op: is tagged
    tag: aws_user_*
  - op: contains
    path: event/COMMAND_LINE
    value: aws

# Response
- action: report
  name: AWS CLI Usage by Console User
```

## Multi-Cloud Detection

Create platform-agnostic rules:

```yaml
# Detection
op: or
rules:
  - event: AwsApiCall
    op: contains
    path: event/eventName
    value: DeleteBucket
  - event: storage.buckets.delete
    op: exists
    path: event/protoPayload
  - event: Microsoft.Storage/storageAccounts/delete
    op: exists
    path: event/operationName

# Response
- action: report
  name: Cloud Storage Deletion Detected
  metadata:
    platform: "{{ .routing.platform }}"
```

## Cloud-to-SIEM Integration

Forward cloud detections to SIEM/SOAR:

1. Configure Output (Syslog, Webhook, S3, etc.)
2. Filter for cloud platforms
3. Enrich with context
4. Route to downstream systems

---

# Best Practices

## What to Monitor

### Critical AWS Events
- Root account usage
- IAM policy changes
- Security group modifications
- S3 bucket permission changes
- EC2 instance launches
- Console logins without MFA
- CloudTrail configuration changes
- KMS key usage

### Critical Azure Events
- Entra ID risky sign-ins
- Admin role assignments
- Resource deletions
- Key Vault access
- Network security group changes
- Subscription-level changes
- Conditional access policy modifications

### Critical GCP Events
- IAM policy modifications
- Service account key creation
- Firewall rule changes
- GCS bucket permission changes
- Compute instance creation
- Project-level changes
- VPC network modifications

## Rule Tuning

### Start with High-Confidence Detections
- Root/admin account usage
- Resource deletions
- IAM policy changes
- Public exposure events

### Add Context to Reduce False Positives
```yaml
# Bad: Too noisy
event: AwsApiCall
op: exists
path: event/eventName

# Good: Specific and contextual
event: AwsApiCall
op: and
rules:
  - op: is
    path: event/eventName
    value: DeleteBucket
  - op: not in
    path: event/userIdentity/principalId
    values:
      - AIDAI123AUTOMATED
      - AIDAI456TERRAFORM
```

### Use Suppression for High-Volume Events
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

### Baseline Normal Activity
- Identify trusted service accounts
- Map expected regions
- Document scheduled automation
- Track business hours patterns

## Cost Management

### Control Data Volume

**Filter at the Source**:
```
# GCP Log Sink Filter
logName:cloudaudit.googleapis.com
protoPayload.serviceName!="k8s.io"
-protoPayload.methodName:"storage.objects.get"
```

**Use Selective Monitoring**:
- Start with CloudTrail management events (not data events)
- Monitor critical resource types first
- Exclude read-only operations initially
- Add granularity as needed

### Optimize Adapter Configuration

**Use Cloud-to-Cloud When Possible**:
- No infrastructure to maintain
- Automatic scaling
- Built-in retry logic

**Batch Events**:
- Use SQS instead of S3 for lower latency
- Configure appropriate buffer sizes

### Monitor Ingestion Costs
- Track events per day per adapter
- Review storage utilization
- Audit detection rule efficiency
- Remove unused adapters

## Security Hygiene

### Protect Credentials
```yaml
# Use Hive Secrets Manager
tenant_id: "hive://secret/azure-tenant-id"
client_secret: "hive://secret/azure-client-secret"
access_key: "hive://secret/aws-access-key"
```

### Principle of Least Privilege
- AWS: Read-only S3/SQS access only
- Azure: Event Hub Listen permission only
- GCP: Pub/Sub Subscriber role only

### Monitor the Monitors
```yaml
# Detect adapter disconnection
target: deployment
event: sensor_disconnected
op: or
rules:
  - op: is platform
    name: aws
  - op: is platform
    name: gcp
  - op: is platform
    name: azure_ad

# Response
- action: report
  name: Cloud Adapter Disconnected
```

### Regular Audits
- Review active adapters monthly
- Validate detection rule effectiveness
- Test response actions quarterly
- Update managed rulesets

---

# Complete Monitoring Setups

## AWS Complete Setup

### 1. Deploy CloudTrail Adapter
```bash
./lc_adapter sqs \
  client_options.identity.installation_key=<KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=aws \
  client_options.hostname=aws-cloudtrail \
  client_options.sensor_seed_key=aws-ct-prod \
  region=us-east-1 \
  access_key=<ACCESS> \
  secret_key=<SECRET> \
  queue_url=<QUEUE>
```

### 2. Deploy GuardDuty Adapter
```bash
./lc_adapter sqs \
  client_options.identity.installation_key=<KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=guard_duty \
  client_options.hostname=aws-guardduty \
  client_options.sensor_seed_key=aws-gd-prod \
  region=us-east-1 \
  access_key=<ACCESS> \
  secret_key=<SECRET> \
  queue_url=<QUEUE>
```

### 3. Subscribe to Soteria AWS Rules
- Navigate to Add-Ons > Extensions
- Subscribe to `soteria-rules-aws`
- Subscribe to `tor` lookup

### 4. Add Custom Detection Rules
Deploy the AWS detection rules provided in this guide, prioritizing:
1. Root account monitoring
2. IAM policy changes
3. Security group modifications
4. S3 public access
5. Console login without MFA

### 5. Configure Outputs
Set up outputs to your SIEM, Slack, or incident response platform.

## Azure Complete Setup

### 1. Create Event Hub
1. Create Event Hub namespace
2. Create Event Hub for each data source:
   - `azure-monitor-hub`
   - `entra-id-hub`
   - `m365-hub`

### 2. Configure Diagnostic Settings
Route Azure logs to Event Hubs:
- Azure Activity Logs → Event Hub
- Entra ID Sign-ins → Event Hub
- Resource Diagnostic Logs → Event Hub

### 3. Deploy Event Hub Adapters

**Azure Monitor**:
```bash
./lc_adapter azure_event_hub \
  client_options.identity.installation_key=<KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=azure_monitor \
  client_options.hostname=azure-monitor \
  client_options.sensor_seed_key=azure-mon-prod \
  "connection_string=<CONNECTION_STRING>"
```

**Entra ID**:
```bash
./lc_adapter azure_event_hub \
  client_options.identity.installation_key=<KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=azure_ad \
  client_options.hostname=entra-id \
  client_options.sensor_seed_key=entra-prod \
  "connection_string=<CONNECTION_STRING>"
```

### 4. Configure M365 Adapter
Use LimaCharlie web UI to configure Office 365 adapter with App Registration credentials.

### 5. Subscribe to Soteria M365 Rules
- Navigate to Add-Ons > Extensions
- Subscribe to `soteria-rules-o365`
- Subscribe to `tor` lookup

### 6. Deploy Detection Rules
Implement Azure-specific rules focusing on:
1. Entra ID risky sign-ins
2. Admin role assignments
3. Resource deletions
4. Key Vault access
5. M365 anonymous access

## GCP Complete Setup

### 1. Configure Log Export

**Create Log Sink**:
1. Logging > Logs Router > Create Sink
2. Select Cloud Pub/Sub Topic
3. Configure filter:
```
logName:cloudaudit.googleapis.com
protoPayload.serviceName!="k8s.io"
```

### 2. Create Pub/Sub Resources
1. Create Topic: `limacharlie-logs`
2. Create Subscription: `limacharlie-logs-sub`
3. Create Service Account with Pub/Sub Subscriber role

### 3. Deploy Adapter on GCE Instance
```bash
# SSH to GCE instance
curl -L https://downloads.limacharlie.io/adapter/linux/64 -o lc_adapter
chmod +x lc_adapter

# Run adapter (use default GCE credentials)
./lc_adapter pubsub \
  client_options.identity.installation_key=<KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=gcp \
  sub_name=limacharlie-logs-sub \
  project_name=<PROJECT> \
  client_options.sensor_seed_key=gcp-logs-prod
```

### 4. Deploy Detection Rules
Implement GCP-specific rules focusing on:
1. IAM policy changes
2. Service account key creation
3. Firewall modifications
4. GCS bucket permissions
5. Compute instance creation

### 5. Create Monitoring Rule
```yaml
# Ensure adapter stays running
target: deployment
event: sensor_disconnected
op: is platform
name: gcp

# Response
- action: report
  name: GCP Log Adapter Disconnected
```

## Multi-Cloud Complete Setup

For organizations using multiple cloud providers:

### 1. Deploy All Cloud Adapters
- AWS: CloudTrail + GuardDuty
- Azure: Event Hub (Monitor + Entra ID) + M365
- GCP: Pub/Sub

### 2. Standardize Naming
Use consistent naming for easier management:
- `aws-cloudtrail-prod`
- `aws-guardduty-prod`
- `azure-monitor-prod`
- `azure-entraid-prod`
- `gcp-logs-prod`

### 3. Create Unified Detection Rules
Use platform-agnostic rules where possible:

```yaml
# Detect admin activity across all clouds
op: or
rules:
  - event: AwsApiCall
    op: is
    path: event/userIdentity/type
    value: Root
  - event: AzureActiveDirectory
    op: contains
    path: event/Operation
    value: Admin
  - event: google.iam.admin.v1.SetIamPolicy
    op: exists
    path: event/protoPayload

# Response
- action: report
  name: Cloud Admin Activity - {{ .routing.platform }}
```

### 4. Centralized Alerting
Configure outputs to send all cloud detections to a single destination:
- SIEM integration
- Slack/Teams notifications
- Incident response platform
- Security orchestration tool

### 5. Dashboard and Reporting
Use LimaCharlie's timeline and search features, or export to:
- Google BigQuery for analytics
- Grafana for visualization
- Custom dashboards via API

---

# Troubleshooting

## Adapter Not Connecting

**Check**:
1. Credentials are correct
2. Network connectivity to cloud API
3. Installation key is valid
4. OID matches your organization

**View Logs**:
- Platform Logs in LimaCharlie web UI
- Adapter stdout/stderr if running CLI

## No Events Flowing

**Check**:
1. Adapter is connected (check Sensor List)
2. Cloud logging is configured (CloudTrail enabled, Event Hub configured, etc.)
3. Events are being generated (test with known action)
4. Filters aren't too restrictive

**Test**:
- Perform a known action in cloud console
- Check adapter logs for errors
- Verify cloud-side logging configuration

## High False Positive Rate

**Solutions**:
1. Add context to rules (user, region, time)
2. Use suppression for high-volume events
3. Baseline normal activity
4. Exclude known service accounts
5. Add "not" conditions for expected behavior

## Performance Issues

**Check**:
1. Event volume (reduce at source if too high)
2. Rule complexity (simplify complex rules)
3. Number of active rules
4. Adapter resource allocation

**Optimize**:
- Use more specific event filters
- Deploy multiple adapters for high volume
- Use suppression appropriately
- Archive old sensors

## Cost Concerns

**Reduce Costs**:
1. Filter logs at source (before ingestion)
2. Exclude read-only operations
3. Sample high-volume events
4. Use managed rulesets instead of custom rules
5. Archive and remove inactive sensors

---

# Quick Reference

## Platform Names
- `aws`: AWS CloudTrail
- `guard_duty`: AWS GuardDuty
- `azure_monitor`: Azure Monitor
- `azure_ad`: Entra ID / Azure AD
- `msdefender`: Microsoft Defender
- `office365`: Microsoft 365
- `gcp`: Google Cloud Platform

## Common Event Names

**AWS**:
- `AwsApiCall`: CloudTrail API calls
- `ConsoleLogin`: AWS Console authentication

**Azure**:
- `AzureActivity`: Azure resource operations
- `SignInLogs`: Entra ID authentication
- `FileAccessed`: M365 file operations

**GCP**:
- `v1.compute.instances.insert`: Instance creation
- `google.iam.admin.v1.SetIamPolicy`: IAM changes
- `storage.setIamPermissions`: Storage permissions

## Key Operators
- `is platform`: Match by platform type
- `exists`: Check for field presence
- `contains`: Substring match
- `is public address`: Check if IP is external
- `is tagged`: Check for sensor tag
- `or` / `and`: Boolean logic

## Response Actions
- `report`: Generate detection
- `task`: Execute sensor command
- `add tag`: Tag sensor
- `re-enroll`: Re-enroll cloned sensor

---

# Additional Resources

## Documentation Links
- AWS CloudTrail Adapter: `/docs/adapter-types-aws-cloudtrail`
- AWS GuardDuty Adapter: `/docs/adapter-types-aws-guardduty`
- Azure Event Hub Adapter: `/docs/adapter-types-azure-event-hub`
- Microsoft Entra ID Adapter: `/docs/adapter-types-microsoft-entra-id`
- Microsoft 365 Adapter: `/docs/adapter-types-microsoft-365`
- Google Cloud Pub/Sub Adapter: `/docs/adapter-types-google-cloud-pubsub`
- Soteria AWS Rules: `/docs/soteria-aws-rules`
- Soteria M365 Rules: `/docs/soteria-m365-rules`

## Community Resources
- LimaCharlie Discord: Community support
- GitHub Examples: Sample configurations
- Sigma Rules: Translate existing detections
- SOC Prime Uncoder: Convert detection formats

---

# Your Role

When helping users with cloud security monitoring:

1. **Understand Their Environment**
   - Which cloud providers do they use?
   - What's their security maturity level?
   - What specific threats concern them?
   - What's their existing security stack?

2. **Recommend Appropriate Solutions**
   - Start with managed rulesets (Soteria)
   - Add custom rules for specific needs
   - Consider their data volume and costs
   - Balance detection coverage with alert fatigue

3. **Provide Complete Configurations**
   - Include all required parameters
   - Use hive secrets for credentials
   - Show both CLI and IaC options
   - Explain each configuration choice

4. **Guide on Best Practices**
   - Start with high-confidence detections
   - Baseline before alerting
   - Use suppression appropriately
   - Monitor the monitors

5. **Help Troubleshoot Issues**
   - Check adapter connectivity
   - Verify cloud-side configuration
   - Review event flow
   - Analyze false positives

Always provide clear, actionable guidance with complete examples that users can implement immediately.
