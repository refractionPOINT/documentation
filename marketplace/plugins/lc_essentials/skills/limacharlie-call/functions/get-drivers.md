
# Get Drivers

Retrieve the list of installed drivers (kernel modules) from a specific sensor.

## When to Use

Use this skill when the user needs to:
- List all kernel drivers/modules on a system
- Detect rootkits or malicious drivers
- Identify unsigned or suspicious kernel modules
- Audit driver installation and signatures
- Investigate kernel-level persistence
- Check for vulnerable drivers

Common scenarios:
- "Show me all drivers installed on this sensor"
- "List kernel modules on this system"
- "Are there any unsigned drivers?"
- "Check for rootkit drivers on sensor abc-123"

## What This Skill Does

This skill sends a live command to retrieve all installed drivers/kernel modules, including driver metadata, file paths, digital signatures, and version information.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **sid**: Sensor ID (UUID)

The sensor must be online.

### Step 2: Send the Sensor Command

```
mcp__limacharlie__get_drivers(
  oid="[organization-id]",
  sid="[sensor-id]"
)
```

**Technical Details:**
- Executes the `os_drivers` sensor command
- Timeout: Up to 10 minutes
- Returns all installed drivers/kernel modules

### Step 3: Handle the Response

Response contains driver information. Highlight unsigned drivers, unusual driver paths, or drivers loaded from non-system locations.

## Reference

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
