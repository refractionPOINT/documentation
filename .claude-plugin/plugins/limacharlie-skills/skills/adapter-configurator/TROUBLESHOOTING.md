# Adapter Troubleshooting Guide

Comprehensive troubleshooting guide for LimaCharlie adapter connectivity, data flow, and configuration issues.

## Quick Diagnostic Checklist

Before diving into specific issues, run through this checklist:

1. **Adapter Running?**
   - Check process is running: `ps aux | grep lc_adapter`
   - Check service status: `systemctl status lc-adapter`

2. **Network Connectivity?**
   - Can reach LimaCharlie: `curl -I https://api.limacharlie.io`
   - Check firewall rules for outbound HTTPS (port 443)

3. **Credentials Valid?**
   - OID correct? (Check LimaCharlie web app > Organization)
   - Installation Key active? (Check Installation Keys page)

4. **Sensor Visible?**
   - Go to LimaCharlie web app > Sensors
   - Look for sensor with matching `sensor_seed_key`
   - Check "Last Seen" timestamp

5. **Data Source Active?**
   - Is data actually being generated?
   - Can adapter access the data source?

---

## Connection Issues

### Adapter Not Connecting to LimaCharlie

**Symptoms**:
- Adapter logs show "usp-client connecting" but never "usp-client connected"
- Sensor doesn't appear in LimaCharlie web app
- "Last Seen" timestamp never updates

**Solution 1: Verify Credentials**

```bash
# Check OID is correct (look for typos)
echo $LIMACHARLIE_OID

# Verify Installation Key exists and is not deleted
# Go to LimaCharlie web app > Installation Keys
# Confirm the key you're using is listed
```

**Solution 2: Check Network Connectivity**

```bash
# Test connection to LimaCharlie API
curl -v https://api.limacharlie.io

# If behind proxy, set proxy environment variables
export HTTPS_PROXY=http://proxy.company.com:8080
export HTTP_PROXY=http://proxy.company.com:8080

# Test again
./lc-adapter ...
```

**Solution 3: Check Firewall Rules**

Ensure outbound connections allowed to:
- `*.limacharlie.io` on port 443 (HTTPS)
- `*.limacharlie.net` on port 443 (HTTPS)

**Solution 4: Enable Verbose Logging**

```bash
# Run adapter in foreground with full output
./lc-adapter syslog port=1514 ... 2>&1 | tee adapter.log

# Look for error messages:
# - "connection refused" = firewall/network issue
# - "authentication failed" = wrong OID or Installation Key
# - "certificate" errors = TLS/SSL issue (check system time)
```

**Solution 5: Check System Time**

```bash
# Verify system time is accurate (within 5 minutes)
date
timedatectl

# If wrong, sync time
sudo ntpdate pool.ntp.org
# or
sudo timedatectl set-ntp true
```

---

### Cloud Adapter Not Starting (Hive Configuration)

**Symptoms**:
- Created `cloud_sensor` in Hive but adapter not working
- No sensor appears in web app

**Solution 1: Verify Hive Record**

```bash
# Check record exists
limacharlie hive get cloud_sensor --key your-adapter-name

# Verify JSON/YAML is valid
limacharlie hive get cloud_sensor --key your-adapter-name --format json | jq .
```

**Solution 2: Check Required Fields**

Ensure all required fields are present:
```yaml
sensor_type: "adapter_type"  # Required
adapter_type:                # Required: config for this type
  field1: value1
  client_options:            # Required
    identity:                # Required
      oid: "..."            # Required
      installation_key: "..." # Required
    platform: "..."          # Required
    sensor_seed_key: "..."   # Required
```

**Solution 3: Wait for Activation**

Cloud adapters take 1-2 minutes to activate after creation. Check:
```bash
# Monitor sensors page
# Refresh after 2 minutes
# Look for new sensor with matching sensor_seed_key
```

---

## No Data Appearing

### Sensor Connected but No Events

**Symptoms**:
- Sensor shows in LimaCharlie with recent "Last Seen"
- No events when searching: `event.sensor_seed_key:your-adapter`
- Adapter logs show no errors

