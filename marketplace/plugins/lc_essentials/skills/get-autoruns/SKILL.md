---
name: get-autoruns
description: Get autorun entries (startup items, scheduled tasks, registry run keys) from a live sensor showing persistence mechanisms. Use for persistence detection, malware startup identification, autoruns auditing, and identifying how malware maintains presence during security investigations.
allowed-tools: mcp__limacharlie__get_autoruns, Read
---

# Get Autoruns

Retrieve autorun entries (startup items) from a specific sensor, showing all persistence mechanisms.

## When to Use

Use this skill when the user needs to:
- List all startup/autorun entries
- Detect malware persistence mechanisms
- Identify suspicious startup items
- Audit system autorun configuration
- Investigate how malware maintains presence
- Check registry run keys and startup folders

Common scenarios:
- "Show me all startup items on this sensor"
- "List autorun entries on this Windows system"
- "What programs start automatically?"
- "Check for malicious persistence on sensor abc-123"

## What This Skill Does

This skill sends a live command to retrieve all autorun entries, including registry run keys, startup folders, scheduled tasks, services, and other persistence locations.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **sid**: Sensor ID (UUID)

The sensor must be online.

### Step 2: Send the Sensor Command

```
mcp__limacharlie__get_autoruns(
  oid="[organization-id]",
  sid="[sensor-id]"
)
```

**Technical Details:**
- Executes the `os_autoruns` sensor command
- Timeout: Up to 10 minutes
- Returns all autorun/startup entries

### Step 3: Handle the Response

Response contains autorun entry information. Highlight suspicious entries, unsigned executables in autorun locations, or entries pointing to unusual file paths.

## Reference

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
