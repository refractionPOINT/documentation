---
name: get-os-version
description: Get operating system version information from a live sensor including OS name, version number, build, architecture, and patch level. Use for inventory, vulnerability assessment, patch compliance checking, platform verification, compatibility analysis, and understanding system configuration during investigations.
allowed-tools: mcp__limacharlie__get_os_version, Read
---

# Get OS Version

Retrieve detailed operating system version information from a specific sensor.

## When to Use

Use this skill when the user needs to:
- Get OS version details for a specific sensor
- Check patch level and build numbers
- Verify OS configuration during investigation
- Assess vulnerability based on OS version
- Inventory system configurations
- Validate compatibility for response actions

Common scenarios:
- "What OS version is running on this sensor?"
- "Is this Windows system fully patched?"
- "What build of Ubuntu is this sensor running?"
- "Check the OS version for sensor abc-123"

## What This Skill Does

This skill sends a live command to the specified sensor to retrieve its operating system version information. The sensor responds with detailed OS metadata including version numbers, build identifiers, service pack levels, architecture, and other OS-specific details.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all operations)
- **sid**: Sensor ID (UUID) of the target sensor

The sensor must be online and responsive for this operation to succeed.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Sensor is online and responsive
4. User has permissions for live sensor tasking

### Step 2: Send the Sensor Command

Use the dedicated MCP tool:

```
mcp__limacharlie__get_os_version(
  oid="[organization-id]",
  sid="[sensor-id]"
)
```

**Technical Details:**
- This executes the `os_version` sensor command
- Timeout: 30 seconds
- Requires sensor to be online
- Uses interactive tasking mode
- Response is synchronous

### Step 3: Handle the Response

The response contains OS version information:
```json
{
  "os_name": "Windows",
  "os_version": "10.0.19045",
  "os_build": "19045",
  "os_edition": "Professional",
  "architecture": "x64",
  "service_pack": "",
  "kernel_version": "10.0.19045.3570"
}
```

**Success:**
- Returns OS version details object
- Windows includes:
  - OS name, version, build number
  - Edition (Home, Pro, Enterprise, Server)
  - Architecture (x64, x86, ARM64)
  - Service pack information
  - Kernel version
- Linux includes:
  - Distribution name
  - Kernel version
  - Distribution version
  - Architecture
- macOS includes:
  - macOS version name
  - Build number
  - Kernel version

**Common Errors:**
- **Sensor offline**: Sensor not currently connected
- **Timeout**: Sensor didn't respond within 30 seconds
- **Permission denied**: Insufficient rights to task sensor
- **Command failed**: Sensor reported error

### Step 4: Format the Response

Present the result to the user:
- Show OS name and version clearly
- Include relevant patch/build information
- Note architecture details
- Flag if OS version is outdated or vulnerable
- Compare against known vulnerable versions if investigating
- Format based on platform (Windows vs Linux vs macOS)

## Example Usage

### Example 1: Checking Windows version

User request: "What version of Windows is sensor abc-123 running?"

Steps:
1. Verify sensor is online
2. Call the tool:
```
mcp__limacharlie__get_os_version(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  sid="abc-123-def-456-ghi-789"
)
```

Expected result: "This sensor is running Windows 10 Professional (build 19045), 64-bit architecture."

### Example 2: Verifying patch level for vulnerability

User request: "Is this server running a vulnerable version of Linux?"

Steps:
1. Get OS version from sensor
2. Check kernel version against known vulnerabilities
3. Report findings: "Server is running Ubuntu 20.04.5 LTS with kernel 5.4.0-124. This version is patched against [specific CVE]."

## Additional Notes

- OS version is static information - doesn't change frequently
- Build numbers indicate patch level on Windows
- Kernel version is key for Linux vulnerability assessment
- Service pack information relevant for older Windows systems
- Architecture (x64 vs x86) affects tool and payload compatibility
- macOS versions have both numeric and name identifiers
- Compare against vulnerability databases for security assessment
- Older OS versions may indicate end-of-life systems
- Use this information to plan remediation or response actions
- Some sensor commands/features may be OS-version specific

## Reference

For the MCP tool, this uses the dedicated `get_os_version` tool.

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/investigation/investigation.go`
