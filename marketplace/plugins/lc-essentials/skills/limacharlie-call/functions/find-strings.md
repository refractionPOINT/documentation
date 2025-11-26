
# Find Strings

Search for specific strings across all process memory on a sensor, identifying which processes contain the target strings.

## When to Use

Use this skill when the user needs to:
- Find which processes contain specific strings
- Hunt for credentials across all process memory
- Locate processes with specific URLs or IPs
- Search for malware indicators in memory
- Identify processes with specific configuration strings
- Efficiently search memory without extracting all strings

Common scenarios:
- "Find which processes have the string 'password123' in memory"
- "Search for 'malicious-c2.com' across all running processes"
- "Which process contains the API key?"
- "Find processes with encryption keys in memory"

## What This Skill Does

This skill sends a targeted search command to the sensor that scans all process memory spaces for specific strings. Instead of extracting all strings from each process (which is slow), it searches for exact matches, making it much more efficient for targeted hunting.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **sid**: Sensor ID (UUID)
- **strings**: Comma-separated list of strings to search for

The sensor must be online. This searches all accessible process memory.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. String(s) to search for
4. Sensor is online and responsive

**String Format:**
- Comma-separated for multiple strings: "password,credential,secret"
- Single string: "malicious-domain.com"
- Case-sensitive search
- Exact substring matching

### Step 2: Send the Sensor Command

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="find_strings",
  parameters={
    "oid": "[organization-id]",
    "sid": "[sensor-id]",
    "strings": "[string1,string2,string3]"
  }
)
```

**Technical Details:**
- Executes the `mem_find_string` sensor command
- Timeout: Up to 10 minutes
- Searches all accessible process memory
- More efficient than extracting all strings
- Uses interactive tasking mode

### Step 3: Handle the Response

The response contains matching processes:
```json
{
  "matches": [
    {
      "pid": 1234,
      "process_name": "malware.exe",
      "found_strings": [
        "password123",
        "api-key-secret"
      ],
      "count": 2
    },
    {
      "pid": 5678,
      "process_name": "chrome.exe",
      "found_strings": [
        "password123"
      ],
      "count": 1
    }
  ],
  "searched_processes": 45,
  "matching_processes": 2
}
```

**Success:**
- Returns array of processes containing the target strings
- Each match includes:
  - `pid`: Process ID
  - `process_name`: Name of the process
  - `found_strings`: Which strings were found
  - `count`: Number of occurrences
- Empty array if no processes contain the strings

**Common Errors:**
- **Sensor offline**: Sensor not connected
- **Timeout**: Too many processes or memory to search
- **Access denied**: Some processes protected
- **Permission denied**: Insufficient rights to task sensor

### Step 4: Format the Response

Present the result to the user:
- Summary: Found in X of Y processes
- List each matching process with PID and process name
- Show which strings were found in each process
- Highlight suspicious findings (credentials in unexpected processes)
- Recommend next steps (extract full strings, investigate process)
- If no matches: confirm strings not found in any process memory

## Example Usage

### Example 1: Hunting for credentials

User request: "Find which processes have 'password' or 'credential' in memory"

Steps:
1. Prepare search string list
2. Call the tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="find_strings",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc-123-def-456-ghi-789",
    "strings": "password,credential,secret"
  }
)
```

Report: "Found credentials in 3 processes: chrome.exe (PID 1234), malware.exe (PID 5678), and lsass.exe (PID 910)."

### Example 2: Searching for C2 domain

User request: "Which process is connecting to evil-c2.com?"

Steps:
1. Search for the C2 domain string
2. Identify matching processes
3. Report findings for further investigation

## Additional Notes

- Much more efficient than get-process-strings for targeted searches
- Searches all accessible process memory
- Some protected processes may not be searchable
- Case-sensitive string matching
- Searches for substrings (partial matches work)
- Good for hunting specific IOCs across all processes
- Use comma-separated list for multiple search terms
- Can search for URLs, IPs, file paths, credentials, etc.
- Results indicate which processes to investigate further
- Combine with get-process-strings for full context
- Protected/system processes may be skipped
- Search is point-in-time - process memory changes
- Useful for incident response and threat hunting
- Can reveal which process loaded malicious content
- Memory-only malware artifacts can be found
- Consider privacy implications when searching for credentials

## Reference

For the MCP tool, this uses the dedicated `find_strings` tool via `lc_call_tool`.

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
