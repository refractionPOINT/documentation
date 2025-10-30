# Incident Response Command and Action Reference

This document provides comprehensive reference information for all sensor commands, D&R response actions, and LCQL query syntax used in incident response operations.

## Sensor Commands

### Investigation Commands

#### Process Investigation

**os_processes**
```bash
os_processes
```
List all currently running processes on the sensor.

**history_dump**
```bash
history_dump
```
Dump recent process execution history from sensor timeline.

**mem_map**
```bash
mem_map --pid <process_id>
```
Get memory map of a specific process.

**mem_strings**
```bash
mem_strings --pid <process_id>
```
Extract printable strings from process memory.

**mem_find_string**
```bash
mem_find_string --pid <process_id> --string <search_string>
```
Search process memory for a specific string.

**mem_read**
```bash
mem_read --pid <process_id> --base <base_address> --size <bytes>
```
Read a memory region from a process.

**mem_handles** (Windows only)
```bash
mem_handles --pid <process_id>
```
List handles held by a process.

**mem_find_handle** (Windows only)
```bash
mem_find_handle --pid <process_id> --path <path_string>
```
Find handles matching a specific path.

#### File System Investigation

**dir_list**
```bash
dir_list <path>
dir_list <path> --recurse
```
List directory contents, optionally recursive.

**file_info**
```bash
file_info <file_path>
```
Get file metadata (size, timestamps, attributes).

**file_hash**
```bash
file_hash <file_path>
```
Calculate cryptographic hash of a file.

**dir_find_hash**
```bash
dir_find_hash <directory_path> --hash <hash_value>
```
Search directory for files matching a specific hash.

**hidden_module_scan**
```bash
hidden_module_scan
```
Scan for hidden modules (rootkit detection).

#### Network Investigation

**netstat**
```bash
netstat
```
Display current network connections and listening ports.

**dns_resolve**
```bash
dns_resolve <domain_name>
```
Resolve DNS name to IP addresses.

#### Windows Registry Investigation

**os_autoruns**
```bash
os_autoruns
```
List Windows autorun/persistence mechanisms.

**os_services**
```bash
os_services
```
List installed services.

**os_packages**
```bash
os_packages
```
List installed software packages.

**os_users**
```bash
os_users
```
List user accounts on the system.

#### Artifact Collection

**artifact_get**
```bash
artifact_get <file_path>
```
Collect a file for forensic analysis. File is uploaded to artifact storage.

**log_get** (Windows only)
```bash
log_get <log_name>
```
Collect Windows Event Log.
Examples:
- `log_get Security`
- `log_get System`
- `log_get Microsoft-Windows-Sysmon/Operational`

### Containment Commands

#### Network Isolation

**segregate_network**
```bash
segregate_network
```
Isolate sensor from network (stateless - does not persist across reboot).
LC connectivity is maintained.

**rejoin_network**
```bash
rejoin_network
```
Remove network isolation (for stateless segregate_network).

**Note**: For stateful network isolation that persists across reboots, use D&R actions:
- `action: isolate network`
- `action: rejoin network`

#### Process Control

**os_kill_process**
```bash
os_kill_process --pid <process_id>
```
Terminate a specific process by PID.

**deny_tree**
```bash
deny_tree <atom_id>
```
Kill a process and all its descendants using the process atom ID.
Preferred over os_kill_process for malware termination.

**os_suspend**
```bash
os_suspend --pid <process_id>
```
Suspend process execution (for analysis before termination).

**os_resume**
```bash
os_resume --pid <process_id>
```
Resume a suspended process.

#### Sensor Protection

**seal**
```bash
seal
```
Enable sensor tamper resistance. Prevents sensor modification or uninstallation.

**Note**: Use D&R action `action: unseal` to remove seal.

#### User Control

**logoff**
```bash
logoff
```
Force current user logoff.

### Remediation Commands

#### File Operations

