---
name: configuring-external-datasources
description: Configure and deploy LimaCharlie external data sources (Cloud Sensors, Adapters, USP, External Adapters) for ingesting telemetry from cloud platforms, logs, webhooks, and third-party services. Use when users need to connect AWS, Azure, GCP, Syslog, webhooks, or any external telemetry source to LimaCharlie.
allowed-tools:
  - Read
  - WebFetch
  - WebSearch
  - mcp__limacharlie__list_cloud_sensors
  - mcp__limacharlie__get_cloud_sensor
  - mcp__limacharlie__set_cloud_sensor
  - mcp__limacharlie__delete_cloud_sensor
  - mcp__limacharlie__list_external_adapters
  - mcp__limacharlie__get_external_adapter
  - mcp__limacharlie__set_external_adapter
  - mcp__limacharlie__delete_external_adapter
  - mcp__limacharlie__get_platform_names
  - mcp__limacharlie__get_event_types_with_schemas_for_platform
  - mcp__limacharlie__get_event_schema
  - mcp__limacharlie__list_installation_keys
  - mcp__limacharlie__create_installation_key
  - mcp__limacharlie__get_sensor_info
  - mcp__limacharlie__list_sensors
  - mcp__limacharlie__get_org_info
---

# Configuring LimaCharlie External Data Sources

This skill provides comprehensive knowledge for configuring LimaCharlie external data sources. External data sources enable ingestion of telemetry from cloud platforms (AWS, Azure, GCP), log aggregators (Syslog, SIEM), SaaS applications (Office 365, Okta, Slack), and custom webhooks. External data sources appear as first-class sensors in LimaCharlie, enabling full Detection & Response rule application.

**CRITICAL: DO NOT USE ANY LIMACHARLIE CLI TO PERFORM OPERATIONS DURING THE ONBOARDING (excluding Adapters themselves), USE THE MCP SERVER**

## When to Use This Skill

This skill provides expert knowledge for configuring and deploying LimaCharlie external data sources:

- **Cloud-to-cloud adapters** - AWS, Azure, GCP, Office 365, Okta, and other SaaS platforms
- **On-premise adapters** - Syslog listeners, file monitoring, custom log collectors
- **Parsing and transformation** - Mapping, field extraction, custom indexing for external telemetry

## Available Tools

You have access to the **limacharlie** MCP server with these focused tools for external data source configuration:

### Cloud Sensor Management Tools

Complete CRUD operations for cloud-to-cloud adapters:

- `list_cloud_sensors` - List all cloud sensors (external adapters) in the organization
  - Returns: Array of cloud sensor configurations with metadata
  - Use for: Viewing existing external data sources
- `get_cloud_sensor` - Get configuration for a specific cloud sensor
  - Parameters: `name` (cloud sensor identifier)
  - Use for: Inspecting existing adapter configuration
- `set_cloud_sensor` - Create or update a cloud sensor configuration
  - Parameters: `name`, `config` (JSON configuration), optional `ttl`
  - Use for: Deploying new adapters or updating configurations
- `delete_cloud_sensor` - Delete a cloud sensor configuration
  - Parameters: `name` (cloud sensor identifier)
  - Use for: Removing cloud-to-cloud adapters

### External Adapter Management Tools

Complete CRUD operations for on-prem adapters with cloud management:

- `list_external_adapters` - List external adapters configured in the organization
  - Returns: External adapter records with GUIDs and configurations
  - Use for: Viewing on-prem adapters with cloud management
- `get_external_adapter` - Get configuration for a specific external adapter
  - Parameters: `name` (external adapter identifier)
  - Use for: Inspecting on-prem adapter configuration
- `set_external_adapter` - Create or update an external adapter configuration
  - Parameters: `name`, `config` (YAML configuration), optional metadata
  - Use for: Creating cloud-managed on-prem adapter configs
- `delete_external_adapter` - Delete an external adapter configuration
  - Parameters: `name` (external adapter identifier)
  - Use for: Removing external adapter records

### Installation Key Management Tools

Manage authentication keys for adapters:

- `list_installation_keys` - List all installation keys in the organization
  - Returns: Array of installation keys with descriptions and tags
  - Use for: Finding existing keys or verifying key availability
