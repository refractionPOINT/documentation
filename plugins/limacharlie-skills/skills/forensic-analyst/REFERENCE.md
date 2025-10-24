# Forensic Analyst Reference

Complete reference for LimaCharlie forensic investigation commands, LCQL syntax, event types, and forensic artifacts.

## Table of Contents

1. [Sensor Commands](#sensor-commands)
2. [LCQL Syntax Reference](#lcql-syntax-reference)
3. [Event Types](#event-types)
4. [Forensic Artifacts](#forensic-artifacts)
5. [Evidence Collection](#evidence-collection)

---

## Sensor Commands

### Process Commands

#### os_processes
List all running processes on the endpoint.

**Syntax**: `os_processes`

**Response Fields**:
- PROCESS_ID: Process ID
- FILE_PATH: Path to executable
- COMMAND_LINE: Full command line
- PARENT_PROCESS_ID: Parent PID
- USER_NAME: User account
- THREADS: Thread count
- MEMORY_USAGE: Memory consumption

**Use Cases**: Current process state, suspicious process identification, process enumeration

---

#### history_dump
Dump recent process execution history from sensor's internal cache.

**Syntax**: `history_dump`

**Use Cases**: Reconstruct attack timeline, identify deleted processes, trace execution chains, recover short-lived processes

---

### Memory Commands

#### mem_map
View memory map of a process including loaded modules and memory regions.

**Syntax**: `mem_map --pid <process_id>`

**Parameters**:
- --pid: Process ID to analyze (required)

**Use Cases**: Find unusual DLLs, identify memory regions with execute permissions, detect reflectively loaded code, find memory-only malware

---

#### mem_strings
Extract readable strings from process memory.

**Syntax**: `mem_strings --pid <process_id>`

**Parameters**:
- --pid: Process ID to analyze (required)

**Use Cases**: Find URLs/domains/IPs, discover credentials or API keys, identify configuration data, locate command strings, extract file paths

---

#### mem_find_string
Search for specific strings in process memory.

**Syntax**: `mem_find_string --pid <process_id> --string <search_string>`

**Parameters**:
- --pid: Process ID to search (required)
- --string: String to search for (required)

**Use Cases**: Search for known IOCs, find credential keywords, search for file paths, search for IP addresses

---

#### mem_read
Read specific memory regions from a process.

**Syntax**: `mem_read --pid <process_id> --base <base_address> --size <byte_count>`

**Parameters**:
- --pid: Process ID (required)
- --base: Base address in hex (e.g., 0x00400000) (required)
- --size: Number of bytes to read (required)

**Use Cases**: Extract specific code or data structures, analyze suspected injection points, retrieve configuration blocks

---

#### mem_handles
List open handles for a process (Windows only).

**Syntax**: `mem_handles --pid <process_id>`

**Parameters**:
- --pid: Process ID (required)

**Use Cases**: Identify files being accessed, find registry keys being modified, detect named pipes, locate open network sockets

---

#### mem_find_handle
Find specific handles in a process (Windows only).

**Syntax**: `mem_find_handle --pid <process_id> --path <path_to_find>`

**Parameters**:
- --pid: Process ID (required)
- --path: Path to search for (required)

**Use Cases**: Track specific file or registry access

---

### Network Commands

#### netstat
List current network connections on the endpoint.

**Syntax**: `netstat`

**Response Fields**:
- NETWORK_ACTIVITY array containing:
  - STATE: Connection state (ESTABLISHED, LISTENING, etc.)
  - PROCESS_ID: Process owning connection
  - SOURCE: IP_ADDRESS and PORT
  - DESTINATION: IP_ADDRESS and PORT

**Use Cases**: Current connection state, unusual destinations, connections from unexpected processes

---

### File Commands

#### file_info
Get detailed metadata about a file.

**Syntax**: `file_info <file_path>`

**Parameters**:
- file_path: Path to file (required)

**Response Fields**:
- FILE_PATH: Full path
- FILE_SIZE: Size in bytes
- CREATION_TIME: File creation timestamp
- MODIFICATION_TIME: Last modification timestamp
- ACCESS_TIME: Last access timestamp
- ATTRIBUTES: File attributes
- OWNER: File owner

**Use Cases**: Timestamp analysis (MACB timeline), file attribute examination, ownership verification

---

#### file_hash
Calculate cryptographic hash of a file.

**Syntax**: `file_hash <file_path>`

**Parameters**:
- file_path: Path to file (required)

**Returns**: SHA256 hash

**Use Cases**: Verify file integrity, search for known malware, track file movement, compare with threat intelligence

---

#### artifact_get
Collect a file as evidence.

**Syntax**: `artifact_get <file_path> [--investigation <id>]`

**Parameters**:
- file_path: Path to file or wildcard pattern (required)
- --investigation: Investigation ID for chain of custody (optional)

**Use Cases**: Collect suspicious files, preserve evidence, gather malware samples, collect logs

---

#### dir_list
List contents of a directory.

**Syntax**: `dir_list <directory_path> [--sort-by modified]`

**Parameters**:
- directory_path: Path to directory (required)
- --sort-by: Sort order (optional, e.g., "modified")

**Use Cases**: Enumerate files in suspicious directories, identify recently modified files, find malware drops

---

#### dir_find_hash
Find files matching a specific hash in directory tree.

**Syntax**: `dir_find_hash <directory_path> --hash <sha256_hash>`

**Parameters**:
- directory_path: Starting directory (required)
- --hash: SHA256 hash to search for (required)

**Use Cases**: Locate all copies of malicious file, find renamed malware, identify propagation paths

---

### System State Commands

#### os_autoruns
Get autorun entries (programs that run at startup).

**Syntax**: `os_autoruns`

**Response**: List of autorun locations and values

**Use Cases**: Identify persistence mechanisms, find malicious autoruns, verify startup programs

---

#### os_services
List all services on the system.

**Syntax**: `os_services`

**Use Cases**: Identify malicious services, verify service configurations, find persistence

---

#### os_packages
List installed software packages.

**Syntax**: `os_packages`

**Use Cases**: Inventory installed software, identify unauthorized installations

---

#### os_drivers
List loaded drivers (Windows only).

**Syntax**: `os_drivers`

**Use Cases**: Identify malicious drivers, rootkit detection, driver analysis

---

#### os_users
List currently logged-in users (Windows only).

**Syntax**: `os_users`

**Use Cases**: Identify active user sessions, detect unauthorized logins

---

### Log Commands

#### log_get
Retrieve Windows Event Log entries.

**Syntax**: `log_get <log_name>`

**Parameters**:
- log_name: Name of log (Security, System, Application, etc.) (required)

**Use Cases**: Collect event logs for analysis, authentication timeline, system event correlation

---

### Extension Commands

#### Memory Dump (via Dumper Extension)
Capture full system memory.

**Syntax** (via D&R rule or API):
```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 30  # days
```

**Use Cases**: APT investigation, rootkit analysis, complete system state preservation, legal evidence

---

#### MFT Dump (via Dumper Extension)
Collect Master File Table for comprehensive file system timeline.

**Syntax** (via D&R rule or API):
```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: mft
    sid: <<routing.sid>>
    retention: 30  # days
```

**Use Cases**: Complete file system timeline, deleted file records, file rename history, NTFS artifact analysis

---

## LCQL Syntax Reference

### Basic Query Structure

```
<time_range> | <platform_filter> | <event_type_filter> | <conditions> | <field_selection> | <aggregation>
```

### Time Range Syntax

**Relative Time Windows**:
```
-1h          # Last 1 hour
-6h          # Last 6 hours
-12h         # Last 12 hours
-24h         # Last 24 hours
-7d          # Last 7 days
-30d         # Last 30 days
```

**Absolute Time Windows**:
```
2024-01-01T00:00:00Z to 2024-01-31T23:59:59Z
```

### Platform Filtering

```
plat == windows          # Windows systems only
plat == linux            # Linux systems only
plat == macos            # macOS systems only
plat == chrome           # Chrome OS systems only
```

### Routing Filters

```
routing/hostname == "server-01"
routing/hostname contains "web"
routing/sid == "abc123-def456"
routing/tags contains "investigation"
routing/tags contains "production"
```

### Event Type Filtering

**Process Events**:
```
| NEW_PROCESS                  # Process creation
| EXISTING_PROCESS             # Process already running at sensor start
| TERMINATE_PROCESS            # Process termination
```

**File Events**:
```
| NEW_DOCUMENT                 # File creation
| FILE_MODIFIED                # File modification
| FILE_DELETE                  # File deletion
| FILE_TYPE_ACCESSED           # File accessed by type
| FILE_GET_REP                 # File reputation check
```

**Network Events**:
```
| NETWORK_CONNECTIONS          # Network connections (generic)
| NEW_TCP4_CONNECTION          # New IPv4 TCP connection
| TERMINATE_TCP4_CONNECTION    # IPv4 TCP connection closed
| NEW_TCP6_CONNECTION          # New IPv6 TCP connection
| TERMINATE_TCP6_CONNECTION    # IPv6 TCP connection closed
| NEW_UDP4_CONNECTION          # New IPv4 UDP connection
| TERMINATE_UDP4_CONNECTION    # IPv4 UDP connection closed
| NEW_UDP6_CONNECTION          # New IPv6 UDP connection
| TERMINATE_UDP6_CONNECTION    # IPv6 UDP connection closed
| DNS_REQUEST                  # DNS query
| NETWORK_SUMMARY              # Aggregated network data
```

**Registry Events (Windows)**:
```
| REGISTRY_WRITE               # Registry value written
| REGISTRY_CREATE              # Registry key created
| REGISTRY_DELETE              # Registry key deleted
```

**Authentication Events**:
```
| WEL                          # Windows Event Log entries
| SSH_LOGIN                    # SSH login (Linux)
| SSH_LOGOUT                   # SSH logout (Linux)
```

**System Events**:
```
| STARTING_UP                  # System booting
| SHUTTING_DOWN                # System shutting down
| CONNECTED                    # Sensor connected to LC
| DISCONNECTED                 # Sensor disconnected from LC
| VOLUME_MOUNT                 # Volume mounted
| VOLUME_UNMOUNT               # Volume unmounted
| SERVICE_CHANGE               # Service state changed
| AUTORUN_CHANGE               # Autorun entry changed
```

**Code Integrity**:
```
| CODE_IDENTITY                # Code signature verification
```

**Injection/Malware Detection**:
```
| NEW_REMOTE_THREAD            # Remote thread created
| THREAD_INJECTION             # Thread injection detected
| SENSITIVE_PROCESS_ACCESS     # Sensitive process accessed
| MODULE_MEM_DISK_MISMATCH     # Module differs from disk
```

### Conditional Operators

**Comparison**:
```
==                           # Equals
!=                           # Not equals
>                            # Greater than
<                            # Less than
>=                           # Greater than or equal
<=                           # Less than or equal
```

**String Operations**:
```
contains                     # Contains substring
starts with                  # Starts with string
ends with                    # Ends with string
matches                      # Regex match
```

**Logical Operators**:
```
and                          # Logical AND
or                           # Logical OR
not                          # Logical NOT
```

**Special Operators**:
```
is public                    # IP is public (not RFC1918)
is private                   # IP is private (RFC1918)
is lookup in resource        # Lookup in threat feed
length                       # String length
in (value1, value2)          # Value in list
not in (value1, value2)      # Value not in list
```

### Field Selection

**Common Field Paths**:
```
event/TIMESTAMP              # Event timestamp
event/FILE_PATH              # File path
event/COMMAND_LINE           # Command line
event/PROCESS_ID             # Process ID
event/PARENT_PROCESS_ID      # Parent process ID
event/PARENT/FILE_PATH       # Parent process path
event/USER_NAME              # User name
event/HASH                   # File hash (SHA256)
event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
event/NETWORK_ACTIVITY/DESTINATION/PORT
event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
event/NETWORK_ACTIVITY/SOURCE/PORT
event/NETWORK_ACTIVITY/BYTES_SENT
event/NETWORK_ACTIVITY/BYTES_RECEIVED
event/DOMAIN_NAME            # DNS domain
event/REGISTRY_KEY           # Registry key path
event/REGISTRY_VALUE         # Registry value data
event/SIGNATURE/FILE_IS_SIGNED           # Code signature status
event/SIGNATURE/CERT_ISSUER              # Certificate issuer
event/SIGNATURE/CERT_CHAIN_STATUS        # Cert validation status
routing/hostname             # Hostname
routing/sid                  # Sensor ID
routing/event_type           # Event type name
routing/tags                 # Sensor tags
plat                         # Platform
```

**Field Aliasing**:
```
| event/TIMESTAMP as time
| event/FILE_PATH as process
| event/COMMAND_LINE as cmdline
| routing/hostname as host
```

### Aggregation Functions

```
COUNT(event)                 # Count events
COUNT_UNIQUE(field)          # Count unique values
SUM(field)                   # Sum numeric field
AVG(field)                   # Average numeric field
MIN(field)                   # Minimum value
MAX(field)                   # Maximum value
```

**Group By**:
```
GROUP BY(field1 field2 ...)
```

**Having Clause** (filter aggregated results):
```
| COUNT(event) as count GROUP BY(host) | count > 100
```

### Example Queries

**Process Execution Timeline**:
```
-24h | plat == windows | NEW_PROCESS | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline event/PARENT/FILE_PATH as parent routing/hostname as host
```

**Suspicious PowerShell Commands**:
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" and (event/COMMAND_LINE contains "-enc" or event/COMMAND_LINE contains "DownloadString") | event/TIMESTAMP as time event/COMMAND_LINE as cmd routing/hostname as host
```

**Network Beaconing Detection**:
```
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/FILE_PATH as process COUNT(event) as conn_count GROUP BY(dst process) | conn_count > 50
```

**Failed Login Attempts**:
```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/TIMESTAMP as time event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as source routing/hostname as host
```

**Registry Persistence**:
```
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\CurrentVersion\\Run" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

**Unsigned Executables**:
```
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as path event/HASH as hash routing/hostname as host
```

**Hash Correlation Across Fleet**:
```
-7d | plat == windows | CODE_IDENTITY | event/HASH == "abc123..." | routing/hostname as host COUNT_UNIQUE(routing/sid) as sensor_count GROUP BY(host)
```

---

## Event Types

### Process Event Types

#### NEW_PROCESS
Process creation event.

**Key Fields**:
- PROCESS_ID: New process ID
- FILE_PATH: Path to executable
- COMMAND_LINE: Full command line
- PARENT_PROCESS_ID: Parent PID
- PARENT/FILE_PATH: Parent executable path
- USER_NAME: User account
- PROCESS_IS_ELEVATED: Elevated privileges (Windows)
- HASH: SHA256 hash of executable

---

#### TERMINATE_PROCESS
Process termination event.

**Key Fields**:
- PROCESS_ID: Terminated process ID
- FILE_PATH: Path to executable
- TIMESTAMP: Termination time

---

### File Event Types

#### NEW_DOCUMENT
File creation event.

**Key Fields**:
- FILE_PATH: Path to new file
- HASH: SHA256 hash
- ATTRIBUTES: File attributes
- TIMESTAMP: Creation time

---

#### FILE_MODIFIED
File modification event.

**Key Fields**:
- FILE_PATH: Path to modified file
- TIMESTAMP: Modification time

---

#### FILE_DELETE
File deletion event.

**Key Fields**:
- FILE_PATH: Path to deleted file
- TIMESTAMP: Deletion time

---

### Network Event Types

#### NETWORK_CONNECTIONS
Generic network connection event.

**Key Fields**:
- NETWORK_ACTIVITY/STATE: Connection state
- NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
- NETWORK_ACTIVITY/DESTINATION/PORT
- NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
- NETWORK_ACTIVITY/SOURCE/PORT
- NETWORK_ACTIVITY/BYTES_SENT
- NETWORK_ACTIVITY/BYTES_RECEIVED
- PROCESS_ID: Process owning connection
- FILE_PATH: Process executable path

---

#### DNS_REQUEST
DNS query event.

**Key Fields**:
- DOMAIN_NAME: Queried domain
- PROCESS_ID: Process making query
- TIMESTAMP: Query time

---

### Registry Event Types (Windows)

#### REGISTRY_WRITE
Registry value written.

**Key Fields**:
- REGISTRY_KEY: Full registry key path
- REGISTRY_VALUE: Value data
- PROCESS_ID: Process making change
- FILE_PATH: Process path
- TIMESTAMP: Write time

---

#### REGISTRY_CREATE
Registry key created.

**Key Fields**:
- REGISTRY_KEY: Created key path
- PROCESS_ID: Process creating key
- TIMESTAMP: Creation time

---

### Authentication Event Types

#### WEL
Windows Event Log entry.

**Key Fields**:
- EVENT/System/EventID: Event ID
- EVENT/EventData/*: Event-specific data

**Common Event IDs**:
- 4624: Successful logon
- 4625: Failed logon
- 4634: Logoff
- 4672: Special privileges assigned
- 4720: User account created
- 4726: User account deleted
- 4698: Scheduled task created
- 4699: Scheduled task deleted

---

### Code Integrity Event Types

#### CODE_IDENTITY
Code signature verification event.

**Key Fields**:
- FILE_PATH: Executable path
- HASH: SHA256 hash
- SIGNATURE/FILE_IS_SIGNED: 1 if signed, 0 if not
- SIGNATURE/CERT_ISSUER: Certificate issuer
- SIGNATURE/CERT_CHAIN_STATUS: Validation status (0 = valid)

---

### Detection Event Types

#### NEW_REMOTE_THREAD
Remote thread created (potential injection).

**Key Fields**:
- PROCESS_ID: Target process
- PARENT_PROCESS_ID: Injecting process
- TIMESTAMP: Injection time

---

#### SENSITIVE_PROCESS_ACCESS
Sensitive process accessed (e.g., lsass.exe).

**Key Fields**:
- TARGET_PROCESS_ID: Accessed process
- TARGET_PROCESS_PATH: Target path
- SOURCE_PROCESS_ID: Accessing process
- SOURCE_PROCESS_PATH: Source path

---

## Forensic Artifacts

### Windows Forensic Artifacts

#### Execution Artifacts

**Prefetch Files**:
- **Location**: `C:\Windows\Prefetch\*.pf`
- **Collection**: `artifact_get C:\Windows\Prefetch\*.pf`
- **Value**: Proof of execution, first/last run times, execution count, files accessed
- **Analysis Tools**: PECmd, WinPrefetchView

**AmCache**:
- **Location**: `C:\Windows\AppCompat\Programs\Amcache.hve`
- **Collection**: `artifact_get C:\Windows\AppCompat\Programs\Amcache.hve`
- **Value**: Program execution evidence, installation dates, SHA1 hashes
- **Analysis Tools**: AmCacheParser (Eric Zimmerman)

**Shimcache (AppCompatCache)**:
- **Location**: Registry key `SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache`
- **Collection**: `artifact_get C:\Windows\System32\config\SYSTEM`
- **Value**: Executed programs with modification times, up to 1024 entries
- **Analysis Tools**: AppCompatCacheParser (Eric Zimmerman)

**UserAssist**:
- **Location**: `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist`
- **Collection**: `artifact_get C:\Users\*\NTUSER.DAT`
- **Value**: Programs executed via Explorer, ROT13-encoded, execution count
- **Analysis Tools**: UserAssistView, Registry Explorer

**BAM/DAM (Background Activity Moderator)**:
- **Location**: `SYSTEM\CurrentControlSet\Services\bam\UserSettings`, `SYSTEM\CurrentControlSet\Services\dam\UserSettings`
- **Collection**: `artifact_get C:\Windows\System32\config\SYSTEM`
- **Value**: Recent program execution with exact timestamps (Windows 10+)

---

#### Persistence Locations

**Registry Run Keys**:
- **Locations**:
  - `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`
  - `HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce`
  - `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
  - `HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce`
- **Live Collection**: `os_autoruns`
- **LCQL**: `-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\Run"`
- **Offline Collection**: `artifact_get C:\Windows\System32\config\SOFTWARE`, `artifact_get C:\Users\*\NTUSER.DAT`

**Services**:
- **Location**: `HKLM\System\CurrentControlSet\Services`
- **Live Collection**: `os_services`
- **LCQL**: `-7d | plat == windows | SERVICE_CHANGE`
- **Offline Collection**: `artifact_get C:\Windows\System32\config\SYSTEM`

**Scheduled Tasks**:
- **Location**: `C:\Windows\System32\Tasks\*`, `C:\Windows\Tasks\*`
- **Collection**: `artifact_get C:\Windows\System32\Tasks\*`
- **WEL Event IDs**: 4698 (task created), 4699 (task deleted), 4700 (task enabled), 4701 (task disabled)
- **LCQL**: `-7d | plat == windows | WEL | event/EVENT/System/EventID == "4698"`

**Startup Folders**:
- **Locations**:
  - `C:\Users\*\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`
  - `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp`
- **Collection**: `artifact_get "C:\Users\*\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\*"`

**Winlogon Keys**:
- **Locations**:
  - `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell`
  - `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit`
  - `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Notify`
- **Collection**: `artifact_get C:\Windows\System32\config\SOFTWARE`

**AppInit DLLs**:
- **Location**: `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs`
- **Collection**: `artifact_get C:\Windows\System32\config\SOFTWARE`

**Image File Execution Options (Debugger Hijacking)**:
- **Location**: `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options`
- **Collection**: `artifact_get C:\Windows\System32\config\SOFTWARE`

---

#### Windows Event Logs

**Security Log**:
- **Location**: `C:\Windows\System32\winevt\Logs\Security.evtx`
- **Collection**: `log_get Security`, `artifact_get C:\Windows\System32\winevt\Logs\Security.evtx`
- **Key Event IDs**:
  - 4624: Successful logon
  - 4625: Failed logon
  - 4634: Logoff
  - 4647: User initiated logoff
  - 4648: Logon using explicit credentials
  - 4672: Special privileges assigned to new logon
  - 4720: User account created
  - 4722: User account enabled
  - 4724: Password reset attempt
  - 4725: User account disabled
  - 4726: User account deleted
  - 4728: Member added to security-enabled global group
  - 4732: Member added to security-enabled local group
  - 4756: Member added to security-enabled universal group

**System Log**:
- **Location**: `C:\Windows\System32\winevt\Logs\System.evtx`
- **Collection**: `log_get System`, `artifact_get C:\Windows\System32\winevt\Logs\System.evtx`
- **Value**: Service starts/stops, driver loads, system events, time changes

**Application Log**:
- **Location**: `C:\Windows\System32\winevt\Logs\Application.evtx`
- **Collection**: `log_get Application`
- **Value**: Application-specific events, errors, warnings

**Sysmon Log**:
- **Location**: `C:\Windows\System32\winevt\Logs\Microsoft-Windows-Sysmon%4Operational.evtx`
- **Collection**: `artifact_get "C:\Windows\System32\winevt\Logs\Microsoft-Windows-Sysmon%4Operational.evtx"`
- **Key Event IDs**:
  - 1: Process creation
  - 2: File creation time changed
  - 3: Network connection
  - 5: Process terminated
  - 7: Image loaded
  - 8: CreateRemoteThread
  - 10: Process access
  - 11: File created
  - 12-14: Registry events
  - 15: FileCreateStreamHash (ADS)

---

#### Browser Artifacts

**Chrome**:
- **History**: `C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\History`
- **Cookies**: `C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\Cookies`
- **Login Data**: `C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\Login Data`
- **Collection**: `artifact_get "C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\History"`

**Firefox**:
- **History**: `C:\Users\*\AppData\Roaming\Mozilla\Firefox\Profiles\*\places.sqlite`
- **Cookies**: `C:\Users\*\AppData\Roaming\Mozilla\Firefox\Profiles\*\cookies.sqlite`
- **Collection**: `artifact_get "C:\Users\*\AppData\Roaming\Mozilla\Firefox\Profiles\*\places.sqlite"`

**Edge**:
- **History**: `C:\Users\*\AppData\Local\Microsoft\Edge\User Data\Default\History`
- **Collection**: `artifact_get "C:\Users\*\AppData\Local\Microsoft\Edge\User Data\Default\History"`

**Internet Explorer**:
- **TypedURLs**: `NTUSER.DAT\Software\Microsoft\Internet Explorer\TypedURLs`
- **Collection**: `artifact_get C:\Users\*\NTUSER.DAT`

---

#### User Activity Artifacts

**Recent Files**:
- **Location**: `C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent\*`
- **Collection**: `artifact_get "C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent\*"`
- **Value**: Recently accessed files, LNK files with metadata

**Jump Lists**:
- **Automatic**: `C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations\*`
- **Custom**: `C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent\CustomDestinations\*`
- **Collection**: `artifact_get "C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent\*Destinations\*"`
- **Value**: Application-specific recently accessed items
- **Analysis Tools**: JumpListExplorer (Eric Zimmerman)

**RecentDocs (Registry)**:
- **Location**: `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs`
- **Collection**: `artifact_get C:\Users\*\NTUSER.DAT`
- **Value**: Recently opened documents by type

**Shellbags**:
- **Locations**:
  - `NTUSER.DAT\Software\Microsoft\Windows\Shell\*`
  - `UsrClass.dat\Local Settings\Software\Microsoft\Windows\Shell\*`
- **Collection**: `artifact_get C:\Users\*\NTUSER.DAT`, `artifact_get "C:\Users\*\AppData\Local\Microsoft\Windows\UsrClass.dat"`
- **Value**: Folders accessed via Explorer, network shares, USB devices
- **Analysis Tools**: ShellBagsExplorer (Eric Zimmerman)

**MUICache**:
- **Location**: `NTUSER.DAT\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache`
- **Collection**: `artifact_get C:\Users\*\NTUSER.DAT`
- **Value**: Executed applications with friendly names

---

#### Registry Hives

**SYSTEM**:
- **Location**: `C:\Windows\System32\config\SYSTEM`
- **Contains**: Computer configuration, services, drivers, network config, mounted devices

**SOFTWARE**:
- **Location**: `C:\Windows\System32\config\SOFTWARE`
- **Contains**: Installed applications, autoruns, system-wide software config

**SAM**:
- **Location**: `C:\Windows\System32\config\SAM`
- **Contains**: Local user accounts and password hashes

**SECURITY**:
- **Location**: `C:\Windows\System32\config\SECURITY`
- **Contains**: Security policies, cached credentials

**NTUSER.DAT**:
- **Location**: `C:\Users\*\NTUSER.DAT`
- **Contains**: Per-user settings, recent docs, user autoruns, UserAssist

**UsrClass.dat**:
- **Location**: `C:\Users\*\AppData\Local\Microsoft\Windows\UsrClass.dat`
- **Contains**: User shellbags, file associations

**Collection**:
```bash
artifact_get C:\Windows\System32\config\SYSTEM
artifact_get C:\Windows\System32\config\SOFTWARE
artifact_get C:\Windows\System32\config\SAM
artifact_get C:\Windows\System32\config\SECURITY
artifact_get C:\Users\*\NTUSER.DAT
artifact_get "C:\Users\*\AppData\Local\Microsoft\Windows\UsrClass.dat"
```

---

### Linux Forensic Artifacts

#### Command History

**Bash History**:
- **Location**: `/home/*/.bash_history`, `/root/.bash_history`
- **Collection**: `artifact_get /home/*/.bash_history`, `artifact_get /root/.bash_history`
- **Value**: Commands executed by users, timestamps (if HISTTIMEFORMAT set)

**Zsh History**:
- **Location**: `/home/*/.zsh_history`, `/root/.zsh_history`
- **Collection**: `artifact_get /home/*/.zsh_history`

---

#### System Logs

**Authentication Logs**:
- **Debian/Ubuntu**: `/var/log/auth.log`
- **RHEL/CentOS**: `/var/log/secure`
- **Collection**: `artifact_get /var/log/auth.log`, `artifact_get /var/log/secure`
- **Value**: SSH logins, sudo usage, authentication attempts

**System Logs**:
- **Locations**: `/var/log/syslog`, `/var/log/messages`
- **Collection**: `artifact_get /var/log/syslog`, `artifact_get /var/log/messages`

**Kernel Logs**:
- **Location**: `/var/log/kern.log`
- **Collection**: `artifact_get /var/log/kern.log`

**Cron Logs**:
- **Location**: `/var/log/cron`
- **Collection**: `artifact_get /var/log/cron`
- **Value**: Scheduled task execution

**Login Records**:
- **btmp**: Failed login attempts (`/var/log/btmp`)
- **wtmp**: Login/logout records (`/var/log/wtmp`)
- **lastlog**: Last login per user (`/var/log/lastlog`)
- **Collection**: `artifact_get /var/log/btmp`, `artifact_get /var/log/wtmp`

---

#### Persistence Locations

**Cron Jobs**:
- **Locations**:
  - `/etc/crontab`
  - `/var/spool/cron/crontabs/*`
  - `/etc/cron.d/*`
  - `/etc/cron.hourly/*`, `/etc/cron.daily/*`, `/etc/cron.weekly/*`, `/etc/cron.monthly/*`
- **Collection**: `artifact_get /etc/crontab`, `artifact_get /var/spool/cron/crontabs/*`

**Systemd Services**:
- **Locations**: `/etc/systemd/system/*`, `/lib/systemd/system/*`, `/usr/lib/systemd/system/*`
- **Collection**: `artifact_get /etc/systemd/system/*`, `artifact_get /lib/systemd/system/*`
- **Live Collection**: `os_services`

**Init Scripts**:
- **Locations**: `/etc/init.d/*`, `/etc/rc*.d/*`
- **Collection**: `artifact_get /etc/init.d/*`

**Shell Profiles**:
- **System-wide**: `/etc/profile`, `/etc/bash.bashrc`
- **Per-user**: `/home/*/.bashrc`, `/home/*/.bash_profile`, `/home/*/.profile`
- **Collection**: `artifact_get /etc/profile`, `artifact_get /home/*/.bashrc`

**SSH Configuration**:
- **Authorized Keys**: `/home/*/.ssh/authorized_keys`, `/root/.ssh/authorized_keys`
- **Known Hosts**: `/home/*/.ssh/known_hosts`
- **Collection**: `artifact_get /home/*/.ssh/authorized_keys`, `artifact_get /root/.ssh/authorized_keys`

---

#### Configuration Files

**Network Configuration**:
- **Locations**: `/etc/network/interfaces`, `/etc/sysconfig/network-scripts/*`, `/etc/netplan/*`
- **Collection**: `artifact_get /etc/network/interfaces`

**User Accounts**:
- **Locations**: `/etc/passwd`, `/etc/shadow`, `/etc/group`
- **Collection**: `artifact_get /etc/passwd`, `artifact_get /etc/shadow` (if authorized)

**Sudo Configuration**:
- **Location**: `/etc/sudoers`, `/etc/sudoers.d/*`
- **Collection**: `artifact_get /etc/sudoers`

---

### macOS Forensic Artifacts

#### Unified Logs

**Collection**: Via Artifact Collection extension with pattern `mul://<query>`

**Value**: Comprehensive system, application, user, and security events

---

#### Persistence Locations

**Launch Agents and Daemons**:
- **System-wide**: `/Library/LaunchAgents/*`, `/Library/LaunchDaemons/*`
- **Per-user**: `/Users/*/Library/LaunchAgents/*`
- **Collection**: `artifact_get /Library/LaunchAgents/*`, `artifact_get /Library/LaunchDaemons/*`

**Login Items**:
- **Location**: `/Users/*/Library/Preferences/com.apple.loginitems.plist`
- **Collection**: `artifact_get "/Users/*/Library/Preferences/com.apple.loginitems.plist"`

**Startup Items**:
- **Location**: `/Library/StartupItems/*`
- **Collection**: `artifact_get /Library/StartupItems/*`

---

#### Command History

**Locations**: `/Users/*/.bash_history`, `/Users/*/.zsh_history`, `/var/root/.bash_history`

**Collection**: `artifact_get /Users/*/.bash_history`, `artifact_get /Users/*/.zsh_history`

---

## Evidence Collection

### Chain of Custody Best Practices

**Investigation ID Tagging**:
All artifact collection and sensor commands support `--investigation` parameter:

```bash
artifact_get C:\malware.exe --investigation incident-2024-001
history_dump --investigation incident-2024-001
os_processes --investigation incident-2024-001
```

**Required Documentation**:
- Who: Analyst name and role
- What: Specific evidence collected
- When: Date and time (UTC)
- Where: Sensor ID, hostname, IP
- Why: Incident ID, case number
- How: Collection method and command

---

### Hash Verification Workflow

1. Hash file on endpoint: `file_hash C:\evidence\file.exe`
2. Document hash in evidence log
3. Collect: `artifact_get C:\evidence\file.exe --investigation INC-001`
4. Download from Artifact Collection UI
5. Verify hash matches original: `sha256sum file.exe`
6. Document verification in chain of custody

---

### Retention Configuration

**Set Retention When Using Dumper Extension**:
```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory  # or 'mft'
    sid: <<routing.sid>>
    retention: 90  # days
```

**Recommended Retention Periods**:
- Active investigations: 90-180 days
- Legal hold: Per legal requirements (often 7 years+)
- Compliance:
  - PCI DSS: 1 year minimum
  - HIPAA: 6 years minimum
  - SOX: 7 years minimum
  - GDPR: Purpose-limited

---

### Evidence Inventory Template

```
Evidence ID: EVD-001
Description: Malicious executable
Source: Sensor ABC123, Host: workstation-01, IP: 192.168.1.100
File Path: C:\Users\victim\Downloads\malware.exe
Collection Method: artifact_get
Collection Time: 2024-01-15 14:32:15 UTC
Collector: analyst@company.com
Hash (SHA256): abc123def456789...
Artifact ID: art-789xyz
Storage Location: LimaCharlie Artifact Collection
Retention: 90 days
Investigation ID: incident-2024-001
Notes: Initial infection vector, signed with invalid certificate
```

---

## Additional Resources

**For investigation scenarios**: See EXAMPLES.md

**For advanced analysis techniques**: See ADVANCED.md

**For troubleshooting**: See TROUBLESHOOTING.md

**For core methodology**: See SKILL.md
