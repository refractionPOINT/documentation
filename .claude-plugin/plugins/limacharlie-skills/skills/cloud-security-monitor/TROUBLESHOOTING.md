# Cloud Security Monitor Troubleshooting

Comprehensive troubleshooting guide for cloud security monitoring issues across AWS, Azure, and GCP.

## Table of Contents

- [Common Issues](#common-issues)
- [AWS Troubleshooting](#aws-troubleshooting)
- [Azure Troubleshooting](#azure-troubleshooting)
- [GCP Troubleshooting](#gcp-troubleshooting)
- [Detection Rule Issues](#detection-rule-issues)
- [Performance Issues](#performance-issues)

---

## Common Issues

### Adapter Not Connecting

**Symptoms**:
- Adapter doesn't appear in Sensor List
- Adapter shows as offline
- No initial connection established

**Diagnostic Steps**:
1. Verify credentials are correct
2. Check network connectivity to cloud API
3. Validate installation key and OID
4. Review adapter logs for errors

**Solutions**:

**Check Credentials**:
```bash
# Test AWS credentials
aws sts get-caller-identity --profile your-profile

# Test Azure connection
az account show

# Test GCP credentials
gcloud auth list
```

**Verify Installation Key**:
```bash
# Installation key should be valid UUID
# OID should match your LimaCharlie organization
# Check in LimaCharlie web UI: Installation Keys section
```

**Check Network Connectivity**:
```bash
# AWS
curl https://sqs.us-east-1.amazonaws.com

# Azure
curl https://login.microsoftonline.com

# GCP
curl https://pubsub.googleapis.com
```

**Review Adapter Logs**:
```bash
# If running via CLI
./lc_adapter [type] [options] 2>&1 | tee adapter.log

# If running as systemd service
sudo journalctl -u lc-adapter-service -f
```

### No Events Flowing

**Symptoms**:
- Adapter connected but no events in Timeline
- Last event time not updating
- Zero event count

**Diagnostic Steps**:
1. Verify adapter is connected
2. Confirm cloud-side logging is enabled
3. Generate test event
4. Check for filter restrictions
5. Review adapter event consumption

**Solutions**:

**Verify Adapter Connection**:
1. Navigate to Sensors in LimaCharlie
2. Check adapter status (should be green/online)
3. Verify last event time
4. Check event count

**Confirm Cloud Logging**:
- **AWS**: CloudTrail enabled and logging to S3/SQS
- **Azure**: Diagnostic settings configured, Event Hub receiving
- **GCP**: Log sink created, Pub/Sub topic has messages

**Generate Test Event**:
```bash
# AWS - Create and delete security group
aws ec2 create-security-group --group-name test-lc --description "LimaCharlie Test"
aws ec2 delete-security-group --group-name test-lc

# Azure - Create and delete resource group
az group create --name lc-test --location eastus
az group delete --name lc-test --yes

# GCP - Create and delete firewall rule
gcloud compute firewall-rules create lc-test --allow tcp:80
gcloud compute firewall-rules delete lc-test --quiet
```

**Check Filters**:
- Review log sink filters (GCP)
- Check diagnostic setting categories (Azure)
- Verify CloudTrail event selectors (AWS)

### High False Positive Rate

**Symptoms**:
- Excessive alerts for normal activity
- Alert fatigue
- Difficulty identifying real threats

**Solutions**:

**Add Contextual Filters**:
```yaml
# Bad: Too broad
event: AwsApiCall
op: exists
path: event/eventName

# Good: Specific with context
event: AwsApiCall
op: and
rules:
  - op: is
    path: event/eventName
    value: DeleteBucket
  - op: not in
    path: event/userIdentity/principalId
    values:
      - AIDAI123TERRAFORM
      - AIDAI456AUTOMATION
```

**Use Suppression**:
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

**Baseline Normal Activity**:
1. Document expected automation (Terraform, CI/CD)
2. Identify service accounts and their typical actions
3. Map business hours and maintenance windows
4. Track seasonal patterns

**Add Temporal Context**:
```yaml
# Alert only outside business hours
op: not in time window
days:
  - monday
  - tuesday
  - wednesday
  - thursday
  - friday
start: 08:00
end: 18:00
timezone: America/New_York
```

### Missing Events

**Symptoms**:
- Some expected events not appearing
- Gaps in timeline
- Inconsistent event delivery

**Diagnostic Steps**:
1. Check cloud-side event generation
2. Review filtering configuration
3. Verify subscription/queue health
4. Check adapter consumption rate

**Solutions**:

**Verify Events Generated in Cloud**:
- **AWS**: Check CloudTrail event history in console
- **Azure**: Review Activity Log in portal
- **GCP**: Use Logs Explorer to view audit logs

**Review Filtering**:
- Ensure filters aren't too restrictive
- Check for exclusion rules
- Verify event types are selected

**Check Queue/Subscription Health**:
```bash
# AWS SQS - Check queue depth
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/ACCOUNT/QUEUE \
  --attribute-names ApproximateNumberOfMessages

# Azure Event Hub - Check metrics in portal
# Navigate to Event Hub > Metrics > Incoming/Outgoing Messages

# GCP Pub/Sub - Check subscription backlog
gcloud pubsub subscriptions describe SUBSCRIPTION_NAME \
  --format="value(numUndeliveredMessages)"
```

---

## AWS Troubleshooting

### CloudTrail Adapter Issues

**Problem: Adapter connects but no events**

**Causes and Solutions**:

1. **CloudTrail not enabled**:
   ```bash
   # Check if CloudTrail is logging
   aws cloudtrail get-trail-status --name your-trail-name
   # Look for "IsLogging": true
   ```

2. **S3 bucket notifications not configured**:
   - Navigate to S3 bucket > Properties > Event notifications
   - Verify notification to SNS topic exists
   - Check filter prefix matches CloudTrail path (usually `AWSLogs/`)

3. **SQS queue not subscribed to SNS**:
   ```bash
   # List SNS subscriptions
   aws sns list-subscriptions-by-topic --topic-arn YOUR_SNS_ARN
   # Ensure your SQS queue is listed
   ```

4. **IAM permissions insufficient**:
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
         "Resource": "arn:aws:sqs:*:*:your-queue"
       },
       {
         "Effect": "Allow",
         "Action": ["s3:GetObject"],
         "Resource": "arn:aws:s3:::cloudtrail-bucket/*"
       }
     ]
   }
   ```

5. **CloudTrail logs delayed**:
   - CloudTrail delivers logs every 5-15 minutes
   - Check S3 bucket for recent log files
   - Verify log files are being created

**Problem: High latency in event delivery**

**Solutions**:
- Use SQS instead of S3 polling
- Reduce SQS polling interval (if custom implementation)
- Check SQS queue for message backlog
- Ensure adapter has sufficient resources

**Problem: Duplicate events**

**Causes**:
- Multiple adapters reading same queue
- SQS visibility timeout too short
- Adapter restarts without proper cleanup

**Solutions**:
- Use unique queue per adapter
- Increase SQS visibility timeout to 60+ seconds
- Implement proper message acknowledgment

### GuardDuty Adapter Issues

**Problem: No GuardDuty findings appearing**

**Causes and Solutions**:

1. **GuardDuty not enabled**:
   ```bash
   # Check GuardDuty status
   aws guardduty list-detectors
   ```

2. **No findings generated**:
   - GuardDuty generates findings based on threat detection
   - No findings = no threats detected (or not enough time elapsed)
   - Generate test finding to verify pipeline

3. **EventBridge rule not configured**:
   - Navigate to EventBridge > Rules
   - Verify rule exists for GuardDuty findings
   - Check rule target (should be SNS or SQS)

4. **Event pattern incorrect**:
   ```json
   {
     "source": ["aws.guardduty"],
     "detail-type": ["GuardDuty Finding"]
   }
   ```

**Generate Test Finding**:
```bash
# Use GuardDuty sample findings feature
aws guardduty create-sample-findings \
  --detector-id YOUR_DETECTOR_ID \
  --finding-types Recon:EC2/PortProbeUnprotectedPort
```

### AWS Authentication Errors

**Problem: "Access Denied" errors**

**Solutions**:
1. Verify IAM user has required permissions
2. Check if MFA is required (not supported by adapter)
3. Ensure credentials are not expired
4. Verify bucket policy allows IAM user access

**Problem: "Invalid security token"**

**Solutions**:
1. Credentials expired - rotate keys
2. Using temporary credentials incorrectly
3. Region mismatch in configuration
4. Check if using correct AWS account

---

## Azure Troubleshooting

### Event Hub Adapter Issues

**Problem: Adapter connects but no events**

**Causes and Solutions**:

1. **Diagnostic settings not configured**:
   - Navigate to resource > Diagnostic settings
   - Verify setting exists
   - Check categories are selected
   - Confirm destination is Event Hub

2. **Event Hub namespace/hub mismatch**:
   - Verify connection string EntityPath matches hub name
   - Check namespace name is correct
   - Ensure hub exists in namespace

3. **Connection string incorrect**:
   ```
   # Format should be:
   Endpoint=sb://NAMESPACE.servicebus.windows.net/;
   SharedAccessKeyName=POLICY_NAME;
   SharedAccessKey=KEY;
   EntityPath=HUB_NAME
   ```

4. **Shared access policy permissions**:
   - Policy needs "Listen" permission
   - Verify policy is on Event Hub (not namespace)
   - Check policy is not expired

5. **Consumer group conflict**:
   - Each adapter needs unique consumer group
   - Default consumer group ($Default) may be in use
   - Create dedicated consumer group for LimaCharlie

**Problem: High latency or missing events**

**Solutions**:
- Check Event Hub metrics for throttling
- Increase throughput units if needed
- Verify adapter is consuming messages
- Check consumer group lag

**Problem: "Unauthorized" or "Forbidden" errors**

**Solutions**:
1. Regenerate shared access key
2. Verify SAS token not expired
3. Check connection string format
4. Ensure policy has Listen permission

### Entra ID Adapter Issues

**Problem: No sign-in logs appearing**

**Causes and Solutions**:

1. **Diagnostic settings not streaming logs**:
   - Navigate to Entra ID > Diagnostic settings
   - Verify SignInLogs category is selected
   - Check destination Event Hub is correct

2. **API permissions not granted**:
   - App Registration needs required permissions
   - Admin consent must be granted
   - Check token has correct scopes

3. **No sign-in activity**:
   - Generate test sign-in
   - Logs may take 5-10 minutes to appear
   - Check Entra ID sign-in logs in portal first

**Problem: API rate limiting**

**Symptoms**:
- HTTP 429 responses
- Gaps in data
- "Too Many Requests" errors

**Solutions**:
- Implement exponential backoff
- Reduce polling frequency
- Use Event Hub streaming instead of API polling
- Check Microsoft Graph API limits

### M365 Adapter Issues

**Problem: No audit events**

**Causes and Solutions**:

1. **Audit logging not enabled**:
   - Navigate to Microsoft 365 Compliance > Audit
   - Verify "Start recording user and admin activity" is on
   - May take 24 hours after enabling

2. **Insufficient license**:
   - M365 audit requires E3/E5 or equivalent
   - Check user license assignments
   - Some events require E5

3. **API permissions missing**:
   ```
   Required:
   - ActivityFeed.Read
   - ActivityFeed.ReadDlp (for DLP events)
   - ServiceHealth.Read
   ```

4. **Content types not selected**:
   - Verify content_types in configuration
   - Start with Audit.General for testing
   - Add specific types as needed

**Problem: DLP events not appearing**

**Solutions**:
- Ensure DLP policies exist and are active
- Verify ActivityFeed.ReadDlp permission granted
- Include "DLP.All" in content_types
- DLP events may take time to generate

---

## GCP Troubleshooting

### Pub/Sub Adapter Issues

**Problem: Adapter connects but no events**

**Causes and Solutions**:

1. **Log sink not created**:
   ```bash
   # List log sinks
   gcloud logging sinks list
   # Verify sink exists and destination is correct
   ```

2. **Pub/Sub topic doesn't exist**:
   ```bash
   # List topics
   gcloud pubsub topics list
   # Create if missing
   gcloud pubsub topics create limacharlie-logs
   ```

3. **Subscription doesn't exist**:
   ```bash
   # List subscriptions
   gcloud pubsub subscriptions list
   # Create if missing
   gcloud pubsub subscriptions create limacharlie-logs-sub \
     --topic=limacharlie-logs
   ```

4. **Log sink writer permissions**:
   - Log sink creates a service account
   - Service account needs Pub/Sub Publisher on topic
   - Grant permission:
     ```bash
     gcloud pubsub topics add-iam-policy-binding limacharlie-logs \
       --member="serviceAccount:SERVICE_ACCOUNT" \
       --role="roles/pubsub.publisher"
     ```

5. **Adapter service account permissions**:
   - Service account needs Pub/Sub Subscriber on subscription
   - Grant permission:
     ```bash
     gcloud pubsub subscriptions add-iam-policy-binding limacharlie-logs-sub \
       --member="serviceAccount:YOUR_SA@PROJECT.iam.gserviceaccount.com" \
       --role="roles/pubsub.subscriber"
     ```

6. **Log filter too restrictive**:
   ```bash
   # View sink details including filter
   gcloud logging sinks describe limacharlie-audit-logs
   # Test filter in Logs Explorer first
   ```

**Problem: Subscription has message backlog**

**Symptoms**:
```bash
# Check backlog
gcloud pubsub subscriptions describe limacharlie-logs-sub \
  --format="value(numUndeliveredMessages)"
# Large number indicates adapter not consuming
```

**Solutions**:
- Verify adapter is running and connected
- Check adapter resource utilization
- Scale adapter horizontally (multiple instances with same subscription)
- Increase ack deadline if needed
- Create multiple subscriptions for load balancing

**Problem: "Permission denied" errors**

**Solutions**:
1. Verify service account has correct permissions
2. Check if using correct project ID
3. Ensure credentials file is valid JSON
4. Test credentials:
   ```bash
   gcloud auth activate-service-account --key-file=creds.json
   gcloud pubsub subscriptions pull limacharlie-logs-sub --limit=1
   ```

### Cloud Audit Log Issues

**Problem: Expected logs not appearing**

**Causes and Solutions**:

1. **Audit logs not enabled for service**:
   - Navigate to IAM & Admin > Audit Logs
   - Check service is selected
   - Verify log types are enabled (Admin, Data Access, etc.)

2. **Data Access logs not enabled**:
   - Data Access logs are OFF by default
   - Must explicitly enable per service
   - Can be expensive - enable selectively

3. **Service exclusion in filter**:
   ```
   # Check log sink filter
   gcloud logging sinks describe SINK_NAME
   # Remove exclusions if too aggressive
   ```

4. **Organization vs project logs**:
   - Verify log sink scope (org-level or project-level)
   - Check if organization sink has --include-children flag
   - Project-level sinks only capture project logs

**Problem: High volume/costs**

**Solutions**:

1. **Refine log sink filter**:
   ```
   # Exclude read operations
   logName:cloudaudit.googleapis.com
   -protoPayload.methodName:"get"
   -protoPayload.methodName:"list"
   ```

2. **Exclude noisy services**:
   ```
   logName:cloudaudit.googleapis.com
   protoPayload.serviceName!="k8s.io"
   protoPayload.serviceName!="compute.googleapis.com"
   ```

3. **Use log exclusions**:
   - Create exclusion filters in Log Router
   - Exclude before ingestion (saves cost)
   - Be careful not to exclude security-relevant logs

4. **Disable Data Access logs for non-critical services**:
   - Keep for: Cloud Storage, BigQuery, Cloud SQL
   - Disable for: Compute Engine, GKE

---

## Detection Rule Issues

### Rules Not Triggering

**Problem: Event appears in Timeline but rule doesn't trigger**

**Diagnostic Steps**:

1. **Verify event structure**:
   - View raw event in Timeline
   - Check if expected fields exist
   - Verify field paths in rule

2. **Test rule syntax**:
   - Use LimaCharlie web UI rule tester
   - Test against actual event JSON
   - Check for typos in field paths

3. **Check platform matching**:
   ```yaml
   # Ensure platform matches
   op: is platform
   name: aws  # Must match adapter platform
   ```

4. **Verify event type**:
   ```yaml
   event: AwsApiCall  # Must match actual event type
   ```

**Common Mistakes**:

```yaml
# Wrong: Case sensitive
path: event/eventname
# Correct:
path: event/eventName

# Wrong: Missing path separator
path: eventawsRegion
# Correct:
path: event/awsRegion

# Wrong: Array without index or proper operator
path: event/requestParameters/ipPermissions
value: 0.0.0.0/0
# Correct:
op: contains
path: event/requestParameters
value: 0.0.0.0/0
```

### Rules Triggering Too Often

**Problem: Rule generates excessive alerts**

**Solutions**:

1. **Add suppression**:
   ```yaml
   suppression:
     is_global: false
     keys:
       - "{{ .event.userIdentity.principalId }}"
     max_count: 1
     period: 3600
   ```

2. **Refine detection logic**:
   ```yaml
   # Add exclusions
   op: and
   rules:
     - op: is
       path: event/eventName
       value: RunInstances
     - op: not in
       path: event/userIdentity/principalId
       values:
         - KNOWN_SERVICE_ACCOUNT_1
         - KNOWN_SERVICE_ACCOUNT_2
   ```

3. **Add temporal constraints**:
   ```yaml
   # Only alert outside business hours
   op: not in time window
   days: [monday, tuesday, wednesday, thursday, friday]
   start: 09:00
   end: 17:00
   timezone: America/New_York
   ```

### Rules Not Matching Expected Events

**Problem: Rule should match but doesn't**

**Debug Process**:

1. **Simplify rule to minimum**:
   ```yaml
   # Start with just event type
   event: AwsApiCall
   op: exists
   path: event
   ```

2. **Add conditions one at a time**:
   ```yaml
   # Add first condition
   event: AwsApiCall
   op: is
   path: event/eventName
   value: RunInstances
   # Test - does this work? If yes, add next condition
   ```

3. **Check field types**:
   ```yaml
   # Wrong: Comparing string to number
   op: is
   path: event/statusCode
   value: "200"

   # Correct:
   op: is
   path: event/statusCode
   value: 200
   ```

4. **Use contains for partial matching**:
   ```yaml
   # Instead of exact match
   op: is
   path: event/operationName
   value: Microsoft.Storage/storageAccounts/delete

   # Use contains
   op: contains
   path: event/operationName
   value: delete
   ```

---

## Performance Issues

### High Adapter Resource Usage

**Symptoms**:
- High CPU or memory usage
- Adapter host becoming unresponsive
- Slow event processing

**Solutions**:

1. **Reduce event volume at source**:
   - Refine log filters
   - Exclude read-only operations
   - Disable verbose logging

2. **Scale horizontally**:
   - Deploy multiple adapter instances
   - Use separate queues/subscriptions
   - Load balance across instances

3. **Optimize adapter host**:
   - Increase instance size
   - Use faster storage
   - Ensure adequate network bandwidth

4. **Batch processing**:
   - Adjust polling intervals
   - Configure batch sizes appropriately

### Event Processing Lag

**Symptoms**:
- Events delayed in appearing in Timeline
- Increasing backlog in queue/subscription
- Old timestamp on events

**Diagnostic Steps**:

1. **Check queue/subscription metrics**:
   - AWS: SQS ApproximateAgeOfOldestMessage
   - Azure: Event Hub consumer lag
   - GCP: Pub/Sub oldest unacked message age

2. **Monitor adapter throughput**:
   - Events per second
   - Processing time per event
   - Network I/O

**Solutions**:

1. **Scale adapter resources**:
   - Increase CPU/memory
   - Deploy multiple instances
   - Use faster network connection

2. **Reduce event volume**:
   - Filter at source
   - Exclude non-critical events
   - Sample high-volume event types

3. **Optimize LimaCharlie organization**:
   - Review detection rule complexity
   - Disable unused rules
   - Optimize output configurations

### Detection Rule Performance

**Symptoms**:
- Slow rule evaluation
- Events delayed in detection
- High LimaCharlie resource usage

**Solutions**:

1. **Simplify complex rules**:
   ```yaml
   # Instead of many OR conditions
   op: or
   rules:
     - op: is
       path: event/eventName
       value: PutUserPolicy
     - op: is
       path: event/eventName
       value: PutRolePolicy
     # ... 20 more ...

   # Use contains or regex
   op: contains
   path: event/eventName
   value: Policy
   ```

2. **Use specific event types**:
   ```yaml
   # Instead of matching all events
   target: artifact
   op: and
   rules:
     - op: exists
       path: /

   # Match specific event type
   event: AwsApiCall
   op: exists
   path: event/eventName
   ```

3. **Reduce rule count**:
   - Combine similar rules
   - Disable unused rules
   - Use managed rulesets (Soteria)

4. **Optimize field access**:
   - Access commonly-used fields first
   - Avoid deep nested paths
   - Use exists checks before value checks

---

## Getting Help

### Information to Collect

When seeking support, provide:

1. **Adapter Configuration**:
   - Platform type (aws, azure_monitor, gcp, etc.)
   - Adapter version
   - Configuration (sanitized, no secrets)

2. **Symptoms**:
   - What's not working
   - When it started
   - Any recent changes

3. **Logs**:
   - Adapter logs (last 100 lines)
   - Cloud platform logs (CloudTrail, Activity Log, etc.)
   - Error messages

4. **Diagnostic Results**:
   - Queue/subscription metrics
   - Event examples (sanitized)
   - Rule configurations (if relevant)

### LimaCharlie Support

- **Discord**: LimaCharlie Community Discord
- **Documentation**: https://docs.limacharlie.io
- **Support Portal**: support@limacharlie.io

### Cloud Provider Support

- **AWS**: AWS Support (if you have support plan)
- **Azure**: Azure Support Portal
- **GCP**: Google Cloud Support

### Debugging Commands

**Check Adapter Version**:
```bash
./lc_adapter version
```

**Test Connectivity**:
```bash
# AWS
aws sqs receive-message --queue-url YOUR_QUEUE_URL --max-number-of-messages 1

# Azure Event Hub (requires Event Hub SDK)
# GCP
gcloud pubsub subscriptions pull YOUR_SUBSCRIPTION --limit=1 --auto-ack
```

**Verbose Logging**:
```bash
# Most adapters support verbose flag
./lc_adapter [type] [options] --verbose
```