**Solution 1: Verify Data Source is Generating Data**

```bash
# For file adapter: Check file has new data
tail -f /var/log/app.log

# For syslog adapter: Send test message
echo "test message" | nc localhost 1514

# For S3 adapter: Check new objects in bucket
aws s3 ls s3://your-bucket/

# For cloud APIs: Check API has events
# Example for Okta:
curl -H "Authorization: SSWS $OKTA_TOKEN" \
  "https://company.okta.com/api/v1/logs?limit=10"
```

**Solution 2: Check Platform Type**

```bash
# Verify platform matches data format
# Wrong: platform: "text" for JSON data
# Right: platform: "json" for JSON data

# Common mistakes:
# - Using "json" for AWS CloudTrail (should be "aws")
# - Using "text" for structured logs (use "json" and parse later)
# - Using "wel" for non-Windows logs
```

**Solution 3: Review Parsing Configuration**

```bash
# If using grok parsing, test pattern
# Use online grok debugger: https://grokdebug.herokuapp.com

# Example log line:
# <14>Jan 1 12:00:00 server1 app[1234]: User logged in

# Test grok pattern:
# ^<%{INT:priority}>%{SYSLOGTIMESTAMP:timestamp}\s+%{HOSTNAME:hostname}\s+%{WORD:program}(?:\[%{INT:pid}\])?:\s+%{GREEDYDATA:message}

# If pattern doesn't match, events will be dropped
```

**Solution 4: Check Field Mapping**

```yaml
# Ensure mapped fields exist in your data
client_options:
  mapping:
    event_type_path: "eventType"  # Must exist in JSON
    event_time_path: "timestamp"   # Must exist in JSON

# Example JSON:
# {"eventType": "login", "timestamp": "2024-01-01T00:00:00Z"}

# Wrong mapping:
# event_type_path: "type"  # Field doesn't exist -> events dropped

# Right mapping:
# event_type_path: "eventType"  # Field exists -> events ingested
```

**Solution 5: Enable Debug Logging in Adapter**

```bash
# Run adapter with verbose output
./lc-adapter file file_path=/var/log/app.json ... 2>&1 | grep -E "(error|warn|processing)"

# Look for:
# - "failed to parse" = parsing issue
# - "no matching field" = mapping issue
# - "dropped event" = filtering issue
```

---

### Events Missing Fields

**Symptoms**:
- Events appear in LimaCharlie but missing expected fields
- Field extraction not working

**Solution 1: Verify Path Syntax**

```yaml
# Correct path syntax uses "/" for nested fields
sensor_hostname_path: "user/name"      # Correct
event_type_path: "metadata/eventType"  # Correct

# Wrong syntax:
sensor_hostname_path: "user.name"      # Wrong: uses dots
event_type_path: "/metadata/eventType" # Wrong: starts with /
```

**Solution 2: Check Field Exists in Source Data**

```bash
# For JSON files, inspect structure
cat /var/log/app.json | jq .

# Example JSON:
# {"user": {"name": "alice"}, "action": "login"}

# Correct paths:
# sensor_hostname_path: "user/name"   → Extracts "alice"
# event_type_path: "action"           → Extracts "login"
```

**Solution 3: Test Grok Extraction**

```bash
# If using grok, verify named captures match fields
# Pattern: %{PATTERN:field_name}

# Example:
parsing_grok:
  message: '%{IP:src_ip} %{WORD:action}'

# Input: "192.168.1.1 login"
# Creates fields: src_ip=192.168.1.1, action=login
```

**Solution 4: Verify Events After Ingestion**

```bash
# Query events in LimaCharlie
event.sensor_seed_key:your-adapter

# Check if fields are present
# If not, review mapping configuration
```

---

## Parsing Problems

### Grok Pattern Not Matching

**Symptoms**:
- Text logs not being parsed
- Events appear as single "message" field
- No structured fields extracted

**Solution 1: Test Grok Pattern Online**

