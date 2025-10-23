---
name: artifact-collector
description: Use this skill when users need to collect, manage, or analyze forensic artifacts such as files, memory dumps, Windows Event Logs, Mac Unified Logs, or network packet captures (PCAP) from endpoints.
---

# LimaCharlie Artifact Collector

This skill provides comprehensive guidance for collecting and managing forensic artifacts from endpoints using LimaCharlie. Use this skill when users need to gather evidence, collect files, capture memory, stream logs, or perform forensic investigations.

## Table of Contents

1. [Artifact Collection Overview](#artifact-collection-overview)
2. [Artifact Types](#artifact-types)
3. [Collection Methods](#collection-methods)
4. [Artifact Collection Commands](#artifact-collection-commands)
5. [Reliable Tasking](#reliable-tasking)
6. [Storage and Access](#storage-and-access)
7. [Automated Collection with D&R Rules](#automated-collection-with-dr-rules)
8. [Best Practices](#best-practices)
9. [Common Collection Scenarios](#common-collection-scenarios)

---

## Artifact Collection Overview

### What are Artifacts?

Artifacts are pieces of forensic evidence collected from endpoints during security investigations or incident response. In LimaCharlie, artifacts can include:

- Files from disk
- Memory dumps (full system or process-specific)
- Windows Event Log (WEL) data
- Mac Unified Log (MUL) data
- Network packet captures (PCAP)
- File system metadata (MFT)

### Why Collect Artifacts?

Artifact collection is critical for:
- **Incident Response**: Gathering evidence during security incidents
- **Forensic Analysis**: Conducting detailed investigations
- **Threat Hunting**: Searching for indicators of compromise
- **Compliance**: Meeting regulatory evidence preservation requirements
- **Malware Analysis**: Collecting suspicious files and memory for analysis

### Prerequisites

To use artifact collection features, you must:

1. Enable the **Artifact Extension** in your organization
2. Enable the **Reliable Tasking Extension** (required dependency)
3. Configure artifact collection rules (optional, for automated collection)

**Note on Billing**: While the Artifact extension is free to enable, ingested artifacts incur charges. Refer to LimaCharlie pricing for artifact ingestion and retention costs.

---

## Artifact Types

### 1. Files

Collect files from endpoints for analysis or preservation.

**Use Cases**:
- Retrieve suspicious executables
- Collect log files
- Gather configuration files
- Preserve evidence

**Collection Pattern**: Use file paths with wildcards or exact paths
- Example: `C:\Users\*\Downloads\*.exe`
- Example: `C:\Windows\System32\malware.exe`

### 2. Memory Dumps

Capture volatile memory for forensic analysis.

**Types**:
- **Full Memory Dumps**: Complete system memory snapshot
- **Process Memory**: Specific process memory regions
- **Memory Strings**: Extract strings from process memory

**Use Cases**:
- Detect in-memory malware
- Analyze running processes
- Extract encryption keys
- Identify code injection
- Examine rootkits

### 3. Windows Event Logs (WEL)

Stream or collect Windows Event Log data.

**Collection Modes**:
- **Real-time streaming**: Use `wel://` pattern (included in sensor flat rate)
- **File collection**: Collect `.evtx` files (incurs artifact costs)

**Common Logs**:
- `wel://Security:*` - Security events
- `wel://System:*` - System events
- `wel://Application:*` - Application events
- `Microsoft-Windows-Sysmon/Operational` - Sysmon events

**Use Cases**:
- Monitor authentication events
- Track privilege escalation
- Detect lateral movement
- Audit system changes

### 4. Mac Unified Logs (MUL)

Stream or collect macOS Unified Logging data.

**Collection Pattern**: Use `mul://` prefix for real-time streaming

**Use Cases**:
- Monitor macOS system events
- Track application behavior
- Audit security events
- Investigate macOS incidents

### 5. Network Packet Captures (PCAP)

Capture network traffic for analysis (Linux only).

**Collection Method**: Configure PCAP capture rules in Artifact Collection

**Use Cases**:
- Network forensics
- Protocol analysis
- Data exfiltration detection
- Communication pattern analysis

### 6. File System Metadata (MFT)

Collect Master File Table data from Windows systems.

**Collection Method**: Use Dumper extension with `target: mft`

**Use Cases**:
- Timeline analysis
- File system forensics
- Deleted file recovery
- Access pattern analysis

---

## Collection Methods

### 1. Manual Collection (Interactive)

Collect artifacts on-demand through the web UI or REST API.

**When to Use**:
- Active incident response
- Ad-hoc investigations
- Testing collection rules
- Quick evidence gathering

**Methods**:
- Task sensors directly from the web UI
- Use REST API for programmatic collection
- Issue commands via CLI tools

### 2. Automated Collection (D&R Rules)

Configure Detection & Response rules to automatically collect artifacts when specific events occur.

**When to Use**:
- Known threat patterns
- Compliance requirements
- Proactive threat hunting
- Systematic evidence collection

**Example**: Automatically collect suspicious files when they're written to disk

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: matches
      path: event/FILE_PATH
      re: .*\.(exe|dll|scr)$
      case sensitive: false
    - op: contains
      path: event/FILE_PATH
      value: \Downloads\

respond:
  - action: report
    name: suspicious-file-written
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
    investigation: susp-file-collection
```

### 3. Reliable Tasking

Use the Reliable Tasking extension to queue tasks for sensors that are currently offline.

**When to Use**:
- Sensors with intermittent connectivity
- Collecting from remote/mobile devices
- Ensuring collection happens on next check-in
- Large-scale deployments

**Benefits**:
- Tasks are automatically sent when sensors come online
- Configurable TTL (time-to-live) for tasks
- Track task status and responses

### 4. Artifact Collection Rules

Configure persistent collection rules that apply automatically based on sensor criteria.

**When to Use**:
- Continuous log streaming
- Ongoing compliance monitoring
- Standard operating procedures
- Fleet-wide artifact collection

**Configuration Location**: **Sensors > Artifact Collection** in the web UI

---

## Artifact Collection Commands

### artifact_get

Retrieve an artifact from a sensor and upload it to LimaCharlie's artifact storage.

**Syntax**:
```
artifact_get <file_path> [--type <type>]
```

**Parameters**:
- `<file_path>`: Path to the file or artifact
- `--type`: Optional type specification (e.g., `pcap`, `evtx`)

**Examples**:
```bash
# Collect a suspicious executable
artifact_get C:\Users\alice\Downloads\malware.exe

# Collect Windows Event Log
artifact_get C:\Windows\System32\winevt\Logs\Security.evtx

# Collect PCAP file
artifact_get /path/to/capture.pcap --type pcap
```

**Supported Platforms**: Windows, macOS, Linux

**Use in D&R Rules**:
```yaml
- action: task
  command: artifact_get {{ .event.FILE_PATH }}
  investigation: artifact-collection
```

### file_get

Retrieve file content from a sensor (returns content in response, does not persist to artifact storage).

**Syntax**:
```
file_get --path <file_path>
```

**Parameters**:
- `--path`: Path to the file to retrieve

**Examples**:
```bash
# Get a configuration file
file_get --path /etc/passwd

# Get a Windows registry hive
file_get --path C:\Windows\System32\config\SAM
```

**Differences from artifact_get**:
- `file_get`: Returns content in command response (smaller files, immediate access)
- `artifact_get`: Uploads to artifact storage (larger files, persistent storage)

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `FILE_GET_REP`

### log_get

Retrieve Windows Event Logs.

**Syntax**:
```
log_get <log_name>
```

**Parameters**:
- `<log_name>`: Name of the Windows Event Log

**Examples**:
```bash
# Get Security log
log_get Security

# Get System log
log_get System

# Get Sysmon log
log_get Microsoft-Windows-Sysmon/Operational
```

**Supported Platforms**: Windows only

**Use Cases**:
- Collect historical event logs
- Audit log analysis
- Incident investigation

### mem_read

Read memory from a specific process.

**Syntax**:
```
mem_read --pid <process_id> --base <address> --size <bytes>
```

**Parameters**:
- `--pid`: Process ID to read from
- `--base`: Base memory address (hexadecimal)
- `--size`: Number of bytes to read

**Examples**:
```bash
# Read 1024 bytes from a specific address
mem_read --pid 1234 --base 0x00400000 --size 1024

# Read specific memory region
mem_read --pid 5678 --base 0x7FF00000 --size 4096
```

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `MEM_READ_REP`

**Use Cases**:
- Extract encrypted data from memory
- Analyze injected code
- Collect encryption keys
- Examine process artifacts

### mem_map

Get the memory map of a process showing all loaded modules and memory regions.

**Syntax**:
```
mem_map --pid <process_id>
```

**Parameters**:
- `--pid`: Process ID to map

**Examples**:
```bash
# Get memory map for process
mem_map --pid 1234
```

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `MEM_MAP_REP`

**Use Cases**:
- Identify loaded DLLs
- Detect code injection
- Find memory anomalies
- Investigate rootkits

### mem_strings

Extract strings from process memory.

**Syntax**:
```
mem_strings --pid <process_id>
```

**Parameters**:
- `--pid`: Process ID to extract strings from

**Examples**:
```bash
# Extract strings from suspicious process
mem_strings --pid 1234
```

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `MEM_STRINGS_REP`

**Use Cases**:
- Find URLs or domains in memory
- Extract configuration data
- Identify command-and-control indicators
- Locate encryption keys

### mem_find_string

Search for a specific string in process memory.

**Syntax**:
```
mem_find_string --pid <process_id> --string <search_string>
```

**Parameters**:
- `--pid`: Process ID to search
- `--string`: String to search for

**Examples**:
```bash
# Search for a domain in process memory
mem_find_string --pid 1234 --string "evil.com"

# Search for a password
mem_find_string --pid 5678 --string "password"
```

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `MEM_FIND_STRING_REP`

### history_dump

Dump historical events from the sensor's local cache.

**Syntax**:
```
history_dump
```

**Description**: Retrieves events cached locally on the sensor, useful for recovering events if connectivity was lost.

**Examples**:
```bash
# Dump all cached events
history_dump
```

**Supported Platforms**: Windows, macOS, Linux, Chrome, Edge

**Response Event**: `HISTORY_DUMP_REP`

**Use Cases**:
- Recover events during connectivity issues
- Investigate incidents that occurred offline
- Fill gaps in timeline

### dir_list

List directory contents.

**Syntax**:
```
dir_list --path <directory_path> [--depth <levels>]
```

**Parameters**:
- `--path`: Directory path to list
- `--depth`: Optional recursion depth

**Examples**:
```bash
# List directory contents
dir_list --path C:\Users\alice\Downloads

# Recursive listing
dir_list --path /tmp --depth 3
```

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `DIR_LIST_REP`

**Use Cases**:
- Identify files before collection
- Survey suspicious directories
- Build file system timeline

### file_hash

Calculate hash of a file without retrieving it.

**Syntax**:
```
file_hash --path <file_path>
```

**Parameters**:
- `--path`: Path to file to hash

**Examples**:
```bash
# Hash a file
file_hash --path C:\Windows\System32\calc.exe

# Hash suspicious file
file_hash --path /tmp/malware.elf
```

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `FILE_HASH_REP`

**Use Cases**:
- Quick malware identification
- Verify file integrity
- Compare against threat intelligence

### file_info

Get detailed file metadata.

**Syntax**:
```
file_info --path <file_path>
```

**Parameters**:
- `--path`: Path to file

**Examples**:
```bash
# Get file information
file_info --path C:\Users\alice\Downloads\setup.exe

# Check file details
file_info --path /var/log/suspicious.log
```

**Supported Platforms**: Windows, macOS, Linux

**Response Event**: `FILE_INFO_REP`

**Returned Information**:
- File size
- Creation time
- Modification time
- Access time
- Attributes
- Permissions

---

## Reliable Tasking

### Overview

The Reliable Tasking extension enables artifact collection from sensors that are currently offline. Tasks are automatically delivered when the sensor comes online.

### Enabling Reliable Tasking

1. Navigate to the Reliable Tasking extension page in the marketplace
2. Select your Organization
3. Click **Subscribe**

**Note**: Reliable Tasking is a prerequisite for the Artifact extension.

### Creating Reliable Tasks

**Via REST API**:

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"context":"artifact-collection","selector":"tag==offline-hosts","task":"artifact_get C:\\Users\\*\\Downloads\\*.exe","ttl":86400}'
```

**Parameters**:
- `context`: Identifier for grouping related tasks
- `selector`: Target criteria (sensor ID, tag, platform)
- `task`: The command to execute
- `ttl`: Time-to-live in seconds (default: 1 week)

**Targeting Options**:
- `sid`: Specific Sensor ID
- `tag`: All sensors with a specific tag
- `plat`: All sensors of a platform (windows, linux, macos)
- `selector`: Advanced selector expression

**Examples**:

```bash
# Task specific sensor
data='{"context":"forensics","sid":"abc123","task":"mem_map --pid 1234","ttl":3600}'

# Task all Windows sensors
data='{"context":"win-collection","plat":"windows","task":"log_get Security","ttl":7200}'

# Task sensors with specific tag
data='{"context":"incident-response","tag":"compromised","task":"history_dump","ttl":86400}'
```

### Listing Active Tasks

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=list&data={}'
```

### Capturing Task Responses

Use the `context` parameter to track responses via D&R rules.

**Example D&R Rule**:

```yaml
detect:
  op: contains
  event: RECEIPT
  path: routing/investigation_id
  value: artifact-collection

respond:
  - action: report
    name: artifact-collection-completed
  - action: output
    name: artifact-responses
```

This rule matches any response from tasks with context "artifact-collection" and forwards them to the specified output.

---

## Storage and Access

### Where Artifacts Are Stored

Collected artifacts are stored in LimaCharlie's artifact storage system with:
- Configurable retention periods (default: 30 days)
- Secure, encrypted storage
- Access controls based on organization permissions
- Unique artifact identifiers

### Accessing Collected Artifacts

**Via Web UI**:
1. Navigate to **Sensors > Artifact Collection**
2. View collected artifacts list
3. Click on artifact to view details
4. Download artifact for analysis

**Via REST API**:

```bash
# List artifacts
GET https://api.limacharlie.io/v1/orgs/{oid}/artifacts

# Download specific artifact
GET https://api.limacharlie.io/v1/orgs/{oid}/artifacts/{artifact_id}
```

### Artifact Retention

**Default Retention**: 30 days

**Configuring Retention**:
- Set retention when using Dumper extension: `retention: 30`
- Retention is measured in days
- Artifacts are automatically deleted after retention period
- Consider compliance requirements when setting retention

**Cost Considerations**:
- Artifact ingestion incurs charges based on volume
- Longer retention = higher storage costs
- Review pricing page for current rates
- Budget for expected artifact volumes

### Downloading Artifacts

**For Analysis**:
- Download via web UI or API
- Use for offline analysis
- Import into forensic tools
- Share with incident response team

**Supported Formats**:
- Files: Original format preserved
- Memory dumps: Raw memory dumps
- PCAP: Standard packet capture format
- Logs: JSON or native format

---

## Automated Collection with D&R Rules

### Overview

D&R rules enable automated artifact collection based on detection criteria. This ensures evidence is collected immediately when suspicious activity occurs.

### Collection Response Actions

**task Action**:

```yaml
- action: task
  command: artifact_get {{ .event.FILE_PATH }}
  investigation: auto-collection
```

**extension request Action (for Dumper)**:

```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 30
```

### Example: Collect Suspicious Files

```yaml
# Detect and collect suspicious executables
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: matches
      path: event/FILE_PATH
      re: .*\.(exe|dll|scr|bat|ps1)$
      case sensitive: false
    - op: or
      rules:
        - op: contains
          path: event/FILE_PATH
          value: \Downloads\
        - op: contains
          path: event/FILE_PATH
          value: \Temp\
        - op: contains
          path: event/FILE_PATH
          value: \AppData\

respond:
  - action: report
    name: suspicious-file-created
    priority: 3
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
    investigation: susp-file-{{ .event.FILE_PATH }}
    suppression:
      max_count: 1
      period: 1h
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
  - action: task
    command: file_hash --path {{ .event.FILE_PATH }}
```

**Key Points**:
- Use templating to include event data in commands
- Add suppression to prevent duplicate collection
- Include investigation ID for tracking
- Consider collecting additional context (hashes, metadata)

### Example: Memory Dump on Suspicious Process

```yaml
# Dump memory when suspicious process starts
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: matches
      path: event/COMMAND_LINE
      re: .*(powershell|cmd).*(invoke|downloadstring|webclient).*
      case sensitive: false
    - op: is
      path: event/PROCESS_IS_ELEVATED
      value: true

respond:
  - action: report
    name: suspicious-elevated-process
    priority: 5
  - action: task
    command: mem_map --pid {{ .event.PROCESS_ID }}
    investigation: proc-{{ .event.PROCESS_ID }}-map
  - action: wait
    duration: 5s
  - action: task
    command: mem_strings --pid {{ .event.PROCESS_ID }}
    investigation: proc-{{ .event.PROCESS_ID }}-strings
  - action: extension request
    extension name: ext-dumper
    extension action: request_dump
    extension request:
      target: memory
      sid: <<routing.sid>>
      retention: 7
    suppression:
      max_count: 1
      period: 24h
      is_global: false
```

**Key Points**:
- Collect multiple types of memory artifacts
- Use `wait` action between commands if needed
- Request full memory dump via Dumper extension
- Set appropriate suppression to prevent resource exhaustion

### Example: Collect Event Logs on Detection

```yaml
# Collect relevant event logs when lateral movement detected
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is
      path: event/NETWORK_ACTIVITY/DESTINATION/PORT
      value: 445  # SMB
    - op: is public address
      path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
      not: true

respond:
  - action: report
    name: potential-lateral-movement
    priority: 4
  - action: task
    command: log_get Security
    investigation: lateral-movement-logs
  - action: task
    command: artifact_get C:\Windows\System32\winevt\Logs\Security.evtx
    suppression:
      max_count: 1
      period: 6h
      is_global: false
  - action: task
    command: netstat
```

### Example: Automated PCAP Collection

```yaml
# Start packet capture when suspicious network activity detected
detect:
  event: DNS_REQUEST
  op: and
  rules:
    - op: contains
      path: event/DOMAIN_NAME
      value: .tk  # Known malicious TLD
    - op: is platform
      name: linux

respond:
  - action: report
    name: suspicious-dns-query
  - action: add tag
    tag: pcap-capture
    ttl: 300  # 5 minutes
```

**Note**: Configure PCAP rules in Artifact Collection to capture when the `pcap-capture` tag is present.

---

## Best Practices

### 1. Evidence Preservation

**Chain of Custody**:
- Document what was collected, when, and why
- Use investigation IDs to track related artifacts
- Preserve original timestamps and metadata
- Maintain audit logs of collection activities

**Integrity**:
- Calculate hashes before collection (`file_hash`)
- Verify hashes after download
- Use write-blockers for disk images
- Maintain read-only access to original artifacts

### 2. Collection Scope

**Targeted Collection**:
- Collect only what's needed for investigation
- Avoid blanket collection to control costs
- Prioritize volatile data (memory, network)
- Use file hashes to identify before collecting

**Prioritization**:
1. **Critical**: Memory dumps, running processes
2. **High**: Recent files, event logs, network connections
3. **Medium**: Configuration files, registry keys
4. **Low**: Historical logs, archived data

### 3. Resource Management

**Prevent Resource Exhaustion**:
- Use suppression in D&R rules
- Limit collection frequency
- Monitor collection volumes
- Set reasonable retention periods

**Example Suppression**:
```yaml
suppression:
  max_count: 1
  period: 1h
  is_global: false
  keys:
    - '{{ .event.FILE_PATH }}'
    - artifact-collection
```

**Performance Considerations**:
- Memory dumps can be large (equal to RAM size)
- PCAP can grow quickly on busy networks
- Event logs can be substantial
- Schedule intensive collections during off-hours

### 4. Automated vs Manual

**Use Automated Collection For**:
- Known threat patterns
- Compliance requirements
- Standard incident response procedures
- High-frequency, low-impact collections

**Use Manual Collection For**:
- Active investigations
- Resource-intensive operations
- Unusual or one-off scenarios
- Testing and validation

### 5. Cost Optimization

**Reduce Costs**:
- Use `wel://` for logs instead of `.evtx` files
- Set minimal necessary retention
- Implement collection suppression
- Filter events before collection
- Use file hashes to avoid duplicate collection

**Monitor Usage**:
- Track artifact ingestion volumes
- Review billing regularly
- Set usage alerts (via Usage Alerts extension)
- Archive to external storage if needed

### 6. Security and Privacy

**Data Protection**:
- Artifacts may contain sensitive data
- Implement role-based access controls
- Encrypt artifacts in transit and at rest
- Follow data retention policies
- Comply with privacy regulations (GDPR, etc.)

**Minimize Exposure**:
- Collect only necessary data
- Redact sensitive information where possible
- Use secure channels for artifact transfer
- Delete artifacts when no longer needed

### 7. Testing and Validation

**Before Production**:
- Test collection rules on representative systems
- Verify artifacts are complete and usable
- Check resource impact
- Validate retention and deletion
- Test download and analysis workflows

**Ongoing**:
- Periodically review collection rules
- Update based on new threat intelligence
- Verify artifacts are being collected
- Monitor for collection failures

---

## Common Collection Scenarios

### Scenario 1: Malware Incident Response

**Objective**: Collect comprehensive evidence from a compromised system.

**Step-by-Step**:

1. **Identify the compromised sensor**
2. **Collect volatile data first**:
   ```bash
   # Get running processes
   os_processes

   # Get network connections
   netstat

   # Dump process memory
   mem_map --pid <suspicious_pid>
   mem_strings --pid <suspicious_pid>
   ```

3. **Collect suspicious files**:
   ```bash
   # Hash the file first
   file_hash --path C:\path\to\malware.exe

   # Collect the file
   artifact_get C:\path\to\malware.exe
   ```

4. **Collect system artifacts**:
   ```bash
   # Event logs
   log_get Security
   log_get System

   # List recent files
   dir_list --path C:\Users\victim\Downloads
   dir_list --path C:\Users\victim\AppData\Local\Temp
   ```

5. **Full memory dump** (if warranted):
   ```yaml
   # Via D&R rule or API
   - action: extension request
     extension name: ext-dumper
     extension action: request_dump
     extension request:
       target: memory
       sid: <<routing.sid>>
       retention: 7
   ```

6. **Collect MFT for timeline**:
   ```yaml
   - action: extension request
     extension name: ext-dumper
     extension action: request_dump
     extension request:
       target: mft
       sid: <<routing.sid>>
       retention: 7
   ```

### Scenario 2: Suspicious Login Investigation

**Objective**: Investigate unusual authentication activity.

**Collection Strategy**:

```yaml
# D&R Rule: Collect on failed login attempts
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '4625'  # Failed logon
    - op: is greater than
      path: event/EVENT/System/EventID
      value: 5
      length of: true
      # Threshold activation could be used here

respond:
  - action: report
    name: multiple-failed-logins
  - action: task
    command: log_get Security
    investigation: failed-login-investigation
  - action: task
    command: netstat
  - action: task
    command: os_users
```

### Scenario 3: Data Exfiltration Detection

**Objective**: Collect evidence of potential data theft.

**Collection Strategy**:

```yaml
# D&R Rule: Large outbound transfer
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is greater than
      path: event/NETWORK_ACTIVITY/BYTES_SENT
      value: 104857600  # 100MB
    - op: is public address
      path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS

respond:
  - action: report
    name: large-data-transfer
    priority: 5
  - action: task
    command: netstat
  - action: task
    command: mem_strings --pid {{ .event.PROCESS_ID }}
  - action: task
    command: history_dump
  - action: add tag
    tag: pcap-capture  # Trigger PCAP collection
    ttl: 600
```

**PCAP Configuration**:
Configure in **Sensors > Artifact Collection** to capture when tagged.

### Scenario 4: Ransomware Response

**Objective**: Collect evidence before and after ransomware execution.

**Automated Collection Rule**:

```yaml
# Detect potential ransomware
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: matches
      path: event/COMMAND_LINE
      re: .*(vssadmin|wbadmin|bcdedit).*(delete|shadows).*
      case sensitive: false

respond:
  - action: report
    name: ransomware-indicator
    priority: 10
  # Immediate isolation
  - action: isolate network
  # Collect process info
  - action: task
    command: os_processes
  - action: task
    command: mem_map --pid {{ .event.PROCESS_ID }}
  # Collect the executable
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
  # Collect event logs
  - action: task
    command: log_get Security
  - action: task
    command: log_get System
  # Full memory dump
  - action: extension request
    extension name: ext-dumper
    extension action: request_dump
    extension request:
      target: memory
      sid: <<routing.sid>>
      retention: 30
```

### Scenario 5: Forensic Timeline Creation

**Objective**: Build a comprehensive timeline of system activity.

**Manual Collection**:

```bash
# File system timeline (MFT)
# Via Dumper extension
extension request: {target: "mft", sid: "sensor-id", retention: 7}

# Event logs
log_get Security
log_get System
log_get Application

# Recent file activity
dir_list --path C:\Users --depth 2

# Process history
history_dump

# Current state
os_processes
netstat
os_services
os_autoruns
```

### Scenario 6: Lateral Movement Detection

**Objective**: Collect artifacts showing lateral movement attempts.

**D&R Rule**:

```yaml
# Detect PsExec-like activity
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: \Admin$
      case sensitive: false
    - op: or
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: psexec
        - op: contains
          path: event/COMMAND_LINE
          value: paexec

respond:
  - action: report
    name: lateral-movement-attempt
    priority: 8
  - action: task
    command: netstat
  - action: task
    command: os_processes
  - action: task
    command: log_get Security
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
  - action: add tag
    tag: lateral-movement
    ttl: 3600
```

### Scenario 7: Browser-Based Threat

**Objective**: Collect artifacts from browser-related threats.

**Collection Commands**:

```bash
# Process memory (browser process)
mem_strings --pid <browser_pid>

# Browser history and cache
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\History
artifact_get C:\Users\*\AppData\Local\Microsoft\Edge\User Data\Default\History

# Downloads
dir_list --path C:\Users\*\Downloads

# Collect downloaded files
artifact_get C:\Users\*\Downloads\*.exe
artifact_get C:\Users\*\Downloads\*.zip
```

### Scenario 8: Linux Server Compromise

**Objective**: Collect artifacts from compromised Linux server.

**Collection Strategy**:

```bash
# Running processes
os_processes

# Network connections
netstat

# Recent commands
artifact_get /home/*/.bash_history
artifact_get /root/.bash_history

# System logs
artifact_get /var/log/auth.log
artifact_get /var/log/syslog
artifact_get /var/log/secure

# Cron jobs
artifact_get /etc/crontab
artifact_get /var/spool/cron/crontabs/*

# SSH keys
artifact_get /root/.ssh/authorized_keys
artifact_get /home/*/.ssh/authorized_keys

# Suspicious files
dir_list --path /tmp
dir_list --path /var/tmp
artifact_get /tmp/*.sh
```

### Scenario 9: Memory-Only Malware

**Objective**: Detect and collect evidence of fileless malware.

**Collection Focus**:

```bash
# Memory analysis is key for fileless malware
# 1. Identify suspicious process
os_processes

# 2. Get memory map
mem_map --pid <suspicious_pid>

# 3. Extract strings
mem_strings --pid <suspicious_pid>

# 4. Search for IOCs
mem_find_string --pid <suspicious_pid> --string "malicious-domain.com"
mem_find_string --pid <suspicious_pid> --string "192.168.1.100"

# 5. Full memory dump
# Via Dumper extension
extension request: {target: "memory", sid: "sensor-id", retention: 7}
```

### Scenario 10: Compliance Evidence Collection

**Objective**: Collect artifacts for compliance audit.

**Automated Collection Rule**:

```yaml
# Collect evidence of privileged access
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '4672'  # Special privileges assigned to new logon
    - op: contains
      path: event/EVENT/System/Channel
      value: Security

respond:
  - action: report
    name: privileged-access-event
  - action: task
    command: log_get Security
    investigation: compliance-audit
    suppression:
      max_count: 1
      period: 24h
      is_global: false
  - action: task
    command: os_processes
  - action: task
    command: os_services
```

---

## Advanced Topics

### Memory Dump Analysis

After collecting memory dumps with the Dumper extension:

1. **Download the dump** from Artifact Collection
2. **Analyze with tools** like:
   - Volatility Framework
   - Rekall
   - WinDbg
   - GDB

3. **Look for**:
   - Injected code
   - Hidden processes
   - Rootkits
   - Encryption keys
   - Network artifacts

### MFT Analysis

Master File Table dumps provide comprehensive file system timeline:

1. **Collect MFT** via Dumper extension
2. **Parse with tools**:
   - MFTExplorer
   - analyzeMFT
   - NTFS Log Tracker

3. **Analyze**:
   - File creation times
   - Modification patterns
   - Deleted files
   - File access sequences

### PCAP Analysis

Network packet captures require additional analysis:

1. **Configure PCAP rules** in Artifact Collection (Linux only)
2. **Download captures** from artifact storage
3. **Analyze with**:
   - Wireshark
   - tcpdump
   - NetworkMiner
   - Zeek (via Zeek extension)

4. **Extract**:
   - Protocols used
   - Transferred files
   - Communications timeline
   - Network indicators

### Integrating with SIEM

Forward collected artifacts to SIEM:

1. **Use Outputs** to forward detection events
2. **Include artifact metadata** in detections
3. **Create output stream** for artifact collection events
4. **Configure SIEM** to ingest from LimaCharlie

**Example Output Rule**:
```yaml
- action: output
  name: siem-artifacts
```

---

## Troubleshooting

### Common Issues

**Artifact Collection Fails**:
- Check sensor connectivity
- Verify Artifact extension is enabled
- Ensure file/path exists
- Check sensor permissions
- Verify sufficient disk space

**Memory Dumps Not Completing**:
- Large memory dumps take time
- Check available disk space on endpoint
- Verify network bandwidth
- Consider using Reliable Tasking for offline systems

**PCAP Not Capturing**:
- PCAP only works on Linux
- Verify Artifact Collection rules are configured
- Check that sensors have required tags
- Ensure network interface is accessible

**Artifacts Not Appearing**:
- Check artifact retention settings
- Verify collection commands succeeded
- Review error events on timeline
- Confirm extension subscriptions

**Cost Concerns**:
- Review artifact ingestion volumes
- Use `wel://` instead of `.evtx` files
- Implement suppression rules
- Reduce retention periods
- Filter before collection

### Getting Help

- Review sensor timeline for error events
- Check D&R rule testing output
- Enable debug logging if needed
- Contact LimaCharlie support
- Consult community resources

---

## Summary

Artifact collection is a critical capability for:
- Incident response and forensics
- Threat hunting and investigation
- Compliance and audit
- Security operations

**Key Takeaways**:
1. Enable Artifact and Reliable Tasking extensions
2. Use appropriate collection method (manual, automated, reliable)
3. Collect volatile data first (memory, processes, network)
4. Implement suppression to prevent resource exhaustion
5. Monitor costs and retention
6. Follow evidence preservation best practices
7. Test collection rules before production deployment

**Remember**:
- Artifacts incur storage costs
- Use templating in D&R rules for dynamic collection
- Leverage Reliable Tasking for offline sensors
- Preserve chain of custody
- Collect only what's needed
- Prioritize volatile data

For more information, refer to:
- LimaCharlie Artifact Extension documentation
- Reliable Tasking Extension documentation
- Endpoint Agent Commands reference
- Detection & Response rules guide
