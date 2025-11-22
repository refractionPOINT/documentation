
# List Sensors

Retrieve a list of all sensors in your LimaCharlie organization with powerful server-side filtering using bexpr selector syntax.

## When to Use

Use this skill when the user needs to:
- List all sensors in the organization
- Get a sensor inventory or fleet overview
- Filter sensors by platform (Windows, Linux, macOS, Chrome)
- Filter sensors by hostname patterns (e.g., all servers starting with "web-")
- Filter sensors by IP address (internal or external)
- Filter sensors by tags
- Filter sensors by online/offline status
- Count total number of sensors or specific subsets
- Find sensors matching complex criteria (combine multiple filters)

Common scenarios:
- "Show me all sensors in my organization"
- "List all online sensors"
- "Show me all Windows sensors"
- "Find all sensors with hostname starting with 'prod-'"
- "Show me sensors with IP address 10.0.1.50"
- "List all Linux servers that are online"
- "Find sensors tagged with 'critical'"
- "How many sensors do I have?"

## What This Skill Does

This skill lists all sensors in the organization by calling the LimaCharlie API's `list_sensors` function. It supports powerful server-side filtering using **bexpr selector syntax**, which allows you to construct complex queries that are evaluated on the server before results are returned. The SDK handles pagination internally, so all matching sensors are returned automatically.

**Key advantage**: All filtering is done **server-side**, making this extremely efficient even for large sensor fleets.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

Optional parameters:
- **selector**: Bexpr expression for complex server-side filtering (see examples below)
- **online_only**: Boolean flag to return only online sensors (true) or all sensors (false/omitted)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Properly formatted selector expression (if using filtering)
3. Valid boolean value for online_only (if filtering by online status)

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

**Basic usage (all sensors):**
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
  }
)
```

**With selector filtering:**
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "selector": "plat == `windows`"
  }
)
```

**With online filtering:**
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "online_only": true
  }
)
```

**Tool Details:**
- Tool name: `list_sensors`
- Required parameters:
  - `oid`: Organization ID
- Optional parameters:
  - `selector`: Bexpr expression for filtering (string)
  - `online_only`: Return only online sensors (boolean)

**Note:** The tool returns all sensors automatically (pagination is handled internally by the SDK).

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
- Each sensor has sid, hostname, platform, last_seen, internal_ip, and external_ip
- The `count` field indicates the total number of sensors returned
- All matching sensors are returned in a single response

**Common Errors:**
- **400 Bad Request**: Invalid selector syntax or parameter format
- **403 Forbidden**: Insufficient permissions to list sensors in the organization
- **500 Server Error**: Rare, retry or check LimaCharlie service status

### Step 4: Format the Response

Present the result to the user:
- Display sensor count at the top
- List sensors in a tabular format with key fields
- All filtering is applied server-side before the response is returned
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

## Selector Syntax (Bexpr)

The `selector` parameter uses **bexpr** (boolean expression) syntax for powerful server-side filtering. All filtering happens on the server before results are returned, making it highly efficient.

### Available Fields

You can filter on the following sensor fields:
- `sid`: Sensor ID (UUID)
- `oid`: Organization ID (UUID)
- `plat`: Platform (e.g., "windows", "linux", "macos", "chrome")
- `arch`: Architecture (e.g., "x86_64", "arm64")
- `hostname`: Sensor hostname (string)
- `int_ip`: Internal IP address (string)
- `ext_ip`: External IP address (string)
- `alive`: Last seen timestamp (Unix timestamp or ISO string)
- `tags`: Array of tag strings

### Bexpr Operators

**Comparison:**
- `==`: Equals
- `!=`: Not equals
- `>`, `<`, `>=`, `<=`: Numeric/timestamp comparison

**String matching:**
- `matches`: Regex pattern matching (e.g., `hostname matches "^web-"`)
- `contains`: Substring matching

**Logical:**
- `and`: Logical AND
- `or`: Logical OR
- `not`: Logical NOT

**Membership:**
- `in`: Check if value is in array (e.g., `"critical" in tags`)

**Note on string literals:** In bexpr syntax, string literals must be enclosed in backticks (`` ` ``) when used with operators. For example: `` plat == `windows` ``

### Selector Examples

**Filter by platform:**
```
selector: "plat == `windows`"
selector: "plat == `linux`"
selector: "plat == `macos`"
```

**Filter by hostname pattern:**
```
selector: "hostname matches `^web-`"       # Starts with "web-"
selector: "hostname matches `^prod-.*-db$`" # Starts with "prod-", ends with "-db"
selector: "hostname contains `test`"        # Contains "test" anywhere
```

**Filter by IP address:**
```
selector: "int_ip == `10.0.1.50`"                    # Exact internal IP
selector: "ext_ip == `203.0.113.45`"                 # Exact external IP
selector: "int_ip matches `^10\\.0\\.1\\.`"          # Internal IP in 10.0.1.0/24 subnet
```

**Filter by tags:**
```
selector: "`critical` in tags"      # Has "critical" tag
selector: "`prod` in tags"          # Has "prod" tag
selector: "`test` in tags"          # Has "test" tag
```

**Combine multiple conditions (AND):**
```
selector: "plat == `windows` and `prod` in tags"
selector: "hostname matches `^web-` and int_ip matches `^10\\.0\\.`"
```

**Combine multiple conditions (OR):**
```
selector: "plat == `windows` or plat == `linux`"
selector: "hostname matches `^web-` or hostname matches `^app-`"
```

**Complex combinations:**
```
selector: "(plat == `windows` or plat == `linux`) and `critical` in tags"
selector: "hostname matches `^prod-` and (plat == `linux` or plat == `macos`)"
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
    { "sid": "sensor-1", "hostname": "SERVER01", "platform": "windows", ... },
    { "sid": "sensor-2", "hostname": "WORKSTATION-05", "platform": "windows", ... }
  ],
  "count": 2
}
```