- `create_installation_key` - Create a new installation key
  - Parameters: `description`, optional `tags`
  - Use for: Creating dedicated keys for new adapters

### Schema Discovery Tools

Validate data formats and field mappings:

- `get_platform_names` - List available platforms (json, text, aws, gcp, carbon_black, etc.)
  - Use for: Validating platform values in adapter configs
- `get_event_types_with_schemas_for_platform` - Get available event types for a platform
  - Parameters: `platform` (e.g., "windows", "linux", "json")
  - Use for: Understanding what event types to expect from a platform
- `get_event_schema` - Get field definitions for specific event types
  - Parameters: `name` (event type like "evt:NEW_PROCESS")
  - Use for: Validating field paths in mapping configurations

### Verification Tools

Confirm successful adapter deployment:

- `get_sensor_info` - Get details about a specific sensor (including adapters)
  - Parameters: `sid` (Sensor ID)
  - Use for: Verifying adapter appeared as a sensor, checking metadata
- `list_sensors` - List all sensors with optional filtering
  - Use for: Confirming adapter sensors are present
- `get_org_info` - Get organization information
  - Use for: Retrieving OID and other details needed for adapter configs

## Adapter Fundamentals

### Adapter Types: On-Prem vs Cloud-to-Cloud

LimaCharlie supports two deployment models for external data ingestion:

**On-Premise Adapters (Binary/Docker)**
- Deploy the LC Adapter binary on your infrastructure
- Supports all adapter types (Syslog, file monitoring, stdin, etc.)
- Can be cloud-managed via `external_adapter` records
- Available for Windows, Linux, macOS, Docker, and more platforms
- Best for: Private networks, custom parsing, local file monitoring

**Cloud-to-Cloud Adapters**
- Direct connection between LimaCharlie cloud and your cloud source
- No binary deployment required - managed entirely through configuration
- Supports major cloud platforms and SaaS providers
- Created via `cloud_sensor` Hive records using the `set_cloud_sensor` MCP tool
- Best for: AWS, Azure, GCP, Office 365, and other cloud services

### Core Adapter Configuration

All adapters require these core configurations:

**Required client_options:**
- `client_options.identity.oid` - Your LimaCharlie Organization ID
- `client_options.identity.installation_key` - Installation Key for authentication
- `client_options.platform` - Data format (json, text, aws, gcp, carbon_black, etc.)
- `client_options.sensor_seed_key` - Unique identifier for stable Sensor ID generation
- `client_options.hostname` - Human-readable hostname for the adapter

**Optional but important:**
- `client_options.mapping` - Parsing, field extraction, and transformation rules
- `client_options.indexing` - Custom indexing for IOC search optimization

## Common Adapter Workflows

### Workflow 1: Deploying a Cloud-to-Cloud Adapter

```
1. Identify the data source type
   - AWS CloudTrail, Azure Event Hub, GCP PubSub, Office 365, etc.
   ↓
2. Check existing adapters
   - Use the `list_cloud_sensors` MCP tool to see what's already configured
   ↓
3. Gather cloud credentials
   - API keys, connection strings, bucket names, etc.
   - Specific to each adapter type (see reference below)
   ↓
4. Build configuration
   - Use adapter type templates as starting point
   - Include required client_options
   ↓
5. Deploy with the `set_cloud_sensor` MCP tool
   - Name: Descriptive identifier
   - Config: Full adapter configuration in JSON/YAML format
   ↓
6. Verify data flow
   - Check sensor list using the `list_sensors` MCP tool
   - View timeline for incoming events
   - Validate with LCQL query
```

### Workflow 2: Deploying an On-Prem Adapter

```
1. Download adapter binary
   - Select appropriate platform from downloads.limacharlie.io
   - Or use Docker image: refractionpoint/lc-adapter
   ↓
2. Create configuration file (YAML)
   - Define adapter type (syslog, file, stdin, etc.)
   - Include all client_options
   - Add type-specific parameters
   ↓
3. Optional: Create external_adapter record for cloud management
   - Use the `list_external_adapters` MCP tool to check existing
   - Note the GUID for cloud-managed configuration
   ↓
4. Deploy and start
   - Run binary with config file or inline parameters
   - For persistence: Install as service (Windows/Linux)
   ↓
5. Monitor and verify
   - Check adapter logs for connection status
   - Verify sensor appears in LimaCharlie
   - Validate data ingestion with queries
```

