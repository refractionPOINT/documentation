# Incident Response Scenario Examples

This document provides complete, step-by-step incident response scenarios demonstrating LimaCharlie's capabilities across the full IR lifecycle.

## Scenario 1: Ransomware Detection and Response

### Overview

This scenario demonstrates a complete ransomware incident response workflow, from initial detection through containment, investigation, eradication, and recovery.

### Initial Detection

#### Detection Rule 1: Mass File Encryption

Detect ransomware behavior based on rapid file encryption activity.

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: .encrypted
      case sensitive: false
  with events:
    event: NEW_DOCUMENT
    op: contains
    path: event/FILE_PATH
    value: .encrypted
    count: 10
    within: 60
respond:
  - action: report
    name: "Ransomware activity detected - mass encryption"
    priority: 5
    metadata:
      description: "Multiple files encrypted in short time period"
      mitre: T1486
      author: security-team@company.com

  # Immediate containment
  - action: isolate network

  # Terminate ransomware process
  - action: task
    command: deny_tree <<routing/this>>
    suppression:
      is_global: false
      keys:
        - '{{ .routing.hostname }}'
      max_count: 1
      period: 1h

  # Forensic collection
  - action: task
    command: history_dump
    investigation: ransomware-incident
    suppression:
      is_global: false
      keys:
        - '{{ .routing.hostname }}'
      max_count: 1
      period: 1h

  # Tag for tracking
  - action: add tag
    tag: ransomware-infected
    ttl: 86400

  # Seal sensor to prevent tampering
  - action: seal
```

#### Detection Rule 2: Ransom Note Creation

Detect creation of ransom note files.

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: README
      case sensitive: false
    - op: or
      rules:
        - op: contains
          path: event/FILE_PATH
          value: DECRYPT
        - op: contains
          path: event/FILE_PATH
          value: RANSOM
        - op: contains
          path: event/FILE_PATH
          value: RECOVER
respond:
  - action: report
    name: "Ransom note detected - {{ .event.FILE_PATH }}"
    priority: 5
    metadata:
      description: "Ransomware note file created"
      mitre: T1486

  # Collect ransom note
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
    investigation: ransomware-incident
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 24h
```

### Phase 1: Containment (Automated)

The D&R rules automatically execute containment:

1. Network isolation activated
2. Ransomware process terminated
3. Sensor sealed to prevent tampering
4. System tagged for incident tracking

### Phase 2: Investigation (Manual)

#### Step 1: Review Timeline

```bash
# Review process execution history
history_dump
```

Analysis:
- Identify ransomware executable path
- Determine initial infection vector (email attachment, exploit, etc.)
- Map process ancestry to find entry point

#### Step 2: System State Assessment

```bash
# Check current processes
os_processes

# Look for persistence mechanisms
os_autoruns

# Review services
os_services

# Check network connections
netstat
```

Analysis:
- Identify any remaining malicious processes
- Look for persistence (autorun entries, services, scheduled tasks)
- Check for backdoors or additional payloads

#### Step 3: Scope Assessment

Use LCQL to determine if other systems are affected:

```
# Search for similar file encryption patterns across org
-1h | NEW_DOCUMENT | event/FILE_PATH contains '.encrypted' | routing/hostname as host COUNT_UNIQUE(event) as count GROUP BY(host)

# Look for ransomware executable on other systems
-24h | NEW_PROCESS | event/FILE_PATH == 'C:\Users\victim\Downloads\ransomware.exe' | routing/hostname as host

# Search for related network connections
-2h | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS == '198.51.100.50' | routing/hostname as host event/FILE_PATH as process
```

#### Step 4: Artifact Collection

```bash
# Collect ransomware executable
artifact_get C:\Users\victim\Downloads\ransomware.exe

# Collect ransom note (already automated via D&R)

# Collect Windows Event Logs for forensic analysis
artifact_get C:\Windows\System32\winevt\Logs\Security.evtx
artifact_get C:\Windows\System32\winevt\Logs\System.evtx

# Collect prefetch files for execution timeline
artifact_get C:\Windows\Prefetch\RANSOMWARE.EXE-*.pf
```

### Phase 3: Eradication

#### Step 1: Remove Persistence

```bash
# Review autoruns output from earlier
# Identify malicious entries

# Remove autorun entry
run reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsUpdate" /f

# Remove scheduled task if present
run schtasks /query /tn "SystemCheck"
run schtasks /delete /tn "SystemCheck" /f
```

