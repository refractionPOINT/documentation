
# Get Usage Statistics

Retrieve comprehensive usage statistics and metrics for a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- Monitor organization resource consumption
- Review data ingestion and event volumes
- Analyze API usage patterns
- Plan capacity and scaling
- Optimize costs and resource allocation
- Prepare for billing reviews
- Track sensor deployment trends

Common scenarios:
- Monthly usage reviews
- Cost optimization analysis
- Capacity planning before expansion
- Identifying usage anomalies
- Understanding peak usage periods
- Troubleshooting performance issues
- Compliance reporting on data volumes

## What This Skill Does

This skill retrieves detailed usage statistics for a LimaCharlie organization. It calls the LimaCharlie API to get metrics on sensor counts, data ingestion volumes, event processing, API requests, and other resource consumption data.

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
  path="/usage/[oid]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/usage/{oid}`
- Query parameters: None
- Body fields: None

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "sensors": {
      "total": 1500,
      "online": 1420,
      "by_platform": {
        "windows": 800,
        "linux": 500,
        "macos": 200
      }
    },
    "data_ingestion": {
      "events_per_day": 50000000,
      "bytes_per_day": 15000000000
    },
    "api_requests": {
      "per_day": 100000
    },
    "retention_days": 30
  }
}
```

**Success (200-299):**
- Response contains comprehensive usage metrics
- Includes sensor counts (total, online, by platform)
- Shows data ingestion volumes (events, bytes)
- Provides API usage statistics
- May include retention period and other limits

**Common Errors:**
- **400 Bad Request**: Invalid organization ID format
- **403 Forbidden**: Insufficient permissions to view usage statistics
- **404 Not Found**: Organization does not exist
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Summarize key usage metrics
- Break down sensor counts by platform
- Show data ingestion rates (per day, per month)
- Highlight API usage
- Compare against plan limits if available
- Identify any concerning trends or anomalies

## Example Usage

### Example 1: Review monthly usage

User request: "Show me our current usage statistics"

Steps:
1. Extract organization ID from context
2. Call API to get usage stats:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/usage/c7e8f940-1234-5678-abcd-1234567890ab"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "sensors": {
      "total": 2500,
      "online": 2375,
      "by_platform": {
        "windows": 1500,
        "linux": 800,
        "macos": 200
      }
    },
    "data_ingestion": {
      "events_per_day": 75000000,
      "bytes_per_day": 25000000000
    },
    "api_requests": {
      "per_day": 150000
    }
  }
}
```

Present to user:
```
Organization Usage Statistics

Sensors:
- Total Deployed: 2,500
- Currently Online: 2,375 (95% uptime)
- Windows: 1,500 (60%)
- Linux: 800 (32%)
- macOS: 200 (8%)

Data Ingestion:
- Events per Day: 75,000,000
- Data Volume: 25 GB/day (~750 GB/month)
- Average per Sensor: 30,000 events/day

API Usage:
- Requests per Day: 150,000
- Average: 6,250 requests/hour

Health: All metrics are within normal ranges
```

### Example 2: Plan capacity for expansion

User request: "We're adding 500 new servers. How will that affect our usage?"

Steps:
1. Get current usage statistics
2. Calculate projected increase
3. Compare with plan limits

Present analysis:
```
Capacity Planning Analysis

Current State:
- Sensors: 2,500
- Events/day: 75M
- Data volume: 25 GB/day

After Adding 500 Servers:
- Sensors: 3,000 (+20%)
- Estimated events/day: 90M (+20%)
- Estimated data volume: 30 GB/day (+20%)

Monthly Projections:
- Current: ~750 GB/month
- Projected: ~900 GB/month
- Increase: +150 GB/month

Recommendations:
✓ Current plan supports this expansion
✓ Monitor data ingestion after deployment
✓ Consider optimizing event filtering to reduce volume
✓ Review retention policies if needed
```

## Additional Notes

- Usage statistics are typically updated hourly or daily
- Data ingestion metrics may have slight delays
- Sensor counts include all registered sensors (online and offline)
- API usage includes all API requests (successful and failed)
- Historical usage data may be available through billing endpoints
- High data volumes may indicate need for event filtering
- Sudden usage spikes may indicate issues or attacks
- This is a read-only monitoring operation
- Usage metrics help with cost optimization and planning

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/organization_ext.go` (GetUsageStats function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/admin/admin.go` (RegisterGetUsageStats)
