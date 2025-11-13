---
name: get-users
description: Get list of system user accounts from a live sensor including usernames, UIDs, group memberships, and account status. Use for user enumeration, privilege escalation detection, unauthorized account identification, security auditing, and understanding user context during investigations.
allowed-tools: mcp__limacharlie__get_users, Read
---

# Get Users

Retrieve the list of user accounts configured on a specific sensor.

## When to Use

Use this skill when the user needs to:
- List all user accounts on a system
- Identify unauthorized or suspicious accounts
- Audit user account configuration
- Investigate privilege escalation
- Understand user context for investigations
- Check for backdoor accounts

Common scenarios:
- "Show me all user accounts on this sensor"
- "List users on this Windows system"
- "Are there any suspicious admin accounts?"
- "What users exist on sensor abc-123?"

## What This Skill Does

This skill sends a live command to retrieve all user accounts configured on the sensor, including local accounts and domain users (on Windows). Returns usernames, user IDs, group memberships, and account metadata.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all operations)
- **sid**: Sensor ID (UUID) of the target sensor

The sensor must be online and responsive.

## How to Use

### Step 1: Validate Parameters

Ensure you have valid oid and sid, and sensor is online.

### Step 2: Send the Sensor Command

```
mcp__limacharlie__get_users(
  oid="[organization-id]",
  sid="[sensor-id]"
)
```

**Technical Details:**
- Executes the `os_users` sensor command
- Timeout: Up to 10 minutes
- Returns all configured user accounts

### Step 3: Handle the Response

Response contains user account information. Present findings highlighting suspicious accounts, admin/root users, and recent additions.

## Reference

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
