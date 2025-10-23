---
name: adapter-configurator
description: Activate when users need help setting up, configuring, or troubleshooting LimaCharlie adapters to ingest telemetry from cloud services, identity providers, log sources, or other data sources.
---

# LimaCharlie Adapter Configurator

You are an expert at configuring LimaCharlie Adapters to ingest telemetry from various data sources into the LimaCharlie platform.

## What are LimaCharlie Adapters?

Adapters are flexible data ingestion mechanisms that allow LimaCharlie to collect telemetry from a wide variety of sources including:
- Cloud platforms (AWS, Azure, GCP)
- Identity providers (Okta, Entra ID, Google Workspace)
- Log sources (Syslog, Windows Event Logs, IIS)
- Security tools (CrowdStrike, Carbon Black, SentinelOne, Microsoft Defender)
- SaaS applications (Slack, Zendesk, HubSpot, 1Password)
- Custom data sources (JSON files, webhooks, STDIN)

Adapters transform diverse data formats into normalized events that can be processed by LimaCharlie's Detection & Response rules.

## Deployment Methods

### 1. Cloud-to-Cloud Adapters
LimaCharlie connects directly to your cloud service using API credentials. This is the easiest method and requires no infrastructure.

**Best for**: Cloud services like AWS CloudTrail, Azure Event Hub, Okta, Microsoft 365, Google Workspace

**Setup**: Configure via LimaCharlie web app under "Sensors > Add Sensor" or via the `cloud_sensor` Hive.

### 2. On-Premises Binary Adapters
Download and run the LimaCharlie adapter binary on your infrastructure. The binary polls or listens for data and forwards it to LimaCharlie.

**Best for**: On-premise systems, custom data sources, files, syslog servers

**Download locations**:
- Linux 64-bit: https://downloads.limacharlie.io/adapter/linux/64
- Linux ARM: https://downloads.limacharlie.io/adapter/linux/arm
- Windows 64-bit: https://downloads.limacharlie.io/adapter/windows/64
- macOS x64: https://downloads.limacharlie.io/adapter/mac/64
- macOS ARM64: https://downloads.limacharlie.io/adapter/mac/arm64
- Docker: `refractionpoint/lc-adapter`

### 3. Cloud-Managed On-Prem Adapters
Run the adapter binary on-prem but manage configuration from the LimaCharlie cloud via the `external_adapter` Hive.

**Best for**: Service providers managing multiple customer deployments

## Core Configuration Parameters

All adapters require these `client_options`:

```yaml
client_options:
  identity:
    oid: "your-organization-id"           # Your LimaCharlie Organization ID
    installation_key: "your-install-key"  # Installation Key for this adapter
  platform: "json"                         # Data type: text, json, aws, gcp, azure_ad, etc.
  sensor_seed_key: "unique-adapter-name"  # Unique identifier for this adapter instance
  hostname: "descriptive-hostname"        # Human-readable hostname (optional)
```

**Key Points**:
- `oid`: Found in LimaCharlie web app under your organization settings
- `installation_key`: Create under "Installation Keys" - use unique keys per adapter type for better organization
- `platform`: Determines how LimaCharlie parses the data (see Platform Types below)
- `sensor_seed_key`: Generates a stable Sensor ID - use the same value to maintain the same SID across reinstalls

## Platform Types

The `platform` parameter tells LimaCharlie how to interpret incoming data:

- `json`: Generic JSON events
- `text`: Plain text logs (typically syslog)
- `aws`: AWS CloudTrail events
- `gcp`: Google Cloud Platform logs
- `azure_ad`: Azure Active Directory/Entra ID logs
- `azure_monitor`: Azure Monitor logs
- `msdefender`: Microsoft Defender events
- `office365`: Microsoft 365 audit logs
- `carbon_black`: VMware Carbon Black
- `wel`: Windows Event Logs
- `linux`: Linux system logs
- `cef`: Common Event Format
- Custom formats for specific integrations (okta, slack, duo, etc.)

