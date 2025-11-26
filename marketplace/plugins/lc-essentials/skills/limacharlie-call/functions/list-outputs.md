
# List Outputs

This skill retrieves all configured outputs in a LimaCharlie organization. Outputs control where and how data (events, detections, audit logs) is exported from LimaCharlie.

## When to Use

Use this skill when the user needs to:
- View all configured outputs in the organization
- Check what data export configurations exist
- See which outputs are sending events, detections, or audit logs
- Audit data routing and destinations
- Troubleshoot output configurations
- Verify syslog, S3, webhook, or other integrations

Common scenarios:
- "Show me all outputs" or "What outputs are configured?"
- "List all syslog destinations" or "Where is event data being sent?"
- "Show me all webhook outputs" or "What integrations are active?"
- Investigating data flow before modifying configurations

## What This Skill Does

This skill calls the LimaCharlie API to retrieve all output configurations for an organization. It returns a complete list of outputs with their names, module types, data types, and full configuration details including destinations, credentials, and filtering options.

## Required Information

Before calling this skill, gather:

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No other parameters are needed for listing outputs.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)

### Step 2: Call the API

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="list_outputs",
  parameters={
    "oid": "[organization-id]"
  }
)
```

**API Details:**
- Tool: `list_outputs`
- Required parameters:
  - `oid`: Organization ID

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "[oid]": {
    "output-name-1": {
      "name": "output-name-1",
      "module": "syslog",
      "for": "event",
      "dest_host": "syslog.example.com",
      "dest_port": "514",
      ...
    },
    "output-name-2": {
      "name": "output-name-2",
      "module": "s3",
      "for": "detect",
      "bucket": "my-bucket",
      ...
    }
  }
}
```

**Success:**
- Response body contains a nested object: `{oid: {output-name: output-config}}`
- Extract the outputs from `response[oid]` to get a dictionary of output configurations
- Each output has:
  - `name`: Output identifier
  - `module`: Output type (syslog, s3, webhook, slack, gcs, etc.)
  - `for` or `type`: Data type (event, detect, audit, deployment, artifact)
  - Module-specific configuration fields (dest_host, bucket, username, etc.)
- Present outputs in a readable format, grouping by type or module if helpful

**Common Errors:**
- **404 Not Found**: Organization doesn't exist or no outputs configured (empty response)
- **403 Forbidden**: Insufficient permissions - user needs read access to organization configuration
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- List each output with its name and module type
- Group outputs by data type (event outputs, detection outputs, etc.) if multiple exist
- Highlight key configuration details (destinations, filters, tags)
- For detailed review, show full configuration including:
  - Routing options (tag filters, sensor filters, event type filters)
  - Destination details (host, bucket, URL, etc.)
  - Security settings (TLS, authentication)
- Note if no outputs are configured (empty result)

## Example Usage

### Example 1: List all outputs

User request: "Show me all outputs configured in the organization"

Steps:
1. Obtain organization ID
2. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_outputs",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
  }
)
```

Expected response:
```json
{
  "c7e8f940-1234-5678-abcd-1234567890ab": {
    "prod-syslog": {
      "name": "prod-syslog",
      "module": "syslog",
      "for": "event",
      "dest_host": "10.0.1.50",
      "dest_port": "514",
      "is_tls": "true",
      "tag": "production"
    },
    "detection-webhook": {
      "name": "detection-webhook",
      "module": "webhook",
      "for": "detect",
      "dest_host": "https://api.example.com/detections",
      "auth_header_name": "X-API-Key",
      "auth_header_value": "[secret:webhook-key]"
    },
    "s3-archive": {
      "name": "s3-archive",
      "module": "s3",
      "for": "event",
      "bucket": "lc-events-archive",
      "region_name": "us-east-1",
      "sec_per_file": "3600"
    }
  }
}
```

Format output:
```
Configured Outputs (3 total):

Event Outputs:
1. prod-syslog (syslog)
   - Destination: 10.0.1.50:514
   - TLS: Enabled
   - Filter: tag=production

2. s3-archive (s3)
   - Bucket: lc-events-archive
   - Region: us-east-1
   - File rotation: Every 3600 seconds

Detection Outputs:
1. detection-webhook (webhook)
   - URL: https://api.example.com/detections
   - Authentication: X-API-Key header
```

### Example 2: No outputs configured

User request: "List outputs"

Steps:
1. Call API as above
2. Receive empty response:
```json
{
  "c7e8f940-1234-5678-abcd-1234567890ab": {}
}
```

Format output:
```
No outputs are currently configured for this organization.

Outputs control where data (events, detections, audit logs) is exported.
You can create outputs to send data to syslog, S3, webhooks, Slack, and other destinations.
```

## Additional Notes

- Output configurations may contain sensitive information (credentials, API keys)
- Secret references appear as `[secret:secret-name]` in configurations
- The `for` field in API responses maps to `type` in SDK/tool terminology
- Common output modules:
  - **syslog**: Send to syslog server (UDP/TCP/TLS)
  - **s3**: Archive to AWS S3 bucket
  - **webhook**: HTTP POST to custom endpoint
  - **slack**: Send to Slack channel
  - **gcs**: Archive to Google Cloud Storage
  - **elastic**: Send to Elasticsearch
  - **kafka**: Stream to Kafka topic
  - **splunk**: Forward to Splunk HEC
- Outputs can filter by tags, sensors, event types, detection categories
- Multiple outputs can be configured for the same data type
- Related skills: `add_output`, `delete_output` for managing outputs

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/output.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/outputs.go`