### Workflow 3: Creating a Webhook Adapter

```
1. Create webhook cloud sensor configuration
   - sensor_type: "webhook"
   - Define secret value for URL authentication
   - Configure client_options
   ↓
2. Deploy with the `set_cloud_sensor` MCP tool
   ↓
3. Retrieve webhook URL
   - Format: https://[domain]/[OID]/[webhook_name]/[secret]
   - Or provide secret in lc-secret header
   ↓
4. Configure source to send webhooks
   - Point third-party service to webhook URL
   - Test with sample POST request
   ↓
5. Verify data ingestion
   - Check Timeline for incoming events
```

### Workflow 4: Parsing and Mapping Custom Data

```
1. Understand source data format
   - JSON, text logs, CEF, custom format
   ↓
2. Define parsing strategy
   - JSON: Direct field extraction
   - Text: Grok patterns or regex with named groups
   - Key/Value: Regex for pair extraction
   ↓
3. Configure extractors
   - event_type_path: Define event type from data field
   - event_time_path: Extract timestamp
   - sensor_hostname_path: Extract hostname
   - sensor_key_path: Define unique sensor identifier
   ↓
4. Apply transformations (optional)
   - Drop sensitive fields
   - Rename fields
   - Apply D&R-style transforms
   ↓
5. Configure custom indexing (optional)
   - Define IOC extraction patterns
   - Specify index types (file_hash, domain, ip, user)
```

## Adapter Type Reference

### Syslog Adapter

**Use case:** Collect syslog events via TCP/UDP listener

**Deployment:** On-prem binary or Docker

**Key configurations:**
- `port` - Listen port (default: 514)
- `iface` - Interface to bind (default: all)
- `is_udp` - Use UDP instead of TCP (default: false)
- `ssl_cert` / `ssl_key` - Optional TLS support

**Common platforms:** text, cef, json

**Example:**
```yaml
sensor_type: syslog
syslog:
  port: 1514
  iface: "0.0.0.0"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    hostname: "syslog-collector"
    platform: "text"
    sensor_seed_key: "syslog-main"
    mapping:
      parsing_grok:
        message: "%{TIMESTAMP_ISO8601:timestamp} %{HOSTNAME:host} %{WORD:process}\\[%{INT:pid}\\]: %{GREEDYDATA:message}"
      event_type_path: "process"
      event_time_path: "timestamp"
```

### AWS CloudTrail Adapter

**Use case:** Ingest AWS CloudTrail audit logs

**Deployment:** Cloud-to-cloud (S3 or SQS) or on-prem binary

**Source options:**
- S3 bucket with CloudTrail logs
- SQS queue receiving CloudTrail events

**Required credentials:**
- `access_key` - AWS access key
- `secret_key` - AWS secret key
- `bucket_name` (S3) or `queue_url` + `region` (SQS)

**Platform:** aws

**Cloud-to-cloud setup:** Use the `set_cloud_sensor` MCP tool

### Azure Event Hub Adapter

**Use case:** Ingest Azure logs via Event Hub

**Deployment:** Cloud-to-cloud or on-prem binary

**Required credentials:**
- Event Hub connection string
- Consumer group (optional)

**Platform:** json or azure (for built-in parsing)

**Supports:** Activity Logs, Key Vault, NSG, Kubernetes, SQL Audit

### Webhook Adapter

**Use case:** Custom HTTP POST integrations

**Deployment:** Cloud-to-cloud only

**Configuration:**
- `secret` - Authentication token for URL
- `signature_secret` / `signature_header` / `signature_scheme` - Optional webhook signature validation

**Supported formats:**
- Single JSON object: `{"some":"data"}`
- Array of JSON: `[{...}, {...}]`
- Newline-delimited JSON (NDJSON)
- Gzip-compressed variants

**Platform:** json (typically)

### File Adapter

**Use case:** Monitor and ingest log files

**Deployment:** On-prem binary only

**Key configurations:**
- `file_path` - Path to file(s), supports wildcards
- Automatically follows file rotation

**Platform:** json, text, or specialized (carbon_black, etc.)

