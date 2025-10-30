# Adapter Reference

Complete reference for all LimaCharlie adapter types with configuration syntax and options.

## Platform Types

The `platform` parameter in `client_options` determines how LimaCharlie parses incoming data:

| Platform | Description | Use Cases |
|----------|-------------|-----------|
| `json` | Generic JSON events | Custom applications, generic APIs |
| `text` | Plain text logs | Syslog, unstructured logs |
| `aws` | AWS CloudTrail format | CloudTrail, GuardDuty |
| `gcp` | Google Cloud Platform logs | GCP audit logs, Workspace |
| `azure_ad` | Azure Active Directory/Entra ID | Entra ID sign-ins, audit logs |
| `azure_monitor` | Azure Monitor logs | Azure resource logs |
| `msdefender` | Microsoft Defender events | Defender for Endpoint, Cloud Apps |
| `office365` | Microsoft 365 audit logs | Exchange, SharePoint, Teams |
| `okta` | Okta events | Okta system logs |
| `carbon_black` | VMware Carbon Black | CB Cloud, CB Defense |
| `crowdstrike` | CrowdStrike Falcon | Falcon detections, events |
| `sentinelone` | SentinelOne events | S1 console events |
| `wel` | Windows Event Logs | Windows Security, System, Application |
| `linux` | Linux system logs | Syslog, auth logs |
| `cef` | Common Event Format | CEF-compatible systems |
| `duo` | Duo Security | Duo authentication logs |
| `1password` | 1Password Events API | 1Password audit events |
| `slack` | Slack Audit API | Slack workspace events |
| `zendesk` | Zendesk Support | Ticket and audit events |
| `hubspot` | HubSpot CRM | Contact, deal, company events |
| `sophos` | Sophos Central | Sophos endpoint events |
| `iis` | Internet Information Services | IIS web server logs |

## Cloud Platform Adapters

### s3 - AWS S3 Bucket

Polls S3 bucket for objects (typically CloudTrail logs).

**Configuration**:
```yaml
sensor_type: "s3"
s3:
  bucket_name: "my-bucket"           # Required: S3 bucket name
  secret_key: "AWS_SECRET_KEY"       # Required: AWS secret access key
  access_key: "AWS_ACCESS_KEY"       # Required: AWS access key ID
  prefix: "AWSLogs/"                 # Optional: Object key prefix filter
  region: "us-east-1"                # Optional: AWS region (auto-detected if not set)
  polling_seconds: 60                # Optional: Poll interval (default: 60)
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "aws"
    sensor_seed_key: "s3-logs"
```

**IAM Permissions Required**:
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

**Common Uses**: CloudTrail logs, GuardDuty findings, VPC Flow Logs, S3 access logs

---

### sqs - AWS SQS Queue

Receives messages from SQS queue (typically S3 event notifications for CloudTrail).

**Configuration**:
```yaml
sensor_type: "sqs"
sqs:
  queue_url: "https://sqs.us-east-1.amazonaws.com/123456789/my-queue"  # Required
  region: "us-east-1"                # Required: AWS region
  secret_key: "AWS_SECRET_KEY"       # Required: AWS secret access key
  access_key: "AWS_ACCESS_KEY"       # Required: AWS access key ID
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "aws"
    sensor_seed_key: "sqs-cloudtrail"
```

**IAM Permissions Required**:
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

**Common Uses**: Real-time CloudTrail ingestion, S3 event-driven processing

---

### azure_event_hub - Azure Event Hub

Consumes events from Azure Event Hub.

**Configuration**:
```yaml
sensor_type: "azure_event_hub"
azure_event_hub:
  connection_string: "Endpoint=sb://namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=KEY;EntityPath=hub-name"
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "azure_monitor"  # or azure_ad, msdefender
    sensor_seed_key: "azure-hub"
```

**Important**: The connection string MUST include `EntityPath=hub-name` at the end.

**Common Uses**: Azure Monitor diagnostic logs, Entra ID sign-in logs, Microsoft Defender alerts

---

### pubsub - Google Cloud Pub/Sub

