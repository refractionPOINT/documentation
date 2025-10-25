# Adapter Setup Examples

Complete, step-by-step setup examples for the most popular LimaCharlie adapters.

## AWS CloudTrail via S3

**Complete setup including AWS IAM configuration**

### Step 1: Enable CloudTrail

1. Go to AWS CloudTrail console
2. Create trail or use existing trail
3. Note the S3 bucket name (e.g., `my-cloudtrail-bucket`)
4. Ensure trail is logging to S3

### Step 2: Create IAM User

1. Go to AWS IAM console
2. Create new IAM user: `limacharlie-adapter`
3. Attach inline policy:

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
        "arn:aws:s3:::my-cloudtrail-bucket",
        "arn:aws:s3:::my-cloudtrail-bucket/*"
      ]
    }
  ]
}
```

4. Create access key and save the credentials

### Step 3: Configure LimaCharlie Adapter

**Option A: Cloud-to-Cloud (via Hive)**

```yaml
sensor_type: s3
s3:
  bucket_name: "my-cloudtrail-bucket"
  secret_key: "hive://secret/aws-secret-key"
  access_key: "hive://secret/aws-access-key"
  prefix: "AWSLogs/"
  region: "us-east-1"
  polling_seconds: 60
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "aws"
    sensor_seed_key: "aws-cloudtrail-prod"
    hostname: "aws-cloudtrail-s3"
```

Create in LimaCharlie:
```bash
# Store secrets
echo "YOUR_AWS_SECRET" | limacharlie hive set secret --key aws-secret-key --data -
echo "YOUR_AWS_ACCESS" | limacharlie hive set secret --key aws-access-key --data -

# Create cloud sensor
cat cloudtrail.yaml | limacharlie hive set cloud_sensor --key aws-cloudtrail --data -
```

**Option B: On-Premises Binary**

```bash
# Download adapter
wget https://downloads.limacharlie.io/adapter/linux/64 -O lc-adapter
chmod +x lc-adapter

# Run adapter
./lc-adapter s3 \
  bucket_name=my-cloudtrail-bucket \
  secret_key=$AWS_SECRET_ACCESS_KEY \
  access_key=$AWS_ACCESS_KEY_ID \
  region=us-east-1 \
  prefix=AWSLogs/ \
  client_options.identity.oid=$LIMACHARLIE_OID \
  client_options.identity.installation_key=$LIMACHARLIE_KEY \
  client_options.platform=aws \
  client_options.sensor_seed_key=aws-cloudtrail-prod
```

### Step 4: Verify Data Flow

1. Check adapter is connected:
   - Go to LimaCharlie web app > Sensors
   - Look for sensor with seed key `aws-cloudtrail-prod`
   - Check "Last Seen" timestamp

2. Query events:
   ```
   event_type:cloudtrail
   ```

---

## AWS CloudTrail via SQS (Real-Time)

**Faster ingestion using S3 event notifications**

### Step 1: Create SQS Queue

1. Go to AWS SQS console
2. Create queue: `limacharlie-cloudtrail-events`
3. Type: Standard queue
4. Note the queue URL

### Step 2: Configure S3 Event Notifications

1. Go to CloudTrail S3 bucket
2. Properties > Event notifications > Create event notification
3. Name: `cloudtrail-to-sqs`
4. Event types: "All object create events"
5. Destination: SQS queue
6. Select your queue: `limacharlie-cloudtrail-events`

### Step 3: Create IAM User

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
      "Resource": "arn:aws:sqs:us-east-1:123456789012:limacharlie-cloudtrail-events"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::my-cloudtrail-bucket/*"
    }
  ]
}
```

### Step 4: Configure Adapter

```yaml
sensor_type: sqs
sqs:
  queue_url: "https://sqs.us-east-1.amazonaws.com/123456789012/limacharlie-cloudtrail-events"
  region: "us-east-1"
  secret_key: "hive://secret/aws-secret-key"
  access_key: "hive://secret/aws-access-key"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "aws"
    sensor_seed_key: "aws-cloudtrail-realtime"
```

