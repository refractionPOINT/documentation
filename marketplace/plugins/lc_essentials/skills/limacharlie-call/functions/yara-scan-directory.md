
# YARA Scan Directory

Recursively scan a directory and its files using YARA rules to detect malware patterns across multiple files.

## When to Use

Use this skill when the user needs to:
- Scan entire directories for malware
- Hunt for threats across file systems
- Bulk scan downloaded files or suspicious folders
- Identify all malicious files in a directory tree
- Perform comprehensive filesystem analysis
- Check user directories for dropped malware

Common scenarios:
- "Scan C:\\Users\\Downloads for malware"
- "Check all executables in C:\\Temp"
- "Scan this directory tree for ransomware"
- "Hunt for malicious PowerShell scripts in user folders"

## What This Skill Does

This skill sends a YARA rule to the sensor and recursively scans files in a directory for matches. The sensor traverses the directory tree up to a specified depth, applies the YARA rule to matching files, and returns any matches found. This is essential for bulk malware detection and filesystem threat hunting.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all operations)
- **sid**: Sensor ID (UUID) of the target sensor
- **root_dir**: Full path to the directory on the sensor
- **rules**: YARA rule content (full rule text)
- **file_expression** (optional): File pattern to match (e.g., '*.exe', '*.dll', '*.ps1')
- **depth** (optional): Maximum recursion depth (default: 5)

The sensor must be online and the directory must exist.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Valid directory path that exists on the sensor
4. Valid YARA rule (syntax-checked)
5. File pattern if filtering specific types
6. Appropriate depth for the operation scope
7. Sensor is online and responsive

### Step 2: Send the Sensor Command

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="yara_scan_directory",
  parameters={
    "oid": "[organization-id]",
    "sid": "[sensor-id]",
    "root_dir": "[directory-path]",
    "rules": "[yara-rule-content]",
    "file_expression": "[file-pattern]",
    "depth": [recursion-depth]
  }
)
```

**Technical Details:**
- This executes the `yara_scan` sensor command with rootDir parameter
- Timeout: Up to 10 minutes (can be longer for large directories)
- Recursively scans subdirectories up to specified depth
- Can filter files by pattern (*.exe, *.dll, etc.)
- Default depth: 5 levels
- Uses interactive tasking mode

### Step 3: Handle the Response

The response contains YARA match results for all matching files:
```json
{
  "matches": [
    {
      "file_path": "C:\\Temp\\malware.exe",
      "rule_name": "Ransomware_Generic",
      "strings": [
        {
          "identifier": "$ransom",
          "offset": "0x1000"
        }
      ]
    },
    {
      "file_path": "C:\\Temp\\subfolder\\trojan.dll",
      "rule_name": "Trojan_Banker",
      "strings": [
        {
          "identifier": "$bank_keyword",
          "offset": "0x2500"
        }
      ]
    }
  ],
  "scanned_files": 156,
  "matched_files": 2
}
```

**Success:**
- Returns array of matches from all scanned files
- Each match includes:
  - `file_path`: Full path to the matching file
  - `rule_name`: YARA rule that matched
  - `strings`: String matches with offsets
  - File-specific metadata
- Summary statistics (files scanned, matches found)
- Empty matches if no malware detected

**Common Errors:**
- **Sensor offline**: Sensor not currently connected
- **Directory not found**: Path doesn't exist on sensor
- **Invalid YARA rule**: Syntax error in rule
- **Timeout**: Too many files or depth too large
- **Access denied**: Directory protected or insufficient privileges
- **Permission denied**: Insufficient rights to task sensor

### Step 4: Format the Response

Present the result to the user:
- Summary: X files scanned, Y matches found
- List each matching file with its detection
- Group by rule name or directory if helpful
- Highlight severity of findings
- Provide file paths for remediation
- If no matches: confirm directory appears clean
- Recommend next steps (quarantine, deletion, further analysis)

## Example Usage

### Example 1: Scanning Downloads folder

User request: "Scan C:\\Users\\John\\Downloads for malware"

Steps:
1. Prepare generic malware YARA rule
2. Call the tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="yara_scan_directory",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc-123-def-456-ghi-789",
    "root_dir": "C:\\Users\\John\\Downloads",
    "rules": "rule Malware { strings: $a = \"malicious\" condition: $a }",
    "file_expression": "*.*",
    "depth": 3
  }
)
```

Report: "Scanned 47 files in Downloads folder. Found 2 malicious files: malware.exe and trojan.dll. Immediate action required."

### Example 2: Scanning for specific file types

User request: "Check all PowerShell scripts in C:\\Scripts for malicious code"

Steps:
1. Use PowerShell-specific YARA rules
2. Filter for .ps1 files:
```
mcp__limacharlie__lc_call_tool(
  tool_name="yara_scan_directory",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc-123-def-456-ghi-789",
    "root_dir": "C:\\Scripts",
    "rules": "rule PS_Malware { strings: $encoded = \"encodedCommand\" condition: $encoded }",
    "file_expression": "*.ps1",
    "depth": 10
  }
)
```

## Additional Notes

- Scanning large directories can take significant time
- Adjust depth parameter to control recursion
- Use file_expression to focus on specific file types (*.exe, *.dll, *.ps1)
- Default depth of 5 is reasonable for most scenarios
- Very deep recursion or large file counts may timeout
- Some directories may have access restrictions (System, Protected)
- Network shares can be scanned if accessible to sensor
- Symbolic links and junctions are followed
- Hidden files are included in scan
- Locked files may be skipped
- Consider scanning during off-hours for large operations
- Can be resource-intensive on endpoint
- Results include all matches across all files
- Use specific YARA rules for better performance
- Broad rules on large directories = long scan times
- Archive files (.zip, .rar) are not automatically extracted
- Encrypted files cannot be effectively scanned

## Reference

For the MCP tool, this uses the dedicated `yara_scan_directory` tool via `lc_call_tool`.

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/yara.go`