### Example 2: List all Windows sensors

User request: "Show me all Windows sensors"

Steps:
1. Call tool with platform selector:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "selector": "plat == `windows`"
  }
)
```
2. Display filtered results:
```
Windows Sensors (15 total):
- SERVER01 (sid: abc-123)
- WORKSTATION-05 (sid: def-456)
...
```

### Example 3: List online sensors only

User request: "Show me all online sensors"

Steps:
1. Call tool with online_only flag:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "online_only": true
  }
)
```
2. Display online sensors only

### Example 4: Filter by hostname pattern

User request: "List all sensors with hostname starting with 'prod-'"

Steps:
1. Call tool with hostname selector:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "selector": "hostname matches `^prod-`"
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

### Example 5: Filter by IP address

User request: "Find the sensor with IP 10.0.1.50"

Steps:
1. Call tool with IP selector:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "selector": "int_ip == `10.0.1.50` or ext_ip == `10.0.1.50`"
  }
)
```
2. Display matching sensor(s)

### Example 6: Combine filters (online Windows sensors)

User request: "Show me all online Windows sensors"

Steps:
1. Call tool with both selector and online_only:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "selector": "plat == `windows`",
    "online_only": true
  }
)
```
2. Display online Windows sensors

### Example 7: Filter by tags

User request: "List all sensors tagged with 'critical'"

Steps:
1. Call tool with tag selector:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "selector": "`critical` in tags"
  }
)
```
2. Display tagged sensors

### Example 8: Complex filter (production Linux servers)

User request: "Find all production Linux servers that are online"

Steps:
1. Call tool with complex selector and online filter:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "selector": "plat == `linux` and hostname matches `^prod-`",
    "online_only": true
  }
)
```
2. Display matching sensors

## Common Filtering Patterns

These patterns show the most efficient ways to filter sensors using the new selector syntax.

### Pattern 1: Online sensors only

**Most efficient approach** for checking active sensors:

```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "online_only": true
  }
)
```

**Server-side filtering** returns only online sensors, reducing data transfer for large fleets.

### Pattern 2: Platform-specific sensors

**Best practice** for targeting specific operating systems:

```
# Windows sensors
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "selector": "plat == `windows`"
  }
)

# Linux sensors
selector: "plat == `linux`"

# Multiple platforms
selector: "plat == `windows` or plat == `linux`"
```

### Pattern 3: Online sensors with platform filter

**Combine online_only with selector** for maximum efficiency:

```
mcp__limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "selector": "plat == `windows`",
    "online_only": true
  }
)
```

**Why this approach?**
- Both filters are evaluated **server-side** before results are returned
- If you have 1000 sensors (600 Windows, 400 Linux) and 200 are offline, you get only 480 Windows sensors that are online
- Minimal data transfer and processing

### Pattern 4: Hostname pattern matching

**Use regex for flexible hostname filtering:**

```
# Servers starting with "web-"
selector: "hostname matches `^web-`"

# Servers ending with "-prod"
selector: "hostname matches `-prod$`"

# Servers containing "test"
selector: "hostname contains `test`"

# Complex pattern: starts with "prod-", ends with "-db"
selector: "hostname matches `^prod-.*-db$`"
```

### Pattern 5: IP subnet filtering

**Filter by IP range using regex:**

```
# All sensors in 10.0.1.0/24 subnet
selector: "int_ip matches `^10\\.0\\.1\\.`"

# All sensors in 192.168.0.0/16 network
selector: "int_ip matches `^192\\.168\\.`"

# Specific IP address
selector: "int_ip == `10.0.1.50`"
```

### Pattern 6: Tag-based filtering

**Filter by sensor tags:**

```
# Sensors with "critical" tag
selector: "`critical` in tags"

# Combine with platform
selector: "plat == `windows` and `critical` in tags"

# Multiple conditions
selector: "`prod` in tags and hostname matches `^web-`"
```

### Filtering Performance Tips

**All filters are server-side** with the new selector syntax:
- `selector`: Evaluated on the server before returning results (most powerful)
- `online_only`: Evaluated on the server before returning results

**Best Practice**:
- Use `selector` for complex filtering (platform, hostname, IP, tags, etc.)
- Use `online_only` when you only need online sensors
- Combine both for maximum efficiency (e.g., online Windows servers)
- All filtering happens server-side, so there's no difference in efficiency between simple and complex selectors

**Migration from old API:**
- Old `with_hostname_prefix: "prod-"` → New `selector: "hostname matches '^prod-'"`
- Old `with_ip: "10.0.1.50"` → New `selector: "int_ip == '10.0.1.50' or ext_ip == '10.0.1.50'"`
- Old `is_online: true` → New `online_only: true`
- Old platform filtering → New `selector: "plat == 'windows'"`

## Additional Notes

- The tool automatically returns all sensors (pagination is handled internally by the SDK)
- Large organizations may have hundreds or thousands of sensors - use selectors to narrow results
- **All filtering is server-side** using the `selector` and `online_only` parameters
- The `selector` parameter uses bexpr syntax, which is very powerful and flexible
- You can combine multiple conditions using `and`, `or`, and parentheses for grouping
- String literals in selectors must use backticks (`` ` ``) around values
- Regex patterns in `matches` operator use standard regex syntax
- The `last_seen` timestamp indicates when the sensor last checked in
- Sensors that haven't checked in for more than a few minutes are likely offline
- Consider caching the sensor list if you need to perform multiple queries
- For wildcard hostname searches, use the `selector` with regex patterns (e.g., `hostname matches "^pattern"`)

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/core/core.go`