**Benefits**: Near real-time ingestion (seconds vs minutes), more efficient than polling S3

---

## Azure Event Hub for Entra ID Logs

**Complete setup for Azure AD/Entra ID sign-in and audit logs**

### Step 1: Create Event Hub

1. Go to Azure Portal
2. Create Event Hubs namespace:
   - Name: `limacharlie-logs`
   - Pricing tier: Standard or higher
   - Location: Your region

3. Create Event Hub within namespace:
   - Name: `entra-id-logs`
   - Partition count: 2
   - Message retention: 1 day

4. Get connection string:
   - Go to namespace > Shared access policies
   - Click "RootManageSharedAccessKey"
   - Copy "Connection string–primary key"

### Step 2: Configure Diagnostic Settings

1. Go to Entra ID (Azure Active Directory)
2. Diagnostic settings > Add diagnostic setting
3. Name: `export-to-eventhub`
4. Select log categories:
   - `SignInLogs`
   - `AuditLogs`
   - `NonInteractiveUserSignInLogs`
   - `ServicePrincipalSignInLogs`
   - `ManagedIdentitySignInLogs`
5. Destination: Stream to an event hub
6. Select your namespace and event hub
7. Save

### Step 3: Update Connection String

The connection string needs `EntityPath=hub-name` at the end:

```
Original:
Endpoint=sb://limacharlie-logs.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=XXXXX

Updated:
Endpoint=sb://limacharlie-logs.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=XXXXX;EntityPath=entra-id-logs
```

### Step 4: Configure LimaCharlie Adapter

**Cloud-to-Cloud (Recommended)**:

```yaml
sensor_type: azure_event_hub
azure_event_hub:
  connection_string: "hive://secret/azure-eventhub-conn"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "azure_ad"
    sensor_seed_key: "azure-entra-id"
    hostname: "azure-entra-id-logs"
```

Store and create:
```bash
# Store connection string
echo "Endpoint=sb://...;EntityPath=entra-id-logs" | limacharlie hive set secret --key azure-eventhub-conn --data -

# Create cloud sensor
cat azure-eventhub.yaml | limacharlie hive set cloud_sensor --key azure-entra --data -
```

**On-Premises Binary**:

```bash
./lc-adapter azure_event_hub \
  connection_string="Endpoint=sb://...;EntityPath=entra-id-logs" \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=azure_ad \
  client_options.sensor_seed_key=azure-entra-id
```

### Step 5: Verify

Query events:
```
event_type:azure_ad
```

Look for sign-in events, audit logs, MFA events.

---

## Azure Monitor Logs (Multi-Resource)

**Ingest logs from multiple Azure resources**

### Setup for Application Insights, VMs, App Services, etc.

1. Create Event Hub (same as Entra ID example)

2. Configure diagnostic settings for each resource:
   - Go to resource (VM, App Service, etc.)
   - Diagnostic settings > Add
   - Select log categories
   - Stream to event hub

3. Use same Event Hub for multiple resources

4. Configure adapter with `platform: azure_monitor`:

```yaml
sensor_type: azure_event_hub
azure_event_hub:
  connection_string: "hive://secret/azure-eventhub-conn"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "azure_monitor"
    sensor_seed_key: "azure-resources"
    hostname: "azure-monitor-logs"
```

---

## GCP Audit Logs via Pub/Sub

**Complete setup for Google Cloud Platform audit logs**

### Step 1: Create Pub/Sub Topic and Subscription

1. Go to GCP Console > Pub/Sub
2. Create topic: `limacharlie-audit-logs`
3. Create subscription:
   - Name: `limacharlie-audit-sub`
   - Delivery type: Pull
   - Acknowledgement deadline: 60 seconds

### Step 2: Create Log Sink

1. Go to Logging > Log Router
2. Create sink:
   - Name: `export-audit-to-pubsub`
   - Sink service: Cloud Pub/Sub topic
   - Select topic: `limacharlie-audit-logs`
