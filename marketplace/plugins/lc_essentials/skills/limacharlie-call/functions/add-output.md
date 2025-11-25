
# Add Output

This skill creates a new output configuration in a LimaCharlie organization. Outputs control where and how data (events, detections, audit logs) is exported from LimaCharlie to external systems.

## When to Use

Use this skill when the user needs to:
- Create a new data export configuration
- Set up syslog forwarding to a SIEM or log collector
- Configure S3 or cloud storage archiving
- Create webhooks for custom integrations
- Set up Slack notifications for detections
- Configure integrations with Elastic, Splunk, Kafka, or other platforms
- Route specific data types (events, detections, audit logs) to destinations
- Filter data by tags, sensors, or event types before export

Common scenarios:
- "Create a syslog output to send events to 10.0.1.50"
- "Set up an S3 bucket for archiving detections"
- "Configure a webhook to send alerts to our API"
- "Create a Slack output for high-priority detections"
- "Forward all Windows events to our Splunk server"

## What This Skill Does

This skill calls the LimaCharlie API to create a new output configuration. It accepts the output name, module type (destination system), data type (what to export), and module-specific configuration parameters. The API validates the configuration and activates the output.

## Required Information

Before calling this skill, gather:

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **name**: Unique name for the output (alphanumeric, hyphens, underscores)
- **module**: Output module type (e.g., syslog, s3, webhook, slack, gcs, elastic, kafka)
- **type** or **for**: Data type to export (event, detect, audit, deployment, artifact)

Module-specific required parameters (varies by module):
- **syslog**: dest_host, dest_port (optional)
- **s3**: bucket, region_name (optional), secret_key (optional)
- **webhook**: dest_host (URL)
- **slack**: slack_api_token, slack_channel
- **gcs**: bucket, key_id (service account JSON)
- **elastic**: dest_host, username, password
- **kafka**: addresses, topic

Optional filtering and configuration:
- **tag**: Filter by sensor tag (e.g., "production")
- **tag_black_list**: Exclude specific tags
- **sid**: Filter by specific sensor ID
- **cat**: Filter detections by category
- **event_white_list**: Include specific event types
- **event_black_list**: Exclude specific event types
- **is_tls**: Enable TLS/SSL (syslog, elastic)
- **is_compression**: Enable gzip compression
- **sec_per_file**: File rotation interval for cloud storage

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Unique output name (not already in use)
3. Valid module type (see common modules below)
4. Correct data type (event, detect, audit, deployment, artifact)
5. Required module-specific parameters
6. Optional: Filtering and routing parameters

### Step 2: Call the API

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="add_output",
  parameters={
    "oid": "[organization-id]",
    "name": "output-name",
    "module": "syslog",
    "type": "event",
    "dest_host": "10.0.1.50",
    "dest_port": "514",
    "is_tls": "true",
    "tag": "production"
  }
)
```

**API Details:**
- Tool: `add_output`
- Required parameters:
  - `oid`: Organization ID
  - `name`: Output identifier
  - `module`: Output module type
  - `type` or `for`: Data type to export
  - Module-specific fields (see examples below)
  - Optional filtering fields (tag, event_white_list, etc.)
  - Boolean fields should be strings: "true" or "false"

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "name": "output-name",
  "module": "syslog",
  "for": "event",
  "dest_host": "10.0.1.50",
  "dest_port": "514",
  "is_tls": "true",
  "tag": "production"
}
```

**Success:**
- Output is created and immediately active
- Response contains the full output configuration as created
- Data matching the configuration will start flowing to the destination
- Verify the configuration matches expectations

**Common Errors:**
- **400 Bad Request**: Invalid parameters (missing required fields, invalid module name, malformed configuration)
- **409 Conflict**: Output name already exists - choose a different name or delete the existing output
- **403 Forbidden**: Insufficient permissions - user needs write access to organization configuration
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, check parameters and retry

### Step 4: Format the Response

Present the result to the user:
- Confirm output creation with name and module type
- Summarize key configuration:
  - What data is being exported (type)
  - Where it's going (destination)
  - Any filtering applied (tags, event types, etc.)
- Provide guidance on:
  - Testing the output (check destination for data)
  - Monitoring output health (check for errors in org errors)
  - Modifying if needed (must delete and recreate)
- Warn about:
  - Sensitive data in transit (use TLS when available)
  - Volume considerations (high-volume events)
  - Cost implications (cloud storage, bandwidth)

## Example Usage

### Example 1: Create syslog output for events

User request: "Create a syslog output to send all events to 10.0.1.50 on port 514 with TLS"

Steps:
1. Gather requirements:
   - Output name: "prod-syslog"
   - Module: syslog
   - Type: event
   - Destination: 10.0.1.50:514
   - TLS: enabled

2. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="add_output",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "prod-syslog",
    "module": "syslog",
    "type": "event",
    "dest_host": "10.0.1.50",
    "dest_port": "514",
    "is_tls": "true"
  }
)
```

Expected response:
```json
{
  "name": "prod-syslog",
  "module": "syslog",
  "for": "event",
  "dest_host": "10.0.1.50",
  "dest_port": "514",
  "is_tls": "true"
}
```

Format output:
```
Successfully created output "prod-syslog"

Configuration:
- Module: syslog
- Data type: event (all sensor telemetry)
- Destination: 10.0.1.50:514
- Security: TLS enabled

All events from your sensors will now be forwarded to this syslog destination.
Check your syslog server to verify data is being received.
```

### Example 2: Create S3 output with filtering

User request: "Archive all detections to S3 bucket 'lc-detections' in us-west-2, only for sensors tagged 'production'"

Steps:
1. Gather requirements:
   - Output name: "prod-detections-archive"
   - Module: s3
   - Type: detect
   - Bucket: lc-detections
   - Region: us-west-2
   - Tag filter: production

2. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="add_output",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "prod-detections-archive",
    "module": "s3",
    "type": "detect",
    "bucket": "lc-detections",
    "region_name": "us-west-2",
    "tag": "production",
    "sec_per_file": "3600",
    "is_compression": "true"
  }
)
```

Expected response:
```json
{
  "name": "prod-detections-archive",
  "module": "s3",
  "for": "detect",
  "bucket": "lc-detections",
  "region_name": "us-west-2",
  "tag": "production",
  "sec_per_file": "3600",
  "is_compression": "true"
}
```

Format output:
```
Successfully created S3 archive output "prod-detections-archive"

Configuration:
- Module: s3
- Data type: detect (detections only)
- Bucket: lc-detections (us-west-2)
- Filter: Sensors tagged "production" only
- File rotation: Every 3600 seconds (1 hour)
- Compression: Enabled (gzip)

Detections from production sensors will be archived to S3.
Files will be created hourly with gzip compression.
Ensure the LC service account has write permissions to the bucket.
```

### Example 3: Create webhook for critical detections

User request: "Send all detections with category 'critical' to https://api.example.com/alerts with API key authentication"

Steps:
1. Gather requirements:
   - Output name: "critical-webhook"
   - Module: webhook
   - Type: detect
   - URL: https://api.example.com/alerts
   - Auth: X-API-Key header
   - Filter: category=critical

2. First, store the API key as a secret (if not already stored)
3. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="add_output",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "critical-webhook",
    "module": "webhook",
    "type": "detect",
    "dest_host": "https://api.example.com/alerts",
    "auth_header_name": "X-API-Key",
    "auth_header_value": "[secret:webhook-api-key]",
    "cat": "critical"
  }
)
```

Expected response:
```json
{
  "name": "critical-webhook",
  "module": "webhook",
  "for": "detect",
  "dest_host": "https://api.example.com/alerts",
  "auth_header_name": "X-API-Key",
  "auth_header_value": "[secret:webhook-api-key]",
  "cat": "critical"
}
```

Format output:
```
Successfully created webhook output "critical-webhook"

Configuration:
- Module: webhook
- Data type: detect (detections only)
- URL: https://api.example.com/alerts
- Authentication: X-API-Key header (using secret)
- Filter: category="critical" only

Critical detections will be POST'ed to your webhook endpoint.
Each detection will be sent as a JSON payload in the request body.
Monitor your endpoint for incoming data.
```

## Additional Notes

- Outputs become active immediately after creation
- Cannot modify outputs - must delete and recreate to change configuration
- Use secrets for storing credentials (API keys, passwords)
- Reference secrets in output configs: `[secret:secret-name]`
- Test outputs with low-volume data first before production use
- Monitor organization errors for output failures (auth issues, network errors)
- Boolean fields must be strings in API: "true" or "false", not actual booleans
- Common output modules and their required fields:
  - **syslog**: dest_host (and optionally dest_port, default 514)
  - **s3**: bucket, region_name (optional), secret_key (optional)
  - **gcs**: bucket, key_id (service account JSON)
  - **webhook**: dest_host (full URL)
  - **slack**: slack_api_token, slack_channel
  - **elastic**: dest_host, username, password, index (optional)
  - **kafka**: addresses (comma-separated brokers), topic
  - **splunk**: dest_host, auth_header_value (HEC token)
- Filtering options reduce data volume and costs
- Use tag filters to route different sensor groups to different destinations
- Event type filtering uses event names like "DNS_REQUEST", "PROCESS_CREATE"
- Related skills: `list_outputs` to view configurations, `delete_output` to remove outputs

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/output.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/outputs.go`
