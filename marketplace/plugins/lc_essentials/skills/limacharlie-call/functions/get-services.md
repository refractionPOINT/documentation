
# Get Services

Retrieve the list of services (running and configured) from a specific sensor.

## When to Use

Use this skill when the user needs to:
- List all services on a system
- Identify malicious or suspicious services
- Detect service-based persistence mechanisms
- Audit service configuration
- Investigate unauthorized services
- Check service executable paths

Common scenarios:
- "Show me all running services on this sensor"
- "List services on this Windows system"
- "Are there any suspicious services running?"
- "What services are configured for automatic startup?"

## What This Skill Does

This skill sends a live command to retrieve all services configured on the sensor, including running services, stopped services, and their startup configuration.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **sid**: Sensor ID (UUID)

The sensor must be online.

### Step 2: Send the Sensor Command

```
mcp__limacharlie__get_services(
  oid="[organization-id]",
  sid="[sensor-id]"
)
```

**Technical Details:**
- Executes the `os_services` sensor command
- Timeout: Up to 10 minutes
- Returns all configured services

### Step 3: Handle the Response

Response contains service information. Highlight suspicious services, unusual executable paths, or services running from temp directories.

## Reference

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
