# D&R Rule Examples

Comprehensive collection of real-world Detection & Response rule examples organized by use case.

## Table of Contents

- [Process-Based Detections](#process-based-detections)
- [Network-Based Detections](#network-based-detections)
- [File-Based Detections](#file-based-detections)
- [Authentication & Identity](#authentication--identity)
- [Lateral Movement](#lateral-movement)
- [Data Exfiltration](#data-exfiltration)
- [Persistence Mechanisms](#persistence-mechanisms)
- [Threat Intelligence](#threat-intelligence)
- [Behavioral Detections](#behavioral-detections)
- [Compliance & Policy](#compliance--policy)

## Process-Based Detections

### Example 1: Execution from Downloads Directory

Detects when executables run from common download locations - often an indicator of user-initiated malware execution.

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: contains
      path: event/FILE_PATH
      value: \Downloads\
      case sensitive: false
respond:
  - action: report
    name: Execution from Downloads Directory
    priority: 2
    metadata:
      description: Process executed from Downloads folder
      mitre: T1204.002
      severity: medium
      recommendation: Investigate if user initiated this execution
  - action: add tag
    tag: execution-from-downloads
    ttl: 3600
  - action: task
    command: history_dump
    investigation: downloads-execution
```

**Detection Logic:**
- Windows platform only
- File path contains "\Downloads\"
- Case-insensitive to catch variations

**Response:**
- Creates medium-priority alert
- Tags sensor for 1 hour
- Captures process history for investigation

### Example 2: Office Application Spawning Encoded PowerShell

Classic macro-based malware behavior - Office apps spawning PowerShell with encoded commands.

```yaml
detect:
  event: NEW_PROCESS
  op: or
  rules:
    - op: ends with
      path: event/PARENT/FILE_PATH
      value: winword.exe
      case sensitive: false
    - op: ends with
      path: event/PARENT/FILE_PATH
      value: excel.exe
      case sensitive: false
    - op: ends with
      path: event/PARENT/FILE_PATH
      value: powerpnt.exe
      case sensitive: false
  with child:
    op: and
    rules:
      - op: ends with
        event: NEW_PROCESS
        path: event/FILE_PATH
        value: powershell.exe
        case sensitive: false
      - op: or
        rules:
          - op: contains
            path: event/COMMAND_LINE
            value: -enc
            case sensitive: false
          - op: contains
            path: event/COMMAND_LINE
            value: -encodedcommand
            case sensitive: false
respond:
  - action: report
    name: Office Application Spawning Encoded PowerShell
    priority: 4
    metadata:
      mitre: T1059.001, T1566.001
      description: Potential macro-based malware execution
      severity: high
      recommendation: Kill process tree and investigate document source
  - action: task
    command: deny_tree <<routing/this>>
    suppression:
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
  - action: isolate network
```

**Detection Logic:**
- Parent process is Word, Excel, or PowerPoint
- Child process is PowerShell
- Command line contains encoded command flags

**Response:**
- High-priority alert
- Kills the PowerShell process tree
- Isolates sensor from network
- Suppresses to prevent duplicate process kills

### Example 3: Suspicious Process Name Variations

Detects common malware technique of mimicking legitimate Windows processes with slight name variations.

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is windows
    - op: or
      rules:
        - op: string distance
          path: event/FILE_PATH
          file name: true
          value: svchost.exe
          max: 2
        - op: string distance
          path: event/FILE_PATH
          file name: true
          value: lsass.exe
          max: 2
        - op: string distance
          path: event/FILE_PATH
          file name: true
          value: csrss.exe
          max: 2
    - op: matches
      path: event/FILE_PATH
      re: ^C:\\Windows\\(System32|SysWOW64)\\
      case sensitive: false
      not: true
respond:
  - action: report
    name: "Suspicious Process Name Variation: {{ .event.FILE_PATH }}"
    priority: 4
    metadata:
      mitre: T1036.005
      description: Process name similar to legitimate Windows process but not in System32
      severity: high
    detect_data:
      process_name: "{{ .event.FILE_PATH }}"
      command_line: "{{ .event.COMMAND_LINE }}"
  - action: task
    command: os_suspend --pid {{ .event.PROCESS_ID }}
  - action: task
    command: yara_scan hive://yara/malware-signatures --pid "{{ .event.PROCESS_ID }}"
    investigation: suspicious-process-scan
```

**Detection Logic:**
- Windows platform
- Process name within 2 characters of svchost.exe, lsass.exe, or csrss.exe
- NOT located in System32 or SysWOW64 directories

**Response:**
- Suspends the process immediately
- Scans with YARA for malware signatures
- Extracts process details in structured format

### Example 4: Living Off the Land Binaries (LOLBins)

Detects abuse of legitimate Windows binaries for malicious purposes.

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is windows
    - op: or
      rules:
        - op: and
          rules:
            - op: ends with
              path: event/FILE_PATH
              value: certutil.exe
              case sensitive: false
            - op: or
              rules:
                - op: contains
                  path: event/COMMAND_LINE
                  value: -decode
                - op: contains
                  path: event/COMMAND_LINE
                  value: -urlcache
        - op: and
          rules:
            - op: ends with
              path: event/FILE_PATH
              value: bitsadmin.exe
              case sensitive: false
            - op: contains
              path: event/COMMAND_LINE
              value: /transfer
        - op: and
          rules:
            - op: ends with
              path: event/FILE_PATH
              value: mshta.exe
              case sensitive: false
            - op: contains
              path: event/COMMAND_LINE
              value: http
respond:
  - action: report
    name: "LOLBin Abuse Detected: {{ .event.FILE_PATH }}"
    priority: 3
    metadata:
      mitre: T1218
      description: Legitimate Windows binary used for potentially malicious purpose
      severity: medium
    detect_data:
      binary: "{{ .event.FILE_PATH }}"
      command: "{{ .event.COMMAND_LINE }}"
  - action: task
    command: history_dump
    investigation: lolbin-abuse
```

**Detection Logic:**
- Certutil with decode or urlcache flags
- Bitsadmin with transfer command
- Mshta with HTTP URL

**Response:**
- Medium-priority alert with structured data
- Captures process history for context

### Example 5: Excessive Child Processes

Detects processes spawning many children rapidly - potential process injection or spray attacks.

```yaml
detect:
  event: NEW_PROCESS
  op: is windows
  with child:
    event: NEW_PROCESS
    op: is windows
    count: 10
    within: 30
respond:
  - action: report
    name: "Process Spawning Excessive Children: {{ .event.FILE_PATH }}"
    priority: 3
    metadata:
      description: Process spawned 10+ children in 30 seconds
      potential_techniques: Process injection, spray attacks
    suppression:
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
  - action: add tag
    tag: excessive-spawning
    ttl: 1800
```

**Detection Logic:**
- Any Windows process
- Spawns 10+ child processes within 30 seconds

**Response:**
- Alert with suppression to prevent spam
- Tags sensor for 30 minutes

## Network-Based Detections

### Example 6: RDP from External IP Address

Detects Remote Desktop Protocol connections originating from public internet addresses.

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is
      path: event/FILE_PATH
      value: C:\WINDOWS\System32\svchost.exe
    - op: contains
      path: event/COMMAND_LINE
      value: TermService
    - op: scope
      path: event/NETWORK_ACTIVITY/
      rule:
        op: and
        rules:
          - op: is
            path: event/DESTINATION/PORT
            value: 3389
          - op: is public address
            path: event/SOURCE/IP_ADDRESS
respond:
  - action: report
    name: "RDP Connection from External IP: {{ index (index .event.NETWORK_ACTIVITY 0) \"SOURCE\" \"IP_ADDRESS\" }}"
    priority: 3
    metadata:
      mitre: T1021.001
      description: Remote Desktop connection from public internet
      severity: high
    detect_data:
      source_ip: "{{ index (index .event.NETWORK_ACTIVITY 0) \"SOURCE\" \"IP_ADDRESS\" }}"
      destination_port: "{{ index (index .event.NETWORK_ACTIVITY 0) \"DESTINATION\" \"PORT\" }}"
      hostname: "{{ .routing.hostname }}"
  - action: task
    command: history_dump
    investigation: rdp-external-access
  - action: add tag
    tag: external-rdp-access
    ttl: 86400
```

**Detection Logic:**
- Process is svchost.exe with TermService
- Destination port is 3389 (RDP)
- Source IP is public address
- Uses scope to properly handle network activity arrays

**Response:**
- High-priority alert with source IP in name
- Captures process history
- Tags sensor for 24 hours

### Example 7: DNS Tunneling Detection

Detects potential DNS tunneling based on suspicious domain characteristics.

```yaml
detect:
  event: DNS_REQUEST
  op: and
  rules:
    - op: is greater than
      path: event/DOMAIN_NAME
      value: 50
      length of: true
    - op: or
      rules:
        - op: contains
          path: event/DOMAIN_NAME
          sub domain: "0"
          value: 0123456789abcdef
        - op: is greater than
          path: event/DOMAIN_NAME
          sub domain: "0"
          value: 30
          length of: true
respond:
  - action: report
    name: "Potential DNS Tunneling: {{ .event.DOMAIN_NAME }}"
    priority: 3
    metadata:
      mitre: T1071.004
      description: DNS query with characteristics of tunneling (long, hex-like subdomain)
      severity: medium
    detect_data:
      domain: "{{ .event.DOMAIN_NAME }}"
      sensor: "{{ .routing.hostname }}"
  - action: add tag
    tag: dns-tunneling-suspect
    ttl: 7200
  - action: task
    command: history_dump
    investigation: dns-tunneling
```

**Detection Logic:**
- Domain name longer than 50 characters
- First subdomain contains hex characters OR is longer than 30 characters

**Response:**
- Alert with full domain name
- Tags sensor for 2 hours
- Captures context for investigation

### Example 8: Connection to Uncommon Ports

Detects network connections to non-standard ports that might indicate backdoors or covert channels.

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: scope
      path: event/NETWORK_ACTIVITY/
      rule:
        op: and
        rules:
          - op: is public address
            path: event/DESTINATION/IP_ADDRESS
          - op: is greater than
            path: event/DESTINATION/PORT
            value: 1024
          - op: is lower than
            path: event/DESTINATION/PORT
            value: 65535
    - op: ends with
      path: event/FILE_PATH
      value: .exe
      case sensitive: false
      not: true
    - op: matches
      path: event/FILE_PATH
      re: ^C:\\(Windows|Program Files)\\
      case sensitive: false
      not: true
respond:
  - action: report
    name: "Uncommon Port Connection: {{ .event.FILE_PATH }} to {{ index (index .event.NETWORK_ACTIVITY 0) \"DESTINATION\" \"IP_ADDRESS\" }}:{{ index (index .event.NETWORK_ACTIVITY 0) \"DESTINATION\" \"PORT\" }}"
    priority: 2
    metadata:
      description: Non-standard executable connecting to high port number
      potential_indicators: Backdoor, covert channel
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
        - '{{ index (index .event.NETWORK_ACTIVITY 0) "DESTINATION" "PORT" }}'
      max_count: 1
      period: 1h
```

**Detection Logic:**
- Public IP destination
- High port number (1024-65535)
- Process NOT a .exe OR NOT in Windows/Program Files

**Response:**
- Alert with connection details
- Suppressed per file/port combination

### Example 9: Beaconing Detection

Detects regular network connections that might indicate command and control beaconing.

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: scope
      path: event/NETWORK_ACTIVITY/
      rule:
        op: is public address
        path: event/DESTINATION/IP_ADDRESS
  with events:
    event: NETWORK_CONNECTIONS
    op: and
    rules:
      - op: is
        path: event/FILE_PATH
        value: <<event/FILE_PATH>>
      - op: scope
        path: event/NETWORK_ACTIVITY/
        rule:
          op: is
          path: event/DESTINATION/IP_ADDRESS
          value: <<event/NETWORK_ACTIVITY/0/DESTINATION/IP_ADDRESS>>
    count: 10
    within: 600
respond:
  - action: report
    name: "Potential C2 Beaconing: {{ .event.FILE_PATH }}"
    priority: 4
    metadata:
      mitre: T1071.001
      description: Process made 10+ connections to same external IP in 10 minutes
      severity: high
    detect_data:
      process: "{{ .event.FILE_PATH }}"
      destination_ip: "{{ index (index .event.NETWORK_ACTIVITY 0) \"DESTINATION\" \"IP_ADDRESS\" }}"
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
        - '{{ index (index .event.NETWORK_ACTIVITY 0) "DESTINATION" "IP_ADDRESS" }}'
      max_count: 1
      period: 1h
  - action: task
    command: history_dump
    investigation: beaconing-analysis
  - action: add tag
    tag: c2-beaconing-suspect
    ttl: 3600
```

**Detection Logic:**
- Connection to public IP
- Same process makes 10+ connections to same IP within 10 minutes

**Response:**
- High-priority alert
- Tags sensor for 1 hour
- Suppresses per process/IP combination

## File-Based Detections

### Example 10: Creation of Suspicious File Extensions

Detects creation of files with extensions commonly associated with malware or attacks.

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: is windows
    - op: or
      rules:
        - op: ends with
          path: event/FILE_PATH
          value: .ps1
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: .vbs
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: .bat
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: .cmd
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: .hta
          case sensitive: false
    - op: or
      rules:
        - op: contains
          path: event/FILE_PATH
          value: \AppData\Roaming\
          case sensitive: false
        - op: contains
          path: event/FILE_PATH
          value: \Temp\
          case sensitive: false
        - op: contains
          path: event/FILE_PATH
          value: \ProgramData\
          case sensitive: false
respond:
  - action: report
    name: "Suspicious Script Created: {{ .event.FILE_PATH }}"
    priority: 2
    metadata:
      mitre: T1059
      description: Script file created in suspicious location
      severity: medium
    detect_data:
      file_path: "{{ .event.FILE_PATH }}"
      creating_process: "{{ .event.PARENT.FILE_PATH }}"
  - action: task
    command: artifact_get "{{ .event.FILE_PATH }}"
    investigation: suspicious-script-collection
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 10m
```

**Detection Logic:**
- Script file extension (.ps1, .vbs, .bat, .cmd, .hta)
- Located in AppData, Temp, or ProgramData directories

**Response:**
- Collects the file for analysis
- Suppresses collection per file

### Example 11: Screensaver File Access

Detects access to screensaver files, which can be used for persistence or code execution.

```yaml
detect:
  event: FILE_TYPE_ACCESSED
  op: and
  rules:
    - op: is windows
    - op: matches
      path: event/FILE_PATH
      re: .*\\system32\\.*\.scr
      case sensitive: false
    - op: ends with
      path: event/PARENT/FILE_PATH
      value: explorer.exe
      case sensitive: false
      not: true
respond:
  - action: report
    name: "Suspicious Screensaver Access: {{ .event.FILE_PATH }}"
    priority: 3
    metadata:
      mitre: T1546.002
      description: Non-Explorer process accessing screensaver file
      severity: medium
    detect_data:
      screensaver: "{{ .event.FILE_PATH }}"
      accessing_process: "{{ .event.PARENT.FILE_PATH }}"
  - action: task
    command: artifact_get "{{ .event.FILE_PATH }}"
    investigation: screensaver-analysis
```

**Detection Logic:**
- .scr file in System32 directory
- Accessed by process other than explorer.exe

**Response:**
- Medium-priority alert
- Collects screensaver file

### Example 12: Large File Transfers

Detects creation or modification of unusually large files that might indicate data staging.

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: is greater than
      path: event/SIZE
      value: 104857600  # 100MB
    - op: or
      rules:
        - op: ends with
          path: event/FILE_PATH
          value: .zip
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: .rar
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: .7z
          case sensitive: false
respond:
  - action: report
    name: "Large Archive Created: {{ .event.FILE_PATH }}"
    priority: 2
    metadata:
      mitre: T1560.001
      description: Large compressed file created (potential data staging)
      severity: medium
    detect_data:
      file_path: "{{ .event.FILE_PATH }}"
      file_size: "{{ .event.SIZE }}"
      process: "{{ .event.PARENT.FILE_PATH }}"
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 1h
```

**Detection Logic:**
- File size greater than 100MB
- Archive file extension (.zip, .rar, .7z)

**Response:**
- Alert with file size details
- Suppressed per file to prevent spam

## Authentication & Identity

### Example 13: Multiple Failed Login Attempts

Classic brute force detection - multiple failed logins in short time period.

```yaml
detect:
  event: WEL
  op: is windows
  with events:
    event: WEL
    op: and
    rules:
      - op: is
        path: event/EVENT/System/EventID
        value: '4625'
      - op: is
        path: event/EVENT/System/Channel
        value: Security
    count: 5
    within: 300
respond:
  - action: report
    name: "Multiple Failed Login Attempts on {{ .routing.hostname }}"
    priority: 3
    metadata:
      mitre: T1110.001
      description: 5+ failed login attempts within 5 minutes
      severity: high
    suppression:
      max_count: 1
      period: 1h
      is_global: false
      keys:
        - '{{ .routing.sid }}'
  - action: add tag
    tag: brute-force-attempt
    ttl: 3600
```

**Detection Logic:**
- Windows Event ID 4625 (failed login)
- 5 occurrences within 300 seconds (5 minutes)

**Response:**
- Alert suppressed to once per hour per sensor
- Tags sensor for investigation

### Example 14: Password Spray Attack

Detects password spray attacks by looking for failed logins across multiple accounts from same source.

```yaml
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '4625'
    - op: is
      path: event/EVENT/System/Channel
      value: Security
  with events:
    event: WEL
    op: and
    rules:
      - op: is
        path: event/EVENT/System/EventID
        value: '4625'
      - op: is
        path: event/EVENT/EventData/Data/?/#text
        value: <<event/EVENT/EventData/Data/?/#text>>
    count: 10
    within: 600
respond:
  - action: report
    name: "Potential Password Spray Attack on {{ .routing.hostname }}"
    priority: 4
    metadata:
      mitre: T1110.003
      description: 10+ failed logins from same source within 10 minutes
      severity: critical
    suppression:
      max_count: 1
      period: 1h
      is_global: false
  - action: add tag
    tag: password-spray-attack
    ttl: 7200
```

**Detection Logic:**
- Failed login event (4625)
- 10+ occurrences from same source IP within 10 minutes

**Response:**
- Critical priority alert
- Tags sensor for 2 hours

### Example 15: New Service Installation

Detects installation of new Windows services, which can indicate persistence mechanisms.

```yaml
detect:
  event: WEL
  op: or
  rules:
    - op: and
      rules:
        - op: is
          path: event/EVENT/System/Channel
          value: System
        - op: or
          rules:
            - op: is
              path: event/EVENT/System/EventID
              value: '4697'
            - op: is
              path: event/EVENT/System/EventID
              value: '7045'
    - op: and
      rules:
        - op: is
          path: event/EVENT/System/Channel
          value: Security
        - op: is
          path: event/EVENT/System/EventID
          value: '4698'
respond:
  - action: report
    name: "New Service Installed on {{ .routing.hostname }}"
    priority: 3
    metadata:
      mitre: T1543.003
      description: New Windows service created
      severity: medium
      recommendation: Review service details for legitimacy
    suppression:
      max_count: 5
      period: 1h
      is_global: false
```

**Detection Logic:**
- Event ID 4697, 7045 (System channel) or 4698 (Security channel)
- All indicate new service installation

**Response:**
- Medium-priority alert
- Rate limited to 5 per hour per sensor

## Lateral Movement

### Example 16: PsExec Usage Detection

Detects use of PsExec or similar tools for remote execution.

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is windows
    - op: or
      rules:
        - op: contains
          path: event/FILE_PATH
          value: psexesvc.exe
          case sensitive: false
        - op: and
          rules:
            - op: ends with
              path: event/FILE_PATH
              value: psexec.exe
              case sensitive: false
            - op: contains
              path: event/COMMAND_LINE
              value: \\\\
respond:
  - action: report
    name: "PsExec Usage Detected: {{ .event.FILE_PATH }}"
    priority: 3
    metadata:
      mitre: T1570, T1021.002
      description: PsExec or similar remote execution tool detected
      severity: high
    detect_data:
      process: "{{ .event.FILE_PATH }}"
      command_line: "{{ .event.COMMAND_LINE }}"
      hostname: "{{ .routing.hostname }}"
  - action: task
    command: history_dump
    investigation: psexec-lateral-movement
  - action: add tag
    tag: lateral-movement-tool
    ttl: 7200
```

**Detection Logic:**
- PsExec service (psexesvc.exe) OR
- PsExec executable with UNC path in command line

**Response:**
- High-priority alert with full details
- Captures process history
- Tags sensor for 2 hours

### Example 17: Windows Admin Shares Access

Detects connections to administrative shares (C$, ADMIN$) which are commonly used in lateral movement.

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is windows
    - op: scope
      path: event/NETWORK_ACTIVITY/
      rule:
        op: and
        rules:
          - op: is
            path: event/DESTINATION/PORT
            value: 445
          - op: is private address
            path: event/DESTINATION/IP_ADDRESS
respond:
  - action: report
    name: "SMB Connection to Internal Host: {{ .routing.hostname }} to {{ index (index .event.NETWORK_ACTIVITY 0) \"DESTINATION\" \"IP_ADDRESS\" }}"
    priority: 2
    metadata:
      mitre: T1021.002
      description: SMB connection to internal system (potential lateral movement)
      severity: medium
    detect_data:
      source_host: "{{ .routing.hostname }}"
      destination_ip: "{{ index (index .event.NETWORK_ACTIVITY 0) \"DESTINATION\" \"IP_ADDRESS\" }}"
      process: "{{ .event.FILE_PATH }}"
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ index (index .event.NETWORK_ACTIVITY 0) "DESTINATION" "IP_ADDRESS" }}'
      max_count: 1
      period: 30m
```

**Detection Logic:**
- SMB port (445) connection
- Destination is private IP address

**Response:**
- Medium-priority alert
- Suppressed per source/destination pair

### Example 18: WMI Remote Execution

Detects Windows Management Instrumentation (WMI) used for remote command execution.

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is windows
    - op: ends with
      path: event/PARENT/FILE_PATH
      value: wmiprvse.exe
      case sensitive: false
    - op: or
      rules:
        - op: ends with
          path: event/FILE_PATH
          value: powershell.exe
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: cmd.exe
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: wscript.exe
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: cscript.exe
          case sensitive: false
respond:
  - action: report
    name: "WMI Remote Execution: {{ .event.FILE_PATH }}"
    priority: 3
    metadata:
      mitre: T1047
      description: Suspicious process spawned by WMI service
      severity: high
    detect_data:
      process: "{{ .event.FILE_PATH }}"
      command_line: "{{ .event.COMMAND_LINE }}"
      parent: "{{ .event.PARENT.FILE_PATH }}"
  - action: task
    command: history_dump
    investigation: wmi-execution
```

**Detection Logic:**
- Parent process is wmiprvse.exe
- Child is PowerShell, cmd, or script interpreter

**Response:**
- High-priority alert
- Captures process history

## Data Exfiltration

### Example 19: Large Data Upload

Detects unusually large outbound data transfers that might indicate exfiltration.

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: scope
      path: event/NETWORK_ACTIVITY/
      rule:
        op: and
        rules:
          - op: is public address
            path: event/DESTINATION/IP_ADDRESS
          - op: is greater than
            path: event/BYTES_SENT
            value: 10485760  # 10MB
respond:
  - action: report
    name: "Large Data Upload: {{ .event.FILE_PATH }} sent {{ index (index .event.NETWORK_ACTIVITY 0) \"BYTES_SENT\" }} bytes"
    priority: 3
    metadata:
      mitre: T1041
      description: Process sent more than 10MB to external IP
      severity: medium
    detect_data:
      process: "{{ .event.FILE_PATH }}"
      bytes_sent: "{{ index (index .event.NETWORK_ACTIVITY 0) \"BYTES_SENT\" }}"
      destination_ip: "{{ index (index .event.NETWORK_ACTIVITY 0) \"DESTINATION\" \"IP_ADDRESS\" }}"
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
        - '{{ index (index .event.NETWORK_ACTIVITY 0) "DESTINATION" "IP_ADDRESS" }}'
      max_count: 1
      period: 1h
```

**Detection Logic:**
- Connection to public IP
- More than 10MB sent

**Response:**
- Alert with byte count
- Suppressed per process/destination

### Example 20: Cloud Storage Upload

Detects uploads to common cloud storage services.

```yaml
detect:
  event: DNS_REQUEST
  op: or
  rules:
    - op: contains
      path: event/DOMAIN_NAME
      sub domain: "-2:"
      value: dropbox.com
      case sensitive: false
    - op: contains
      path: event/DOMAIN_NAME
      sub domain: "-2:"
      value: box.com
      case sensitive: false
    - op: contains
      path: event/DOMAIN_NAME
      sub domain: "-2:"
      value: drive.google.com
      case sensitive: false
    - op: contains
      path: event/DOMAIN_NAME
      sub domain: "-2:"
      value: onedrive.live.com
      case sensitive: false
respond:
  - action: report
    name: "Cloud Storage Access: {{ .event.DOMAIN_NAME }}"
    priority: 1
    metadata:
      description: Access to cloud storage service detected
      recommendation: Verify if access is authorized
    detect_data:
      domain: "{{ .event.DOMAIN_NAME }}"
      hostname: "{{ .routing.hostname }}"
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ .event.DOMAIN_NAME }}'
      max_count: 1
      period: 12h
```

**Detection Logic:**
- DNS request to known cloud storage domains
- Uses subdomain extraction to match base domains

**Response:**
- Low-priority informational alert
- Suppressed per sensor/domain for 12 hours

## Persistence Mechanisms

### Example 21: Registry Run Key Modification

Detects modifications to registry Run keys used for persistence.

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is windows
    - op: ends with
      path: event/FILE_PATH
      value: reg.exe
      case sensitive: false
    - op: contains
      path: event/COMMAND_LINE
      value: add
      case sensitive: false
    - op: or
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: CurrentVersion\Run
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: CurrentVersion\RunOnce
          case sensitive: false
respond:
  - action: report
    name: "Registry Run Key Modified: {{ .routing.hostname }}"
    priority: 3
    metadata:
      mitre: T1547.001
      description: Registry Run key modified for persistence
      severity: high
    detect_data:
      command_line: "{{ .event.COMMAND_LINE }}"
      parent_process: "{{ .event.PARENT.FILE_PATH }}"
  - action: task
    command: history_dump
    investigation: registry-persistence
```

**Detection Logic:**
- reg.exe process
- "add" command
- CurrentVersion\Run or CurrentVersion\RunOnce in command line

**Response:**
- High-priority alert
- Captures process history

### Example 22: Scheduled Task Creation

Detects creation of scheduled tasks, a common persistence mechanism.

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is windows
    - op: ends with
      path: event/FILE_PATH
      value: schtasks.exe
      case sensitive: false
    - op: contains
      path: event/COMMAND_LINE
      value: /create
      case sensitive: false
respond:
  - action: report
    name: "Scheduled Task Created: {{ .routing.hostname }}"
    priority: 2
    metadata:
      mitre: T1053.005
      description: New scheduled task created
      severity: medium
    detect_data:
      command_line: "{{ .event.COMMAND_LINE }}"
      parent_process: "{{ .event.PARENT.FILE_PATH }}"
      hostname: "{{ .routing.hostname }}"
  - action: task
    command: history_dump
    investigation: scheduled-task-analysis
```

**Detection Logic:**
- schtasks.exe with /create parameter

**Response:**
- Medium-priority alert
- Captures process context

## Threat Intelligence

### Example 23: Malware Domain Lookup

Detects DNS requests to known malicious domains using threat feed.

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malwaredomains
  case sensitive: false
respond:
  - action: report
    name: "DNS Request to Known Malicious Domain: {{ .event.DOMAIN_NAME }}"
    priority: 4
    metadata:
      mitre: T1071.001
      description: DNS query to domain in threat intelligence feed
      severity: critical
    detect_data:
      domain: "{{ .event.DOMAIN_NAME }}"
      sensor: "{{ .routing.hostname }}"
  - action: add tag
    tag: contacted-malicious-domain
    ttl: 86400
  - action: task
    command: history_dump
    investigation: malicious-dns
  - action: isolate network
```

**Detection Logic:**
- DNS request matches entry in malwaredomains lookup resource

**Response:**
- Critical alert
- Isolates sensor immediately
- Tags for 24 hours

### Example 24: Known Malware Hash Detection

Detects execution of files with known malicious hashes.

```yaml
detect:
  event: CODE_IDENTITY
  op: lookup
  path: event/HASH
  resource: hive://lookup/malware-hashes
respond:
  - action: report
    name: "Known Malware Executed: {{ .event.FILE_PATH }}"
    priority: 5
    metadata:
      mitre: T1204
      description: File with known malicious hash executed
      severity: critical
    detect_data:
      file_path: "{{ .event.FILE_PATH }}"
      hash: "{{ .event.HASH }}"
      hostname: "{{ .routing.hostname }}"
  - action: task
    command: deny_tree <<routing/this>>
  - action: task
    command: artifact_get "{{ .event.FILE_PATH }}"
    investigation: malware-sample
  - action: isolate network
```

**Detection Logic:**
- File hash matches entry in malware-hashes lookup resource

**Response:**
- Maximum priority alert
- Kills process tree immediately
- Collects file sample
- Isolates sensor

## Behavioral Detections

### Example 25: After-Hours Activity

Detects suspicious activity outside of normal business hours.

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is windows
    - op: or
      rules:
        - op: ends with
          path: event/FILE_PATH
          value: powershell.exe
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: cmd.exe
          case sensitive: false
  times:
    - day_of_week_start: 2     # Monday
      day_of_week_end: 6       # Friday
      time_of_day_start: 1800  # 6 PM
      time_of_day_end: 2359    # 11:59 PM
      tz: America/New_York
    - day_of_week_start: 2
      day_of_week_end: 6
      time_of_day_start: 0     # 12 AM
      time_of_day_end: 700     # 7 AM
      tz: America/New_York
    - day_of_week_start: 6     # Saturday
      day_of_week_end: 7       # Sunday
      time_of_day_start: 0
      time_of_day_end: 2359
      tz: America/New_York
respond:
  - action: report
    name: "After-Hours PowerShell/CMD Activity: {{ .routing.hostname }}"
    priority: 2
    metadata:
      description: PowerShell or CMD executed outside business hours
      severity: medium
    detect_data:
      process: "{{ .event.FILE_PATH }}"
      command_line: "{{ .event.COMMAND_LINE }}"
      time: "{{ .routing.event_time }}"
```

**Detection Logic:**
- PowerShell or CMD execution
- Outside business hours (6PM-7AM weekdays, all weekend)
- Eastern Time timezone

**Response:**
- Medium-priority alert with timestamp

## Compliance & Policy

### Example 26: USB Device Connection

Detects when USB storage devices are connected (for compliance monitoring).

```yaml
detect:
  event: VOLUME_MOUNT
  op: and
  rules:
    - op: is windows
    - op: is
      path: event/DEVICE_TYPE
      value: USB
respond:
  - action: report
    name: "USB Device Connected: {{ .routing.hostname }}"
    priority: 1
    metadata:
      compliance: USB usage monitoring
      description: USB storage device connected to endpoint
    detect_data:
      volume_path: "{{ .event.VOLUME_PATH }}"
      device_name: "{{ .event.DEVICE_NAME }}"
      hostname: "{{ .routing.hostname }}"
      user: "{{ .event.USER_NAME }}"
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ .event.DEVICE_NAME }}'
      max_count: 1
      period: 24h
```

**Detection Logic:**
- Volume mount event
- Device type is USB

**Response:**
- Low-priority informational alert
- Tracks user and device details
- Suppressed per sensor/device for 24 hours

---

[Back to SKILL.md](SKILL.md) | [Reference](REFERENCE.md) | [Troubleshooting](TROUBLESHOOTING.md)