3. Choose logs to include (filter):
   ```
   logName:"cloudaudit.googleapis.com"
   ```
4. Create sink

### Step 3: Create Service Account

1. Go to IAM & Admin > Service Accounts
2. Create service account: `limacharlie-adapter`
3. Grant roles:
   - `Pub/Sub Subscriber` on the subscription
4. Create and download JSON key

### Step 4: Configure Adapter

**Cloud-to-Cloud**:

```yaml
sensor_type: pubsub
pubsub:
  sub_name: "limacharlie-audit-sub"
  project_name: "my-gcp-project"
  service_account_creds: "hive://secret/gcp-service-account"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "gcp"
    sensor_seed_key: "gcp-audit-logs"
    hostname: "gcp-audit"
```

Store credentials:
```bash
# Store service account JSON
cat service-account.json | limacharlie hive set secret --key gcp-service-account --data -

# Create cloud sensor
cat gcp-pubsub.yaml | limacharlie hive set cloud_sensor --key gcp-audit --data -
```

**On-Premises Binary**:

```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Run adapter
./lc-adapter pubsub \
  sub_name=limacharlie-audit-sub \
  project_name=my-gcp-project \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=gcp \
  client_options.sensor_seed_key=gcp-audit-logs
```

---

## Google Workspace Logs

**Setup for Google Workspace admin, login, and drive logs**

### Step 1: Enable GCP Integration

1. Go to Google Workspace Admin Console
2. Security > API controls > API permissions
3. Enable "Google Cloud Platform Sharing Options"
4. Set organization: Select your GCP organization

### Step 2: Verify Logs in GCP

1. Go to GCP Console > Logging > Logs Explorer
2. Set resource to "Organization" level (not project!)
3. Look for logs:
   ```
   logName:"cloudaudit.googleapis.com/activity"
   protoPayload.serviceName:"login.googleapis.com"
   ```

### Step 3: Create Log Sink (at Organization Level)

