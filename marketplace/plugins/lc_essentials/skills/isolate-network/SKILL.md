---
name: isolate-network
description: Isolate a sensor from the network to contain threats during incident response. Blocks all network access except LimaCharlie communication. Use for quarantine, containment, preventing lateral movement, stopping ransomware spread, or isolating compromised endpoints during security incidents.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Isolate Network

Isolate a sensor from the network to contain threats and prevent lateral movement during security incidents.

## When to Use

Use this skill when the user needs to:
- Quarantine a compromised or suspicious endpoint
- Contain an active threat or malware infection
- Prevent lateral movement during an incident
- Stop ransomware from spreading to other systems
- Isolate a sensor during forensic investigation

Common scenarios:
- "Isolate the infected machine to stop the attack"
- "Quarantine sensor XYZ immediately"
- "Cut off network access for this compromised host"
- "Contain this endpoint during the incident response"

## What This Skill Does

This skill isolates a sensor from the network by blocking all network traffic except communication with LimaCharlie. The sensor remains manageable through the LimaCharlie platform, allowing continued monitoring and tasking while preventing any lateral movement or external communication. This is a critical incident response action for threat containment.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all API calls)
- **sid**: Sensor ID (UUID format) - the sensor to isolate

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Confirm the sensor exists and is the correct target for isolation

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/[sensor-id]/isolation"
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/{sid}/isolation` where `{sid}` is the sensor UUID
- No query parameters needed
- No request body needed

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

**Success (200-299):**
- Status code 200 indicates the sensor was successfully isolated
- The sensor will immediately begin blocking all network traffic except LC communication
- The sensor remains online and responsive to LC commands
- Network isolation is persistent until explicitly removed

**Common Errors:**
- **400 Bad Request**: Invalid sensor ID format - verify the sid is a valid UUID
- **404 Not Found**: Sensor does not exist - verify the sid is correct and the sensor is enrolled
- **403 Forbidden**: Insufficient permissions - requires sensor management permissions
- **409 Conflict**: Sensor may already be isolated or in an incompatible state
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm the sensor is now isolated from the network
- Explain that the sensor can still be managed through LimaCharlie
- Warn that all network applications on the endpoint will lose connectivity
- Mention that isolation persists until explicitly removed with rejoin-network
- Remind the user to monitor the sensor and investigate the threat

## Example Usage

### Example 1: Isolate Compromised Sensor

User request: "Isolate sensor abc12345-6789-0123-4567-890abcdef012 immediately, it's been compromised"

Steps:
1. Validate the sensor ID format (UUID)
2. Confirm this is the correct sensor to isolate
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/abc12345-6789-0123-4567-890abcdef012/isolation"
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

Response to user:
"Sensor abc12345-6789-0123-4567-890abcdef012 has been successfully isolated from the network. The endpoint can no longer communicate with other systems but remains manageable through LimaCharlie. All network applications on this machine will lose connectivity. The isolation will remain active until you explicitly rejoin the sensor to the network."

### Example 2: Contain Active Ransomware

User request: "Quarantine the host with ransomware immediately to stop it from spreading"

Steps:
1. First identify the sensor ID (may need to search by hostname)
2. Validate the sensor exists and is the correct target
3. Call API to isolate:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/def45678-90ab-cdef-0123-456789abcdef/isolation"
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

Response to user:
"The infected host has been quarantined successfully. Network isolation is now active, preventing the ransomware from spreading to other systems. The sensor remains under LimaCharlie management for continued monitoring and investigation. You should now investigate the extent of the infection and determine next steps for remediation."

## Additional Notes

- Network isolation is immediate and persistent until explicitly removed
- The sensor maintains its connection to LimaCharlie only - all other traffic is blocked
- Isolation happens at the kernel level, bypassing any malware or user intervention
- Users on the endpoint will experience complete network loss (except LC)
- You can still task the sensor, collect artifacts, and run commands while isolated
- Use the `is-isolated` skill to check current isolation status
- Use the `rejoin-network` skill to restore normal network access
- This is a critical containment action - ensure you have the correct sensor before isolating
- Consider tagging the sensor (use `add-tag` skill) to track isolation status and reason

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go` (IsolateFromNetwork method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/response/response.go` (isolate_network)
