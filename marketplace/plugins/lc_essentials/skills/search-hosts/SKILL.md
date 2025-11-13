---
name: search-hosts
description: Search for LimaCharlie sensors by hostname pattern using wildcard matching. Supports asterisk (*) and question mark (?) wildcards for flexible hostname filtering. Use to find sensors by naming convention, locate servers matching patterns, filter by environment prefix/suffix, or discover sensors with specific hostname characteristics.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Search Hosts by Hostname Pattern

Search for sensors using flexible wildcard patterns in hostnames.

## When to Use

Use this skill when the user needs to:
- Search for sensors by hostname pattern
- Find sensors matching wildcard expressions
- Locate servers with specific naming conventions
- Filter sensors by hostname prefix, suffix, or substring
- Discover sensors in a specific environment (e.g., prod-*, *-staging)
- Find sensors with similar hostname patterns

Common scenarios:
- "Find all sensors with hostname starting with 'web-'"
- "Show me all production servers (*-prod)"
- "List sensors with 'database' in the hostname"
- "Find all Windows workstations (WS-*)"
- "Search for sensors matching pattern 'app-*-prod'"

## What This Skill Does

This skill searches for sensors by hostname using wildcard patterns. It supports `*` (matches any characters) and `?` (matches single character) for flexible pattern matching.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all API calls)
- **hostname_expr**: Hostname pattern with wildcards (e.g., "web-*", "*-prod", "*database*")

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Hostname pattern (can include `*` and `?` wildcards)

### Step 2: Call the API

This operation requires listing all sensors and filtering client-side:

```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/sensors/c7e8f940-1234-5678-abcd-1234567890ab"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/sensors/{oid}`
- No query parameters
- Pattern matching is performed client-side using `filepath.Match`

**Note:** The SDK method `org.ListSensors()` followed by client-side pattern matching using Go's `filepath.Match` function.

### Step 3: Handle the Response

The API returns all sensors:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "sensors": {
      "sensor-1": {
        "sid": "sensor-1",
        "hostname": "web-server-01",
        ...
      },
      "sensor-2": {
        "sid": "sensor-2",
        "hostname": "web-server-02",
        ...
      },
      "sensor-3": {
        "sid": "sensor-3",
        "hostname": "db-server-01",
        ...
      }
    }
  }
}
```

**Success (200):**
- Retrieve all sensors from the organization
- Apply wildcard pattern matching to hostname field
- Return only matching sensors
- Pattern matching is case-sensitive by default

**Wildcard Pattern Rules:**
- `*` matches zero or more characters
- `?` matches exactly one character
- Examples:
  - `web-*` matches "web-01", "web-server", "web-prod-01"
  - `*-prod` matches "app-prod", "web-prod", "db-prod"
  - `*database*` matches "database-01", "my-database-server"
  - `app-??` matches "app-01", "app-db" (exactly 2 chars after app-)

**Common Errors:**
- **403 Forbidden**: Insufficient permissions to list sensors
- **500 Server Error**: Rare, retry or check LimaCharlie service status

### Step 4: Format the Response

Present the result to the user:
- Display count of matching sensors
- List sensor ID, hostname, platform, and last seen
- Sort results by hostname for easy reading
- Highlight the pattern that was searched
- Show zero results message if no matches

**Example formatted output:**
```
Sensors matching pattern "web-*": 3 found

ID              Hostname         Platform    Last Seen            Internal IP
----------------------------------------------------------------------------
xyz-123         web-server-01    Linux       2024-01-20 14:22    10.0.1.10
abc-456         web-server-02    Linux       2024-01-20 14:20    10.0.1.11
def-789         web-app-01       Linux       2024-01-20 14:18    10.0.1.12
```

## Example Usage

### Example 1: Find all web servers

User request: "Find all sensors with hostname starting with 'web-'"

Steps:
1. Get organization ID from context
2. Call API to list all sensors:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/sensors/c7e8f940-1234-5678-abcd-1234567890ab"
)
```
3. Filter sensors where hostname matches pattern "web-*"
4. Display matching sensors

Expected result:
```
Found 3 sensors matching "web-*":
- web-server-01 (sensor-xyz-123)
- web-server-02 (sensor-abc-456)
- web-app-01 (sensor-def-789)
```

### Example 2: Find production servers

User request: "Show me all production servers (*-prod)"

Steps:
1. List all sensors
2. Filter by pattern "*-prod"
3. Display results:
```
Production Servers (4 found):
- app-prod (sensor-111)
- web-prod (sensor-222)
- db-prod (sensor-333)
- cache-prod (sensor-444)
```

### Example 3: Find sensors with substring

User request: "List sensors with 'database' in the hostname"

Steps:
1. List all sensors
2. Filter by pattern "*database*"
3. Show matching sensors

## Additional Notes

- Pattern matching uses Go's `filepath.Match` internally
- Matching is case-sensitive (use lowercase patterns if hostnames are lowercase)
- The `*` wildcard is greedy and matches everything
- For exact match, omit wildcards (e.g., "web-server-01")
- For prefix match, use pattern like "web-*"
- For suffix match, use pattern like "*-prod"
- For substring match, use pattern like "*database*"
- Invalid patterns will fall back to exact string comparison
- Large organizations may have slower response due to client-side filtering
- Consider using more specific patterns to reduce result set
- The search retrieves all sensors first, then filters locally
- For IP-based filtering, use `list-sensors` with IP filter instead
- For hostname-only endpoint search, use the org's SearchHostname method for "hostname" IOC type

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/core/core.go`