1. Go to Logging > Log Router (make sure you're at Organization level!)
2. Create sink:
   - Name: `workspace-to-pubsub`
   - Sink service: Cloud Pub/Sub topic
   - Create new topic or use existing
3. Filter for Workspace logs:
   ```
   protoPayload.serviceName:("admin.googleapis.com" OR "login.googleapis.com" OR "drive.googleapis.com")
   ```

### Step 4: Configure Adapter

Use same Pub/Sub adapter as GCP Audit Logs example, with `platform: gcp`:

```yaml
sensor_type: pubsub
pubsub:
  sub_name: "workspace-logs-sub"
  project_name: "my-gcp-project"
  service_account_creds: "hive://secret/gcp-service-account"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "gcp"
    sensor_seed_key: "google-workspace"
```

---

## Okta System Logs

**Complete setup for Okta authentication and user events**

### Step 1: Create API Token

1. Sign in to Okta Admin Console
2. Go to Security > API
3. Click Tokens tab
4. Click "Create Token"
5. Name: `LimaCharlie Adapter`
6. Copy token (shown only once!)

### Step 2: Note Your Okta Domain

Your Okta URL: `https://company.okta.com` or `https://company.oktapreview.com`

### Step 3: Configure Adapter

**Cloud-to-Cloud (Recommended)**:

```yaml
sensor_type: okta
okta:
  apikey: "hive://secret/okta-api-token"
  url: "https://company.okta.com"
  polling_seconds: 60
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "json"
    sensor_seed_key: "okta-system-logs"
    hostname: "okta-logs"
    mapping:
      event_type_path: "eventType"
      event_time_path: "published"
      sensor_hostname_path: "client.device"
```

Create in LimaCharlie:
```bash
# Store API token
echo "YOUR_OKTA_TOKEN" | limacharlie hive set secret --key okta-api-token --data -

# Create cloud sensor
cat okta.yaml | limacharlie hive set cloud_sensor --key okta --data -
```

**On-Premises Binary**:

```bash
./lc-adapter okta \
  apikey=$OKTA_API_TOKEN \
  url=https://company.okta.com \
  polling_seconds=60 \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=json \
  client_options.sensor_seed_key=okta-logs
```

### Step 4: Verify

Query events:
```
event.eventType:*
```

Common event types: `user.session.start`, `user.authentication.sso`, `user.mfa.factor.activate`

---

## Microsoft 365 Audit Logs

**Complete setup for Exchange, SharePoint, Teams, OneDrive logs**

### Step 1: Enable Audit Logging

1. Go to Microsoft 365 Compliance Center
2. Audit > Search
3. Enable auditing if not already enabled
4. Wait 24 hours for initial setup

### Step 2: Create App Registration

1. Go to Azure Portal > App registrations
2. Click "New registration"
3. Name: `LimaCharlie M365 Adapter`
4. Supported account types: "Accounts in this organizational directory only"
5. Redirect URI: Leave blank
6. Register

### Step 3: Configure API Permissions

1. Go to app > API permissions
2. Add a permission > Office 365 Management APIs
3. Application permissions:
   - `ActivityFeed.Read`
   - `ActivityFeed.ReadDlp` (if using DLP logs)
4. Grant admin consent for organization

### Step 4: Create Client Secret

1. Go to app > Certificates & secrets
2. New client secret
3. Description: `LimaCharlie`
4. Expires: Choose duration
5. Copy secret value (shown only once!)

### Step 5: Note Required Values

- Tenant ID: Azure Portal > App registrations > Your app > Overview > Directory (tenant) ID
- Client ID: Overview > Application (client) ID
- Client Secret: From step 4

### Step 6: Configure Adapter

**Cloud-to-Cloud (Recommended)**:

```yaml
sensor_type: office365
office365:
  tenant_id: "hive://secret/o365-tenant-id"
  client_id: "hive://secret/o365-client-id"
  client_secret: "hive://secret/o365-client-secret"
  content_types:
    - "Audit.AzureActiveDirectory"
    - "Audit.Exchange"
    - "Audit.SharePoint"
    - "Audit.General"
    - "DLP.All"
  polling_seconds: 300
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "office365"
    sensor_seed_key: "ms-office365"
    hostname: "office365-audit"
    mapping:
      event_type_path: "Operation"
      event_time_path: "CreationTime"
```

Store credentials:
```bash
# Store secrets
echo "TENANT_ID" | limacharlie hive set secret --key o365-tenant-id --data -
echo "CLIENT_ID" | limacharlie hive set secret --key o365-client-id --data -
echo "CLIENT_SECRET" | limacharlie hive set secret --key o365-client-secret --data -

# Create cloud sensor
cat office365.yaml | limacharlie hive set cloud_sensor --key office365 --data -
```

### Step 7: Verify

Query events:
```
event.Workload:*
```

Common workloads: `Exchange`, `SharePoint`, `AzureActiveDirectory`, `OneDrive`

---

## Syslog Server (Advanced)

**Production-ready syslog server with TLS and parsing**

### Step 1: Generate TLS Certificates

```bash
# Generate CA
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -days 3650 -key ca-key.pem -out ca-cert.pem

# Generate server certificate
openssl genrsa -out server-key.pem 4096
openssl req -new -key server-key.pem -out server-csr.pem
openssl x509 -req -days 3650 -in server-csr.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem

# Set permissions
chmod 600 server-key.pem ca-key.pem
```

### Step 2: Configure Adapter

**TCP with TLS**:

```yaml
sensor_type: syslog
syslog:
  port: 6514
  iface: "0.0.0.0"
  is_udp: false
  ssl_cert: "/opt/certs/server-cert.pem"
  ssl_key: "/opt/certs/server-key.pem"
  mutual_tls_cert: "/opt/certs/ca-cert.pem"  # Optional: client cert verification
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "text"
    sensor_seed_key: "syslog-tls-server"
    hostname: "syslog-collector"
    mapping:
      parsing_grok:
        message: '^<%{INT:priority}>%{SYSLOGTIMESTAMP:timestamp}\s+%{HOSTNAME:hostname}\s+%{WORD:program}(?:\[%{INT:pid}\])?:\s+%{GREEDYDATA:message}'
      sensor_hostname_path: "hostname"
      event_type_path: "program"
```

### Step 3: Run as Docker Container

**Dockerfile**:
```dockerfile
FROM refractionpoint/lc-adapter:latest

# Copy certificates
COPY server-cert.pem /certs/
COPY server-key.pem /certs/
COPY ca-cert.pem /certs/

# Copy config
COPY syslog-config.yaml /config.yaml

CMD ["/config.yaml"]
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  lc-adapter-syslog:
    build: .
    ports:
      - "6514:6514"
    restart: unless-stopped
    environment:
      - LIMACHARLIE_OID=${OID}
      - LIMACHARLIE_KEY=${KEY}
```

### Step 4: Configure Syslog Clients

**rsyslog (Linux)**:

```bash
# /etc/rsyslog.d/50-limacharlie.conf
*.* @@(o)syslog-server:6514

# Restart rsyslog
systemctl restart rsyslog
```

**Firewall devices**: Configure remote syslog to `syslog-server:6514` with TLS

### Common Grok Patterns for Different Log Formats

**Standard Syslog (RFC 3164)**:
```yaml
parsing_grok:
  message: '^<%{INT:priority}>%{SYSLOGTIMESTAMP:timestamp}\s+%{HOSTNAME:hostname}\s+%{WORD:program}(?:\[%{INT:pid}\])?:\s+%{GREEDYDATA:message}'
```

**Syslog (RFC 5424)**:
```yaml
parsing_grok:
  message: '^<%{INT:priority}>%{INT:version}\s+%{TIMESTAMP_ISO8601:timestamp}\s+%{HOSTNAME:hostname}\s+%{WORD:program}\s+%{INT:pid}\s+%{WORD:msgid}\s+(?:\[%{DATA:structured_data}\])?\s+%{GREEDYDATA:message}'
```

**Cisco ASA**:
```yaml
parsing_grok:
  message: '^<%{INT:priority}>%{SYSLOGTIMESTAMP:timestamp} %{HOSTNAME:hostname} : %%{WORD:facility}-%{INT:severity}-%{WORD:mnemonic}: %{GREEDYDATA:message}'
```

**Palo Alto Networks**:
```yaml
parsing_grok:
  message: '%{DATA:future_use1},%{DATA:receive_time},%{DATA:serial_number},%{DATA:type},%{DATA:threat_content_type},%{DATA:future_use2},%{DATA:generated_time},%{IP:src_ip},%{IP:dst_ip},%{IP:nat_src_ip},%{IP:nat_dst_ip},%{GREEDYDATA:remaining}'
```

---

## Windows Event Logs

**Complete setup for domain controllers and servers**

### Step 1: Download Adapter

Download Windows binary: https://downloads.limacharlie.io/adapter/windows/64

### Step 2: Configure Adapter

**All Security, System, and Application logs**:

```powershell
.\lc_adapter.exe wel `
  evt_sources="Security:'*',System:'*',Application:'*'" `
  client_options.identity.oid=$env:OID `
  client_options.identity.installation_key=$env:KEY `
  client_options.platform=wel `
  client_options.sensor_seed_key=dc01-wel
```

**Filtered Security events only**:

```powershell
# Logon events, failures, and account changes
.\lc_adapter.exe wel `
  evt_sources="Security:'*[System[(EventID=4624 or EventID=4625 or EventID=4740 or EventID=4728 or EventID=4732)]]'" `
  client_options.identity.oid=$env:OID `
  client_options.identity.installation_key=$env:KEY `
  client_options.platform=wel `
  client_options.sensor_seed_key=dc01-security
```

### Step 3: Install as Windows Service

```powershell
# Install service
.\lc_adapter.exe -install:LimaCharlieWEL wel `
  evt_sources="Security:'*',System:'*',Application:'*'" `
  client_options.identity.oid=$env:OID `
  client_options.identity.installation_key=$env:KEY `
  client_options.platform=wel `
  client_options.sensor_seed_key=dc01-wel

# Start service
Start-Service LimaCharlieWEL

# Check status
Get-Service LimaCharlieWEL

# Uninstall
.\lc_adapter.exe -remove:LimaCharlieWEL
```

### Useful XPath Filters

**High-priority events only**:
```
Security:'*[System[(Level=1 or Level=2 or Level=3)]]'
```

**Authentication events**:
```
Security:'*[System[(EventID=4624 or EventID=4625 or EventID=4634 or EventID=4647 or EventID=4648)]]'
```

**Account changes**:
```
Security:'*[System[(EventID=4720 or EventID=4722 or EventID=4723 or EventID=4724 or EventID=4725 or EventID=4726 or EventID=4738 or EventID=4740)]]'
```

**Group changes**:
```
Security:'*[System[(EventID=4728 or EventID=4729 or EventID=4732 or EventID=4733 or EventID=4756 or EventID=4757)]]'
```

**PowerShell execution**:
```
Microsoft-Windows-PowerShell/Operational:'*[System[(EventID=4103 or EventID=4104)]]'
```

---

## Webhook Adapter

**Setup for custom integrations and third-party webhooks**

### Step 1: Create Webhook in LimaCharlie

```bash
# Create webhook configuration
cat <<EOF > webhook.yaml
sensor_type: webhook
webhook:
  secret: "your-hard-to-guess-secret-value"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "json"
    sensor_seed_key: "custom-webhook"
    hostname: "webhook-ingestion"
    mapping:
      event_type_path: "event_type"
      event_time_path: "timestamp"
EOF

# Store in Hive
cat webhook.yaml | limacharlie hive set cloud_sensor --key my-webhook --data -
```

### Step 2: Get Webhook URL

```bash
# Using Python SDK
python3 -c "import limacharlie; print(limacharlie.Manager().getOrgURLs()['hooks'])"

# Returns: https://HOOKDOMAIN.hook.limacharlie.io
# Your webhook URL: https://HOOKDOMAIN.hook.limacharlie.io/OID/my-webhook/your-hard-to-guess-secret-value
```

### Step 3: Test Webhook

**Single event**:
```bash
curl -X POST https://HOOKDOMAIN.hook.limacharlie.io/OID/my-webhook/SECRET \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "test_event",
    "timestamp": "2024-01-01T00:00:00Z",
    "user": "alice",
    "action": "login"
  }'
