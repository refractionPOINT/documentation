---
name: reliable-tasking
description: Send persistent tasks to sensors with automatic retry and delivery guarantee. Tasks persist until acknowledged or retention expires. Use for critical commands, offline sensor tasking, forensic collection, response actions, or fleet-wide operations that must execute even when sensors are temporarily offline.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Reliable Tasking

Send persistent, retry-enabled tasks to sensors that guarantee execution even when sensors are offline or intermittently connected.

## When to Use

Use this skill when the user needs to:
- Execute critical commands that must succeed
- Task sensors that are currently offline
- Perform fleet-wide operations across many sensors
- Collect forensic artifacts from intermittently connected endpoints
- Execute response actions with guaranteed delivery
- Schedule tasks for sensors with unreliable connectivity

Common scenarios:
- "Task all production servers to collect memory dumps"
- "Send a remediation command to offline sensors when they come back"
- "Execute this forensic collection across the entire fleet"
- "Run this command on sensors matching a specific criteria"

## What This Skill Does

This skill creates a persistent task that remains active until sensors execute it or the retention period expires. Unlike direct tasking, reliable tasks automatically retry when sensors come online and guarantee execution. Tasks can target specific sensors using sensor selectors (tags, platform, etc.) and can be associated with investigations for tracking. The task persists in the system for a configurable retention period (default 24 hours).

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **command**: The command to execute on sensors (LC sensor command syntax)

Optional parameters:
- **sensor_selector**: Expression to target specific sensors (e.g., `tag=production`, `platform=windows`)
- **investigation_id**: Investigation ID to associate the task with for tracking
- **retention_seconds**: How long to keep the task active (default: 86400 = 24 hours)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid command in LimaCharlie sensor command format
3. Appropriate sensor selector if targeting specific sensors
4. Reasonable retention period (default 86400 seconds = 24 hours)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/reliable_tasking",
  body={
    "command": "[sensor-command]",
    "sensor_selector": "[optional-selector]",
    "investigation_id": "[optional-investigation-id]",
    "retention": [retention-in-seconds]
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/reliable_tasking` (organization-level endpoint, no OID in path)
- No query parameters needed
- Body fields:
  - `command`: String - the LC sensor command to execute (required)
  - `sensor_selector`: String - selector expression to target sensors (optional)
  - `investigation_id`: String - investigation tracking ID (optional)
  - `retention`: Number - seconds to keep task active (optional, default: 86400)

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "task_id": "task-uuid-here",
    "command": "os_packages",
    "retention": 86400,
    "created": 1234567890
  }
}
```

**Success (200-299):**
- Status code 200 indicates the reliable task was created successfully
- Response includes a `task_id` for tracking
- The task is now active and will be delivered to matching sensors
- Sensors will receive and execute the task when they connect
- The task remains active for the retention period
- Use the task_id to monitor or cancel the task later

**Common Errors:**
- **400 Bad Request**: Invalid command format or parameters - verify command syntax
- **403 Forbidden**: Insufficient permissions - requires tasking permissions
- **404 Not Found**: Invalid endpoint or organization - verify OID
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm the reliable task was created
- Display the task ID for tracking
- Explain the retention period
- Mention which sensors will receive the task (based on selector)
- Suggest using `list-reliable-tasks` to monitor execution
- Note that the task will execute automatically when sensors connect

## Example Usage

### Example 1: Collect Memory from All Production Windows Sensors

User request: "Get memory dumps from all Windows production servers, even if they're offline"

Steps:
1. Construct the memory collection command
2. Create sensor selector for Windows + production tag
3. Set appropriate retention (48 hours for offline servers)
4. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/reliable_tasking",
  body={
    "command": "mem_map --pid 4",
    "sensor_selector": "platform=windows and tag=production",
    "investigation_id": "incident-2024-001",
    "retention": 172800
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "task_id": "abc12345-6789-0123-4567-890abcdef012",
    "command": "mem_map --pid 4",
    "retention": 172800,
    "created": 1234567890
  }
}
```

Response to user:
"Created reliable task abc12345-6789-0123-4567-890abcdef012 to collect memory maps from all Windows production servers. The task will automatically execute on matching sensors when they connect, even if currently offline. The task will remain active for 48 hours (172800 seconds) and is associated with investigation incident-2024-001. Use list-reliable-tasks to monitor execution status."

### Example 2: Emergency Response Action to All Compromised Sensors

User request: "Kill the malicious process on all sensors tagged as compromised"

Steps:
1. Create the process termination command
2. Target sensors with 'compromised' tag
3. Associate with incident investigation
4. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/reliable_tasking",
  body={
    "command": "deny_tree -p malware.exe",
    "sensor_selector": "tag=compromised",
    "investigation_id": "ransomware-response-2024",
    "retention": 86400
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "task_id": "def45678-90ab-cdef-0123-456789abcdef",
    "command": "deny_tree -p malware.exe",
    "retention": 86400,
    "created": 1234567890
  }
}
```

Response to user:
"Emergency response task created (ID: def45678-90ab-cdef-0123-456789abcdef) to terminate malware.exe on all compromised sensors. The task will execute automatically on any sensor with the 'compromised' tag, including offline sensors when they reconnect. Task is active for 24 hours and tracked under investigation ransomware-response-2024."

## Additional Notes

- Reliable tasks guarantee delivery - they persist until executed or retention expires
- Tasks execute automatically when matching sensors connect to LimaCharlie
- Use sensor selectors to target specific sensor groups (tags, platform, hostname patterns)
- Default retention is 24 hours (86400 seconds), maximum is typically 7 days
- Tasks are tracked by task_id for monitoring and management
- Multiple sensors can execute the same reliable task
- Tasks associated with investigation_id appear in investigation tracking
- Use this for critical operations that must succeed even with network issues
- Sensors execute tasks in order of receipt
- Task execution is confirmed when sensor acknowledges completion
- Failed task executions may retry depending on failure type
- Use `list-reliable-tasks` skill to see pending tasks
- Consider retention period based on sensor connectivity patterns
- Offline sensors will execute tasks immediately upon reconnecting
- This is more reliable than direct sensor tasking for critical operations
- Task commands use standard LC sensor command syntax
- Selector syntax: `tag=value`, `platform=value`, `hostname=pattern`, combined with `and`/`or`

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/` (GenericPOSTRequest with reliable_tasking endpoint)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/response/tasking.go` (reliable_tasking)