#### Step 2: Delete Malware

```bash
# Verify ransomware process terminated
os_processes

# Delete ransomware executable
file_del C:\Users\victim\Downloads\ransomware.exe

# Delete any dropped files
file_del C:\ProgramData\update.exe
```

#### Step 3: Remove Ransom Notes

```bash
# Remove ransom notes from common locations
file_del C:\Users\victim\Desktop\README-DECRYPT.txt
file_del C:\Users\victim\Documents\README-DECRYPT.txt
```

### Phase 4: Recovery

#### Step 1: Restore Files

```bash
# Option 1: Restore from backup (recommended)
# Execute restore procedure from backup system

# Option 2: Attempt decryption (if decryptor available)
# Research ransomware variant for available decryptors
```

#### Step 2: System Validation

```bash
# Verify no malware remains
os_processes
os_autoruns
os_services

# Check for suspicious network connections
netstat

# Scan with YARA rules if available
# YARA scanning automatic if rules deployed
```

#### Step 3: Remove Containment

```yaml
# Create D&R rule to rejoin network (or execute manually)
detect:
  event: tag_added
  op: is
  path: event/tag
  value: remediation-complete
respond:
  - action: rejoin network
  - action: unseal
  - action: remove tag
    tag: ransomware-infected
```

#### Step 4: Monitoring

Apply enhanced monitoring tag:

```yaml
# Tag for enhanced monitoring
respond:
  - action: add tag
    tag: post-ransomware-monitoring
    ttl: 604800  # 7 days
```

Create monitoring rules for reinfection:

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is tagged
      tag: post-ransomware-monitoring
    - op: contains
      path: event/FILE_PATH
      value: .exe
      case sensitive: false
respond:
  - action: report
    name: "New executable on recently infected system"
    priority: 3
```

### Phase 5: Lessons Learned

#### Document Findings

Key information to document:
- Initial infection vector (email, exploit, RDP brute force)
- Ransomware variant and IOCs (hashes, IPs, domains)
- Timeline of events
- Files encrypted vs. recovered
- Total response time

#### Create Detection Rules

```yaml
# Detection for this specific ransomware variant
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is
      path: event/HASH
      value: abc123def456...  # Actual ransomware hash
respond:
  - action: report
    name: "Known ransomware variant detected"
    priority: 5
  - action: isolate network
  - action: task
    command: deny_tree <<routing/this>>
```

#### Update Threat Intelligence

Add indicators to lookup lists:

```yaml
# Block known ransomware C2 domains
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/ransomware-c2-domains
respond:
  - action: report
    name: "DNS query to known ransomware C2"
    priority: 5
  - action: isolate network
```

---

## Scenario 2: Compromised Credentials and Lateral Movement

### Overview

This scenario demonstrates detection and response to a credential compromise leading to lateral movement across the environment.

### Initial Detection

#### Detection Rule: Multiple Network Logons

```yaml
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '4624'
    - op: is
      path: event/EVENT/EventData/LogonType
      value: '3'  # Network logon
  with events:
    event: WEL
    op: and
    rules:
      - op: is
        path: event/EVENT/System/EventID
        value: '4624'
      - op: is
        path: event/EVENT/EventData/LogonType
        value: '3'
    count: 5
    within: 300
respond:
  - action: report
    name: "Multiple network logons - potential lateral movement"
    priority: 4
    metadata:
      description: "User account used for multiple network logons in short time"
      mitre: T1021

  - action: task
    command: history_dump
    investigation: lateral-movement

  - action: add tag
    tag: suspicious-logons
    ttl: 3600
```

#### Detection Rule: PsExec Usage

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/COMMAND_LINE
      value: psexec
      case sensitive: false
    - op: is public address
      path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
respond:
  - action: report
    name: "PsExec execution detected - possible lateral movement"
    priority: 5
    metadata:
      description: "PsExec used from external IP address"
      mitre: T1021.002

  - action: isolate network

  - action: task
    command: history_dump
    investigation: lateral-movement

  - action: task
    command: os_processes
    investigation: lateral-movement

  - action: task
    command: netstat
    investigation: lateral-movement

  - action: add tag
    tag: lateral-movement-victim
    ttl: 86400
```

### Phase 1: Initial Investigation

#### Step 1: Identify Compromised Account

