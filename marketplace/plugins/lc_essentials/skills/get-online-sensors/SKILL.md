---
name: get-online-sensors
description: List all currently online and connected LimaCharlie sensors in the organization. Returns only sensor IDs that are actively communicating with the platform. Use for real-time fleet status monitoring, checking sensor availability, identifying offline sensors, verifying sensor connectivity, or preparing for live investigation tasks.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Get Online Sensors

Retrieve a list of all sensors that are currently online and actively connected to the LimaCharlie platform.

## When to Use

Use this skill when the user needs to:
- Check which sensors are currently online
- Get real-time fleet availability status
- Identify which sensors can receive live commands
- Determine sensor connectivity before investigation
- Monitor sensor health and uptime
- Count active vs inactive sensors

Common scenarios:
- "Which sensors are currently online?"
- "Show me all active sensors"
- "How many sensors are connected right now?"
- "Can I run commands on sensor xyz-123?" (check if it's online first)
- "List sensors available for live investigation"

## What This Skill Does

This skill first retrieves all sensors in the organization, then checks their online status by calling the LimaCharlie API. It returns only the sensor IDs that are currently active and connected.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all API calls)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)

### Step 2: Call the API

This operation requires two API calls:

**First, list all sensors:**
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/sensors/c7e8f940-1234-5678-abcd-1234567890ab"
)
```

**Then, check which sensors are active:**
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/sensors/c7e8f940-1234-5678-abcd-1234567890ab/active",
  body={"sids": ["sensor-id-1", "sensor-id-2", "sensor-id-3"]}
)
```

**API Details:**
- Endpoint: `api`
- Method: First GET (list sensors), then POST (check active status)
- Path: `/sensors/{oid}` then `/sensors/{oid}/active`
- Body for active check: `{"sids": [array of sensor IDs]}`

**Note:** The SDK method `org.ActiveSensors(sids)` checks the online status of multiple sensors in a single API call.

### Step 3: Handle the Response

The active sensors API returns:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "sensor-id-1": true,
    "sensor-id-2": false,
    "sensor-id-3": true
  }
}
```

**Success (200):**
- The response maps sensor IDs to boolean values
- `true` means the sensor is currently online and active
- `false` means the sensor is offline or not responding
- Filter to return only sensors with `true` status

**Common Errors:**
- **403 Forbidden**: Insufficient permissions to check sensor status
- **500 Server Error**: Rare, retry or check LimaCharlie service status

### Step 4: Format the Response

Present the result to the user:
- Display count of online sensors vs total sensors
- List online sensor IDs
- Optionally include hostname if sensor list is enriched
- Indicate when the status was checked
- Consider sorting by hostname or sensor ID

**Example formatted output:**
```
Online Sensors: 12 of 15 total

Currently Active:
- xyz-123 (SERVER01)
- abc-456 (WORKSTATION-05)
- def-789 (ubuntu-web-01)
- ghi-012 (macbook-pro-15)
...

Status checked at: 2024-01-20 14:30:00 UTC
```

## Example Usage

### Example 1: Check all online sensors

User request: "Which sensors are currently online?"

Steps:
1. Get organization ID from context
2. List all sensors:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/sensors/c7e8f940-1234-5678-abcd-1234567890ab"
)
```
3. Extract all sensor IDs from response
4. Check active status:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/sensors/c7e8f940-1234-5678-abcd-1234567890ab/active",
  body={"sids": ["sensor-1", "sensor-2", "sensor-3", ...]}
)
```
5. Filter and display only online sensors

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "sensor-1": true,
    "sensor-2": false,
    "sensor-3": true
  }
}
```

### Example 2: Count active vs inactive sensors

User request: "How many sensors are connected right now?"

Steps:
1. Get all sensors and check their online status
2. Count sensors with `true` status
3. Report summary:
```
Fleet Status:
- Online: 12 sensors
- Offline: 3 sensors
- Total: 15 sensors
- Availability: 80%
```

## Additional Notes

- Sensor online status is determined by recent heartbeat/check-in activity
- A sensor is typically considered online if it checked in within the last few minutes
- Online status can change rapidly as sensors connect/disconnect
- This check is real-time and reflects current connectivity
- For individual sensor status, use `is-online` skill
- For full sensor details, use `get-sensor-info` skill
- Large organizations should be aware this makes one API call per batch of sensors
- The SDK batches sensor IDs efficiently for the active status check
- Sensors behind firewalls or with network issues may appear offline even if running
- Consider the sensor's `alive` timestamp from `list-sensors` for historical context

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/core/core.go`