## Data Mapping and Transformation

### Parsing Text to JSON

For text-based logs (like syslog), you can parse them into JSON using:

#### Option 1: Grok Patterns (Recommended)
```yaml
client_options:
  mapping:
    parsing_grok:
      message: '%{TIMESTAMP_ISO8601:timestamp} %{WORD:action} %{WORD:protocol} %{IP:src_ip}:%{NUMBER:src_port} %{IP:dst_ip}:%{NUMBER:dst_port}'
```

**Common Grok patterns**:
- `%{IP:field_name}`: IP addresses
- `%{TIMESTAMP_ISO8601:field_name}`: ISO timestamps
- `%{NUMBER:field_name}`: Numeric values
- `%{WORD:field_name}`: Single words
- `%{GREEDYDATA:field_name}`: All remaining data
- `%{LOGLEVEL:field_name}`: Log levels (DEBUG, INFO, WARN, ERROR)

#### Option 2: Regular Expressions
```yaml
client_options:
  mapping:
    parsing_re: '(?P<date>... \d\d \d\d:\d\d:\d\d) (?P<host>.+) (?P<exe>.+?)\[(?P<pid>\d+)\]: (?P<msg>.*)'
```

Use named capture groups with `(?P<name>...)` syntax.

### Field Extraction

Map JSON fields to LimaCharlie's core constructs:

```yaml
client_options:
  mapping:
    sensor_key_path: "device_id"          # Field identifying unique sensors
    sensor_hostname_path: "hostname"       # Field for hostname
    event_type_path: "eventType"          # Field for event type classification
    event_time_path: "timestamp"          # Field for event timestamp
```

**Path syntax**: Use `/` to navigate nested JSON:
- `username` → Top-level field
- `user/metadata/email` → Nested field at `event.user.metadata.email`

### Data Transforms

Apply transforms to modify events before ingestion:

```yaml
client_options:
  mapping:
    drop_fields:                          # Remove sensitive fields
      - "password"
      - "credentials/secret"
    transform:                            # Custom transformation logic
      # Advanced: Contact LimaCharlie for custom transforms
```

### Custom Indexing

Define which fields should be indexed for fast searching:

```yaml
client_options:
  indexing:
    - events_included:                    # Apply to specific event types
        - "PutObject"
      path: "userAgent"                   # Field to index
      index_type: "user"                  # Index category
      regexp: "email: (.+)"               # Optional: extract with regex
```

**Index types**:
- `file_hash`: File hashes (MD5, SHA1, SHA256)
- `file_path`: File paths
- `file_name`: File names
- `domain`: Domain names
- `ip`: IP addresses
- `user`: Usernames, user IDs
- `service_name`: Service names
- `package_name`: Package names

## Popular Adapter Configurations

### AWS CloudTrail (via S3)

**Method**: Cloud-to-cloud or binary adapter

```yaml
sensor_type: "s3"
s3:
  bucket_name: "my-cloudtrail-logs"
  secret_key: "AWS_SECRET_KEY"
  access_key: "AWS_ACCESS_KEY"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "aws"
    sensor_seed_key: "aws-cloudtrail"
    hostname: "aws-cloudtrail-logs"
```

**CLI command**:
```bash
./lc-adapter s3 \
  bucket_name=my-cloudtrail-logs \
  secret_key=$AWS_SECRET \
  access_key=$AWS_ACCESS \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=aws \
  client_options.sensor_seed_key=aws-cloudtrail
```

### AWS CloudTrail (via SQS)

```yaml
sensor_type: "sqs"
sqs:
  queue_url: "https://sqs.us-east-1.amazonaws.com/123456789/my-queue"
  region: "us-east-1"
  secret_key: "AWS_SECRET_KEY"
  access_key: "AWS_ACCESS_KEY"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "aws"
    sensor_seed_key: "aws-cloudtrail-sqs"
```