From initial alert, identify the user account:
- Review Windows Event Log 4624 events
- Determine source IP of logons
- Identify target systems

```
# Find all systems accessed by suspicious user
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/TargetUserName == "compromised_user" | routing/hostname as host event/EVENT/EventData/LogonType as type event/EVENT/EventData/IpAddress as source
```

#### Step 2: Map Lateral Movement

```
# Find all logons from suspicious source IP
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/IpAddress == "10.0.1.50" | routing/hostname as target event/EVENT/EventData/TargetUserName as user

# Hunt for PsExec across all systems
-24h | plat == windows | * | event/* contains 'psexec' | routing/hostname as host routing/event_type as event

# Look for admin share access
-24h | plat == windows | WEL | event/EVENT/System/EventID == "5140" | event/EVENT/EventData/ShareName as share routing/hostname as host event/EVENT/EventData/IpAddress as source
```

#### Step 3: Identify Attacker Activities

On each compromised system:

```bash
# Review process execution
history_dump

# Check current processes
os_processes

# Look for persistence
os_autoruns

# Check scheduled tasks
run schtasks /query /fo LIST /v

# Review network connections
netstat
```

### Phase 2: Containment

#### Step 1: Isolate All Affected Systems

Create D&R rule to isolate all systems with suspicious-logons or lateral-movement-victim tags:

```yaml
detect:
  event: tag_added
  op: or
  rules:
    - op: is
      path: event/tag
      value: suspicious-logons
    - op: is
      path: event/tag
      value: lateral-movement-victim
respond:
  - action: isolate network
  - action: report
    name: "System isolated due to lateral movement"
    priority: 5
```

#### Step 2: Disable Compromised Account

Execute via enterprise authentication system:
- Disable Active Directory account
- Force password reset
- Revoke all active sessions

#### Step 3: Block Attacker Source

If external access point identified:

```yaml
# Create detection for source IP
detect:
  event: NETWORK_CONNECTIONS
  op: is
  path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
  value: 203.0.113.50
respond:
  - action: report
    name: "Connection from attacker IP blocked"
    priority: 5
  - action: isolate network
```

### Phase 3: Investigation Deep Dive

#### Step 1: Determine Initial Access

```
# Search for initial authentication
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/TargetUserName == "compromised_user" | routing/hostname as host event/EVENT/EventData/IpAddress as source event/EVENT/System/TimeCreated/@SystemTime as time

# Look for brute force attempts
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4625" AND event/EVENT/EventData/TargetUserName == "compromised_user" | COUNT_UNIQUE(event) as attempts event/EVENT/EventData/IpAddress as source GROUP BY(source)

# Check for RDP connections
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/LogonType == "10" | routing/hostname as host event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as source
```

#### Step 2: Identify Data Access

```
# Search for file access
-24h | plat == windows | * | event/FILE_PATH contains 'Confidential' | routing/hostname as host event/FILE_PATH as path routing/event_type as event

# Look for large data transfers
-24h | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/BYTES_SENT > 104857600 | routing/hostname as host event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/BYTES_SENT as bytes
```

#### Step 3: Artifact Collection

On each compromised system:

```bash
# Collect Windows Event Logs
artifact_get C:\Windows\System32\winevt\Logs\Security.evtx
artifact_get C:\Windows\System32\winevt\Logs\System.evtx

# Collect PowerShell logs
artifact_get C:\Windows\System32\winevt\Logs\Microsoft-Windows-PowerShell\Operational.evtx

# Collect prefetch files
dir_list C:\Windows\Prefetch
# Then collect relevant prefetch files for PsExec, tools used

# Collect browser history if relevant
artifact_get C:\Users\compromised_user\AppData\Local\Google\Chrome\User Data\Default\History
```

### Phase 4: Eradication

#### Step 1: Remove Attacker Persistence

On each affected system:

```bash
# Check and remove malicious autoruns
os_autoruns
run reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "Update" /f

# Remove malicious scheduled tasks
run schtasks /query
run schtasks /delete /tn "SystemUpdate" /f

# Remove malicious services
os_services
run sc delete MaliciousService

# Delete attacker tools
file_del C:\Windows\Temp\psexec.exe
file_del C:\ProgramData\tools\
```

#### Step 2: Reset All Privileged Credentials

- Reset Domain Admin passwords
- Reset local Administrator passwords on affected systems
- Rotate service account credentials
- Reset compromised user password

#### Step 3: Remove Backdoors

