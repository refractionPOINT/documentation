---
name: incident-responder
description: Use this skill when the user needs help executing incident response workflows, investigating security incidents, containing threats, collecting forensic evidence, or performing remediation actions.
---

# LimaCharlie Incident Responder

This skill helps you execute comprehensive incident response workflows using LimaCharlie's capabilities. Use this when users need assistance with security incident investigation, threat containment, forensic collection, remediation, and recovery operations.

## Overview

LimaCharlie provides incident response teams with a powerful, centralized solution that enables rapid response to security incidents with real-time visibility, instant deployment, and comprehensive response capabilities. IR teams can detect, investigate, contain, remediate, and recover from threats with unparalleled speed and effectiveness.

### Key IR Capabilities

- **Instant Deployment**: Launch LimaCharlie in seconds, gaining immediate visibility and control
- **Real-time Response**: Execute response actions within 100ms of detection
- **Unified Visibility**: Centralized view across endpoints, networks, and cloud environments
- **Advanced Analytics**: Powerful query language (LCQL) for threat hunting and investigation
- **Automated Response**: D&R rules for automated containment and remediation
- **Forensic Collection**: Comprehensive artifact and evidence gathering
- **Historical Analysis**: One year of historical data for retrospective investigations

## Incident Response Phases

LimaCharlie supports all phases of the incident response lifecycle:

### 1. Detection
- Real-time alerting via D&R rules
- Threat feed integration
- Behavioral detection
- YARA scanning
- Sigma rule support

### 2. Investigation
- Timeline analysis
- LCQL queries for threat hunting
- Process tree visualization
- Historical data analysis
- Artifact examination

### 3. Containment
- Network isolation
- Process termination
- Service control
- Sensor sealing (tamper resistance)
- Tag-based response orchestration

### 4. Eradication
- Malware removal
- Deny tree (kill process and descendants)
- File deletion
- Registry cleanup
- Persistent threat removal

### 5. Recovery
- Network rejoin
- Service restoration
- Monitoring for reinfection
- System validation

### 6. Lessons Learned
- Detection tuning
- D&R rule creation from findings
- Automated prevention of similar attacks
- Timeline reconstruction

## Investigation Tools and Techniques

### Timeline Analysis

Every sensor maintains a complete timeline of activities. Use the Timeline view to:

- Examine process execution history
- Review network connections
- Analyze file system changes
- Investigate user activities
- Trace lateral movement

**Key Timeline Commands:**

```bash
# Dump recent process history
history_dump

# Get current running processes
os_processes

# View network connections
netstat

# List directory contents
dir_list C:\Users\

# Get file information
file_info C:\path\to\suspicious.exe

# Calculate file hash
file_hash C:\path\to\suspicious.exe
```

### LCQL Queries for Investigation

LCQL (LimaCharlie Query Language) enables powerful searches across telemetry. Common investigation queries:

#### Search for Process Execution
```
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains 'powershell' | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

#### Find Network Connections to Suspicious IPs
```
-12h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS == '192.0.2.100' | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/PORT as port routing/hostname as host
```

#### Search for File Modifications
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

### Process Investigation

**Get process information:**
```bash
# List all running processes
os_processes

# Get memory map of a process
mem_map --pid 1234

# Search process memory for strings
mem_find_string --pid 1234 --string 'password'

# Dump process memory region
mem_read --pid 1234 --base 0x400000 --size 4096

# List handles held by a process (Windows)
mem_handles --pid 1234
```

### Network Investigation

**Analyze network activity:**
```bash
# Get current network connections
netstat

# Resolve DNS name
dns_resolve malicious-domain.com

# View network activity from timeline
# Use Timeline view or LCQL:
# -1h | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is public
```

### File System Investigation

**Examine files and directories:**
```bash
# List directory contents
dir_list C:\Windows\Temp

# Get file metadata
file_info C:\suspicious.exe

# Calculate file hash
file_hash C:\suspicious.exe