Use https://grokdebug.herokuapp.com:

1. Paste sample log line in "Input" field
2. Enter grok pattern in "Pattern" field
3. Verify fields are extracted correctly

**Solution 2: Common Grok Mistakes**

```yaml
# Mistake 1: Using wrong timestamp pattern
# Log: 2024-01-01T12:00:00Z
parsing_grok:
  message: '%{SYSLOGTIMESTAMP:timestamp}'  # Wrong!
  # Should be:
  message: '%{TIMESTAMP_ISO8601:timestamp}'  # Correct

# Mistake 2: Missing anchors
# Pattern matches anywhere in line, not from start
parsing_grok:
  message: '%{IP:ip}'  # Matches IP anywhere
  # Better:
  message: '^%{IP:ip}'  # Matches IP at start

# Mistake 3: Greedy patterns too early
parsing_grok:
  message: '%{GREEDYDATA:message} %{IP:ip}'  # IP never captured!
  # GREEDYDATA consumes everything, including IP
  # Should be:
  message: '%{DATA:message} %{IP:ip}'  # DATA stops at whitespace
```

**Solution 3: Use Simpler Patterns First**

```yaml
# Start with basic pattern
parsing_grok:
  message: '%{GREEDYDATA:raw}'  # Captures everything

# Then add structure incrementally
parsing_grok:
  message: '%{TIMESTAMP_ISO8601:timestamp} %{GREEDYDATA:raw}'

# Finally, full pattern
parsing_grok:
  message: '%{TIMESTAMP_ISO8601:timestamp} %{IP:src_ip} %{WORD:action}'
```

**Solution 4: Common Log Format Patterns**

**Apache/Nginx Combined Log**:
```yaml
parsing_grok:
  message: '%{IPORHOST:remote_addr} - %{USER:remote_user} \[%{HTTPDATE:timestamp}\] "%{WORD:method} %{DATA:request} HTTP/%{NUMBER:http_version}" %{NUMBER:status} %{NUMBER:body_bytes_sent} "%{DATA:http_referer}" "%{DATA:http_user_agent}"'
```

**Standard Syslog**:
```yaml
parsing_grok:
  message: '^<%{INT:priority}>%{SYSLOGTIMESTAMP:timestamp}\s+%{HOSTNAME:hostname}\s+%{WORD:program}(?:\[%{INT:pid}\])?:\s+%{GREEDYDATA:message}'
```

**Custom Application Log**:
```yaml
# Log format: [2024-01-01 12:00:00] INFO: User alice logged in from 192.168.1.1
parsing_grok:
  message: '^\[%{TIMESTAMP_ISO8601:timestamp}\] %{LOGLEVEL:level}: User %{WORD:user} %{WORD:action} %{WORD:preposition} from %{IP:ip}'
```

---

### Regex Pattern Not Working

**Symptoms**:
- Using `parsing_re` instead of `parsing_grok`
- Pattern doesn't match expected data

**Solution 1: Use Named Groups**

```yaml
# Correct: Use (?P<name>pattern) for named groups
parsing_re: '(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<message>.*)'

# Wrong: Regular capture groups don't create fields
parsing_re: '(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) (.*)'
```

**Solution 2: Test Regex Online**

Use https://regex101.com:
1. Select "Golang" flavor (important!)
2. Paste sample log line
3. Enter regex pattern
4. Verify groups are captured

**Solution 3: Escape Special Characters**

```yaml
# Wrong: Unescaped dots match any character
parsing_re: '(?P<ip>\d+.\d+.\d+.\d+)'  # Matches 192x168x1x1 !

# Correct: Escape dots
parsing_re: '(?P<ip>\d+\.\d+\.\d+\.\d+)'  # Only matches 192.168.1.1
```

**Solution 4: Common Regex Patterns**

**IP Address**:
```yaml
parsing_re: '(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
```

**ISO Timestamp**:
```yaml
parsing_re: '(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)'
```

**Key-Value Pairs**:
```yaml
parsing_re: 'user=(?P<user>\w+) action=(?P<action>\w+) status=(?P<status>\w+)'
```