**file_del**
```bash
file_del <file_path>
```
Delete a file from the file system.

**file_mov**
```bash
file_mov <source_path> <destination_path>
```
Move or rename a file.

#### Command Execution

**run**
```bash
run <command_line>
```
Execute arbitrary command on the sensor.

Examples:
```bash
# Windows - delete registry key
run reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v MalwareName /f

# Windows - stop service
run sc stop MalwareService

# Windows - delete service
run sc delete MalwareService

# Windows - delete scheduled task
run schtasks /delete /tn MalwareTask /f

# Linux - kill process by name
run pkill malware_process

# Linux - remove file
run rm /tmp/malware.sh
```

## D&R Response Actions

### Reporting Actions

**report**
```yaml
- action: report
  name: detection-name
  priority: 1-5
  metadata:
    author: analyst@company.com
    description: Human-readable description
    mitre: T1059.001
    remediation: Response guidance
```

Priority levels:
- 5: Critical (active malware, data exfiltration)
- 4: High (lateral movement, privilege escalation)
- 3: Medium (suspicious behavior, policy violations)
- 2: Low (anomalous activity, failed attacks)
- 1: Informational (logging, compliance)

### Containment Actions

**isolate network**
```yaml
- action: isolate network
```
Isolate sensor from network (stateful - persists across reboots).
LC connectivity is maintained via cloud-hosted relay.

**rejoin network**
```yaml
- action: rejoin network
```
Remove network isolation.

**seal**
```yaml
- action: seal
```
Enable sensor tamper resistance.

**unseal**
```yaml
- action: unseal
```
Disable sensor tamper resistance.

### Tagging Actions

**add tag**
```yaml
- action: add tag
  tag: incident-tag-name
  ttl: 86400                    # Optional: seconds until tag expires
  entire_device: false          # Optional: tag all sensors on device
```

**remove tag**
```yaml
- action: remove tag
  tag: incident-tag-name
```

### Task Execution Actions

**task**
```yaml
- action: task
  command: sensor_command
  investigation: incident-id    # Optional: group related tasks
  suppression:                  # Optional: prevent runaway execution
    is_global: false
    keys:
      - '{{ .event.PROCESS_ID }}'
    max_count: 1
    period: 5m
```

Task suppression prevents the same action from executing too frequently.
Use suppression keys to control uniqueness (e.g., per-process, per-file, per-host).

### Extension Actions

**extension request**
```yaml
- action: extension request
  extension name: extension-name
  extension action: action-name
  extension request:
    parameter1: value1
    parameter2: value2
```

Common extensions:

**Dumper Extension** (memory dumping):
```yaml
- action: extension request
  extension name: dumper
  extension action: dump
  extension request:
    sid: '{{ .routing.sid }}'
    pid: '{{ .event.PROCESS_ID }}'
```

**Artifact Collection Extension**:
Configured via Artifact Collection rules in web UI, not via D&R actions.

### Control Flow Actions

**wait**
```yaml
- action: wait
  duration: 5s
```
Pause execution before proceeding to next action.

Supported durations: `5s`, `1m`, `5m`, etc.

Use cases:
- Wait for process termination before deleting file
- Delay between containment and remediation
- Rate limiting automated responses

## LCQL Query Syntax

LCQL (LimaCharlie Query Language) enables powerful searches across telemetry data.

### Basic Query Structure

```
<time_range> | <filter> | <event_type> | <conditions> | <projections> | <aggregations>
```

### Time Ranges

```
-1h          # Last 1 hour
-24h         # Last 24 hours
-7d          # Last 7 days
-30d         # Last 30 days
```

### Platform Filters

```
plat == windows
plat == linux
plat == macos
plat == chrome
```

### Event Types

Common event types for IR:

```
NEW_PROCESS              # Process creation
NETWORK_CONNECTIONS      # Network activity
NEW_DOCUMENT             # File creation/modification
DNS_REQUEST              # DNS queries
WEL                      # Windows Event Logs
YARA_DETECTION          # YARA rule matches
CODE_IDENTITY           # Code signature verification
VOLUME_MOUNT            # Drive mounting
USER_OBSERVED           # User activity
EXISTING_PROCESS        # Process inventory
```

Use `*` to match all event types.

### Condition Operators

**Equality:**
```
event/FIELD == "value"
event/FIELD != "value"
```

**String Matching:**
```
event/FIELD contains "substring"
event/FIELD starts with "prefix"
event/FIELD ends with "suffix"
```

**Numeric Comparison:**
```
event/FIELD > 100
event/FIELD < 1000
event/FIELD >= 50
event/FIELD <= 500
event/FIELD is greater than 100
event/FIELD is less than 1000
```

**Boolean:**
```
AND
OR
```

**IP Address:**
```
event/IP_ADDRESS is public
event/IP_ADDRESS is private
```

**Existence:**
```
event/FIELD is set
event/FIELD is not set
```

### Projections

Select specific fields to display:

```
event/COMMAND_LINE as cli
event/FILE_PATH as path
routing/hostname as host
routing/sid as sensor
event/HASH as hash
event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip
event/NETWORK_ACTIVITY/DESTINATION/PORT as dst_port
```

### Aggregations

**COUNT_UNIQUE:**
```
COUNT_UNIQUE(event) as count
COUNT_UNIQUE(event/HASH) as unique_hashes
```

**GROUP BY:**
```
GROUP BY(host)
GROUP BY(path hash)
GROUP BY(parent child)
```

### Complete Query Examples

