---
name: list-cloud-sensors
description: List all cloud sensor configurations in a LimaCharlie organization. Cloud sensors are integrations that collect telemetry from cloud platforms and SaaS services (AWS CloudTrail, Azure Activity Logs, GCP Audit Logs, Office 365, Okta, etc.) without requiring agent installation. Use this skill when users need to view existing cloud data sources, audit cloud integrations, check which cloud platforms are being monitored, review cloud sensor configurations, or troubleshoot cloud data ingestion. Shows sensor names, enabled status, tags, and configuration metadata.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# List Cloud Sensors

Retrieve all cloud sensor configurations from a LimaCharlie organization, showing which cloud platforms and services are being monitored.

## When to Use

Use this skill when the user needs to:
- View all configured cloud sensor integrations
- Check which cloud platforms are being monitored (AWS, Azure, GCP, etc.)
- Audit existing cloud data source configurations
- Find a specific cloud sensor by name or tags
- Review cloud sensor enablement status and metadata
- Troubleshoot cloud data ingestion issues

Common scenarios:
- Initial setup verification after configuring cloud integrations
- Security audits of monitored cloud platforms
- Compliance reporting on data source coverage
- Troubleshooting missing cloud telemetry
- Planning new cloud sensor deployments
- Documenting current cloud monitoring setup

## What This Skill Does

This skill retrieves all cloud sensor configurations from the organization's Hive storage. Cloud sensors are virtual sensors that collect telemetry from cloud platforms and SaaS services without requiring agent installation on endpoints. Examples include AWS CloudTrail, Azure Activity Logs, GCP Audit Logs, Office 365 logs, Okta events, and other cloud-native data sources. The skill calls the LimaCharlie Hive API to list all entries in the "cloud_sensor" hive with the "global" partition key, returning each sensor's configuration, enablement status, tags, and metadata.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No additional parameters are needed.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="GET",
  path="/hive/cloud_sensor/global"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/hive/cloud_sensor/global`
- Query parameters: None
- Body: None

The path uses the Hive structure:
- `cloud_sensor`: The hive name for cloud sensor configurations
- `global`: The partition key (cloud sensors use the global partition)

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "sensor-name-1": {
      "data": {
        "sensor_type": "aws_cloudtrail",
        "config": { ... }
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["aws", "production"],
        "comment": "Production AWS CloudTrail",
        "expiry": 0
      },
      "sys_mtd": {
        "etag": "abc123",
        "created_by": "user@example.com",
        "created_at": 1704067200,
        "last_author": "user@example.com",
        "last_mod": 1704153600,
        "guid": "unique-guid-123",
        "last_error": "",
        "last_error_ts": 0
      }
    },
    "sensor-name-2": { ... }
  }
}
```

**Success (200-299):**
- The response body contains a map of cloud sensor configurations
- Each key is the cloud sensor name
- Each value contains:
  - `data`: The sensor configuration including type and settings
  - `usr_mtd`: User metadata (enabled status, tags, comment, expiry)
  - `sys_mtd`: System metadata (creation info, modification info, GUID, errors)
- If no cloud sensors exist, the response body will be an empty object `{}`

**Common Errors:**
- **400 Bad Request**: Invalid organization ID format or malformed request
- **401 Unauthorized**: Authentication token is invalid or expired
- **403 Forbidden**: Insufficient permissions to view cloud sensors (requires fleet_management role)
- **404 Not Found**: Organization does not exist or hive partition not found
- **500 Server Error**: Internal server error, retry the request

### Step 4: Format the Response

Present the result to the user:
- Display each cloud sensor with its name and key properties
- Show the sensor type (AWS, Azure, GCP, Office 365, etc.)
- Indicate whether each sensor is enabled or disabled
- List any tags associated with the sensor
- Show creation and last modification dates
- Highlight any errors in the last_error field
- Provide a count of total cloud sensors configured
- If filtering, apply filters by name, tags, or sensor type

## Example Usage

### Example 1: List all cloud sensors

User request: "Show me all cloud sensor configurations"

Steps:
1. Extract the organization ID from context
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/hive/cloud_sensor/global"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "prod-aws-cloudtrail": {
      "data": {
        "sensor_type": "aws_cloudtrail",
        "aws_region": "us-east-1",
        "s3_bucket": "my-cloudtrail-logs"
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["aws", "production", "cloudtrail"],
        "comment": "Production AWS CloudTrail integration",
        "expiry": 0
      },
      "sys_mtd": {
        "created_at": 1704067200,
        "last_mod": 1704153600,
        "last_error": ""
      }
    },
    "office365-audit": {
      "data": {
        "sensor_type": "office365",
        "tenant_id": "abc-123-def"
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["office365", "saas"],
        "comment": "Office 365 audit logs",
        "expiry": 0
      },
      "sys_mtd": {
        "created_at": 1704240000,
        "last_mod": 1704240000,
        "last_error": ""
      }
    }
  }
}
```

Present to user:
```
Found 2 cloud sensors:

1. prod-aws-cloudtrail
   - Type: AWS CloudTrail
   - Status: Enabled
   - Tags: aws, production, cloudtrail
   - Comment: Production AWS CloudTrail integration
   - Created: January 1, 2024
   - Last Modified: January 2, 2024

2. office365-audit
   - Type: Office 365
   - Status: Enabled
   - Tags: office365, saas
   - Comment: Office 365 audit logs
   - Created: January 3, 2024
```

### Example 2: Check for AWS cloud sensors

User request: "Which AWS cloud sensors do we have configured?"

Steps:
1. Call API to get all cloud sensors
2. Filter results for AWS-related sensors (check sensor_type or tags)
3. Present filtered results:
```
Found 1 AWS cloud sensor:

prod-aws-cloudtrail
- Type: AWS CloudTrail
- Status: Enabled
- Region: us-east-1
- S3 Bucket: my-cloudtrail-logs
- Tags: aws, production, cloudtrail
```

### Example 3: No cloud sensors configured

User request: "List cloud sensors"

Steps:
1. Call API
2. Receive empty response body: `{}`

Present to user:
```
No cloud sensors are currently configured in this organization.

Cloud sensors collect telemetry from cloud platforms and SaaS services like:
- AWS CloudTrail, GuardDuty, VPC Flow Logs
- Azure Activity Logs, Sign-in Logs
- GCP Audit Logs
- Office 365, Okta, and other SaaS platforms

Use the set-cloud-sensor skill to create cloud sensor configurations.
```

## Additional Notes

- Cloud sensors are stored in the Hive under the `cloud_sensor` hive name with `global` partition
- Each cloud sensor has a unique name within the organization
- The `enabled` field controls whether the sensor is actively collecting data
- Tags can be used to organize and filter cloud sensors
- The `last_error` field in sys_mtd shows the most recent error, if any
- Cloud sensors do not require endpoint agents - they collect data from cloud APIs
- Common sensor types include:
  - AWS: CloudTrail, GuardDuty, VPC Flow Logs, Config
  - Azure: Activity Logs, Sign-in Logs, Security Center
  - GCP: Audit Logs, Cloud Logging
  - SaaS: Office 365, Okta, GitHub, etc.
- Use the get-cloud-sensor skill to retrieve detailed configuration for a specific sensor
- Use the set-cloud-sensor skill to create or update cloud sensor configurations
- Use the delete-cloud-sensor skill to remove cloud sensors
- Cloud sensor configurations may contain sensitive credentials - handle with care
- The `comment` field is useful for documenting the purpose or scope of each sensor

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/lc-mcp-server/internal/tools/hive/cloud_sensors.go`
