
# List Sensors

Retrieve a list of all sensors in your LimaCharlie organization with optional filtering capabilities.

## When to Use

Use this skill when the user needs to:
- List all sensors in the organization
- Get a sensor inventory or fleet overview
- Filter sensors by hostname prefix (e.g., all servers starting with "web-")
- Filter sensors by IP address (internal or external)
- Filter sensors by online/offline status
- Count total number of sensors
- Find sensors matching specific naming patterns

Common scenarios:
- "Show me all sensors in my organization"
- "List all online sensors"
- "Show me all offline sensors"
- "Find all sensors with hostname starting with 'prod-'"
- "Show me sensors with IP address 10.0.1.50"
- "How many sensors do I have?"

## What This Skill Does

This skill lists all sensors in the organization by calling the LimaCharlie API. It returns all sensors automatically and can filter results by hostname prefix, IP address, or online status.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

Optional parameters:
- **with_hostname_prefix**: Filter sensors where hostname starts with this prefix
- **with_ip**: Filter sensors with this IP address (matches internal or external IP)
- **is_online**: Filter sensors by online status (true for online, false for offline)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Optional filters are properly formatted

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
  }
)
```

**Tool Details:**
- Tool name: `list_sensors`
- Required parameters:
  - `oid`: Organization ID
- Optional parameters:
  - `with_hostname_prefix`: Filter by hostname prefix
  - `with_ip`: Filter by IP address
  - `is_online`: Filter by online status (boolean)

**Note:** The tool returns all sensors automatically (pagination is handled internally).

### Step 3: Handle the Response

The tool returns data directly:
```json
{
  "sensors": [
    {
      "sid": "sensor-id-1",
      "hostname": "SERVER01",
      "platform": "windows",
      "last_seen": "2024-01-20T14:22:13Z",
      "internal_ip": "10.0.1.50",
      "external_ip": "203.0.113.45"
    },
    {
      "sid": "sensor-id-2",
      "hostname": "WORKSTATION-05",
      "platform": "windows",
      "last_seen": "2024-01-20T14:20:00Z",
      "internal_ip": "10.0.1.105",
      "external_ip": "203.0.113.46"
    }
  ],
  "count": 2
}
```

**Success:**
- The response contains an array of sensor objects with basic metadata
- Each sensor has hostname, platform, IPs, and last seen timestamp
- The `count` field indicates the total number of sensors returned
- All matching sensors are returned in a single response

**Common Errors:**
- **403 Forbidden**: Insufficient permissions to list sensors in the organization
- **500 Server Error**: Rare, retry or check LimaCharlie service status

### Step 4: Format the Response

Present the result to the user:
- Display sensor count at the top
- List sensors in a tabular format with key fields
- Filters (hostname prefix, IP address, online status) are applied automatically by the tool
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
2. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
  }
)
```
3. Format and display all sensors

Expected response:
```json
{
  "sensors": [
    { "sid": "sensor-1", "hostname": "SERVER01", ... },
    { "sid": "sensor-2", "hostname": "WORKSTATION-05", ... }
  ],
  "count": 2
}
```

### Example 2: Filter by hostname prefix

User request: "List all sensors with hostname starting with 'prod-'"

Steps:
1. Call tool with hostname filter:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "with_hostname_prefix": "prod-"
  }
)
```
2. Display filtered results:
```
Production Sensors (3 total):
- prod-web-01 (sensor-123)
- prod-db-01 (sensor-456)
- prod-app-01 (sensor-789)
```

### Example 3: Filter by online status

User request: "Show me all online sensors"

Steps:
1. Call tool with online filter:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "is_online": true
  }
)
```
2. Display online sensors only

### Example 4: Filter by IP address

User request: "Find the sensor with IP 10.0.1.50"

Steps:
1. Call tool with IP filter:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "with_ip": "10.0.1.50"
  }
)
```
2. Display matching sensor(s)

## Additional Notes

- The tool automatically returns all sensors (pagination is handled internally by the SDK)
- Large organizations may have hundreds or thousands of sensors
- Filtering is done server-side for `is_online` parameter (more efficient)
- The `with_hostname_prefix` and `with_ip` filters are applied client-side after retrieval
- For wildcard hostname searches, use the `search-hosts` skill instead
- You can combine multiple filters (e.g., `is_online=true` and `with_hostname_prefix="prod-"`)
- The `last_seen` timestamp indicates when the sensor last checked in
- Sensors that haven't checked in for more than a few minutes are likely offline
- Consider caching the sensor list if you need to perform multiple queries

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/core/core.go`
