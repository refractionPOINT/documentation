# External Telemetry Onboarding Reference

This is the complete technical reference for LimaCharlie adapters, covering all adapter types, configuration parameters, and advanced features.

## Table of Contents

1. [Complete Adapter Type Catalog](#complete-adapter-type-catalog)
2. [Installation Keys Deep Dive](#installation-keys-deep-dive)
3. [Configuration Anatomy](#configuration-anatomy)
4. [Data Mapping and Transformation](#data-mapping-and-transformation)
5. [Platform Types Reference](#platform-types-reference)
6. [Indexing Configuration](#indexing-configuration)
7. [MCP Commands Reference](#mcp-commands-reference)
8. [Cloud Provider Requirements](#cloud-provider-requirements)

---

## Complete Adapter Type Catalog

LimaCharlie supports 50+ adapter types across multiple categories.

### Cloud Provider Adapters

| Adapter Type | Platform | Description | Connection Method | Credentials Needed |
|--------------|----------|-------------|-------------------|-------------------|
| `s3` | `aws` | AWS S3 bucket polling | Cloud-to-cloud | Access key, secret key, bucket name |
| `sqs` | `aws` | AWS SQS message queue | Cloud-to-cloud | Access key, secret key, queue URL, region |
| `aws_guardduty` | `json` | AWS GuardDuty findings | Cloud-to-cloud | Access key, secret key, region |
| `azure_event_hub` | `azure_monitor`, `azure_ad`, `msdefender`, `json` | Azure Event Hub streaming | Cloud-to-cloud | Connection string with EntityPath |
| `google_cloud_pubsub` | `gcp`, `json` | GCP Pub/Sub messaging | Cloud-to-cloud | Service account JSON, project ID, subscription |
| `google_cloud_storage` | `json` | GCP Cloud Storage buckets | Cloud-to-cloud | Service account JSON, bucket name |

### SaaS Application Adapters

| Adapter Type | Platform | Description | Connection Method | Credentials Needed |
|--------------|----------|-------------|-------------------|-------------------|
| `office365` | `office365` | Microsoft 365 Management API | Cloud-to-cloud | Tenant ID, client ID, client secret, domain |
| `okta` | `json` | Okta system logs | Cloud-to-cloud | API token, URL |
| `google_workspace` | `json` | Google Workspace admin logs | Cloud-to-cloud | Service account JSON, customer ID |
| `slack_audit_logs` | `json` | Slack audit events | Cloud-to-cloud | OAuth token |
| `duo` | `json` | Duo authentication logs | Cloud-to-cloud | Integration key, secret key, API hostname |
| `zendesk` | `json` | Zendesk audit logs | Cloud-to-cloud | API token, subdomain |
| `hubspot` | `json` | HubSpot activity | Cloud-to-cloud | API key |
| `pandadoc` | `json` | PandaDoc audit logs | Cloud-to-cloud | API key |
| `it_glue` | `json` | IT Glue activity | Cloud-to-cloud | API key, region |

### Security Tool Adapters

| Adapter Type | Platform | Description | Connection Method | Credentials Needed |
|--------------|----------|-------------|-------------------|-------------------|
| `falconcloud` | `falconcloud` | CrowdStrike Falcon EDR | Cloud-to-cloud | Client ID, client secret |
| `microsoft_defender` | `msdefender` | Microsoft Defender alerts | Cloud-to-cloud | Tenant ID, client ID, client secret |
| `microsoft_entra_id` | `azure_ad` | Microsoft Entra ID (Azure AD) | Cloud-to-cloud | Tenant ID, client ID, client secret |
| `sophos` | `json` | Sophos Central events | Cloud-to-cloud | Client ID, client secret, region |
| `vmware_carbon_black` | `carbon_black` | VMware Carbon Black | Cloud-to-cloud | API ID, API secret, org key, URL |
| `sentinelone` | `json` | SentinelOne events | Cloud-to-cloud | API token, URL |
| `mimecast` | `json` | Mimecast email security | Cloud-to-cloud | App ID, app key, access key, secret key |
| `canarytokens` | `json` | Canary token alerts | Webhook | Canary webhook |
| `sublime_security` | `json` | Sublime Security email events | Cloud-to-cloud | API key |

### Network and Infrastructure Adapters

| Adapter Type | Platform | Description | Connection Method | Credentials Needed |
|--------------|----------|-------------|-------------------|-------------------|
| `syslog` | `text`, `cef` | Syslog listener (TCP/UDP) | On-prem binary | Port, interface config |
| `tailscale` | `json` | Tailscale network logs | Cloud-to-cloud | API key, tailnet |
| `cato` | `json` | CATO SASE platform | Cloud-to-cloud | Account ID, API key |

### Local Collection Adapters

| Adapter Type | Platform | Description | Connection Method | Credentials Needed |
|--------------|----------|-------------|-------------------|-------------------|
| `file` | `json`, `text` | Monitor local file/directory | On-prem binary | File path, watch pattern |
| `stdin` | `json`, `text` | Read from stdin pipe | On-prem binary | None (pipe data in) |
| `evtx` | `json` | Windows EVTX files | On-prem binary | EVTX file path |
| `windows_event_log` | `json` | Live Windows Event Log | On-prem binary | Log channel name |
| `mac_unified_logging` | `json` | macOS unified logs | On-prem binary | Predicates, log stream |
| `iis` | `text` | IIS web server logs | On-prem binary | IIS log file path |
| `kubernetes_pods_logs` | `text`, `json` | Kubernetes pod logs | On-prem binary | Kubeconfig, namespace |

### Generic and Structured Data Adapters

| Adapter Type | Platform | Description | Connection Method | Credentials Needed |
|--------------|----------|-------------|-------------------|-------------------|
| `json` | `json` | Generic JSON ingestion | On-prem binary | Varies by source |
| `imap` | `text` | Email via IMAP | On-prem binary | IMAP server, credentials |

---

## Installation Keys Deep Dive

### Components of an Installation Key

An Installation Key is a Base64-encoded string containing four components:

1. **Organization ID (OID)**
   - Your unique LimaCharlie tenant identifier
   - Format: UUID (e.g., `8cbe27f4-bfa1-4afb-ba19-138cd51389cd`)
   - Determines which organization the adapter reports to
   - Find it: `limacharlie organization info`

2. **Installer ID (IID)**
   - Unique identifier for this specific installation key
   - Generated automatically when key is created
   - Format: UUID
   - Used for tracking and revoking keys

3. **Tags**
   - List of labels automatically applied to sensors using this key
   - Examples: `["aws", "production"]`, `["firewall", "network"]`
   - Use for organizing sensors and targeting D&R rules
   - Best practice: At least one tag identifying the source type

4. **Description**
   - Human-readable label for the key
   - Helps differentiate keys in the UI
   - Examples: "AWS CloudTrail Production", "Office 365 Audit Logs"

### Creating Installation Keys

**Via MCP**:
```bash
# Basic key
limacharlie installation_key create \
  --description "My Data Source" \
  --tags "tag1,tag2"

# With custom settings (via REST API wrapper)
limacharlie installation_key create \
  --description "Unpinned SSL Key" \
  --use-public-root-ca true
```

**Via REST API**:
```bash
curl -X POST https://api.limacharlie.io/v1/orgs/{oid}/installer_keys \
  -H "Authorization: bearer {jwt}" \
  -d '{
    "description": "My Adapter Key",
    "tags": ["aws", "production"],
    "use_public_root_ca": false
  }'
```

### SSL Certificate Pinning

By default, sensors and adapters use **pinned SSL certificates** for communication with LimaCharlie. This prevents traffic interception but requires direct connectivity.

If you need to route through a proxy or corporate SSL inspection:
- Create key with `use_public_root_ca: true`
- Allows public root CA verification instead of pinning
- Less secure but compatible with SSL-inspecting proxies

### Managing Installation Keys

**List all keys**:
```bash
limacharlie installation_key list
```

**View key details**:
```bash
limacharlie installation_key info --iid <INSTALLER_ID>
```

**Delete/revoke a key**:
```bash
limacharlie installation_key delete --iid <INSTALLER_ID>
```

**Note**: Deleting a key will disconnect all sensors/adapters using it.

---

## Configuration Anatomy

Every adapter configuration has the same core structure with adapter-specific additions.

### Required Core Configuration

```yaml
<adapter_type>:  # e.g., s3, syslog, okta, office365
  client_options:
    identity:
      oid: <ORGANIZATION_ID>           # Your LimaCharlie org UUID
      installation_key: <INSTALL_KEY>  # Base64 key from above
    platform: <PLATFORM_TYPE>          # json, aws, text, office365, etc.
    sensor_seed_key: <UNIQUE_NAME>     # Stable identifier for this adapter
    hostname: <SENSOR_HOSTNAME>        # Display name in LimaCharlie UI
    mapping:                           # Optional: data transformation
      event_type_path: <FIELD_PATH>
      event_time_path: <FIELD_PATH>
      sensor_hostname_path: <FIELD_PATH>
  # Adapter-specific fields below this
```

### Field Explanations

**`client_options.identity.oid`** (required)
- Your Organization ID
- Get it: `limacharlie organization info` or from web UI
- Must match the org where your Installation Key was created

**`client_options.identity.installation_key`** (required)
- The Installation Key Base64 string
- Created via `limacharlie installation_key create`
- Authenticates the adapter

**`client_options.platform`** (required)
- Tells LimaCharlie what data format to expect
- Enables platform-specific parsers
- Common values: `json`, `text`, `aws`, `gcp`, `office365`, `carbon_black`
- See [Platform Types Reference](#platform-types-reference) for full list

**`client_options.sensor_seed_key`** (required)
- An arbitrary unique name you choose
- Generates a deterministic Sensor ID (SID)
- **Critical**: Reusing the same seed key preserves the sensor's identity
- Best practice: Use descriptive names like `aws-cloudtrail-production`
- Allows re-deploying adapter without creating a duplicate sensor

**`client_options.hostname`** (required)
- Display name shown in LimaCharlie sensor list
- Does not need to be a real hostname
- Best practice: Descriptive of the data source (e.g., `okta-system-logs`)

**`client_options.mapping`** (optional)
- Configures how to extract/transform fields from events
- See [Data Mapping section](#data-mapping-and-transformation) below

### Runtime Configuration

Optional settings for adapter behavior:

**`healthcheck`** (integer)
- Port number for HTTP healthcheck endpoint
- Returns 200 OK if adapter is running
- Useful for Docker orchestration, load balancers
- Example: `healthcheck: 8080`

---

## Data Mapping and Transformation

Data mapping extracts key fields from raw events and transforms them into LimaCharlie's standard format.

### Transformation Pipeline Order

Events are processed in this order:

1. **Parsing** - Convert raw text to JSON using regex or grok
2. **Platform Parser** - Built-in parsers for known formats (aws, carbon_black, etc.)
3. **Field Extraction** - Extract core fields (event type, time, hostname)
4. **Custom Mappings** - Apply user-defined transformations
5. **Indexing** - Mark specific fields for searchability

### Parsing Configuration

#### Option 1: Regular Expression with Named Groups

For text logs, extract fields using regex:

```yaml
client_options:
  mapping:
    parsing_re: '(?P<date>... \d\d \d\d:\d\d:\d\d) (?P<host>.+) (?P<exe>.+?)\[(?P<pid>\d+)\]: (?P<msg>.*)'
```

**Input**:
```
Nov 09 10:57:09 penguin PackageKit[21212]: daemon quit
```

**Output JSON**:
```json
{
  "date": "Nov 09 10:57:09",
  "host": "penguin",
  "exe": "PackageKit",
  "pid": "21212",
  "msg": "daemon quit"
}
```

#### Option 2: Grok Patterns

Easier-to-read alternative to regex:

```yaml
client_options:
  mapping:
    parsing_grok:
      message: '%{TIMESTAMP_ISO8601:timestamp} %{HOSTNAME:host} %{WORD:action} %{IP:src_ip} %{IP:dst_ip}'
```

**Built-in Grok Patterns**:
- `%{IP:field_name}` - IPv4/IPv6 addresses
- `%{NUMBER:field_name}` - Numeric values
- `%{WORD:field_name}` - Single word (no whitespace)
- `%{DATA:field_name}` - Any data up to delimiter
- `%{GREEDYDATA:field_name}` - All remaining data
- `%{TIMESTAMP_ISO8601:field_name}` - ISO timestamps
- `%{LOGLEVEL:field_name}` - DEBUG, INFO, WARN, ERROR
- `%{HOSTNAME:field_name}` - Hostname pattern
- `%{INT:field_name}` - Integer

**Firewall example** (Palo Alto):
```yaml
parsing_grok:
  message: '%{TIMESTAMP_ISO8601:time} %{IP:src} %{IP:dst} %{WORD:action} %{WORD:proto} %{NUMBER:bytes}'
```

### Field Extraction

Map JSON fields to LimaCharlie's core concepts:

```yaml
client_options:
  mapping:
    event_type_path: "eventType"           # Which field = event type
    event_time_path: "timestamp"           # Which field = event timestamp
    sensor_hostname_path: "device/name"    # Which field = source hostname
    sensor_key_path: "device/id"           # Which field = unique sensor ID
```

**Path Syntax**:
- Use `/` to navigate nested JSON: `metadata/user/email`
- Example JSON:
  ```json
  {
    "metadata": {
      "user": {
        "email": "user@example.com"
      }
    }
  }
  ```
- Path `metadata/user/email` extracts: `"user@example.com"`

**Template Strings** (for `event_type_path`):
```yaml
event_type_path: "source: {{ .cloudProvider }}"
```
- Allows dynamic event types based on event content
- Uses Go template syntax

### Custom Field Transformations

**Drop unwanted fields**:
```yaml
client_options:
  mapping:
    drop_fields:
      - "internal_metadata"
      - "debug_info"
      - "temp_data"
```

**Apply transformation** (advanced):
```yaml
client_options:
  mapping:
    transform: <transform_spec>
```
See LimaCharlie transform documentation for syntax.

### Multi-Adapter Configurations

Run multiple adapter instances in one process using YAML document separators:

```yaml
file:
  client_options:
    identity:
      installation_key: <KEY>
      oid: <OID>
    platform: json
    sensor_seed_key: app-logs-1
  file_path: /var/log/app1/*.json

---

file:
  client_options:
    identity:
      installation_key: <KEY>
      oid: <OID>
    platform: json
    sensor_seed_key: app-logs-2
  file_path: /var/log/app2/*.json
```

Each adapter instance:
- Must have unique `sensor_seed_key`
- Can have different configurations
- Runs in the same process

---

## Platform Types Reference

The `platform` field determines which built-in parser is used.

| Platform Value | Description | Use For |
|----------------|-------------|---------|
| `aws` | AWS CloudTrail events | CloudTrail S3/SQS |
| `gcp` | Google Cloud Platform logs | GCP Pub/Sub, Cloud Storage |
| `azure_monitor` | Azure Monitor/Activity logs | Azure Event Hub (Monitor) |
| `azure_ad` | Azure Active Directory logs | Azure Event Hub (Entra ID) |
| `msdefender` | Microsoft Defender alerts | Azure Event Hub (Defender) |
| `office365` | Microsoft 365 audit logs | Office 365 Management API |
| `json` | Generic JSON events | Most SaaS APIs, custom apps |
| `text` | Plain text logs | Syslog, unstructured logs |
| `cef` | Common Event Format | CEF-compliant devices |
| `carbon_black` | VMware Carbon Black | Carbon Black Response/Cloud |
| `falconcloud` | CrowdStrike Falcon | Falcon streaming API |
| `linux` | Linux system logs | Syslog with Linux format |

**When unsure**: Use `json` for JSON data or `text` for plain text. LimaCharlie will still ingest it, just without specialized parsing.

---

## Indexing Configuration

Indexing makes specific fields searchable in LimaCharlie's timeline and search interfaces.

### How Indexing Works

1. **Built-in indexers** - Applied automatically for known platforms (e.g., `carbon_black`)
2. **Generic indexer** - Applied to all fields if no built-in indexer
3. **User-defined indexing** - Custom indexing rules you specify

### User-Defined Indexing

```yaml
client_options:
  indexing:
    - events_included:       # Optional: only for these event types
        - PutObject
        - GetObject
      path: userAgent        # Field to index
      index_type: user       # Category of index
    - events_excluded:       # Optional: exclude these event types
        - HealthCheck
      path: sourceIP
      index_type: ip
      regexp: "IP: (.+)"     # Optional: extract via regex
```

### Index Types (Categories)

LimaCharlie supports these index types:

- `file_hash` - File hashes (MD5, SHA1, SHA256)
- `file_path` - File paths
- `file_name` - File names
- `domain` - DNS domains
- `ip` - IP addresses
- `user` - Usernames, emails, user IDs
- `service_name` - Service/process names
- `package_name` - Software package names

**Why index?**
- Fast searches: Find all events for IP `1.2.3.4` across millions of events
- Timeline correlation: See all activity for a user/file/domain
- Detection pivoting: Rules can search indexed fields efficiently

---

## MCP Commands Reference

Common LimaCharlie MCP commands for adapter management.

### Organization Information

```bash
# Get your Organization ID and details
limacharlie organization info

# List all organizations you have access to
limacharlie organization list
```

### Installation Key Management

```bash
# Create new installation key
limacharlie installation_key create \
  --description "My Adapter" \
  --tags "tag1,tag2"

# List all keys
limacharlie installation_key list

# Get key details
limacharlie installation_key info --iid <INSTALLER_ID>

# Delete key (disconnects all sensors using it)
limacharlie installation_key delete --iid <INSTALLER_ID>
```

### Adapter/Sensor Management

```bash
# Create adapter from YAML config
limacharlie adapter create --config adapter-config.yaml

# List all sensors (includes adapters)
limacharlie sensor list

# Filter sensors
limacharlie sensor list --filter "tag:aws"
limacharlie sensor list --filter "hostname:cloudtrail"

# Get sensor details
limacharlie sensor info --sensor-id <SID>

# Delete sensor
limacharlie sensor delete --sensor-id <SID>
```

### Event Queries

```bash
# Query recent events from a sensor
limacharlie events query \
  --sensor-id <SID> \
  --limit 20

# Query with time range
limacharlie events query \
  --sensor-id <SID> \
  --start "2024-01-01T00:00:00Z" \
  --end "2024-01-02T00:00:00Z"

# Query by event type
limacharlie events query \
  --event-type "FileAccessed" \
  --limit 100
```

### Cloud Connector Management

```bash
# List cloud connectors (cloud-to-cloud adapters)
limacharlie connector list

# Get connector details
limacharlie connector info --connector-id <ID>

# Delete cloud connector
limacharlie connector delete --connector-id <ID>
```

---

## Cloud Provider Requirements

### AWS CloudTrail

**IAM Policy** (minimum permissions for S3):
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

**For SQS**:
- Add `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes`
- SQS queue must be configured to receive S3 notifications from CloudTrail bucket

### Microsoft 365

**App Registration Requirements**:
- **API**: Office 365 Management APIs
- **Permissions** (Application, not Delegated):
  - `ActivityFeed.Read` (required)
  - `ActivityFeed.ReadDlp` (for DLP events)
- **Admin Consent**: Must be granted
- **Client Secret**: Create and copy before leaving the page

**Endpoint Options**:
- `enterprise` - Commercial M365
- `gcc-gov` - GCC
- `gcc-high-gov` - GCC High
- `dod-gov` - DoD

### Azure Event Hub

**Required Information**:
- Connection string with `EntityPath` appended
- Format: `Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=<HUB_NAME>`

**Diagnostic Settings**:
- Must be configured to stream to Event Hub
- Select log categories you want
- Can stream from multiple Azure services to same hub

### Okta

**API Token Requirements**:
- Create in Okta Admin: Security → API → Tokens
- Permissions: Read-only sufficient for system logs
- No expiration or set per policy
- Token shows once - copy immediately

**Rate Limits**:
- 600 requests/minute (default)
- Adapter respects rate limits automatically

### CrowdStrike Falcon

**API Client Requirements**:
- Scope: **Event streams: Read**
- Client ID and Secret provided once on creation
- Ensure API client is active (not disabled)

**Cloud Regions**:
- Adapter auto-detects cloud region
- Works with US-1, US-2, EU-1, US-GOV-1

---

## Additional Resources

For more details on specific adapter types, see the full documentation at:
- https://docs.limacharlie.io/docs/adapter-usage
- https://docs.limacharlie.io/docs/adapter-types

For guided walkthroughs, see [EXAMPLES.md](EXAMPLES.md).

For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
