
# Get Processes

Retrieve the real-time process list from a specific sensor, showing all running processes with detailed information.

## When to Use

Use this skill when the user needs to:
- Get a live snapshot of running processes on a system
- Investigate suspicious process activity
- Hunt for malware or malicious processes
- Understand process relationships (parent-child)
- Analyze system state during incident response
- Identify processes for further investigation

Common scenarios:
- "Show me what processes are running on this sensor"
- "I need to see all running processes on the compromised system"
- "Is there a suspicious process named X running?"
- "What's the parent process of PID 1234?"

## What This Skill Does

This skill sends a live command to the specified sensor to retrieve its current process list. The sensor responds with detailed information about all running processes including process IDs, file paths, command line arguments, parent process relationships, and other relevant metadata. This is a real-time operation that queries the sensor's current state.

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
3. Sensor is online and responsive (check sensor status first)
4. User has permissions for live sensor tasking

### Step 2: Send the Sensor Command

Use the dedicated MCP tool:

```
mcp__limacharlie__get_processes(
  oid="[organization-id]",
  sid="[sensor-id]"
)
```

**Technical Details:**
- This executes the `os_processes` sensor command
- Timeout: 30 seconds
- Requires sensor to be online
- Uses interactive tasking mode
- Response is synchronous

### Step 3: Handle the Response

The response contains detailed process information:
```json
{
  "processes": [
    {
      "pid": 1234,
      "ppid": 1000,
      "name": "chrome.exe",
      "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
      "cmdline": "chrome.exe --type=renderer",
      "user": "SYSTEM",
      "threads": 15,
      "memory": 204800000,
      "cpu_time": 12345
    },
    ...
  ]
}
```

**Success:**
- Returns array of process objects
- Each process includes:
  - `pid`: Process ID
  - `ppid`: Parent process ID
  - `name`: Process name/executable
  - `path`: Full file path to executable
  - `cmdline`: Command line with arguments
  - `user`: User account running the process
  - `threads`: Number of threads
  - `memory`: Memory usage in bytes
  - Platform-specific fields may vary

**Common Errors:**
- **Sensor offline**: Sensor not currently connected - wait for sensor to come online
- **Timeout**: Sensor didn't respond within 30 seconds - check sensor connectivity
- **Permission denied**: Insufficient rights to task sensor - verify API permissions
- **Command failed**: Sensor reported error executing command

### Step 4: Format the Response

Present the result to the user:
- Create a table or list of processes sorted by criteria (PID, name, memory, etc.)
- Highlight suspicious processes if investigation-focused
- Show parent-child relationships when relevant
- Include key details: PID, name, path, command line, user
- Filter or search based on user's query
- Note any unusual patterns (high memory, suspicious names, unusual paths)

## Example Usage

### Example 1: Getting all processes

User request: "Show me all running processes on sensor abc-123"

Steps:
1. Verify sensor is online
2. Call the tool:
```
mcp__limacharlie__get_processes(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  sid="abc-123-def-456-ghi-789"
)
```

Present formatted list of processes with key information.

### Example 2: Hunting for suspicious processes

User request: "Is there any process with 'powershell' in the name on this system?"

Steps:
1. Get all processes from sensor
2. Filter results for processes containing 'powershell'
3. Present matching processes with full details
4. Highlight unusual PowerShell usage (encoded commands, unusual parent processes)

## Additional Notes

- This is a live operation requiring active sensor connection
- Process list is point-in-time snapshot - processes may start/stop quickly
- Some system processes may not be visible depending on sensor privileges
- Windows sensors show more detailed process information than Linux/macOS
- Use process PID for further investigation (get-process-modules, get-process-strings)
- Parent process ID (ppid) helps understand process relationships
- Command line arguments often reveal malicious intent
- Cross-reference process hashes with threat intelligence
- Elevated/system processes may indicate persistence mechanisms
- Look for processes running from unusual locations (temp directories, appdata)
- Consider process creation time if available for timeline analysis

## Reference

For the MCP tool, this uses the dedicated `get_processes` tool rather than generic API calling.

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/investigation/investigation.go`
