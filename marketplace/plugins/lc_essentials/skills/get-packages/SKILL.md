---
name: get-packages
description: Get list of installed software packages from a live sensor including package names, versions, and installation dates. Use for software inventory, vulnerability assessment, unauthorized software detection, patch compliance checking, and understanding installed applications during investigations.
allowed-tools: mcp__limacharlie__get_packages, Read
---

# Get Packages

Retrieve the list of installed software packages from a specific sensor.

## When to Use

Use this skill when the user needs to:
- List all installed software packages
- Perform software inventory
- Identify vulnerable software versions
- Detect unauthorized applications
- Audit installed software
- Check patch levels and versions

Common scenarios:
- "Show me all installed software on this sensor"
- "List packages on this Linux system"
- "What version of Apache is installed?"
- "Check installed software on sensor abc-123"

## What This Skill Does

This skill sends a live command to retrieve all installed software packages. On Linux, this includes RPM/DEB packages. On Windows, this includes installed programs. On macOS, this includes installed applications.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **sid**: Sensor ID (UUID)

The sensor must be online.

### Step 2: Send the Sensor Command

```
mcp__limacharlie__get_packages(
  oid="[organization-id]",
  sid="[sensor-id]"
)
```

**Technical Details:**
- Executes the `os_packages` sensor command
- Timeout: Up to 10 minutes
- Returns all installed packages/applications

### Step 3: Handle the Response

Response contains package information including names, versions, and installation details. Cross-reference with vulnerability databases to identify outdated or vulnerable software.

## Reference

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
