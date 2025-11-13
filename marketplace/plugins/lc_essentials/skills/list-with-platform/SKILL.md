---
name: list-with-platform
description: List all sensors in the organization that match a specific platform (Windows, Linux, macOS, Chrome, etc.). Returns detailed sensor information filtered by operating system. Use when users need to find platform-specific sensors, target investigations by OS, count sensors per platform, build platform-targeted responses, or inventory infrastructure by operating system.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# List Sensors With Platform

List all sensors in the organization filtered by a specific platform, returning detailed sensor information for matching systems.

## When to Use

Use this skill when the user needs to:
- Find all sensors running on a specific platform
- Target investigations to Windows, Linux, or macOS systems
- Count sensors by operating system
- Build platform-specific response actions
- Inventory infrastructure by platform

Common scenarios:
- "Show me all Windows sensors"
- "How many Linux systems do we have?"
- "List all macOS endpoints"
- "I need to investigate only Windows machines"

## What This Skill Does

This skill queries the organization's sensor list using a platform selector, returning all sensors that match the specified platform. It provides detailed information about each sensor including hostname, IP addresses, enrollment status, and isolation state. This is useful for platform-targeted operations and understanding your platform distribution.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **platform**: Platform name (e.g., 'windows', 'linux', 'macos', 'chrome')

Platform names should match LimaCharlie's platform naming. Use `get-platform-names` to get valid platform names if unsure.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid platform name from the ontology
3. Platform name is lowercase and exact

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="GET",
  path="/sensors/[organization-id]",
  query_params={"selector": "plat == `[platform]`"}
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/sensors/{oid}`
- Query parameters: `selector` with platform filter expression
- Selector format: `plat == \`platform-name\`` (note the backticks)
- No request body

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "sensors": {
      "sensor-id-1": {
        "oid": "org-id",
        "iid": "installation-key-id",
        "plat": 1,
        "arch": 2,
        "hostname": "DESKTOP-ABC123",
        "int_ip": "192.168.1.100",
        "ext_ip": "203.0.113.50",
        "enroll": "1234567890",
        "alive": "1234567999",
        "isolated": false
      },
      ...
    }
  }
}
```

**Success (200-299):**
- Body contains `sensors` object with sensor IDs as keys
- Each sensor includes:
  - `oid`: Organization ID
  - `iid`: Installation key ID
  - `plat`: Platform numeric ID
  - `arch`: Architecture numeric ID
  - `hostname`: Computer hostname
  - `int_ip`: Internal IP address
  - `ext_ip`: External IP address
  - `enroll`: Enrollment timestamp
  - `alive`: Last seen timestamp
  - `isolated`: Network isolation status
- Empty object if no sensors match the platform

**Common Errors:**
- **400 Bad Request**: Invalid selector syntax
- **403 Forbidden**: Insufficient permissions to list sensors
- **500 Server Error**: Temporary API issue - retry

### Step 4: Format the Response

Present the result to the user:
- Count of total sensors on the platform
- Summary of sensor information (hostnames, IPs)
- Group by online/offline status if applicable
- Highlight any isolated sensors
- Present in table or list format for readability
- Note enrollment and last seen times for offline sensors

## Example Usage

### Example 1: Listing Windows sensors

User request: "Show me all Windows sensors"

Steps:
1. Extract oid from context
2. Platform is 'windows'
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/sensors/c7e8f940-1234-5678-abcd-1234567890ab",
  query_params={"selector": "plat == `windows`"}
)
```

Expected response contains all Windows sensors with their details.

Present to user: "Found 25 Windows sensors in the organization. Notable systems include: DESKTOP-ABC123 (192.168.1.100), SERVER-XYZ789 (192.168.1.10)..."

### Example 2: Counting Linux systems

User request: "How many Linux systems do we have?"

Steps:
1. List sensors with platform='linux'
2. Count the returned sensors
3. Present count and summary

Result: "You have 18 Linux systems enrolled. They include 12 Ubuntu servers, 4 CentOS systems, and 2 Debian workstations."

## Additional Notes

- The selector uses LimaCharlie's query language with backtick-quoted values
- Platform numeric IDs in response correspond to the ontology mapping
- Not all sensors may be currently online
- Check `alive` timestamp to determine recent activity
- Isolated sensors have `isolated: true` flag
- Use this as a foundation for platform-targeted tasking
- Combine with other sensors tools for detailed investigation
- Architecture field indicates 32-bit vs 64-bit systems
- Empty result means no sensors on that platform in the organization
- Consider using `list-sensors` without filter to see all platforms first

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/schemas.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/schemas/schemas.go`
