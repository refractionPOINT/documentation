
# Is Isolated

Check whether a sensor is currently isolated from the network to verify containment status during incident response.

## When to Use

Use this skill when the user needs to:
- Check if a sensor is currently quarantined
- Verify network isolation status before rejoining
- Confirm a sensor was successfully isolated
- Audit which sensors are in isolation
- Check containment status during incident response

Common scenarios:
- "Is this sensor isolated?"
- "Check if the quarantine is still active"
- "Verify the sensor is cut off from the network"
- "Show me the isolation status of this endpoint"

## What This Skill Does

This skill retrieves the current network isolation status of a sensor. It returns a boolean value indicating whether the sensor is isolated (true) or connected to the network normally (false). This is useful for verifying containment actions and checking sensor state before making changes.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **sid**: Sensor ID (UUID format) - the sensor to check

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Confirm the sensor exists in your organization

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="is_isolated",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc12345-6789-0123-4567-890abcdef012"
  }
)
```

**Tool Details:**
- Tool name: `is_isolated`
- Required parameters:
  - `oid`: Organization ID
  - `sid`: Sensor ID

### Step 3: Handle the Response

The tool returns data directly:
```json
{
  "is_isolated": true
}
```

**Success:**
- The response contains the isolation status
- `is_isolated: true` means the sensor is currently isolated from the network
- `is_isolated: false` means the sensor has normal network connectivity
- Extract and return this boolean value to the user

**Common Errors:**
- **400 Bad Request**: Invalid sensor ID format - verify the sid is a valid UUID
- **404 Not Found**: Sensor does not exist - verify the sid is correct and the sensor is enrolled
- **403 Forbidden**: Insufficient permissions - requires sensor read permissions
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Clearly state whether the sensor is isolated or not
- If isolated, remind the user they can use `rejoin-network` to restore access
- If not isolated, mention they can use `isolate-network` if needed
- Include the sensor ID and hostname for clarity
- Suggest next actions based on the isolation state

## Example Usage

### Example 1: Check Isolation Before Rejoining

User request: "Is sensor abc12345-6789-0123-4567-890abcdef012 still isolated?"

Steps:
1. Validate the sensor ID format (UUID)
2. Call tool to get isolation status:
```
mcp__limacharlie__lc_call_tool(
  tool_name="is_isolated",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc12345-6789-0123-4567-890abcdef012"
  }
)
```

Expected response:
```json
{
  "is_isolated": true
}
```

Response to user:
"Yes, sensor abc12345-6789-0123-4567-890abcdef012 is currently isolated from the network. The endpoint cannot communicate with other systems but remains manageable through LimaCharlie. If you want to restore network access, use the rejoin-network skill."

### Example 2: Verify Isolation After Containment

User request: "Check if the quarantine worked for the infected machine"

Steps:
1. Identify the sensor ID
2. Call tool to verify isolation status:
```
mcp__limacharlie__lc_call_tool(
  tool_name="is_isolated",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "def45678-90ab-cdef-0123-456789abcdef"
  }
)
```

Expected response:
```json
{
  "is_isolated": false
}
```

Response to user:
"The sensor def45678-90ab-cdef-0123-456789abcdef is NOT currently isolated. It has normal network connectivity. If this machine should be quarantined, you need to use the isolate-network skill to contain the threat."

## Additional Notes

- The isolation status is a real-time boolean flag in the sensor metadata
- This check does not modify the sensor state - it's read-only
- The `is_isolated` field is always present in sensor information
- You can check isolation status even if the sensor is offline
- This is useful before performing isolation or rejoin operations
- Consider checking this before calling `rejoin-network` to confirm isolation is active
- Use this in automation workflows to make decisions based on isolation state
- The isolation state persists across sensor reboots and remains until explicitly removed

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go` (Update method, IsIsolated field)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/response/response.go` (is_isolated)