Subscribes to Google Cloud Pub/Sub topics.

**Configuration**:
```yaml
sensor_type: "pubsub"
pubsub:
  sub_name: "my-subscription"        # Required: Subscription name
  project_name: "my-gcp-project"     # Required: GCP project ID
  service_account_creds: "hive://secret/gcp-creds"  # Optional: JSON credentials
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "gcp"
    sensor_seed_key: "gcp-pubsub"
```

**Authentication**:
- Provide `service_account_creds` as JSON string or Hive secret
- Or use default credentials via `GOOGLE_APPLICATION_CREDENTIALS` environment variable

**IAM Permissions**: Service account needs `roles/pubsub.subscriber` on the subscription

**Common Uses**: GCP audit logs, Google Workspace logs, Cloud Storage events

---

### gcs - Google Cloud Storage

Polls Google Cloud Storage bucket for objects.

**Configuration**:
```yaml
sensor_type: "gcs"
gcs:
  bucket_name: "my-gcs-bucket"       # Required: GCS bucket name
  project_name: "my-gcp-project"     # Required: GCP project ID
  prefix: "logs/"                    # Optional: Object prefix filter
  service_account_creds: "hive://secret/gcp-creds"  # Optional
  polling_seconds: 60                # Optional: Poll interval
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "gcp"
    sensor_seed_key: "gcs-logs"
```

**IAM Permissions**: Service account needs `roles/storage.objectViewer` on the bucket

**Common Uses**: GCP audit log exports, application log archives

---

## Identity Provider Adapters

### okta - Okta System Logs

Polls Okta System Log API.

**Configuration**:
```yaml
sensor_type: "okta"
okta:
  apikey: "hive://secret/okta-api-key"    # Required: Okta API token
  url: "https://company.okta.com"         # Required: Okta domain URL
  polling_seconds: 60                     # Optional: Poll interval
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "okta-logs"
    mapping:
      event_type_path: "eventType"
      event_time_path: "published"
      sensor_hostname_path: "client.device"
```

**API Token Requirements**:
- Create in Okta Admin Console: Security > API > Tokens
- Requires `okta.logs.read` permission
- Token does not expire but can be revoked

**Common Uses**: Authentication events, user lifecycle, MFA events

---

### office365 - Microsoft 365 Audit Logs

Polls Microsoft 365 Management Activity API.

**Configuration**:
```yaml
sensor_type: "office365"
office365:
  tenant_id: "hive://secret/o365-tenant-id"          # Required: Azure AD tenant ID
  client_id: "hive://secret/o365-client-id"          # Required: App registration client ID
  client_secret: "hive://secret/o365-client-secret"  # Required: Client secret
  content_types:                                      # Required: Content types to fetch
    - "Audit.AzureActiveDirectory"
    - "Audit.Exchange"
    - "Audit.SharePoint"
    - "Audit.General"
    - "DLP.All"
  polling_seconds: 300                                # Optional: Poll interval
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "office365"
    sensor_seed_key: "o365-audit"
    mapping:
      event_type_path: "Operation"
      event_time_path: "CreationTime"
```

**Azure App Registration Setup**:
1. Create App Registration in Azure Portal
2. Add API permissions: `ActivityFeed.Read`, `ActivityFeed.ReadDlp` (Office 365 Management APIs)
3. Grant admin consent
4. Create client secret under "Certificates & secrets"

**Available Content Types**:
- `Audit.AzureActiveDirectory` - Entra ID events
- `Audit.Exchange` - Email events
- `Audit.SharePoint` - SharePoint/OneDrive events
- `Audit.General` - General Office 365 events
- `DLP.All` - Data Loss Prevention events

**Common Uses**: Email access, file sharing, Teams activity, admin actions

---

### duo - Duo Security

Polls Duo Admin API for authentication logs.

**Configuration**:
```yaml
sensor_type: "duo"
duo:
  client_id: "hive://secret/duo-client-id"          # Required: Integration key
  client_secret: "hive://secret/duo-client-secret"  # Required: Secret key
  api_hostname: "api-xxxxxx.duosecurity.com"        # Required: API hostname
  polling_seconds: 60                               # Optional
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "duo-logs"
```