```

**Multiple events**:
```bash
curl -X POST https://HOOKDOMAIN.hook.limacharlie.io/OID/my-webhook/SECRET \
  -H "Content-Type: application/json" \
  -d '[
    {"event_type": "login", "user": "alice"},
    {"event_type": "logout", "user": "bob"}
  ]'
```

**NDJSON (newline-delimited)**:
```bash
curl -X POST https://HOOKDOMAIN.hook.limacharlie.io/OID/my-webhook/SECRET \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @- <<EOF
{"event_type": "login", "user": "alice"}
{"event_type": "logout", "user": "bob"}
{"event_type": "file_access", "user": "charlie"}
EOF
```

### Step 4: Use with Third-Party Services

**GitHub Webhooks**:
1. Go to GitHub repo > Settings > Webhooks
2. Payload URL: Your LimaCharlie webhook URL
3. Content type: application/json
4. Events: Choose events to monitor

**Slack Outgoing Webhooks**:
1. Go to Slack App settings
2. Outgoing Webhooks > Add webhook
3. URL: Your LimaCharlie webhook URL

**Custom Application**:
```python
import requests
import json

webhook_url = "https://HOOKDOMAIN.hook.limacharlie.io/OID/my-webhook/SECRET"

# Send event
event = {
    "event_type": "custom_event",
    "timestamp": "2024-01-01T00:00:00Z",
    "data": {"key": "value"}
}

