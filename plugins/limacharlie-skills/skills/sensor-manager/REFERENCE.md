# Sensor Command Reference

Complete reference for all LimaCharlie sensor commands with syntax, parameters, and platform support.

## Table of Contents

- [File Operations](#file-operations)
- [Memory Operations](#memory-operations)
- [Process Operations](#process-operations)
- [System Information](#system-information)
- [Network Operations](#network-operations)
- [File Integrity Monitoring (FIM)](#file-integrity-monitoring-fim)
- [Exfiltration Rules](#exfiltration-rules)
- [YARA Scanning](#yara-scanning)
- [Artifacts and Logs](#artifacts-and-logs)
- [Management Operations](#management-operations)
- [macOS EPP Commands](#macos-epp-commands)
- [Platform Support Matrix](#platform-support-matrix)

---

## File Operations

### file_get

Retrieve a file from the sensor.

**Syntax:**
```
file_get --path <file_path>
```

**Parameters:**
- `--path`: Full path to the file to retrieve (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
file_get --path "C:\Windows\System32\suspicious.exe"
file_get --path "/var/log/syslog"
```

---

### file_del

Delete a file from the endpoint.

**Syntax:**
```
file_del --path <file_path>
```

**Parameters:**
- `--path`: Full path to the file to delete (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
file_del --path "C:\Temp\malware.exe"
```

**Warning:** Use with caution. This permanently deletes files.

---

### file_hash

Get the hash of a file.

**Syntax:**
```
file_hash --path <file_path>
```

**Parameters:**
- `--path`: Full path to the file to hash (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
file_hash --path "C:\Windows\System32\notepad.exe"
```

**Output:** Returns MD5, SHA1, and SHA256 hashes.

---

### file_info

Get detailed metadata about a file.

**Syntax:**
```
file_info --path <file_path>
```

**Parameters:**
- `--path`: Full path to the file (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
file_info --path "C:\Windows\System32\cmd.exe"
```

**Output:** Returns file size, timestamps, owner, permissions, and attributes.

---

### file_mov

Move or rename a file.

**Syntax:**
```
file_mov --src <source_path> --dst <destination_path>
```

**Parameters:**
- `--src`: Source file path (required)
- `--dst`: Destination file path (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
file_mov --src "C:\Temp\file.txt" --dst "C:\Archive\file.txt"
```

---

### dir_list

List the contents of a directory.

**Syntax:**
```
dir_list --path <directory_path> [--depth <max_depth>]
```

**Parameters:**
- `--path`: Full path to the directory (required)
- `--depth`: Maximum recursion depth (optional, default: 0)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
dir_list --path "C:\Users\Administrator"
dir_list --path "/home/user" --depth 2
```

---

### dir_find_hash

Find files by hash within a directory tree.

**Syntax:**
```
dir_find_hash --path <directory_path> --hash <file_hash>
```

**Parameters:**
- `--path`: Root directory to search (required)
- `--hash`: Hash to search for (MD5, SHA1, or SHA256) (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
dir_find_hash --path "C:\Windows" --hash "5d41402abc4b2a76b9719d911017c592"
```

---

## Memory Operations

### mem_map

Get the memory map of a process.

**Syntax:**
```
mem_map --pid <process_id>
```

**Parameters:**
- `--pid`: Process ID (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
mem_map --pid 1234
```

**Output:** Lists memory regions with addresses, sizes, and permissions.

---

### mem_read

Read memory from a process.

**Syntax:**
```
mem_read --pid <process_id> --base <base_address> --size <bytes>
```

**Parameters:**
- `--pid`: Process ID (required)
- `--base`: Base memory address (hex format) (required)
- `--size`: Number of bytes to read (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
mem_read --pid 1234 --base 0x7ff8a0000000 --size 1024
```

---

### mem_strings

Extract ASCII and Unicode strings from process memory.

**Syntax:**
```
mem_strings --pid <process_id>
```

**Parameters:**
- `--pid`: Process ID (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
mem_strings --pid 1234
```

---

### mem_find_string

Search for a specific string in process memory.

**Syntax:**
```
mem_find_string --pid <process_id> --string <search_string>
```

**Parameters:**
- `--pid`: Process ID (required)
- `--string`: String to search for (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
mem_find_string --pid 1234 --string "password"
```

---

### mem_handles

List all handles opened by a process (Windows only).

**Syntax:**
```
mem_handles --pid <process_id>
```

**Parameters:**
- `--pid`: Process ID (required)

**Platform Support:** Windows

**Example:**
```
mem_handles --pid 1234
```

**Output:** Lists files, registry keys, mutexes, and other handles.

---

### mem_find_handle

Find processes with a specific handle (Windows only).

**Syntax:**
```
mem_find_handle --needle <handle_name>
```

**Parameters:**
- `--needle`: Handle name or pattern to search for (required)

**Platform Support:** Windows

**Example:**
```
mem_find_handle --needle "\\Device\\NamedPipe\\malware"
```

---

## Process Operations

### os_processes

List all running processes.

**Syntax:**
```
os_processes
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
os_processes
```

**Output:** Process list with PID, name, command line, and parent process information.

---

### os_kill_process

Terminate a process.

**Syntax:**
```
os_kill_process --pid <process_id>
```

**Parameters:**
- `--pid`: Process ID to terminate (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
os_kill_process --pid 1234
```

**Warning:** Use with caution. Terminating system processes can cause instability.

---

### os_suspend

Suspend a running process.

**Syntax:**
```
os_suspend --pid <process_id>
```

**Parameters:**
- `--pid`: Process ID to suspend (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
os_suspend --pid 1234
```

---

### os_resume

Resume a suspended process.

**Syntax:**
```
os_resume --pid <process_id>
```

**Parameters:**
- `--pid`: Process ID to resume (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
os_resume --pid 1234
```

---

## System Information

### os_version

Get operating system version information.

**Syntax:**
```
os_version
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
os_version
```

**Output:** OS name, version, build number, architecture, and other system details.

---

### os_services

List all system services.

**Syntax:**
```
os_services
```

**Parameters:** None

**Platform Support:** Windows, Linux (systemd)

**Example:**
```
os_services
```

**Output:** Service name, status, startup type, and display name.

---

### os_autoruns

List autorun entries (startup programs).

**Syntax:**
```
os_autoruns
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
os_autoruns
```

**Output:** Registry keys, startup folders, scheduled tasks, and launch agents.

---

### os_drivers

List loaded kernel drivers (Windows only).

**Syntax:**
```
os_drivers
```

**Parameters:** None

**Platform Support:** Windows

**Example:**
```
os_drivers
```

**Output:** Driver name, path, base address, and size.

---

### os_packages

List installed packages.

**Syntax:**
```
os_packages
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
os_packages
```

**Output:** Package name, version, and installation date.

**Note:**
- Windows: Lists installed programs from registry
- macOS: Lists installed applications
- Linux: Lists packages from package manager (dpkg, rpm, etc.)

---

### os_users

List system user accounts (Windows only).

**Syntax:**
```
os_users
```

**Parameters:** None

**Platform Support:** Windows

**Example:**
```
os_users
```

**Output:** Username, SID, account type, and status.

---

### netstat

Get network connections.

**Syntax:**
```
netstat
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
netstat
```

**Output:** Local/remote addresses, ports, connection state, and associated process.

---

## Network Operations

### dns_resolve

Resolve a DNS name to IP addresses.

**Syntax:**
```
dns_resolve --hostname <hostname>
```

**Parameters:**
- `--hostname`: DNS name to resolve (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
dns_resolve --hostname "www.example.com"
```

**Output:** List of IP addresses (A and AAAA records).

---

### segregate_network

Isolate the sensor from the network (except LimaCharlie connection).

**Syntax:**
```
segregate_network
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
segregate_network
```

**Warning:** This will block all network traffic except the sensor's connection to LimaCharlie. Use during incident response to contain threats.

---

### rejoin_network

Restore network connectivity after isolation.

**Syntax:**
```
rejoin_network
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
rejoin_network
```

---

## File Integrity Monitoring (FIM)

### fim_add

Add a path to File Integrity Monitoring.

**Syntax:**
```
fim_add --path <path_to_monitor> [--patterns <file_patterns>]
```

**Parameters:**
- `--path`: Directory or file path to monitor (required)
- `--patterns`: File patterns to match (optional, e.g., "*.exe,*.dll")

**Platform Support:** Windows, macOS, Linux

**Example:**
```
fim_add --path "C:\Windows\System32" --patterns "*.exe,*.dll"
fim_add --path "/etc"
```

**Note:** Generates events when files are created, modified, or deleted.

---

### fim_del

Remove a path from File Integrity Monitoring.

**Syntax:**
```
fim_del --path <path_to_remove>
```

**Parameters:**
- `--path`: Path to stop monitoring (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
fim_del --path "C:\Windows\System32"
```

---

### fim_get

List all active FIM rules.

**Syntax:**
```
fim_get
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
fim_get
```

**Output:** List of monitored paths and their patterns.

---

## Exfiltration Rules

Exfiltration rules allow you to automatically capture and forward specific events or data to the LimaCharlie cloud for retention and analysis.

### exfil_add

Add an exfiltration rule.

**Syntax:**
```
exfil_add --event <event_type> [--path <path_pattern>]
```

**Parameters:**
- `--event`: Event type to exfiltrate (required)
- `--path`: Path pattern to filter (optional)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
exfil_add --event "NEW_PROCESS"
exfil_add --event "DNS_REQUEST"
exfil_add --event "FILE_CREATE" --path "C:\Users\*\Desktop\*"
```

**Common Event Types:**
- `NEW_PROCESS`: Process creation events
- `TERMINATE_PROCESS`: Process termination events
- `DNS_REQUEST`: DNS query events
- `NEW_TCP4_CONNECTION`: New TCP IPv4 connections
- `FILE_CREATE`: File creation events
- `FILE_DELETE`: File deletion events
- `CODE_IDENTITY`: Code signing information

---

### exfil_del

Delete an exfiltration rule.

**Syntax:**
```
exfil_del --event <event_type> [--path <path_pattern>]
```

**Parameters:**
- `--event`: Event type to stop exfiltrating (required)
- `--path`: Path pattern to match (optional)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
exfil_del --event "NEW_PROCESS"
```

---

### exfil_get

List all active exfiltration rules.

**Syntax:**
```
exfil_get
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
exfil_get
```

**Output:** List of active exfiltration rules with event types and patterns.

---

## YARA Scanning

### yara_scan

Scan files or memory using YARA rules.

**Syntax:**
```
yara_scan --rule-name <rule_name> --path <scan_path> [--pid <process_id>]
```

**Parameters:**
- `--rule-name`: Name of YARA rule set to use (required)
- `--path`: Directory or file path to scan (optional)
- `--pid`: Process ID to scan memory (optional)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
yara_scan --rule-name "malware_signatures" --path "C:\Users"
yara_scan --rule-name "memory_patterns" --pid 1234
```

**Note:** YARA rules must be configured in your organization before use.

---

### yara_update

Update YARA rules on the sensor.

**Syntax:**
```
yara_update --rule-name <rule_name>
```

**Parameters:**
- `--rule-name`: Name of YARA rule set to update (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
yara_update --rule-name "malware_signatures"
```

---

## Artifacts and Logs

### artifact_get

Retrieve an artifact (forensic evidence).

**Syntax:**
```
artifact_get --name <artifact_name> [--path <path>]
```

**Parameters:**
- `--name`: Artifact type to collect (required)
- `--path`: Specific path if applicable (optional)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
artifact_get --name "prefetch"
artifact_get --name "browser_history"
artifact_get --name "registry" --path "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
```

**Common Artifacts:**
- `prefetch`: Windows Prefetch files
- `registry`: Windows Registry hives or keys
- `browser_history`: Browser history and artifacts
- `event_logs`: Windows Event Logs
- `amcache`: Windows Amcache
- `shimcache`: Windows Shimcache

---

### log_get

Get Windows event logs.

**Syntax:**
```
log_get --source <log_source> [--time-start <timestamp>] [--time-end <timestamp>]
```

**Parameters:**
- `--source`: Event log source name (required)
- `--time-start`: Start timestamp (optional)
- `--time-end`: End timestamp (optional)

**Platform Support:** Windows

**Example:**
```
log_get --source "Security"
log_get --source "System" --time-start 1640000000 --time-end 1640086400
```

---

### history_dump

Dump historical telemetry from the sensor.

**Syntax:**
```
history_dump [--time-start <timestamp>] [--time-end <timestamp>]
```

**Parameters:**
- `--time-start`: Start timestamp in epoch seconds (optional)
- `--time-end`: End timestamp in epoch seconds (optional)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
history_dump --time-start 1640000000 --time-end 1640086400
```

**Note:** Returns cached telemetry data from the sensor's local buffer.

---

## Management Operations

### restart

Restart the sensor service.

**Syntax:**
```
restart
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
restart
```

**Note:** The sensor will disconnect briefly and reconnect after restart.

---

### uninstall

Uninstall the sensor from the endpoint.

**Syntax:**
```
uninstall --is-confirmed [--msi]
```

**Parameters:**
- `--is-confirmed`: Required confirmation flag
- `--msi`: Use for sensors installed via MSI (Windows only) (optional)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
uninstall --is-confirmed
uninstall --is-confirmed --msi
```

**Warning:** This will permanently remove the sensor from the endpoint.

---

### shutdown

Shutdown the sensor (temporary).

**Syntax:**
```
shutdown
```

**Parameters:** None

**Platform Support:** Windows, macOS, Linux

**Example:**
```
shutdown
```

**Note:** The sensor service will stop but remain installed. Use `restart` to bring it back online.

---

### set_performance_mode

Adjust sensor performance settings.

**Syntax:**
```
set_performance_mode --mode <performance_level>
```

**Parameters:**
- `--mode`: Performance mode (low, normal, high) (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
set_performance_mode --mode low
set_performance_mode --mode normal
set_performance_mode --mode high
```

**Performance Modes:**
- `low`: Minimal resource usage, reduced telemetry
- `normal`: Balanced mode (default)
- `high`: Maximum visibility, higher resource usage

---

### run

Execute a command on the endpoint.

**Syntax:**
```
run --command <command_to_execute> [--shell-command <shell_command>]
```

**Parameters:**
- `--command`: Command to execute (Windows: cmd.exe /c, macOS/Linux: /bin/sh -c)
- `--shell-command`: Alternative parameter for shell commands

**Platform Support:** Windows, macOS, Linux

**Example:**
```
run --command "ipconfig /all"
run --shell-command "ps aux | grep suspicious"
```

**Warning:** Use with extreme caution. This can execute arbitrary commands on the endpoint.

---

### put

Upload a file to the endpoint.

**Syntax:**
```
put --path <destination_path> --payload <file_content_base64>
```

**Parameters:**
- `--path`: Destination path on endpoint (required)
- `--payload`: Base64-encoded file content (required)

**Platform Support:** Windows, macOS, Linux

**Example:**
```
put --path "C:\Temp\script.bat" --payload "QGVjaG8gb2ZmCnBhdXNl"
```

**Warning:** Use with caution. This can write arbitrary files to the endpoint.

---

### logoff

Log off the current user session.

**Syntax:**
```
logoff
```

**Parameters:** None

**Platform Support:** Windows

**Example:**
```
logoff
```

**Warning:** This will immediately log off the active user.

---

## macOS EPP Commands

macOS sensors include built-in Endpoint Protection Platform (EPP) capabilities with anti-malware scanning.

### epp_status

Get EPP status and configuration.

**Syntax:**
```
epp_status
```

**Parameters:** None

**Platform Support:** macOS

**Example:**
```
epp_status
```

**Output:** EPP status, version, scan statistics, and configuration.

---

### epp_scan

Trigger an EPP scan.

**Syntax:**
```
epp_scan --path <scan_path>
```

**Parameters:**
- `--path`: Path to scan (required)

**Platform Support:** macOS

**Example:**
```
epp_scan --path "/Users"
epp_scan --path "/Applications"
```

---

### epp_list_exclusions

List EPP scan exclusions.

**Syntax:**
```
epp_list_exclusions
```

**Parameters:** None

**Platform Support:** macOS

**Example:**
```
epp_list_exclusions
```

---

### epp_add_exclusion

Add a path to EPP exclusions.

**Syntax:**
```
epp_add_exclusion --path <exclusion_path>
```

**Parameters:**
- `--path`: Path to exclude from scanning (required)

**Platform Support:** macOS

**Example:**
```
epp_add_exclusion --path "/Applications/TrustedApp.app"
```

---

### epp_rem_exclusion

Remove a path from EPP exclusions.

**Syntax:**
```
epp_rem_exclusion --path <exclusion_path>
```

**Parameters:**
- `--path`: Path to remove from exclusions (required)

**Platform Support:** macOS

**Example:**
```
epp_rem_exclusion --path "/Applications/TrustedApp.app"
```

---

### epp_list_quarantine

List quarantined items.

**Syntax:**
```
epp_list_quarantine
```

**Parameters:** None

**Platform Support:** macOS

**Example:**
```
epp_list_quarantine
```

**Output:** List of quarantined files with detection information.

---

## Platform Support Matrix

| Command | Windows | macOS | Linux | Chrome | Edge |
|---------|---------|-------|-------|--------|------|
| file_get | ✓ | ✓ | ✓ | - | - |
| file_del | ✓ | ✓ | ✓ | - | - |
| file_hash | ✓ | ✓ | ✓ | - | - |
| file_info | ✓ | ✓ | ✓ | - | - |
| file_mov | ✓ | ✓ | ✓ | - | - |
| dir_list | ✓ | ✓ | ✓ | - | - |
| dir_find_hash | ✓ | ✓ | ✓ | - | - |
| mem_map | ✓ | ✓ | ✓ | - | - |
| mem_read | ✓ | ✓ | ✓ | - | - |
| mem_strings | ✓ | ✓ | ✓ | - | - |
| mem_find_string | ✓ | ✓ | ✓ | - | - |
| mem_handles | ✓ | - | - | - | - |
| mem_find_handle | ✓ | - | - | - | - |
| os_processes | ✓ | ✓ | ✓ | - | - |
| os_kill_process | ✓ | ✓ | ✓ | - | - |
| os_suspend | ✓ | ✓ | ✓ | - | - |
| os_resume | ✓ | ✓ | ✓ | - | - |
| os_version | ✓ | ✓ | ✓ | ✓ | ✓ |
| os_services | ✓ | - | ✓ | - | - |
| os_autoruns | ✓ | ✓ | ✓ | - | - |
| os_drivers | ✓ | - | - | - | - |
| os_packages | ✓ | ✓ | ✓ | - | - |
| os_users | ✓ | - | - | - | - |
| netstat | ✓ | ✓ | ✓ | - | - |
| dns_resolve | ✓ | ✓ | ✓ | - | - |
| segregate_network | ✓ | ✓ | ✓ | - | - |
| rejoin_network | ✓ | ✓ | ✓ | - | - |
| fim_add | ✓ | ✓ | ✓ | - | - |
| fim_del | ✓ | ✓ | ✓ | - | - |
| fim_get | ✓ | ✓ | ✓ | - | - |
| exfil_add | ✓ | ✓ | ✓ | - | - |
| exfil_del | ✓ | ✓ | ✓ | - | - |
| exfil_get | ✓ | ✓ | ✓ | - | - |
| yara_scan | ✓ | ✓ | ✓ | - | - |
| yara_update | ✓ | ✓ | ✓ | - | - |
| artifact_get | ✓ | ✓ | ✓ | - | - |
| log_get | ✓ | - | - | - | - |
| history_dump | ✓ | ✓ | ✓ | - | - |
| restart | ✓ | ✓ | ✓ | - | - |
| uninstall | ✓ | ✓ | ✓ | - | - |
| shutdown | ✓ | ✓ | ✓ | - | - |
| set_performance_mode | ✓ | ✓ | ✓ | - | - |
| run | ✓ | ✓ | ✓ | - | - |
| put | ✓ | ✓ | ✓ | - | - |
| logoff | ✓ | - | - | - | - |
| epp_status | - | ✓ | - | - | - |
| epp_scan | - | ✓ | - | - | - |
| epp_list_exclusions | - | ✓ | - | - | - |
| epp_add_exclusion | - | ✓ | - | - | - |
| epp_rem_exclusion | - | ✓ | - | - | - |
| epp_list_quarantine | - | ✓ | - | - | - |

**Legend:**
- ✓ = Supported
- \- = Not supported

---

## Additional Resources

### Documentation
- Sensor Commands: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Commands/reference-endpoint-agent-commands.md`
- Command Examples: Search individual command documentation for detailed examples

### Related Guides
- [Deployment Guide](./DEPLOYMENT.md): Platform-specific installation instructions
- [Troubleshooting Guide](./TROUBLESHOOTING.md): Resolve sensor issues
- [Main Skill Guide](./SKILL.md): Sensor management overview

### API/SDK Resources
- REST API: https://api.limacharlie.io/static/swagger/
- Python SDK: https://github.com/refractionPOINT/python-limacharlie
- Go SDK: https://github.com/refractionPOINT/go-limacharlie

---

## Notes on Command Usage

### Best Practices

1. **Test First**: Test commands on non-production systems when possible
2. **Use Selectively**: Target specific sensors using selector expressions
3. **Document Actions**: Maintain audit trail of commands executed
4. **Review Output**: Always review command output for expected results
5. **Understand Impact**: Know what each command does before execution

### Safety Considerations

**Destructive Commands** (use with caution):
- `file_del`: Permanently deletes files
- `os_kill_process`: Terminates processes
- `uninstall`: Removes the sensor
- `run`: Can execute arbitrary commands
- `put`: Can write arbitrary files
- `logoff`: Logs off users

**Network Impact Commands**:
- `segregate_network`: Isolates endpoint from network
- Must use `rejoin_network` to restore connectivity

**Resource Intensive Commands**:
- `yara_scan`: Can consume significant CPU/disk I/O
- `history_dump`: May generate large data transfers
- `mem_strings`: Can be slow on large processes

### Command Execution

Commands can be executed via:
1. **Web Console**: Navigate to sensor, open command console
2. **API**: Use REST API endpoint `/sensors/{sid}/task`
3. **SDK**: Use language-specific SDK (Python, Go)
4. **Detection & Response Rules**: Automate command execution in response to detections

### Return to Main Guide

[← Back to Sensor Manager](./SKILL.md)
