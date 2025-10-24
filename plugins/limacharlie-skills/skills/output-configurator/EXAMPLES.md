# Output Configuration Examples

Complete end-to-end examples for common output configurations.

## Table of Contents

1. [Example 1: Splunk Integration for Detections](#example-1-splunk-integration-for-detections)
2. [Example 2: S3 Archive for Long-Term Storage](#example-2-s3-archive-for-long-term-storage)
3. [Example 3: BigQuery for Analytics](#example-3-bigquery-for-analytics)
4. [Example 4: Slack Notifications for Critical Detections](#example-4-slack-notifications-for-critical-detections)
5. [Example 5: Tailored Stream for Specific Process Monitoring](#example-5-tailored-stream-for-specific-process-monitoring)

---

## Example 1: Splunk Integration for Detections

### Goal
Send all detection alerts to Splunk via HTTP Event Collector (HEC) for SOC team analysis.

### Prerequisites
- Splunk Enterprise or Splunk Cloud instance
- Admin access to configure HEC
- Network connectivity from LimaCharlie to Splunk

### Step 1: Configure Splunk HEC

1. Log in to Splunk as admin
2. Navigate to **Settings > Data Inputs > HTTP Event Collector**
3. Click **New Token**
4. Configure token:
   - Name: `LimaCharlie Detections`
   - Source type: `_json`
   - Index: `security` (or create new index)
   - Enable token
5. Copy the generated token (e.g., `EA12XXXX-XXXX-XXXX-XXXX-XXXXXXXXXX34`)

### Step 2: Test HEC Endpoint

```bash
curl -k https://splunk.corp.com:8088/services/collector/raw \
  -H "Authorization: Splunk EA12XXXX-XXXX-XXXX-XXXX-XXXXXXXXXX34" \
  -d '{"test": "event"}'
```

Should return: `{"text":"Success","code":0}`

### Step 3: Configure LimaCharlie Output

```yaml
# Output Configuration
name: splunk-detections
stream: detection
destination: webhook

# Webhook Settings
dest_host: https://splunk.corp.com:8088/services/collector/raw
auth_header_name: Authorization
auth_header_value: Splunk EA12XXXX-XXXX-XXXX-XXXX-XXXXXXXXXX34
secret_key: my-shared-hmac-secret

# Advanced Settings
flatten: false
wrap_with_event_type: false
delete_on_failure: false
```

### Step 4: Test Configuration

1. In LimaCharlie, temporarily change stream to `audit`
2. Make any configuration change (e.g., edit the output description)
3. In Splunk, search: `index=security sourcetype=_json`
4. Verify audit event appears
5. Switch stream back to `detection`

### Step 5: Create Splunk Dashboards

Example Splunk searches:

**Top Detections**:
```spl
index=security sourcetype=_json
| stats count by cat
| sort -count
```

**Detections by Host**:
```spl
index=security sourcetype=_json
| stats count by routing.hostname
| sort -count
```

**Detection Timeline**:
```spl
index=security sourcetype=_json
| timechart count by cat
```

### Troubleshooting

**Issue**: Events not appearing in Splunk
- Verify HEC token is enabled
- Check Splunk HEC logs: `/opt/splunk/var/log/splunk/splunkd.log`
- Verify index exists and is not frozen
- Check LimaCharlie Platform Logs for errors

**Issue**: Certificate errors
- For testing, use `-k` flag (ignore cert) in curl
- For production, ensure valid SSL certificate
- Or use Splunk's self-signed cert with `is_strict_tls: false`

### Advanced: High-Volume Event Stream

For full event stream (not just detections), use bulk webhook:

```yaml
name: splunk-events-bulk
stream: event
destination: webhook_bulk

dest_host: https://splunk.corp.com:8088/services/collector/raw
auth_header_name: Authorization
auth_header_value: Splunk EA12XXXX-XXXX-XXXX-XXXX-XXXXXXXXXX34
secret_key: my-shared-hmac-secret
sec_per_file: 300

# Filter to reduce volume
detection_categories:
  - NEW_PROCESS
  - NETWORK_CONNECTIONS
  - DNS_REQUEST
```

---

## Example 2: S3 Archive for Long-Term Storage

### Goal
Archive all EDR events to S3 with compression for compliance and long-term analysis.

### Prerequisites
- AWS account with S3 access
- IAM user creation permissions
- LimaCharlie organization

### Step 1: Create S3 Bucket

```bash
aws s3 mb s3://my-security-archive --region us-east-1
```

Or via AWS Console:
1. Navigate to S3
2. Click **Create bucket**
3. Name: `my-security-archive`
4. Region: `us-east-1`
5. Disable public access (recommended)
6. Create bucket

### Step 2: Create IAM User

```bash
aws iam create-user --user-name limacharlie-s3-writer
```

Create access keys:
```bash
aws iam create-access-key --user-name limacharlie-s3-writer
```

Save the output:
- Access Key ID: `AKIAIOSFODNN7EXAMPLE`
- Secret Access Key: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

### Step 3: Create IAM Policy

Create file `limacharlie-s3-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::my-security-archive/*"
  }]
}
```

Attach to user:
```bash
aws iam put-user-policy \
  --user-name limacharlie-s3-writer \
  --policy-name S3WriteAccess \
  --policy-document file://limacharlie-s3-policy.json
```

### Step 4: Configure Bucket Policy

Create file `bucket-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::123456789012:user/limacharlie-s3-writer"
    },
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::my-security-archive/*"
  }]
}
```

Apply policy:
```bash
aws s3api put-bucket-policy \
  --bucket my-security-archive \
  --policy file://bucket-policy.json
```

### Step 5: Configure LimaCharlie Output

```yaml
# Output Configuration
name: s3-event-archive
stream: event
destination: s3

# S3 Settings
bucket: my-security-archive
key_id: AKIAIOSFODNN7EXAMPLE
secret_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region_name: us-east-1
is_compression: "true"
is_indexing: "false"
sec_per_file: 600
dir: limacharlie/events

# Advanced Settings - Reduce data size
is_no_routing: true  # Exclude routing metadata to save space
```

### Step 6: Test and Verify

1. Start with audit stream for testing
2. Wait 10 minutes (600 seconds)
3. Check S3 bucket:
```bash
aws s3 ls s3://my-security-archive/limacharlie/events/ --recursive
```

Expected file structure:
```
limacharlie/events/my-org/event/2024/01/15/20240115-143025-abc123.json.gz
```

4. Download and verify file:
```bash
aws s3 cp s3://my-security-archive/limacharlie/events/my-org/event/2024/01/15/20240115-143025-abc123.json.gz .
gunzip 20240115-143025-abc123.json.gz
cat 20240115-143025-abc123.json | jq .
```

5. Switch to event stream

### Step 7: Cost Optimization

**Enable Lifecycle Policy** to transition old data to cheaper storage:

```json
{
  "Rules": [{
    "Id": "ArchiveOldEvents",
    "Status": "Enabled",
    "Filter": {"Prefix": "limacharlie/events/"},
    "Transitions": [
      {
        "Days": 90,
        "StorageClass": "STANDARD_IA"
      },
      {
        "Days": 180,
        "StorageClass": "GLACIER"
      }
    ],
    "Expiration": {
      "Days": 2555
    }
  }]
}
```

Apply lifecycle:
```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-security-archive \
  --lifecycle-configuration file://lifecycle.json
```

### Volume and Cost Estimation

Assumptions:
- 100 endpoints
- 10 MB per endpoint per day (compressed)
- S3 Standard storage: $0.023/GB/month

Monthly data: `100 endpoints × 10 MB × 30 days = 30 GB`
Monthly cost: `30 GB × $0.023 = $0.69`

With lifecycle (90 days Standard, 90 days IA, rest Glacier):
- Standard (0-90 days): 90 GB × $0.023 = $2.07
- IA (90-180 days): 90 GB × $0.0125 = $1.13
- Glacier (180+ days): Variable

### Troubleshooting

**Issue**: Access Denied errors
- Verify IAM user has correct policy
- Check bucket policy allows IAM user
- Verify bucket name and region are correct
- Check access keys are not rotated/deleted

**Issue**: No files appearing
- Wait full `sec_per_file` duration
- Check Platform Logs for errors
- Verify stream has events (check Timeline)
- Test with audit stream first

---

## Example 3: BigQuery for Analytics

### Goal
Stream detections to BigQuery for real-time dashboards with Looker Studio.

### Prerequisites
- Google Cloud Platform project
- BigQuery API enabled
- Service account creation permissions

### Step 1: Create BigQuery Dataset and Table

```bash
# Create dataset
bq mk --dataset \
  --location=US \
  my-project:security_data

# Create table
bq mk --table \
  my-project:security_data.detections \
  timestamp:TIMESTAMP,event_type:STRING,hostname:STRING,detection_name:STRING,sid:STRING,oid:STRING,link:STRING,severity:STRING
```

Or via GCP Console:
1. Navigate to BigQuery
2. Click **Create Dataset**
   - Dataset ID: `security_data`
   - Location: `US` (or match LimaCharlie region for free output)
3. Click **Create Table**
   - Dataset: `security_data`
   - Table: `detections`
   - Schema:
     ```
     timestamp: TIMESTAMP
     event_type: STRING
     hostname: STRING
     detection_name: STRING
     sid: STRING
     oid: STRING
     link: STRING
     severity: STRING
     ```

### Step 2: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create limacharlie-bigquery \
  --display-name "LimaCharlie BigQuery Writer"

# Grant BigQuery Data Editor role
gcloud projects add-iam-policy-binding my-project \
  --member "serviceAccount:limacharlie-bigquery@my-project.iam.gserviceaccount.com" \
  --role "roles/bigquery.dataEditor"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account limacharlie-bigquery@my-project.iam.gserviceaccount.com
```

### Step 3: Configure LimaCharlie Output

```yaml
# Output Configuration
name: bigquery-detections
stream: detection
destination: bigquery

# BigQuery Settings
project: my-project
dataset: security_data
table: detections
schema: timestamp:TIMESTAMP, event_type:STRING, hostname:STRING, detection_name:STRING, sid:STRING, oid:STRING, link:STRING, severity:STRING
secret_key: |
  {
    "type": "service_account",
    "project_id": "my-project",
    "private_key_id": "abc123...",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
    "client_email": "limacharlie-bigquery@my-project.iam.gserviceaccount.com",
    "client_id": "123456789",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/limacharlie-bigquery%40my-project.iam.gserviceaccount.com"
  }
custom_transform: |
  {
    "timestamp": "routing.this_ts",
    "event_type": "routing.event_type",
    "hostname": "routing.hostname",
    "detection_name": "cat",
    "sid": "routing.sid",
    "oid": "routing.oid",
    "link": "link",
    "severity": "routing.severity"
  }
sec_per_file: 300
```

### Step 4: Test Configuration

1. Start with audit stream
2. Wait 5 minutes (300 seconds)
3. Query BigQuery:
```sql
SELECT * FROM `my-project.security_data.detections`
ORDER BY timestamp DESC
LIMIT 10
```

4. Verify data appears correctly
5. Switch to detection stream

### Step 5: Create Looker Studio Dashboard

1. Navigate to https://lookerstudio.google.com
2. Click **Create > Data Source**
3. Select **BigQuery**
4. Choose project: `my-project`
5. Choose dataset: `security_data`
6. Choose table: `detections`
7. Click **Connect**

Create visualizations:

**Detection Count Over Time**:
- Chart type: Time series
- Dimension: `timestamp` (Date Hour)
- Metric: Record Count

**Top Detections**:
- Chart type: Bar chart
- Dimension: `detection_name`
- Metric: Record Count
- Sort: Descending

**Detections by Host**:
- Chart type: Table
- Dimensions: `hostname`, `detection_name`
- Metrics: Record Count
- Filter: Last 7 days

**Detection Heatmap**:
- Chart type: Heatmap
- Row dimension: `hostname`
- Column dimension: `detection_name`
- Metric: Record Count

### Step 6: Cost Optimization

For FREE BigQuery output:
1. Create BigQuery dataset in same region as LimaCharlie datacenter
2. For USA: use `us-central1`
3. Update dataset location:
```bash
bq mk --dataset \
  --location=us-central1 \
  my-project:security_data_us
```

BigQuery storage costs:
- Active storage: $0.020/GB/month
- Long-term storage: $0.010/GB/month (90+ days)

BigQuery query costs:
- $5.00 per TB processed
- First 1 TB per month free

### Troubleshooting

**Issue**: Schema mismatch errors
- Verify schema string EXACTLY matches table schema
- Check field types match (STRING, TIMESTAMP, etc.)
- Ensure custom_transform maps to all schema fields

**Issue**: Permission denied
- Verify service account has BigQuery Data Editor role
- Check project_id in service account JSON matches BigQuery project
- Verify dataset and table exist

**Issue**: No data appearing
- Wait full `sec_per_file` duration (5 minutes)
- Check Platform Logs for errors
- Verify detections are being generated
- Test with audit stream first

---

## Example 4: Slack Notifications for Critical Detections

### Goal
Send critical security alerts to Slack channel for immediate SOC team awareness.

### Prerequisites
- Slack workspace with admin permissions
- Ability to create Slack apps

### Step 1: Create Slack App

1. Navigate to https://api.slack.com/apps
2. Click **Create New App**
3. Choose **From scratch**
4. App Name: `LimaCharlie Alerts`
5. Workspace: Select your workspace
6. Click **Create App**

### Step 2: Configure Bot Permissions

1. Click **OAuth & Permissions** in left sidebar
2. Scroll to **Scopes > Bot Token Scopes**
3. Click **Add an OAuth Scope**
4. Add scope: `chat:write`
5. Scroll to top and click **Install to Workspace**
6. Click **Allow**
7. Copy **Bot User OAuth Token** (starts with `xoxb-`)
   Example: `xoxb-123456789-987654321-AbCdEfGhIjKlMnOpQrStUvWx`

### Step 3: Create Slack Channel and Invite Bot

1. In Slack, create channel (or use existing):
   - Name: `#security-critical`
   - Make it private if containing sensitive info
2. In the channel, type: `/invite @LimaCharlie Alerts`
3. Bot joins the channel

### Step 4: Configure LimaCharlie Output

```yaml
# Output Configuration
name: slack-critical-alerts
stream: detection
destination: slack

# Slack Settings
slack_api_token: xoxb-123456789-987654321-AbCdEfGhIjKlMnOpQrStUvWx
slack_channel: #security-critical

# Advanced Settings - Filter for critical only
detection_categories:
  - ransomware-detected
  - lateral-movement
  - privilege-escalation
  - credential-theft
  - suspicious-powershell
```

**Note**: `detection_categories` filters by detection rule names, not event types.

### Step 5: Test Configuration

1. Temporarily remove `detection_categories` filter
2. Change stream to `audit`
3. Make a configuration change in LimaCharlie
4. Check Slack channel for audit notification
5. Restore `detection_categories` filter
6. Switch stream to `detection`

### Step 6: Trigger Test Detection

Create test D&R rule to verify:

```yaml
# Test Detection Rule
detect:
  op: is
  event: USER_OBSERVED
  path: event/USERNAME
  value: test-alert

respond:
  - action: report
    name: test-critical-detection
```

1. Save rule with name: `test-critical-detection`
2. Trigger detection (user login with username "test-alert")
3. Check Slack channel for notification
4. Delete test rule

### Step 7: Configure Multiple Severity Levels

For tiered alerting, create multiple outputs:

**Critical Alerts**:
```yaml
name: slack-critical
stream: detection
destination: slack
slack_api_token: xoxb-...
slack_channel: #security-critical
detection_categories:
  - ransomware-detected
  - lateral-movement
```

**High Alerts**:
```yaml
name: slack-high
stream: detection
destination: slack
slack_api_token: xoxb-...
slack_channel: #security-high
detection_categories:
  - suspicious-process
  - suspicious-network
```

**Audit Events**:
```yaml
name: slack-audit
stream: audit
destination: slack
slack_api_token: xoxb-...
slack_channel: #security-audit
```

### Message Format

LimaCharlie sends formatted messages:

**Detection Message**:
```
Detection: ransomware-detected
Host: DESKTOP-ABC123
Time: 2024-01-15 14:30:25 UTC
Link: https://app.limacharlie.io/...
```

**Audit Message**:
```
Audit Event: output_modified
User: admin@company.com
Time: 2024-01-15 14:30:25 UTC
Details: Modified output 'splunk-detections'
```

### Troubleshooting

**Issue**: Bot not in channel
- Manually invite: `/invite @LimaCharlie Alerts`
- Verify bot installed to workspace
- Check bot has `chat:write` scope

**Issue**: Messages not appearing
- Verify token starts with `xoxb-` (not `xoxp-`)
- Check token hasn't been revoked
- Verify channel name includes `#`
- Check Platform Logs for errors

**Issue**: Too many messages
- Add `detection_categories` filter
- Create separate channels for different severities
- Consider using webhook with custom filtering instead

### Advanced: Custom Slack Messages via Webhook

For custom message formatting, use webhook output with Slack webhook URL:

```yaml
name: slack-custom-alerts
stream: detection
destination: webhook

dest_host: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
custom_transform: |
  {
    "text": ":rotating_light: *{{ .cat }}* detected on {{ .routing.hostname }}",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Detection:* {{ .cat }}\n*Host:* {{ .routing.hostname }}\n*Time:* {{ .routing.this_ts }}"
        }
      },
      {
        "type": "actions",
        "elements": [{
          "type": "button",
          "text": {"type": "plain_text", "text": "View in LimaCharlie"},
          "url": "{{ .link }}"
        }]
      }
    ]
  }
```

This provides richer formatting with buttons and emojis.

---

## Example 5: Tailored Stream for Specific Process Monitoring

### Goal
Send only specific PowerShell and CMD events to webhook for focused monitoring without full event stream overhead.

### Prerequisites
- Webhook receiver endpoint
- LimaCharlie organization with D&R rules

### Step 1: Set Up Webhook Receiver

Example Python Flask receiver:

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)
SECRET_KEY = "my-shared-secret"

def verify_signature(payload, signature):
    computed = hmac.new(
        SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature)

@app.route('/limacharlie/suspicious-processes', methods=['POST'])
def receive_event():
    # Verify HMAC signature
    signature = request.headers.get('lc-signature')
    if not signature or not verify_signature(request.data.decode(), signature):
        return jsonify({"error": "Invalid signature"}), 403

    # Process event
    event = request.json
    print(f"Suspicious process detected:")
    print(f"  Process: {event['event']['FILE_PATH']}")
    print(f"  Command: {event['event'].get('COMMAND_LINE', 'N/A')}")
    print(f"  Host: {event['routing']['hostname']}")

    # Add your custom logic here
    # - Store in database
    # - Trigger automation
    # - Send notification

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Deploy receiver and get public URL (e.g., `https://webhooks.corp.com/limacharlie/suspicious-processes`)

### Step 2: Configure LimaCharlie Tailored Output

```yaml
# Output Configuration
name: suspicious-processes
stream: tailored
destination: webhook

# Webhook Settings
dest_host: https://webhooks.corp.com/limacharlie/suspicious-processes
secret_key: my-shared-secret
auth_header_name: X-API-Key
auth_header_value: your-api-key-here
```

**Important**: Stream must be `tailored`. This output will NOT receive events until D&R rule forwards to it.

### Step 3: Create D&R Rules to Forward Events

**Rule 1: PowerShell with Encoded Commands**

```yaml
# Detection & Response Rule
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: powershell.exe
      case sensitive: false
    - op: or
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: "-enc"
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: "-encodedcommand"
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: "frombase64string"
          case sensitive: false

respond:
  - action: report
    name: suspicious-powershell-encoding
  - action: output
    name: suspicious-processes
```

Save this rule as: `suspicious-powershell-encoding`

**Rule 2: CMD with Suspicious Patterns**

```yaml
# Detection & Response Rule
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: cmd.exe
      case sensitive: false
    - op: or
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: "/c echo"
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: "& whoami"
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: "net user"
          case sensitive: false

respond:
  - action: report
    name: suspicious-cmd-patterns
  - action: output
    name: suspicious-processes
```

Save this rule as: `suspicious-cmd-patterns`

**Rule 3: Any Process from Suspicious Paths**

```yaml
# Detection & Response Rule
detect:
  event: NEW_PROCESS
  op: or
  rules:
    - op: starts with
      path: event/FILE_PATH
      value: "C:\\Users\\Public\\"
      case sensitive: false
    - op: starts with
      path: event/FILE_PATH
      value: "C:\\ProgramData\\"
      case sensitive: false
    - op: starts with
      path: event/FILE_PATH
      value: "C:\\Temp\\"
      case sensitive: false

respond:
  - action: report
    name: process-from-suspicious-path
  - action: output
    name: suspicious-processes
```

Save this rule as: `process-from-suspicious-path`

### Step 4: Test the Configuration

1. Trigger a test detection by running PowerShell with encoded command:
```powershell
powershell.exe -enc "SGVsbG8gV29ybGQ="
```

2. Check webhook receiver logs for event
3. Verify event includes full process details
4. Check LimaCharlie Timeline to confirm detection fired

### Step 5: Monitoring and Metrics

Check output health:
1. Navigate to **Outputs** in LimaCharlie console
2. Find output: `suspicious-processes`
3. View statistics:
   - Events sent
   - Last sent timestamp
   - Error count

Monitor D&R rules:
1. Navigate to **Detection & Response** > **Rules**
2. View rule statistics for trigger counts
3. Adjust rules based on false positive rate

### Benefits of Tailored Stream

**Cost Efficiency**:
- Only specific events sent (not full event stream)
- Reduces data transfer costs
- Lower webhook receiver load

**Precision**:
- Complex filtering using D&R rule logic
- Can combine multiple conditions
- Easy to add/remove specific detections

**Flexibility**:
- Multiple D&R rules can forward to same output
- Different outputs for different event types
- Can modify filtering without changing output config

### Advanced: Multiple Tailored Outputs

Create separate outputs for different purposes:

**Suspicious Processes**:
```yaml
name: suspicious-processes
stream: tailored
destination: webhook
dest_host: https://webhooks.corp.com/suspicious-processes
```
Forward: PowerShell, CMD, suspicious paths

**Lateral Movement**:
```yaml
name: lateral-movement
stream: tailored
destination: webhook
dest_host: https://webhooks.corp.com/lateral-movement
```
Forward: Remote execution, PsExec, WMI, PowerShell remoting

**Credential Access**:
```yaml
name: credential-access
stream: tailored
destination: webhook
dest_host: https://webhooks.corp.com/credential-access
```
Forward: LSASS access, credential dumping, registry access

Each D&R rule specifies output name in `respond` action.

### Scaling Considerations

For high-volume tailored streams, use webhook_bulk:

```yaml
name: suspicious-processes-bulk
stream: tailored
destination: webhook_bulk
dest_host: https://webhooks.corp.com/suspicious-processes/bulk
secret_key: my-shared-secret
sec_per_file: 300
```

Update D&R rules to forward to `suspicious-processes-bulk`.

Receiver must handle batch format:
```python
@app.route('/limacharlie/suspicious-processes/bulk', methods=['POST'])
def receive_batch():
    events = request.json  # Array of events
    for event in events:
        # Process each event
        print(f"Process: {event['event']['FILE_PATH']}")
    return jsonify({"status": "received"}), 200
```

### Troubleshooting

**Issue**: No events received at webhook
- Verify D&R rules are enabled
- Check rules have `output` action with correct output name
- Trigger test detection manually
- Check Platform Logs for errors

**Issue**: Too many events
- Add more specific filtering in D&R rules
- Use `op: and` to combine conditions
- Add exclusions for known-good processes

**Issue**: Missing expected events
- Verify event type is correct (NEW_PROCESS, etc.)
- Check path case sensitivity
- Review D&R rule logic
- Test rule separately with `report` action first

---

## Summary

These examples demonstrate:

1. **Splunk**: Traditional SIEM integration with HEC
2. **S3**: Long-term archival with compression and lifecycle policies
3. **BigQuery**: Real-time analytics with dashboard visualization
4. **Slack**: Immediate notifications with filtering
5. **Tailored Stream**: Precise event forwarding with D&R rules

Key patterns:
- Always test with audit stream first
- Use compression for storage outputs
- Filter events to reduce volume and costs
- Implement HMAC verification for webhooks
- Match GCP regions for free outputs
- Use tailored streams for precise filtering

For additional help, see:
- SKILL.md for general guidance
- REFERENCE.md for complete configuration syntax
- TROUBLESHOOTING.md for common issues
