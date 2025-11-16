
# Get Registry Keys

Retrieve Windows registry keys and values from a specific path on a sensor. Windows-only operation.

## When to Use

Use this skill when the user needs to:
- Query Windows registry for specific keys
- Investigate registry-based persistence
- Extract malware configuration from registry
- Analyze registry modifications
- Check registry run keys or startup entries
- Collect registry forensic artifacts

Common scenarios:
- "Show me the registry key HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
- "Get registry values for this path"
- "Check what's in the malware's registry key"
- "Query registry for persistence mechanisms"

## What This Skill Does

This skill sends a live command to query a specific Windows registry path and retrieve all keys, subkeys, and values at that location. This is essential for Windows forensics and malware investigation.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **sid**: Sensor ID (UUID) - must be a Windows sensor
- **path**: Full registry path (e.g., "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run")

The sensor must be online and must be running Windows.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) - Windows sensor
3. Valid registry path
4. Sensor is online

**Registry Path Format:**
- Use full registry paths with hive abbreviations
- HKLM = HKEY_LOCAL_MACHINE
- HKCU = HKEY_CURRENT_USER
- HKCR = HKEY_CLASSES_ROOT
- HKU = HKEY_USERS
- Example: "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"

### Step 2: Send the Sensor Command

```
mcp__limacharlie__get_registry_keys(
  oid="[organization-id]",
  sid="[sensor-id]",
  path="[registry-path]"
)
```

**Technical Details:**
- Executes the `reg_list` sensor command
- Timeout: Up to 10 minutes
- Windows-only operation
- Returns keys, values, and data

### Step 3: Handle the Response

The response contains registry information:
```json
{
  "keys": [
    {
      "name": "Run",
      "values": [
        {
          "name": "SecurityHealth",
          "type": "REG_EXPAND_SZ",
          "data": "%windir%\\system32\\SecurityHealthSystray.exe"
        },
        {
          "name": "MalwareEntry",
          "type": "REG_SZ",
          "data": "C:\\Temp\\malware.exe"
        }
      ]
    }
  ]
}
```

**Success:**
- Returns registry structure with keys and values
- Each value includes:
  - `name`: Value name
  - `type`: Registry value type (REG_SZ, REG_DWORD, etc.)
  - `data`: Value data
- Subkeys listed if present

**Common Errors:**
- **Sensor offline**: Sensor not connected
- **Not Windows**: This only works on Windows sensors
- **Access denied**: Registry key protected or insufficient privileges
- **Key not found**: Registry path doesn't exist
- **Permission denied**: Insufficient rights to task sensor

### Step 4: Format the Response

Present the result to the user:
- Show registry path queried
- List all values found with their types and data
- Highlight suspicious entries (unusual paths, temp directories)
- Note any empty or missing values
- Explain significance of found entries

## Example Usage

### Example 1: Checking Run keys for persistence

User request: "Check the Run key for startup entries"

Steps:
1. Query the Run registry key
2. Call the tool:
```
mcp__limacharlie__get_registry_keys(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  sid="abc-123-def-456-ghi-789",
  path="HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
)
```

Present findings highlighting any suspicious entries.

### Example 2: Investigating malware registry key

User request: "What's stored in this malware's registry configuration?"

Steps:
1. Identify registry path from malware analysis
2. Query that specific path
3. Extract and present configuration data

## Additional Notes

- Windows-only operation - will fail on Linux/macOS sensors
- Registry paths are case-insensitive on Windows
- Some registry keys require elevated privileges
- Protected keys (SAM, SECURITY) may be inaccessible
- Common persistence locations:
  - HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run
  - HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run
  - HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce
  - HKLM\\SYSTEM\\CurrentControlSet\\Services
- Registry forensics is critical for Windows investigations
- Malware often stores configuration in registry
- Check for unusual binary data in registry values
- Some values may contain encrypted or encoded data
- Registry timestamps not returned by this command
- Use for targeted queries, not full registry dumps
- Large registry keys may take time to enumerate

## Reference

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