```bash
# Check for web shells on web servers
dir_list C:\inetpub\wwwroot --recurse
# Review for suspicious files, collect if found

# Look for remote access tools
os_processes
# Terminate and remove any RAT software found
```

### Phase 5: Recovery

#### Step 1: Verify Eradication

On each system:

```bash
# Verify no malicious processes
os_processes

# Verify persistence removed
os_autoruns
os_services

# Verify no suspicious network connections
netstat
```

#### Step 2: Rejoin Systems to Network

```yaml
# Manually rejoin after validation
respond:
  - action: rejoin network
  - action: remove tag
    tag: lateral-movement-victim
```

#### Step 3: Enhanced Monitoring

Apply post-incident monitoring:

```yaml
detect:
  event: WEL
  op: and
  rules:
    - op: is tagged
      tag: post-lateral-movement-monitoring
    - op: is
      path: event/EVENT/System/EventID
      value: '4624'
    - op: is
      path: event/EVENT/EventData/LogonType
      value: '3'
respond:
  - action: report
    name: "Network logon on recently compromised system"
    priority: 3
```

### Phase 6: Lessons Learned

#### Create Detection Rules

```yaml
# Detect credential reuse
detect:
  event: WEL
  op: is
  path: event/EVENT/System/EventID
  value: '4624'
  with events:
    event: WEL
    op: and
    rules:
      - op: is
        path: event/EVENT/System/EventID
        value: '4624'
      - op: is
        path: event/EVENT/EventData/LogonType
        value: '3'
    count: 3
    within: 60
respond:
  - action: report
    name: "Rapid credential reuse detected"
    priority: 4

# Detect PsExec from service creation
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '7045'
    - op: contains
      path: event/EVENT/EventData/ServiceName
      value: PSEXESVC
respond:
  - action: report
    name: "PsExec service detected"
    priority: 4
```

---

## Scenario 3: Web Shell Detection and Response

### Overview

This scenario demonstrates detection and response to a web shell deployed on a public-facing web server.

### Initial Detection

#### Detection Rule: Web Server Spawning Shell

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: or
      rules:
        - op: ends with
          path: event/PARENT/FILE_PATH
          value: w3wp.exe
          case sensitive: false
        - op: ends with
          path: event/PARENT/FILE_PATH
          value: httpd
        - op: ends with
          path: event/PARENT/FILE_PATH
          value: nginx
  with child:
    op: and
    rules:
      - op: or
        rules:
          - op: ends with
            event: NEW_PROCESS
            path: event/FILE_PATH
            value: cmd.exe
            case sensitive: false
          - op: ends with
            event: NEW_PROCESS
            path: event/FILE_PATH
            value: powershell.exe
            case sensitive: false
          - op: ends with
            event: NEW_PROCESS
            path: event/FILE_PATH
            value: bash
          - op: ends with
            event: NEW_PROCESS
            path: event/FILE_PATH
            value: sh
respond:
  - action: report
    name: "Web server spawning suspicious process - possible web shell"
    priority: 5
    metadata:
      description: "Web server process spawned command shell"
      mitre: T1505.003

  - action: task
    command: history_dump
    investigation: web-shell

  - action: task
    command: deny_tree <<routing/this>>
    suppression:
      is_global: false
      keys:
        - '{{ .routing.hostname }}'
      max_count: 1
      period: 5m

  - action: add tag
    tag: web-shell-detected
```

### Phase 1: Immediate Response

#### Step 1: Terminate Malicious Processes

Already automated via D&R rule (deny_tree).

#### Step 2: Initial Investigation

```bash
# Get process history
history_dump

# Check current processes
os_processes

# Review network connections
netstat
```

### Phase 2: Investigation

#### Step 1: Locate Web Shell

```bash
# List web root directory
dir_list /var/www/html              # Linux
dir_list C:\inetpub\wwwroot         # Windows

# Get file info for suspicious files
file_info /var/www/html/upload.php
file_hash /var/www/html/upload.php
```

Find recently created/modified files:

```
# Search for recent file creation in web root
-24h | plat == linux | NEW_DOCUMENT | event/FILE_PATH starts with '/var/www/' | event/FILE_PATH as path event/HASH as hash routing/event_time as time

