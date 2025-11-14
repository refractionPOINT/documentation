
# Directory List

List directory contents on a sensor with support for wildcards and recursive traversal.

## When to Use

Use this skill when the user needs to:
- List files in a directory
- Explore file system structure
- Find files matching patterns (*.exe, *.dll, etc.)
- Recursively enumerate directory trees
- Investigate dropped malware files
- Check for specific file types in directories

Common scenarios:
- "List all files in C:\\Temp"
- "Show me all executables in C:\\Users\\Downloads"
- "Find all .ps1 files in C:\\Scripts recursively"
- "List contents of /var/log"

## What This Skill Does

This skill sends a directory listing command to the sensor that returns file and subdirectory information. It supports wildcards for file matching and can recursively traverse subdirectories to a specified depth.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **sid**: Sensor ID (UUID)
- **root_dir**: Root directory path to list
- **file_expression**: File pattern with wildcards (* and ?)
- **depth** (optional): Maximum recursion depth (default: 1 for single level)

The sensor must be online and the directory must exist.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Valid directory path that exists
4. File expression with wildcards if needed
5. Appropriate depth for the operation
6. Sensor is online

**File Expression Wildcards:**
- `*` - Matches any characters
- `?` - Matches single character
- `*.*` - All files with extensions
- `*.exe` - All executable files
- `file?.txt` - Matches file1.txt, fileA.txt, etc.

**Depth Parameter:**
- 1 = Only the root directory (no recursion)
- 2 = Root and immediate subdirectories
- 5+ = Deep recursion (be careful with large trees)

### Step 2: Send the Sensor Command

```
mcp__limacharlie__dir_list(
  oid="[organization-id]",
  sid="[sensor-id]",
  root_dir="[directory-path]",
  file_expression="[pattern]",
  depth=[depth-level]
)
```

**Technical Details:**
- Executes the `dir_list` sensor command
- Timeout: Up to 10 minutes
- Supports wildcards in file expression
- Recursively traverses based on depth
- Uses interactive tasking mode

### Step 3: Handle the Response

The response contains file and directory information:
```json
{
  "files": [
    {
      "path": "C:\\Temp\\malware.exe",
      "name": "malware.exe",
      "size": 1048576,
      "modified": "2024-01-15T10:30:00Z",
      "created": "2024-01-15T10:25:00Z",
      "attributes": ["archive"],
      "is_directory": false
    },
    {
      "path": "C:\\Temp\\logs",
      "name": "logs",
      "is_directory": true
    }
  ],
  "total_files": 15,
  "total_directories": 3
}
```

**Success:**
- Returns array of files and directories
- Each entry includes:
  - `path`: Full path to the item
  - `name`: File/directory name
  - `size`: File size in bytes (files only)
  - `modified`: Last modified timestamp
  - `created`: Creation timestamp
  - `attributes`: File attributes
  - `is_directory`: Boolean flag
- Summary counts

**Common Errors:**
- **Sensor offline**: Sensor not connected
- **Directory not found**: Path doesn't exist
- **Access denied**: Directory protected or insufficient privileges
- **Timeout**: Too many files or depth too large
- **Permission denied**: Insufficient rights to task sensor

### Step 4: Format the Response

Present the result to the user:
- Summary: Found X files and Y directories
- List files with relevant details (name, size, timestamps)
- Highlight suspicious files (executables in temp, recently created)
- Group by directory if recursive
- Note any unusual file attributes or timestamps
- Filter or sort based on user's query

## Example Usage

### Example 1: Listing temp directory

User request: "Show me all files in C:\\Temp"

Steps:
1. Set root_dir to C:\\Temp
2. Use *.* for all files
3. Call the tool:
```
mcp__limacharlie__dir_list(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  sid="abc-123-def-456-ghi-789",
  root_dir="C:\\Temp",
  file_expression="*.*",
  depth=1
)
```

Present formatted list of files found.

### Example 2: Finding PowerShell scripts recursively

User request: "Find all .ps1 files in C:\\Scripts and subdirectories"

Steps:
1. Set root_dir to C:\\Scripts
2. Use *.ps1 pattern
3. Set depth=5 for recursive search
4. Present all matching PowerShell scripts found

## Additional Notes

- Depth 1 is non-recursive (only the specified directory)
- Higher depth values scan more directories (slower)
- Large directories with deep recursion may timeout
- Wildcards work on file names, not paths
- Hidden and system files are included
- Some directories may have access restrictions
- Network paths can be listed if accessible
- Timestamps help identify recently dropped files
- File size can indicate packed/compressed files
- Symbolic links and junctions are followed
- Use specific patterns (*.exe, *.dll) for focused searches
- Consider performance impact on deep/large directory trees
- Archive attributes may indicate compression
- Recently created files in temp directories are suspicious
- Cross-reference file hashes with threat intelligence

## Reference

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