# Find files by hash in directory
dir_find_hash C:\Users\ --hash abc123...

# Search for hidden modules (Windows/Linux)
hidden_module_scan
```

### Registry Investigation (Windows)

**Examine persistence mechanisms:**
```bash
# Get autorun entries
os_autoruns

# Check installed services
os_services

# List installed packages/software
os_packages
```

### Memory Analysis

**Search memory for indicators:**
```bash
# Find strings in process memory
mem_strings --pid 1234

# Search for specific string
mem_find_string --pid 1234 --string 'malware-indicator'

# Find open handles to files/registry (Windows)
mem_find_handle --pid 1234 --path 'C:\suspicious'
```

## Containment Actions

When an incident is confirmed, immediate containment prevents further damage.

### Network Isolation

**Isolate endpoint from network (maintains LC connectivity):**

Via D&R rule:
```yaml
detect:
  event: YARA_DETECTION
  op: exists
  path: event/RULE_NAME
respond:
  - action: report
    name: "Malware detected - isolating host"
    priority: 5
  - action: isolate network
  - action: task
    command: history_dump
```

Via sensor command:
```bash
# Isolate from network (stateful, persists across reboots)
# Use 'isolate network' action in D&R rule

# Temporary isolation (stateless, does not persist)
segregate_network
```

**Remove isolation:**
```yaml
respond:
  - action: rejoin network
```

Or via command:
```bash
rejoin_network
```

### Process Termination

**Kill malicious processes:**

Via D&R rule:
```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: malware.exe
      case sensitive: false
respond:
  - action: report
    name: "Malware process detected - terminating"
  - action: task
    command: deny_tree <<routing/this>>
```

Via sensor command:
```bash
# Kill specific process
os_kill_process --pid 1234

# Kill process and all descendants (recommended)
deny_tree <atom_id>

# Suspend process (for analysis before termination)
os_suspend --pid 1234

# Resume suspended process
os_resume --pid 1234
```

### Service Control

**Stop malicious services:**
```bash
# List services
os_services

# Note: Stopping services requires running commands via sensor
# Use run command to execute service stop:
run sc stop "MaliciousService"
```

### File Quarantine

**Remove or quarantine malicious files:**
```bash
# Delete file
file_del C:\malware.exe

