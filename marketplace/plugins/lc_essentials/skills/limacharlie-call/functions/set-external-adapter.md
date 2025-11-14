
# Set External Adapter

Create a new external adapter or update an existing external adapter configuration for external data ingestion and processing.

## When to Use

Use this skill when the user needs to:
- Configure a new external adapter for syslog, webhook, or API data ingestion
- Update an existing adapter's configuration or credentials
- Modify parsing rules and field mappings
- Enable or disable an external adapter
- Update connection parameters or credentials
- Change adapter tags for organization
- Reconfigure adapter after data format changes

Common scenarios:
- Initial setup of external data source integrations
- Updating parsing rules when external data format changes
- Configuring syslog receivers for firewall, router, or switch logs
- Setting up webhook receivers for third-party alerts
- Modifying field mappings for better data normalization
- Enabling previously disabled adapters
- Fixing configuration errors in external integrations

## What This Skill Does

This skill creates or updates an external adapter configuration in the organization's Hive storage. External adapters receive and process data from external sources like syslog servers, webhooks, custom APIs, and third-party security tools. Each adapter includes parsing rules that transform external data formats into LimaCharlie's normalized event format. The skill calls the LimaCharlie Hive API to store the adapter configuration with automatic enablement. If an adapter with the same name exists, it will be updated; otherwise, a new adapter is created.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **adapter_name**: Name for the external adapter (required, alphanumeric with hyphens/underscores)
- **adapter_config**: Complete configuration object (required, structure varies by adapter type)

The adapter_config typically includes:
- **adapter_type**: Type of adapter (syslog, webhook, api, custom)
- **Connection parameters**: Port, protocol, URL, etc. (varies by type)
- **parsing_rules**: Rules for transforming external data
  - **format**: Data format (syslog, json, cef, leef, custom_regex)
  - **field_mappings**: External field → LimaCharlie field mappings
  - **filters**: Include/exclude patterns (optional)
  - **transformations**: Data normalization rules (optional)
- **Authentication**: Credentials, tokens, API keys (if required)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Unique adapter name (or name of existing adapter to update)
3. Complete adapter configuration with all required fields
4. Valid parsing rules that match the external data format
5. Correct connection parameters and credentials
6. Understanding of the external data source's format and structure

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/v1/hive/external_adapter/global/[adapter-name]/data",
  body={
    "gzdata": "[base64-gzip-encoded-json]",
    "usr_mtd": {
      "enabled": true,
      "tags": ["tag1", "tag2"],
      "comment": "Adapter description",
      "expiry": 0
    }
  }
)
```

**Note**: The body requires `gzdata` which is a gzip-compressed, base64-encoded JSON string. The MCP tool handles compression automatically.

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/v1/hive/external_adapter/global/{adapter-name}/data`
- Body fields:
  - `gzdata`: Compressed and encoded adapter configuration
  - `usr_mtd`: User metadata (enabled, tags, comment, expiry)
  - `etag` (optional): For optimistic concurrency control during updates

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "guid": "unique-adapter-guid",
    "hive": {
      "name": "external_adapter",
      "partition": "global"
    },
    "name": "adapter-name"
  }
}
```

**Success (200-299):**
- The external adapter has been created or updated successfully
- The response contains the adapter's GUID and hive information
- The adapter is automatically enabled unless specified otherwise
- The adapter will begin processing data based on its configuration

**Common Errors:**
- **400 Bad Request**: Missing required fields, invalid configuration structure, or malformed parsing rules
- **401 Unauthorized**: Authentication token is invalid or expired
- **403 Forbidden**: Insufficient permissions to manage external adapters (requires platform_admin role)
- **409 Conflict**: ETag mismatch if updating existing adapter with concurrent modifications
- **500 Server Error**: Internal server error, retry the request

### Step 4: Format the Response

Present the result to the user:
- Confirm successful creation or update of the external adapter
- Display the adapter name and type
- Show the enabled status
- List any tags applied
- Provide connection details for sending data
- Suggest testing data ingestion with sample events
- For updates, note what changed

## Example Usage

### Example 1: Create syslog adapter for firewall logs

User request: "Set up a syslog adapter for our Palo Alto firewall logs"

Steps:
1. Extract organization ID from context
2. Prepare adapter name: "firewall-syslog"
3. Gather configuration: port, protocol, parsing rules
4. Call API with configuration:

```
The adapter_config (before encoding) would be:
{
  "adapter_type": "syslog",
  "listen_port": 514,
  "protocol": "udp",
  "parsing_rules": {
    "format": "syslog_rfc5424",
    "field_mappings": {
      "timestamp": "event.timestamp",
      "hostname": "routing.hostname",
      "severity": "event.severity",
      "facility": "event.facility",
      "message": "event.message",
      "source_ip": "routing.source_ip"
    },
    "filters": {
      "include_patterns": ["threat", "traffic", "system"]
    }
  }
}
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "guid": "abc-123-def-456",
    "hive": {
      "name": "external_adapter",
      "partition": "global"
    },
    "name": "firewall-syslog"
  }
}
```

Present to user:
```
Successfully created syslog external adapter!

