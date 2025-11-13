---
name: configuring-external-datasources
description: Manage and configure existing LimaCharlie external data sources (Cloud Sensors, Adapters, External Adapters). Update parsing rules, modify field mappings, adjust adapter configurations, optimize indexing, and troubleshoot data ingestion. Use when users need to modify, update, fix, or optimize existing external datasource configurations.
allowed-tools:
  - Read
  - WebFetch
  - WebSearch
  - Skill
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

This skill provides comprehensive knowledge for managing and modifying LimaCharlie external data sources. External data sources enable ingestion of telemetry from cloud platforms (AWS, Azure, GCP), log aggregators (Syslog, SIEM), SaaS applications (Office 365, Okta, Slack), and custom webhooks. External data sources appear as first-class sensors in LimaCharlie, enabling full Detection & Response rule application.

**CRITICAL: DO NOT USE ANY LIMACHARLIE CLI TO PERFORM CONFIGURATION OPERATIONS, USE THE MCP SERVER**

## When to Use This Skill

This skill provides expert knowledge for configuring and managing existing LimaCharlie external data sources:

- **Modifying adapter configurations** - Update credentials, change parameters, adjust collection settings
- **Parsing and transformation** - Update mapping rules, modify field extraction, fix parsing issues
- **Custom indexing** - Add, remove, or adjust IOC indexing configurations
- **Performance optimization** - Fine-tune adapter settings for better throughput and efficiency
- **Troubleshooting** - Diagnose and fix data flow issues, parsing errors, or connectivity problems

**Note:** For initial setup and onboarding of new external data sources, use the `onboarding-external-datasources` skill instead.

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

## Common Configuration Workflows

### Workflow 1: Updating a Cloud Sensor Configuration

```
1. Retrieve existing configuration
   - Use `get_cloud_sensor` MCP tool to fetch current config
   - Review current settings and identify what needs to change
   ↓
2. Modify configuration as needed
   - Update credentials or connection parameters
   - Adjust collection filters or scopes
   - Change platform or parsing settings
   ↓
3. Update with the `set_cloud_sensor` MCP tool
   - Name: Same identifier as existing sensor
   - Config: Modified configuration
   ↓
4. Verify changes
   - Check sensor list to confirm update
   - Monitor data flow for expected changes
   - Validate with LCQL query
```

### Workflow 2: Modifying Parsing and Mapping Rules

```
1. Identify parsing issue
   - Events not parsed correctly
   - Missing or incorrectly mapped fields
   - Wrong event types assigned
   ↓
2. Retrieve current adapter configuration
   - Use `get_cloud_sensor` or `get_external_adapter` MCP tool
   - Review existing mapping configuration
   ↓
3. Update parsing rules
   - Modify Grok patterns or regex
   - Adjust field extractors (event_type_path, event_time_path, etc.)
   - Update transformations (drop_fields, rename, etc.)
   ↓
4. Test with sample data
   - Verify parsing logic matches data format
   - Check field paths exist in parsed output
   ↓
5. Deploy updated configuration
   - Use `set_cloud_sensor` or `set_external_adapter` MCP tool
   - For on-prem adapters: Configuration syncs automatically if cloud-managed
   ↓
6. Verify improved parsing
   - Check Timeline for correctly parsed events
   - Validate field mappings with queries
```

### Workflow 3: Troubleshooting Data Flow Issues

```
1. Verify adapter status
   - Check if sensor appears: Use `list_sensors` MCP tool
   - Review sensor metadata: Use `get_sensor_info` MCP tool
   ↓
2. Review adapter configuration
   - Fetch config: `get_cloud_sensor` or `get_external_adapter`
   - Verify credentials, endpoints, and connection parameters
   - Check platform and mapping settings
   ↓
3. Identify the issue
   - No sensor: Connection/authentication problem
   - Sensor but no events: Collection or parsing problem
   - Events but wrong format: Mapping/parsing problem
   ↓
4. Fix configuration
   - Update credentials if expired
   - Adjust parsing patterns if failing
   - Modify field extractors if missing data
   ↓
5. Monitor recovery
   - Watch for sensor reconnection
   - Verify events flowing correctly
   - Check adapter logs if on-prem
```

### Workflow 4: Optimizing Adapter Performance