response = requests.post(webhook_url, json=event)
print(response.status_code)
```

---

## Multi-Adapter Configuration

**Run multiple adapters in a single process**

### Example: Multiple Log Files

```yaml
# /etc/lc-adapter/config.yaml

file:
  file_path: "/var/log/nginx/access.log"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "text"
    sensor_seed_key: "nginx-access"
    mapping:
      parsing_grok:
        message: '%{IPORHOST:remote_addr} - %{USER:remote_user} \[%{HTTPDATE:timestamp}\] "%{WORD:method} %{DATA:request} HTTP/%{NUMBER:http_version}" %{NUMBER:status} %{NUMBER:body_bytes_sent} "%{DATA:http_referer}" "%{DATA:http_user_agent}"'

---

file:
  file_path: "/var/log/nginx/error.log"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "text"
    sensor_seed_key: "nginx-error"

---

file:
  file_path: "/var/log/app/*.json"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "json"
    sensor_seed_key: "app-logs"

---

syslog:
  port: 1514
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "text"
    sensor_seed_key: "syslog-server"
```

### Run with systemd

```ini
# /etc/systemd/system/lc-adapter.service
[Unit]
Description=LimaCharlie Multi-Adapter
After=network.target

[Service]
Type=simple
ExecStart=/opt/lc-adapter/lc-adapter /etc/lc-adapter/config.yaml
WorkingDirectory=/opt/lc-adapter
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lc-adapter

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable lc-adapter
sudo systemctl start lc-adapter
```

---

## Cloud-Managed Adapter Deployment

**Deploy adapters with cloud-managed configuration for easy updates**

### Step 1: Create Configuration in LimaCharlie

```bash
# Create adapter config
cat <<EOF > adapter-config.yaml
sensor_type: syslog
syslog:
  port: 1514
  iface: "0.0.0.0"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "text"
    sensor_seed_key: "managed-syslog"
    hostname: "syslog-collector"
    mapping:
      parsing_grok:
        message: '^<%{INT:priority}>%{SYSLOGTIMESTAMP:timestamp}\s+%{HOSTNAME:hostname}\s+%{WORD:program}:\s+%{GREEDYDATA:message}'
      sensor_hostname_path: "hostname"
      event_type_path: "program"