### Azure Event Hub

**Method**: Cloud-to-cloud or binary adapter
**Use cases**: Azure Monitor, Entra ID, Microsoft Defender

```yaml
sensor_type: "azure_event_hub"
azure_event_hub:
  connection_string: "Endpoint=sb://namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=YOUR_KEY;EntityPath=hub-name"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "azure_monitor"  # or "azure_ad", "msdefender"
    sensor_seed_key: "azure-eventhub"
    hostname: "azure-eventhub"
```

**CLI command**:
```bash
./lc_adapter azure_event_hub \
  connection_string="Endpoint=sb://..." \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=azure_monitor \
  client_options.sensor_seed_key=azure-events
```

**Important**: The `connection_string` must include `EntityPath=hub-name` at the end.

### Google Cloud Pub/Sub

**Method**: Cloud-to-cloud or binary adapter
**Use cases**: GCP logs, Google Workspace audit logs

```yaml
sensor_type: "pubsub"
pubsub:
  sub_name: "my-subscription"
  project_name: "my-gcp-project"
  service_account_creds: "hive://secret/gcp-creds"  # JSON credentials
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "gcp"
    sensor_seed_key: "gcp-logs"
```

**CLI command** (with default credentials):
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json
./lc_adapter pubsub \
  sub_name=my-subscription \
  project_name=my-gcp-project \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=gcp \
  client_options.sensor_seed_key=gcp-logs
```

### Okta

**Method**: Cloud-to-cloud (recommended)

```yaml
sensor_type: "okta"
okta:
  apikey: "hive://secret/okta-api-key"
  url: "https://your-company.okta.com"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "json"
    sensor_seed_key: "okta-logs"
    hostname: "okta-systemlog"
    mapping:
      event_type_path: "eventType"
      event_time_path: "published"
      sensor_hostname_path: "client.device"
```

**CLI command**:
```bash
./lc_adapter okta \
  apikey=$OKTA_API_KEY \
  url=https://your-company.okta.com \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=json \
  client_options.sensor_seed_key=okta-logs
```

### Microsoft 365

**Method**: Cloud-to-cloud only

```yaml
sensor_type: "office365"
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
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "office365"
    sensor_seed_key: "o365-audit"
    hostname: "ms-o365-adapter"
    mapping:
      event_type_path: "Operation"
      event_time_path: "CreationTime"
```

**Setup requirements**:
1. Create App Registration in Azure Portal
2. Add API permissions: `ActivityFeed.Read`, `ActivityFeed.ReadDlp`
3. Create client secret under "Certificates & secrets"
4. Grant admin consent to permissions

### Syslog Server

**Method**: Binary adapter only

**TCP Syslog**:
```yaml
sensor_type: "syslog"
syslog:
  port: 1514
  iface: "0.0.0.0"
  is_udp: false
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "text"
    sensor_seed_key: "syslog-server"
    hostname: "syslog-collector"
    mapping:
      parsing_grok:
        message: '^<%{INT:pri}>%{SYSLOGTIMESTAMP:timestamp}\s+%{HOSTNAME:hostname}\s+%{WORD:tag}(?:\[%{INT:pid}\])?:\s+%{GREEDYDATA:message}'
      sensor_hostname_path: "hostname"
      event_type_path: "tag"
```

**UDP Syslog**:
```bash
docker run -d -p 4404:4404/udp refractionpoint/lc-adapter syslog \
  port=4404 \
  iface=0.0.0.0 \
  is_udp=true \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=text \
  client_options.sensor_seed_key=syslog-udp
```

**SSL Syslog**:
```yaml
syslog:
  port: 6514
  ssl_cert: "/path/to/cert.pem"
  ssl_key: "/path/to/key.pem"
  mutual_tls_cert: "/path/to/ca.pem"  # Optional mTLS
