# Artifact Collection Command Reference

Complete syntax and parameters for all artifact collection commands.

## Table of Contents

1. [File Collection Commands](#file-collection-commands)
2. [Memory Commands](#memory-commands)
3. [Log Commands](#log-commands)
4. [Information Commands](#information-commands)
5. [Dumper Extension](#dumper-extension)
6. [Reliable Tasking](#reliable-tasking)
7. [Artifact Collection Rules](#artifact-collection-rules)

---

## File Collection Commands

### artifact_get

Retrieve an artifact from a sensor and upload it to LimaCharlie's artifact storage.

**Syntax**:
```
artifact_get <file_path> [--type <type>]
```

**Parameters**:
- `<file_path>`: Path to the file or artifact (required)
- `--type`: Optional type specification (e.g., `pcap`, `evtx`)

**Supported Platforms**: Windows, macOS, Linux

**Examples**:
```bash
# Collect a suspicious executable
artifact_get C:\Users\alice\Downloads\malware.exe

# Collect Windows Event Log
artifact_get C:\Windows\System32\winevt\Logs\Security.evtx

# Collect PCAP file
artifact_get /path/to/capture.pcap --type pcap

# Collect with wildcards
artifact_get C:\Users\*\Downloads\*.exe
```

**Use in D&R Rules**:
```yaml
- action: task
  command: artifact_get {{ .event.FILE_PATH }}
  investigation: artifact-collection
```

**Notes**:
- Uploads to persistent artifact storage
- Files are retained based on retention policy (default: 30 days)
- Incurs artifact ingestion costs
- Supports wildcards for bulk collection

---

### file_get

Retrieve file content from a sensor (returns content in response, does not persist to artifact storage).

**Syntax**:
```
file_get --path <file_path>
```

**Parameters**:
- `--path`: Path to the file to retrieve (required)

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `FILE_GET_REP`

**Examples**:
```bash
# Get a configuration file
file_get --path /etc/passwd

# Get a Windows registry hive
file_get --path C:\Windows\System32\config\SAM

# Get a small log file
file_get --path /var/log/application.log
```

**Differences from artifact_get**:
- `file_get`: Returns content in command response (smaller files, immediate access, no storage costs)
- `artifact_get`: Uploads to artifact storage (larger files, persistent storage, incurs costs)

**Best for**:
- Small configuration files
- Quick file inspection
- Files under 1MB
- When you don't need persistent storage

---

### file_hash

Calculate hash of a file without retrieving it.

**Syntax**:
```
file_hash --path <file_path>
```

**Parameters**:
- `--path`: Path to file to hash (required)

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `FILE_HASH_REP`

**Examples**:
```bash
# Hash a file
file_hash --path C:\Windows\System32\calc.exe

# Hash suspicious file
file_hash --path /tmp/malware.elf

# Hash before collecting
file_hash --path C:\Users\alice\Downloads\setup.exe
```

**Use Cases**:
- Quick malware identification
- Verify file integrity
- Compare against threat intelligence
- Check before collecting to avoid duplicates

**Returned Hashes**:
- MD5
- SHA1
- SHA256

---

### file_info

Get detailed file metadata.

**Syntax**:
```
file_info --path <file_path>
```

**Parameters**:
- `--path`: Path to file (required)

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `FILE_INFO_REP`

**Examples**:
```bash
# Get file information
file_info --path C:\Users\alice\Downloads\setup.exe

# Check file details
file_info --path /var/log/suspicious.log
```

**Returned Information**:
- File size
- Creation time (Windows)
- Modification time
- Access time
- File attributes (Windows)
- Permissions (Linux/macOS)
- Owner (Linux/macOS)

**Use Cases**:
- Determine file size before collection
- Check timestamps for timeline analysis
- Verify file permissions
- Assess if file should be collected

---

### dir_list

List directory contents.

**Syntax**:
```
dir_list --path <directory_path> [--depth <levels>]
```

**Parameters**:
- `--path`: Directory path to list (required)
- `--depth`: Optional recursion depth (default: 0 = non-recursive)

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `DIR_LIST_REP`

**Examples**:
```bash
# List directory contents
dir_list --path C:\Users\alice\Downloads

# Recursive listing (2 levels deep)
dir_list --path /tmp --depth 2

# Deep recursive listing
dir_list --path C:\Windows\Temp --depth 5
```

**Use Cases**:
- Identify files before collection
- Survey suspicious directories
- Build file system timeline
- Find files matching patterns

**Notes**:
- Returns file names, sizes, and timestamps
- Use before collecting to understand what you're getting
- Deep recursion can take time on large directories

---

## Memory Commands

### mem_read

Read memory from a specific process.

**Syntax**:
```
mem_read --pid <process_id> --base <address> --size <bytes>
```

**Parameters**:
- `--pid`: Process ID to read from (required)
- `--base`: Base memory address in hexadecimal (required)
- `--size`: Number of bytes to read (required)

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `MEM_READ_REP`

**Examples**:
```bash
# Read 1024 bytes from a specific address
mem_read --pid 1234 --base 0x00400000 --size 1024

# Read specific memory region
mem_read --pid 5678 --base 0x7FF00000 --size 4096

# Read from discovered address
mem_read --pid 2468 --base 0x140000000 --size 512
```

**Use Cases**:
- Extract encrypted data from memory
- Analyze injected code
- Collect encryption keys
- Examine process artifacts
- Read specific memory regions found via mem_map

**Notes**:
- Requires knowing the exact address (use mem_map first)
- Address must be in hexadecimal format
- Returns raw bytes

---

### mem_map

Get the memory map of a process showing all loaded modules and memory regions.

**Syntax**:
```
mem_map --pid <process_id>
```

**Parameters**:
- `--pid`: Process ID to map (required)

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `MEM_MAP_REP`

**Examples**:
```bash
# Get memory map for process
mem_map --pid 1234

# Map suspicious process
mem_map --pid 5678
```

**Use Cases**:
- Identify loaded DLLs/libraries
- Detect code injection
- Find memory anomalies
- Investigate rootkits
- Locate memory regions for mem_read

**Returned Information**:
- Memory region addresses
- Loaded module names
- Memory permissions
- Region sizes
- Module paths

---

### mem_strings

Extract strings from process memory.

**Syntax**:
```
mem_strings --pid <process_id>
```

**Parameters**:
- `--pid`: Process ID to extract strings from (required)

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `MEM_STRINGS_REP`

**Examples**:
```bash
# Extract strings from suspicious process
mem_strings --pid 1234

# Extract strings from browser process
mem_strings --pid 5678
```

**Use Cases**:
- Find URLs or domains in memory
- Extract configuration data
- Identify command-and-control indicators
- Locate encryption keys
- Discover hardcoded credentials

**Notes**:
- Extracts ASCII and Unicode strings
- Can generate large output
- Use mem_find_string if searching for specific strings

---

### mem_find_string

Search for a specific string in process memory.

**Syntax**:
```
mem_find_string --pid <process_id> --string <search_string>
```

**Parameters**:
- `--pid`: Process ID to search (required)
- `--string`: String to search for (required)

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `MEM_FIND_STRING_REP`

**Examples**:
```bash
# Search for a domain in process memory
mem_find_string --pid 1234 --string "evil.com"

# Search for a password
mem_find_string --pid 5678 --string "password"

# Search for an IP address
mem_find_string --pid 9012 --string "192.168.1.100"

# Search for a URL
mem_find_string --pid 3456 --string "http://malicious-site.com"
```

**Use Cases**:
- Find specific IOCs in memory
- Locate C2 domains
- Search for credentials
- Find configuration strings
- Verify presence of indicators

**Notes**:
- More efficient than mem_strings when searching for specific values
- Returns addresses where string was found
- Case-sensitive search

---

## Log Commands

### log_get

Retrieve Windows Event Logs.

**Syntax**:
```
log_get <log_name>
```

**Parameters**:
- `<log_name>`: Name of the Windows Event Log (required)

**Supported Platforms**: Windows only

**Examples**:
```bash
# Get Security log
log_get Security

# Get System log
log_get System

# Get Application log
log_get Application

# Get Sysmon log
log_get Microsoft-Windows-Sysmon/Operational

# Get PowerShell log
log_get Microsoft-Windows-PowerShell/Operational
```

**Common Log Names**:
- `Security` - Security events
- `System` - System events
- `Application` - Application events
- `Microsoft-Windows-Sysmon/Operational` - Sysmon events
- `Microsoft-Windows-PowerShell/Operational` - PowerShell events
- `Microsoft-Windows-Windows Defender/Operational` - Defender events

**Use Cases**:
- Collect historical event logs
- Audit log analysis
- Incident investigation
- Compliance evidence

**Notes**:
- Returns events in JSON format
- For real-time streaming, use `wel://` in Artifact Collection rules
- File collection incurs costs; streaming is included in sensor flat rate

---

### history_dump

Dump historical events from the sensor's local cache.

**Syntax**:
```
history_dump
```

**Parameters**: None

**Supported Platforms**: Windows, macOS, Linux, Chrome, Edge

**Response Event**: `HISTORY_DUMP_REP`

**Examples**:
```bash
# Dump all cached events
history_dump
```

**Use Cases**:
- Recover events during connectivity issues
- Investigate incidents that occurred offline
- Fill gaps in timeline
- Retrieve events not yet sent to cloud

**Notes**:
- Retrieves events cached locally on the sensor
- Cache size depends on sensor configuration
- Useful when sensors were offline during an incident

---

## Information Commands

### os_processes

List all running processes.

**Syntax**:
```
os_processes
```

**Parameters**: None

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `PROCESS_LIST`

**Use Cases**:
- Identify suspicious processes
- Baseline running processes
- Find process IDs for memory commands
- Detect anomalies

---

### netstat

Show network connections.

**Syntax**:
```
netstat
```

**Parameters**: None

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `NETWORK_CONNECTIONS`

**Use Cases**:
- Identify active network connections
- Detect unauthorized communications
- Find listening ports
- Map network activity

---

### os_users

List user accounts.

**Syntax**:
```
os_users
```

**Parameters**: None

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `USER_LIST`

**Use Cases**:
- Audit user accounts
- Detect unauthorized users
- Investigate authentication issues

---

### os_services

List system services.

**Syntax**:
```
os_services
```

**Parameters**: None

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `SERVICE_LIST`

**Use Cases**:
- Identify malicious services
- Audit running services
- Detect persistence mechanisms

---

### os_autoruns

List autostart programs.

**Syntax**:
```
os_autoruns
```

**Parameters**: None

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `AUTORUNS`

**Use Cases**:
- Detect persistence mechanisms
- Identify malicious autoruns
- Audit startup programs

---

## Dumper Extension

The Dumper extension enables collection of large artifacts like full memory dumps and MFT data.

### Overview

**Extension Name**: `ext-dumper`

**Capabilities**:
- Full memory dumps
- Master File Table (MFT) dumps
- Process dumps
- Configurable retention

### Requesting a Memory Dump

**Via D&R Rule**:
```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 30
```

**Via REST API**:
```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-dumper' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=request_dump&data={"target":"memory","sid":"SENSOR_ID","retention":30}'
```

**Parameters**:
- `target`: Type of dump (`memory` or `mft`)
- `sid`: Sensor ID to collect from
- `retention`: Number of days to retain (default: 30)

### Requesting an MFT Dump

**Via D&R Rule**:
```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: mft
    sid: <<routing.sid>>
    retention: 7
```

**Via REST API**:
```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-dumper' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=request_dump&data={"target":"mft","sid":"SENSOR_ID","retention":7}'
```

### Dump Types

**Memory Dumps**:
- Complete system memory snapshot
- Size equals system RAM
- Useful for malware analysis, rootkit detection
- Can be analyzed with Volatility, Rekall, WinDbg

**MFT Dumps**:
- Windows Master File Table
- Complete file system metadata
- Timeline analysis capability
- Deleted file recovery
- Can be analyzed with MFTExplorer, analyzeMFT

### Performance Considerations

- Memory dumps can be very large (equal to RAM size)
- MFT dumps are typically smaller but still substantial
- Collection takes time depending on size and network bandwidth
- Consider using Reliable Tasking for offline or intermittent systems
- Set appropriate retention to manage costs

---

## Reliable Tasking

The Reliable Tasking extension enables artifact collection from sensors that are currently offline.

### Overview

**Extension Name**: `ext-reliable-tasking`

**Benefits**:
- Tasks are automatically sent when sensors come online
- Configurable TTL (time-to-live) for tasks
- Track task status and responses
- Support for multiple targeting criteria

### Creating Tasks

**Endpoint**:
```
POST https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking
```

**Action**: `task`

**Data Parameters**:
- `context`: Identifier for grouping related tasks
- `task`: The command to execute
- `ttl`: Time-to-live in seconds (default: 604800 = 1 week)
- Targeting (choose one):
  - `sid`: Specific Sensor ID
  - `tag`: All sensors with a specific tag
  - `plat`: All sensors of a platform (windows, linux, macos)
  - `selector`: Advanced selector expression

### Examples

**Task Specific Sensor**:
```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"context":"forensics","sid":"abc123","task":"mem_map --pid 1234","ttl":3600}'
```

**Task All Windows Sensors**:
```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"context":"win-collection","plat":"windows","task":"log_get Security","ttl":7200}'
```

**Task Sensors with Tag**:
```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"context":"incident-response","tag":"compromised","task":"artifact_get C:\\malware.exe","ttl":86400}'
```

**Using Selector Expression**:
```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"context":"investigation","selector":"tag==critical AND plat==windows","task":"history_dump","ttl":172800}'
```

### Listing Active Tasks

**Action**: `list`

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=list&data={}'
```

### Deleting Tasks

**Action**: `delete`

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=delete&data={"task_id":"TASK_ID"}'
```

### Capturing Task Responses

Use the `context` parameter to track responses via D&R rules.

**D&R Rule Example**:
```yaml
detect:
  op: contains
  event: RECEIPT
  path: routing/investigation_id
  value: incident-response

respond:
  - action: report
    name: collection-completed
  - action: output
    name: artifact-responses
```

This rule matches any response from tasks with context "incident-response" and forwards them to the specified output.

---

## Artifact Collection Rules

Configure persistent collection rules in the web UI under **Sensors > Artifact Collection**.

### Windows Event Log Streaming

**Pattern**: `wel://<LogName>:<EventID>`

**Examples**:
```
wel://Security:*
wel://System:*
wel://Security:4624
wel://Microsoft-Windows-Sysmon/Operational:*
```

**Benefits**:
- Real-time streaming
- Included in sensor flat rate (no artifact costs)
- Filtered by event ID
- Automatic collection

### Mac Unified Log Streaming

**Pattern**: `mul://<filter>`

**Examples**:
```
mul://*
mul://process=="loginwindow"
mul://subsystem=="com.apple.securityd"
```

**Benefits**:
- Real-time streaming of macOS logs
- Included in sensor flat rate
- Filtered by process/subsystem

### PCAP Collection

**Platform**: Linux only

**Configuration**:
1. Navigate to **Sensors > Artifact Collection**
2. Add PCAP rule
3. Specify interface and filters
4. Configure trigger (tag, time-based, continuous)

**Trigger Options**:
- Tag-based: Start capture when sensor has specific tag
- Time-based: Capture for specified duration
- Continuous: Always capturing

**Example Configuration**:
```yaml
interface: eth0
filter: "port 443 or port 80"
trigger: tag==pcap-capture
duration: 300  # 5 minutes
```

**Use Case**:
Add tag via D&R rule to trigger PCAP on detection:
```yaml
respond:
  - action: add tag
    tag: pcap-capture
    ttl: 300
```

### File Collection Patterns

**Wildcard Support**:
```
C:\Users\*\Downloads\*.exe
/tmp/*.sh
/var/log/*.log
```

**Notes**:
- Use wildcards for bulk collection
- Consider suppression to avoid duplicates
- Monitor costs for high-volume collections
