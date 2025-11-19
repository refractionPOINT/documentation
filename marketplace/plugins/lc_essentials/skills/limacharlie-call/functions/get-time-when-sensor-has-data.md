
# Get Sensor Data Timeline

Get the time range when a sensor has telemetry data available.

## When to Use

Use this skill when the user needs to:
- Check if sensor has data in a specific timeframe
- Verify data retention for a sensor
- Determine earliest available data
- Find latest data timestamp
- Troubleshoot missing sensor data
- Plan historical queries

Common scenarios:
- "Does this sensor have data from last week?"
- "When did this sensor start sending telemetry?"
- "What's the earliest data available for this sensor?"
- "Check if we have data for the incident timeframe"
- "Verify sensor data retention"

## What This Skill Does

This skill queries the sensor's data timeline to return the timestamps for which telemetry data is available.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID
- **sid**: Sensor ID

## How to Use

### Step 1: Validate Parameters

Ensure valid org ID and sensor ID.

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="get_time_when_sensor_has_data",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "xyz-sensor-id"
  }
)
```

**Tool Details:**
- Tool name: `get_time_when_sensor_has_data`
- Required parameters:
  - `oid`: Organization ID
  - `sid`: Sensor ID

### Step 3: Handle Response

The tool returns data directly:
```json
{
  "overview": [1705000000, 1705003600, 1705007200, ...]
}
```

**Success:**
- `overview`: Array of Unix timestamps representing time batches where sensor data is available
- Empty array means no data in the requested timeframe

### Step 4: Format Response

```
Sensor Data Availability: xyz-sensor-id

Data Batches Found: 45 timestamps
- First batch: 2024-01-11 12:00:00 UTC
- Last batch: 2024-01-21 14:00:00 UTC

Status: Data available for historical queries in this timeframe
```

## Example Usage

### Example 1: Check data availability

User: "Does sensor xyz-123 have data from last week?"

Steps:
1. Get organization ID from context
2. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_time_when_sensor_has_data",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "xyz-123"
  }
)
```
3. Compare returned timestamps with the requested timeframe

### Example 2: Troubleshoot missing data

User: "Why can't I query events for this sensor?"

Check timeline to verify sensor has any data available.

## Additional Notes

- Empty response means no data retained
- Useful before running expensive queries
- Data retention depends on org tier/policy
- Sensors may have gaps in timeline

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

SDK: `../go-limacharlie/limacharlie/organization.go`
MCP: `../lc-mcp-server/internal/tools/historical/historical.go`