**Duo Setup**:
1. Create Admin API application in Duo Admin Panel
2. Grant permissions: "Grant read log"
3. Note integration key, secret key, and API hostname

**Common Uses**: MFA events, authentication logs, device trust

---

### 1password - 1Password Events API

Polls 1Password Events API.

**Configuration**:
```yaml
sensor_type: "1password"
1password:
  bearer_token: "hive://secret/1password-token"  # Required: Events API token
  polling_seconds: 300                           # Optional
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "1password-events"
```

**Token Setup**:
1. Sign in to 1Password Business account
2. Go to Integrations > Events API
3. Generate bearer token

**Common Uses**: Vault access, item usage, sign-in events

---

## Security Tool Adapters

### crowdstrike - CrowdStrike Falcon

Polls CrowdStrike Falcon Event Stream API.

**Configuration**:
```yaml
sensor_type: "crowdstrike"
crowdstrike:
  client_id: "hive://secret/cs-client-id"        # Required: API client ID
  client_secret: "hive://secret/cs-secret"       # Required: API client secret
  base_url: "https://api.crowdstrike.com"        # Optional: Default is US-1
  event_types:                                   # Optional: Event types to fetch
    - "DetectionSummaryEvent"
    - "IncidentSummaryEvent"
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "crowdstrike"
```

**API Client Setup**:
1. Create API client in Falcon console: Support > API Clients and Keys
2. Required scopes: "Event streams: READ"

**Common Uses**: Detections, incidents, host activity

---

### carbon_black - VMware Carbon Black

Polls Carbon Black Cloud API.

**Configuration**:
```yaml
sensor_type: "carbon_black"
carbon_black:
  api_id: "hive://secret/cb-api-id"              # Required: API ID
  api_key: "hive://secret/cb-api-key"            # Required: API secret key
  org_key: "ABCD1234"                            # Required: Org key
  api_url: "https://defense.conferdeploy.net"    # Required: CB Cloud URL
  polling_seconds: 60                            # Optional
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "carbon-black"
```

**API Setup**:
1. Create API key in CB Cloud: Settings > API Access
2. Access level: "Custom" with "Notifications" read permission

**Common Uses**: Alerts, threat events, device events

---

### sentinelone - SentinelOne

Polls SentinelOne Management Console API.

**Configuration**:
```yaml
sensor_type: "sentinelone"
sentinelone:
  api_token: "hive://secret/s1-token"       # Required: API token
  console_url: "https://company.sentinelone.net"  # Required: Console URL
  polling_seconds: 60                       # Optional
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "sentinelone"
```

**API Token Setup**:
1. Generate in S1 console: Settings > Users > Service Users
2. Create API token with "Viewer" role

**Common Uses**: Threats, agent activity, console events

---

### sophos - Sophos Central

Polls Sophos Central Event API.

**Configuration**:
```yaml
sensor_type: "sophos"
sophos:
  client_id: "hive://secret/sophos-client-id"      # Required
  client_secret: "hive://secret/sophos-secret"     # Required
  tenant_id: "hive://secret/sophos-tenant-id"      # Required
  polling_seconds: 300                             # Optional
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "sophos"
```

**API Credentials Setup**:
1. Create in Sophos Central: Global Settings > API Credentials
2. Grant "Event" read permissions

**Common Uses**: Endpoint events, threat detections, admin actions

---

## Log Collection Adapters

### syslog - Syslog Server

Runs a syslog server listening for TCP, UDP, or TLS connections.