**Example:**
```yaml
sensor_type: file
file:
  file_path: "/var/log/application/*.json"
  client_options:
    identity:
      oid: "your-oid"
      installation_key: "your-key"
    platform: "json"
    sensor_seed_key: "app-logs"
    hostname: "app-server-01"
    mapping:
      event_type_path: "log_type"
```

### Office 365 / Microsoft 365 Adapter

**Use case:** Ingest O365 audit logs

**Deployment:** Cloud-to-cloud

**Required:**
- Azure AD application credentials
- Tenant ID
- API permissions for O365 Management API

**Platform:** json with built-in O365 parsing

**Setup:** Use the `set_cloud_sensor` MCP tool for configuration

### Okta Adapter

**Use case:** Ingest Okta system logs

**Deployment:** Cloud-to-cloud

**Required:**
- Okta API token
- Okta domain

**Platform:** json

### Google Cloud PubSub Adapter

**Use case:** Ingest GCP logs via Cloud Pub/Sub

**Deployment:** Cloud-to-cloud or on-prem binary

**Required:**
- GCP service account credentials (JSON key file)
- Project ID
- Subscription ID

**Platform:** gcp or json

## Parsing and Mapping Deep Dive

### Transformation Pipeline Order

Data flows through this processing pipeline:

```
1. Regular Expression / Grok Parsing (text → JSON)
   ↓
2. Built-in Platform Parsers (cloud-specific formats)
   ↓
3. Field Extractors (event type, time, hostname, sensor key)
   ↓
4. Custom Mappings (field transforms, renames, drops)
   ↓
5. Indexing (IOC extraction for search optimization)
```

### Grok Pattern Parsing

For text logs, use Grok patterns for structured extraction:

**Syntax:** `%{PATTERN_NAME:field_name}`

**Common patterns:**
- `%{IP:field}` - IPv4/IPv6 addresses
- `%{NUMBER:field}` - Numeric values
- `%{WORD:field}` - Single words
- `%{TIMESTAMP_ISO8601:field}` - ISO timestamps
- `%{GREEDYDATA:field}` - All remaining data

**Configuration:**
```yaml
client_options:
  mapping:
    parsing_grok:
      message: "%{IP:src_ip} - - \\[%{TIMESTAMP_ISO8601:timestamp}\\] \"%{WORD:method} %{DATA:uri}\" %{NUMBER:status} %{NUMBER:bytes}"
    event_type_path: "method"
    event_time_path: "timestamp"
```

### Regular Expression Parsing

Alternative to Grok for custom patterns:

**Named capture groups** (one JSON object per log line):
```yaml
parsing_re: "(?P<timestamp>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}) (?P<level>\\w+) (?P<message>.*)"
```

**Key/Value extraction** (CEF-style logs):
```yaml
parsing_re: "(?:<\\d+>\\s*)?(\\w+)=(\".*?\"|\\S+)"
```
Results in: `{"key1": "value1", "key2": "value2", ...}`

### Field Extractors

Map JSON fields to LimaCharlie core concepts:

**Path syntax:** Use `/` to traverse nested JSON
- `field` - Top-level field
- `parent/child` - Nested field
- `data/user/email` - Deeply nested

**Extractors:**
- `sensor_key_path` - Unique sensor identifier (generates stable SID)
- `sensor_hostname_path` - Hostname for the sensor
- `event_type_path` - Event type name (supports template strings)
- `event_time_path` - Event timestamp

**Template event types:**
```yaml
event_type_path: "{{.action}}_{{.resource}}"
# With data: {action: "CREATE", resource: "USER"}
# Results in: CREATE_USER event type
```

### Field Transformations

**Drop sensitive fields:**
```yaml
client_options:
  mapping:
    drop_fields:
      - "credentials/password"
      - "auth_token"
      - "api_keys"
```

**Apply transforms:**
```yaml
client_options:
  mapping:
    transform:
      - op: "add_tag"
        value: "external_source"
      - op: "rename"
        path: "src_ip"
        to: "source_ip"
```

### Custom Indexing

Optimize IOC searches by defining custom indexes:

```yaml
client_options:
  indexing:
    - events_included: ["LOGIN"]
      path: "user/email"
      index_type: "user"
    - events_included: ["FILE_ACCESS"]
      path: "file/path"
      index_type: "file_path"
    - path: "network/remote_ip"
      index_type: "ip"
```

