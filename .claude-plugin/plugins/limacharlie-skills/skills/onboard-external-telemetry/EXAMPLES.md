# External Telemetry Onboarding Examples

> **Note**: These are complete end-to-end walkthroughs showing every step at once. When using the onboard-external-telemetry skill interactively, you'll be guided through these steps **one at a time** with questions and confirmations at each stage. You won't see this entire document - instead, you'll only see the specific steps relevant to your chosen data source as we progress through the conversation.

This document provides complete, step-by-step walkthroughs for onboarding the most common external data sources to LimaCharlie. Each example takes you from zero to fully operational, with exact commands and links to vendor documentation.

## Table of Contents

1. [AWS CloudTrail via S3](#example-1-aws-cloudtrail-via-s3)
2. [Microsoft 365 Audit Logs](#example-2-microsoft-365-audit-logs)
3. [Okta System Logs](#example-3-okta-system-logs)
4. [Azure Event Hub](#example-4-azure-event-hub)
5. [CrowdStrike Falcon Cloud](#example-5-crowdstrike-falcon-cloud)
6. [Firewall Syslog (On-Prem)](#example-6-firewall-syslog-on-prem)

---

## Example 1: AWS CloudTrail via S3

This walkthrough shows how to ingest AWS CloudTrail logs from an S3 bucket.

### What You'll Accomplish
- Configure AWS to send CloudTrail logs to an S3 bucket
- Create an IAM user with S3 read permissions
- Set up a cloud-to-cloud adapter in LimaCharlie
- Validate that CloudTrail events are flowing

### Prerequisites Checklist
- [ ] AWS account with admin access
- [ ] CloudTrail already enabled and logging to S3 (or I'll show you how)
- [ ] LimaCharlie organization set up
- [ ] LimaCharlie MCP server installed locally

### Step 1: Enable CloudTrail (if not already enabled)

1. Go to AWS Console → **CloudTrail** → **Trails**
2. If no trail exists, click **Create trail**
3. Enter a trail name (e.g., `organization-trail`)
4. Create a new S3 bucket or select existing (note the bucket name)
5. Leave encryption settings as default
6. Click **Next** → **Create trail**

**Result**: CloudTrail is now logging all AWS API calls to your S3 bucket

### Step 2: Create IAM User for LimaCharlie

We need credentials for LimaCharlie to read from the S3 bucket.

1. Go to AWS Console → **IAM** → **Users** → **Create user**
2. Username: `limacharlie-cloudtrail-reader`
3. Access type: **Access key - Programmatic access**
4. Click **Next**

### Step 3: Attach S3 Read Permissions

1. Click **Attach policies directly**
2. Click **Create policy** (opens new tab)
3. Select **JSON** tab and paste:

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
        "arn:aws:s3:::YOUR_BUCKET_NAME/*",
        "arn:aws:s3:::YOUR_BUCKET_NAME"
      ]
    }
  ]
}
```

4. Replace `YOUR_BUCKET_NAME` with your actual S3 bucket name
5. Name the policy `LimaCharlie-S3-CloudTrail-Read`
6. Click **Create policy**
7. Return to user creation tab, refresh policies, select your new policy
8. Click **Next** → **Create user**

### Step 4: Get Access Keys

1. Click on the newly created user
2. Go to **Security credentials** tab
3. Click **Create access key**
4. Select **Third-party service**
5. Click **Next** → **Create access key**
6. **Copy both the Access Key ID and Secret Access Key** (you can't retrieve the secret later)

### Step 5: Gather Your Information

You now have everything needed:

- **S3 Bucket Name**: (from CloudTrail configuration)
- **AWS Access Key ID**: (from Step 4)
- **AWS Secret Access Key**: (from Step 4)
- **LimaCharlie Organization ID**: (run `limacharlie organization info` via MCP)

### Step 6: Create Installation Key

I'll create this via MCP:

```bash
limacharlie installation_key create \
  --description "AWS CloudTrail S3 Adapter" \
  --tags "aws,cloudtrail,s3"
```

**Expected output**:
```
Created installation key:
IID: 12345678-1234-1234-1234-123456789abc
Installation Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Copy the **Installation Key** value.

### Step 7: Create Adapter Configuration

Create a file `aws-cloudtrail-adapter.yaml`:

```yaml
s3:
  client_options:
    hostname: aws-cloudtrail-logs
    identity:
      installation_key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # From Step 6
      oid: 8cbe27f4-bfa1-4afb-ba19-138cd51389cd              # Your OID
    platform: aws
    sensor_seed_key: aws-cloudtrail-production
  bucket_name: my-organization-cloudtrail-logs  # Your S3 bucket
  secret_key: YOUR_SECRET_ACCESS_KEY            # From Step 4
  access_key: YOUR_ACCESS_KEY_ID                # From Step 4
```

### Step 8: Deploy the Adapter

Via MCP:

```bash
limacharlie adapter create --config aws-cloudtrail-adapter.yaml
```

**Expected output**:
```
Adapter created successfully
Sensor ID: abcd1234-5678-90ef-ghij-klmnopqrstuv
Status: connecting...
```

### Step 9: Validate Data Flow

Wait 2-3 minutes for initial connection, then check:

```bash
# Check if sensor is online
limacharlie sensor list --filter "hostname:aws-cloudtrail-logs"

# View recent events
limacharlie events query --sensor-id abcd1234-5678-90ef-ghij-klmnopqrstuv --limit 10
```

**Expected**: You should see CloudTrail events with event types like `AssumeRole`, `PutObject`, `DescribeInstances`, etc.

### Verification Checklist
- [ ] Sensor appears in `limacharlie sensor list`
- [ ] Sensor status is "online" or "active"
- [ ] Events are appearing in the timeline
- [ ] Event types match AWS CloudTrail actions
- [ ] No errors in sensor logs

### Common Issues

**"Access Denied" errors**:
- Verify IAM policy includes both `s3:GetObject` and `s3:ListBucket`
- Check bucket name is exact (case-sensitive)
- Confirm ARN in policy matches your bucket

**No events appearing**:
- CloudTrail has a 5-15 minute delay from action to S3 delivery
- Check CloudTrail is actually enabled and logging
- Verify bucket has recent log files

---

## Example 2: Microsoft 365 Audit Logs

This walkthrough connects Microsoft 365 (Office 365) audit logs via the Management Activity API.

### What You'll Accomplish
- Create an Azure App Registration
- Configure API permissions for Office 365 Management API
- Generate a client secret
- Set up cloud-to-cloud M365 adapter

### Prerequisites Checklist
- [ ] Microsoft 365 subscription with admin access
- [ ] Azure AD/Entra ID admin permissions
- [ ] Audit logging enabled in M365 (usually default)
- [ ] LimaCharlie MCP installed

### Step 1: Create Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** (or **Microsoft Entra ID**)
3. Select **App registrations** → **New registration**
4. Enter a name: `LimaCharlie-M365-Audit`
5. Supported account types: **Accounts in this organizational directory only**
6. Redirect URI: Leave blank
7. Click **Register**

**Result**: You'll see the app's Overview page with Tenant ID and Client ID

### Step 2: Copy Essential IDs

From the Overview page, copy these values:

- **Tenant ID** (also called Directory ID)
- **Client ID** (also called Application ID)
- **Publisher ID** (for single-tenant apps, this equals Tenant ID)

### Step 3: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Description: `LimaCharlie Adapter Secret`
4. Expires: 24 months (or per your security policy)
5. Click **Add**
6. **IMMEDIATELY COPY THE SECRET VALUE** - you can only see it once

### Step 4: Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Office 365 Management APIs**
4. Select **Application permissions** (not Delegated)
5. Add these permissions:
   - `ActivityFeed.Read`
   - `ActivityFeed.ReadDlp` (if you want DLP events)
6. Click **Add permissions**

### Step 5: Grant Admin Consent

**Critical**: The permissions won't work until admin consent is granted.

1. Still in **API permissions** page
2. Click **Grant admin consent for [Your Organization]**
3. Confirm by clicking **Yes**
4. Verify status shows green checkmarks

### Step 6: Get Your Domain

Your M365 domain is usually: `yourcompany.onmicrosoft.com`

To find it:
1. Go to [Microsoft 365 Admin Center](https://admin.microsoft.com)
2. Check the header or go to **Settings** → **Domains**

### Step 7: Gather Your Information

You now have:

- **Domain**: yourcompany.onmicrosoft.com
- **Tenant ID**: (from Step 2)
- **Publisher ID**: (same as Tenant ID for single-tenant)
- **Client ID**: (from Step 2)
- **Client Secret**: (from Step 3)
- **Endpoint**: `enterprise` (use `gcc-gov` for GCC, `gcc-high-gov` for GCC High)

### Step 8: Create Installation Key

```bash
limacharlie installation_key create \
  --description "Microsoft 365 Audit Adapter" \
  --tags "m365,office365,audit"
```

Copy the generated Installation Key.

### Step 9: Create Adapter Configuration

Create file `m365-audit-adapter.yaml`:

```yaml
office365:
  domain: yourcompany.onmicrosoft.com
  tenant_id: 12345678-1234-1234-1234-123456789abc
  publisher_id: 12345678-1234-1234-1234-123456789abc  # Usually same as tenant_id
  client_id: 87654321-4321-4321-4321-cba987654321
  client_secret: abc123~VERY_SECRET_VALUE_HERE~xyz789
  endpoint: enterprise
  content_types:
    - Audit.AzureActiveDirectory
    - Audit.Exchange
    - Audit.SharePoint
    - Audit.General
    - DLP.All
  client_options:
    identity:
      oid: YOUR_LIMACHARLIE_ORG_ID
      installation_key: YOUR_INSTALLATION_KEY_FROM_STEP_8
    hostname: ms-o365-adapter
    platform: office365
    sensor_seed_key: office365-audit-production
    mapping:
      sensor_hostname_path: ClientIP
      event_type_path: Operation
      event_time_path: CreationTime
```

### Step 10: Deploy the Adapter

```bash
limacharlie adapter create --config m365-audit-adapter.yaml
```

### Step 11: Validate Data Flow

Wait 3-5 minutes (M365 API has initial latency), then:

```bash
# Check sensor status
limacharlie sensor list --filter "hostname:ms-o365-adapter"

# Query recent events
limacharlie events query --sensor-id <SENSOR_ID> --limit 20
```

**Expected events**: `UserLoggedIn`, `FileAccessed`, `MailItemsAccessed`, `FileDeleted`, etc.

### Verification Checklist
- [ ] App registration has admin consent granted
- [ ] Sensor shows as online
- [ ] Events are arriving (may take 5-10 minutes initially)
- [ ] Multiple content types are represented

### Common Issues

**"Unauthorized" or "Forbidden" errors**:
- Verify admin consent was granted (green checkmarks in API permissions)
- Ensure application permissions (not delegated) were selected
- Check client secret hasn't expired

**No events appearing**:
- M365 audit logging must be enabled (check M365 Admin Center → Audit)
- Initial subscription can take up to 12 hours to activate
- Try generating activity (login, access a file) and wait 10-15 minutes

---

## Example 3: Okta System Logs

Connect Okta identity and authentication logs to LimaCharlie.

### What You'll Accomplish
- Create an Okta API token
- Configure Okta system log adapter
- Monitor authentication and authorization events

### Prerequisites Checklist
- [ ] Okta administrator access
- [ ] Okta URL (e.g., dev-123456.okta.com or yourcompany.okta.com)
- [ ] LimaCharlie MCP installed

### Step 1: Create Okta API Token

1. Log in to your Okta Admin Console
2. Go to **Security** → **API**
3. Click **Create Token** (in the Tokens tab)
4. Name: `LimaCharlie System Log Reader`
5. Click **Create Token**
6. **COPY THE TOKEN VALUE IMMEDIATELY** - you can only see it once
7. Click **OK, got it**

**Official docs**: https://developer.okta.com/docs/guides/create-an-api-token/

### Step 2: Get Your Okta URL

Your Okta URL is the domain you use to access Okta admin:
- Format: `https://your-domain.okta.com`
- Example: `https://dev-123456.okta.com`

You can find it in the browser when logged into Okta admin.

### Step 3: Gather Your Information

You now have:

- **Okta URL**: https://your-domain.okta.com
- **API Token**: 00ABC...XYZ (from Step 1)

### Step 4: Create Installation Key

```bash
limacharlie installation_key create \
  --description "Okta System Logs Adapter" \
  --tags "okta,identity,auth"
```

Copy the Installation Key.

### Step 5: Create Adapter Configuration

Create file `okta-adapter.yaml`:

```yaml
okta:
  apikey: 00ABC1234567890DEFGHIJKLMNOPQRSTUVWXYZ
  url: https://your-company.okta.com
  client_options:
    identity:
      oid: YOUR_LIMACHARLIE_ORG_ID
      installation_key: YOUR_INSTALLATION_KEY
    hostname: okta-systemlog-adapter
    platform: json
    sensor_seed_key: okta-system-logs-production
    mapping:
      sensor_hostname_path: client.device
      event_type_path: eventType
      event_time_path: published
```

### Step 6: Deploy the Adapter

```bash
limacharlie adapter create --config okta-adapter.yaml
```

### Step 7: Validate Data Flow

```bash
# Check sensor
limacharlie sensor list --filter "hostname:okta-systemlog-adapter"

# View events
limacharlie events query --sensor-id <SENSOR_ID> --limit 10
```

**Expected events**: `user.authentication.sso`, `user.session.start`, `policy.evaluate_sign_on`, etc.

### Verification Checklist
- [ ] Sensor is online
- [ ] Events show authentication activity
- [ ] Event types match Okta system log format
- [ ] Client IP and user information are populated

### Common Issues

**"Invalid token" errors**:
- API token may have been deactivated - create a new one
- Check for copy/paste errors (no extra spaces)

**Rate limiting**:
- Okta API has rate limits (600 requests/minute typically)
- Adapter automatically handles this with backoff

**Official Okta System Log API docs**: https://developer.okta.com/docs/reference/api/system-log/

---

## Example 4: Azure Event Hub

Connect Azure Event Hub for streaming Azure Monitor, Entra ID, or Microsoft Defender logs.

### What You'll Accomplish
- Create an Azure Event Hub namespace and hub
- Configure Azure diagnostic settings to stream logs
- Connect LimaCharlie to the Event Hub

### Prerequisites Checklist
- [ ] Azure subscription with Contributor access
- [ ] Logs/services you want to collect (Azure Monitor, Entra ID, etc.)
- [ ] LimaCharlie MCP installed

### Step 1: Create Event Hub Namespace

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **Event Hubs** → **Create**
3. **Basics**:
   - Resource group: Create new or select existing
   - Namespace name: `limacharlie-logs-hub`
   - Location: Select region nearest you
   - Pricing tier: **Standard** (supports >1 consumer group)
4. Click **Review + create** → **Create**

Wait 2-3 minutes for deployment.

### Step 2: Create Event Hub

1. Open your new Event Hub namespace
2. Click **+ Event Hub**
3. Name: `azure-security-logs`
4. Partition count: 2 (default)
5. Click **Create**

### Step 3: Get Connection String

1. In Event Hub namespace, go to **Shared access policies**
2. Click **RootManageSharedAccessKey** (or create a new policy with Listen permission)
3. Click **Copy** for **Connection string–primary key**
4. **Important**: The connection string must include `EntityPath=azure-security-logs` at the end
   - If it doesn't, manually append: `;EntityPath=azure-security-logs`

**Full connection string format**:
```
Endpoint=sb://limacharlie-logs-hub.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=ABC123...XYZ789=;EntityPath=azure-security-logs
```

### Step 4: Configure Diagnostic Settings (Example: Azure Monitor)

To stream Azure Activity Logs to Event Hub:

1. Go to **Monitor** → **Activity log**
2. Click **Export Activity Logs**
3. Click **+ Add diagnostic setting**
4. **Diagnostic setting name**: `stream-to-limacharlie`
5. Check the log categories you want (e.g., Administrative, Security, Alert)
6. Check **Stream to an event hub**
7. Select your subscription, Event Hub namespace, and hub name
8. Click **Save**

Repeat this for other Azure services (Entra ID, Defender, etc.).

### Step 5: Create Installation Key

```bash
limacharlie installation_key create \
  --description "Azure Event Hub Adapter" \
  --tags "azure,eventhub,monitor"
```

### Step 6: Create Adapter Configuration

Create file `azure-eventhub-adapter.yaml`:

```yaml
azure_event_hub:
  connection_string: "Endpoint=sb://limacharlie-logs-hub.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=YOUR_KEY_HERE;EntityPath=azure-security-logs"
  client_options:
    identity:
      oid: YOUR_LIMACHARLIE_ORG_ID
      installation_key: YOUR_INSTALLATION_KEY
    hostname: azure-eventhub-adapter
    platform: azure_monitor  # or json, azure_ad, msdefender
    sensor_seed_key: azure-eventhub-production
```

**Platform options**:
- `azure_monitor` - Azure Monitor/Activity logs
- `azure_ad` - Azure Active Directory/Entra ID logs
- `msdefender` - Microsoft Defender alerts
- `json` - Generic JSON if unsure

### Step 7: Deploy the Adapter

```bash
limacharlie adapter create --config azure-eventhub-adapter.yaml
```

### Step 8: Validate Data Flow

Generate some Azure activity (create a resource, restart a VM), then:

```bash
limacharlie events query --sensor-id <SENSOR_ID> --limit 10
```

### Verification Checklist
- [ ] Event Hub shows incoming messages (check Metrics in Azure portal)
- [ ] LimaCharlie sensor is online
- [ ] Events match the log types you configured

### Common Issues

**Missing `EntityPath` in connection string**:
- Manually append `;EntityPath=YOUR_HUB_NAME` to the connection string

**No events flowing**:
- Verify diagnostic settings are saved and active
- Generate test activity in Azure
- Check Event Hub metrics show incoming messages

**Official docs**: https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-create

---

## Example 5: CrowdStrike Falcon Cloud

Stream CrowdStrike Falcon EDR events and detections to LimaCharlie.

### What You'll Accomplish
- Create CrowdStrike API credentials
- Configure Falcon event streaming
- Monitor EDR detections in LimaCharlie

### Prerequisites Checklist
- [ ] CrowdStrike Falcon subscription
- [ ] CrowdStrike admin access to create API clients
- [ ] LimaCharlie MCP installed

### Step 1: Create Falcon API Client

1. Log in to [CrowdStrike Falcon Console](https://falcon.crowdstrike.com)
2. Go to **Support and resources** → **API Clients and Keys**
3. Click **Create API client**
4. **Client Name**: `LimaCharlie Event Streaming`
5. **API Scopes** - Enable:
   - **Event streams**: Read
6. Click **Create**

### Step 2: Copy Credentials

After creation, you'll see:
- **Client ID** (looks like: abc123def456ghi789)
- **Client Secret** (only shown once - copy it!)

Click **Done** when copied.

### Step 3: Gather Your Information

You now have:

- **Client ID**: (from Step 2)
- **Client Secret**: (from Step 2)

### Step 4: Create Installation Key

```bash
limacharlie installation_key create \
  --description "CrowdStrike Falcon Cloud Adapter" \
  --tags "crowdstrike,falcon,edr"
```

### Step 5: Create Adapter Configuration

Create file `crowdstrike-adapter.yaml`:

```yaml
falconcloud:
  client_id: abc123def456ghi789
  client_secret: YOUR_FALCON_CLIENT_SECRET
  client_options:
    identity:
      oid: YOUR_LIMACHARLIE_ORG_ID
      installation_key: YOUR_INSTALLATION_KEY
    hostname: crowdstrike-falcon-adapter
    platform: falconcloud
    sensor_seed_key: falcon-cloud-production
    mapping:
      event_type_path: metadata/eventType
```

### Step 6: Deploy the Adapter

```bash
limacharlie adapter create --config crowdstrike-adapter.yaml
```

### Step 7: Validate Data Flow

CrowdStrike events stream in real-time, so you should see data quickly:

```bash
limacharlie events query --sensor-id <SENSOR_ID> --limit 10
```

**Expected events**: Detections, process executions, network connections, etc.

### Verification Checklist
- [ ] Sensor online within 1-2 minutes
- [ ] Events include CrowdStrike detection metadata
- [ ] Event types match Falcon event schema

### Common Issues

**"Invalid credentials"**:
- Verify API scope includes "Event streams: Read"
- Check Client ID and Secret for copy/paste errors
- Ensure API client is active (not disabled)

**Official docs**: https://developer.crowdstrike.com/docs/openapi/

---

## Example 6: Firewall Syslog (On-Prem)

Configure an on-premises syslog adapter to collect logs from network firewalls (Palo Alto, Fortinet, etc.).

### What You'll Accomplish
- Deploy the LimaCharlie adapter binary
- Configure it as a syslog listener
- Point your firewall to send logs to the adapter
- Parse firewall logs into structured events

### Prerequisites Checklist
- [ ] Linux server/VM to run the adapter (Ubuntu, CentOS, etc.)
- [ ] Network access from firewall to adapter server
- [ ] Firewall admin access to configure syslog forwarding
- [ ] LimaCharlie MCP installed

### Step 1: Download LimaCharlie Adapter Binary

On your Linux server:

```bash
# Download latest adapter (x86_64 Linux)
wget https://downloads.limacharlie.io/sensor/linux/64 -O lc_adapter
chmod +x lc_adapter

# Move to /usr/local/bin for easy access
sudo mv lc_adapter /usr/local/bin/
```

Official download page: https://docs.limacharlie.io/docs/adapter-deployment

### Step 2: Create Installation Key

```bash
limacharlie installation_key create \
  --description "Firewall Syslog Adapter" \
  --tags "firewall,syslog,network"
```

Copy the Installation Key and your Organization ID.

### Step 3: Create Adapter Configuration

Create `/etc/limacharlie/syslog-adapter.yaml`:

```yaml
syslog:
  port: 1514
  iface: 0.0.0.0  # Listen on all interfaces
  is_udp: true    # Most firewalls use UDP syslog
  client_options:
    identity:
      oid: YOUR_LIMACHARLIE_ORG_ID
      installation_key: YOUR_INSTALLATION_KEY
    hostname: firewall-syslog-adapter
    platform: text
    sensor_seed_key: firewall-syslog-production
    mapping:
      # Grok pattern for Palo Alto firewall logs (customize for your firewall)
      parsing_grok:
        message: '%{TIMESTAMP_ISO8601:timestamp} %{HOSTNAME:firewall_host} %{WORD:log_type} %{GREEDYDATA:raw_message}'
      event_type_path: log_type
      event_time_path: timestamp
      sensor_hostname_path: firewall_host
```

**For Fortinet firewalls**, use this grok pattern instead:
```yaml
parsing_grok:
  message: 'date=%{DATA:date} time=%{DATA:time} devname="%{DATA:device}" devid="%{DATA:device_id}" logid="%{DATA:log_id}" type="%{DATA:log_type}" subtype="%{DATA:subtype}" %{GREEDYDATA:raw_fields}'
```

### Step 4: Test the Configuration

```bash
# Test that the adapter can start with your config
lc_adapter syslog /etc/limacharlie/syslog-adapter.yaml
```

You should see:
```
DBG: usp-client connecting
DBG: usp-client connected
DBG: listening for connections on 0.0.0.0:1514
```

Press Ctrl+C to stop for now.

### Step 5: Configure Firewall to Send Syslog

**For Palo Alto firewalls**:
1. Go to **Device** → **Server Profiles** → **Syslog**
2. Add server: IP of your adapter server, port 1514, UDP
3. Go to **Objects** → **Log Forwarding**
4. Create profile forwarding traffic/threat/etc. logs to your syslog server
5. Apply to security policies

**For Fortinet firewalls**:
1. Go to **Log & Report** → **Log Settings**
2. Enable **Send Logs to Syslog**
3. IP/Port: Your adapter server IP and 1514
4. Select log types to send

**For generic firewalls**: Look for "Syslog server" or "Remote logging" settings.

### Step 6: Create Systemd Service (Run as Service)

Create `/etc/systemd/system/limacharlie-syslog.service`:

```ini
[Unit]
Description=LimaCharlie Syslog Adapter
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/lc_adapter syslog /etc/limacharlie/syslog-adapter.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable limacharlie-syslog
sudo systemctl start limacharlie-syslog
sudo systemctl status limacharlie-syslog
```

### Step 7: Validate Data Flow

Check adapter logs:
```bash
sudo journalctl -u limacharlie-syslog -f
```

You should see:
```
DBG: listening for connections on 0.0.0.0:1514
DBG: received 1024 bytes from 192.168.1.100
```

Check in LimaCharlie:
```bash
limacharlie sensor list --filter "hostname:firewall-syslog-adapter"
limacharlie events query --sensor-id <SENSOR_ID> --limit 10
```

### Verification Checklist
- [ ] Adapter service is running (systemctl status)
- [ ] Firewall shows successful syslog delivery
- [ ] Adapter logs show incoming bytes
- [ ] Events appear in LimaCharlie
- [ ] Parsing is working (fields are extracted)

### Common Issues

**No events appearing**:
- Check firewall can reach adapter IP:port (telnet or nc test)
- Verify firewall config saved and applied
- Check adapter is listening: `sudo netstat -tulpn | grep 1514`

**Events unparsed/raw**:
- Grok pattern doesn't match your firewall format
- Get a sample log line from firewall
- Test grok pattern at https://grokdebugger.com or ask me to help craft one

**Permission denied on port 1514**:
- Ports below 1024 require root
- Use port 1514 or higher, or run as root

---

## Next Steps

Now that you've seen complete examples, you can:
- Adapt these patterns to other similar sources
- Combine multiple adapters for comprehensive coverage
- Create custom parsers for unique log formats

For more technical details, see [REFERENCE.md](REFERENCE.md).

For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