# Move file to quarantine location
file_mov C:\malware.exe C:\Quarantine\malware.exe
```

### Sensor Sealing

**Enable tamper resistance:**

Via D&R rule:
```yaml
detect:
  event: YARA_DETECTION
  op: exists
  path: event/PROCESS/*
respond:
  - action: seal
  - action: report
    name: "Active malware - sensor sealed"
```

Via sensor command:
```bash
# Enable seal (prevents sensor modification)
seal

# Remove seal (when remediation is complete)
# Use 'unseal' action in D&R rule
```

### Logoff User

**Force user logoff:**
```bash
# Log off current user
logoff
```

## Forensic Collection

Collect evidence during incident response for analysis and compliance.

### Artifact Collection

The Artifact extension provides comprehensive collection capabilities.

**Common artifacts to collect:**

1. **Suspicious executables:**
```bash
artifact_get C:\Users\victim\Downloads\suspicious.exe
```

2. **Document files:**
```bash
artifact_get C:\Users\victim\Documents\ransom-note.txt
```

3. **Windows Event Logs:**
```yaml
# Via Artifact Collection rules (configured in web UI)
# Pattern: wel://Security
# Pattern: wel://System
# Pattern: wel://Application
# Pattern: wel://Microsoft-Windows-Sysmon/Operational

# Or collect .evtx files directly:
artifact_get C:\Windows\System32\winevt\Logs\Security.evtx
```

4. **Registry hives (for offline analysis):**
```bash
artifact_get C:\Windows\System32\config\SYSTEM
artifact_get C:\Windows\System32\config\SOFTWARE
```

5. **Browser history/cache:**
```bash
artifact_get C:\Users\victim\AppData\Local\Google\Chrome\User Data\Default\History
```

6. **Prefetch files (Windows):**
```bash
dir_list C:\Windows\Prefetch
# Then collect specific prefetch files
artifact_get C:\Windows\Prefetch\MALWARE.EXE-ABC12345.pf
```

### Memory Dumps

**Capture process memory:**
```yaml
# Use dumper extension via D&R rule
respond:
  - action: extension request
    extension name: dumper
    extension action: dump
    extension request:
      sid: '{{ .routing.sid }}'
      pid: '{{ .event.PROCESS_ID }}'
```

### Network Packet Capture

**Capture network traffic (Linux only):**
```yaml
# Configure PCAP capture via Artifact Collection rules
# Pattern: pcap://eth0
```

### Timeline Export

**Export sensor timeline for analysis:**
```bash
# Dump recent process history
history_dump

# Get comprehensive system state
os_processes
os_services
os_autoruns
netstat
```

### File Metadata Collection

**Gather file information without retrieval:**
```bash
# Get file metadata
file_info C:\suspicious.exe

# Calculate hash
file_hash C:\suspicious.exe

# Get code signature details
# View CODE_IDENTITY events in timeline
```

## Remediation Procedures

### Malware Removal Workflow

Complete workflow for removing malware:

```yaml
detect:
  event: YARA_DETECTION
  op: and
  rules:
    - op: exists
      path: event/PROCESS/*
    - op: exists
      path: event/RULE_NAME
respond:
  # 1. Alert
  - action: report
    name: "Active malware detected - {{ .event.RULE_NAME }}"
    priority: 5
    metadata:
      description: "Malware running in memory"
      remediation: "Automated containment initiated"

  # 2. Tag for tracking
  - action: add tag
    tag: malware-incident
    ttl: 86400

  # 3. Collect forensics
  - action: task
    command: history_dump
    investigation: malware-investigation

  # 4. Isolate network
  - action: isolate network

  # 5. Terminate malicious process
  - action: task
    command: deny_tree <<routing/this>>

  # 6. Wait for process termination
  - action: wait
    duration: 5s

  # 7. Delete malicious file
  - action: task
    command: file_del {{ .event.FILE_PATH }}
```

### Lateral Movement Response

Respond to lateral movement detection:

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
    name: "Lateral movement via PsExec from external IP"
    priority: 5

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

### Data Exfiltration Response

Respond to suspicious data transfer:

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

### Persistence Removal

Remove malware persistence mechanisms:

```bash
# 1. Identify persistence
os_autoruns

# 2. Review services
os_services

# 3. Remove malicious autorun entries (via run command)
run reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v MalwareName /f

# 4. Stop and remove malicious service
run sc stop MalwareService
run sc delete MalwareService

# 5. Remove scheduled tasks
run schtasks /delete /tn MalwareTask /f

# 6. Verify removal
os_autoruns
os_services
```

## Complete Incident Response Scenarios

### Scenario 1: Ransomware Response

**Detection to Recovery workflow:**

```yaml
# Detection Rule 1: Detect ransomware behavior
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

  # Immediate containment
  - action: isolate network

  - action: task
    command: deny_tree <<routing/this>>

  # Forensic collection
  - action: task
    command: history_dump
    investigation: ransomware-incident

  - action: add tag
    tag: ransomware-infected
    ttl: 86400

# Detection Rule 2: Detect ransom note creation
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
respond:
  - action: report
    name: "Ransom note detected - {{ .event.FILE_PATH }}"

  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
    investigation: ransomware-incident
```

**Manual remediation steps:**

1. **Contain:**
   - Network isolation already applied via D&R
   - Verify no other systems infected

2. **Investigate:**
   ```bash
   # Review timeline for initial infection vector
   history_dump

   # Check for other malware
   os_processes

   # Look for persistence
   os_autoruns
   ```

3. **Eradicate:**
   ```bash
   # Kill ransomware process (already done via deny_tree)

   # Remove persistence
   os_autoruns  # identify malicious entries
   run reg delete "HKCU\...\Run" /v RansomwareName /f

   # Delete ransomware binary
   file_del C:\path\to\ransomware.exe
   ```

4. **Recover:**
   - Restore files from backup
   - Verify system integrity
   - Remove network isolation via `rejoin network` action

5. **Post-Incident:**
   - Create D&R rules to prevent similar attacks
   - Update YARA rules
   - Document lessons learned

### Scenario 2: Compromised Credentials / Lateral Movement

**Detection:**

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

  - action: task
    command: history_dump
    investigation: lateral-movement

  - action: add tag
    tag: suspicious-logons
    ttl: 3600
```

**Investigation queries:**

```
# Find all systems accessed by suspicious user
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/TargetUserName == "compromised_user" | routing/hostname as host event/EVENT/EventData/LogonType as type event/EVENT/EventData/IpAddress as source

# Find all logons from suspicious source IP
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/IpAddress == "10.0.1.50" | routing/hostname as target event/EVENT/EventData/TargetUserName as user

# Hunt for PsExec usage
-24h | plat == windows | * | event/* contains 'psexec'
```

**Response:**

1. **Contain spread:**
   - Isolate all affected systems
   - Disable compromised account

2. **Investigate scope:**
   - Identify all accessed systems
   - Review activities on each system
   - Determine data accessed/exfiltrated

3. **Eradicate:**
   - Remove attacker persistence
   - Reset compromised credentials
   - Clear malicious scheduled tasks

4. **Recover:**
   - Verify no backdoors remain
   - Rejoin systems to network
   - Monitor for re-compromise

### Scenario 3: Web Shell / Initial Access

**Detection:**

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
            value: sh
respond:
  - action: report
    name: "Web server spawning suspicious process - possible web shell"
    priority: 5

  - action: task
    command: history_dump
    investigation: web-shell

  - action: task
    command: deny_tree <<routing/this>>

  - action: add tag
    tag: web-shell-detected
```

**Investigation:**

```bash
# Find suspicious files in web root
dir_list /var/www/html
dir_list C:\inetpub\wwwroot

# Get file info for suspicious files
file_info /var/www/html/shell.php
file_hash /var/www/html/shell.php

# Collect web server logs
artifact_get /var/log/apache2/access.log
artifact_get C:\inetpub\logs\LogFiles\W3SVC1\u_ex*.log

# Review network connections
netstat
```

**Remediation:**

```bash
# 1. Terminate malicious processes (already done)

# 2. Collect the web shell for analysis
artifact_get /var/www/html/shell.php

# 3. Delete web shell
file_del /var/www/html/shell.php

# 4. Check for other backdoors
dir_list /var/www/html --recurse

# 5. Review recently modified files
# Use LCQL to find recent NEW_DOCUMENT events

# 6. Patch vulnerable application
```

## Best Practices

### Investigation Best Practices

1. **Work from a hypothesis**: Develop theories based on initial indicators and test them
2. **Document everything**: Maintain detailed notes of all actions and findings
3. **Preserve evidence**: Collect artifacts before making changes
4. **Use investigation IDs**: Group related sensor commands with investigation parameter
5. **Timeline analysis first**: Review sensor timeline before issuing commands
6. **Query broadly, then narrow**: Start with wide searches, refine based on findings
7. **Cross-reference indicators**: Correlate findings across multiple data sources
8. **Track attacker TTPs**: Map observed behaviors to MITRE ATT&CK framework

### Containment Best Practices

1. **Isolate early**: When in doubt, isolate to prevent spread
2. **Maintain communication**: Network isolation preserves LC connectivity
3. **Tag affected systems**: Use tags to track incident scope
4. **Kill process trees**: Use deny_tree instead of os_kill_process
5. **Seal sensors**: Enable tamper resistance on compromised systems
6. **Gradual recovery**: Test systems before rejoining network
7. **Verify effectiveness**: Confirm containment actions succeeded
8. **Have rollback plan**: Know how to reverse containment if needed

### Forensic Collection Best Practices

1. **Collect volatile data first**: Memory, network connections, running processes
2. **Hash before collection**: Calculate hashes before moving/deleting files
3. **Use investigation IDs**: Group related collections
4. **Preserve timelines**: Export timeline data before remediation
5. **Document chain of custody**: Track what was collected, when, and by whom
6. **Collect context**: Get surrounding artifacts, not just the malicious file
7. **Monitor collection impact**: Artifact collection uses bandwidth and storage
8. **Automate when possible**: Use D&R rules for automatic collection

### Remediation Best Practices

1. **Test in staging**: Validate remediation steps before production deployment
2. **Automate cautiously**: Start with manual remediation, automate after validation
3. **Use suppression**: Prevent remediation actions from running away
4. **Verify success**: Check that remediation actions completed successfully
5. **Monitor for reinfection**: Watch for indicators returning after remediation
6. **Address root cause**: Don't just remove malware, fix the vulnerability
7. **Document procedures**: Create runbooks for common incidents
8. **Gradual automation**: Incrementally automate response as confidence grows

### D&R Rule Development for IR

1. **Start with detection**: Create detection rules before automated response
2. **Test with replay**: Use replay service to test against historical data
3. **Use priority levels**: Assign appropriate priority (1-5) to detections
4. **Include metadata**: Add author, MITRE ATT&CK, remediation guidance
5. **Chain detections**: Build higher-order detections from multiple signals
6. **Tune false positives**: Create FP rules for known benign behaviors
7. **Use stateful rules**: Detect behavior patterns, not single events
8. **Limit scope when testing**: Use `__` prefix for internal-only detections

### Response Automation Guidelines

**When to automate:**
- High-confidence detections (known malware signatures)
- Well-tested containment actions (network isolation)
- Non-destructive collection (artifact_get, history_dump)
- Repetitive tasks (tagging, reporting)

**When to require human approval:**
- Destructive actions (file deletion, account lockout)
- Business-critical systems
- Ambiguous detections
- Novel attack patterns
- Production environment changes

**Progressive automation approach:**

1. **Phase 1 - Alert only:**
   ```yaml
   respond:
     - action: report
       name: suspicious-behavior
   ```

2. **Phase 2 - Alert + collect:**
   ```yaml
   respond:
     - action: report
       name: suspicious-behavior
     - action: task
       command: history_dump
   ```

3. **Phase 3 - Alert + collect + contain:**
   ```yaml
   respond:
     - action: report
       name: suspicious-behavior
     - action: task
       command: history_dump
     - action: isolate network
   ```

4. **Phase 4 - Full automation:**
   ```yaml
   respond:
     - action: report
       name: malware-detected
     - action: task
       command: history_dump
     - action: isolate network
     - action: task
       command: deny_tree <<routing/this>>
     - action: wait
       duration: 5s
     - action: task
       command: file_del {{ .event.FILE_PATH }}
   ```

## Response Action Reference

### Quick Command Reference

**Investigation Commands:**
```bash
history_dump                    # Recent process history
os_processes                    # Running processes
os_services                     # Installed services
os_autoruns                     # Persistence mechanisms
netstat                         # Network connections
file_info <path>               # File metadata
file_hash <path>               # Calculate hash
dir_list <path>                # Directory listing
mem_strings --pid <pid>        # Extract strings from memory
```

**Containment Commands:**
```bash
# Via D&R actions:
isolate network                 # Isolate from network (stateful)
segregate_network              # Isolate from network (stateless)
deny_tree <atom_id>            # Kill process tree
os_kill_process --pid <pid>    # Kill specific process
seal                           # Enable tamper resistance
logoff                         # Force user logoff
```

**Collection Commands:**
```bash
artifact_get <path>            # Collect file
os_packages                    # List installed software
os_users                       # List user accounts
log_get <log_name>            # Collect Windows event log (Windows)
```

**Remediation Commands:**
```bash
file_del <path>                # Delete file
file_mov <src> <dst>           # Move file
rejoin_network                 # Remove network isolation
unseal                         # Remove tamper resistance
```

### D&R Action Reference

**Reporting:**
```yaml
- action: report
  name: detection-name
  priority: 1-5
  metadata:
    author: analyst@company.com
    mitre: T1059.001
```

**Containment:**
```yaml
- action: isolate network      # Isolate from network
- action: rejoin network       # Remove isolation
- action: seal                 # Enable tamper resistance
- action: unseal               # Disable tamper resistance
```

**Tagging:**
```yaml
- action: add tag
  tag: incident-tag
  ttl: 86400                   # Optional: seconds until expiry
  entire_device: false         # Optional: tag all sensors on device
```

**Sensor Commands:**
```yaml
- action: task
  command: history_dump
  investigation: incident-id   # Optional: group related tasks
  suppression:                 # Optional: prevent runaway
    is_global: false
    keys:
      - '{{ .event.PROCESS_ID }}'
    max_count: 1
    period: 5m
```

**Extension Requests:**
```yaml
- action: extension request
  extension name: dumper
  extension action: dump
  extension request:
    sid: '{{ .routing.sid }}'
    pid: '{{ .event.PROCESS_ID }}'
```

**Delays:**
```yaml
- action: wait
  duration: 5s                 # Wait before next action
```

## Common Incident Response Patterns

### Pattern 1: Detect → Alert → Investigate

For low-confidence detections requiring human review:

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: suspicious-string
respond:
  - action: report
    name: suspicious-activity
    priority: 2
  - action: task
    command: history_dump
    investigation: suspicious-process
  - action: add tag
    tag: needs-review
    ttl: 86400
```

### Pattern 2: Detect → Contain → Alert → Investigate

For high-confidence detections requiring immediate containment:

```yaml
detect:
  event: YARA_DETECTION
  op: exists
  path: event/RULE_NAME
respond:
  - action: isolate network
  - action: report
    name: "Malware detected - host isolated"
    priority: 5
  - action: task
    command: history_dump
    investigation: malware-incident
  - action: add tag
    tag: malware-infected
```

### Pattern 3: Detect → Investigate → Contain → Remediate

For confirmed threats requiring full response:

```yaml
detect:
  event: YARA_DETECTION
  op: and
  rules:
    - op: exists
      path: event/PROCESS/*
    - op: exists
      path: event/RULE_NAME
respond:
  - action: report
    name: "Active malware - initiating response"
    priority: 5
  - action: task
    command: history_dump
    investigation: malware
  - action: isolate network
  - action: task
    command: deny_tree <<routing/this>>
  - action: wait
    duration: 5s
  - action: task
    command: file_del {{ .event.FILE_PATH }}
```

### Pattern 4: Behavioral Detection with Threshold

For detecting anomalous repetitive behavior:

```yaml
detect:
  event: WEL
  op: is windows
  with events:
    event: WEL
    op: is
    path: event/EVENT/System/EventID
    value: '4625'
    count: 5
    within: 300
respond:
  - action: report
    name: brute-force-attempt
    priority: 4
  - action: add tag
    tag: brute-force
    ttl: 3600
```

### Pattern 5: Threat Feed Lookup → Automated Response

For known bad indicators:

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malware-domains
respond:
  - action: report
    name: "DNS to known malicious domain - {{ .event.DOMAIN_NAME }}"
    priority: 5
  - action: isolate network
  - action: task
    command: history_dump
    investigation: malicious-dns
```

## Integration with IR Workflows

### Integration with SIEM/SOAR

LimaCharlie can integrate with external systems:

1. **Send detections to SIEM**: Configure Outputs to forward detections
2. **Receive commands from SOAR**: Use API to trigger response actions
3. **Enrich SIEM data**: Send LC telemetry to SIEM for correlation
4. **Bi-directional integration**: SIEM triggers LC response, LC updates SIEM

### Evidence Export

Export evidence for legal/compliance requirements:

1. **Timeline export**: Use historical queries to extract relevant events
2. **Artifact collection**: Collect files and logs via artifact_get
3. **Detection export**: Export detection reports via API
4. **Chain of custody**: Document all collection activities

### Ticketing Integration

Integrate with ticketing systems:

1. **Auto-create tickets**: Use Outputs to create tickets from detections
2. **Update tickets**: Use API to update ticket status during response
3. **Close loop**: Close tickets when incident resolved
4. **Metrics tracking**: Track MTTR, incident count, etc.

## Troubleshooting

### Common Issues

**Sensor command not executing:**
- Verify sensor is online (check connectivity status)
- Check sensor platform supports command (see command reference)
- Review sensor errors in timeline
- Verify command syntax is correct

**Network isolation not working:**
- Verify platform supports segregate_network command
- Check if sensor has necessary permissions
- Review sensor timeline for SEGREGATE_NETWORK event
- Test with stateless segregate_network command first

**Artifact collection failing:**
- Verify Artifact extension is enabled
- Check file path is correct (case-sensitive on Linux)
- Verify sensor has read access to file
- Check artifact size limits

**D&R rule not matching:**
- Use replay service to test rule
- Enable trace mode to see where rule fails
- Verify event type and path syntax
- Check case sensitivity settings

**False positives:**
- Create false positive rules to filter benign detections
- Add more specific matching criteria
- Use stateful rules to require multiple correlated events
- Implement threshold activation with min_count

## Additional Resources

### Key Documentation Links

- Detection & Response Rules: Reference for D&R rule syntax
- Sensor Commands: Complete list of available commands
- LCQL: Query language documentation and examples
- Response Actions: Detailed action parameter reference
- Artifact Collection: Forensic collection capabilities

### CLI Commands

```bash
# Query historical data
limacharlie query --query "-24h | plat == windows | NEW_PROCESS"

# Test D&R rule
limacharlie replay --rule-content rule.yaml --events test-event.json

# Send sensor command
limacharlie task --sid SENSOR_ID --command "history_dump"

# Export detections
limacharlie detections --last-seconds 86400 --output detections.json
```

### Response Time Guidelines

- **Critical incidents (malware, ransomware)**: Immediate automated containment
- **High priority (lateral movement, exfiltration)**: <5 minute response
- **Medium priority (suspicious behavior)**: <30 minute response
- **Low priority (policy violations)**: <4 hour response

### Incident Severity Matrix

**Priority 5 - Critical:**
- Active malware/ransomware
- Data exfiltration in progress
- Widespread compromise
- Business-critical system impacted

**Priority 4 - High:**
- Lateral movement
- Privilege escalation
- Known malicious indicators
- Multiple systems affected

**Priority 3 - Medium:**
- Suspicious behavior patterns
- Policy violations
- Unauthorized access attempts
- Single system affected

**Priority 2 - Low:**
- Anomalous activity
- Failed attack attempts
- Potential false positives
- Minimal business impact

**Priority 1 - Informational:**
- Benign events requiring logging
- Compliance monitoring
- Baseline tracking

## Summary

LimaCharlie provides comprehensive incident response capabilities across all phases:

- **Detect**: Real-time alerting with D&R rules and threat feeds
- **Investigate**: Timeline analysis, LCQL queries, and sensor commands
- **Contain**: Network isolation, process termination, sensor sealing
- **Eradicate**: Malware removal, persistence elimination
- **Recover**: Service restoration, network rejoin
- **Learn**: D&R rule creation, automated prevention

Use this skill to guide users through complete IR workflows, from initial detection through final remediation and lessons learned. Always emphasize testing, documentation, and gradual automation of response actions.