# Windows equivalent
-24h | plat == windows | NEW_DOCUMENT | event/FILE_PATH starts with 'C:\inetpub\wwwroot' | event/FILE_PATH as path event/HASH as hash routing/event_time as time
```

#### Step 2: Identify Exploitation Vector

Review web server logs to find exploitation attempt:

```bash
# Collect web server access logs
artifact_get /var/log/apache2/access.log
artifact_get /var/log/nginx/access.log
artifact_get C:\inetpub\logs\LogFiles\W3SVC1\u_ex*.log

# Collect error logs
artifact_get /var/log/apache2/error.log
artifact_get /var/log/nginx/error.log
```

Common exploitation methods:
- File upload vulnerability
- SQL injection to file write
- Vulnerable plugin/component
- Credential compromise

#### Step 3: Assess Attacker Activities

```
# Find all processes spawned by web server
-12h | plat == linux | NEW_PROCESS | event/PARENT/FILE_PATH ends with 'httpd' OR event/PARENT/FILE_PATH ends with 'nginx' | event/FILE_PATH as process event/COMMAND_LINE as command routing/event_time as time

# Check for data exfiltration
-12h | NETWORK_CONNECTIONS | event/FILE_PATH ends with 'httpd' OR event/FILE_PATH ends with 'nginx' | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/BYTES_SENT as bytes

# Look for privilege escalation attempts
-12h | plat == linux | NEW_PROCESS | event/USER == 'root' AND event/PARENT/USER == 'www-data' | event/FILE_PATH as process event/COMMAND_LINE as command
```

#### Step 4: Check for Additional Backdoors

```bash
# Scan web directories for PHP files (common web shells)
dir_list /var/www/html --recurse

# Check for recently modified files
# Use LCQL NEW_DOCUMENT events from Step 1

# Look for suspicious file names
# Common web shell names: shell.php, c99.php, r57.php, wso.php, b374k.php
```

### Phase 3: Containment

#### Step 1: Collect Web Shell

```bash
# Collect the web shell file for analysis
artifact_get /var/www/html/upload.php
```

#### Step 2: Remove Web Shell

```bash
# Delete web shell
file_del /var/www/html/upload.php
```

#### Step 3: Block Attacker IP

If attacker IP identified from logs:

```yaml
# Create temporary blocking rule
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is
      path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
      value: 198.51.100.100
    - op: is tagged
      tag: web-server
respond:
  - action: report
    name: "Connection from known attacker IP"
    priority: 5
```

Also block at firewall/WAF level.

### Phase 4: Eradication

#### Step 1: Remove All Backdoors

```bash
# Check for additional web shells
dir_list /var/www/html --recurse
# Review for suspicious files