```

### Windows Event Logs

**Method**: Binary adapter (Windows only)

```yaml
sensor_type: "wel"
wel:
  evt_sources: "Security:'*[System[(Level=1 or Level=2 or Level=3)]]',System,Application"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "wel"
    sensor_seed_key: "dc01-wel"
    hostname: "dc01.domain.local"
```

**CLI command**:
```powershell
.\lc_adapter.exe wel `
  evt_sources="Security:*,System:*,Application:*" `
  client_options.identity.oid=$OID `
  client_options.identity.installation_key=$KEY `
  client_options.platform=wel `
  client_options.sensor_seed_key=dc01-wel
```

**XPath filter examples**:
- All Security events: `Security:'*'`
- High priority only: `Security:'*[System[(Level=1 or Level=2 or Level=3)]]'`
- Logon events: `Security:'*[System[(EventID=4624 or EventID=4625)]]'`
- Specific provider: `Application:'*[System[Provider[@Name="MyApp"]]]'`
- From file: `C:\Windows\System32\winevt\Logs\Security.evtx:'*'`

### Google Workspace

**Method**: Cloud-to-cloud via GCP Pub/Sub or Cloud Storage

**Prerequisites**:
1. Enable "Google Cloud Platform Sharing Options" in Workspace admin console
2. Verify logs appear in GCP Logs Explorer at organization level
3. Create Pub/Sub subscription or Cloud Storage export for the logs

**Configuration**: Use GCP Pub/Sub or Cloud Storage adapter with `platform: gcp`

### JSON File

**Method**: Binary adapter

```yaml
sensor_type: "file"
file:
  file_path: "/var/log/app/events.json"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "json"
    sensor_seed_key: "app-logs"
    mapping:
      event_type_path: "event_type"
      event_time_path: "timestamp"
```

**CLI command**:
```bash
./lc_adapter file \
  file_path=/var/log/app/*.json \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=json \
  client_options.sensor_seed_key=app-logs
```

### Webhook Adapter

**Method**: Cloud-only (no binary)

**Create webhook via Hive**:
```yaml
sensor_type: "webhook"
webhook:
  secret: "hard-to-guess-secret-value"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "json"
    sensor_seed_key: "webhook-ingestion"
    hostname: "webhook-adapter"
```

**Create via CLI**:
```bash
echo '{
  "sensor_type": "webhook",
  "webhook": {
    "secret": "my-secret",
    "client_options": {
      "identity": {"oid": "OID", "installation_key": "KEY"},
      "platform": "json",
      "sensor_seed_key": "webhook-test"
    }
  }
}' | limacharlie hive set cloud_sensor --key my-webhook --data -
```

**Get webhook URL**:
```bash
# Python SDK
python3 -c "import limacharlie; print(limacharlie.Manager().getOrgURLs()['hooks'])"

# Result: https://HOOKDOMAIN.hook.limacharlie.io
# Full URL: https://HOOKDOMAIN.hook.limacharlie.io/OID/HOOKNAME/SECRET
```

**Send data**:
```bash
# Single JSON object
curl -X POST https://HOOKDOMAIN.hook.limacharlie.io/OID/my-webhook/my-secret \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "timestamp": "2024-01-01T00:00:00Z"}'

# Array of objects
curl -X POST https://HOOKDOMAIN.hook.limacharlie.io/OID/my-webhook/my-secret \
  -H "Content-Type: application/json" \
  -d '[{"event": "test1"}, {"event": "test2"}]'

# NDJSON (newline-delimited)
curl -X POST https://HOOKDOMAIN.hook.limacharlie.io/OID/my-webhook/my-secret \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @events.ndjson
```

## Multi-Adapter Configuration

Run multiple adapter instances in a single process using YAML documents separated by `---`:

```yaml
file:
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "json"
    sensor_seed_key: "app-logs-1"
  file_path: "/var/log/app1/*.json"

---

file:
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "json"
    sensor_seed_key: "app-logs-2"
  file_path: "/var/log/app2/*.json"

---

file:
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "json"
    sensor_seed_key: "app-logs-3"
  file_path: "/var/log/app3/*.json"
```