EOF

# Store in external_adapter Hive
cat adapter-config.yaml | limacharlie hive set external_adapter --key syslog-01 --data -
```

### Step 2: Get Configuration GUID

```bash
# Get the record
limacharlie hive get external_adapter --key syslog-01 --format json

# Look for "sys_mtd.guid" in output
# Example GUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Step 3: Deploy Adapter

```bash
# On the server where adapter will run
./lc-adapter cloud \
  conf_guid=a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  oid=your-oid
```

### Step 4: Update Configuration Remotely

```bash
# Edit configuration
cat <<EOF > adapter-config-updated.yaml
sensor_type: syslog
syslog:
  port: 1514
  iface: "0.0.0.0"
  # Added TLS support
  ssl_cert: "/opt/certs/server-cert.pem"
  ssl_key: "/opt/certs/server-key.pem"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "text"
    sensor_seed_key: "managed-syslog"
    hostname: "syslog-collector"
    mapping:
      parsing_grok:
        message: '^<%{INT:priority}>%{SYSLOGTIMESTAMP:timestamp}\s+%{HOSTNAME:hostname}\s+%{WORD:program}:\s+%{GREEDYDATA:message}'
      sensor_hostname_path: "hostname"
      event_type_path: "program"
EOF

# Update in Hive
cat adapter-config-updated.yaml | limacharlie hive set external_adapter --key syslog-01 --data -
```

Adapter will automatically pick up new configuration within ~1 minute. No SSH or restart needed!
