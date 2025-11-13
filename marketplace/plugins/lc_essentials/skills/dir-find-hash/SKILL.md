---
name: dir-find-hash
description: Search for files by SHA256 hash in directory trees on a live sensor. Takes hash list, directory path, file pattern, and recursion depth. Returns matching file paths. Use for IOC hunting, known malware detection, file hash validation, identifying specific files across systems, and locating known threats during investigations.
allowed-tools: mcp__limacharlie__dir_find_hash, Read
---

# Directory Find Hash

Search for files matching specific SHA256 hashes within a directory tree on a sensor.

## When to Use

Use this skill when the user needs to:
- Find files matching known malware hashes
- Hunt for specific IOCs across the file system
- Locate files by hash across directory trees
- Validate presence of known malicious files
- Search for threat intelligence hashes
- Identify specific files without knowing paths

Common scenarios:
- "Find this malware hash on the system"
- "Search for these IOC hashes in C:\\Users"
- "Does this file hash exist anywhere in C:\\Windows?"
- "Hunt for these threat intel hashes across the file system"

## What This Skill Does

This skill sends a hash-based search command to the sensor that computes SHA256 hashes of files in a directory tree and compares them against a provided list of target hashes. It returns the paths of any files that match, making it ideal for IOC hunting.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **sid**: Sensor ID (UUID)
- **root_dir**: Root directory path to search
- **file_expression**: File pattern with wildcards
- **hashes**: Array of SHA256 hashes (64 hex characters each)
- **depth** (optional): Maximum recursion depth (default: 1)

The sensor must be online and directory must exist.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Valid directory path
4. Valid SHA256 hashes (exactly 64 hexadecimal characters)
5. File expression with wildcards
6. Appropriate depth for search scope
7. Sensor is online

**Hash Format:**
- Must be SHA256 (64 hexadecimal characters)
- Lowercase or uppercase accepted
- Example: "d41d8cd98f00b204e9800998ecf8427e..."
- Provide as array: ["hash1", "hash2", "hash3"]

### Step 2: Send the Sensor Command

```
mcp__limacharlie__dir_find_hash(
  oid="[organization-id]",
  sid="[sensor-id]",
  root_dir="[directory-path]",
  file_expression="[pattern]",
  hashes=["hash1", "hash2", "hash3"],
  depth=[depth-level]
)
```

**Technical Details:**
- Executes the `dir_find_hash` sensor command
- Timeout: Up to 10 minutes (longer for large searches)
- Computes SHA256 of each matching file
- Compares against provided hash list
- Returns only matching files
- Uses interactive tasking mode

### Step 3: Handle the Response

The response contains matching files:
```json
{
  "matches": [
    {
      "path": "C:\\Temp\\malware.exe",
      "hash": "d41d8cd98f00b204e9800998ecf8427e...",
      "size": 1048576,
      "modified": "2024-01-15T10:30:00Z"
    },
    {
      "path": "C:\\Users\\Downloads\\threat.dll",
      "hash": "098f6bcd4621d373cade4e832627b4f6...",
      "size": 524288,
      "modified": "2024-01-14T08:15:00Z"
    }
  ],
  "scanned_files": 450,
  "matched_files": 2
}
```

**Success:**
- Returns array of files matching the provided hashes
- Each match includes:
  - `path`: Full path to the matching file
  - `hash`: The matching SHA256 hash
  - `size`: File size in bytes
  - `modified`: Last modified timestamp
- Summary of files scanned and matched
- Empty array if no matches found (good news)

**Common Errors:**
- **Sensor offline**: Sensor not connected
- **Directory not found**: Path doesn't exist
- **Invalid hash**: Hash not 64 hex characters
- **Timeout**: Too many files or depth too large
- **Access denied**: Directory protected
- **Permission denied**: Insufficient rights

### Step 4: Format the Response

Present the result to the user:
- Clear alert if matches found (IOC detected)
- List each matching file with path and hash
- Include file metadata (size, timestamp)
- Explain significance (known malware, threat intel match)
- If no matches: confirm hashes not found (system clean)
- Recommend next steps (quarantine, deletion, investigation)
- Note how many files were scanned

## Example Usage

### Example 1: Hunting for malware hash

User request: "Search for this malware hash across C:\\Users"

Steps:
1. Obtain malware SHA256 hash
2. Call the tool:
```
mcp__limacharlie__dir_find_hash(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  sid="abc-123-def-456-ghi-789",
  root_dir="C:\\Users",
  file_expression="*.*",
  hashes=["d41d8cd98f00b204e9800998ecf8427e..."],
  depth=5
)
```

If found: "ALERT: Malware hash found at C:\\Users\\John\\Downloads\\malware.exe. Immediate action required."

### Example 2: Multiple IOC hunting

User request: "Check for these 5 threat intel hashes on the system"

Steps:
1. Collect array of hashes from threat intelligence
2. Search across relevant directories
3. Report any matches with full context

## Additional Notes

- Hash computation can be time-consuming for large files
- Scans only files matching the pattern
- Depth controls how deep to recurse
- More efficient than listing all files then hashing separately
- Useful for IOC hunting from threat intelligence
- SHA256 is cryptographically strong - matches are reliable
- Can search for multiple hashes in one operation
- Large file counts with deep recursion may timeout
- Consider focusing on high-risk directories (Downloads, Temp)
- Files must be readable to compute hash
- Locked files will be skipped
- Network paths can be searched if accessible
- Archive files (.zip, .rar) are not extracted
- Matches indicate presence of known threat
- Cross-reference with VirusTotal or other threat intel
- Useful for post-incident validation
- Can verify cleanup after malware removal
- Empty result means system appears clean for those hashes

## Reference

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/sensor.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/forensics/forensics.go`