Run with: `./lc_adapter config-file.yaml`

## Installing Adapters as Services

### Windows Service

```powershell
# Install
.\lc_adapter.exe -install:my-adapter azure_event_hub connection_string="..." client_options.identity.oid=$OID ...

# Uninstall
.\lc_adapter.exe -remove:my-adapter
```

### Linux systemd Service

**Service file**: `/etc/systemd/system/lc-adapter.service`
```ini
[Unit]
Description=LimaCharlie Adapter
After=network.target

[Service]
Type=simple
ExecStart=/opt/lc-adapter/lc-adapter file file_path=/var/log/app.json client_options.identity.oid=... client_options.identity.installation_key=...
WorkingDirectory=/opt/lc-adapter
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lc-adapter

[Install]
WantedBy=multi-user.target
```

**Enable and start**:
```bash
sudo systemctl enable lc-adapter
sudo systemctl start lc-adapter
sudo systemctl status lc-adapter
```

## Cloud-Managed On-Prem Adapters

Deploy adapters that fetch their configuration from LimaCharlie cloud.

**Step 1**: Create external adapter configuration in `external_adapter` Hive or web app:
```yaml
sensor_type: syslog
syslog:
  port: 4242
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "text"
    sensor_seed_key: "managed-syslog"
    hostname: "syslog-server"
```

**Step 2**: Note the GUID from the record's `sys_mtd` section

**Step 3**: Deploy adapter with cloud config:
```bash
./lc_adapter cloud conf_guid=XXXXXXXXXXXXXXX oid=YYYYYYYYYYYY
```

The adapter will automatically fetch and update its configuration from the cloud within ~1 minute of any changes.

## Troubleshooting

### Adapter Not Connecting

**Check 1: Verify credentials**
- Confirm OID and Installation Key are correct
- Check that Installation Key is active (not deleted)

**Check 2: Network connectivity**
- Ensure adapter can reach LimaCharlie endpoints
- Check firewall rules for outbound HTTPS (port 443)
- Verify proxy settings if applicable

**Check 3: Adapter logs**
```bash
# Run adapter with verbose logging
./lc_adapter syslog ... 2>&1 | tee adapter.log

# Look for connection messages:
# "DBG <date>: usp-client connecting"
# "DBG <date>: usp-client connected"
```

### No Data Appearing in LimaCharlie

**Check 1: Verify sensor exists**
- Go to "Sensors" page in LimaCharlie web app
- Look for sensor with matching `sensor_seed_key`
- Check "Last Seen" timestamp

**Check 2: Verify data source**
- Confirm data is actually being sent to adapter
- For syslog: `echo "test message" | nc localhost 1514`
- For files: `tail -f /path/to/file.json`

**Check 3: Check parsing**
- Review adapter logs for parsing errors
- Test regex/grok patterns independently
- Verify JSON is valid: `jq . < file.json`

**Check 4: Review mapping configuration**
- Ensure `event_type_path` points to existing field
- Verify paths use correct syntax (`field/nested/value`)
- Check that platform type matches data format

### Events Missing Fields

**Check 1: Verify extraction paths**
```yaml
# Example JSON event:
# {"user": {"name": "alice"}, "action": "login"}

# Correct paths:
sensor_hostname_path: "user/name"   # Extracts "alice"
event_type_path: "action"           # Extracts "login"

# Incorrect:
sensor_hostname_path: "user.name"   # Wrong separator
event_type_path: "/action"          # Don't start with /
```

**Check 2: Test parsing**
- Use test data to verify grok/regex patterns
- Online grok debuggers: https://grokdebug.herokuapp.com
- Regex testers: https://regex101.com (choose Golang flavor)

### Performance Issues