**Configuration**:
```yaml
sensor_type: "syslog"
syslog:
  port: 1514                    # Required: Port to listen on
  iface: "0.0.0.0"             # Optional: Interface to bind (default: 0.0.0.0)
  is_udp: false                # Optional: Use UDP instead of TCP (default: false)
  ssl_cert: "/path/to/cert.pem"      # Optional: TLS certificate
  ssl_key: "/path/to/key.pem"        # Optional: TLS private key
  mutual_tls_cert: "/path/to/ca.pem" # Optional: Client CA for mTLS
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "text"
    sensor_seed_key: "syslog-server"
    mapping:
      parsing_grok:
        message: '^<%{INT:pri}>%{SYSLOGTIMESTAMP:timestamp}\s+%{HOSTNAME:hostname}\s+%{WORD:tag}(?:\[%{INT:pid}\])?:\s+%{GREEDYDATA:message}'
      sensor_hostname_path: "hostname"
      event_type_path: "tag"
```

**Common Uses**: Firewall logs, network device logs, application syslog

---

### wel - Windows Event Logs

Reads Windows Event Logs on Windows systems.

**Configuration**:
```yaml
sensor_type: "wel"
wel:
  evt_sources: "Security:'*',System:'*',Application:'*'"  # Required: Event sources
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "wel"
    sensor_seed_key: "windows-events"
```

**Event Source Format**: `ChannelName:'XPathQuery'`

**XPath Examples**:
- All events: `Security:'*'`
- Specific event IDs: `Security:'*[System[(EventID=4624 or EventID=4625)]]'`
- By severity: `Security:'*[System[(Level=1 or Level=2 or Level=3)]]'`
- From file: `C:\logs\Security.evtx:'*'`

**Common Uses**: Security logs, authentication, system events

---

### file - File Tailing

Reads lines from files (supports wildcards).

**Configuration**:
```yaml
sensor_type: "file"
file:
  file_path: "/var/log/app/*.log"    # Required: File path (supports * wildcard)
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"  # or "text"
    sensor_seed_key: "app-logs"
```

**Features**:
- Automatically follows file rotation
- Supports wildcards: `/var/log/*.log`
- Remembers position across restarts

**Common Uses**: Application logs, JSON logs, custom file formats

---

### evtx - Windows Event Log Files

Reads Windows .evtx files (for forensics or offline analysis).

**Configuration**:
```yaml
sensor_type: "evtx"
evtx:
  file_path: "C:\\logs\\Security.evtx"  # Required: Path to .evtx file
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "wel"
    sensor_seed_key: "forensic-evtx"
```

**Common Uses**: Forensic analysis, offline log processing

---

### iis - IIS Logs

Reads IIS W3C log files.

**Configuration**:
```yaml
sensor_type: "iis"
iis:
  file_path: "C:\\inetpub\\logs\\LogFiles\\W3SVC1\\*.log"  # Required
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "iis-logs"
```

**Common Uses**: Web server access logs, application logs

---

### stdin - Standard Input

Reads JSON or text from STDIN (for piping data).

**Configuration**:
```bash
# Pipe data directly to adapter
cat events.json | ./lc_adapter stdin \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$KEY \
  client_options.platform=json \
  client_options.sensor_seed_key=stdin-test
```

**Common Uses**: Testing, custom scripts, one-time imports

---

## SaaS Application Adapters

### slack - Slack Audit Logs

Polls Slack Audit Logs API.

**Configuration**:
```yaml
sensor_type: "slack"
slack:
  bearer_token: "hive://secret/slack-token"  # Required: Audit API token
  polling_seconds: 300                       # Optional
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "slack-audit"
```

**Token Setup**:
1. Create app in Slack: https://api.slack.com/apps
2. Enable Audit Logs API (Enterprise Grid only)
3. Install app to workspace and copy token

**Common Uses**: User actions, channel activity, workspace changes

---

### zendesk - Zendesk Support

Polls Zendesk Audit Logs API.

**Configuration**:
```yaml
sensor_type: "zendesk"
zendesk:
  subdomain: "company"                       # Required: Zendesk subdomain
  email: "admin@company.com"                 # Required: Admin email
  api_token: "hive://secret/zendesk-token"   # Required: API token
  polling_seconds: 300                       # Optional
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "zendesk"
```

**API Token Setup**:
1. Admin Center > Apps and integrations > APIs > Zendesk API
2. Enable token access and create token

