
# YARA Scan File

Scan a specific file on disk using YARA rules to detect malware patterns and indicators of compromise.

## When to Use

Use this skill when the user needs to:
- Scan suspicious files for malware signatures
- Validate files against threat intelligence
- Identify malware families by file signature
- Check downloaded files for threats
- Analyze dropped files during incident response
- Perform targeted IOC matching on disk

Common scenarios:
- "Scan this suspicious executable with YARA"
- "Check if this file matches known malware"
- "Run malware detection on C:\\Temp\\suspicious.exe"
- "Use YARA to identify this file"

## What This Skill Does

This skill sends a YARA rule to the sensor and scans a specific file on disk for matches. The sensor loads the YARA rule, applies it to the target file's contents, and returns any matches found. This is essential for file-based malware detection and forensic analysis.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all operations)
- **sid**: Sensor ID (UUID) of the target sensor
- **file_path**: Full path to the file on the sensor
- **rules**: YARA rule content (full rule text)

The sensor must be online, the file must exist, and the YARA rule must be valid.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Valid file path that exists on the sensor
4. Valid YARA rule (syntax-checked)
5. Sensor is online and responsive
6. File is accessible (not locked or protected)

### Step 2: Send the Sensor Command

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="yara_scan_file",
  parameters={
    "oid": "[organization-id]",
    "sid": "[sensor-id]",
    "file_path": "[full-file-path]",
    "rules": "[yara-rule-content]"
  }
)
```

**Technical Details:**
- This executes the `yara_scan` sensor command with filePath parameter
- Timeout: Up to 10 minutes for large files
- Requires sensor to be online and file to exist
- Must provide full YARA rule content
- Scans file contents on disk
- Uses interactive tasking mode

### Step 3: Handle the Response

The response contains YARA match results:
```json
{
  "matches": [
    {
      "rule_name": "Ransomware_Wannacry",
      "namespace": "malware",
      "tags": ["ransomware", "worm"],
      "strings": [
        {
          "identifier": "$ransom_note",
          "offset": "0x2000",
          "data": "596F75722066696C65732068617665206265656E20656E637279707465642E2E2E"
        }
      ],
      "meta": {
        "description": "Detects WannaCry ransomware",
        "author": "Threat Intel Team",
        "hash": "abc123..."
      }
    }
  ],
  "file_path": "C:\\Temp\\suspicious.exe",
  "file_size": 1048576,
  "file_hash": "d41d8cd98f00b204e9800998ecf8427e"
}
```

**Success:**
- Returns array of rule matches
- Each match includes:
  - `rule_name`: Name of the YARA rule that matched
  - `namespace`: Rule namespace if defined
  - `tags`: Rule tags for categorization
  - `strings`: Specific string matches with file offsets
  - `meta`: Rule metadata (author, description, etc.)
- File information (path, size, hash)
- Empty matches array if file is clean

**Common Errors:**
- **Sensor offline**: Sensor not currently connected
- **File not found**: File path doesn't exist on sensor
- **Invalid YARA rule**: Syntax error in rule - validate rule first
- **Timeout**: Scan took longer than expected (large file)
- **Access denied**: File locked, protected, or insufficient privileges
- **Permission denied**: Insufficient rights to task sensor

### Step 4: Format the Response

Present the result to the user:
- Clearly state if matches were found (positive detection)
- List matched rule names and their significance
- Show match details including file offsets
- Include file hash for correlation with threat intelligence
- Explain what the detection means (malware family, threat type)
- If no matches: confirm file appears clean for given rules
- Recommend next steps (quarantine, analysis, deletion)

## Example Usage

### Example 1: Scanning suspicious executable

User request: "Scan C:\\Temp\\suspicious.exe for malware"

Steps:
1. Obtain or create comprehensive malware YARA rule
2. Call the tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="yara_scan_file",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc-123-def-456-ghi-789",
    "file_path": "C:\\Temp\\suspicious.exe",
    "rules": "rule Generic_Malware { strings: $mz = \"MZ\" $sus = \"malicious\" condition: $mz and $sus }"
  }
)
```

If match found: "ALERT: File matches malware signature. File hash: [hash]. Recommend immediate quarantine."

### Example 2: Using specific threat rule

User request: "Check if this file is Emotet"

Steps:
1. Use Emotet-specific YARA rule
2. Scan the target file
3. Report findings with context about Emotet threat

## Additional Notes

- File scanning is generally faster than process memory scanning
- Large files may take significant time to scan
- File must be readable by the sensor (not locked)
- Scans file contents, not memory representation
- Useful for scanning downloaded files, dropped malware, suspicious executables
- Can detect packed executables if rules are designed for it
- File hash provided in response helps with threat intelligence correlation
- Some packers/obfuscators may evade detection
- Combine with other analysis (static, dynamic, sandboxing)
- False positives possible - validate findings
- Use high-quality, tested YARA rules
- Keep rules updated with latest threat intelligence
- Consider scanning related files (DLLs, configs) in same investigation
- File offset information helps with manual analysis
- Archives and compressed files require extraction first
- Encrypted files cannot be scanned effectively

## Reference

For the MCP tool, this uses the dedicated `yara_scan_file` tool via `lc_call_tool`.

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/yara.go`
