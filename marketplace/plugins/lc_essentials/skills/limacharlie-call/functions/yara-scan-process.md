
# YARA Scan Process

Scan a specific process's memory using YARA rules to detect malware patterns and indicators of compromise.

## When to Use

Use this skill when the user needs to:
- Scan process memory for malware signatures
- Hunt for specific threats using YARA rules
- Detect fileless malware in memory
- Validate suspicious processes against threat intelligence
- Perform targeted IOC matching in process space
- Identify malware families by signature

Common scenarios:
- "Scan process 1234 with this YARA rule"
- "Check if this process matches Cobalt Strike signatures"
- "Run malware detection on the suspicious PowerShell process"
- "Use YARA to identify this malware in memory"

## What This Skill Does

This skill sends a YARA rule to the sensor and scans a specific process's memory for matches. The sensor loads the YARA rule, applies it to the target process's memory space, and returns any matches found. This is essential for real-time malware detection and threat hunting.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all operations)
- **sid**: Sensor ID (UUID) of the target sensor
- **pid**: Process ID of the target process
- **rules**: YARA rule content (full rule text)

The sensor must be online, the process must be running, and the YARA rule must be valid.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Valid process ID (pid) that exists on the sensor
4. Valid YARA rule (syntax-checked)
5. Sensor is online and responsive
6. Process is currently running

### Step 2: Send the Sensor Command

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="yara_scan_process",
  parameters={
    "oid": "[organization-id]",
    "sid": "[sensor-id]",
    "pid": [process-id],
    "rules": "[yara-rule-content]"
  }
)
```

**Technical Details:**
- This executes the `yara_scan` sensor command
- Timeout: Up to 10 minutes for large processes
- Requires sensor to be online and process to exist
- Must provide full YARA rule content
- Scans process virtual memory
- Uses interactive tasking mode

### Step 3: Handle the Response

The response contains YARA match results:
```json
{
  "matches": [
    {
      "rule_name": "CobaltStrike_Beacon",
      "namespace": "malware",
      "tags": ["apt", "c2"],
      "strings": [
        {
          "identifier": "$beacon_config",
          "offset": "0x1000",
          "data": "6D6573736167652E..."
        }
      ],
      "meta": {
        "description": "Detects Cobalt Strike beacon in memory",
        "author": "Threat Intel Team"
      }
    }
  ]
}
```

**Success:**
- Returns array of rule matches
- Each match includes:
  - `rule_name`: Name of the YARA rule that matched
  - `namespace`: Rule namespace if defined
  - `tags`: Rule tags for categorization
  - `strings`: Specific string matches with offsets
  - `meta`: Rule metadata (author, description, etc.)
- Empty array if no matches found (clean result)

**Common Errors:**
- **Sensor offline**: Sensor not currently connected
- **Process not found**: PID doesn't exist on sensor
- **Invalid YARA rule**: Syntax error in rule - validate rule first
- **Timeout**: Scan took longer than expected (large process)
- **Access denied**: Process protected or insufficient privileges
- **Permission denied**: Insufficient rights to task sensor

### Step 4: Format the Response

Present the result to the user:
- Clearly state if matches were found (positive detection)
- List matched rule names and their significance
- Show match details including memory offsets
- Explain what the detection means (malware family, threat type)
- If no matches: confirm process appears clean for given rules
- Include rule metadata for context
- Recommend next steps based on findings

## Example Usage

### Example 1: Scanning for Cobalt Strike

User request: "Scan process 1234 for Cobalt Strike indicators"

Steps:
1. Obtain or create YARA rule for Cobalt Strike
2. Call the tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="yara_scan_process",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc-123-def-456-ghi-789",
    "pid": 1234,
    "rules": "rule CobaltStrike_Beacon { strings: $a = \"beacon\" meta: author = \"SOC\" condition: $a }"
  }
)
```

If match found: "ALERT: Process 1234 matches Cobalt Strike beacon signature. Immediate investigation required."

### Example 2: Using comprehensive malware rules

User request: "Scan the suspicious PowerShell process with ransomware rules"

Steps:
1. Find PowerShell process PID
2. Provide ransomware detection rules:
```
mcp__limacharlie__lc_call_tool(
  tool_name="yara_scan_process",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc-123-def-456-ghi-789",
    "pid": 5678,
    "rules": "rule Ransomware_Generic { strings: $ransom = \"Your files have been encrypted\" condition: $ransom }"
  }
)
```

## Additional Notes

- YARA scanning can be resource-intensive on large processes
- False positives are possible - validate findings
- Use high-quality, well-tested YARA rules
- Must provide full rule content inline
- Process memory is scanned, not the file on disk
- Useful for detecting fileless malware
- Packed/obfuscated malware may evade simple rules
- Combine with other forensic tools for comprehensive analysis
- Match offsets help locate malicious code in memory
- Some legitimate software may trigger generic rules
- Keep YARA rules updated with latest threat intelligence
- Consider scanning multiple processes for thorough hunting
- Rule performance varies - complex rules take longer
- Memory-only artifacts (shellcode, reflective DLLs) can be detected

## Reference

For the MCP tool, this uses the dedicated `yara_scan_process` tool via `lc_call_tool`.

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/yara.go`
