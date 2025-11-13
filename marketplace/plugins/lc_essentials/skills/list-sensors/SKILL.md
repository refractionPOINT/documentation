---
name: list-sensors
description: List all sensors in a LimaCharlie organization with optional filtering by hostname prefix or IP address. Returns sensor ID, hostname, platform, last seen timestamp, and IP addresses. Use for sensor inventory, fleet management, filtering sensors by name or IP, counting total sensors, or finding sensors matching specific criteria.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# List Sensors

Retrieve a list of all sensors in your LimaCharlie organization with optional filtering capabilities.

## When to Use

Use this skill when the user needs to:
- List all sensors in the organization
- Get a sensor inventory or fleet overview
- Filter sensors by hostname prefix (e.g., all servers starting with "web-")
- Filter sensors by IP address (internal or external)
- Count total number of sensors
- Find sensors matching specific naming patterns

Common scenarios:
- "Show me all sensors in my organization"
- "List all Windows sensors"
- "Find all sensors with hostname starting with 'prod-'"
- "Show me sensors with IP address 10.0.1.50"
- "How many sensors do I have?"

## What This Skill Does

This skill lists all sensors in the organization by calling the LimaCharlie API. It supports pagination automatically and can filter results by hostname prefix or IP address.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

Optional parameters:
- **with_hostname_prefix**: Filter sensors where hostname starts with this prefix
- **with_ip**: Filter sensors with this IP address (matches internal or external IP)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Optional filters are properly formatted

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

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
- Path: `/sensors/{oid}` (replace with actual organization ID)
- Query parameters: None (pagination handled via continuation tokens internally)
- No request body needed

**Note:** The SDK method `org.ListSensors()` handles pagination automatically using continuation tokens returned by the API.

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "sensors": {
      "sensor-id-1": {
        "sid": "sensor-id-1",
        "hostname": "SERVER01",
        "plat": 268435456,
        "arch": 1,
        "enroll": "2024-01-15T10:30:00Z",
        "alive": "2024-01-20T14:22:13Z",
        "int_ip": "10.0.1.50",
        "ext_ip": "203.0.113.45",
        "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
        "iid": "install-key-123"
      },
      "sensor-id-2": {
        "sid": "sensor-id-2",
        "hostname": "WORKSTATION-05",
        ...
      }
    },
    "continuation_token": ""
  }
}
```

**Success (200):**
- The response contains a map of sensor objects keyed by sensor ID
- Each sensor has basic metadata (hostname, platform, IPs, last seen)
- Empty `continuation_token` means all sensors have been retrieved
- Apply client-side filtering for hostname prefix or IP address after retrieval

**Common Errors:**
- **403 Forbidden**: Insufficient permissions to list sensors in the organization
- **500 Server Error**: Rare, retry or check LimaCharlie service status

### Step 4: Format the Response

Present the result to the user:
- Display sensor count at the top
- List sensors in a tabular format with key fields
- Apply any requested filters (hostname prefix, IP address)
- Sort by hostname or last seen timestamp for better readability
- Highlight offline sensors or sensors that haven't checked in recently

**Example formatted output:**
```
Sensors (5 total):

ID              Hostname         Platform    Last Seen            Internal IP    External IP
--------------------------------------------------------------------------------
xyz-123         SERVER01         Windows     2024-01-20 14:22    10.0.1.50      203.0.113.45
abc-456         WORKSTATION-05   Windows     2024-01-20 14:20    10.0.1.105     203.0.113.46
def-789         ubuntu-web-01    Linux       2024-01-20 14:18    10.0.2.10      203.0.113.47
...
```

## Example Usage

### Example 1: List all sensors

User request: "Show me all sensors in my organization"

Steps:
1. Get organization ID from context
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/sensors/c7e8f940-1234-5678-abcd-1234567890ab"
)
```
3. Format and display all sensors

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "sensors": {
      "sensor-1": { ... },
      "sensor-2": { ... },
      ...
    }
  }
}
```

### Example 2: Filter by hostname prefix

User request: "List all sensors with hostname starting with 'prod-'"

Steps:
1. Get all sensors using the API call
2. Filter results client-side where `hostname` starts with "prod-"
3. Display filtered list:
```
Production Sensors (3 total):
- prod-web-01 (sensor-123)
- prod-db-01 (sensor-456)
- prod-app-01 (sensor-789)
```

### Example 3: Filter by IP address

User request: "Find the sensor with IP 10.0.1.50"

Steps:
1. Get all sensors using the API call
2. Filter results where `int_ip` or `ext_ip` matches "10.0.1.50"
3. Display matching sensor(s)

## Additional Notes

- The API automatically handles pagination using continuation tokens
- Large organizations may have hundreds or thousands of sensors
- Platform codes: Windows=268435456, Linux=67108864, macOS=33554432
- Filtering is done client-side after retrieving all sensors
- For more specific searches, consider using `search-hosts` skill with wildcard patterns
- Use `get-online-sensors` skill if you only need to know which sensors are currently online
- The `alive` timestamp indicates when the sensor last checked in
- Sensors that haven't checked in for more than a few minutes are likely offline
- Consider caching the sensor list if you need to perform multiple queries

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/core/core.go`
