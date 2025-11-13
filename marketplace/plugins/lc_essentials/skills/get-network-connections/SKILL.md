---
name: get-network-connections
description: Get real-time network connections from a live sensor showing active TCP/UDP connections, listening ports, remote IPs, and associated processes. Use for network investigation, lateral movement detection, C2 communication analysis, port scanning, suspicious connection identification, and understanding network activity during security incidents.
allowed-tools: mcp__limacharlie__get_network_connections, Read
---

# Get Network Connections

Retrieve the real-time network connection list from a specific sensor, showing all active and listening network connections.

## When to Use

Use this skill when the user needs to:
- Get live network connections from a sensor
- Investigate suspicious network activity
- Identify command and control (C2) communications
- Detect lateral movement attempts
- Analyze listening ports and services
- Correlate network connections with processes

Common scenarios:
- "Show me all network connections on this sensor"
- "Is this sensor connecting to any suspicious IPs?"
- "What ports is this system listening on?"
- "Which process is communicating with IP X.X.X.X?"

## What This Skill Does

This skill sends a live command to the specified sensor to retrieve its current network connection state. The sensor responds with information about all active TCP/UDP connections, listening ports, remote endpoints, local endpoints, and the processes responsible for each connection.

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
mcp__limacharlie__get_network_connections(
  oid="[organization-id]",
  sid="[sensor-id]"
)
```

**Technical Details:**
- This executes the `netstat` sensor command
- Timeout: 30 seconds
- Requires sensor to be online
- Uses interactive tasking mode
- Response is synchronous

### Step 3: Handle the Response

The response contains network connection information:
```json
{
  "connections": [
    {
      "state": "ESTABLISHED",
      "local_address": "192.168.1.100",
      "local_port": 54321,
      "remote_address": "203.0.113.50",
      "remote_port": 443,
      "pid": 1234,
      "process_name": "chrome.exe",
      "protocol": "TCP"
    },
    {
      "state": "LISTENING",
      "local_address": "0.0.0.0",
      "local_port": 445,
      "pid": 4,
      "process_name": "System",
      "protocol": "TCP"
    },
    ...
  ]
}
```

**Success:**
- Returns array of connection objects
- Each connection includes:
  - `state`: Connection state (ESTABLISHED, LISTENING, TIME_WAIT, etc.)
  - `local_address`: Local IP address
  - `local_port`: Local port number
  - `remote_address`: Remote IP address (if established)
  - `remote_port`: Remote port number (if established)
  - `pid`: Process ID responsible for connection
  - `process_name`: Name of the process
  - `protocol`: TCP or UDP

**Common Errors:**
- **Sensor offline**: Sensor not currently connected
- **Timeout**: Sensor didn't respond within 30 seconds
- **Permission denied**: Insufficient rights to task sensor
- **Command failed**: Sensor reported error

### Step 4: Format the Response

Present the result to the user:
- Group connections by state (ESTABLISHED, LISTENING, etc.)
- Highlight suspicious IPs, ports, or connections
- Show process information with each connection
- Filter based on user's specific query
- Flag unusual ports, foreign IPs, or suspicious processes
- Correlate with threat intelligence if available

## Example Usage

### Example 1: Listing all network connections

User request: "Show me all network connections on sensor abc-123"

Steps:
1. Verify sensor is online
2. Call the tool:
```
mcp__limacharlie__get_network_connections(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  sid="abc-123-def-456-ghi-789"
)
```

Present formatted list grouped by state and highlighting key information.

### Example 2: Investigating suspicious C2 communication

User request: "Is this sensor connecting to IP 198.51.100.42?"

Steps:
1. Get all network connections
2. Filter for remote_address matching 198.51.100.42
3. If found, show full connection details including process
4. Note whether connection is active, port used, and process responsible

## Additional Notes

- This is a point-in-time snapshot of network state
- Short-lived connections may not appear
- Some processes may show multiple connections
- Listening on 0.0.0.0 means all interfaces
- Unusual high ports may indicate malware communication
- Check for connections to known malicious IPs
- Correlate PIDs with process list for full context
- ESTABLISHED connections to foreign IPs warrant investigation
- Listening services on unusual ports may be backdoors
- TIME_WAIT connections are recently closed
- Use remote IP/port to identify service type (443=HTTPS, 80=HTTP, etc.)
- Compare with baseline to identify anomalies

## Reference

For the MCP tool, this uses the dedicated `get_network_connections` tool.

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/investigation/investigation.go`