```
1. Assess current performance
   - Review event ingestion rate
   - Check for dropped events or delays
   - Identify high-volume sources
   ↓
2. Retrieve and analyze configuration
   - Use `get_cloud_sensor` or `get_external_adapter`
   - Review parsing complexity
   - Check for unnecessary field processing
   ↓
3. Apply optimizations
   - Add drop_fields early in pipeline to remove unnecessary data
   - Simplify Grok patterns (avoid greedy captures at start)
   - Add source-side filtering if possible
   - Configure custom indexing for frequently searched fields
   ↓
4. Update configuration
   - Deploy optimized config via MCP tools
   - Monitor impact on performance
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

### Updating an Existing Cloud Adapter

**MCP Tool:** `mcp__limacharlie__set_cloud_sensor`

**Parameters:**
- `name` (string): Identifier of the existing cloud sensor (e.g., "aws-cloudtrail-prod")
- `config` (JSON object): Updated adapter configuration
- `ttl` (integer, optional): Time-to-live for the configuration

**Returns:** Success confirmation

**Workflow:**
1. First retrieve the current configuration using `get_cloud_sensor`
2. Modify the configuration as needed
3. Use `set_cloud_sensor` with the same name to update

**Example - Updating credentials:**
```json
{
  "name": "aws-cloudtrail-prod",
  "config": {
    "sensor_type": "s3",
    "s3": {
      "bucket_name": "my-cloudtrail-logs",
      "access_key": "AKIANEWKEY123",
      "secret_key": "new-secret-key",
      "client_options": {
        "identity": {
          "oid": "your-oid",
          "installation_key": "your-key"
        },
        "platform": "aws",
        "sensor_seed_key": "cloudtrail-prod",
        "hostname": "aws-cloudtrail",
        "mapping": {
          "event_type_path": "eventName"
        }
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

### Verifying Configuration Changes

After updating an adapter configuration, verify the changes took effect:

**Check adapter status:**

**MCP Tool:** `mcp__limacharlie__list_sensors`

**Parameters:** None (supports optional filtering)

**Returns:** List of all sensors including adapter-based sensors

**Usage:** Verify the adapter sensor is still present and active after configuration changes.

**Get adapter sensor details:**

**MCP Tool:** `mcp__limacharlie__get_sensor_info`

**Parameters:**
- `sid` (string): Sensor ID of the adapter

**Returns:** Detailed sensor information including platform, hostname, and status

**Usage:** Check sensor metadata to confirm configuration updates are reflected.

**Verify events with updated configuration:** Use the `querying-limacharlie` skill to run LCQL queries and validate:
- Events are flowing after configuration change
- Parsing rules are working correctly
- Field mappings are applied as expected
- Custom indexing is functioning

Query by hostname, platform, or sensor ID to confirm the updated configuration is working as intended.

## Best Practices

### Configuration Management

- Use descriptive `sensor_seed_key` values: `syslog-firewall`, `aws-prod-cloudtrail`, `o365-audit-logs`
- Set meaningful `hostname` values for easy identification in UI
- Apply tags when updating configurations for better grouping and filtering
- Keep backup of working configurations before making changes

### Security Considerations

- Use least-privilege credentials for cloud connections
- Rotate API keys and connection secrets regularly
- Avoid hardcoding secrets - use environment variables or secure vaults
- For webhooks, use strong unpredictable secret values
- Enable TLS for Syslog adapters when possible

### Parsing Configuration

- Start with built-in platform parsers when available
- Use Grok patterns for common log formats (faster than regex)
- Test parsing changes with sample data before applying to production
- Keep extractors minimal - extract only necessary fields
- Make incremental changes to parsing rules rather than large rewrites

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

For adapter-specific configuration details, consult the documentation:
- Adapter Types: /limacharlie/doc/Sensors/Adapters/Adapter_Types/
- Configuration Reference: /limacharlie/doc/Sensors/Adapters/adapter-usage.md
- Deployment Guides (for initial setup): /limacharlie/doc/Sensors/Adapters/Adapter_Tutorials/

For comprehensive documentation lookup, use the `lc-essentials:lookup-lc-doc` skill to search across all LimaCharlie documentation, including adapter configurations, examples, and best practices.

For initial onboarding of new external data sources, use the `onboarding-external-datasources` skill which provides step-by-step guidance for first-time setup.
