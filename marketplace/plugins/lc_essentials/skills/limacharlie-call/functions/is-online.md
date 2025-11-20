
# Is Sensor Online

Check whether a specific sensor is currently online and responsive.

## When to Use

Use this skill when the user needs to:
- Check if a specific sensor is currently online
- Verify sensor connectivity before sending commands
- Troubleshoot sensor communication issues
- Confirm sensor availability for live investigation
- Determine if a sensor can receive tasking

Common scenarios:
- "Is sensor xyz-123 online?"
- "Can I run commands on this sensor?"
- "Check if SERVER01's sensor is connected"
- "Verify sensor availability before investigation"
- "Is the sensor on host WORKSTATION-05 responsive?"

## What This Skill Does

This skill checks the online status of a specific sensor by calling the LimaCharlie API. It returns a boolean indicating whether the sensor is currently connected and actively communicating with the platform.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **sid**: Sensor ID (UUID format)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="is_online",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "xyz-sensor-id"
  }
)
```

**Tool Details:**
- Tool name: `is_online`
- Required parameters:
  - `oid`: Organization ID
  - `sid`: Sensor ID

### Step 3: Handle the Response

The tool returns data directly:
```json
{
  "xyz-sensor-id": true
}
```

**Success:**
- Response contains a boolean value for the sensor ID
- `true`: Sensor is currently online and responsive
- `false`: Sensor is offline or not responding
- Extract the boolean value for the queried sensor

**Common Errors:**
- **400 Bad Request**: Invalid sensor ID format
- **404 Not Found**: Sensor does not exist in the organization
- **403 Forbidden**: Insufficient permissions to check sensor status
- **500 Server Error**: Rare, retry or check LimaCharlie service status

### Step 4: Format the Response

Present the result to the user:
- Clearly state whether the sensor is online or offline
- Include sensor ID and hostname (if available)
- Suggest next actions based on status
- If offline, mention checking `alive` timestamp for last seen time

**Example formatted output:**
```
Sensor xyz-123 (SERVER01) is currently ONLINE.

You can send live commands and perform investigation tasks on this sensor.
```

Or if offline:
```
Sensor xyz-123 (SERVER01) is currently OFFLINE.

The sensor is not responding to platform queries. Check:
- Network connectivity on the host
- Sensor process status
- Last seen timestamp using get-sensor-info
```

## Example Usage

### Example 1: Check sensor before tasking

User request: "Is sensor xyz-123 online?"

Steps:
1. Get organization ID from context
2. Call tool to check online status:
```
mcp__limacharlie__lc_call_tool(
  tool_name="is_online",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "xyz-123"
  }
)
```
3. Report status to user

Expected response:
```json
{
  "xyz-123": true
}
```

Result: "Sensor xyz-123 is ONLINE and ready for commands."

### Example 2: Troubleshoot connectivity

User request: "Why can't I run commands on sensor abc-456?"

Steps:
1. Check if sensor is online using the tool call
2. If offline, suggest troubleshooting steps
3. Recommend checking last seen timestamp:
```
Sensor abc-456 is currently OFFLINE.

Troubleshooting steps:
1. Check if sensor process is running on the host
2. Verify network connectivity to LimaCharlie platform
3. Check firewall rules
4. Use get-sensor-info to see last check-in time
5. Review sensor logs for errors
```

## Additional Notes

- A sensor is considered online if it has recently checked in (typically within last 1-2 minutes)
- Online status is real-time and can change quickly
- Sensors may go offline temporarily due to network issues or host restarts
- Always check online status before attempting live investigation tasks
- For bulk checking, use `get-online-sensors` to check all sensors at once
- The online check is lightweight and fast
- Combine with `get-sensor-info` to get full details including last seen timestamp
- Sensors in isolated mode may still be online but network-isolated
- Consider sensor location and network topology when troubleshooting connectivity

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/core/core.go`
