
# Get Organization Info

Retrieve comprehensive information about a LimaCharlie organization including configuration, limits, and metadata.

## When to Use

Use this skill when the user needs to:
- View organization details and configuration
- Check plan limits and quotas
- Verify organization name and location
- Understand organization capabilities
- Troubleshoot configuration issues
- Review organization settings

Common scenarios:
- Verifying organization setup
- Checking resource limits before scaling
- Troubleshooting service availability
- Auditing organization configuration
- Understanding plan restrictions
- Documenting organization details

## What This Skill Does

This skill retrieves detailed information about a LimaCharlie organization. It calls the LimaCharlie API to get organization metadata including name, location, plan type, resource limits, enabled features, and configuration settings.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No additional parameters are required.

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
  path="/v1/orgs/[oid]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/orgs/{oid}`
- Query parameters: None
- Body fields: None

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "name": "My Organization",
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "location": "usa",
    "plan": "enterprise",
    "limits": {
      "max_sensors": 1000,
      "max_rules": 500
    },
    "features": ["advanced_detection", "threat_intel"],
    "created": 1609459200
  }
}
```

**Success (200-299):**
- Response contains comprehensive organization information
- Includes name, location, plan tier, and limits
- Shows enabled features and capabilities
- May include creation timestamp and other metadata

**Common Errors:**
- **400 Bad Request**: Invalid organization ID format
- **403 Forbidden**: Insufficient permissions to view organization details
- **404 Not Found**: Organization does not exist
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Display organization name and ID
- Show location and plan type
- List resource limits (sensors, rules, retention)
- Highlight enabled features
- Include creation date if available
- Note any warnings or restrictions

## Example Usage

### Example 1: View organization details

User request: "Show me information about my organization"

Steps:
1. Extract organization ID from context
2. Call API to get organization info:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/v1/orgs/c7e8f940-1234-5678-abcd-1234567890ab"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "name": "Acme Security",
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "location": "usa",
    "plan": "enterprise",
    "limits": {
      "max_sensors": 5000,
      "retention_days": 365
    },
    "created": 1577836800
  }
}
```

Present to user:
```
Organization Details

Name: Acme Security
ID: c7e8f940-1234-5678-abcd-1234567890ab
Location: USA
Plan: Enterprise
Created: January 1, 2020

Resource Limits:
- Maximum Sensors: 5,000
- Data Retention: 365 days

Your organization has enterprise-level access with extended retention.
```

### Example 2: Check plan limits before scaling

User request: "Can I add 100 more sensors? What's my limit?"

Steps:
1. Get organization info to check current limits
2. Compare with planned scaling
3. Provide guidance

Present analysis:
```
Current Sensor Capacity

Plan: Enterprise
Maximum Sensors: 5,000
Current Sensors: 3,847
Available Capacity: 1,153

✅ Yes, you can add 100 more sensors.

After adding 100 sensors:
- Total: 3,947 / 5,000
- Remaining capacity: 1,053 sensors
- Utilization: 79%

You have plenty of capacity for this expansion.
```

## Additional Notes

- Organization information is read-only through this endpoint
- Plan limits may vary based on subscription tier
- Location affects data residency and compliance
- Some features may be plan-dependent
- Contact LimaCharlie support to modify plan or increase limits
- Organization ID is the primary unique identifier
- This is a safe read-only operation

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/organization.go` (GetInfo function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/admin/admin.go` (RegisterGetOrgInfo)