**Common Uses**: Ticket activity, user actions, admin changes

---

### hubspot - HubSpot CRM

Polls HubSpot API for CRM events.

**Configuration**:
```yaml
sensor_type: "hubspot"
hubspot:
  api_key: "hive://secret/hubspot-key"       # Required: Private app token
  polling_seconds: 300                       # Optional
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "hubspot"
```

**Common Uses**: Contact events, deal updates, CRM activity

---

## Generic/Custom Adapters

### webhook - Webhook Receiver

Creates an HTTPS endpoint to receive webhook data.

**Configuration** (via Hive `cloud_sensor`):
```yaml
sensor_type: "webhook"
webhook:
  secret: "hard-to-guess-secret"    # Required: URL secret component
  client_options:
    identity:
      oid: "org-id"
      installation_key: "install-key"
    platform: "json"
    sensor_seed_key: "webhook-ingestion"
```

**Get Webhook URL**:
```bash
python3 -c "import limacharlie; print(limacharlie.Manager().getOrgURLs()['hooks'])"
# Returns: https://HOOKDOMAIN.hook.limacharlie.io
# Full URL: https://HOOKDOMAIN.hook.limacharlie.io/OID/HOOKNAME/SECRET
```

**Send Data**:
```bash
# Single JSON object
curl -X POST https://HOOKDOMAIN.hook.limacharlie.io/OID/webhook-name/secret \
  -H "Content-Type: application/json" \
  -d '{"event": "test"}'

# Array of objects
curl -X POST https://HOOKDOMAIN.hook.limacharlie.io/OID/webhook-name/secret \
  -H "Content-Type: application/json" \
  -d '[{"event": "test1"}, {"event": "test2"}]'

# NDJSON (newline-delimited)
curl -X POST https://HOOKDOMAIN.hook.limacharlie.io/OID/webhook-name/secret \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @events.ndjson
```

**Common Uses**: Custom integrations, API webhooks, third-party services

---

### json - Generic JSON

Reads raw JSON from various sources (use with file, stdin, etc.).

**Configuration**: Use `platform: "json"` with other adapter types like `file` or `stdin`.

---

## Advanced Configuration Options

### Data Mapping

```yaml
client_options:
  mapping:
    # Field extraction
    sensor_key_path: "device_id"           # Unique sensor identifier
    sensor_hostname_path: "hostname"        # Hostname field
    event_type_path: "eventType"           # Event type classification
    event_time_path: "timestamp"           # Event timestamp

    # Text parsing
    parsing_grok:
      message: '%{PATTERN:field}'          # Grok pattern
    parsing_re: '(?P<field>pattern)'       # Regex with named groups

    # Data transformation
    drop_fields:                           # Remove fields
      - "password"
      - "sensitive/data"

    # Custom transforms
    transform: "custom_transform_name"     # Contact LimaCharlie for custom
```

### Custom Indexing

```yaml
client_options:
  indexing:
    - events_included:                     # Filter by event types
        - "PutObject"
        - "GetObject"
      path: "userAgent"                    # Field to index
      index_type: "user"                   # Index category
      regexp: "email: (.+)"                # Optional: extract with regex
```

**Index Types**:
- `file_hash` - File hashes (MD5, SHA1, SHA256)
- `file_path` - File paths
- `file_name` - File names
- `domain` - Domain names
- `ip` - IP addresses
- `user` - Usernames, user IDs
- `service_name` - Service names
- `package_name` - Package names

### Grok Pattern Reference

**Common Patterns**:
- `%{IP:field}` - IPv4/IPv6 addresses
- `%{IPV4:field}` - IPv4 only
- `%{IPV6:field}` - IPv6 only
- `%{HOSTNAME:field}` - Hostnames
- `%{WORD:field}` - Single word (alphanumeric)
- `%{NUMBER:field}` - Integer or float
- `%{INT:field}` - Integer only
- `%{POSINT:field}` - Positive integer
- `%{GREEDYDATA:field}` - Everything remaining
- `%{DATA:field}` - Non-whitespace data
- `%{QUOTEDSTRING:field}` - Quoted strings
- `%{UUID:field}` - UUIDs
- `%{MAC:field}` - MAC addresses
- `%{URI:field}` - URIs
- `%{PATH:field}` - File paths
- `%{EMAILADDRESS:field}` - Email addresses

