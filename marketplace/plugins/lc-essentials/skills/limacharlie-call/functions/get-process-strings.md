
# Get Process Strings

Extract all readable ASCII and Unicode strings from a process's memory space.

## When to Use

Use this skill when the user needs to:
- Extract strings from malware running in memory
- Hunt for credentials or sensitive data in process memory
- Identify C2 server addresses or malicious URLs
- Discover malware configuration details
- Extract IOCs from suspicious processes
- Perform memory forensics on running processes

Common scenarios:
- "Extract strings from this suspicious process"
- "Show me memory strings from PID 1234"
- "Are there any URLs in this malware's memory?"
- "Extract configuration from this process memory"

## What This Skill Does

This skill sends a live command to the specified sensor to extract all readable strings from a process's memory. It scans the process memory space and returns ASCII and Unicode strings, which can reveal URLs, IP addresses, file paths, credentials, encryption keys, and other valuable forensic artifacts.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all operations)
- **sid**: Sensor ID (UUID) of the target sensor
- **pid**: Process ID of the target process

The sensor must be online and the process must be running. Note: This operation can take significant time for large processes.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Valid process ID (pid) that exists on the sensor
4. Sensor is online and responsive
5. Process is currently running
6. Be aware this may return large amounts of data

### Step 2: Send the Sensor Command

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="get_process_strings",
  parameters={
    "oid": "[organization-id]",
    "sid": "[sensor-id]",
    "pid": [process-id]
  }
)
```

**Technical Details:**
- This executes the `mem_strings` sensor command
- Timeout: Up to 10 minutes for large processes
- Requires sensor to be online and process to exist
- Extracts both ASCII and Unicode strings
- May return thousands of strings
- Uses interactive tasking mode

### Step 3: Handle the Response

The response contains extracted strings:
```json
{
  "strings": [
    "http://malicious-c2.com/callback",
    "C:\\Windows\\System32\\cmd.exe",
    "GET /api/beac on HTTP/1.1",
    "password123",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    ...
  ]
}
```

**Success:**
- Returns array of string values found in memory
- Includes both ASCII and Unicode strings
- Minimum string length typically 4-6 characters
- May include:
  - URLs and IP addresses
  - File paths and registry keys
  - User-agent strings
  - Error messages
  - Configuration parameters
  - Credentials and keys
  - Function names and debug strings
- Large result set (potentially thousands of strings)

**Common Errors:**
- **Sensor offline**: Sensor not currently connected
- **Process not found**: PID doesn't exist on sensor
- **Timeout**: Process memory too large, operation exceeded timeout
- **Access denied**: Process protected or insufficient privileges
- **Permission denied**: Insufficient rights to task sensor

### Step 4: Format the Response

Present the result to the user:
- Filter and highlight interesting strings (URLs, IPs, file paths)
- Group by category if possible (network, filesystem, crypto)
- Search for specific patterns user is interested in
- Present summary of findings before full list
- Note that output can be very large - consider pagination
- Flag suspicious indicators (malicious URLs, encoded content)
- Remove noise if possible (random binary data, meaningless strings)

## Example Usage

### Example 1: Extracting C2 URLs from malware

User request: "Extract network indicators from process 1234"

Steps:
1. Get process strings
2. Filter for URLs, IP addresses, domain names
3. Present network-related strings:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_process_strings",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc-123-def-456-ghi-789",
    "pid": 1234
  }
)
```

Found URLs:
- http://malicious-c2.com/callback
- https://attacker.net/config.php

### Example 2: Searching for credentials

User request: "Are there any passwords in memory of PID 5678?"

Steps:
1. Extract all strings from process
2. Search for patterns: "password", "passwd", "pwd", "credential"
3. Report findings with context
4. Warn user about sensitive data handling

## Additional Notes

- This operation can be time-consuming for large processes
- Output can be extremely large (MB of text)
- Many strings will be benign (function names, debug strings, UI text)
- Unicode strings include wide-character encodings
- Useful for fileless malware that exists only in memory
- Can reveal hardcoded credentials, keys, or configurations
- Look for:
  - URLs and IP addresses (C2 servers)
  - File paths (persistence locations)
  - Registry keys (persistence mechanisms)
  - User-agent strings (network behavior)
  - Error messages (malware debugging)
  - Encoded or encrypted data (obfuscation)
- Consider privacy and legal implications of memory extraction
- Some strings may be partial or corrupted
- Reflective loading may leave artifacts in memory strings
- Compare with known IOCs from threat intelligence
- Use `find_strings` for targeted string search instead of full extraction

## Reference

For the MCP tool, this uses the dedicated `get_process_strings` tool via `lc_call_tool`.

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
