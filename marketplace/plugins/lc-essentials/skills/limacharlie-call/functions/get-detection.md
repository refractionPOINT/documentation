
# Get Detection

Retrieve detailed information about a **single, specific detection** by its detection ID.

**⚠️ IMPORTANT: This is NOT `get_historic_detections`**
- Use `get_detection` when you have a **specific detection ID** and want its details
- Use `get_historic_detections` when you want to **search by time range** (requires `start` and `end` timestamps)

## When to Use

Use `get_detection` (THIS skill) when:
- You already have a specific detection ID (UUID/atom)
- You want full details about ONE known detection
- You're drilling down from a detection list to view details
- You received a detection ID from an alert or another query

**DO NOT use this skill when:**
- You want detections from a time period → use `get_historic_detections` instead
- You don't have a specific detection ID → use `get_historic_detections` instead
- You want to search/filter detections → use `get_historic_detections` instead

Common scenarios for `get_detection`:
- "Get details about detection f04b4ea9-02c1-484d-bad9-00306928c074"
- "Show me the full event data for detection ID abc-123"
- "What triggered this specific detection: xyz-456?"
- "Investigate detection [specific UUID]"

## What This Skill Does

This skill retrieves the complete detection object for a **single detection ID**, including the original event that triggered the detection, routing information (sensor ID, hostname), and rule metadata (name, author, severity, tags).

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required)
- **detection_id**: The detection ID (detect_id/atom) to retrieve (required)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid detection ID (typically a UUID or atom identifier)
3. Detection ID exists in the organization

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="get_detection",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detection_id": "detect-uuid-123-456"
  }
)
```

**Tool Details:**
- Tool name: `get_detection`
- Parameters:
  - `oid`: Organization ID (required)
  - `detection_id`: Detection ID to retrieve (required)

### Step 3: Handle the Response

The tool returns:
```json
{
  "detection": {
    "detect_id": "detect-uuid-123-456",
    "cat": "suspicious_process",
    "detect": {
      "event": {
        "TIMESTAMP": 1705761234567,
        "COMMAND_LINE": "powershell.exe -encodedCommand ZWNobyAiaGVsbG8i",
        "FILE_PATH": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
        "HASH": "abc123def456...",
        "PARENT": {
          "COMMAND_LINE": "cmd.exe /c ...",
          "FILE_PATH": "C:\\Windows\\System32\\cmd.exe"
        }
      },
      "routing": {
        "sid": "xyz-sensor-123",
        "hostname": "SERVER01",
        "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
      }
    },
    "detect_mtd": {
      "rule_name": "Encoded PowerShell Command",
      "author": "security-team",
      "severity": 8,
      "tags": ["mitre:T1059.001", "powershell", "encoded"]
    }
  }
}
```

**Success:**
- Returns complete detection object with full event context
- Includes original event data that triggered the detection
- Contains routing information (sensor, hostname, organization)
- Provides rule metadata (name, author, severity, tags)

**Common Errors:**
- **400 Bad Request**: Invalid detection ID format
- **403 Forbidden**: Insufficient permissions to view detection
- **404 Not Found**: Detection with specified ID does not exist
- **500 Server Error**: Service issue, retry

### Step 4: Format the Response

Present results to user:
- Show detection ID and category
- Display the triggering event details
- Highlight affected host and sensor
- Show rule name and severity
- Include relevant tags and MITRE mappings

**Example output:**
```
Detection Details: detect-uuid-123-456

Category: suspicious_process
Severity: 8 (High)
Rule: Encoded PowerShell Command
Author: security-team

Affected Host:
- Hostname: SERVER01
- Sensor ID: xyz-sensor-123

Triggering Event:
- Timestamp: 2024-01-20 14:22:14 UTC
- Process: powershell.exe
- Command: powershell.exe -encodedCommand ZWNobyAiaGVsbG8i
- Path: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
- Parent: cmd.exe /c ...

Tags: mitre:T1059.001, powershell, encoded
```

## Example Usage

### Example 1: Get detection details by ID

User: "Get details about detection abc-123-def"

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="get_detection",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detection_id": "abc-123-def"
  }
)
```

### Example 2: Investigate alert from detection list

User: "I see detection xyz-456 in the list, what triggered it?"

Steps:
1. Use `get_detection` with the detection ID
2. Extract the event data from the response
3. Present the command line, process path, and parent process details

### Example 3: Get rule information for a detection

User: "What rule generated detection detect-789?"

Steps:
1. Call `get_detection` with the detection ID
2. Extract `detect_mtd` from response
3. Report rule name, author, severity, and tags

## Additional Notes

**⚠️ Common Confusion: `get_detection` vs `get_historic_detections`**

| Feature | `get_detection` | `get_historic_detections` |
|---------|-----------------|---------------------------|
| Purpose | Get ONE detection by ID | Search detections by time range |
| Required params | `detection_id` | `start`, `end` (timestamps) |
| Returns | Single detection object | Array of detections |
| Use when | You have a specific ID | You want to search/browse |

- Detection IDs are also known as "detect_id" or "atom" identifiers
- Use `get_historic_detections` first to retrieve a list of detection IDs within a time range, then use `get_detection` to get full details for a specific one
- The `detect.event` structure matches the original telemetry event schema
- Rule metadata (`detect_mtd`) includes MITRE ATT&CK mappings if configured
- Severity typically ranges 1-10 (low to critical)
- The `routing` section provides context about where the detection occurred
- Combine with sensor info skills for complete host context

## Reference

See [CALLING_API.md](../../CALLING_API.md) for details on using `lc_call_tool`.

SDK: `../go-limacharlie/limacharlie/organization.go`
MCP: `../lc-mcp-server/internal/tools/historical/historical.go`
