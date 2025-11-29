
# Get Historic Events for Sensor

Retrieve historical telemetry events for a specific sensor within a specified time range.

## When to Use

Use this skill when the user needs to:
- Get historical events for a specific sensor
- Build forensic timelines for incident investigation
- Review sensor activity during a specific time window
- Correlate events on a single endpoint
- Analyze sensor behavior before/after an incident
- Extract specific event types from sensor history

Common scenarios:
- "Show me all events from sensor xyz-123 between 2PM and 3PM yesterday"
- "Get process execution history for this sensor today"
- "Retrieve network connections from sensor abc-456 in the last hour"
- "Show DNS requests from this endpoint during the incident window"
- "Build a timeline of events on this compromised system"

## What This Skill Does

This skill retrieves historical telemetry events for a single sensor within a specified time range. It can optionally filter by event type and supports pagination for large result sets.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.

**⚠️ CRITICAL: Timestamps Must Be in SECONDS, Not Milliseconds**

The `start` and `end` parameters require Unix epoch timestamps in **seconds** (10 digits), NOT milliseconds (13 digits).

- Detection and event data from LimaCharlie contains timestamps in **milliseconds** (e.g., `event_time: 1764445150453`)
- This API requires timestamps in **seconds** (e.g., `start: 1764445150`)
- **You MUST divide by 1000** when using timestamps from detection/event data

```
Detection timestamp (ms): 1764445150453
                        ÷ 1000
API parameter (seconds):  1764445150
```

- **oid**: Organization ID (required for all API calls)
- **sid**: Sensor ID (UUID format)
- **start**: Start timestamp in Unix epoch **seconds** (NOT milliseconds)
- **end**: End timestamp in Unix epoch **seconds** (NOT milliseconds)

Optional parameters:
- **limit**: Maximum number of events to return (default: 1000)
- **event_type**: Filter by specific event type (e.g., "NEW_PROCESS", "DNS_REQUEST")

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid)
3. Start and end timestamps (Unix epoch in seconds)
4. Time range is reasonable (not too large)
5. Sensor has data retention for the requested timeframe

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="get_historic_events",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "xyz-sensor-id",
    "start": 1705761234,
    "end": 1705764834,
    "limit": 1000,
    "event_type": "NEW_PROCESS"
  }
)
```

**Tool Details:**
- Tool name: `get_historic_events`
- Parameters:
  - `oid`: Organization ID (required)
  - `sid`: Sensor ID (required)
  - `start`: Unix epoch timestamp in seconds (required)
  - `end`: Unix epoch timestamp in seconds (required)
  - `limit`: Max events to return (optional, default 1000)
  - `event_type`: Filter by type (optional)

### Step 3: Handle the Response

The tool returns events:
```json
{
  "events": [
    {
      "event": {
        "TIMESTAMP": 1705761234567,
        "EVENT_TYPE": "NEW_PROCESS",
        "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
        "COMMAND_LINE": "cmd.exe /c whoami",
        "PARENT_PROCESS_ID": 1234,
        "PROCESS_ID": 5678,
        "USER": "DOMAIN\\administrator"
      },
      "routing": {
        "sid": "xyz-sensor-id",
        "hostname": "SERVER01",
        "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
      }
    }
  ]
}
```

**Success:**
- Returns array of events in chronological order
- Each event contains `event` data and `routing` metadata
- Events are streamed efficiently for large result sets
- Pagination handled automatically

**Common Errors:**
- **400 Bad Request**: Invalid timestamp format or parameters
- **404 Not Found**: Sensor does not exist or no data in timeframe
- **403 Forbidden**: Insufficient permissions or retention policy limits
- **413 Payload Too Large**: Timeframe too large, narrow the window or use smaller limit
- **500 Server Error**: Service issue, retry with smaller timeframe

### Step 4: Format the Response

Present the result to the user:
- Display events in chronological timeline format
- Show event count and timeframe queried
- Highlight key fields based on event type
- Convert timestamps to human-readable format
- Group similar events if many results
- Indicate if limit was reached

**Example formatted output:**
```
Historic Events for SERVER01 (sensor xyz-123)
Time Range: 2024-01-20 14:00:00 to 2024-01-20 15:00:00
Events: 45 found (limit: 1000)

Timeline:

[14:22:15] NEW_PROCESS
  File: C:\Windows\System32\cmd.exe
  Command: cmd.exe /c whoami
  User: DOMAIN\administrator
  PID: 5678

[14:23:01] NETWORK_CONNECTIONS
  Protocol: TCP
  Remote IP: 203.0.113.50
  Remote Port: 443
  State: ESTABLISHED

[14:24:33] DNS_REQUEST
  Domain: api.example.com
  Request Type: A
  Response: 203.0.113.100

...
```

## Example Usage

### Example 1: Get all events in timeframe

User request: "Show me all events from sensor xyz-123 between 2PM and 3PM yesterday"

Steps:
1. Convert "2PM to 3PM yesterday" to Unix timestamps
2. Call the tool:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="get_historic_events",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "xyz-123",
    "start": 1705676400,
    "end": 1705680000,
    "limit": 1000
  }
)
```
3. Build timeline from returned events

### Example 2: Filter by event type

User request: "Get process execution history for sensor abc-456 today"

Steps:
1. Calculate today's start and end timestamps
2. Add event_type filter for "NEW_PROCESS"
3. Call the tool with filter:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="get_historic_events",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc-456",
    "start": 1705708800,
    "end": 1705795200,
    "event_type": "NEW_PROCESS",
    "limit": 500
  }
)
```
4. Display process executions with command lines

### Example 3: Network activity investigation

User request: "Show DNS requests from this endpoint during the incident window"

Steps:
1. Get incident timeframe from context
2. Filter for DNS_REQUEST events
3. Format results showing domains queried

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Using milliseconds instead of seconds | Empty results, no data found | Divide timestamp by 1000 |
| Timestamp from detection data used directly | Query returns nothing | `event_time / 1000` for seconds |
| Time range too narrow | No events returned | Expand window by a few seconds |
| Time range too wide | Timeout or too many results | Narrow window, use limit parameter |

**Example of the most common mistake:**

```
# WRONG - Using milliseconds from detection
start: 1764445150453  # 13 digits = milliseconds = WRONG
end:   1764445200453

# CORRECT - Converted to seconds
start: 1764445150     # 10 digits = seconds = CORRECT
end:   1764445200
```

## Additional Notes

- **Timestamps in API parameters**: Must be in **seconds** (10 digits)
- **Timestamps in returned event data**: Are in **milliseconds** (13 digits)
- Time range should be reasonable; very large ranges may timeout
- Default limit of 1000 events prevents overwhelming responses
- Events are returned in chronological order
- Event types include: NEW_PROCESS, DNS_REQUEST, NETWORK_CONNECTIONS, FILE_CREATE, FILE_DELETE, REGISTRY_CREATE, etc.
- Use `get-time-when-sensor-has-data` to check data availability first
- Sensors must have data retention for the queried timeframe
- Free tier typically has 30-day retention; paid tiers may have longer
- Consider using LCQL queries for more complex filtering across multiple sensors
- Large result sets may take time to retrieve
- Combine with `get_sensor_info` to get sensor context before querying events

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/forensics/forensics.go`
