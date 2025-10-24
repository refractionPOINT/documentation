---
name: incident-responder
description: Use this skill when the user needs help executing incident response workflows, investigating security incidents, containing threats, collecting forensic evidence, or performing remediation actions.
---

# LimaCharlie Incident Responder

This skill helps you execute comprehensive incident response workflows using LimaCharlie's capabilities. Use this when users need assistance with security incident investigation, threat containment, forensic collection, remediation, and recovery operations.

## Overview

LimaCharlie provides incident response teams with a powerful, centralized solution that enables rapid response to security incidents with real-time visibility, instant deployment, and comprehensive response capabilities.

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

1. **Detection**: Real-time alerting via D&R rules, threat feeds, behavioral detection, YARA scanning
2. **Investigation**: Timeline analysis, LCQL queries, process trees, historical data analysis
3. **Containment**: Network isolation, process termination, sensor sealing, tag-based orchestration
4. **Eradication**: Malware removal, deny tree, file deletion, persistence cleanup
5. **Recovery**: Network rejoin, service restoration, reinfection monitoring
6. **Lessons Learned**: Detection tuning, D&R rule creation, automated prevention

## Quick Response Guide

### Immediate Containment

**Network Isolation:**
```yaml
respond:
  - action: isolate network
```

**Process Termination:**
```yaml
respond:
  - action: task
    command: deny_tree <<routing/this>>
```

**Sensor Protection:**
```yaml
respond:
  - action: seal
```

### Essential Commands

```bash
history_dump                    # Recent process history
os_processes                    # Running processes
netstat                         # Network connections
file_info <path>               # File metadata
file_hash <path>               # Calculate hash
os_autoruns                     # Persistence mechanisms (Windows)
artifact_get <path>            # Collect file
```

## Investigation Tools

### Timeline Analysis

Every sensor maintains a complete timeline. Key commands:
- `history_dump` - Recent process history
- `os_processes` - Current processes
- `netstat` - Network connections
- `dir_list <path>` - Directory contents
- `file_info <path>` - File metadata

### LCQL Queries

**Process Execution:**
```
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains 'powershell' | event/FILE_PATH as path routing/hostname as host
```

**Network Connections:**
```
-12h | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS == '192.0.2.100' | event/FILE_PATH as process routing/hostname as host
```

**Lateral Movement:**
```
-24h | * | event/* contains 'psexec' | routing/hostname as host routing/event_type as event
```

See REFERENCE.md for complete LCQL syntax.

### Process Investigation

```bash
os_processes                            # List all processes
mem_map --pid <pid>                    # Memory map
mem_find_string --pid <pid> --string <str>  # Search memory
mem_handles --pid <pid>                # Handles (Windows)
```

### File System Investigation

```bash
dir_list <path>                        # List directory
file_info <path>                       # File metadata
file_hash <path>                       # Calculate hash
dir_find_hash <dir> --hash <hash>     # Find by hash
hidden_module_scan                     # Rootkit detection
```

### Registry Investigation (Windows)

```bash
os_autoruns                            # Autorun entries
os_services                            # Services
os_packages                            # Installed software
os_users                               # User accounts
```

## Containment Actions

### Network Isolation

**Stateful (persists across reboot):**
```yaml
respond:
  - action: isolate network
```

**Stateless (does not persist):**
```bash
segregate_network
```

**Remove isolation:**
```yaml
respond:
  - action: rejoin network
```

### Process Control

```yaml
# Kill process tree (recommended)
respond:
  - action: task
    command: deny_tree <<routing/this>>
```

```bash
# Manual commands
os_kill_process --pid <pid>            # Kill process
os_suspend --pid <pid>                 # Suspend
os_resume --pid <pid>                  # Resume
```

### File Operations

```bash
file_del <path>                        # Delete file
file_mov <source> <dest>               # Move/quarantine
```

### Sensor Protection

```yaml
respond:
  - action: seal                       # Enable tamper resistance
  - action: unseal                     # Remove tamper resistance
```

## Forensic Collection

```bash
# Collect files
artifact_get <path>

# Windows Event Logs
artifact_get C:\Windows\System32\winevt\Logs\Security.evtx

# Browser history
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\History

# Prefetch files (Windows)
artifact_get C:\Windows\Prefetch\*.pf

# Timeline export
history_dump
os_processes
os_autoruns
netstat
```

## Common IR Workflows

### Workflow 1: Malware Response

```yaml
detect:
  event: YARA_DETECTION
  op: exists
  path: event/PROCESS/*
respond:
  - action: report
    name: "Active malware detected"
    priority: 5
  - action: task
    command: history_dump
    investigation: malware-incident
  - action: isolate network
  - action: task
    command: deny_tree <<routing/this>>
  - action: wait
    duration: 5s
  - action: task
    command: file_del {{ .event.FILE_PATH }}
  - action: add tag
    tag: malware-incident
    ttl: 86400
```

### Workflow 2: Lateral Movement

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: psexec
  case sensitive: false
respond:
  - action: report
    name: "Lateral movement via PsExec"
    priority: 5
  - action: isolate network
  - action: task
    command: history_dump
    investigation: lateral-movement
  - action: add tag
    tag: lateral-movement-victim
```

### Workflow 3: Web Shell

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/PARENT/FILE_PATH
  value: w3wp.exe
  with child:
    op: ends with
    event: NEW_PROCESS
    path: event/FILE_PATH
    value: cmd.exe
respond:
  - action: report
    name: "Web shell detected"
    priority: 5
  - action: task
    command: deny_tree <<routing/this>>
```

