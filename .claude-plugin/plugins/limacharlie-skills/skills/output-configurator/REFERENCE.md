# Output Destinations Reference

Complete configuration reference for all LimaCharlie output destinations.

## Table of Contents

- [SIEM & Security Platforms](#siem--security-platforms)
  - [Splunk](#splunk)
  - [Elastic](#elastic)
  - [OpenSearch](#opensearch)
- [Cloud Storage & Data Lakes](#cloud-storage--data-lakes)
  - [Amazon S3](#amazon-s3)
  - [Google Cloud Storage](#google-cloud-storage)
  - [Google Cloud BigQuery](#google-cloud-bigquery)
  - [Azure Storage Blob](#azure-storage-blob)
  - [Azure Event Hub](#azure-event-hub)
- [Real-Time Streaming](#real-time-streaming)
  - [Apache Kafka](#apache-kafka)
  - [Google Cloud Pub/Sub](#google-cloud-pubsub)
- [Webhooks & Notifications](#webhooks--notifications)
  - [Webhook (Individual)](#webhook-individual)
  - [Webhook (Bulk)](#webhook-bulk)
  - [Slack](#slack)
  - [Syslog](#syslog)
  - [SMTP (Email)](#smtp-email)
- [Automation & Orchestration](#automation--orchestration)
  - [Tines](#tines)

---

## Output Stream Structures

Before configuring output destinations, it's crucial to understand what data each stream type contains. LimaCharlie has four output streams, each with a different structure and purpose.

### Stream Types Overview

| Stream | Purpose | Volume | Structure |
|--------|---------|--------|-----------|
| `event` | Real-time telemetry from sensors/adapters | High | Event structure (routing + event) |
| `detect` | D&R rule alerts | Low-Medium | Detection structure |
| `audit` | Platform management actions | Low | Audit structure |
| `deployment` | Sensor lifecycle events | Very Low | Deployment structure |

### Event Stream (`event`)

**What flows**: Real-time telemetry - process executions, DNS queries, network connections, file operations, etc.

**Structure**:
```json
{
  "routing": {
    "sid": "sensor-uuid",
    "hostname": "workstation-01",
    "event_type": "NEW_PROCESS",
    "event_time": 1656959942437,
    "oid": "org-uuid",
    "plat": 268435456,
    "this": "process-hash",
    "parent": "parent-hash"
  },
  "event": {
    "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
    "COMMAND_LINE": "cmd.exe /c whoami",
    "PROCESS_ID": 4812
  }
}
```

**Common Use**: Send to SIEM for long-term storage, threat hunting, compliance, behavioral analytics.

### Detection Stream (`detect`)

**What flows**: Alerts when D&R rules match events.

**Structure**:
```json
{
  "cat": "Suspicious PowerShell",
  "source": "dr-general",
  "routing": { /* inherited from event */ },
  "detect": { /* copy of event data */ },
  "detect_id": "detection-uuid",
  "priority": 7,
  "detect_data": {
    "suspicious_file": "powershell.exe",
    "encoded_command": "base64..."
  },
  "source_rule": "detect-encoded-powershell"
}
```

**Key Fields for Parsing**:
- `cat` - Detection name
- `priority` - Priority 0-10 (filter high-priority first)
- `detect_data` - Extracted IOCs ready for enrichment
- `routing/hostname`, `routing/sid` - Context from triggering event

**Common Use**: Send to SOAR, ticketing systems, Slack for real-time alerting. Filter by `priority` to reduce noise.

### Audit Stream (`audit`)

**What flows**: Platform management events - configuration changes, user actions, API calls.

**Structure**:
```json
{
  "oid": "org-uuid",
  "ts": "2024-06-05T14:23:18Z",
  "etype": "config_change",
  "msg": "D&R rule created",
  "ident": "user@company.com",
  "entity": {
    "type": "dr_rule",
    "name": "detect-lateral-movement"
  },
  "mtd": {
    "action": "create",
    "source_ip": "203.0.113.10"
  }
}
```

**Key Fields for Parsing**:
- `ident` - Who performed the action
- `entity/type` - What was modified (dr_rule, sensor, output, etc.)
- `mtd/action` - Action type (create, update, delete)

**Common Use**: Compliance logging, security monitoring, change tracking. Required for SOC 2, ISO 27001 audits.

### Deployment Stream (`deployment`)

**What flows**: Sensor installation, removal, upgrade events.

**Structure**:
```json
{
  "routing": {
    "sid": "sensor-uuid",
    "hostname": "new-workstation",
    "event_type": "sensor_installed",
    "oid": "org-uuid"
  },
  "event": {
    "action": "install",
    "sensor_version": "4.25.0",
    "tags": ["production", "finance"]
  }
}
```

**Common Use**: Asset tracking, deployment monitoring, detecting unexpected sensor removals (potential evasion).

### Choosing the Right Stream

**For SIEM Integration**:
- Use `event` stream for all telemetry (high volume)
- Use `detect` stream for alerts only (lower volume)
- Consider separate outputs for each to different indexes

**For Real-Time Alerting** (Slack, PagerDuty):
- Use `detect` stream only
- Filter by `priority >= 7` for critical alerts

**For Compliance**:
- Use `audit` stream to tamper-proof storage
- Use `event` stream for forensic retention

**For Asset Management**:
- Use `deployment` stream to track sensor inventory

### Filtering Before Sending

Reduce volume by filtering field values:

**Event Stream - Only Windows Process Events**:
```yaml
stream: event
filters:
  - path: routing/event_type
    op: is
    value: NEW_PROCESS
  - path: routing/plat
    op: is
    value: 268435456  # Windows
```

**Detection Stream - High Priority Only**:
```yaml
stream: detect
filters:
  - path: priority
    op: is greater than
    value: 6
```

**Audit Stream - Configuration Changes Only**:
```yaml
stream: audit
filters:
  - path: etype
    op: is
    value: config_change
```

### Parsing Recommendations

**Event Stream Parsers**:
1. Index by `routing/event_type` for efficient queries
2. Extract `routing/hostname`, `routing/sid` for host correlation
3. Parse `event/*` based on `routing/event_type`

**Detection Stream Parsers**:
1. Alert severity from `priority`
2. Extract all fields in `detect_data` for IOC enrichment
3. Link back to sensor using `routing/sid`, `routing/hostname`

**Audit Stream Parsers**:
1. Index by `etype` and `entity/type`
2. Track changes by `ident` (user attribution)
3. Monitor `mtd/action` for create/update/delete patterns

For complete structure details, see the [Output Stream Structures documentation](../../../limacharlie/doc/Outputs/output-stream-structures.md).

---

## SIEM & Security Platforms

### Splunk

Send detections and events to Splunk via HTTP Event Collector (HEC).

**Type**: `webhook` or `webhook_bulk`

**Required Parameters**:
```yaml
dest_host: https://splunk-host.com:8088/services/collector/raw
auth_header_name: Authorization
auth_header_value: Splunk <HEC_TOKEN>
```

**Optional Parameters**:
```yaml
secret_key: shared-secret-for-hmac
```

**Setup Requirements**:
1. Configure HEC in Splunk with source type `_json`
2. Use `/services/collector/raw` endpoint for raw JSON
3. For Splunk Cloud, use: `https://<host>.splunkcloud.com:8088/services/collector/raw`
4. Generate HEC token in Splunk (Settings > Data Inputs > HTTP Event Collector)

**Notes**:
- Use `webhook` for individual events (detection stream)
- Use `webhook_bulk` for batched events (event stream)
- HMAC signature included in `lc-signature` header when `secret_key` is set

---

### Elastic

Index events and detections in Elasticsearch.

**Type**: `elastic`

**Required Parameters**:
```yaml
addresses: elastic-host-1.com,elastic-host-2.com
index: limacharlie
```

**Authentication Option 1 - Username/Password**:
```yaml
username: elastic_user
password: elastic_password
```

**Authentication Option 2 - API Key**:
```yaml
api_key: base64-encoded-api-key
```

**Authentication Option 3 - Cloud ID**:
```yaml
cloud_id: deployment-name:base64-cloud-id
api_key: base64-encoded-api-key
```

**Optional Parameters**:
```yaml
ca_cert: |
  -----BEGIN CERTIFICATE-----
  ...
  -----END CERTIFICATE-----
```

**Setup Requirements**:
1. Create Elasticsearch index with appropriate mapping
2. Create user with write permissions to index, or generate API key
3. For Elastic Cloud, use Cloud ID from deployment overview
4. Configure network access from LimaCharlie

**Notes**:
- Multiple addresses can be comma-separated for cluster support
- API key authentication recommended for security
- CA certificate required for self-signed TLS certificates

---

### OpenSearch

Send data to OpenSearch clusters (AWS OpenSearch, self-hosted).

**Type**: `opensearch`

**Required Parameters**:
```yaml
addresses: opensearch-host-1.com,opensearch-host-2.com
index: limacharlie
```

**Authentication**:
```yaml
username: opensearch_user
password: opensearch_password
```

**Optional Parameters**:
```yaml
ca_cert: |
  -----BEGIN CERTIFICATE-----
  ...
  -----END CERTIFICATE-----
```

**Setup Requirements**:
1. Create OpenSearch index
2. Create user with appropriate permissions
3. Configure security plugin if using AWS OpenSearch

**Notes**:
- Configuration similar to Elastic output
- Compatible with AWS OpenSearch Service
- Supports OpenSearch security plugin authentication

---

## Cloud Storage & Data Lakes

### Amazon S3

Archive events to S3 buckets for long-term storage and compliance.

**Type**: `s3`

**Required Parameters**:
```yaml
bucket: my-security-bucket
key_id: AKIAIOSFODNN7EXAMPLE
secret_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region_name: us-east-1
```

**Optional Parameters**:
```yaml
is_compression: "true"          # Highly recommended
is_indexing: "true"             # Create manifest files
sec_per_file: 300               # Seconds per file (default: 300)
dir: limacharlie/events         # Directory prefix
is_no_sharding: false           # Enable sharding for organization
```

**IAM Configuration Required**:

1. Create IAM user with programmatic access
2. Attach policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::BUCKET_NAME/*"
  }]
}
```
3. Apply bucket policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::ACCOUNT:user/USERNAME"},
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::BUCKET_NAME/*"
  }]
}
```

**File Naming Convention**:
```
<org-name>/<stream-type>/<year>/<month>/<day>/<timestamp>-<uuid>.json[.gz]
```

**Notes**:
- Compression reduces costs by ~70%
- Indexing creates manifest files for searchability
- `sec_per_file` controls batch frequency (lower = more files, higher costs)
- Files are JSON or gzipped JSON based on `is_compression`

---

### Google Cloud Storage

Archive to GCS buckets; integrate with Google Chronicle SIEM.

**Type**: `gcs`

**Required Parameters**:
```yaml
bucket: my-security-bucket
secret_key: |
  {
    "type": "service_account",
    "project_id": "my-project",
    "private_key_id": "key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "client_email": "service-account@my-project.iam.gserviceaccount.com",
    "client_id": "123456789",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
  }
```

**Optional Parameters**:
```yaml
is_compression: "true"          # Highly recommended
is_indexing: "true"             # Create manifest files
sec_per_file: 300               # Seconds per file (default: 300)
dir: limacharlie/events         # Directory prefix
```

**Service Account Setup**:
1. Create service account in GCP Console
2. Grant "Storage Object Creator" role
3. Generate JSON key
4. Paste entire JSON as `secret_key` value

**Free Output Eligibility**:
When GCS bucket is in same region as LimaCharlie datacenter, output is FREE.

LimaCharlie regions:
- USA: `us-central1`
- Canada: `northamerica-northeast1`
- Europe: `europe-west4`
- UK: `europe-west2`
- India: `asia-south1`
- Australia: `australia-southeast1`

**Chronicle Integration**:
1. Configure GCS output to bucket
2. In Chronicle, configure ingestion from GCS bucket
3. Chronicle reads files from bucket automatically

**Notes**:
- Same parameters as S3 output
- Free when region-matched with LimaCharlie datacenter
- Ideal for cost optimization

---

### Google Cloud BigQuery

Stream events to BigQuery for real-time analytics and dashboards.

**Type**: `bigquery`

**Required Parameters**:
```yaml
project: my-gcp-project
dataset: security_data
table: detections
schema: event_type:STRING, oid:STRING, sid:STRING, hostname:STRING
secret_key: |
  {
    "type": "service_account",
    "project_id": "my-project",
    "private_key_id": "key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "client_email": "service-account@my-project.iam.gserviceaccount.com",
    ...
  }
```

**Custom Transform** (maps LimaCharlie fields to BigQuery columns):
```yaml
custom_transform: |
  {
    "event_type": "routing.event_type",
    "oid": "routing.oid",
    "sid": "routing.sid",
    "hostname": "routing.hostname"
  }
```

**Optional Parameters**:
```yaml
sec_per_file: 300               # Batch interval
```

**BigQuery Setup**:
1. Create dataset in BigQuery
2. Create table with schema matching `schema` parameter
3. Create service account with "BigQuery Data Editor" role
4. Generate JSON key

**Schema Format**:
```
field1:TYPE, field2:TYPE, field3:TYPE
```

Supported types: `STRING`, `INTEGER`, `FLOAT`, `BOOLEAN`, `TIMESTAMP`, `RECORD`, `REPEATED`

**Custom Transform Template Fields**:
- `routing.event_type` - Event type
- `routing.oid` - Organization ID
- `routing.sid` - Sensor ID
- `routing.hostname` - Host name
- `routing.this_ts` - Timestamp
- `cat` - Detection category (for detection stream)
- `event.*` - Any event field

**Notes**:
- Schema must match BigQuery table EXACTLY
- Custom transform is REQUIRED to map fields
- Use Looker Studio for dashboards
- Free when region-matched with LimaCharlie datacenter

---

### Azure Storage Blob

Archive to Azure Blob Storage.

**Type**: `azure_blob`

**Required Parameters**:
```yaml
connection_string: DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net
container: limacharlie-events
```

**Optional Parameters**:
```yaml
is_compression: "true"
sec_per_file: 300
dir: events
```

**Azure Setup**:
1. Create Storage Account
2. Create Blob Container
3. Get connection string from Access Keys
4. Optional: Use SAS token for limited access

**Notes**:
- Connection string includes account name and key
- Container must exist before configuring output
- Compression recommended for cost savings

---

### Azure Event Hub

Stream events to Azure Event Hub for processing.

**Type**: `azure_event_hub`

**Required Parameters**:
```yaml
connection_string: Endpoint=sb://namespace.servicebus.windows.net/;SharedAccessKeyName=key-name;SharedAccessKey=key-value;EntityPath=hub-name
```

**IMPORTANT**: Connection string MUST include `;EntityPath=hub-name` at the end.

**Azure Setup**:
1. Create Event Hub Namespace
2. Create Event Hub within namespace
3. Create Shared Access Policy with "Send" permission
4. Get connection string and append `;EntityPath=<hub-name>`

**Notes**:
- Used for real-time event streaming to Azure services
- Integrate with Azure Stream Analytics, Functions, Logic Apps
- EntityPath MUST be included in connection string

---

## Real-Time Streaming

### Apache Kafka

Stream events to Kafka topics for real-time processing.

**Type**: `kafka`

**Required Parameters**:
```yaml
dest_host: kafka-broker1:9092,kafka-broker2:9092
topic: limacharlie-events
```

**Optional Parameters** (authentication):
```yaml
username: kafka-user
password: kafka-pass
```

**Authentication Notes**:
- When username/password provided, assumes SASL_SSL + SCRAM-SHA-512
- For no authentication, omit username/password
- For other auth mechanisms, contact LimaCharlie support

**Kafka Setup**:
1. Create Kafka topic
2. Configure appropriate retention and partitioning
3. Create SASL/SCRAM credentials if using authentication
4. Ensure network connectivity from LimaCharlie

**AWS MSK Compatibility**:
- Works with AWS Managed Streaming for Kafka
- Use MSK bootstrap servers as `dest_host`
- Configure SASL/SCRAM authentication in MSK

**Notes**:
- Multiple brokers comma-separated for fault tolerance
- Events sent as JSON strings to topic
- Consider partitioning strategy for high volume

---

### Google Cloud Pub/Sub

Stream events to Google Cloud Pub/Sub topics.

**Type**: `pubsub`

**Required Parameters**:
```yaml
project: my-gcp-project
topic: limacharlie-events
secret_key: |
  {
    "type": "service_account",
    "project_id": "my-project",
    ...
  }
```

**Service Account Setup**:
1. Create service account
2. Grant "Pub/Sub Publisher" role
3. Generate JSON key

**Pub/Sub Setup**:
1. Create Pub/Sub topic
2. Create subscription for consumers
3. Configure service account permissions

**Free Output Eligibility**:
Free when topic in same region as LimaCharlie datacenter.

**Notes**:
- Ideal for event-driven architectures
- Integrate with Cloud Functions, Cloud Run, Dataflow
- Messages published as JSON

---

## Webhooks & Notifications

### Webhook (Individual)

Send each event individually via HTTP POST.

**Type**: `webhook`

**Required Parameters**:
```yaml
dest_host: https://webhooks.corp.com/limacharlie
```

**Optional Parameters**:
```yaml
secret_key: shared-secret-for-hmac
auth_header_name: X-API-Key
auth_header_value: your-api-key
custom_transform: |
  {
    "custom_field": "{{ .routing.hostname }}"
  }
```

**Security**:
- `secret_key`: Shared secret for HMAC signature
- HMAC-SHA256 signature sent in `lc-signature` header
- Verify signature on receiver: `HMAC-SHA256(secret_key, payload)`

**Custom Transform**:
Supports Go templates to customize payload.

Example for Google Chat:
```yaml
custom_transform: |
  {
    "text": "Detection {{ .cat }} on {{ .routing.hostname }}: {{ .link }}"
  }
```

Template fields:
- `.cat` - Detection category
- `.routing.sid` - Sensor ID
- `.routing.hostname` - Host name
- `.routing.event_type` - Event type
- `.link` - Detection link
- `.event.*` - All event fields

**Receiver Implementation**:
```python
import hmac
import hashlib

def verify_signature(secret, payload, signature):
    computed = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature)

# In request handler:
signature = request.headers.get('lc-signature')
if verify_signature(SECRET_KEY, request.body, signature):
    # Process event
```

**Notes**:
- Each event sent immediately
- Best for low-volume streams (detection, audit)
- Use webhook_bulk for high volume

---

### Webhook (Bulk)

Send batched events via HTTP POST.

**Type**: `webhook_bulk`

**Required Parameters**:
```yaml
dest_host: https://webhooks.corp.com/limacharlie/bulk
```

**Optional Parameters**:
```yaml
secret_key: shared-secret-for-hmac
auth_header_name: X-API-Key
auth_header_value: your-api-key
sec_per_file: 300               # Batch interval
```

**Payload Format**:
JSON array of events:
```json
[
  {"routing": {...}, "event": {...}},
  {"routing": {...}, "event": {...}},
  ...
]
```

**Batching Behavior**:
- Events accumulated for `sec_per_file` seconds
- When batch time reached OR max size reached, POST sent
- Empty batches not sent

**Notes**:
- More efficient for high-volume streams
- Reduces per-request overhead
- Receiver must handle array of events
- HMAC signature covers entire payload

---

### Slack

Send detections and audit events to Slack channels.

**Type**: `slack`

**Required Parameters**:
```yaml
slack_api_token: xoxb-123456789-abcdefghijklmnop
slack_channel: #security-alerts
```

**Slack App Setup**:
1. Create Slack App at https://api.slack.com/apps
2. Navigate to "OAuth & Permissions"
3. Add `chat:write` Bot Token Scope
4. Install app to workspace
5. Copy "Bot User OAuth Token" (starts with `xoxb-`)
6. Invite bot to target channel: `/invite @bot-name`

**Supported Streams**:
- Detection stream - Sends alert notifications
- Audit stream - Sends audit event notifications

**Message Format**:
LimaCharlie formats messages with detection/audit details including:
- Detection name/category
- Hostname
- Timestamp
- Link to web console

**Notes**:
- Bot must be member of target channel
- NOT suitable for high-volume event stream
- Use for notifications only (detection, audit)

---

### Syslog

Forward events to syslog receivers via TCP.

**Type**: `syslog`

**Required Parameters**:
```yaml
dest_host: syslog.corp.com:514
```

**Optional Parameters**:
```yaml
is_tls: "true"                  # Enable TLS
is_strict_tls: "true"           # Enforce certificate validation
is_no_header: "false"           # Include syslog header
structured_data: additional-metadata
```

**Syslog Format**:
```
<priority>version timestamp hostname app-name procid msgid [structured-data] message
```

**TCP Mode** (plain TCP, no syslog header):
```yaml
is_no_header: "true"
```
Sends raw JSON over TCP connection.

**TLS Mode**:
```yaml
is_tls: "true"
is_strict_tls: "true"
```
Enables TLS with certificate validation.

**Notes**:
- TCP only (no UDP support)
- Use `is_no_header: true` for plain TCP JSON forwarding
- Default priority: 14 (user-level, informational)
- Structured data field for custom metadata

---

### SMTP (Email)

Send detection alerts via email.

**Type**: `smtp`

**Required Parameters**:
```yaml
smtp_server: smtp.gmail.com:587
smtp_username: alerts@company.com
smtp_password: app-password
smtp_from: limacharlie@company.com
smtp_to: soc@company.com
```

**Optional Parameters**:
```yaml
smtp_subject: LimaCharlie Detection Alert
```

**Gmail Setup** (example):
1. Enable 2FA on Google account
2. Generate App Password (Security > App Passwords)
3. Use app password as `smtp_password`

**Supported Streams**:
- Detection stream only

**Notes**:
- Not recommended for high-volume streams
- Use for critical alerts only
- Consider rate limits of email provider
- HTML formatted emails with detection details

---

## Automation & Orchestration

### Tines

Trigger Tines automation workflows from detections.

**Type**: `tines`

**Required Parameters**:
```yaml
dest_host: https://your-tenant.tines.com/webhook/unique-webhook-id/unique-webhook-token
```

**Optional Parameters**:
```yaml
secret_key: webhook-secret      # For signature verification
```

**Tines Setup**:
1. Create Story in Tines
2. Add Webhook trigger
3. Copy webhook URL
4. Optional: Set webhook secret for verification

**Use Cases**:
- Automated incident response workflows
- Enrichment and investigation automation
- Integration with ticketing systems
- Multi-tool orchestration

**Notes**:
- Detection stream most common
- Each detection triggers Tines webhook
- Tines can verify HMAC signature if `secret_key` set
- Access full detection data in Tines workflow

---

## Advanced Configuration Options

### Filtering Options

Available for all output types:

**Filter by Tag**:
```yaml
tag: production
```

**Filter by Sensor ID**:
```yaml
sensor: <sensor-id-hex>
```

**Filter by Event Type (Allow List)**:
```yaml
detection_categories:
  - NEW_PROCESS
  - NETWORK_CONNECTIONS
  - FILE_CREATE
```

**Filter by Event Type (Deny List)**:
```yaml
disallowed_detection_categories:
  - DNS_REQUEST
  - FILE_GET_REP
```

### Data Manipulation Options

**Flatten JSON**:
```yaml
flatten: true
```
Converts nested JSON to flat structure with dot notation.

**Wrap with Event Type**:
```yaml
wrap_with_event_type: true
```
Adds event type as top-level key.

**Exclude Routing Metadata**:
```yaml
is_no_routing: true
```
Removes routing label to reduce data volume.

### Management Options

**Delete on Failure**:
```yaml
delete_on_failure: true
```
Automatically removes output if it fails to deliver.

**Custom Labels**:
```yaml
labels:
  environment: production
  team: security-ops
```
Add metadata for organization and filtering.

---

## Output State Management

### Failure Handling

When an output fails:
1. **Automatic Disable**: Output temporarily disabled
2. **Error Logging**: Error logged to Platform Logs > Errors
3. **Auto Re-enable**: Attempts to re-enable after cooldown
4. **Manual Re-enable**: Edit and save output to force retry

### Monitoring Output Health

Check output status:
1. Navigate to "Outputs" in web console
2. View status indicator (green = healthy, red = failed)
3. Check "Platform Logs" > "Errors" for details
4. Look for key `outputs/<output-name>`

---

## Network and Authentication

### Network Connectivity

LimaCharlie outputs originate from auto-scaling infrastructure without static IPs.

**For Allowlisting**:
- Use authentication headers instead of IP allowlisting
- Implement webhook signature verification
- Use TLS/HTTPS for encryption

### Authentication Methods

Different destinations support different auth methods:

**API Keys**: Splunk, custom webhooks
**Username/Password**: Elastic, OpenSearch, Kafka, SMTP
**Service Account JSON**: GCP services (GCS, BigQuery, Pub/Sub)
**IAM Keys**: AWS S3
**Connection Strings**: Azure services
**OAuth Tokens**: Slack

### Security Recommendations

1. Use HTTPS/TLS endpoints
2. Implement HMAC signature verification for webhooks
3. Rotate credentials regularly
4. Use service accounts with minimal permissions
5. Enable TLS certificate validation
6. Store credentials securely (LimaCharlie encrypts at rest)

---

## Performance Considerations

### Batching Recommendations

- **Webhook**: Use individual for <100 events/hour
- **Webhook Bulk**: Use bulk for >100 events/hour
- **S3/GCS**: 300-600 seconds per file typical
- **BigQuery**: 300 seconds typical

### Compression Recommendations

Always enable compression for:
- S3 outputs
- GCS outputs
- High-volume storage

Saves ~70% storage and transfer costs.

### Filtering Recommendations

Filter at source (output configuration) rather than destination:
- Reduces data transfer costs
- Improves performance
- Simplifies destination processing

Use tailored streams for most precise filtering.
