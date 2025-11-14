
# Get Sensor Info

Retrieve comprehensive information about a specific sensor in your LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- Get detailed information about a specific sensor
- Check if a sensor is online and healthy
- View sensor metadata (hostname, platform, architecture, IPs)
- Check sensor tags and isolation status
- Investigate sensor configuration during incident response
- Verify sensor enrollment and installation details

Common scenarios:
- "Show me details about sensor xyz-123"
- "What's the hostname of sensor abc-456?"
- "Is sensor def-789 isolated from the network?"
- "Get information about the Windows sensor on host SERVER01"

## What This Skill Does

This skill retrieves detailed information about a specific sensor by calling the LimaCharlie API. It returns comprehensive sensor metadata including platform details, network information, tags, and operational status.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **sid**: Sensor ID (UUID format, e.g., "c7e8f940-1234-5678-abcd-1234567890ab")

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Sensor exists in the organization

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/sensors/c7e8f940-1234-5678-abcd-1234567890ab/xyz-sensor-id"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/sensors/{oid}/{sid}` (replace both placeholders with actual IDs)
- No query parameters needed
- No request body needed

**Note:** The SDK method `org.GetSensor(sid)` followed by `sensor.Update()` is used internally, which makes a GET request to `/sensors/{oid}/{sid}` and also fetches tags via GET `/sensors/{oid}/{sid}/tags`.

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "info": {
      "sid": "xyz-sensor-id",
      "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
      "hostname": "SERVER01",
      "platform": 268435456,
      "arch": 1,
      "enroll": "2024-01-15T10:30:00Z",
      "alive": "2024-01-20T14:22:13Z",
      "int_ip": "10.0.1.50",
      "ext_ip": "203.0.113.45",
      "iid": "install-key-123",
      "isolated": false,
      "should_isolate": false,
      "kernel": true
    },
    "is_online": true
  }
}
```

**Success (200):**
- The response contains detailed sensor information
- `info` object has all sensor metadata
- `is_online` indicates current connection status
- Tags are fetched separately and included in formatted response
- Platform codes: Windows=268435456, Linux=67108864, macOS=33554432
- Architecture codes: x64=1, x86=2, ARM=3

**Common Errors:**
- **400 Bad Request**: Invalid sensor ID format (must be valid UUID)
- **404 Not Found**: Sensor with the specified ID does not exist in the organization
- **403 Forbidden**: Insufficient permissions to view sensor details
- **500 Server Error**: Rare, retry or check LimaCharlie service status

### Step 4: Format the Response

Present the result to the user:
- Display sensor ID, hostname, and platform in a clear format
- Show network information (internal and external IPs)
- Highlight online status and last seen timestamp
- List all tags applied to the sensor
- Indicate isolation status if applicable
- Show enrollment time and installation key for reference

**Example formatted output:**
```
Sensor Information:
- Sensor ID: xyz-sensor-id
- Hostname: SERVER01
- Platform: Windows x64
- Status: Online (last seen 2024-01-20 14:22:13)
- Internal IP: 10.0.1.50
- External IP: 203.0.113.45
- Tags: production, windows-servers, critical
- Isolated: No
- Enrolled: 2024-01-15 10:30:00
```

## Example Usage

### Example 1: Get info for a known sensor

User request: "Show me details about sensor xyz-123"

Steps:
1. Validate sensor ID format
2. Get organization ID from context
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/sensors/c7e8f940-1234-5678-abcd-1234567890ab/xyz-123"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "info": {
      "sid": "xyz-123",
      "hostname": "WORKSTATION-05",
      "platform": 268435456,
      "arch": 1,
      "int_ip": "192.168.1.105",
      "alive": "2024-01-20T15:00:00Z",
      "isolated": false
    },
    "is_online": true
  }
}
```

### Example 2: Check if sensor is isolated

User request: "Is sensor abc-456 isolated from the network?"

Steps:
1. Get sensor info using the API call
2. Check the `isolated` field in the response
3. Report isolation status:
```
Sensor abc-456 (hostname: DB-SERVER-01) is currently NOT isolated.
Network isolation status: Normal
```

## Additional Notes

- Platform codes are numeric constants: Windows=268435456 (0x10000000), Linux=67108864 (0x04000000), macOS=33554432 (0x02000000)
- The `alive` timestamp indicates the last time the sensor checked in
- A sensor is considered online if it has checked in recently (typically within the last few minutes)
- The `iid` field contains the installation key ID used to enroll the sensor
- Tags can be used to organize and filter sensors (e.g., by environment, role, or criticality)
- The `kernel` field indicates if kernel-level monitoring is available on the sensor
- Use `is-online` skill if you only need to check online status without full details
- Use `list-sensors` skill to get a list of all sensors before getting details

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/core/core.go`