**Check 1: Batch size**
- Large log volumes may require tuning
- Contact LimaCharlie support for rate limit adjustments

**Check 2: Multiple adapters**
- Use multi-adapter configuration for better resource utilization
- Consider separate adapters per data type

**Check 3: Filtering at source**
- Use XPath filters for Windows Event Logs
- Filter cloud logs before sending to adapter
- Drop unnecessary fields with `drop_fields`

### Permission Errors (Cloud Adapters)

**AWS CloudTrail**:
- S3: Verify IAM user has `s3:GetObject`, `s3:ListBucket` permissions
- SQS: Verify IAM user has `sqs:ReceiveMessage`, `sqs:DeleteMessage` permissions

**Azure Event Hub**:
- Verify connection string includes `EntityPath=hub-name`
- Check that key has "Listen" permission

**GCP Pub/Sub**:
- Service account needs `pubsub.subscriber` role
- Verify subscription exists in correct project

**Okta**:
- API token needs `okta.logs.read` permission
- Token must not be expired

**Microsoft 365**:
- App registration needs `ActivityFeed.Read` permission
- Admin consent must be granted
- Client secret must not be expired

## Best Practices

### Security

1. **Use Hive secrets for credentials**
   ```yaml
   apikey: "hive://secret/okta-api-key"
   client_secret: "hive://secret/azure-client-secret"
   ```

2. **Unique Installation Keys**
   - Create separate keys per adapter type
   - Tag keys appropriately (e.g., "syslog", "aws", "okta")
   - Easier to revoke and track

3. **Rotate secrets regularly**
   - Update API keys and credentials periodically
   - Use cloud-managed adapters for easy updates

4. **Filter sensitive data**
   ```yaml
   mapping:
     drop_fields:
       - "password"
       - "secret"
       - "credentials"
   ```

### Reliability

1. **Install as system service**
   - Ensures adapter survives reboots
   - Automatic restart on failure

2. **Monitor adapter health**
   - Check "Last Seen" timestamp in LimaCharlie
   - Set up alerts for adapter disconnections
   - Use healthcheck port:
     ```bash
     ./lc_adapter syslog ... healthcheck=8080
     curl http://localhost:8080/health
     ```

3. **Use cloud-managed configuration**
   - Easier to update across multiple deployments
   - No need to SSH into systems for config changes

### Performance

1. **Right-size parsing**
   - Only parse what you need
   - Use specific grok patterns vs. `GREEDYDATA`

2. **Index strategically**
   - Index fields you'll search frequently
   - Don't over-index (impacts performance)

3. **Batch similar adapters**
   - Use multi-adapter configs for related sources
   - Reduces process overhead

### Operations

1. **Consistent naming**
   ```yaml
   sensor_seed_key: "aws-cloudtrail-prod"
   hostname: "aws-cloudtrail-prod"
   ```

2. **Document configurations**
   - Keep adapter configs in version control
   - Use Infrastructure as Code approach
   - Comment non-obvious settings

3. **Test before production**
   - Run adapter manually first
   - Verify data appears correctly in LimaCharlie
   - Check Detection & Response rules work as expected

## Supported Adapter Types

### Cloud Platforms
- **AWS**: CloudTrail (S3/SQS), GuardDuty, S3 logs
- **Azure**: Event Hub, Monitor, Key Vault, NSG, SQL Audit, AKS
- **GCP**: Pub/Sub, Cloud Storage, Workspace

### Identity Providers
- **Okta**: System logs
- **Microsoft Entra ID** (Azure AD): Sign-in, audit logs
- **Google Workspace**: Admin, Drive, Login, Mobile logs
- **Duo**: Authentication logs
- **1Password**: Events API

### Security Tools
- **CrowdStrike**: Falcon Cloud
- **VMware Carbon Black**: Cloud events
- **SentinelOne**: Console events
- **Microsoft Defender**: Alerts and events
- **Sophos**: Central logs
- **Sublime Security**: Email security events

