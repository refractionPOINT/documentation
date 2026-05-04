# Reference: Endpoint Agent Commands

## Supported Commands by OS

For commands which emit a report/reply event type from the agent, the corresponding event type is provided.

| Command | Report/Reply Event | macOS | Windows | Linux | Chrome | Edge |
| --- | --- | --- | --- | --- | --- | --- |
| [artifact\_get](#artifact_get) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| deny\_tree | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [dir\_find\_hash](#dir_findhash) | [DIR\_FINDHASH\_REP](edr-events.md#dir_findhash_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [dir\_list](#dir_list) | [DIR\_LIST\_REP](edr-events.md#dir_list_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [dns\_resolve](#dns_resolve) | [DNS\_REQUEST](edr-events.md#dns_request) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [doc\_cache\_get](#doc_cache_get) | [GET\_DOCUMENT\_REP](edr-events.md#get_document_rep) | ☑️ | ☑️ |  |  |  |
| [get\_debug\_data](#get_debug_data) | [DEBUG\_DATA\_REP](edr-events.md#debug_data_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [exfil\_add](#exfil_add) | [CLOUD\_NOTIFICATION](edr-events.md#cloud_notification) | ☑️ | ☑️ | ☑️ |  |  |
| [exfil\_del](#exfil_del) | [CLOUD\_NOTIFICATION](edr-events.md#cloud_notification) | ☑️ | ☑️ | ☑️ |  |  |
| [exfil\_get](#exfil_get) | [GET\_EXFIL\_EVENT\_REP](edr-events.md#get_exfil_event_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_del](#file_del) | [FILE\_DEL\_REP](edr-events.md#file_del_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_get](#file_get) | [FILE\_GET\_REP](edr-events.md#file_get_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_hash](#file_hash) | [FILE\_HASH\_REP](edr-events.md#file_hash_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_info](#file_info) | [FILE\_INFO\_REP](edr-events.md#file_info_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_mov](#file_mov) | [FILE\_MOV\_REP](edr-events.md#file_mov_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [fim\_add](#fim_add) | [FIM\_ADD](edr-events.md#fim_add) | ☑️ | ☑️ | ☑️ |  |  |
| [fim\_del](#fim_del) | [FIM\_REMOVE](edr-events.md#fim_remove) | ☑️ | ☑️ | ☑️ |  |  |
| [fim\_get](#fim_get) | [FIM\_LIST\_REP](edr-events.md#fim_list_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [hidden\_module\_scan](#hidden_module_scan) | [HIDDEN\_MODULE\_DETECTED](edr-events.md#hidden_module_detected) |  | ☑️ | ☑️ |  |  |
| [history\_dump](#history_dump) | [HISTORY\_DUMP\_REP](edr-events.md#history_dump_rep) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [log\_get](#log_get) | N/A |  | ☑️ |  |  |  |
| logoff | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_find\_handle](#mem_find_handle) | [MEM\_FIND\_HANDLES\_REP](edr-events.md#mem_find_handles_rep) |  | ☑️ |  |  |  |
| [mem\_find\_string](#mem_find_string) | [MEM\_FIND\_STRING\_REP](edr-events.md#mem_find_string_rep) | ☑️ | ☑️ | ☑️ |  |  |
| mem\_handles | [MEM\_HANDLES\_REP](edr-events.md#mem_handles_rep) |  | ☑️ |  |  |  |
| [mem\_map](#mem_map) | [MEM\_MAP\_REP](edr-events.md#mem_map_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_read](#mem_read) | [MEM\_READ\_REP](edr-events.md#mem_read_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_strings](#mem_strings) | [MEM\_STRINGS\_REP](edr-events.md#mem_strings_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [netstat](#netstat) | [NETSTAT\_REP](edr-events.md#netstat_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_autoruns](#os_autoruns) | [OS\_AUTORUNS\_REP](edr-events.md#os_autoruns_rep) | ☑️ | ☑️ |  |  |  |
| [os\_drivers](#os_drivers) | N/A |  | ☑️ |  |  |  |
| [os\_kill\_process](#os_kill_process) | [OS\_KILL\_PROCESS\_REP](edr-events.md#os_kill_process_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_packages](#os_packages) | [OS\_PACKAGES\_REP](edr-events.md#os_packages_rep) |  | ☑️ | ☑️ | ☑️ | ☑️ |
| [os\_processes](#os_processes) | [OS\_PROCESSES\_REP](edr-events.md#os_processes_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_resume](#os_resume) | [OS\_RESUME\_REP](edr-events.md#os_resume_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_services](#os_services) | [OS\_SERVICES\_REP](edr-events.md#os_services_rep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_suspend](#os_suspend) | [OS\_SUSPEND\_REP](edr-events.md#os_suspend_rep) | ☑️ | ☑️ | ☑️ |  |  |
| os\_users | [OS\_USERS\_REP](edr-events.md#os_users_rep) |  | ☑️ |  |  |  |
| [os\_version](#os_version) | [OS\_VERSION\_REP](edr-events.md#os_version_rep) | ☑️ | ☑️ | ☑️ |  |  |
| put | [RECEIPT](edr-events.md#receipt) | ☑️ | ☑️ | ☑️ |  |  |
| [reg\_list](#reg_list) | [REGISTRY\_LIST\_REP](edr-events.md#registry_list_rep) |  | ☑️ |  |  |  |
| [rejoin\_network](#rejoin_network) | [REJOIN\_NETWORK](edr-events.md#rejoin_network) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| restart | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [run](#run) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| seal |  |  | ☑️ |  |  |  |
| [segregate\_network](#segregate_network) | [SEGREGATE\_NETWORK](edr-events.md#segregate_network) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| set\_performance\_mode | N/A | ☑️ | ☑️ | ☑️ |  |  |
| shutdown |  | ☑️ | ☑️ | ☑️ |  |  |
| uninstall | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [yara\_scan](#yara_scan) | [YARA\_DETECTION](edr-events.md#yara_detection) | ☑️ | ☑️ | ☑️ |  |  |
| yara\_update | N/A | ☑️ | ☑️ | ☑️ |  |  |
| epp\_status | [EPP\_STATUS\_REP] | ☑️ |  |  |  |  |
| [epp\_scan](#epp_scan) | [EPP\_SCAN\_REP] | ☑️ |  |  |  |  |
| [epp\_list\_exclusions](#epp_list_exclusions) | [EPP\_LIST\_EXCLUSIONS\_REP] | ☑️ |  |  |  |  |
| [epp\_add\_exclusion](#epp_add_exclusion) | [EPP\_ADD\_EXCLUSION\_REP] | ☑️ |  |  |  |  |
| [epp\_rem\_exclusion](#epp_rem_exclusion) | [EPP\_REM\_EXCLUSION\_REP] | ☑️ |  |  |  |  |
| [epp\_list\_quarantine](#epp_list_quarantine) | [EPP\_LIST\_QUARANTINE\_REP] | ☑️ |  |  |  |  |

## Command Descriptions

### artifact_get

Collect an artifact from a sensor by specifying a file path.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `file` (required): File path to collect from the sensor
- `type` (optional): Artifact type (e.g., "pcap")
- `payload_id` (optional): Idempotent payload ID for the request (auto-generated if not provided)
- `days_retention` (optional): Number of days the artifact should be retained (default: 30)
- `is_ignore_cert` (optional): If set, the sensor will ignore SSL certificate mismatches during artifact upload

**Response Event:** FILE_GET_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> artifact_get --file "C:\\Windows\\System32\\drivers\\etc\\hosts"
```

---

### dir_list

List files and directories at a specified path on the endpoint.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `dir_path` (required): Directory path to list
- `depth` (optional): Recursion depth (default: 0 = no recursion)
- `file_pattern` (optional): File pattern filter (e.g., "*.exe")

**Response Event:** DIR_LIST_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> dir_list --dir_path "C:\\Windows\\System32" --depth 1
```

**Sample Response:**

```json
{
  "event": {
    "DIRECTORY_LIST": [
      {
        "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
        "FILE_SIZE": 289792,
        "LAST_MODIFIED": 1579000000
      }
    ]
  }
}
```

---

### dir_findhash

Search for files matching a specific hash across a directory tree.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `dir_path` (required): Root directory to search
- `hash` (required): Hash value to search for (MD5, SHA1, or SHA256)
- `depth` (optional): Maximum recursion depth

**Response Event:** DIR_FINDHASH_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> dir_findhash --dir_path "/var" --hash <HASH_VALUE>
```

---

### dns_resolve

Perform DNS resolution on the endpoint to determine what DNS server responds.

**Platforms:** macOS | Windows | Linux | Chrome | Edge

**Parameters:**

- `hostname` (required): Hostname to resolve

**Response Event:** DNS_REQUEST

**Usage Example:**

```bash
limacharlie sensor task <SID> dns_resolve --hostname "example.com"
```

---

### doc_cache_get

Retrieve a previously cached document from the sensor's local cache.

**Platforms:** macOS | Windows

**Parameters:**

- `hash` (required): Hash of the cached document

**Response Event:** GET_DOCUMENT_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> doc_cache_get --hash <DOC_HASH>
```

---

### exfil_add

Add an exfiltration detection watch for specific event types and patterns.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `event` (required): Event type to monitor (e.g., "DNS_REQUEST", "NEW_PROCESS")
- `operator` (required): Comparison operator ("is", "contains", "matches", etc.)
- `path` (required): JSON path to the field to watch (e.g., "event/DOMAIN_NAME")
- `value` (required): Value or pattern to match
- `expire` (optional): TTL in seconds for the watch (default: permanent)

**Response Event:** EXFIL_ADD_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> exfil_add --event "DNS_REQUEST" --operator "contains" --path "event/DOMAIN_NAME" --value "malware" --expire 3600
```

---

### exfil_del

Remove an exfiltration detection watch by its ID.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `id` (required): Watch ID to remove (from exfil_get response)

**Response Event:** EXFIL_DEL_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> exfil_del --id <WATCH_ID>
```

---

### exfil_get

List all active exfiltration detection watches on the sensor.

**Platforms:** macOS | Windows | Linux

**Parameters:** None

**Response Event:** EXFIL_GET_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> exfil_get
```

---

### file_del

Delete a file from the endpoint filesystem.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `file_path` (required): Path to the file to delete

**Response Event:** FILE_DEL_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> file_del --file_path "/tmp/suspicious_file"
```

---

### file_get

Retrieve a file from the endpoint and upload it to LimaCharlie cloud storage.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `file_path` (required): Path to the file to retrieve

**Response Event:** FILE_GET_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> file_get --file_path "C:\\Windows\\System32\\calc.exe"
```

---

### file_hash

Calculate cryptographic hashes (MD5, SHA1, SHA256) for a file.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `file_path` (required): Path to the file to hash

**Response Event:** FILE_HASH_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> file_hash --file_path "/etc/passwd"
```

**Sample Response:**

```json
{
  "event": {
    "FILE_PATH": "/etc/passwd",
    "HASH": "abc123...",
    "MD5": "def456...",
    "SHA1": "ghi789...",
    "SHA256": "jkl012..."
  }
}
```

---

### file_info

Get detailed metadata about a file without retrieving its contents.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `file_path` (required): Path to the file

**Response Event:** FILE_INFO_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> file_info --file_path "C:\\Program Files\\app.exe"
```

**Sample Response:**

```json
{
  "event": {
    "FILE_PATH": "C:\\Program Files\\app.exe",
    "FILE_SIZE": 1048576,
    "CREATED": 1579000000,
    "MODIFIED": 1580000000,
    "ACCESSED": 1581000000
  }
}
```

---

### file_mov

Move or rename a file on the endpoint filesystem.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `src_path` (required): Source file path
- `dst_path` (required): Destination file path

**Response Event:** FILE_MOV_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> file_mov --src_path "/tmp/file.txt" --dst_path "/tmp/renamed.txt"
```

---

### fim_add

Add a File Integrity Monitoring (FIM) watch for a specific path or pattern.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `file_path` (required): Path or pattern to monitor (supports wildcards)

**Response Event:** FIM_ADD_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> fim_add --file_path "C:\\Windows\\System32\\*.dll"
```

---

### fim_del

Remove a File Integrity Monitoring watch.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `file_path` (required): Path pattern to stop monitoring

**Response Event:** FIM_REMOVE (note: event name is FIM_REMOVE, not FIM_DEL_REP)

**Usage Example:**

```bash
limacharlie sensor task <SID> fim_del --file_path "C:\\Windows\\System32\\*.dll"
```

---

### fim_get

List all active File Integrity Monitoring watches on the sensor.

**Platforms:** macOS | Windows | Linux

**Parameters:** None

**Response Event:** FIM_LIST_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> fim_get
```

---

### get_debug_data

Retrieve internal sensor debug data for troubleshooting.

**Platforms:** Windows

**Parameters:** None

**Response Event:** DEBUG_DATA_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> get_debug_data
```

---

### hidden_module_scan

Scan for hidden or stealthy modules loaded in process memory that may not appear in normal module lists.

**Platforms:** Windows

**Parameters:**

- `pid` (optional): Specific process ID to scan (default: all processes)

**Response Event:** HIDDEN_MODULE_DETECTED

**Usage Example:**

```bash
limacharlie sensor task <SID> hidden_module_scan --pid 1234
```

---

### history_dump

Export a dump of recent events from the sensor's local event cache.

**Platforms:** macOS | Windows | Linux | Chrome | Edge

**Parameters:** None

**Response Event:** HISTORY_DUMP_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> history_dump
```

---

### log_get

Retrieve Windows Event Logs or macOS Unified Logs from the endpoint.

**Platforms:** Windows (Event Logs) | macOS (Unified Logs)

**Parameters:**

- `source` (Windows required): Event log source name (e.g., "Security", "System")
- `predicate` (macOS optional): Unified log filter predicate

**Response Event:** LOG_GET_REP

**Usage Example:**

```bash
# Windows
limacharlie sensor task <SID> log_get --source "Security"

# macOS
limacharlie sensor task <SID> log_get --predicate "eventType == logEvent"
```

---

### mem_find_string

Search process memory for specific string patterns.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `pid` (required): Process ID to scan
- `strings` (required): String or list of strings to search for

**Response Event:** MEM_FIND_STRING_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> mem_find_string --pid 1234 --strings "password"
```

---

### mem_find_handle

Find handles (file, registry, process) held by a process on Windows.

**Platforms:** Windows

**Parameters:**

- `pid` (optional): Specific process ID (default: all processes)
- `needle` (optional): Handle name pattern to search for

**Response Event:** MEM_FIND_HANDLE_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> mem_find_handle --pid 1234 --needle "malware.exe"
```

---

### mem_map

Get memory map of a process showing loaded modules and memory regions.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `pid` (required): Process ID to map

**Response Event:** MEM_MAP_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> mem_map --pid 1234
```

---

### mem_read

Read raw memory from a process at a specific address.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `pid` (required): Process ID
- `base_address` (required): Memory address to read from (hex format)
- `size` (required): Number of bytes to read

**Response Event:** MEM_READ_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> mem_read --pid 1234 --base_address 0x00400000 --size 1024
```

---

### mem_strings

Extract all readable strings from a process's memory.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `pid` (required): Process ID to scan

**Response Event:** MEM_STRINGS_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> mem_strings --pid 1234
```

---

### netstat

Get current network connections on the endpoint (similar to netstat command).

**Platforms:** macOS | Windows | Linux

**Parameters:** None

**Response Event:** NETWORK_CONNECTIONS

**Usage Example:**

```bash
limacharlie sensor task <SID> netstat
```

**Sample Response:**

```json
{
  "event": {
    "NETWORK_ACTIVITY": [
      {
        "STATE": "ESTABLISHED",
        "LOCAL_ADDRESS": "192.168.1.100",
        "LOCAL_PORT": 50234,
        "REMOTE_ADDRESS": "93.184.216.34",
        "REMOTE_PORT": 443,
        "PID": 1234,
        "PROCESS": "chrome.exe"
      }
    ]
  }
}
```

---

### network_summary

Get aggregated network statistics and active connections summary.

**Platforms:** macOS | Windows | Linux

**Parameters:** None

**Response Event:** NETWORK_SUMMARY

**Usage Example:**

```bash
limacharlie sensor task <SID> network_summary
```

---

### os_kill_process

Terminate a running process.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `pid` (required): Process ID to terminate

**Response Event:** OS_KILL_PROCESS_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> os_kill_process --pid 1234
```

---

### os_packages

List installed software packages on the endpoint.

**Platforms:** Windows (via registry) | macOS (future) | Linux (future)

**Response Event:** OS_PACKAGES_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> os_packages
```

**Sample Response:**

```json
{
  "event": {
    "PACKAGES": [
      {
        "NAME": "Google Chrome",
        "VERSION": "120.0.6099.130",
        "PUBLISHER": "Google LLC"
      }
    ]
  }
}
```

---

### os_processes

Get a list of all running processes with detailed information.

**Platforms:** macOS | Windows | Linux

**Parameters:** None

**Response Event:** EXISTING_PROCESS (multiple events, one per process)

**Usage Example:**

```bash
limacharlie sensor task <SID> os_processes
```

**Sample Response:**

```json
{
  "event": {
    "PROCESS_ID": 1234,
    "PARENT_PROCESS_ID": 5678,
    "COMMAND_LINE": "C:\\Windows\\System32\\notepad.exe",
    "FILE_PATH": "C:\\Windows\\System32\\notepad.exe",
    "USER_NAME": "DOMAIN\\user"
  }
}
```

---

### os_resume

Resume a suspended process.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `pid` (required): Process ID to resume

**Response Event:** OS_RESUME_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> os_resume --pid 1234
```

---

### os_services

List all services/daemons running on the endpoint.

**Platforms:** macOS | Windows | Linux

**Parameters:** None

**Response Event:** OS_SERVICES_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> os_services
```

---

### os_suspend

Suspend (pause) a running process.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `pid` (required): Process ID to suspend

**Response Event:** OS_SUSPEND_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> os_suspend --pid 1234
```

---

### os_autoruns

List programs configured to run automatically at system startup.

**Platforms:** macOS | Windows | Linux

**Parameters:** None

**Response Event:** OS_AUTORUNS_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> os_autoruns
```

---

### os_drivers

List all loaded kernel drivers/modules.

**Platforms:** macOS | Windows | Linux

**Parameters:** None

**Response Event:** OS_DRIVERS_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> os_drivers
```

---

### os_version

Get detailed operating system version information.

**Platforms:** macOS | Windows | Linux

**Parameters:** None

**Response Event:** OS_VERSION_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> os_version
```

**Sample Response:**

```json
{
  "event": {
    "OS_NAME": "Windows 11",
    "OS_VERSION": "10.0.22631",
    "ARCHITECTURE": "x64"
  }
}
```

---

### rejoin_network

Re-enable network connectivity for a sensor that was previously isolated.

**Platforms:** macOS | Windows | Linux | Chrome | Edge

**Parameters:** None

**Response Event:** None (sensor reconnects)

**Usage Example:**

```bash
limacharlie sensor task <SID> rejoin_network
```

---

### run

Execute a command or script on the endpoint (out-of-band execution).

**Platforms:** macOS | Linux

**Parameters:**

- `command` (required): Command line to execute

**Response Event:** EXEC_OOB

**Usage Example:**

```bash
limacharlie sensor task <SID> run --command "ps aux | grep chrome"
```

---

### segregate_network

Isolate a sensor from the network (except LimaCharlie cloud connectivity).

**Platforms:** macOS | Windows | Linux | Chrome | Edge

**Parameters:** None

**Response Event:** None (sensor becomes isolated)

**Usage Example:**

```bash
limacharlie sensor task <SID> segregate_network
```

---

### yara_scan

Scan files or process memory with YARA rules.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `rule` (required): YARA rule content
- `file_path` (optional): Specific file to scan
- `pid` (optional): Specific process to scan
- `process_expr` (optional): Process name pattern to scan

**Response Event:** YARA_DETECTION

**Usage Example:**

```bash
# Scan a file
limacharlie sensor task <SID> yara_scan --file_path "C:\\suspicious.exe" --rule "rule test { strings: $a = \"malware\" condition: $a }"

# Scan process memory
limacharlie sensor task <SID> yara_scan --pid 1234 --rule "rule test { strings: $a = \"malware\" condition: $a }"
```

---

### pcap_ifaces

List available network interfaces for packet capture.

**Platforms:** macOS | Windows | Linux

**Parameters:** None

**Response Event:** PCAP_INTERFACES_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> pcap_ifaces
```

---

### pcap_start

Start capturing network packets on a specified interface.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `iface` (required): Network interface ID or name
- `max_size` (optional): Maximum capture size in MB

**Response Event:** PCAP_START_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> pcap_start --iface eth0 --max_size 100
```

---

### pcap_stop

Stop an active packet capture and upload the PCAP file.

**Platforms:** macOS | Windows | Linux

**Parameters:**

- `iface` (optional): Specific interface to stop (default: all)

**Response Event:** PCAP_STOP_REP, followed by EXPORT_COMPLETE

**Usage Example:**

```bash
limacharlie sensor task <SID> pcap_stop
```

---

### reg_list

List Windows registry keys and values at the specified path.

**Platforms:** Windows

**Parameters:**

- `<path>` (required, positional): Registry path to list. Use short hive prefixes such as `hklm`, `hku`, `hkcu`, `hkcr`, `hkcc`.

**Response Event:** REGISTRY_LIST_REP

**Usage Examples:**

```bash
limacharlie sensor task <SID> reg_list hklm\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging
limacharlie sensor task <SID> reg_list hklm\Software\Policies\Microsoft\Windows\PowerShell\ModuleLogging
limacharlie sensor task <SID> reg_list hklm\Software\Policies\Microsoft\Windows\PowerShell\Transcription
```

---

### epp_scan

Trigger an Endpoint Protection (EPP) scan on a file or directory.

**Platforms:** Windows

**Parameters:**

- `file_path` (required): Path to scan

**Response Event:** EPP_SCAN_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> epp_scan --file_path "C:\\Users\\Public"
```

---

### epp_list_exclusions

List EPP scan exclusions currently configured on the sensor.

**Platforms:** Windows

**Parameters:** None

**Response Event:** EPP_LIST_EXCLUSIONS_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> epp_list_exclusions
```

---

### epp_add_exclusion

Add a path or process to EPP scan exclusions.

**Platforms:** Windows

**Parameters:**

- `file_path` (optional): File/directory path to exclude
- `process` (optional): Process name to exclude

**Response Event:** EPP_ADD_EXCLUSION_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> epp_add_exclusion --file_path "C:\\safe_app"
```

---

### epp_rem_exclusion

Remove a path or process from EPP scan exclusions.

**Platforms:** Windows

**Parameters:**

- `file_path` (optional): File/directory path to remove from exclusions
- `process` (optional): Process name to remove from exclusions

**Response Event:** EPP_REM_EXCLUSION_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> epp_rem_exclusion --file_path "C:\\safe_app"
```

---

### epp_list_quarantine

List files currently in EPP quarantine.

**Platforms:** Windows

**Parameters:** None

**Response Event:** EPP_LIST_QUARANTINE_REP

**Usage Example:**

```bash
limacharlie sensor task <SID> epp_list_quarantine
```

---

## Command Usage Notes

**General Syntax:**

```bash
limacharlie sensor task <SENSOR_ID> <COMMAND_NAME> [--param value ...]
```

**Platform Abbreviations:**

- macOS: Apple macOS and OS X
- Windows: Microsoft Windows (7, 8, 10, 11, Server editions)
- Linux: Linux distributions (Ubuntu, CentOS, Debian, etc.)
- Chrome: Chrome browser extension sensor
- Edge: Microsoft Edge browser extension sensor

**Response Events:**
Most commands generate a response event (typically ending in `_REP`) that can be:

- Viewed in the LimaCharlie web interface under Sensor > Timeline
- Retrieved via API
- Triggered on with D&R rules

**Error Handling:**
Response events typically include an `ERROR` field:

- `ERROR: 0` indicates success
- Non-zero ERROR values indicate specific error conditions

**Permissions:**
Some commands require elevated privileges (root/administrator) on the endpoint to execute successfully.

**Timeouts:**
Commands have default timeouts (typically 30-60 seconds). Long-running operations may timeout and can be made persistent using the Reliable Tasking extension.
