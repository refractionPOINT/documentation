
# Get Process Modules

Retrieve the list of modules (DLLs, shared libraries) loaded by a specific process on a sensor.

## When to Use

Use this skill when the user needs to:
- Investigate what DLLs/libraries a process has loaded
- Detect DLL injection or code injection
- Analyze malware behavior and dependencies
- Identify suspicious or unsigned modules
- Understand process memory layout
- Investigate security incidents involving specific processes

Common scenarios:
- "What DLLs does this suspicious process have loaded?"
- "Is there any unusual module loaded in process PID 1234?"
- "Show me all modules for the chrome.exe process"
- "Check for DLL injection in this process"

## What This Skill Does

This skill sends a live command to the specified sensor to retrieve the list of modules loaded in a specific process's memory space. This includes DLLs on Windows, shared objects on Linux, and dylibs on macOS, along with their memory addresses and other metadata.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all operations)
- **sid**: Sensor ID (UUID) of the target sensor
- **pid**: Process ID of the target process

The sensor must be online and the process must be running.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Valid process ID (pid) that exists on the sensor
4. Sensor is online and responsive
5. Process is currently running

### Step 2: Send the Sensor Command

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="get_process_modules",
  parameters={
    "oid": "[organization-id]",
    "sid": "[sensor-id]",
    "pid": [process-id]
  }
)
```

**Technical Details:**
- This executes the `os_processes` sensor command with --pid parameter
- Timeout: Up to 10 minutes for long-running operations
- Requires sensor to be online and process to exist
- Uses interactive tasking mode
- Response is synchronous

### Step 3: Handle the Response

The response contains module information:
```json
{
  "modules": [
    {
      "name": "kernel32.dll",
      "path": "C:\\Windows\\System32\\kernel32.dll",
      "base_address": "0x7FF800000000",
      "size": 1048576,
      "signed": true,
      "signer": "Microsoft Corporation"
    },
    {
      "name": "injected.dll",
      "path": "C:\\Temp\\injected.dll",
      "base_address": "0x10000000",
      "size": 32768,
      "signed": false
    },
    ...
  ]
}
```

**Success:**
- Returns array of module objects
- Each module includes:
  - `name`: Module filename
  - `path`: Full path to module file
  - `base_address`: Memory address where module is loaded
  - `size`: Module size in bytes
  - `signed`: Whether module is digitally signed (Windows)
  - `signer`: Certificate signer name if signed
- Modules appear in load order

**Common Errors:**
- **Sensor offline**: Sensor not currently connected
- **Process not found**: PID doesn't exist on sensor
- **Timeout**: Operation took longer than expected
- **Access denied**: Process protected or insufficient privileges
- **Permission denied**: Insufficient rights to task sensor

### Step 4: Format the Response

Present the result to the user:
- List modules with key information (name, path, signed status)
- Highlight unsigned or suspicious modules
- Flag modules loaded from unusual locations (temp directories, user folders)
- Note modules with suspicious names or paths
- Group by signed/unsigned if investigating malware
- Check module signers for legitimacy

## Example Usage

### Example 1: Investigating suspicious process modules

User request: "What DLLs does process 1234 have loaded on sensor abc-123?"

Steps:
1. Verify sensor is online
2. Call the tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_process_modules",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc-123-def-456-ghi-789",
    "pid": 1234
  }
)
```

Present list of modules highlighting any unsigned or suspicious ones.

### Example 2: Detecting DLL injection

User request: "Check for DLL injection in the svchost.exe process"

Steps:
1. Get process list to find svchost.exe PID
2. Get modules for that PID
3. Look for:
   - Unsigned DLLs
   - DLLs loaded from unusual paths
   - DLLs not typically loaded by svchost.exe
4. Report findings

## Additional Notes

- Windows shows DLLs, Linux shows .so files, macOS shows .dylib files
- Unsigned modules on Windows are suspicious
- Modules loaded from temp folders, appdata, or user directories warrant investigation
- Base address can help with memory forensics
- Module load order can indicate injection timing
- System processes should only load Microsoft-signed DLLs
- Reflective DLL injection may not appear in this list
- Some legitimate software loads unsigned DLLs (less common on Windows)
- Compare with known-good module lists for the process
- Memory-only modules (fileless) may not show path
- This is a point-in-time snapshot
- Combine with process strings or memory scan for deeper analysis

## Reference

For the MCP tool, this uses the dedicated `get_process_modules` tool via `lc_call_tool`.

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
