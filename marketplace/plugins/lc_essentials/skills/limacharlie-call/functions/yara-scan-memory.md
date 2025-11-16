
# YARA Scan Memory

Scan process memory using YARA rules with process expression matching to target multiple processes simultaneously.

## When to Use

Use this skill when the user needs to:
- Scan multiple processes matching a pattern
- Hunt for threats across process families (all chrome.exe, all powershell.exe)
- Detect fileless malware in memory at scale
- Perform bulk memory scanning with process filters
- Target specific process names or patterns
- Efficient scanning of related processes

Common scenarios:
- "Scan all PowerShell processes for malicious code"
- "Check memory of all chrome.exe processes for threats"
- "Hunt for malware in all svchost.exe instances"
- "Scan processes matching name pattern with YARA"

## What This Skill Does

This skill sends a YARA rule to the sensor along with a process expression that matches multiple processes. The sensor identifies all processes matching the expression, applies the YARA rule to each matching process's memory, and returns any matches found. This is more efficient than scanning processes individually.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all operations)
- **sid**: Sensor ID (UUID) of the target sensor
- **process_expression**: Process matching expression (e.g., 'name:chrome.exe', 'name:*powershell*')
- **rule**: YARA rule content (full rule text) or rule name

The sensor must be online and matching processes must exist.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Valid process expression (see format below)
4. Valid YARA rule (syntax-checked)
5. Sensor is online and responsive
6. Matching processes exist on sensor

**Process Expression Format:**
- `name:process_name` - Match by exact process name
- `name:*pattern*` - Match by wildcard pattern
- Examples:
  - `name:chrome.exe` - All Chrome processes
  - `name:powershell.exe` - All PowerShell processes
  - `name:*svchost*` - All svchost variants

### Step 2: Send the Sensor Command

Use the dedicated MCP tool:

```
mcp__limacharlie__yara_scan_memory(
  oid="[organization-id]",
  sid="[sensor-id]",
  process_expression="[process-expression]",
  rule="[yara-rule-content-or-name]"
)
```

**Technical Details:**
- This executes the `yara_scan` sensor command with processExpr parameter
- Timeout: Up to 10 minutes for scanning multiple large processes
- Scans all processes matching the expression
- Can scan dozens of processes in one operation
- Uses interactive tasking mode

### Step 3: Handle the Response

The response contains YARA match results across all scanned processes:
```json
{
  "matches": [
    {
      "pid": 1234,
      "process_name": "powershell.exe",
      "rule_name": "Fileless_Malware",
      "strings": [
        {
          "identifier": "$shellcode",
          "offset": "0x1000",
          "data": "4D5A..."
        }
      ]
    },
    {
      "pid": 5678,
      "process_name": "powershell.exe",
      "rule_name": "Fileless_Malware",
      "strings": [
        {
          "identifier": "$encoded_cmd",
          "offset": "0x2000"
        }
      ]
    }
  ],
  "scanned_processes": 3,
  "matched_processes": 2
}
```

**Success:**
- Returns array of matches from all scanned processes
- Each match includes:
  - `pid`: Process ID that matched
  - `process_name`: Name of the matching process
  - `rule_name`: YARA rule that matched
  - `strings`: String matches with memory offsets
- Summary statistics (processes scanned, matches found)
- Empty matches if no threats detected

**Common Errors:**
- **Sensor offline**: Sensor not currently connected
- **No matching processes**: Process expression didn't match any processes
- **Invalid YARA rule**: Syntax error in rule
- **Timeout**: Too many processes or processes too large
- **Access denied**: Processes protected or insufficient privileges
- **Permission denied**: Insufficient rights to task sensor

### Step 4: Format the Response

Present the result to the user:
- Summary: Scanned X processes, found matches in Y processes
- List each matching process with PID and detection
- Group by rule name if multiple rules matched
- Highlight severity and process context
- Provide PIDs for further investigation or response
- If no matches: confirm processes appear clean
- Recommend next steps based on findings

## Example Usage

### Example 1: Scanning all PowerShell processes

User request: "Check all PowerShell processes for malicious activity"

Steps:
1. Create or use PowerShell-specific YARA rule
2. Call the tool:
```
mcp__limacharlie__yara_scan_memory(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  sid="abc-123-def-456-ghi-789",
  process_expression="name:powershell.exe",
  rule="rule PS_Malware { strings: $encoded = \"encodedCommand\" condition: $encoded }"
)
```

Report: "Scanned 3 PowerShell processes. Found malicious activity in PID 1234 and PID 5678."

### Example 2: Hunting across process families

User request: "Hunt for Cobalt Strike across all svchost processes"

Steps:
1. Use Cobalt Strike YARA signatures
2. Target all svchost instances:
```
mcp__limacharlie__yara_scan_memory(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  sid="abc-123-def-456-ghi-789",
  process_expression="name:svchost.exe",
  rule="cobalt_strike_beacon_rules"
)
```

## Additional Notes

- More efficient than scanning processes individually
- Process expression must match at least one process
- Wildcards allow flexible matching patterns
- Large numbers of matching processes increase scan time
- Protected system processes may be inaccessible
- Some processes may terminate during scan
- Useful for hunting specific threat patterns at scale
- Can target process families known for abuse (powershell, wscript, etc.)
- Combines well with process listing to identify targets first
- Consider impact on system performance with many/large processes
- Memory scanning is resource-intensive
- Results aggregate across all matching processes
- Each process scanned independently
- Failed processes don't stop overall scan
- Useful for detecting process injection across multiple instances
- Good for hunting DLL injection or shellcode in specific process types

## Reference

For the MCP tool, this uses the dedicated `yara_scan_memory` tool.

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/yara.go`