#### Find PowerShell Execution
```
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains 'powershell' | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

#### Search for Network Connections to Suspicious IP
```
-12h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS == '192.0.2.100' | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/PORT as port routing/hostname as host
```

#### Find Recent File Modifications
```
-6h | plat == windows | NEW_DOCUMENT | event/FILE_PATH contains '\AppData\' | event/FILE_PATH as path event/HASH as hash routing/hostname as host
```

#### Hunt for Lateral Movement (PsExec)
```
-24h | plat == windows | * | event/* contains 'psexec' | routing/hostname as host routing/event_type as event
```

#### Stack Process Parent-Child Relationships
```
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains 'cmd.exe' | event/PARENT/FILE_PATH as parent event/FILE_PATH as child COUNT_UNIQUE(event) as count GROUP BY(parent child)
```

#### Find Unsigned Executables
```
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as Path event/HASH as Hash COUNT_UNIQUE(Hash) as Count GROUP BY(Path Hash)
```

#### Search for Public IP Connections
```
-1h | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is public | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip routing/hostname as host
```

#### Find Failed Logon Attempts (Windows)
```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/TargetUserName as user routing/hostname as host COUNT_UNIQUE(event) as attempts GROUP BY(user host)
```

#### Hunt for Scheduled Task Creation
```
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4698" | event/EVENT/EventData/TaskName as task routing/hostname as host
```

#### Search for DNS Queries to Suspicious Domains
```
-12h | DNS_REQUEST | event/DOMAIN_NAME ends with ".ru" | event/DOMAIN_NAME as domain routing/hostname as host COUNT_UNIQUE(domain) as count GROUP BY(domain)
```

#### Find Processes with Network Activity
```
-1h | NETWORK_CONNECTIONS | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port routing/hostname as host
```

## D&R Detection Operators

### Basic Operators

**exists**
```yaml
op: exists
path: event/FIELD_NAME
```

**is**
```yaml
op: is
path: event/FIELD_NAME
value: exact-value
```

**contains**
```yaml
op: contains
path: event/FIELD_NAME
value: substring
case sensitive: false    # Optional
```

**starts with**
```yaml
op: starts with
path: event/FIELD_NAME
value: prefix
case sensitive: false
```

**ends with**
```yaml
op: ends with
path: event/FIELD_NAME
value: suffix
case sensitive: false
```

**matches**
```yaml
op: matches
path: event/FIELD_NAME
re: regex-pattern
```

### Numeric Operators

```yaml
op: is greater than
path: event/NUMERIC_FIELD
value: 100
```

```yaml
op: is lower than
path: event/NUMERIC_FIELD
value: 1000
```

### Logical Operators

**and**
```yaml
op: and
rules:
  - op: condition1
  - op: condition2
```

**or**
```yaml
op: or
rules:
  - op: condition1
  - op: condition2
```

### Network Operators

**is public address**
```yaml
op: is public address
path: event/IP_ADDRESS_FIELD
```

**is private address**
```yaml
op: is private address
path: event/IP_ADDRESS_FIELD
```

### Lookup Operators

**lookup**
```yaml
op: lookup
path: event/FIELD_NAME
resource: hive://lookup/list-name
```

Lookup against custom threat feed or list.

### Platform Operators

```yaml
op: is windows
op: is linux
op: is macos
op: is chrome
```

### Stateful Detection

**with events**
```yaml
detect:
  event: EVENT_TYPE
  op: condition
  with events:
    event: EVENT_TYPE
    op: condition
    count: 5           # Minimum occurrences
    within: 300        # Within 300 seconds
```

**with child**
```yaml
detect:
  event: NEW_PROCESS
  op: parent_condition
  with child:
    op: child_condition
    event: NEW_PROCESS
    rules:
      - op: condition
```

Detect parent-child process relationships.

**with descendant**
```yaml
detect:
  event: NEW_PROCESS
  op: ancestor_condition
  with descendant:
    op: descendant_condition
    event: NEW_PROCESS
    rules:
      - op: condition
```

Detect across multiple generations of process ancestry.

## Event Field Paths

### Common Event Fields

**Routing Fields:**
```
routing/sid                    # Sensor ID
routing/hostname              # Hostname
routing/platform              # Platform (windows, linux, macos)
routing/arch                  # Architecture (x64, x86, arm64)
routing/event_type            # Event type
routing/this                  # Atom ID of current event
```

**Process Events (NEW_PROCESS):**
```
event/PROCESS_ID              # Process ID
event/FILE_PATH               # Process executable path
event/COMMAND_LINE            # Command line arguments
event/HASH                    # File hash
event/PARENT/PROCESS_ID       # Parent PID
event/PARENT/FILE_PATH        # Parent executable path
event/USER                    # User account
```

**Network Events (NETWORK_CONNECTIONS):**
```
event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
event/NETWORK_ACTIVITY/DESTINATION/PORT
event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
event/NETWORK_ACTIVITY/SOURCE/PORT
event/NETWORK_ACTIVITY/PROTOCOL
event/NETWORK_ACTIVITY/BYTES_SENT
event/NETWORK_ACTIVITY/BYTES_RECEIVED
event/FILE_PATH               # Process making connection
event/PROCESS_ID
```

**File Events (NEW_DOCUMENT):**
```
event/FILE_PATH               # File path
event/HASH                    # File hash
event/SIZE                    # File size
event/PROCESS/*               # Process that created/modified file
```

**DNS Events (DNS_REQUEST):**
```
event/DOMAIN_NAME             # Queried domain
event/FILE_PATH               # Process making request
event/PROCESS_ID
```

**Windows Event Logs (WEL):**
```
event/EVENT/System/EventID
event/EVENT/System/Provider/@Name
event/EVENT/EventData/*
```

**YARA Detection:**
```
event/RULE_NAME               # Matched YARA rule
event/FILE_PATH               # Scanned file
event/PROCESS/*               # Process (for in-memory scans)
```

**Code Identity (CODE_IDENTITY):**
```
event/FILE_PATH
event/HASH
event/SIGNATURE/FILE_IS_SIGNED
event/SIGNATURE/CERT_ISSUER
event/SIGNATURE/CERT_SUBJECT
```

## Template Variables

In D&R response actions, use template variables to reference event data:

### Basic Variable Syntax
```
{{ .event.FIELD_NAME }}
{{ .routing.FIELD_NAME }}
```

### Common Template Variables

```yaml
# File paths
{{ .event.FILE_PATH }}

# Process information
{{ .event.PROCESS_ID }}
{{ .event.COMMAND_LINE }}

# Hashes
{{ .event.HASH }}

# Network
{{ index (index .event.NETWORK_ACTIVITY 0) "DESTINATION" "IP_ADDRESS" }}
{{ index (index .event.NETWORK_ACTIVITY 0) "DESTINATION" "PORT" }}

# Routing
{{ .routing.sid }}
{{ .routing.hostname }}
{{ .routing.this }}              # Atom ID of current event

# YARA
{{ .event.RULE_NAME }}
```

### Special Variables

**routing/this (Atom ID):**
Used with deny_tree to kill the process associated with the event:
```yaml
- action: task
  command: deny_tree <<routing/this>>
```

Note: Use `<<routing/this>>` (double angle brackets), not template syntax.

## Artifact Collection Patterns

Artifact Collection rules are configured in the web UI, not via D&R rules.

### File Patterns

**Specific files:**
```
C:\Windows\System32\config\SYSTEM
/var/log/auth.log
```

**Wildcard patterns:**
```
C:\Users\*\Downloads\*.exe
/tmp/*.sh
```

**Recursive patterns:**
```
C:\Users\**\*.dll
/home/**/.*history
```

### Windows Event Log Patterns

```
wel://Security
wel://System
wel://Application
wel://Microsoft-Windows-Sysmon/Operational
wel://Microsoft-Windows-PowerShell/Operational
```

### Network Capture Patterns (Linux only)

```
pcap://eth0
pcap://any
```

### Registry Patterns (Windows only)

```
reg://HKLM/Software/Microsoft/Windows/CurrentVersion/Run
reg://HKCU/Software/Microsoft/Windows/CurrentVersion/Run
```

## Suppression Configuration

Suppression prevents response actions from executing too frequently.

### Basic Suppression

```yaml
suppression:
  is_global: false                      # false = org-level, true = global
  max_count: 1                          # Max executions
  period: 5m                            # Time window