Adapter Name: firewall-syslog
Type: Syslog
Status: Enabled
Tags: syslog, firewall, palo-alto

Connection Details:
- Protocol: UDP
- Port: 514
- Format: RFC 5424

Parsing Rules:
- timestamp → event.timestamp
- hostname → routing.hostname
- severity → event.severity
- message → event.message

To send logs from your Palo Alto firewall:
1. Configure syslog forwarding to LimaCharlie's syslog endpoint
2. Use UDP port 514
3. Send logs in RFC 5424 format

The adapter will begin processing logs as soon as they arrive.
Test by sending a sample log and checking the event stream.
```

### Example 2: Create webhook adapter for alerts

User request: "Set up a webhook to receive alerts from our monitoring system"

Steps:
1. Prepare adapter name: "monitoring-webhook"
2. Configure webhook settings
3. Call API:

```
The adapter_config would be:
{
  "adapter_type": "webhook",
  "endpoint_url": "/webhook/monitoring",
  "auth_token": "secret-token-123",
  "parsing_rules": {
    "format": "json",
    "field_mappings": {
      "alert_name": "event.alert_name",
      "severity": "event.severity",
      "timestamp": "event.timestamp",
      "description": "event.message",
      "source": "routing.source"
    }
  }
}
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "guid": "webhook-guid-789",
    "name": "monitoring-webhook"
  }
}
```

Present to user:
```
Successfully created webhook external adapter!

Adapter Name: monitoring-webhook
Type: Webhook
Status: Enabled

Webhook Endpoint:
https://api.limacharlie.io/webhook/monitoring

Authentication:
- Include header: Authorization: Bearer secret-token-123

Expected Format: JSON
Field Mappings:
- alert_name → event.alert_name
- severity → event.severity
- timestamp → event.timestamp
- description → event.message

Configure your monitoring system to POST alerts to the webhook endpoint.
```

### Example 3: Update parsing rules for existing adapter

User request: "Update the firewall-syslog adapter to parse additional fields"

Steps:
1. Get existing configuration (use get-external-adapter skill)
2. Update parsing rules with new field mappings
3. Call API with updated configuration
4. Include all existing fields plus new mappings

Present to user:
```
Successfully updated external adapter 'firewall-syslog'!

Updated parsing rules to include:
- New field: action → event.action
- New field: destination_port → event.dest_port
- New field: protocol → event.network_protocol

The adapter will now extract these additional fields from incoming syslog messages.
```

### Example 4: Enable a disabled adapter

User request: "Enable the webhook-backup adapter"

Steps:
1. Get existing configuration
2. Update with enabled=true in usr_mtd
3. Call API

Present to user:
```
Successfully enabled external adapter 'webhook-backup'.

The adapter is now active and will process incoming webhook requests.
```

## Additional Notes

- External adapters use the Hive storage system under `external_adapter` hive with `global` partition
- Adapter names must be unique within the organization
- The adapter_config structure varies by adapter type (syslog, webhook, api, custom)
- Parsing rules are critical - incorrect rules result in unparsed or malformed events
- Test parsing rules with sample data before deploying to production
- Field mappings should align with LimaCharlie's event schema for proper normalization
- Common LimaCharlie event fields:
  - `event.timestamp`: Event timestamp
  - `event.event_type`: Type of event
  - `event.message`: Event message or description
  - `event.severity`: Event severity level
  - `routing.hostname`: Source hostname
  - `routing.source_ip`: Source IP address
- The adapter is automatically enabled unless explicitly disabled in usr_mtd
- Tags are useful for organizing adapters by source, type, or purpose
- Use meaningful adapter names that indicate the data source and type
- When updating, the entire configuration is replaced - include all fields
- For credential updates, update the adapter configuration with new credentials
- The `etag` field can be used for concurrent update protection
- After creating or updating, test data ingestion with sample events
- Check the adapter's last_error field if data isn't appearing (use get-external-adapter)
- Common adapter types and their key configuration fields:
  - **Syslog**: adapter_type, listen_port, protocol, parsing_rules
  - **Webhook**: adapter_type, endpoint_url, auth_token, parsing_rules
  - **API Polling**: adapter_type, poll_url, poll_interval, auth_headers, parsing_rules
  - **Custom**: adapter_type, custom configuration fields, parsing_rules
- Parsing rule formats:
  - **syslog**: RFC 3164 or RFC 5424
  - **json**: JSON objects
  - **cef**: Common Event Format
  - **leef**: Log Event Extended Format
  - **custom_regex**: Regular expression patterns
- Use list-external-adapters to verify the adapter was created
- Use get-external-adapter to inspect the configuration after creation
- Use delete-external-adapter to remove adapters that are no longer needed
- Consider network security when exposing syslog ports or webhook endpoints
- Document parsing rules and field mappings for maintenance

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/lc-mcp-server/internal/tools/hive/external_adapters.go`