### Workflow 4: Ransomware

```yaml
detect:
  event: NEW_DOCUMENT
  op: contains
  path: event/FILE_PATH
  value: .encrypted
  with events:
    event: NEW_DOCUMENT
    op: contains
    path: event/FILE_PATH
    value: .encrypted
    count: 10
    within: 60
respond:
  - action: report
    name: "Ransomware detected"
    priority: 5
  - action: isolate network
  - action: task
    command: deny_tree <<routing/this>>
  - action: seal
```

See EXAMPLES.md for complete step-by-step scenarios.

## Best Practices

### Investigation
1. Work from hypothesis - develop and test theories
2. Document everything - maintain detailed notes
3. Preserve evidence - collect before changing
4. Use investigation IDs - group related actions
5. Timeline first - review before issuing commands
6. Cross-reference - correlate across data sources

### Containment
1. Isolate early - prevent spread
2. Maintain communication - LC connectivity preserved
3. Tag systems - track incident scope
4. Kill process trees - use deny_tree
5. Seal sensors - enable tamper resistance
6. Verify effectiveness - confirm actions succeeded

### Forensic Collection
1. Volatile data first - memory, network, processes
2. Hash before collection - document integrity
3. Use investigation IDs - group collections
4. Preserve timelines - export before remediation
5. Chain of custody - track what, when, who
6. Automate collection - use D&R rules

### Response Automation

**Automate:**
- High-confidence detections (known malware)
- Non-destructive actions (collection, tagging)
- Well-tested containment (network isolation)

**Require approval:**
- Destructive actions (file deletion)
- Business-critical systems
- Novel/ambiguous threats

**Progressive approach:**
1. Alert only
2. Alert + collect
3. Alert + collect + contain
4. Full automation

## Quick Command Reference

### Investigation
```bash
history_dump                    # Process history
os_processes                    # Running processes
os_services                     # Services
os_autoruns                     # Persistence
netstat                         # Network connections
file_info <path>               # File metadata
file_hash <path>               # File hash
dir_list <path>                # Directory listing
mem_strings --pid <pid>        # Memory strings
```

### Containment
```bash
isolate network                 # Network isolation (D&R action)
segregate_network              # Network isolation (command)
deny_tree <atom_id>            # Kill process tree
os_kill_process --pid <pid>    # Kill process
seal                           # Tamper resistance (D&R action)
```

### Collection
```bash
artifact_get <path>            # Collect file
os_packages                    # Installed software
os_users                       # User accounts
log_get <log_name>            # Event log (Windows)
```

### Remediation
```bash
file_del <path>                # Delete file
file_mov <src> <dst>           # Move file
rejoin_network                 # Remove isolation
unseal                         # Remove seal (D&R action)
```

## D&R Actions Reference

**Report:**
```yaml
- action: report
  name: detection-name
  priority: 1-5
```

**Containment:**
```yaml
- action: isolate network
- action: rejoin network
- action: seal
- action: unseal
```

**Tagging:**
```yaml
- action: add tag
  tag: incident-tag
  ttl: 86400
```

**Task:**
```yaml
- action: task
  command: history_dump
  investigation: incident-id
  suppression:
    is_global: false
    max_count: 1
    period: 5m
```

**Wait:**
```yaml
- action: wait
  duration: 5s
```

## Navigation

### SKILL.md (This Document)
- IR overview and methodology
- Quick response guide
- Essential investigation tools
- Common IR workflows
- Best practices

### REFERENCE.md
Complete technical reference:
- All sensor commands with syntax
- All D&R response actions
- Complete LCQL query syntax
- Event field paths and template variables
- Platform-specific notes

### EXAMPLES.md
Complete IR scenarios with step-by-step workflows:
- Ransomware detection and response
- Compromised credentials and lateral movement
- Web shell detection and remediation
- Advanced persistent threat investigation
- Data exfiltration detection

### TROUBLESHOOTING.md
Problem-solving guidance:
- Sensor command issues
- Network isolation problems
- D&R rule troubleshooting
- LCQL query issues
- Investigation challenges
- Escalation guidance

## Response Time Guidelines

- **Critical** (malware, ransomware): Immediate automated containment
- **High priority** (lateral movement): <5 minute response
- **Medium priority** (suspicious behavior): <30 minute response
- **Low priority** (policy violations): <4 hour response

## Incident Severity Matrix

**Priority 5 - Critical:** Active malware, data exfiltration, widespread compromise, critical system impact

**Priority 4 - High:** Lateral movement, privilege escalation, known malicious indicators, multiple systems

**Priority 3 - Medium:** Suspicious behavior, policy violations, unauthorized access, single system

**Priority 2 - Low:** Anomalous activity, failed attacks, potential false positives, minimal impact

**Priority 1 - Informational:** Benign events, compliance monitoring, baseline tracking

## Summary

LimaCharlie provides comprehensive incident response capabilities:

- **Detect**: Real-time alerting with D&R rules and threat feeds
- **Investigate**: Timeline analysis, LCQL queries, sensor commands
- **Contain**: Network isolation, process termination, sensor sealing
- **Eradicate**: Malware removal, persistence elimination
- **Recover**: Service restoration, network rejoin
- **Learn**: D&R rule creation, automated prevention

Use this skill to guide users through complete IR workflows. Always emphasize testing, documentation, and gradual automation.

For detailed syntax: REFERENCE.md
For complete scenarios: EXAMPLES.md
For troubleshooting: TROUBLESHOOTING.md