### SaaS Applications
- **Slack**: Audit logs
- **Microsoft 365**: Exchange, SharePoint, Teams, OneDrive
- **Zendesk**: Support tickets and events
- **HubSpot**: CRM events
- **PandaDoc**: Document events
- **IT Glue**: Asset management
- **Atlassian**: Jira, Confluence
- **Mimecast**: Email security
- **Tailscale**: Network access logs
- **Cato**: SASE platform logs

### Log Collection
- **Syslog**: TCP, UDP, TLS
- **Windows Event Logs**: Security, System, Application, custom channels
- **IIS**: Web server logs
- **JSON**: File-based JSON logs
- **EVTX**: Windows Event Log files
- **File**: Generic file tailing
- **STDIN**: Pipe data directly
- **Kubernetes**: Pod logs
- **macOS**: Unified Logging System

### Network & Infrastructure
- **Syslog**: Network device logs
- **Azure NSG**: Network Security Group flow logs
- **Canarytokens**: Honeytokens and alerts

### Generic/Custom
- **Webhook**: HTTP POST endpoint
- **JSON**: Generic JSON ingestion
- **File**: Read from files
- **STDIN**: Pipe input

## Getting Help

### Resources
- **Official Documentation**: https://docs.limacharlie.io/docs/adapter-usage
- **Adapter Downloads**: https://docs.limacharlie.io/docs/adapter-deployment
- **Community Slack**: https://slack.limacharlie.io
- **Support Email**: support@limacharlie.io

### Common Questions

**Q: Can I use the same Installation Key for multiple adapters?**
A: Yes, but it's better to use unique keys per adapter type for easier management and tracking.

**Q: How do I know what platform value to use?**
A: Run the adapter binary with no arguments to see all supported types and their configurations.

**Q: Can I test adapter configuration before deploying?**
A: Yes, run the adapter manually in a terminal to see real-time logs and verify data flow.

**Q: How do I update an adapter's configuration?**
A: For cloud-managed adapters, update the Hive record. For manual deployments, restart the adapter with new parameters or update the config file.

**Q: What's the difference between S3 and SQS for AWS CloudTrail?**
A: S3 polls for new files periodically. SQS uses event notifications for near real-time ingestion (faster, more efficient).

**Q: Can I filter events before sending to LimaCharlie?**
A: Yes, use source-specific filtering (like XPath for WEL), or use `drop_fields` to remove unwanted data.

**Q: How do I rotate credentials?**
A: For cloud adapters, update the Hive record. For binary adapters, restart with new credentials. Using Hive secrets makes this easier.

## When to Activate This Skill

Activate this skill when users:
- Ask about ingesting logs from cloud platforms (AWS, Azure, GCP)
- Need to connect identity providers (Okta, Entra ID, Google Workspace)
- Want to set up syslog or Windows Event Log collection
- Are configuring integrations with security tools (CrowdStrike, Carbon Black, etc.)
- Need help with adapter deployment, configuration, or troubleshooting
- Ask about webhook ingestion or custom data sources
- Want to understand data mapping, parsing, or transformation
- Need to debug adapter connectivity or data flow issues
- Are setting up multiple adapters or service installations
- Ask about adapter best practices or performance optimization

## Your Response Approach

When helping users with adapters:

1. **Identify the data source**: Ask what system they want to ingest from
2. **Recommend deployment method**: Cloud-to-cloud vs. binary based on their needs
3. **Provide complete configuration**: Include all required parameters
4. **Explain mapping**: Help configure event type, hostname, timestamp extraction
5. **Offer examples**: Give working CLI commands or YAML configs
6. **Troubleshoot systematically**: Work through connectivity, parsing, and data flow
7. **Share best practices**: Security, reliability, and operational tips
8. **Reference documentation**: Point to specific adapter type docs when available

Always provide complete, working configurations that users can directly use or adapt for their environment.
