---
name: add-tag
description: Add a tag to a sensor for organization, categorization, and automation. Tags enable sensor grouping, D&R rule targeting, output filtering, investigation tracking, and fleet management. Set TTL for temporary tags or 0 for permanent. Essential for incident response, compliance, and operational workflows.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Add Tag

Add a tag to a sensor for organization, targeting detection rules, filtering outputs, and tracking investigations.

## When to Use

Use this skill when the user needs to:
- Organize sensors by function, location, or department
- Target D&R rules to specific sensor groups
- Filter outputs and alerts by sensor categories
- Track sensors involved in an investigation
- Mark sensors with temporary status (e.g., "under-investigation", "compromised")
- Group sensors for compliance or operational purposes

Common scenarios:
- "Tag this sensor as compromised for investigation tracking"
- "Add the 'production' tag to these database servers"
- "Mark this endpoint as under-investigation for 24 hours"
- "Tag sensors in the finance department for specific monitoring"

## What This Skill Does

This skill adds a tag to a sensor with an optional time-to-live (TTL). Tags are labels that help organize sensors and control which D&R rules apply to them. Tags can be permanent (TTL=0) or temporary (TTL>0), automatically expiring after the specified duration. Multiple tags can be added to a single sensor, and tags are immediately available for use in D&R rules, outputs, and searches.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **sid**: Sensor ID (UUID format) - the sensor to tag
- **tag**: Tag name/label to add (string, no spaces recommended)
- **ttl**: Time to live in seconds (0 for permanent, >0 for temporary)

Optional considerations:
- Choose descriptive tag names (e.g., "production", "dev", "compromised", "investigation-2024")
- Use TTL for temporary states (e.g., 86400 for 24 hours)
- Use TTL=0 for permanent categorization tags

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Tag name is descriptive and follows your organization's naming convention
4. TTL is set appropriately (0 for permanent, seconds for temporary)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/[sensor-id]/tags",
  body={
    "tags": "[tag-name]",
    "ttl": [ttl-in-seconds]
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/{sid}/tags` where `{sid}` is the sensor UUID
- No query parameters needed
- Body fields:
  - `tags`: String - the tag name to add
  - `ttl`: Number - time to live in seconds (0 = permanent, >0 = temporary)

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

**Success (200-299):**
- Status code 200 indicates the tag was successfully added
- The tag is immediately active and available for use
- If TTL > 0, the tag will automatically expire after the specified duration
- The tag will appear in sensor metadata and can be used in D&R rules

**Common Errors:**
- **400 Bad Request**: Invalid sensor ID format or invalid TTL - verify parameters
- **404 Not Found**: Sensor does not exist - verify the sid is correct
- **403 Forbidden**: Insufficient permissions - requires sensor tag management permissions
- **409 Conflict**: Tag may already exist (usually not an error, operation is idempotent)
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm the tag was successfully added to the sensor
- Mention the TTL if temporary (e.g., "Tag will expire in 24 hours")
- Explain how the tag can be used (D&R rules, outputs, searches)
- If this is an investigation tag, note it for tracking purposes
- Suggest verifying the tag with a sensor query if needed

## Example Usage

### Example 1: Tag Compromised Sensor for Investigation

User request: "Tag sensor abc12345-6789-0123-4567-890abcdef012 as 'compromised' for the next 48 hours"

Steps:
1. Validate the sensor ID format (UUID)
2. Calculate TTL: 48 hours = 172800 seconds
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/abc12345-6789-0123-4567-890abcdef012/tags",
  body={
    "tags": "compromised",
    "ttl": 172800
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

Response to user:
"Successfully added tag 'compromised' to sensor abc12345-6789-0123-4567-890abcdef012. The tag will automatically expire in 48 hours (172800 seconds). You can now use this tag in D&R rules to apply special monitoring or response actions to this sensor during the investigation."

### Example 2: Add Permanent Department Tag

User request: "Tag all finance servers with 'finance-dept' permanently"

Steps:
1. For each sensor, validate the sensor ID
2. Set TTL to 0 for permanent tag
3. Call API for each sensor:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/def45678-90ab-cdef-0123-456789abcdef/tags",
  body={
    "tags": "finance-dept",
    "ttl": 0
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

Response to user:
"Successfully added permanent tag 'finance-dept' to the sensor. This tag will remain active indefinitely and can be used to target D&R rules, filter outputs, and organize your sensor fleet. The tag will persist until explicitly removed with the remove-tag skill."

## Additional Notes

- Tags are case-sensitive (e.g., "Production" and "production" are different tags)
- Use descriptive names that align with your organization's tagging strategy
- TTL of 0 means permanent - the tag never expires
- TTL > 0 means temporary - tag automatically removes after specified seconds
- Common TTL values: 3600 (1 hour), 86400 (24 hours), 604800 (1 week)
- Multiple tags can exist on a single sensor simultaneously
- Tags can be used in D&R rule sensor selectors (e.g., `target: tag=production`)
- Tags enable output filtering (e.g., only send alerts from production sensors)
- Consider using consistent naming conventions (e.g., `dept-`, `env-`, `status-`)
- Tags are inherited by new sensor enrollments if set at installation key level
- Use the `remove-tag` skill to remove a tag before its TTL expires
- Tags are immediately visible in sensor metadata and searches
- Adding a tag that already exists will update its TTL

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go` (AddTag method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/response/response.go` (add_tag)