---

## Cloud Adapter Issues

### AWS S3 Adapter Problems

**Symptoms**:
- S3 adapter not finding objects
- Permission denied errors

**Solution 1: Verify IAM Permissions**

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
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

Test permissions:
```bash
# Test ListBucket
aws s3 ls s3://my-bucket/ --profile adapter-user

# Test GetObject
aws s3 cp s3://my-bucket/test.json - --profile adapter-user
```

**Solution 2: Check Bucket Region**

```yaml
# Specify region explicitly if auto-detection fails
s3:
  bucket_name: "my-bucket"
  region: "us-east-1"  # Add this
  access_key: "..."
  secret_key: "..."
```

**Solution 3: Verify Object Prefix**

```yaml
# If objects are in subdirectory
s3:
  bucket_name: "my-bucket"
  prefix: "AWSLogs/"  # Must match actual path
```

**Solution 4: Check Object Format**

```bash
# Download sample object
aws s3 cp s3://my-bucket/sample.json sample.json

# Verify it's valid JSON
jq . sample.json

# Check if it's gzipped CloudTrail
file sample.json
# If gzipped: adapter automatically decompresses
```

---

### AWS SQS Adapter Problems

**Symptoms**:
- SQS adapter not receiving messages
- Messages stuck in queue

**Solution 1: Verify IAM Permissions**

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
      "Resource": "arn:aws:sqs:us-east-1:123456789:my-queue"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::my-cloudtrail-bucket/*"
    }
  ]
}
```

**Solution 2: Check S3 Event Notifications**

1. Go to S3 bucket > Properties > Event notifications
2. Verify event notification exists pointing to SQS queue
3. Test by uploading file to bucket
4. Check queue receives message:

```bash
aws sqs receive-message --queue-url https://sqs.us-east-1.amazonaws.com/123456789/my-queue
```

**Solution 3: Verify Queue Visibility Timeout**

- Visibility timeout should be >= 60 seconds
- Allows adapter time to process messages
- If too short, messages reappear before processing completes

---

### Azure Event Hub Problems

**Symptoms**:
- Azure Event Hub adapter not receiving events
- Connection string errors

**Solution 1: Verify Connection String Format**

Connection string MUST include `EntityPath=hub-name`:

```
Endpoint=sb://namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=KEY;EntityPath=hub-name
```

**Solution 2: Check Event Hub Permissions**

1. Go to Event Hub namespace > Shared access policies
2. Verify key has "Listen" permission
3. Use correct key (not namespace-level key without EntityPath)

**Solution 3: Verify Diagnostic Settings**

1. Go to source resource (e.g., Entra ID)
2. Diagnostic settings > Check your setting
3. Verify:
   - Log categories are selected
   - Destination is "Stream to an event hub"
   - Correct namespace and hub selected

**Solution 4: Test Event Hub Directly**

Use Azure CLI:
```bash
# Check events are flowing to hub
az eventhubs eventhub show \
  --resource-group my-rg \
  --namespace-name my-namespace \
  --name my-hub \
  --query messageRetentionInDays
```

---

### GCP Pub/Sub Problems

**Symptoms**:
- Pub/Sub adapter not receiving messages
- Authentication failures

**Solution 1: Verify Service Account Permissions**

```bash
# Check service account has correct role
gcloud projects get-iam-policy my-project \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:adapter@my-project.iam.gserviceaccount.com"

# Should show: roles/pubsub.subscriber
```

Grant permission:
```bash
gcloud pubsub subscriptions add-iam-policy-binding my-subscription \
  --member="serviceAccount:adapter@my-project.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber"
```

**Solution 2: Check Subscription Exists**

```bash
# List subscriptions
gcloud pubsub subscriptions list --project=my-project

# Describe subscription
gcloud pubsub subscriptions describe my-subscription --project=my-project
```

**Solution 3: Verify Log Sink**

```bash
# List log sinks
gcloud logging sinks list --project=my-project

# Describe sink
gcloud logging sinks describe my-sink --project=my-project

# Verify destination is your Pub/Sub topic
```

**Solution 4: Test Pub/Sub Flow**

```bash
# Pull messages manually
gcloud pubsub subscriptions pull my-subscription --limit=5 --project=my-project

# If no messages:
# - Check log sink filter
# - Verify logs are being generated
# - Check topic exists
```

---

### Okta Adapter Problems

**Symptoms**:
- Okta adapter not fetching logs
- Authentication errors

**Solution 1: Verify API Token**

```bash
# Test token manually
curl -H "Authorization: SSWS $OKTA_TOKEN" \
  "https://company.okta.com/api/v1/logs?limit=1"

# Should return JSON with log events
# If error, token is invalid or expired
```

**Solution 2: Check Token Permissions**

1. Go to Okta Admin Console
2. Security > API > Tokens
3. Find your token
4. Verify it has "Read-only" permission
5. Okta API tokens don't expire but can be revoked

**Solution 3: Verify Okta Domain**

```yaml
# Use full Okta domain
okta:
  url: "https://company.okta.com"  # Correct
  # Not: "company.okta.com"          # Wrong: missing https://
  # Not: "https://company-admin.okta.com"  # Wrong: admin URL
```

**Solution 4: Check Rate Limits**

Okta rate limits:
- 1000 requests per minute (default)
- Adapter polls every 60 seconds by default

If rate limited:
```yaml
okta:
  polling_seconds: 120  # Increase polling interval
```

---

### Microsoft 365 Adapter Problems

**Symptoms**:
- Office 365 adapter not fetching audit logs
- Authentication errors

**Solution 1: Verify App Registration Permissions**

1. Go to Azure Portal > App registrations > Your app
2. API permissions:
   - Office 365 Management APIs
   - Application permissions: `ActivityFeed.Read`, `ActivityFeed.ReadDlp`
   - Status: Granted admin consent (green checkmark)

**Solution 2: Check Client Secret**

1. Go to app > Certificates & secrets
2. Verify secret hasn't expired
3. Create new secret if expired
4. Update adapter configuration with new secret

**Solution 3: Verify Tenant ID**

```bash
# Get tenant ID from Azure Portal
# Azure Active Directory > Overview > Tenant ID

# Or via CLI
az account show --query tenantId -o tsv
```

**Solution 4: Check Audit Logging Enabled**

1. Go to Microsoft 365 Compliance Center
2. Audit > Search
3. Verify auditing is enabled
4. Initial setup takes 24 hours

**Solution 5: Test API Manually**

```bash
# Get access token
curl -X POST "https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/token" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "scope=https://manage.office.com/.default" \
  -d "grant_type=client_credentials"

# Use token to query audit logs
curl -H "Authorization: Bearer $TOKEN" \
  "https://manage.office.com/api/v1.0/$TENANT_ID/activity/feed/subscriptions/list"
```

---

## Performance Issues

### High Memory Usage

**Symptoms**:
- Adapter process using excessive memory
- System running out of memory
- OOM killer terminating adapter

**Solution 1: Reduce Batch Size**

For high-volume adapters, consider multiple instances:

```yaml
# Instead of one adapter for all logs
file:
  file_path: "/var/log/*.log"

# Use separate adapters per file type
file:
  file_path: "/var/log/app1.log"
---
file:
  file_path: "/var/log/app2.log"
---
file:
  file_path: "/var/log/app3.log"
```

**Solution 2: Filter at Source**

```yaml
# For Windows Event Logs, use XPath filters
wel:
  evt_sources: "Security:'*[System[(EventID=4624 or EventID=4625)]]'"
  # Instead of: "Security:'*'"
```

**Solution 3: Drop Unnecessary Fields**

```yaml
client_options:
  mapping:
    drop_fields:
      - "large_field"
      - "unnecessary_data"
      - "verbose_logs"
```

---

### High CPU Usage

**Symptoms**:
- Adapter using 100% CPU
- System slow or unresponsive

**Solution 1: Simplify Parsing**

```yaml
# Complex grok patterns are CPU-intensive
# Use simpler patterns or parse less data

# Instead of:
parsing_grok:
  message: '%{COMPLEX_PATTERN} %{MORE_PATTERNS} %{EVEN_MORE}'

# Use:
parsing_grok:
  message: '%{SIMPLE_PATTERN}'
```

**Solution 2: Reduce Polling Frequency**

```yaml
# Increase polling interval for API adapters
okta:
  polling_seconds: 300  # Poll every 5 minutes instead of 1
```

**Solution 3: Use Multiple Adapters**

Distribute load across multiple adapter processes:
- One adapter per data source
- Run on different systems if possible

---

### Events Delayed

**Symptoms**:
- Events appear in LimaCharlie minutes/hours late
- Event timestamps show old times

**Solution 1: Check Polling Interval**

```yaml
# Reduce polling interval for faster ingestion
s3:
  polling_seconds: 30  # Default is 60
```

**Solution 2: Use Real-Time Methods**

- Use SQS instead of S3 polling for AWS CloudTrail
- Use Event Hub instead of polling for Azure
- Use Pub/Sub instead of Cloud Storage for GCP

**Solution 3: Check System Resources**

```bash
# Check if system is overloaded
top
# Look for high CPU or memory usage

# Check disk I/O
iostat -x 1

# If system is overloaded, scale up or distribute load
```

---

## Syslog-Specific Issues

### Syslog Server Not Receiving Logs

**Symptoms**:
- Syslog adapter running but no logs received
- Remote systems can't connect

**Solution 1: Verify Port and Interface**

```yaml
syslog:
  port: 1514
  iface: "0.0.0.0"  # Listen on all interfaces

# Test if port is open
netstat -tuln | grep 1514
# or
ss -tuln | grep 1514
```

**Solution 2: Check Firewall**

```bash
# Allow incoming connections
sudo ufw allow 1514/tcp
sudo ufw allow 1514/udp

# Or for iptables
sudo iptables -A INPUT -p tcp --dport 1514 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 1514 -j ACCEPT
```

**Solution 3: Test Connection**

```bash
# Test TCP syslog
echo "test message" | nc localhost 1514

# Test UDP syslog
echo "test message" | nc -u localhost 1514

# From remote system
echo "test message" | nc syslog-server 1514
```

**Solution 4: Check Syslog Format**

```bash
# Standard syslog format:
<priority>timestamp hostname program[pid]: message

# Example:
<14>Jan 1 12:00:00 server1 app[1234]: Test message

# Send test message:
echo "<14>$(date '+%b %d %H:%M:%S') $(hostname) test[$$]: Test message" | nc localhost 1514
```

---

### TLS Syslog Connection Failures

**Symptoms**:
- TLS syslog clients can't connect
- Certificate errors

**Solution 1: Verify Certificate Files**

```bash
# Check certificate files exist and are readable
ls -l /path/to/server-cert.pem
ls -l /path/to/server-key.pem

# Verify certificate is valid
openssl x509 -in /path/to/server-cert.pem -text -noout

# Check certificate hasn't expired
openssl x509 -in /path/to/server-cert.pem -noout -enddate
```

**Solution 2: Test TLS Connection**

```bash
# Test with openssl
openssl s_client -connect localhost:6514 -CAfile /path/to/ca-cert.pem

# Should show certificate details and "Verify return code: 0 (ok)"
```

**Solution 3: Check Certificate Chain**

```bash
# Verify certificate chain
openssl verify -CAfile /path/to/ca-cert.pem /path/to/server-cert.pem

# Should return: server-cert.pem: OK
```

---

## Windows Event Log Issues

### WEL Adapter Not Reading Events

**Symptoms**:
- Windows Event Log adapter not ingesting events
- Permission denied errors

**Solution 1: Run as Administrator**

```powershell
# Run PowerShell as Administrator
# Then run adapter
.\lc_adapter.exe wel evt_sources="Security:'*'" ...
```

**Solution 2: Verify Event Log Service**

```powershell
# Check Windows Event Log service is running
Get-Service EventLog

# If stopped, start it
Start-Service EventLog
```

**Solution 3: Check XPath Filter**

```powershell
# Test XPath query in Event Viewer
# Open Event Viewer > Windows Logs > Security
# Right-click > Filter Current Log
# XML tab > Edit query manually
# Enter your XPath query

# Example:
*[System[(EventID=4624 or EventID=4625)]]
```

**Solution 4: Check Log Permissions**

```powershell
# Grant read access to Event Logs
wevtutil gl Security

# If access denied, run as SYSTEM
# Or add user to Event Log Readers group
net localgroup "Event Log Readers" YourUser /add
```

---

### XPath Filters Not Working

**Symptoms**:
- XPath filter doesn't match expected events
- Too many or too few events

**Solution 1: Test XPath in Event Viewer**

1. Open Event Viewer
2. Navigate to log (e.g., Security)
3. Right-click > Filter Current Log
4. XML tab > Edit query manually
5. Enter XPath query
6. Apply and verify events match

**Solution 2: Common XPath Examples**

**All events**:
```
*
```

**Specific event IDs**:
```
*[System[(EventID=4624 or EventID=4625 or EventID=4634)]]
```

**By severity level**:
```
*[System[(Level=1 or Level=2 or Level=3)]]
```
- Level 1 = Critical
- Level 2 = Error
- Level 3 = Warning

**By time range**:
```
*[System[TimeCreated[timediff(@SystemTime) <= 86400000]]]
```
(Last 24 hours)

**By provider**:
```
*[System[Provider[@Name='Microsoft-Windows-Security-Auditing']]]
```

---

## General Debugging Techniques

### Enable Verbose Adapter Logging

```bash
# Run adapter in foreground with full output
./lc-adapter [adapter_type] ... 2>&1 | tee adapter.log

# On Windows
.\lc_adapter.exe [adapter_type] ... 2>&1 | Tee-Object adapter.log
```

Look for:
- Connection status: "usp-client connected"
- Event processing: "processing event"
- Errors: "error", "failed", "denied"

---

### Check Adapter Version

```bash
# Check adapter binary version
./lc-adapter --version

# Update to latest version
wget https://downloads.limacharlie.io/adapter/linux/64 -O lc-adapter
chmod +x lc-adapter
```

---

### Test with Simple Configuration

Start with minimal configuration to isolate issues:

```bash
# Simplest possible test: STDIN
echo '{"test": "event"}' | ./lc-adapter stdin \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=json \
  client_options.sensor_seed_key=test

# If this works, credentials are valid
# Then test your actual adapter configuration
```

---

### Monitor Adapter Health

```bash
# Enable healthcheck endpoint
./lc-adapter [adapter_type] ... healthcheck=8080 &

# Check health
curl http://localhost:8080/health

# Response:
# {"status": "ok", "connected": true}
```

---

### Review LimaCharlie Sensor Timeline

1. Go to LimaCharlie web app
2. Sensors > Find your adapter sensor
3. Click sensor name
4. View Timeline tab
5. Look for:
   - Connection events
   - Error messages
   - Event samples

---

## Getting Help

If none of these solutions resolve your issue:

1. **Collect Information**:
   ```bash
   # Adapter configuration (sanitized)
   cat config.yaml

   # Adapter logs
   ./lc-adapter ... 2>&1 | tee adapter.log

   # System information
   uname -a

   # Network connectivity
   curl -v https://api.limacharlie.io
   ```

2. **Contact Support**:
   - Email: support@limacharlie.io
   - Community Slack: https://slack.limacharlie.io
   - Include:
     - Adapter type and version
     - Sanitized configuration
     - Relevant log excerpts
     - Error messages
     - Steps to reproduce

3. **Check Documentation**:
   - Official docs: https://docs.limacharlie.io/docs/adapter-usage
   - Adapter downloads: https://docs.limacharlie.io/docs/adapter-deployment
   - API reference: https://docs.limacharlie.io/api