**Timestamp Patterns**:
- `%{TIMESTAMP_ISO8601:field}` - ISO 8601 (2024-01-01T00:00:00Z)
- `%{SYSLOGTIMESTAMP:field}` - Syslog format (Jan 1 00:00:00)
- `%{HTTPDATE:field}` - HTTP log format
- `%{DATE:field}` - Various date formats

**Log Patterns**:
- `%{LOGLEVEL:field}` - Log levels (DEBUG, INFO, WARN, ERROR, etc.)
- `%{SYSLOGPROG:field}` - Syslog program name
- `%{SYSLOGFACILITY:field}` - Syslog facility

**Custom Patterns**:
```yaml
parsing_grok:
  message: '%{CUSTOM_PATTERN:field}'
  custom_patterns:
    CUSTOM_PATTERN: 'regex pattern here'
```

### Regex Pattern Reference

Use named capture groups: `(?P<name>pattern)`

**Examples**:
```yaml
# Extract timestamp, host, and message
parsing_re: '(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<host>\S+) (?P<message>.*)'

# Extract IP and port
parsing_re: 'src=(?P<src_ip>\d+\.\d+\.\d+\.\d+):(?P<src_port>\d+)'

# Extract key-value pairs
parsing_re: 'user=(?P<user>\w+) action=(?P<action>\w+) result=(?P<result>\w+)'
```

**Regex Tips**:
- Use Go regex syntax (different from Python/Perl)
- Test patterns at https://regex101.com (select Golang flavor)
- `\d` - digit, `\w` - word char, `\s` - whitespace
- `\S` - non-whitespace, `\D` - non-digit
- `+` - one or more, `*` - zero or more, `?` - optional
- `.` - any character, `\.` - literal dot

## Multi-Adapter Configuration

Run multiple adapters in a single process using YAML documents separated by `---`:

```yaml
file:
  file_path: "/var/log/app1/*.json"
  client_options:
    identity:
      oid: "org-id"
      installation_key: "key"
    platform: "json"
    sensor_seed_key: "app1"

---

file:
  file_path: "/var/log/app2/*.log"
  client_options:
    identity:
      oid: "org-id"
      installation_key: "key"
    platform: "text"
    sensor_seed_key: "app2"

---

syslog:
  port: 1514
  client_options:
    identity:
      oid: "org-id"
      installation_key: "key"
    platform: "text"
    sensor_seed_key: "syslog"
```

Run with: `./lc_adapter multi-config.yaml`

## Cloud-Managed Adapters

Deploy adapters that fetch configuration from LimaCharlie cloud.

**Step 1**: Create configuration in `external_adapter` Hive:
```yaml
sensor_type: syslog
syslog:
  port: 1514
  client_options:
    identity:
      oid: "org-id"
      installation_key: "key"
    platform: "text"
    sensor_seed_key: "managed-syslog"
```

**Step 2**: Note the GUID from the Hive record's `sys_mtd` section

**Step 3**: Deploy adapter:
```bash
./lc_adapter cloud conf_guid=XXXXXXXXXXXXXXX oid=YYYYYYYYYYYY
```

The adapter automatically updates configuration within ~1 minute of cloud changes.

## Adapter Binary Commands

**View help**:
```bash
./lc_adapter
./lc_adapter [adapter_type]
```

**Run adapter**:
```bash
./lc_adapter [adapter_type] key=value key2=value2 ...
```

**Run with config file**:
```bash
./lc_adapter config.yaml
```

**Install as Windows service**:
```powershell
.\lc_adapter.exe -install:service-name [adapter_type] [options]
.\lc_adapter.exe -remove:service-name
```

**Healthcheck endpoint**:
```bash
./lc_adapter [adapter_type] ... healthcheck=8080
curl http://localhost:8080/health
```
