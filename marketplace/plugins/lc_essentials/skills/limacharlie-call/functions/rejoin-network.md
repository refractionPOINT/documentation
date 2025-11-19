
# Rejoin Network

Remove network isolation from a sensor and restore normal network connectivity after threat containment or investigation.

## When to Use

Use this skill when the user needs to:
- Restore network access after threat remediation
- End quarantine after verifying the endpoint is clean
- Remove isolation after completing forensic investigation
- Re-enable network connectivity after false positive isolation
- Bring a sensor back online after maintenance or testing

Common scenarios:
- "Remove isolation from the sensor now that it's clean"
- "Restore network access to the quarantined machine"
- "Rejoin the sensor to the network after investigation"
- "End the quarantine for this endpoint"

## What This Skill Does

This skill removes network isolation from a sensor, restoring full network connectivity. The sensor will be able to communicate with all systems and services normally. This reverses the action taken by the `isolate-network` skill and should only be done after confirming the threat has been contained or the endpoint has been remediated.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **sid**: Sensor ID (UUID format) - the sensor to rejoin to the network

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Confirm the sensor is currently isolated (use `is-isolated` skill to check)
4. Verify the threat has been remediated or investigation is complete
5. Confirm it's safe to restore network access

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="rejoin_network",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc12345-6789-0123-4567-890abcdef012"
  }
)
```

**Tool Details:**
- Tool name: `rejoin_network`
- Required parameters:
  - `oid`: Organization ID
  - `sid`: Sensor ID

### Step 3: Handle the Response

The tool returns data directly:
```json
{}
```

**Success:**
- Empty response indicates network isolation was successfully removed
- The sensor will immediately restore normal network connectivity
- All network applications and services can communicate normally
- The endpoint can now access other systems and the internet

**Common Errors:**
- **400 Bad Request**: Invalid sensor ID format - verify the sid is a valid UUID
- **404 Not Found**: Sensor does not exist or is not isolated - verify the sid and check isolation status
- **403 Forbidden**: Insufficient permissions - requires sensor management permissions
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm the sensor has rejoined the network
- Explain that network connectivity has been fully restored
- Mention that all applications can now communicate normally
- Remind the user to monitor the sensor for any suspicious activity
- Suggest removing any isolation-related tags if they were added

## Example Usage

### Example 1: Restore Network After Remediation

User request: "The malware has been cleaned, restore network access to sensor abc12345-6789-0123-4567-890abcdef012"

Steps:
1. Validate the sensor ID format (UUID)
2. Verify the sensor is currently isolated
3. Confirm remediation is complete
4. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="rejoin_network",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc12345-6789-0123-4567-890abcdef012"
  }
)
```

Expected response:
```json
{}
```

Response to user:
"Network isolation has been removed from sensor abc12345-6789-0123-4567-890abcdef012. The endpoint now has full network connectivity restored and all applications can communicate normally. Continue monitoring the sensor for any signs of re-infection or suspicious activity."

### Example 2: End False Positive Quarantine

User request: "This was a false alarm, rejoin the sensor to the network"

Steps:
1. Identify the sensor ID
2. Verify the sensor is isolated
3. Confirm this is a false positive
4. Call tool to rejoin:
```
mcp__limacharlie__lc_call_tool(
  tool_name="rejoin_network",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "def45678-90ab-cdef-0123-456789abcdef"
  }
)
```

Expected response:
```json
{}
```

Response to user:
"The sensor has been successfully rejoined to the network. Network connectivity is fully restored. Since this was a false positive, you may want to review and adjust the detection rule that triggered the isolation to prevent future false alarms."

## Additional Notes

- Network restoration is immediate once the tool call completes
- The sensor maintains all its configuration, tags, and management state
- If the sensor was not isolated, the operation will return a 404 or similar error
- Always verify remediation is complete before rejoining to prevent re-infection
- Consider using the `is-isolated` skill first to confirm current isolation status
- You may want to add a tag (use `add-tag` skill) to track when and why isolation was removed
- Monitor the sensor closely after rejoining to ensure no malicious activity resumes
- This reverses the `isolate-network` action - both operations are complementary
- Network restoration affects all traffic - there's no partial network access option

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go` (RejoinNetwork method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/response/response.go` (rejoin_network)