```

### Suppression with Keys

Use keys to control uniqueness:

**Per-process suppression:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.PROCESS_ID }}'
  max_count: 1
  period: 5m
```

**Per-file suppression:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.FILE_PATH }}'
  max_count: 1
  period: 1h
```

**Per-host suppression:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .routing.hostname }}'
  max_count: 3
  period: 24h
```

**Multi-key suppression:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .routing.hostname }}'
    - '{{ .event.FILE_PATH }}'
  max_count: 1
  period: 6h
```

## Investigation IDs

Group related sensor commands using investigation IDs:

```yaml
- action: task
  command: history_dump
  investigation: malware-incident-2024-001

- action: task
  command: os_processes
  investigation: malware-incident-2024-001

- action: task
  command: netstat
  investigation: malware-incident-2024-001
```

Benefits:
- View all related command outputs together
- Track forensic collection per incident
- Organize response activities
- Generate incident timeline

## CLI Commands

### Query Historical Data

```bash
limacharlie query --query "-24h | plat == windows | NEW_PROCESS"
```

### Test D&R Rule

```bash
limacharlie replay --rule-content rule.yaml --events test-event.json
```

### Send Sensor Command

```bash
limacharlie task --sid SENSOR_ID --command "history_dump"
```

### Export Detections

```bash
limacharlie detections --last-seconds 86400 --output detections.json
```

### List Sensors

```bash
limacharlie sensors list
```

### Get Sensor Information

```bash
limacharlie sensors get --sid SENSOR_ID
```

## Platform-Specific Notes

### Windows

**Supported commands:**
- All investigation commands
- All containment commands
- All remediation commands
- Windows-specific: mem_handles, mem_find_handle, os_autoruns, log_get

**Event sources:**
- Process creation, network, file system, DNS
- Windows Event Logs (WEL)
- Code signing verification

### Linux

**Supported commands:**
- All investigation commands (except mem_handles, mem_find_handle, log_get)
- All containment commands
- All remediation commands

**Event sources:**
- Process creation, network, file system, DNS
- Limited logging compared to Windows (consider deploying Sysmon for Linux)

**Note:** Network packet capture (PCAP) only available on Linux.

### macOS

**Supported commands:**
- Most investigation commands
- Most containment commands
- Most remediation commands

**Limitations:**
- Some memory analysis commands may have limited functionality
- Endpoint Security Framework restrictions may apply

### ChromeOS

**Supported commands:**
- Limited command set compared to other platforms
- Focus on process and network monitoring

**Limitations:**
- No file system modification commands
- Limited memory analysis
- No process termination

## Performance Considerations

### Query Performance

**Optimize LCQL queries:**
- Limit time range to minimum needed
- Use specific event types (avoid `*` when possible)
- Add platform filters early
- Use projections to reduce data returned

**Example - Unoptimized:**
```
-30d | * | event/* contains 'malware'
```

**Example - Optimized:**
```
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains 'malware' | event/FILE_PATH as path routing/hostname as host
```

### Artifact Collection

**File size limits:**
- Individual files: 100MB by default
- Configure limits per artifact pattern

**Bandwidth considerations:**
- Artifact collection uses network bandwidth
- Rate-limit collections in high-volume environments
- Schedule large collections during off-hours

### Response Action Performance

**Task execution:**
- Most sensor commands execute in <1 second
- Memory dumps and large artifact collections take longer
- Use wait actions when timing matters

**Network isolation:**
- Stateful isolation (D&R action) takes 1-2 seconds
- Stateless segregate_network is near-instantaneous

## Security Considerations

### Sensor Commands

**Destructive commands:**
- file_del, file_mov: Irreversible file operations
- deny_tree, os_kill_process: Terminate running processes
- Always verify targets before execution

**Privileged operations:**
- Sensor runs with high privileges (SYSTEM/root)
- Commands execute with sensor privileges
- Be cautious with run command

### D&R Rule Security

**Response action safety:**
- Test detection rules before adding response actions
- Use suppression to prevent runaway automation
- Start with report-only, gradually add containment
- Require human approval for destructive actions on critical systems

**Template injection:**
- Validate template variables before use in commands
- Be cautious with user-controlled input in event fields
- Use suppression keys carefully with untrusted data

## Troubleshooting Reference

### Command Execution Issues

**Sensor command not executing:**
1. Check sensor online status
2. Verify command syntax
3. Check platform compatibility
4. Review sensor timeline for errors

**Sensor command output:**
View command results in:
- Sensor timeline (real-time)
- Investigation view (if investigation ID used)
- API query results

### D&R Rule Issues

**Rule not matching:**
1. Use replay service to test
2. Enable trace mode
3. Verify event type
4. Check path syntax

**False positives:**
- Create FP rules to filter benign activity
- Add more specific conditions
- Use stateful detection (with events)

### Network Isolation Issues

**Isolation not working:**
1. Verify platform support
2. Check sensor permissions
3. Review timeline for SEGREGATE_NETWORK event
4. Test with stateless command first

**Cannot rejoin network:**
1. Ensure isolation was stateful (D&R action)
2. Use matching rejoin action (action vs. command)
3. Check sensor status

### Artifact Collection Issues

**Collection failing:**
1. Verify Artifact extension enabled
2. Check file path (case-sensitive on Linux)
3. Verify sensor file access permissions
4. Check file size limits
5. Review artifact collection quota

**Collection timeout:**
- Large files take time to upload
- Check network connectivity
- Verify bandwidth availability

## Additional Reference Material

### MITRE ATT&CK Mapping

Common tactics and techniques detected by LimaCharlie:

**Initial Access:**
- T1566: Phishing (detect malicious attachments)
- T1190: Exploit Public-Facing Application (web shell detection)

**Execution:**
- T1059: Command and Scripting Interpreter (PowerShell, cmd.exe)
- T1053: Scheduled Task/Job

**Persistence:**
- T1547: Boot or Logon Autostart Execution (os_autoruns)
- T1543: Create or Modify System Process (services)

**Privilege Escalation:**
- T1068: Exploitation for Privilege Escalation
- T1055: Process Injection (memory analysis)

**Defense Evasion:**
- T1070: Indicator Removal (file deletion, log clearing)
- T1027: Obfuscated Files or Information

**Credential Access:**
- T1003: OS Credential Dumping
- T1110: Brute Force (failed logon detection)

**Discovery:**
- T1082: System Information Discovery
- T1083: File and Directory Discovery

**Lateral Movement:**
- T1021: Remote Services (PsExec, RDP)
- T1570: Lateral Tool Transfer

**Collection:**
- T1560: Archive Collected Data
- T1005: Data from Local System

**Exfiltration:**
- T1041: Exfiltration Over C2 Channel (large data transfers)
- T1048: Exfiltration Over Alternative Protocol

### Event Type Reference

Complete list of event types available for detection and querying:

```
CODE_IDENTITY
CONNECTED
DESYNC_EXEC
DISCONNECTED
DNS_REQUEST
EXISTING_PROCESS
FILE_GET_REP
FILE_TYPE_ACCESSED
HIDDEN_MODULE_DETECTED
HTTP_REQUEST
MODULE_LOAD
MODULE_MEM_DISK_MISMATCH
NETWORK_CONNECTIONS
NETWORK_SUMMARY
NEW_DOCUMENT
NEW_PROCESS
NEW_REMOTE_THREAD
OS_AUTORUNS_REP
OS_DRIVERS_REP
OS_KILL_PROCESS_REP
OS_PACKAGES_REP
OS_PROCESSES_REP
OS_RESUME_REP
OS_SERVICES_REP
OS_SUSPEND_REP
OS_USERS_REP
PARENT_UNKNOWN_PROCESS
RECEIPT
RECON_BURST
REGISTRY_MODIFICATION
REMOTE_PROCESS_HANDLE
RENAME_PROCESS
RESUME
SELF_TEST_EVENT
SERVICE_CHANGE
SHUTTING_DOWN
STARTING_UP
SUSPEND
SYNC
TERMINATE_PROCESS
USER_OBSERVED
VOLUME_MOUNT
WEL
YARA_DETECTION
```

### Time Format Reference

**D&R wait durations:**
```
5s      # 5 seconds
1m      # 1 minute
5m      # 5 minutes
1h      # 1 hour
```

**LCQL time ranges:**
```
-1h     # Last hour
-24h    # Last 24 hours
-7d     # Last 7 days
-30d    # Last 30 days
```

**Tag TTL (seconds):**
```
300     # 5 minutes
3600    # 1 hour
86400   # 24 hours
604800  # 7 days
```

### Hash Formats

LimaCharlie supports multiple hash formats:

```
MD5
SHA1
SHA256 (default)
```

Event field: `event/HASH` typically contains SHA256.

### Size and Limit Reference

**Artifact collection:**
- Default max file size: 100MB
- Configurable per pattern

**Query results:**
- API query limits apply
- Use pagination for large result sets

**Timeline retention:**
- Default: 1 year historical data
- Configurable per organization

**D&R rule limits:**
- Practical limit: ~1000 rules per organization
- Consider rule complexity and performance

This reference provides complete details for all commands, actions, and syntax used in LimaCharlie incident response operations.
