# create_payload

Upload a payload (executable or script) to be deployed and executed on sensors.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| oid | UUID | Yes | Organization ID ([Core Concepts](../../../CALLING_API.md#core-concepts)) |
| name | string | Yes | Payload name (use file extension for type: `.exe`, `.ps1`, `.bat`, `.sh`) |
| file_path | string | Yes | Absolute path to the file to upload |

## Returns

```json
{
  "success": true,
  "message": "Successfully uploaded payload 'cleanup-tool.exe' (1048576 bytes)",
  "payload_name": "cleanup-tool.exe",
  "size": 1048576
}
```

## Examples

**Upload Windows executable:**
```
lc_call_tool(tool_name="create_payload", parameters={
  "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
  "name": "cleanup-tool.exe",
  "file_path": "/path/to/cleanup-tool.exe"
})
```

**Upload PowerShell script:**
```
lc_call_tool(tool_name="create_payload", parameters={
  "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
  "name": "collect-artifacts.ps1",
  "file_path": "/path/to/collect-artifacts.ps1"
})
```

**Upload batch script:**
```
lc_call_tool(tool_name="create_payload", parameters={
  "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
  "name": "cleanup.bat",
  "file_path": "/path/to/cleanup.bat"
})
```

## File Extension Behavior

| Extension | Execution Method |
|-----------|-----------------|
| `.exe` | Windows executable |
| `.ps1` | PowerShell script |
| `.bat` | Windows batch file |
| `.sh` | Linux/macOS shell script |
| (none) | Native executable for platform |

## Notes

- **Name determines execution type** - include appropriate file extension
- Creating with existing name **replaces** the payload
- Payload available immediately after upload
- Use `run` command with `--payload-name` to execute on sensors
- STDOUT/STDERR returned in `RECEIPT` event (up to ~10 MB)
- Requires `payload.ctrl` permission
- Consider LimaCharlie native functionality first for better performance/indexing
- Related: `list_payloads`, `get_payload`, `delete_payload`
