# Artifact Collection Examples

10 detailed investigation scenarios with complete commands and strategies.

## Table of Contents

1. [Malware Incident Response](#scenario-1-malware-incident-response)
2. [Suspicious Login Investigation](#scenario-2-suspicious-login-investigation)
3. [Data Exfiltration Detection](#scenario-3-data-exfiltration-detection)
4. [Ransomware Response](#scenario-4-ransomware-response)
5. [Forensic Timeline Creation](#scenario-5-forensic-timeline-creation)
6. [Lateral Movement Detection](#scenario-6-lateral-movement-detection)
7. [Browser-Based Threat](#scenario-7-browser-based-threat)
8. [Linux Server Compromise](#scenario-8-linux-server-compromise)
9. [Memory-Only Malware](#scenario-9-memory-only-malware)
10. [Compliance Evidence Collection](#scenario-10-compliance-evidence-collection)

---

## Scenario 1: Malware Incident Response

**Objective**: Collect comprehensive evidence from a compromised system.

**When to Use**: Alert triggered on suspicious file or process execution.

### Step-by-Step Collection

**Step 1: Collect volatile data first**

Volatile data disappears when the system powers off or reboots. Collect this immediately.

```bash
# Get running processes
os_processes

# Get network connections
netstat

# Get logged-in users
os_users

# Dump process memory for suspicious process
mem_map --pid <suspicious_pid>
mem_strings --pid <suspicious_pid>
```

**Step 2: Collect suspicious files**

Always hash before collecting to verify and avoid duplicates.

```bash
# Hash the file first
file_hash --path C:\path\to\malware.exe

# Get file metadata
file_info --path C:\path\to\malware.exe

# Collect the file
artifact_get C:\path\to\malware.exe
```

**Step 3: Collect system artifacts**

```bash
# Windows Event logs
log_get Security
log_get System
log_get Application

# Sysmon logs (if installed)
log_get Microsoft-Windows-Sysmon/Operational

# List recent files in suspicious locations
dir_list --path C:\Users\victim\Downloads
dir_list --path C:\Users\victim\AppData\Local\Temp
dir_list --path C:\Windows\Temp
```

**Step 4: Collect historical events**

```bash
# Dump cached events from sensor
history_dump
```

**Step 5: Full memory dump (if warranted)**

Via D&R rule or REST API:

```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 7
```

**Step 6: Collect MFT for timeline analysis**

```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: mft
    sid: <<routing.sid>>
    retention: 7
```

### Automated D&R Rule

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: matches
      path: event/FILE_PATH
      re: .*\\(temp|downloads)\\.*\.(exe|dll|scr)$
      case sensitive: false
    - op: exists
      path: event/HASH

respond:
  - action: report
    name: malware-execution-detected
    priority: 8
  # Collect the executable
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
    investigation: malware-{{ .event.HASH }}
  # Get process memory
  - action: task
    command: mem_map --pid {{ .event.PROCESS_ID }}
  - action: task
    command: mem_strings --pid {{ .event.PROCESS_ID }}
  # Collect context
  - action: task
    command: netstat
  - action: task
    command: os_processes
```

---

## Scenario 2: Suspicious Login Investigation

**Objective**: Investigate unusual authentication activity.

**When to Use**: Failed login attempts, unusual login times, or suspicious user activity.

### Manual Investigation

```bash
# Collect Security logs
log_get Security

# Check current users
os_users

# Check network connections
netstat

# Get current processes
os_processes

# Check running services
os_services

# Collect authentication logs (Linux)
artifact_get /var/log/auth.log
artifact_get /var/log/secure
```

### Automated Collection

```yaml
# D&R Rule: Collect on multiple failed login attempts
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '4625'  # Failed logon
    - op: exists
      path: event/EVENT/EventData/TargetUserName

respond:
  - action: report
    name: failed-login-attempt
    priority: 5
  - action: task
    command: log_get Security
    investigation: failed-login-{{ .event.EVENT.EventData.TargetUserName }}
    suppression:
      max_count: 1
      period: 1h
      is_global: false
      keys:
        - '{{ .event.EVENT.EventData.TargetUserName }}'
  - action: task
    command: netstat
  - action: task
    command: os_users
  - action: task
    command: os_processes
```

### Successful Privileged Login

```yaml
# Collect on successful privileged login
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
    name: privileged-login
    priority: 3
  - action: task
    command: log_get Security
    investigation: privileged-access
    suppression:
      max_count: 1
      period: 6h
      is_global: false
  - action: task
    command: os_processes
  - action: task
    command: netstat
```

---

## Scenario 3: Data Exfiltration Detection

**Objective**: Collect evidence of potential data theft.

**When to Use**: Large outbound data transfers, suspicious network activity, or unauthorized data access.

### Automated Collection Rule

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
    priority: 8
  # Get network state
  - action: task
    command: netstat
  # Get process memory
  - action: task
    command: mem_strings --pid {{ .event.PROCESS_ID }}
    investigation: exfil-{{ .event.PROCESS_ID }}
  # Get historical events
  - action: task
    command: history_dump
  # Trigger PCAP collection (Linux only)
  - action: add tag
    tag: pcap-capture
    ttl: 600  # 10 minutes
  # Get process info
  - action: task
    command: os_processes
```

### PCAP Configuration

Configure in **Sensors > Artifact Collection**:

```yaml
interface: eth0
filter: ""  # Capture all traffic
trigger: tag==pcap-capture
duration: 600  # 10 minutes
```

### Manual Investigation

```bash
# Check network connections
netstat

# Get process list
os_processes

# Check for suspicious files
dir_list --path C:\Users\*\Documents
dir_list --path C:\Users\*\Desktop

# Collect browser history
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\History
artifact_get C:\Users\*\AppData\Local\Microsoft\Edge\User Data\Default\History

# Check recent file modifications
dir_list --path C:\Users\*\Recent
```

---

## Scenario 4: Ransomware Response

**Objective**: Collect evidence before and after ransomware execution.

**When to Use**: Ransomware indicators detected (shadow copy deletion, mass file encryption).

### Automated Collection Rule

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
    investigation: ransomware-{{ .routing.sid }}
  - action: task
    command: mem_map --pid {{ .event.PROCESS_ID }}
  # Collect the executable
  - action: task
    command: file_hash --path {{ .event.FILE_PATH }}
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
  # Collect event logs
  - action: task
    command: log_get Security
  - action: task
    command: log_get System
  - action: task
    command: log_get Application
  # Full memory dump
  - action: extension request
    extension name: ext-dumper
    extension action: request_dump
    extension request:
      target: memory
      sid: <<routing.sid>>
      retention: 30
  # Get autoruns for persistence
  - action: task
    command: os_autoruns
```

### Mass File Encryption Detection

```yaml
# Detect rapid file modifications
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: matches
      path: event/FILE_PATH
      re: .*\.(encrypted|locked|crypto|crypt)$
      case sensitive: false

respond:
  - action: report
    name: file-encryption-detected
    priority: 10
  - action: isolate network
  - action: task
    command: os_processes
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
    suppression:
      max_count: 10
      period: 1h
      is_global: false
```

### Manual Response

```bash
# Get all running processes
os_processes

# Check for suspicious processes
os_autoruns

# Collect ransom notes
artifact_get C:\Users\*\Desktop\*.txt
artifact_get C:\Users\*\Desktop\*.html

# Collect event logs
log_get Security
log_get System
log_get Application

# Get network connections
netstat
```

---

## Scenario 5: Forensic Timeline Creation

**Objective**: Build a comprehensive timeline of system activity.

**When to Use**: Post-incident analysis, compliance audit, or detailed investigation.

### Manual Collection

```bash
# File system timeline (MFT) - Windows
# Via Dumper extension (use REST API or D&R rule)
extension request: {target: "mft", sid: "sensor-id", retention: 7}

# Event logs
log_get Security
log_get System
log_get Application
log_get Microsoft-Windows-Sysmon/Operational
log_get Microsoft-Windows-PowerShell/Operational

# Recent file activity
dir_list --path C:\Users --depth 2
dir_list --path C:\Windows\Temp --depth 1
dir_list --path C:\ProgramData --depth 2

# Process history
history_dump

# Current state
os_processes
netstat
os_services
os_autoruns

# Registry (Windows)
artifact_get C:\Windows\System32\config\SYSTEM
artifact_get C:\Windows\System32\config\SOFTWARE
artifact_get C:\Windows\System32\config\SAM
```

### Linux Timeline Collection

```bash
# System logs
artifact_get /var/log/syslog
artifact_get /var/log/auth.log
artifact_get /var/log/secure
artifact_get /var/log/messages

# Command history
artifact_get /root/.bash_history
artifact_get /home/*/.bash_history

# File activity
dir_list --path /tmp --depth 2
dir_list --path /var/tmp --depth 2
dir_list --path /home --depth 2

# Current state
os_processes
netstat
os_services
```

### Automated Timeline Collection

```yaml
# Triggered by investigation tag
detect:
  event: STARTING
  op: and
  rules:
    - op: is tagged
      tag: timeline-collection

respond:
  - action: task
    command: log_get Security
  - action: task
    command: log_get System
  - action: task
    command: history_dump
  - action: task
    command: os_processes
  - action: task
    command: netstat
  - action: task
    command: os_autoruns
  - action: extension request
    extension name: ext-dumper
    extension action: request_dump
    extension request:
      target: mft
      sid: <<routing.sid>>
      retention: 30
```

---

## Scenario 6: Lateral Movement Detection

**Objective**: Collect artifacts showing lateral movement attempts.

**When to Use**: PsExec activity, remote execution, or pass-the-hash attacks detected.

### PsExec Detection

```yaml
# Detect PsExec-like activity
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: or
      rules:
        - op: contains
          path: event/FILE_PATH
          value: \Admin$
          case sensitive: false
        - op: contains
          path: event/FILE_PATH
          value: psexesvc
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
    priority: 9
  # Network state
  - action: task
    command: netstat
    investigation: lateral-movement
  # Process state
  - action: task
    command: os_processes
  # Event logs
  - action: task
    command: log_get Security
  - action: task
    command: log_get System
  # Collect the executable
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
  # Tag for monitoring
  - action: add tag
    tag: lateral-movement
    ttl: 3600
```

### SMB Lateral Movement

```yaml
# Detect remote file execution via SMB
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
    name: potential-lateral-movement-smb
    priority: 6
  - action: task
    command: netstat
  - action: task
    command: log_get Security
    suppression:
      max_count: 1
      period: 6h
      is_global: false
  - action: task
    command: os_processes
```

### Manual Investigation

```bash
# Check network connections
netstat

# Get processes
os_processes

# Collect Security logs
log_get Security

# Check for remote access
artifact_get C:\Windows\System32\winevt\Logs\Microsoft-Windows-TerminalServices-LocalSessionManager%4Operational.evtx

# Check scheduled tasks
os_autoruns
```

---

## Scenario 7: Browser-Based Threat

**Objective**: Collect artifacts from browser-related threats.

**When to Use**: Malicious downloads, browser exploitation, or credential theft via browser.

### Manual Collection

```bash
# Process memory (browser process)
# First, find browser PID with os_processes
mem_strings --pid <browser_pid>
mem_find_string --pid <browser_pid> --string "http"

# Browser history and cache (Chrome)
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\History
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\Cookies
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\Login Data

# Browser history and cache (Edge)
artifact_get C:\Users\*\AppData\Local\Microsoft\Edge\User Data\Default\History
artifact_get C:\Users\*\AppData\Local\Microsoft\Edge\User Data\Default\Cookies

# Browser history (Firefox)
artifact_get C:\Users\*\AppData\Roaming\Mozilla\Firefox\Profiles\*\places.sqlite

# Downloads
dir_list --path C:\Users\*\Downloads
artifact_get C:\Users\*\Downloads\*.exe
artifact_get C:\Users\*\Downloads\*.zip
artifact_get C:\Users\*\Downloads\*.js
```

### Automated Collection

```yaml
# Collect on browser download
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: \Downloads\
      case sensitive: false
    - op: matches
      path: event/FILE_PATH
      re: .*\.(exe|msi|zip|rar|js|vbs|hta)$
      case sensitive: false

respond:
  - action: report
    name: browser-download-detected
    priority: 5
  # Hash first
  - action: task
    command: file_hash --path {{ .event.FILE_PATH }}
  # Collect file
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
    investigation: browser-download
    suppression:
      max_count: 1
      period: 1h
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
```

---

## Scenario 8: Linux Server Compromise

**Objective**: Collect artifacts from compromised Linux server.

**When to Use**: Suspicious activity on Linux systems, unauthorized access, or malware detection.

### Manual Collection

```bash
# Running processes
os_processes

# Network connections
netstat

# Logged-in users
os_users

# Recent commands
artifact_get /home/*/.bash_history
artifact_get /root/.bash_history
artifact_get /home/*/.zsh_history

# System logs
artifact_get /var/log/auth.log
artifact_get /var/log/syslog
artifact_get /var/log/secure
artifact_get /var/log/messages

# Cron jobs
artifact_get /etc/crontab
artifact_get /var/spool/cron/crontabs/*
artifact_get /etc/cron.d/*

# SSH keys and configs
artifact_get /root/.ssh/authorized_keys
artifact_get /home/*/.ssh/authorized_keys
artifact_get /etc/ssh/sshd_config

# Suspicious files in temp
dir_list --path /tmp
dir_list --path /var/tmp
dir_list --path /dev/shm
artifact_get /tmp/*.sh
artifact_get /tmp/*.elf

# Web server logs (if applicable)
artifact_get /var/log/apache2/access.log
artifact_get /var/log/nginx/access.log

# Check for persistence
os_services
os_autoruns
artifact_get /etc/systemd/system/*.service
```

### Automated Collection

```yaml
# Detect suspicious SSH activity
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: linux
    - op: contains
      path: event/COMMAND_LINE
      value: sshd

respond:
  - action: task
    command: artifact_get /var/log/auth.log
    investigation: ssh-activity
    suppression:
      max_count: 1
      period: 1h
      is_global: false
  - action: task
    command: netstat
  - action: task
    command: os_users
```

### Webshell Detection

```yaml
# Detect potential webshell
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: is platform
      name: linux
    - op: or
      rules:
        - op: contains
          path: event/FILE_PATH
          value: /var/www/
        - op: contains
          path: event/FILE_PATH
          value: /usr/share/nginx/
    - op: matches
      path: event/FILE_PATH
      re: .*\.(php|jsp|asp|aspx)$
      case sensitive: false

respond:
  - action: report
    name: potential-webshell
    priority: 9
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
  - action: task
    command: file_hash --path {{ .event.FILE_PATH }}
  - action: task
    command: os_processes
```

---

## Scenario 9: Memory-Only Malware

**Objective**: Detect and collect evidence of fileless malware.

**When to Use**: Suspicious process with no file on disk, PowerShell/script-based attacks, or reflective DLL injection.

### Manual Investigation

```bash
# 1. Identify suspicious process
os_processes

# 2. Get memory map
mem_map --pid <suspicious_pid>

# 3. Extract strings
mem_strings --pid <suspicious_pid>

# 4. Search for IOCs
mem_find_string --pid <suspicious_pid> --string "malicious-domain.com"
mem_find_string --pid <suspicious_pid> --string "192.168.1.100"
mem_find_string --pid <suspicious_pid> --string "powershell"
mem_find_string --pid <suspicious_pid> --string "invoke"

# 5. Read specific memory regions (from mem_map output)
mem_read --pid <suspicious_pid> --base 0x00400000 --size 4096

# 6. Full memory dump
# Via Dumper extension
extension request: {target: "memory", sid: "sensor-id", retention: 7}

# 7. Get command line and parent process
os_processes

# 8. Get network connections
netstat
```

### Automated Collection

```yaml
# Detect PowerShell memory injection
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: powershell
      case sensitive: false
    - op: or
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: invoke
        - op: contains
          path: event/COMMAND_LINE
          value: downloadstring
        - op: contains
          path: event/COMMAND_LINE
          value: webclient
        - op: contains
          path: event/COMMAND_LINE
          value: reflection

respond:
  - action: report
    name: powershell-injection-detected
    priority: 9
  # Get memory artifacts
  - action: task
    command: mem_map --pid {{ .event.PROCESS_ID }}
    investigation: fileless-{{ .event.PROCESS_ID }}
  - action: wait
    duration: 2s
  - action: task
    command: mem_strings --pid {{ .event.PROCESS_ID }}
  # Get process tree
  - action: task
    command: os_processes
  # Get network
  - action: task
    command: netstat
  # Full memory dump
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

### Reflective DLL Injection

```yaml
# Detect unsigned DLL in memory
detect:
  event: CODE_IDENTITY
  op: and
  rules:
    - op: is
      path: event/IS_SIGNED
      value: false
    - op: contains
      path: event/FILE_PATH
      value: memory
      case sensitive: false

respond:
  - action: report
    name: unsigned-memory-dll
    priority: 8
  - action: task
    command: mem_map --pid {{ .event.PROCESS_ID }}
  - action: task
    command: mem_strings --pid {{ .event.PROCESS_ID }}
  - action: task
    command: os_processes
```

---

## Scenario 10: Compliance Evidence Collection

**Objective**: Collect artifacts for compliance audit.

**When to Use**: Regular compliance monitoring, audit requirements, or regulatory evidence.

### Automated Privileged Access Collection

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
    priority: 3
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

### User Account Changes

```yaml
# Collect on user account changes
detect:
  event: WEL
  op: and
  rules:
    - op: or
      rules:
        - op: is
          path: event/EVENT/System/EventID
          value: '4720'  # User account created
        - op: is
          path: event/EVENT/System/EventID
          value: '4722'  # User account enabled
        - op: is
          path: event/EVENT/System/EventID
          value: '4738'  # User account changed

respond:
  - action: report
    name: user-account-change
    priority: 4
  - action: task
    command: log_get Security
    investigation: compliance-user-changes
  - action: task
    command: os_users
```

### Scheduled Compliance Collection

Use Reliable Tasking to schedule regular evidence collection:

```bash
# Weekly compliance collection
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"context":"weekly-compliance","plat":"windows","task":"log_get Security","ttl":604800}'
```

### Manual Compliance Collection

```bash
# Windows
log_get Security
log_get System
os_users
os_services
os_autoruns

# Linux
artifact_get /var/log/auth.log
artifact_get /var/log/secure
os_users
os_services
```

### File Integrity Monitoring

```yaml
# Monitor critical files for changes
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: or
      rules:
        - op: contains
          path: event/FILE_PATH
          value: C:\Windows\System32\
        - op: contains
          path: event/FILE_PATH
          value: C:\Program Files\

respond:
  - action: report
    name: critical-file-change
    priority: 6
  - action: task
    command: file_hash --path {{ .event.FILE_PATH }}
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
    investigation: fim-compliance
    suppression:
      max_count: 1
      period: 24h
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
```