**Supported index types:**
- `file_hash`, `file_path`, `file_name`
- `domain`, `ip`
- `user`
- `service_name`, `package_name`

## Multi-Adapter Deployment

Deploy multiple adapter instances in a single process using YAML multi-document format:

```yaml
file:
  client_options:
    identity: {...}
    platform: json
    sensor_seed_key: logs-dir1
  file_path: /var/log/app1/*.json

---

file:
  client_options:
    identity: {...}
    platform: json
    sensor_seed_key: logs-dir2
  file_path: /var/log/app2/*.json

---

file:
  client_options:
    identity: {...}
    platform: json
    sensor_seed_key: logs-dir3
  file_path: /var/log/app3/*.json
```

## Installation as Service

### Windows Service

Install adapter as Windows service:
```powershell
lc_adapter.exe -install:service_name <adapter_type> <configurations>
```

Example:
```powershell
lc_adapter.exe -install:syslog_collector syslog port=514 client_options.identity.installation_key=... client_options.identity.oid=...
```

Remove service:
```powershell
lc_adapter.exe -remove:service_name
```

### Linux systemd Service

Create service file `/etc/systemd/system/lc-adapter.service`:

```ini
[Unit]
Description=LimaCharlie Adapter
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/lc-adapter file config.yaml
WorkingDirectory=/opt/lc-adapter
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable lc-adapter
sudo systemctl start lc-adapter
sudo systemctl status lc-adapter
```

## Cloud-Managed On-Prem Adapters

Deploy on-prem adapters with cloud-based configuration management:

**Benefits:**
- Update configurations remotely without local access
- Centralized management for distributed deployments
- Automatic configuration sync within ~1 minute

**Setup:**

1. Create `external_adapter` record using the `set_external_adapter` MCP tool
   - Contains full adapter YAML configuration
   - Note the GUID from the record

2. Deploy adapter with cloud configuration:
   ```bash
   ./lc_adapter cloud conf_guid=XXXXXXXXXXXXXXXX oid=YYYYYYYYYYYYYYYY
   ```

3. Update configuration remotely anytime
   - Changes propagate automatically to deployed adapters

**Requires:** `externaladapter.*` permissions

## Using MCP Tools for Adapter Management

### Listing Existing Adapters

**Cloud-to-cloud adapters:**

**MCP Tool:** `mcp__limacharlie__list_cloud_sensors`

**Parameters:** None

**Returns:** Array of cloud sensor configurations with metadata

**Usage:** Returns all cloud sensors configured in the organization, including names, types, and configuration details.

**On-prem with cloud management:**

**MCP Tool:** `mcp__limacharlie__list_external_adapters`

**Parameters:** None

**Returns:** External adapter records with GUIDs and configurations

**Usage:** Returns all external adapter records that enable cloud-based configuration management for on-premise adapter deployments.

### Deploying a New Cloud Adapter

**MCP Tool:** `mcp__limacharlie__set_cloud_sensor`

**Parameters:**
- `name` (string): Unique identifier for the cloud sensor (e.g., "aws-cloudtrail-prod")
- `config` (JSON object): Complete adapter configuration
- `ttl` (integer, optional): Time-to-live for the configuration

**Returns:** Success confirmation

**Example configuration:**
```json
{
  "name": "aws-cloudtrail-prod",
  "config": {
    "sensor_type": "s3",
    "s3": {
      "bucket_name": "my-cloudtrail-logs",
      "access_key": "AKIAXXXXX",
      "secret_key": "xxxxx",
      "client_options": {
        "identity": {
          "oid": "your-oid",
          "installation_key": "your-key"
        },
        "platform": "aws",
        "sensor_seed_key": "cloudtrail-prod",
        "hostname": "aws-cloudtrail"
      }
    }
  }
}
```

### Inspecting Adapter Configuration

**MCP Tool:** `mcp__limacharlie__get_cloud_sensor`

**Parameters:**
- `name` (string): Cloud sensor identifier

**Returns:** Full configuration and metadata for the specified cloud sensor

**Usage:** Retrieves complete configuration of a cloud sensor to review settings, credentials, or troubleshoot connectivity issues.

### Verifying Data Flow

After deploying an adapter, verify ingestion using these MCP tools:

**Check if adapter appears as sensor:**

**MCP Tool:** `mcp__limacharlie__list_sensors`

**Parameters:** None (supports optional filtering)

**Returns:** List of all sensors including adapter-based sensors

**Get details about the adapter sensor:**

**MCP Tool:** `mcp__limacharlie__get_sensor_info`

**Parameters:**
- `sid` (string): Sensor ID of the adapter

**Returns:** Detailed sensor information including platform, hostname, and status

**To query and verify events are flowing:** Use the `querying-limacharlie` skill to run LCQL queries and search for events from the adapter. Query by hostname, platform, or sensor ID to confirm telemetry ingestion.

## Best Practices

### Adapter Naming and Organization

- Use descriptive `sensor_seed_key` values: `syslog-firewall`, `aws-prod-cloudtrail`, `o365-audit-logs`
- Set meaningful `hostname` values for easy identification in UI
- Apply tags during deployment for grouping and filtering

### Security Considerations

- Use least-privilege credentials for cloud connections
- Rotate API keys and connection secrets regularly
- Avoid hardcoding secrets - use environment variables or secure vaults
- For webhooks, use strong unpredictable secret values
- Enable TLS for Syslog adapters when possible

### Parsing Strategy

- Start with built-in platform parsers when available
- Use Grok patterns for common log formats (faster than regex)
- Test parsing with sample data before full deployment
- Keep extractors minimal - extract only necessary fields

### Performance Optimization

- Use specific event_type_path for better querying and detection
- Configure custom indexing for IOC-heavy data sources
- Drop unnecessary fields early in pipeline with `drop_fields`
- For high-volume sources, consider filtering at source if possible

### Monitoring and Maintenance

- Monitor adapter logs for connection issues
- Set up D&R rules to alert on adapter disconnections
- Periodically review and update parsing patterns
- Test configuration changes in non-production first

## Troubleshooting

### Adapter Not Connecting

**Symptoms:** No sensor appears in LimaCharlie
**Check:**
- Installation Key validity (`installation_key` and `oid` match)
- Network connectivity to LimaCharlie endpoints
- Credentials for cloud-to-cloud adapters
- Adapter logs for error messages

**Cloud-to-cloud specific:**
- Verify credentials have correct permissions
- Check cloud source is generating data
- Review cloud_sensor configuration with `get_cloud_sensor`

**On-prem specific:**
- Confirm adapter binary is running
- Check firewall rules allow outbound HTTPS
- Verify adapter version is current

### Data Not Being Parsed Correctly

**Symptoms:** Events appear but fields are wrong or missing
**Check:**
- Platform value matches data format
- Grok pattern or regex syntax is correct
- Test patterns with sample data outside LimaCharlie
- Verify field paths in extractors exist in parsed data

**Debug approach:**
1. Start with minimal parsing (just platform setting)
2. Add Grok/regex parsing incrementally
3. Add extractors one at a time
4. Add transformations last

### Events Not Showing in Timeline

**Symptoms:** Sensor appears but no events
**Check:**
- Source is actually generating data
- Adapter collection method is configured correctly
- File paths, ports, or endpoints are correct
- Parsing isn't failing silently (check adapter logs)
- Timeframe filter in Timeline view

### Performance Issues

**Symptoms:** High latency, dropped events, resource usage
**Solutions:**
- Reduce parsing complexity
- Drop unnecessary fields early
- Increase adapter resources (CPU, memory)
- Split high-volume sources across multiple adapters
- Optimize Grok patterns (avoid greedy captures at start)

## Key Differences from Endpoint Agents

This skill focuses on **external data ingestion**, not endpoint agents:

- Endpoint agents: Native EDR sensors installed on hosts
- Adapters/Cloud Sensors: External telemetry from cloud, logs, SaaS, custom sources
- Both appear as "Sensors" in LimaCharlie but have different capabilities
- Adapters provide telemetry ingestion; agents provide telemetry + tasking

## Additional Resources

For adapter-specific details, consult the documentation:
- Adapter Types: /limacharlie/doc/Sensors/Adapters/Adapter_Types/
- Deployment Guides: /limacharlie/doc/Sensors/Adapters/Adapter_Tutorials/
- Configuration Reference: /limacharlie/doc/Sensors/Adapters/adapter-usage.md