# Check cron jobs for persistence (Linux)
run crontab -l
run cat /etc/cron.d/*

# Check for malicious startup scripts
dir_list /etc/init.d
dir_list /etc/systemd/system
```

#### Step 2: Patch Vulnerability

Identify and patch the exploited vulnerability:

```bash
# Check application version
run /var/www/html/app --version

# Review for available patches
# Update vulnerable component
```

#### Step 3: Reset Credentials

If web application credentials may be compromised:

- Reset database passwords
- Reset web application admin accounts
- Rotate API keys
- Change FTP/SSH credentials

### Phase 5: Recovery

#### Step 1: Verify Clean State

```bash
# Verify no malicious processes
os_processes

# Verify no suspicious files remain
dir_list /var/www/html --recurse

# Check for suspicious network connections
netstat

# Verify no cron jobs
run crontab -l
```

#### Step 2: Restore Service

If web server was taken offline:

```bash
# Restart web server
run systemctl start apache2    # Linux
run systemctl start nginx       # Linux
run net start W3SVC            # Windows IIS
```

#### Step 3: Enhanced Monitoring

```yaml
# Monitor for reinfection
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: is tagged
      tag: web-server
    - op: or
      rules:
        - op: starts with
          path: event/FILE_PATH
          value: /var/www/
        - op: starts with
          path: event/FILE_PATH
          value: C:\inetpub\
respond:
  - action: report
    name: "New file in web root - {{ .event.FILE_PATH }}"
    priority: 3
  - action: task
    command: file_info {{ .event.FILE_PATH }}
    investigation: web-server-monitoring

# Monitor for command shell execution
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is tagged
      tag: web-server
    - op: or
      rules:
        - op: ends with
          path: event/PARENT/FILE_PATH
          value: httpd
        - op: ends with
          path: event/PARENT/FILE_PATH
          value: nginx
        - op: ends with
          path: event/PARENT/FILE_PATH
          value: w3wp.exe
respond:
  - action: report
    name: "Process spawned by web server"
    priority: 4
  - action: task
    command: history_dump
    investigation: web-server-monitoring
```

### Phase 6: Lessons Learned

#### Create Permanent Detection Rules

```yaml
# Detect common web shell indicators
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: or
      rules:
        - op: starts with
          path: event/FILE_PATH
          value: /var/www/
        - op: starts with
          path: event/FILE_PATH
          value: C:\inetpub\
    - op: or
      rules:
        - op: contains
          path: event/FILE_PATH
          value: shell
        - op: contains
          path: event/FILE_PATH
          value: c99
        - op: contains
          path: event/FILE_PATH
          value: r57
        - op: contains
          path: event/FILE_PATH
          value: wso
respond:
  - action: report
    name: "Suspicious filename in web root - {{ .event.FILE_PATH }}"
    priority: 4
  - action: task
    command: file_info {{ .event.FILE_PATH }}
```

#### Implement Preventive Controls

- Deploy Web Application Firewall (WAF)
- Implement file integrity monitoring for web directories
- Disable unnecessary PHP functions (exec, shell_exec, system)
- Set proper file permissions on web root
- Enable AppArmor/SELinux for web server process
- Implement upload restrictions (file type, size, location)

---

## Scenario 4: Advanced Persistent Threat (APT) Detection

### Overview

This scenario demonstrates detection and investigation of sophisticated attacker techniques including:
- Living-off-the-land binaries (LOLBins)
- Process injection
- Memory-only malware
- Covert C2 channels

### Phase 1: Initial Detection

#### Detection Rule: Suspicious PowerShell Execution

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: powershell.exe
      case sensitive: false
    - op: or
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: -encodedcommand
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: -enc
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: downloadstring
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: invoke-expression
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: iex
          case sensitive: false
respond:
  - action: report
    name: "Suspicious PowerShell execution - {{ .event.COMMAND_LINE }}"
    priority: 4
    metadata:
      mitre: T1059.001

  - action: task
    command: history_dump
    investigation: apt-investigation
```

#### Detection Rule: Process Injection

```yaml
detect:
  event: NEW_REMOTE_THREAD
  op: exists
  path: event/PROCESS/*
respond:
  - action: report
    name: "Process injection detected - remote thread creation"
    priority: 4
    metadata:
      mitre: T1055

  - action: task
    command: mem_map --pid {{ .event.PROCESS_ID }}
    investigation: apt-investigation

  - action: task
    command: history_dump
    investigation: apt-investigation
```

### Phase 2: Investigation

#### Step 1: Analyze PowerShell Activity

```bash
# Get process tree
history_dump

# Decode base64 command line if present
# Use external tool to decode base64 from detection

# Search for PowerShell downloads
```

LCQL queries:

```
# Find all PowerShell executions with suspicious parameters
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with 'powershell.exe' AND event/COMMAND_LINE contains 'download' | event/COMMAND_LINE as command routing/hostname as host routing/event_time as time

# Find encoded PowerShell commands
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains '-enc' | event/COMMAND_LINE as command routing/hostname as host
```

#### Step 2: Memory Analysis

```bash
# Get memory map of suspicious process
mem_map --pid 1234

# Look for injected code (non-file-backed memory)
# Review mem_map output for suspicious regions

# Extract strings from memory
mem_strings --pid 1234

# Search for specific indicators
mem_find_string --pid 1234 --string 'malicious-domain.com'
```

#### Step 3: Network Analysis

```bash
# Get current connections
netstat

# Review connection history
```

LCQL queries:

```
# Find DNS requests for suspicious domains
-12h | DNS_REQUEST | event/DOMAIN_NAME not ends with '.com' AND event/DOMAIN_NAME not ends with '.net' | event/DOMAIN_NAME as domain routing/hostname as host COUNT_UNIQUE(event) as count GROUP BY(domain)

# Find connections to cloud services (potential C2)
-12h | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is public | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst routing/hostname as host

# Look for beaconing behavior (regular connections)
# Requires manual analysis of connection timestamps
```

#### Step 4: Hunt for Related Activity

```
# Find similar PowerShell patterns across environment
-7d | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains 'encodedcommand' | routing/hostname as host COUNT_UNIQUE(event) as count GROUP BY(host)

# Look for lateral movement
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/LogonType == "3" | routing/hostname as host event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as source

# Search for credential access attempts
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains 'mimikatz' OR event/COMMAND_LINE contains 'procdump' OR event/COMMAND_LINE contains 'lsass' | event/COMMAND_LINE as command routing/hostname as host
```

### Phase 3: Containment

```yaml
# Tag affected systems
respond:
  - action: add tag
    tag: apt-infected
    ttl: 86400

# Isolate infected systems
respond:
  - action: isolate network

# Collect forensic data
respond:
  - action: task
    command: history_dump
    investigation: apt-response
  - action: task
    command: os_processes
    investigation: apt-response
  - action: task
    command: netstat
    investigation: apt-response
```

### Phase 4: Artifact Collection

```bash
# Collect memory dump (if dumper extension available)
# Via D&R rule with extension request

# Collect PowerShell logs
artifact_get C:\Windows\System32\winevt\Logs\Microsoft-Windows-PowerShell\Operational.evtx
artifact_get C:\Windows\System32\winevt\Logs\Windows PowerShell.evtx

# Collect Sysmon logs
artifact_get C:\Windows\System32\winevt\Logs\Microsoft-Windows-Sysmon\Operational.evtx

# Collect prefetch files
dir_list C:\Windows\Prefetch
# Collect relevant prefetch files

# Collect browser history (for initial infection vector)
artifact_get C:\Users\*\AppData\Local\Microsoft\Edge\User Data\Default\History
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\History
```

### Phase 5: Eradication

For memory-only threats:

```bash
# Terminate malicious processes
deny_tree <atom_id>

# Reboot system to clear memory-resident malware
# (if appropriate and after forensic collection)
```

For persistent threats:

```bash
# Remove persistence mechanisms
os_autoruns
# Remove identified malicious entries

# Check WMI for persistence
run wmic /namespace:\\root\subscription path __EventFilter get /format:list
run wmic /namespace:\\root\subscription path __EventConsumer get /format:list

# Remove WMI persistence if found
run wmic /namespace:\\root\subscription path __EventFilter where Name="MaliciousFilter" delete
```

---

## Scenario 5: Data Exfiltration Detection

### Overview

Detect and respond to large-scale data exfiltration attempts.

### Detection Rule: Large Data Transfer

```yaml
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
    name: "Large data transfer to external IP - {{ index (index .event.NETWORK_ACTIVITY 0) \"DESTINATION\" \"IP_ADDRESS\" }}"
    priority: 4
    metadata:
      mitre: T1041

  - action: task
    command: history_dump
    investigation: exfiltration

  - action: task
    command: netstat
    investigation: exfiltration

  - action: add tag
    tag: potential-exfiltration
    ttl: 86400
```

### Investigation

```bash
# Review process making connection
history_dump
os_processes

# Check for archiving activity
```

LCQL queries:

```
# Look for archive file creation
-6h | NEW_DOCUMENT | event/FILE_PATH ends with '.zip' OR event/FILE_PATH ends with '.rar' OR event/FILE_PATH ends with '.7z' | event/FILE_PATH as file event/SIZE as size routing/hostname as host

# Find file compression commands
-6h | NEW_PROCESS | event/COMMAND_LINE contains 'compress' OR event/COMMAND_LINE contains 'tar' OR event/COMMAND_LINE contains '7z' OR event/COMMAND_LINE contains 'zip' | event/COMMAND_LINE as command routing/hostname as host
```

### Response

If confirmed malicious:

```yaml
respond:
  - action: isolate network
  - action: task
    command: deny_tree <<routing/this>>
```

---

## Summary

These scenarios demonstrate complete incident response workflows using LimaCharlie:

1. **Ransomware**: Automated containment, investigation, eradication, recovery
2. **Lateral Movement**: Credential compromise detection, scope assessment, remediation
3. **Web Shell**: Web server compromise detection, forensic collection, patching
4. **APT**: Advanced attacker techniques, memory analysis, threat hunting
5. **Data Exfiltration**: Large data transfer detection, investigation

Each scenario follows the IR lifecycle:
- Detection (automated via D&R rules)
- Investigation (LCQL queries, sensor commands)
- Containment (network isolation, process termination)
- Eradication (malware removal, persistence cleanup)
- Recovery (service restoration, monitoring)
- Lessons Learned (rule creation, documentation)

Use these as templates for building your own incident response playbooks.
