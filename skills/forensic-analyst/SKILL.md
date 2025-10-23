---
name: forensic-analyst
description: Use this skill when users need to conduct digital forensics investigations, perform timeline reconstruction, analyze memory dumps, examine artifacts, or build comprehensive forensic reports using LimaCharlie's forensic capabilities.
---

# LimaCharlie Forensic Analyst

This skill provides expert guidance for conducting comprehensive digital forensics investigations using LimaCharlie. Use this skill to help users perform deep forensic analysis, reconstruct attack timelines, analyze artifacts, and build evidence-based forensic reports.

## Table of Contents

1. [Digital Forensics Overview](#digital-forensics-overview)
2. [Forensic Methodology](#forensic-methodology)
3. [Memory Analysis](#memory-analysis)
4. [Process Analysis](#process-analysis)
5. [File Analysis](#file-analysis)
6. [Timeline Reconstruction](#timeline-reconstruction)
7. [Artifact Examination](#artifact-examination)
8. [Registry Analysis](#registry-analysis)
9. [Network Analysis](#network-analysis)
10. [Evidence Preservation](#evidence-preservation)
11. [Forensic Investigation Scenarios](#forensic-investigation-scenarios)
12. [Reporting and Documentation](#reporting-and-documentation)

---

## Digital Forensics Overview

### What is Digital Forensics?

Digital forensics is the systematic process of collecting, preserving, analyzing, and presenting digital evidence from computer systems, networks, and storage devices. In LimaCharlie, forensic investigations leverage real-time endpoint visibility, historical telemetry, and comprehensive artifact collection to reconstruct security incidents and understand attacker behavior.

### Key Forensic Principles

1. **Evidence Preservation**: Maintain integrity of evidence from collection to presentation
2. **Chain of Custody**: Document all evidence handling and access
3. **Non-Destructive Analysis**: Analyze without altering original evidence
4. **Repeatability**: Ensure investigations can be replicated with same results
5. **Documentation**: Maintain detailed records of all investigative steps
6. **Timeline Construction**: Establish chronological sequence of events
7. **Context Awareness**: Understand evidence within system and business context

### Types of Forensic Investigations

**Incident Response Forensics**:
- Analyzing active security incidents
- Identifying attack vectors and scope
- Containing ongoing threats
- Collecting volatile evidence

**Post-Incident Forensics**:
- Reconstructing completed attacks
- Understanding full impact
- Identifying persistence mechanisms
- Supporting legal proceedings

**Proactive Forensics**:
- Threat hunting investigations
- Baseline establishment
- Anomaly detection
- Security posture assessment

**Compliance Forensics**:
- Audit trail analysis
- Policy violation investigation
- Regulatory evidence collection
- Internal investigations

---

## Forensic Methodology

### 1. Identification Phase

**Determine Investigation Scope**:
- What systems are affected?
- What is the suspected timeframe?
- What type of incident (malware, intrusion, data theft)?
- What evidence sources are available?

**Identify Key Indicators**:
- Known malicious files, hashes, or domains
- Suspicious process names or command lines
- Unusual network connections
- Anomalous user behaviors
- Triggered detection rules

**Select Target Sensors**:
```
# Via web UI: Sensors view
# Via LCQL: Filter by hostname, tags, or platform
routing/hostname == "compromised-host"
routing/tags contains "investigation"
plat == windows
```

### 2. Preservation Phase

**Collect Volatile Data First** (Order of Volatility):

1. **System Memory**:
```yaml
# Via Dumper extension
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 30
```

2. **Running Processes**:
```bash
os_processes
```

3. **Network Connections**:
```bash
netstat
```

4. **Logged-in Users**:
```bash
os_users  # Windows
```

5. **Command History**:
```bash
history_dump
```

**Document Chain of Custody**:
- Who collected the evidence
- When it was collected
- What was collected
- Where it's stored
- Why it was collected
- How it was collected

### 3. Collection Phase

**Systematic Evidence Collection**:

**File System Evidence**:
```bash
# List suspicious directories
dir_list C:\Users\victim\Downloads
dir_list C:\Windows\Temp
dir_list /tmp
dir_list /var/tmp

# Get file metadata
file_info C:\path\to\suspicious.exe
file_hash C:\path\to\suspicious.exe

# Collect artifacts
artifact_get C:\path\to\suspicious.exe
artifact_get C:\Windows\Prefetch\MALWARE.EXE-*.pf
```

**Event Logs (Windows)**:
```bash
# Collect Windows Event Logs
log_get Security
log_get System
log_get Application
artifact_get C:\Windows\System32\winevt\Logs\Security.evtx
```

**Registry Artifacts (Windows)**:
```bash
# Get autoruns
os_autoruns

# Collect registry hives
artifact_get C:\Windows\System32\config\SYSTEM
artifact_get C:\Windows\System32\config\SOFTWARE
artifact_get C:\Windows\System32\config\SAM
```

**System State**:
```bash
# Services
os_services

# Packages/software
os_packages

# Drivers (Windows)
os_drivers
```

### 4. Examination Phase

**Timeline Analysis**:
```
# Process execution timeline
-24h | plat == windows | NEW_PROCESS | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline routing/hostname as host

# File modification timeline
-24h | plat == windows | NEW_DOCUMENT FILE_MODIFIED | event/TIMESTAMP as time event/FILE_PATH as file routing/hostname as host

# Network connection timeline
-12h | plat == windows | NETWORK_CONNECTIONS | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/FILE_PATH as process routing/hostname as host
```

**Pattern Detection**:
- Identify related events
- Correlate across different event types
- Build process trees
- Map network communications
- Trace file operations

### 5. Analysis Phase

**Hypothesis-Driven Analysis**:
1. Develop theories based on initial evidence
2. Test hypotheses with targeted queries
3. Validate or refute with additional evidence
4. Refine understanding iteratively

**Attribution Analysis**:
- Map to MITRE ATT&CK framework
- Identify TTPs (Tactics, Techniques, Procedures)
- Compare to known threat actor behaviors
- Establish timeline of attacker actions

**Impact Assessment**:
- What data was accessed?
- What systems were compromised?
- What modifications were made?
- What was exfiltrated?

### 6. Reporting Phase

**Document Findings**:
- Executive summary
- Timeline of events
- Evidence inventory
- Analysis methodology
- Conclusions and recommendations
- Appendices with technical details

---

## Memory Analysis

### Memory Forensics Fundamentals

Memory contains volatile artifacts not present on disk:
- Running processes and loaded modules
- Decrypted data and credentials
- Network connections and artifacts
- Injected code and rootkits
- Malware operating only in memory

### Live Memory Analysis Commands

#### Process Memory Map

**View loaded modules and memory regions**:
```bash
mem_map --pid 1234
```

**Interpretation**:
- Look for unusual DLLs or modules
- Identify memory regions with execute permissions
- Detect reflectively loaded code
- Find memory-only malware

**Example Analysis**:
```
# Get process list to find suspicious PID
os_processes

# Map memory for suspicious process
mem_map --pid 2468

# Look for:
# - DLLs from unusual paths
# - Executable memory without backing file
# - Known malicious module names
# - Hidden or unbacked regions
```

#### Memory String Extraction

**Extract readable strings from process memory**:
```bash
mem_strings --pid 1234
```

**Use Cases**:
- Find URLs, domains, IP addresses
- Discover credentials or API keys
- Identify configuration data
- Locate command strings
- Extract file paths

**Example Investigation**:
```bash
# Extract strings from suspicious browser process
mem_strings --pid 3456

# Search response for:
# - C2 domains or IPs
# - Encryption keys
# - File paths to malware
# - Registry keys
# - Command syntax
```

#### Memory String Search

**Search for specific strings in memory**:
```bash
mem_find_string --pid 1234 --string "evil.com"
mem_find_string --pid 1234 --string "password"
mem_find_string --pid 1234 --string "192.168"
```

**Targeted Search Strategies**:
```bash
# Search for known IOCs
mem_find_string --pid 2468 --string "malicious-domain.com"

# Search for credential keywords
mem_find_string --pid 2468 --string "username"
mem_find_string --pid 2468 --string "token"

# Search for file paths
mem_find_string --pid 2468 --string "C:\ProgramData"

# Search for IP addresses
mem_find_string --pid 2468 --string "203.0.113"
```

#### Memory Region Reading

**Read specific memory regions**:
```bash
mem_read --pid 1234 --base 0x00400000 --size 4096
```

**When to Use**:
- After identifying interesting addresses via mem_map
- To extract specific code or data structures
- To analyze suspected injection points
- To retrieve configuration blocks

**Workflow Example**:
```bash
# 1. Get memory map
mem_map --pid 1234

# 2. Identify suspicious region (e.g., executable with no backing file)
# Base: 0x7FFF0000, Size: 65536, Protect: PAGE_EXECUTE_READWRITE

# 3. Read the region
mem_read --pid 1234 --base 0x7FFF0000 --size 65536

# 4. Analyze dumped bytes for shellcode, malware, etc.
```

#### Handle Analysis (Windows)

**List open handles**:
```bash
mem_handles --pid 1234
```

**Find specific handles**:
```bash
mem_find_handle --pid 1234 --path "C:\suspicious"
```

**Handle Analysis Use Cases**:
- Identify files being accessed
- Find registry keys being modified
- Detect named pipes (IPC mechanisms)
- Locate open network sockets
- Identify process injection targets

### Full Memory Dumps

**Capture complete system memory**:
```yaml
# Via D&R rule or API request
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 30  # days
```

**When to Capture Full Memory**:
- Advanced persistent threat (APT) investigation
- Rootkit or bootkit analysis
- Complete system state preservation
- Legal evidence requirements
- Kernel-level malware suspected

**Memory Dump Analysis Workflow**:

1. **Capture and Download**:
   - Request dump via Dumper extension
   - Wait for completion (can take several minutes)
   - Download from Artifact Collection

2. **Offline Analysis Tools**:
   - Volatility Framework
   - Rekall
   - WinDbg (Windows)
   - GDB (Linux)

3. **Key Analysis Areas**:
   - Process listing and trees
   - Network connections
   - DLL and driver analysis
   - Registry artifacts
   - Code injection detection
   - Rootkit detection
   - Credential extraction

**Volatility Analysis Examples**:
```bash
# Identify Volatility profile
vol.py -f memory.dmp imageinfo

# List processes
vol.py -f memory.dmp --profile=Win10x64 pslist
vol.py -f memory.dmp --profile=Win10x64 pstree

# Network connections
vol.py -f memory.dmp --profile=Win10x64 netscan

# Find injected code
vol.py -f memory.dmp --profile=Win10x64 malfind

# Dump process memory
vol.py -f memory.dmp --profile=Win10x64 procdump -p 1234 -D output/

# Extract command history
vol.py -f memory.dmp --profile=Win10x64 cmdscan
vol.py -f memory.dmp --profile=Win10x64 consoles
```

### Memory Analysis Best Practices

**Prioritize Volatile Data**:
- Collect memory before disk artifacts
- Network connections change rapidly
- Running processes may terminate
- Memory may be cleared on reboot

**Correlate with Disk Evidence**:
- Compare memory modules with disk files
- Verify process binaries on disk
- Check for memory/disk mismatches
- Identify packed or protected executables

**Document Context**:
- System state at time of capture
- Running applications
- User activity
- Network state
- Time and date

**Look for Anomalies**:
- Processes without disk backing
- Modules loaded from unusual paths
- Hidden or unnamed processes
- Executable memory in unexpected locations
- Suspicious parent-child relationships

---

## Process Analysis

### Process Investigation Techniques

#### Current Process State

**List running processes**:
```bash
os_processes
```

**Response Analysis**:
```json
{
  "PROCESS_ID": 1234,
  "FILE_PATH": "C:\\Windows\\System32\\svchost.exe",
  "COMMAND_LINE": "C:\\Windows\\system32\\svchost.exe -k netsvcs",
  "PARENT_PROCESS_ID": 664,
  "USER_NAME": "NT AUTHORITY\\SYSTEM",
  "THREADS": 15,
  "MEMORY_USAGE": 12582912
}
```

**Key Indicators to Examine**:
- Unusual process names or paths
- Suspicious command-line arguments
- Unexpected parent processes
- Processes running from temp directories
- Processes with high CPU/memory without justification
- Unsigned or rarely seen executables

#### Historical Process Execution

**Dump recent process history**:
```bash
history_dump
```

**Use Cases**:
- Reconstruct attack timeline
- Identify deleted processes
- Trace process execution chains
- Recover evidence of short-lived processes

**Timeline Reconstruction via LCQL**:
```
# All process executions in 24h window
-24h | plat == windows | NEW_PROCESS | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline event/PARENT/FILE_PATH as parent routing/hostname as host

# Process executions from specific parent
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "cmd.exe" | event/TIMESTAMP as time event/FILE_PATH as child event/COMMAND_LINE as cmdline routing/hostname as host

# Unsigned process executions
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/TIMESTAMP as time event/FILE_PATH as path event/HASH as hash routing/hostname as host
```

#### Process Tree Construction

**Build parent-child relationships**:
```
# Stack process relationships
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH as parent event/FILE_PATH as child event/COMMAND_LINE as cmdline COUNT(event) as count GROUP BY(parent child cmdline)

# Specific process tree (e.g., from Word)
-6h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "WINWORD.EXE" | event/PARENT/FILE_PATH as parent event/FILE_PATH as child event/COMMAND_LINE as cmdline routing/hostname as host
```

**Suspicious Process Trees**:
- Office apps (Word, Excel) spawning cmd.exe or powershell.exe
- Browser processes launching unusual children
- Services spawning interactive shells
- System processes from wrong parents
- Long chains of script interpreters

#### Process Termination Analysis

**Track process terminations**:
```
-12h | plat == windows | TERMINATE_PROCESS | event/PROCESS_ID as pid event/FILE_PATH as process event/TIMESTAMP as time routing/hostname as host
```

**Correlation with Response Actions**:
- Was process killed by IR action?
- Self-termination by malware?
- Normal process lifecycle?
- Crash or error termination?

### Process Anomaly Detection

#### Suspicious Command Lines

**PowerShell Investigation**:
```
# Encoded PowerShell commands
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" and event/COMMAND_LINE contains "-enc" | event/COMMAND_LINE as cmd routing/hostname as host

# Download cradles
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" and (event/COMMAND_LINE contains "DownloadString" or event/COMMAND_LINE contains "WebClient" or event/COMMAND_LINE contains "Invoke-Expression") | event/COMMAND_LINE as cmd routing/hostname as host

# Bypass execution policy
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" and event/COMMAND_LINE contains "bypass" | event/COMMAND_LINE as cmd routing/hostname as host
```

**Command Shell Investigation**:
```
# Cmd.exe with suspicious flags
-12h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with "cmd.exe" and (event/COMMAND_LINE contains "/c" or event/COMMAND_LINE contains "/k") | event/COMMAND_LINE as cmd event/PARENT/FILE_PATH as parent routing/hostname as host

# Batch file execution
-12h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains ".bat" or event/COMMAND_LINE contains ".cmd" | event/COMMAND_LINE as cmd routing/hostname as host
```

**Living Off the Land Binaries (LOLBins)**:
```
# Common LOLBin abuse
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with "certutil.exe" or event/FILE_PATH ends with "bitsadmin.exe" or event/FILE_PATH ends with "mshta.exe" or event/FILE_PATH ends with "regsvr32.exe" or event/FILE_PATH ends with "rundll32.exe" | event/FILE_PATH as binary event/COMMAND_LINE as cmd routing/hostname as host
```

#### Process Execution from Unusual Locations

**Suspicious Execution Paths**:
```
# Executables from user directories
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "\\Users\\" and event/FILE_PATH ends with ".exe" | event/FILE_PATH as path event/COMMAND_LINE as cmd routing/hostname as host

# Temp directory execution
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "\\Temp\\" or event/FILE_PATH contains "\\AppData\\Local\\Temp\\" | event/FILE_PATH as path routing/hostname as host

# Recycle bin execution
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "$Recycle.Bin" | event/FILE_PATH as path routing/hostname as host
```

#### Code Identity Analysis

**Signature Verification**:
```
# Unsigned binaries
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as path event/HASH as hash routing/hostname as host

# Specific signer analysis
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/CERT_ISSUER as issuer event/FILE_PATH as path COUNT(event) as count GROUP BY(issuer path)

# Invalid or expired signatures
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/CERT_CHAIN_STATUS != 0 | event/FILE_PATH as path event/SIGNATURE/CERT_CHAIN_STATUS as status routing/hostname as host
```

### Process Injection Detection

**Remote Thread Creation**:
```
-6h | plat == windows | NEW_REMOTE_THREAD | event/PROCESS_ID as target_pid event/PARENT_PROCESS_ID as injector_pid routing/hostname as host
```

**Thread Injection Event Analysis**:
```
-6h | plat == windows | THREAD_INJECTION | event/INJECTED_ADDRESS as address event/PROCESS_ID as pid event/SOURCE_PROCESS_ID as source routing/hostname as host
```

**Sensitive Process Access**:
```
-12h | plat == windows | SENSITIVE_PROCESS_ACCESS | event/TARGET_PROCESS_ID as target event/SOURCE_PROCESS_ID as source routing/hostname as host
```

**Process Hollowing Indicators**:
- Process created in suspended state
- Memory unmapped and remapped
- Execution transferred to new code
- Look for MODULE_MEM_DISK_MISMATCH events

---

## File Analysis

### File System Forensics

#### File Metadata Examination

**Get detailed file information**:
```bash
file_info C:\path\to\suspicious.exe
```

**Response Analysis**:
```json
{
  "FILE_PATH": "C:\\Users\\victim\\Downloads\\malware.exe",
  "FILE_SIZE": 102400,
  "CREATION_TIME": 1634567890123,
  "MODIFICATION_TIME": 1634567890456,
  "ACCESS_TIME": 1634570000789,
  "ATTRIBUTES": 32,
  "OWNER": "DOMAIN\\victim"
}
```

**Forensic Value of Timestamps**:
- **Creation Time**: When file first appeared on system
- **Modification Time**: Last write to file content
- **Access Time**: Last read operation (may be disabled)
- **Metadata Change**: Permission or attribute changes

**MACB Timeline**:
- M: Modified (content changed)
- A: Accessed (file read)
- C: Changed (metadata changed)
- B: Birth (file created)

#### File Hashing

**Calculate file hash**:
```bash
file_hash C:\path\to\file.exe
```

**Hash Uses**:
- Verify file integrity
- Search for known malware
- Track file movement across systems
- Compare with threat intelligence
- Evidence preservation

**Hash Correlation Queries**:
```
# Find all instances of specific hash
-24h | plat == windows | CODE_IDENTITY | event/HASH == "abc123..." | event/FILE_PATH as path routing/hostname as host

# Find systems with matching hash
-7d | plat == windows | CODE_IDENTITY | event/HASH == "abc123..." | routing/hostname as host COUNT_UNIQUE(routing/sid) as sensor_count GROUP BY(host)
```

#### File Collection

**Collect suspicious files**:
```bash
# Hash first for verification
file_hash C:\Users\victim\Downloads\suspicious.exe

# Then collect
artifact_get C:\Users\victim\Downloads\suspicious.exe
```

**Strategic File Collection**:
```bash
# Collect prefetch files (Windows execution artifacts)
dir_list C:\Windows\Prefetch
artifact_get C:\Windows\Prefetch\MALWARE.EXE-*.pf

# Collect recent files from downloads
dir_list C:\Users\*\Downloads
artifact_get C:\Users\*\Downloads\*.exe

# Collect web browser history
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\History
artifact_get C:\Users\*\AppData\Roaming\Mozilla\Firefox\Profiles\*\places.sqlite

# Collect shell bags and recent items
artifact_get C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent\*
```

#### File Search by Hash

**Find files matching hash in directory tree**:
```bash
dir_find_hash C:\Users\ --hash abc123def456...
```

**Use Cases**:
- Locate all copies of malicious file
- Find renamed malware
- Identify propagation paths
- Verify deletion success

### File Activity Timeline

**File Creation Events**:
```
-24h | plat == windows | NEW_DOCUMENT | event/TIMESTAMP as time event/FILE_PATH as path event/HASH as hash routing/hostname as host
```

**File Modification Events**:
```
-24h | plat == windows | FILE_MODIFIED | event/TIMESTAMP as time event/FILE_PATH as path routing/hostname as host
```

**File Deletion Events**:
```
-24h | plat == windows | FILE_DELETE | event/TIMESTAMP as time event/FILE_PATH as path routing/hostname as host
```

**Comprehensive File Activity**:
```
-24h | plat == windows | NEW_DOCUMENT FILE_MODIFIED FILE_DELETE | event/TIMESTAMP as time routing/event_type as activity event/FILE_PATH as path routing/hostname as host
```

### Suspicious File Patterns

**Files in Suspicious Locations**:
```
# Files in temp directories
-24h | plat == windows | NEW_DOCUMENT | event/FILE_PATH contains "\\Temp\\" or event/FILE_PATH contains "\\TMP\\" | event/FILE_PATH as path event/HASH as hash routing/hostname as host

# Files in user profile AppData
-24h | plat == windows | NEW_DOCUMENT | event/FILE_PATH contains "\\AppData\\" and event/FILE_PATH ends with ".exe" | event/FILE_PATH as path routing/hostname as host

# Hidden files
-24h | plat == windows | NEW_DOCUMENT | event/ATTRIBUTES == 2 | event/FILE_PATH as path routing/hostname as host
```

**Suspicious File Types**:
```
# Executable extensions
-24h | plat == windows | NEW_DOCUMENT | event/FILE_PATH ends with ".exe" or event/FILE_PATH ends with ".dll" or event/FILE_PATH ends with ".scr" or event/FILE_PATH ends with ".bat" | event/FILE_PATH as path routing/hostname as host

# Script files
-24h | plat == windows | NEW_DOCUMENT | event/FILE_PATH ends with ".ps1" or event/FILE_PATH ends with ".vbs" or event/FILE_PATH ends with ".js" | event/FILE_PATH as path routing/hostname as host

# Double extensions
-24h | plat == windows | NEW_DOCUMENT | event/FILE_PATH matches ".*\\.[a-z]{3}\\.(exe|scr|bat)$" | event/FILE_PATH as path routing/hostname as host
```

### Master File Table (MFT) Analysis

**Collect MFT for timeline analysis**:
```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: mft
    sid: <<routing.sid>>
    retention: 30
```

**MFT Forensic Value**:
- Complete file system timeline
- Deleted file records
- File rename history
- Directory structure changes
- NTFS artifact analysis

**MFT Analysis Tools**:
- MFTExplorer
- analyzeMFT
- NTFS Log Tracker
- Plaso (via LimaCharlie Plaso extension)

**MFT Investigation Workflow**:
1. Collect MFT via Dumper extension
2. Download from Artifact Collection
3. Parse with forensic tools
4. Build comprehensive timeline
5. Correlate with LimaCharlie telemetry
6. Identify gaps or anomalies

---

## Timeline Reconstruction

### Forensic Timeline Fundamentals

Timeline reconstruction is the process of establishing a chronological sequence of events during an incident. Timelines help investigators understand:
- Initial compromise vector
- Attacker movement and actions
- Data accessed or exfiltrated
- Persistence mechanisms established
- Full scope and duration of incident

### Timeline Data Sources

**LimaCharlie Event Types for Timeline**:

1. **Process Execution**: NEW_PROCESS, EXISTING_PROCESS, TERMINATE_PROCESS
2. **File Operations**: NEW_DOCUMENT, FILE_MODIFIED, FILE_DELETE
3. **Network Activity**: NETWORK_CONNECTIONS, DNS_REQUEST, NEW_TCP4_CONNECTION
4. **Authentication**: WEL (EventID 4624, 4625, 4634, 4672)
5. **Persistence**: AUTORUN_CHANGE, SERVICE_CHANGE, REGISTRY_WRITE
6. **System Events**: STARTING_UP, SHUTTING_DOWN, CONNECTED, DISCONNECTED

### Building Multi-Source Timelines

#### Comprehensive Timeline Query

**All significant events in timeframe**:
```
-24h | plat == windows | NEW_PROCESS NETWORK_CONNECTIONS NEW_DOCUMENT REGISTRY_WRITE SERVICE_CHANGE | event/TIMESTAMP as time routing/event_type as event_type event/FILE_PATH as file_path routing/hostname as host
```

**Focused Timeline for Specific Host**:
```
-48h | routing/hostname == "compromised-host" | * | event/TIMESTAMP as time routing/event_type as event_type
```

#### Process-Centric Timeline

**All activity related to specific process**:
```
# By process name
-24h | plat == windows | NEW_PROCESS TERMINATE_PROCESS | event/FILE_PATH contains "malware.exe" | event/TIMESTAMP as time routing/event_type as activity event/PROCESS_ID as pid event/COMMAND_LINE as cmdline routing/hostname as host

# By PID (requires correlation with historical data)
-12h | plat == windows | * | event/PROCESS_ID == 1234 or event/PARENT_PROCESS_ID == 1234 | event/TIMESTAMP as time routing/event_type as activity
```

**Process Tree Timeline**:
```
-24h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "WINWORD.EXE" | event/TIMESTAMP as time event/PARENT/FILE_PATH as parent event/FILE_PATH as child event/COMMAND_LINE as cmdline routing/hostname as host
```

#### Network-Centric Timeline

**All network connections from host**:
```
-24h | routing/hostname == "compromised-host" | NETWORK_CONNECTIONS DNS_REQUEST NEW_TCP4_CONNECTION | event/TIMESTAMP as time routing/event_type as activity event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/FILE_PATH as process
```

**Timeline of specific C2 domain**:
```
-7d | plat == windows | DNS_REQUEST NETWORK_CONNECTIONS | event/* contains "evil-domain.com" | event/TIMESTAMP as time routing/event_type as activity routing/hostname as host
```

#### File-Centric Timeline

**All operations on specific file**:
```
-24h | plat == windows | NEW_DOCUMENT FILE_MODIFIED FILE_DELETE FILE_GET_REP | event/FILE_PATH == "C:\\Users\\victim\\Documents\\sensitive.docx" | event/TIMESTAMP as time routing/event_type as activity routing/hostname as host
```

**Timeline of file drops in directory**:
```
-24h | plat == windows | NEW_DOCUMENT | event/FILE_PATH contains "C:\\ProgramData\\" | event/TIMESTAMP as time event/FILE_PATH as path event/HASH as hash routing/hostname as host
```

#### User Activity Timeline

**All actions by specific user**:
```
-24h | plat == windows | NEW_PROCESS | event/USER_NAME == "DOMAIN\\victim" | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline routing/hostname as host
```

**Login/Logout Timeline**:
```
# Via Windows Event Logs
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" or event/EVENT/System/EventID == "4634" | event/TIMESTAMP as time event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/LogonType as type routing/hostname as host
```

### Attack Timeline Construction

#### Phase 1: Initial Access

**Identify Entry Point**:
```
# Look for initial malicious process
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH contains "Downloads" or event/FILE_PATH contains "Temp" | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline event/PARENT/FILE_PATH as parent routing/hostname as host

# Identify phishing email attachment execution
-7d | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "OUTLOOK.EXE" or event/PARENT/FILE_PATH contains "chrome.exe" | event/TIMESTAMP as time event/FILE_PATH as process routing/hostname as host

# Web-based exploitation
-7d | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "iexplore.exe" or event/PARENT/FILE_PATH contains "chrome.exe" or event/PARENT/FILE_PATH contains "firefox.exe" | event/FILE_PATH ends with ".exe" and event/FILE_PATH contains "\\Temp\\" | event/TIMESTAMP as time event/FILE_PATH as process routing/hostname as host
```

#### Phase 2: Execution and Persistence

**Execution Timeline**:
```
# Process execution chain
-7d | routing/hostname == "compromised-host" | NEW_PROCESS | event/TIMESTAMP as time event/FILE_PATH as process event/PARENT/FILE_PATH as parent event/COMMAND_LINE as cmdline

# Script execution
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" or event/FILE_PATH contains "wscript" or event/FILE_PATH contains "cscript" | event/TIMESTAMP as time event/COMMAND_LINE as cmdline routing/hostname as host
```

**Persistence Establishment**:
```
# Registry-based persistence
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\CurrentVersion\\Run" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host

# Service installation
-7d | plat == windows | SERVICE_CHANGE | event/SVC_STATE == 1 | event/TIMESTAMP as time event/SVC_NAME as service event/EXECUTABLE as exe routing/hostname as host

# Scheduled task creation
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4698" | event/TIMESTAMP as time event/EVENT/EventData/TaskName as task routing/hostname as host
```

#### Phase 3: Privilege Escalation

**Elevated Process Execution**:
```
-7d | plat == windows | NEW_PROCESS | event/PROCESS_IS_ELEVATED == true | event/TIMESTAMP as time event/FILE_PATH as process event/USER_NAME as user routing/hostname as host
```

**Credential Access**:
```
# LSASS access
-7d | plat == windows | SENSITIVE_PROCESS_ACCESS | event/TARGET_PROCESS_PATH contains "lsass.exe" | event/TIMESTAMP as time event/SOURCE_PROCESS_PATH as source routing/hostname as host
```

#### Phase 4: Discovery and Lateral Movement

**Discovery Commands**:
```
-7d | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "net view" or event/COMMAND_LINE contains "net user" or event/COMMAND_LINE contains "net group" or event/COMMAND_LINE contains "whoami" or event/COMMAND_LINE contains "ipconfig" | event/TIMESTAMP as time event/COMMAND_LINE as cmd routing/hostname as host
```

**Lateral Movement**:
```
# RDP connections
-7d | plat == windows | NEW_TCP4_CONNECTION | event/NETWORK_ACTIVITY/DESTINATION/PORT == 3389 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as target routing/hostname as source

# SMB connections
-7d | plat == windows | NEW_TCP4_CONNECTION | event/NETWORK_ACTIVITY/DESTINATION/PORT == 445 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as target routing/hostname as source

# WMI/PsExec indicators
-7d | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "wmic" or event/COMMAND_LINE contains "psexec" | event/TIMESTAMP as time event/COMMAND_LINE as cmd routing/hostname as host
```

#### Phase 5: Collection and Exfiltration

**File Access Timeline**:
```
-7d | plat == windows | FILE_TYPE_ACCESSED | event/FILE_PATH contains ".docx" or event/FILE_PATH contains ".xlsx" or event/FILE_PATH contains ".pdf" | event/TIMESTAMP as time event/FILE_PATH as file routing/hostname as host
```

**Data Staging**:
```
# Files moved to staging directory
-7d | plat == windows | NEW_DOCUMENT FILE_MODIFIED | event/FILE_PATH contains "\\ProgramData\\" or event/FILE_PATH contains "\\Temp\\staging" | event/TIMESTAMP as time event/FILE_PATH as file routing/hostname as host
```

**Exfiltration Events**:
```
# Large outbound transfers
-7d | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/BYTES_SENT > 10485760 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/BYTES_SENT as bytes event/FILE_PATH as process routing/hostname as host

# Unusual DNS queries (DNS tunneling)
-7d | plat == windows | DNS_REQUEST | event/DOMAIN_NAME length > 50 | event/TIMESTAMP as time event/DOMAIN_NAME as domain routing/hostname as host
```

### Timeline Correlation Techniques

**Multi-Host Correlation**:
```
# Track lateral movement across hosts
-7d | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT == 445 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as target routing/hostname as source COUNT(event) as connections GROUP BY(time target source)
```

**User Activity Correlation**:
```
# Track user across multiple systems
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/TargetUserName == "victim" | event/TIMESTAMP as time routing/hostname as host event/EVENT/EventData/IpAddress as source
```

**Hash-Based Correlation**:
```
# Track file propagation by hash
-7d | plat == windows | CODE_IDENTITY | event/HASH == "abc123..." | event/TIMESTAMP as time event/FILE_PATH as path routing/hostname as host
```

### Timeline Visualization and Export

**Export Timeline for Analysis**:
1. Run LCQL query with time, event_type, and relevant fields
2. Export results to CSV via web UI
3. Import to timeline tools (Timesketch, Plaso, Excel)
4. Visualize with graphing tools

**Timeline Best Practices**:
- Start with broad time windows, then narrow
- Include all relevant event types
- Correlate across multiple data sources
- Document timezone considerations
- Validate timestamp accuracy
- Look for gaps or anomalies in timeline
- Cross-reference with external logs (firewall, proxy, etc.)

---

## Artifact Examination

### Windows Forensic Artifacts

#### Prefetch Files

**Purpose**: Windows execution artifacts showing program execution history

**Collection**:
```bash
dir_list C:\Windows\Prefetch
artifact_get C:\Windows\Prefetch\MALWARE.EXE-*.pf
```

**Forensic Value**:
- Proof of execution
- First and last execution times
- Execution count
- Files and directories accessed
- Device volumes accessed

**Analysis**:
- Parse with PECmd or WinPrefetchView
- Correlate with process execution timeline
- Identify deleted executables
- Track malware execution frequency

#### Windows Event Logs

**Critical Logs**:
```bash
# Security log (authentication, privileges)
log_get Security
artifact_get C:\Windows\System32\winevt\Logs\Security.evtx

# System log (services, drivers, system events)
log_get System
artifact_get C:\Windows\System32\winevt\Logs\System.evtx

# Application log
log_get Application

# Sysmon (if installed)
artifact_get C:\Windows\System32\winevt\Logs\Microsoft-Windows-Sysmon%4Operational.evtx
```

**Key Event IDs**:

**Authentication**:
- 4624: Successful logon
- 4625: Failed logon
- 4634: Logoff
- 4672: Special privileges assigned
- 4720: User account created
- 4726: User account deleted

**Process Execution (Sysmon)**:
- Event ID 1: Process creation
- Event ID 3: Network connection
- Event ID 7: Image loaded
- Event ID 8: CreateRemoteThread
- Event ID 10: Process access

**LCQL Queries for WEL**:
```
# Failed login attempts
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as source routing/hostname as host

# Privilege escalation
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4672" | event/EVENT/EventData/SubjectUserName as user routing/hostname as host

# Account creation
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4720" | event/EVENT/EventData/TargetUserName as new_user event/EVENT/EventData/SubjectUserName as creator routing/hostname as host

# Scheduled task creation
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4698" | event/EVENT/EventData/TaskName as task routing/hostname as host
```

#### Registry Artifacts

**Autorun Locations**:
```bash
# Get current autoruns
os_autoruns
```

**Critical Registry Keys**:
```
# Run keys
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce

# Services
HKLM\System\CurrentControlSet\Services

# Winlogon
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon

# AppInit DLLs
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs

# Image File Execution Options (debugger hijacking)
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options
```

**Collect Registry Hives**:
```bash
artifact_get C:\Windows\System32\config\SYSTEM
artifact_get C:\Windows\System32\config\SOFTWARE
artifact_get C:\Windows\System32\config\SAM
artifact_get C:\Windows\System32\config\SECURITY
artifact_get C:\Users\*\NTUSER.DAT
```

**Registry Timeline**:
```
# Registry writes
-24h | plat == windows | REGISTRY_WRITE | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host

# Persistence via registry
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\Run" or event/REGISTRY_KEY contains "\\Services" or event/REGISTRY_KEY contains "\\Winlogon" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

#### Browser Artifacts

**Chrome History**:
```bash
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\History
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\Cookies
artifact_get C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\Login Data
```

**Firefox History**:
```bash
artifact_get C:\Users\*\AppData\Roaming\Mozilla\Firefox\Profiles\*\places.sqlite
artifact_get C:\Users\*\AppData\Roaming\Mozilla\Firefox\Profiles\*\cookies.sqlite
```

**Edge History**:
```bash
artifact_get C:\Users\*\AppData\Local\Microsoft\Edge\User Data\Default\History
```

**Browser Forensic Value**:
- Initial infection vector (malicious download)
- Web-based C2 communications
- Phishing page visits
- Data exfiltration via web
- Credential harvesting sites

#### Shellbags

**Collection**:
```bash
# Via registry hives or dedicated tools
artifact_get C:\Users\*\NTUSER.DAT
artifact_get C:\Users\*\AppData\Local\Microsoft\Windows\UsrClass.dat
```

**Forensic Value**:
- Folders accessed via Explorer
- Network shares accessed
- USB device access
- Deleted folder evidence
- User activity timeline

#### Jump Lists and Recent Items

**Collection**:
```bash
# Recent items
artifact_get C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent\*

# Jump lists
artifact_get C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations\*
artifact_get C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent\CustomDestinations\*
```

**Forensic Value**:
- Recently accessed files
- Application usage
- File interaction timestamps
- Deleted file evidence

### Linux Forensic Artifacts

#### Command History

**Collection**:
```bash
artifact_get /home/*/.bash_history
artifact_get /root/.bash_history
artifact_get /home/*/.zsh_history
```

**Forensic Value**:
- Commands executed by users
- Privilege escalation attempts
- Data exfiltration commands
- Persistence mechanism creation

#### System Logs

**Collection**:
```bash
artifact_get /var/log/auth.log      # Debian/Ubuntu
artifact_get /var/log/secure        # RHEL/CentOS
artifact_get /var/log/syslog
artifact_get /var/log/messages
artifact_get /var/log/kern.log
```

**Key Log Files**:
- auth.log/secure: Authentication and sudo usage
- syslog/messages: General system events
- kern.log: Kernel events
- cron: Scheduled task execution
- btmp: Failed login attempts
- wtmp: Login/logout records

#### Persistence Locations

**Collection**:
```bash
# Cron jobs
artifact_get /etc/crontab
artifact_get /var/spool/cron/crontabs/*
artifact_get /etc/cron.d/*

# Systemd services
artifact_get /etc/systemd/system/*
artifact_get /lib/systemd/system/*

# Init scripts
artifact_get /etc/init.d/*
artifact_get /etc/rc*.d/*

# Shell profiles
artifact_get /etc/profile
artifact_get /home/*/.bashrc
artifact_get /home/*/.bash_profile
artifact_get /root/.bashrc
```

#### SSH Artifacts

**Collection**:
```bash
artifact_get /home/*/.ssh/authorized_keys
artifact_get /root/.ssh/authorized_keys
artifact_get /home/*/.ssh/known_hosts
artifact_get /var/log/auth.log
```

**SSH Timeline**:
```
-7d | plat == linux | SSH_LOGIN SSH_LOGOUT | event/TIMESTAMP as time routing/event_type as activity event/USER_NAME as user routing/hostname as host
```

### macOS Forensic Artifacts

#### Unified Logs

**Collection via Artifact Collection Extension**:
```yaml
# Configure in Artifact Collection rules
# Pattern: mul://<query>
```

**Forensic Value**:
- System events
- Application activity
- User actions
- Security events

#### Persistence Locations

**Collection**:
```bash
# Launch agents and daemons
artifact_get /Library/LaunchAgents/*
artifact_get /Library/LaunchDaemons/*
artifact_get /Users/*/Library/LaunchAgents/*

# Login items
artifact_get /Users/*/Library/Preferences/com.apple.loginitems.plist

# Startup items
artifact_get /Library/StartupItems/*
```

#### Command History

**Collection**:
```bash
artifact_get /Users/*/.bash_history
artifact_get /Users/*/.zsh_history
artifact_get /var/root/.bash_history
```

---

## Registry Analysis

### Windows Registry Forensics

#### Registry Structure

**Registry Hives**:
- HKEY_LOCAL_MACHINE (HKLM): System-wide settings
  - SYSTEM: System configuration
  - SOFTWARE: Installed applications
  - SAM: User account database
  - SECURITY: Security policies
- HKEY_CURRENT_USER (HKCU): Current user settings
  - Stored in NTUSER.DAT per user
- HKEY_USERS: All user profiles

#### Live Registry Analysis

**Monitor Registry Changes**:
```
# Registry writes
-24h | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY as key event/REGISTRY_VALUE as value event/TIMESTAMP as time routing/hostname as host

# Registry creation
-24h | plat == windows | REGISTRY_CREATE | event/REGISTRY_KEY as key event/TIMESTAMP as time routing/hostname as host

# Registry deletion
-24h | plat == windows | REGISTRY_DELETE | event/REGISTRY_KEY as key event/TIMESTAMP as time routing/hostname as host
```

#### Persistence via Registry

**Autorun Keys**:
```
# Monitor Run keys
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\CurrentVersion\\Run" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host

# Monitor RunOnce keys
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\CurrentVersion\\RunOnce" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host

# Services
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\CurrentControlSet\\Services" | event/TIMESTAMP as time event/REGISTRY_KEY as key routing/hostname as host
```

**Winlogon Persistence**:
```
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\Winlogon" and (event/REGISTRY_KEY contains "Shell" or event/REGISTRY_KEY contains "Userinit" or event/REGISTRY_KEY contains "Notify") | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

**AppInit DLLs**:
```
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "AppInit_DLLs" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

#### Forensic Registry Collection

**Collect Registry Hives**:
```bash
# System hives
artifact_get C:\Windows\System32\config\SYSTEM
artifact_get C:\Windows\System32\config\SOFTWARE
artifact_get C:\Windows\System32\config\SAM
artifact_get C:\Windows\System32\config\SECURITY

# User hives
artifact_get C:\Users\*\NTUSER.DAT
artifact_get C:\Users\*\AppData\Local\Microsoft\Windows\UsrClass.dat
```

#### Offline Registry Analysis

**Analysis Tools**:
- Registry Explorer (Eric Zimmerman)
- RegRipper
- Registry Decoder
- Volatility (for memory-based registry)

**Key Registry Artifacts**:

1. **UserAssist**: Programs executed via Explorer
   - Key: `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist`
   - Value: ROT13-encoded program paths with execution count

2. **MUICache**: Executed applications
   - Key: `NTUSER.DAT\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache`

3. **RecentDocs**: Recently opened documents
   - Key: `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs`

4. **TypedURLs**: URLs typed in IE/Edge
   - Key: `NTUSER.DAT\Software\Microsoft\Internet Explorer\TypedURLs`

5. **Shimcache**: Application Compatibility Cache
   - Key: `SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache`
   - Value: Executed programs with modification times

6. **AmCache**: Application execution artifacts
   - File: `C:\Windows\AppCompat\Programs\Amcache.hve`
   - Contains program execution evidence

#### Registry Forensics Workflow

1. **Collect Hives**:
   - Live collection via artifact_get
   - Or from forensic image

2. **Parse with Tools**:
   - Extract autorun entries
   - Parse execution artifacts
   - Identify installed software
   - Extract user activity

3. **Correlate with Telemetry**:
   - Match registry writes with REGISTRY_WRITE events
   - Correlate timestamps with file/process events
   - Validate persistence mechanisms

4. **Timeline Integration**:
   - Add registry artifacts to master timeline
   - Cross-reference with other evidence
   - Identify discrepancies or anomalies

---

## Network Analysis

### Network Forensics in LimaCharlie

#### Current Network State

**Active Connections**:
```bash
netstat
```

**Response Analysis**:
```json
{
  "NETWORK_ACTIVITY": [{
    "STATE": "ESTABLISHED",
    "PROCESS_ID": 1234,
    "SOURCE": {
      "IP_ADDRESS": "192.168.1.100",
      "PORT": 49152
    },
    "DESTINATION": {
      "IP_ADDRESS": "203.0.113.50",
      "PORT": 443
    }
  }]
}
```

**Connection Analysis**:
- Unusual destination IPs or ports
- High-prevalence source ports
- Connections from unexpected processes
- Connections to non-RFC1918 addresses
- Large data transfers

#### Network Connection Timeline

**All Network Connections**:
```
-24h | plat == windows | NETWORK_CONNECTIONS | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process routing/hostname as host
```

**TCP Connections by Type**:
```
# IPv4 TCP connections
-12h | plat == windows | NEW_TCP4_CONNECTION TERMINATE_TCP4_CONNECTION | event/TIMESTAMP as time routing/event_type as activity event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/DESTINATION/PORT as port routing/hostname as host

# IPv6 TCP connections
-12h | plat == windows | NEW_TCP6_CONNECTION TERMINATE_TCP6_CONNECTION | event/TIMESTAMP as time routing/event_type as activity event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst routing/hostname as host
```

**UDP Traffic**:
```
-12h | plat == windows | NEW_UDP4_CONNECTION TERMINATE_UDP4_CONNECTION | event/TIMESTAMP as time routing/event_type as activity event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/DESTINATION/PORT as port routing/hostname as host
```

#### DNS Analysis

**DNS Queries**:
```
-24h | plat == windows | DNS_REQUEST | event/TIMESTAMP as time event/DOMAIN_NAME as domain event/PROCESS_ID as pid routing/hostname as host
```

**Suspicious DNS Patterns**:

**DGA Domains**:
```
# Long or random-looking domains
-12h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME length > 20 | event/DOMAIN_NAME as domain routing/hostname as host

# Unusual TLDs
-12h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains ".tk" or event/DOMAIN_NAME contains ".cc" or event/DOMAIN_NAME contains ".xyz" | event/DOMAIN_NAME as domain routing/hostname as host
```

**DNS Tunneling**:
```
# Excessive subdomain length (data exfil)
-12h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME length > 50 | event/TIMESTAMP as time event/DOMAIN_NAME as domain routing/hostname as host

# High query volume to single domain
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT(event) as queries GROUP BY(domain) | queries > 100
```

**Low Prevalence Domains**:
```
# Domains resolved by few systems
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as sensor_count GROUP BY(domain) | sensor_count <= 2
```

#### Connection Pattern Analysis

**Beaconing Detection**:
```
# Repetitive connections to same destination
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/FILE_PATH as process COUNT(event) as conn_count GROUP BY(dst_ip process) | conn_count > 50
```

**Port Scanning**:
```
# Many destinations, same source
-6h | plat == windows | NEW_TCP4_CONNECTION | routing/hostname as source event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst COUNT_UNIQUE(dst) as target_count GROUP BY(source) | target_count > 20
```

**Unusual Protocols/Ports**:
```
# Non-standard ports for common services
-12h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT not in (80, 443, 53, 22, 3389, 445) and event/NETWORK_ACTIVITY/DESTINATION/PORT < 1024 | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process routing/hostname as host
```

**Data Transfer Volume**:
```
# Large outbound transfers
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/BYTES_SENT > 104857600 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/BYTES_SENT as bytes event/FILE_PATH as process routing/hostname as host
```

#### Process-Network Correlation

**Network Activity by Process**:
```
-12h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip COUNT(event) as connections GROUP BY(process dst_ip)
```

**Unusual Process Network Activity**:
```
# System binaries making external connections
-12h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH contains "\\System32\\" and event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is public | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst routing/hostname as host

# Office apps making network connections
-12h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH contains "WINWORD.EXE" or event/FILE_PATH contains "EXCEL.EXE" or event/FILE_PATH contains "POWERPNT.EXE" | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst routing/hostname as host
```

#### Network Summary Events

**Aggregate Connection Data**:
```
-24h | plat == windows | NETWORK_SUMMARY | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/BYTES_SENT as sent event/NETWORK_ACTIVITY/BYTES_RECEIVED as received routing/hostname as host
```

### Packet Capture Analysis

**PCAP Collection (Linux only)**:
```yaml
# Configure in Artifact Collection
# Pattern: pcap://<interface>
# Example: pcap://eth0
```

**PCAP Forensic Analysis**:
1. Trigger PCAP capture (via tag or rule)
2. Download from Artifact Collection
3. Analyze with:
   - Wireshark
   - tcpdump
   - NetworkMiner
   - Zeek (via Zeek extension)
   - tshark

**PCAP Use Cases**:
- Protocol-level analysis
- Payload extraction
- Encrypted traffic metadata
- Communication patterns
- Data exfiltration evidence

**Example Wireshark Filters**:
```
# HTTP requests
http.request

# DNS queries
dns.qry.name

# TLS handshakes
tls.handshake.type == 1

# Large transfers
tcp.len > 1400

# Specific IP
ip.addr == 203.0.113.50
```

### Geographic and Threat Intelligence Enrichment

**Public IP Identification**:
```
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is public | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as ip COUNT(event) as connections GROUP BY(ip)
```

**External Enrichment**:
- Lookup IPs in threat intelligence feeds
- Use VirusTotal, AbuseIPDB, AlienVault OTX
- Check geolocation (unexpected countries)
- Validate against known good IPs
- Correlate with domain reputation

**Integration with Threat Feeds**:
```
# Lookup in LimaCharlie threat feed
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is lookup in resource: "hive://lookup/malicious-ips" | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as ip routing/hostname as host
```

---

## Evidence Preservation

### Chain of Custody

**Documentation Requirements**:
- **Who**: Name and role of collector
- **What**: Specific evidence collected
- **When**: Date and time of collection (UTC recommended)
- **Where**: Source system (hostname, IP, sensor ID)
- **Why**: Reason for collection (incident ID, case number)
- **How**: Collection method and tools used

**LimaCharlie Evidence Metadata**:
- Sensor ID: Unique identifier
- Organization ID: Evidence context
- Timestamp: Precise collection time
- Investigation ID: Group related evidence
- Command used: Exact collection method

**Investigation ID Usage**:
```bash
# Tag commands with investigation ID
artifact_get C:\malware.exe --investigation incident-2024-001
history_dump --investigation incident-2024-001
os_processes --investigation incident-2024-001
```

**Tracking in D&R Rules**:
```yaml
- action: task
  command: artifact_get {{ .event.FILE_PATH }}
  investigation: incident-{{ .routing.hostname }}-{{ .event.TIMESTAMP }}
```

### Evidence Integrity

**Cryptographic Hashing**:
```bash
# Hash before collection
file_hash C:\evidence\suspicious.exe

# Record hash in chain of custody
# SHA256: abc123def456...

# Collect evidence
artifact_get C:\evidence\suspicious.exe

# Verify hash after download
# sha256sum suspicious.exe
```

**Verification Workflow**:
1. Hash file on endpoint
2. Document hash in evidence log
3. Collect via artifact_get
4. Download from Artifact Collection
5. Verify hash matches original
6. Document verification in chain of custody

**Read-Only Analysis**:
- Never modify original evidence
- Work on copies for analysis
- Use write-blockers for disk images
- Document any analysis that touches evidence
- Maintain original in secure storage

### Evidence Storage

**LimaCharlie Artifact Storage**:
- Encrypted at rest and in transit
- Configurable retention periods
- Access logging and audit trail
- Role-based access control
- Unique artifact identifiers

**Retention Configuration**:
```yaml
# Set retention when collecting
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 90  # days for legal hold
```

**Evidence Export**:
- Download from Artifact Collection UI
- Via API for automated export
- Hash verification post-download
- Secure external storage (compliance)
- Maintain multiple copies (3-2-1 rule)

### Legal and Compliance Considerations

**Admissibility Requirements**:
- Documented chain of custody
- Verifiable integrity (hashing)
- Authenticated collection methods
- Qualified personnel
- Proper authorization
- Evidence preservation

**Privacy and Data Protection**:
- Minimize collection scope
- PII redaction where possible
- Encryption for sensitive data
- Access restrictions
- Retention limits (GDPR, etc.)
- Data subject rights

**Compliance Evidence**:
- PCI DSS: 1 year minimum
- HIPAA: 6 years minimum
- SOX: 7 years minimum
- GDPR: Purpose-limited retention
- Industry-specific requirements

### Evidence Documentation

**Forensic Report Structure**:

1. **Executive Summary**
   - Incident overview
   - Key findings
   - Impact assessment
   - Recommendations

2. **Investigation Scope**
   - Systems examined
   - Time period analyzed
   - Data sources used
   - Limitations

3. **Methodology**
   - Tools and techniques
   - Collection procedures
   - Analysis methods
   - Quality assurance

4. **Timeline of Events**
   - Chronological reconstruction
   - Key milestones
   - Actor actions
   - System responses

5. **Findings and Evidence**
   - Detailed analysis
   - Supporting evidence
   - Screenshots and logs
   - Hash values

6. **Conclusions**
   - Root cause
   - Attack vector
   - Scope and impact
   - Recommendations

7. **Appendices**
   - Evidence inventory
   - Chain of custody forms
   - Technical details
   - Tool output
   - LCQL queries used

**Evidence Inventory Template**:
```
Evidence ID: EVD-001
Description: Malicious executable
Source: Sensor ABC123, Host: workstation-01
File Path: C:\Users\victim\Downloads\malware.exe
Collection Method: artifact_get
Collection Time: 2024-01-15 14:32:15 UTC
Collector: analyst@company.com
Hash (SHA256): abc123def456...
Artifact ID: art-789xyz
Storage Location: LimaCharlie Artifact Collection
Retention: 90 days
Notes: Initial infection vector
```

---

## Forensic Investigation Scenarios

### Scenario 1: Ransomware Investigation

**Objective**: Reconstruct ransomware attack from initial infection through encryption.

#### Phase 1: Initial Triage

**Identify Affected Systems**:
```
# Search for encryption-related detections
-24h | plat == windows | * | event/* contains ".encrypted" or event/* contains "ransom" or event/* contains "decrypt" | routing/hostname as host COUNT(event) as events GROUP BY(host)
```

**Collect Volatile Data**:
```bash
# From identified hosts
os_processes
netstat
history_dump
```

#### Phase 2: Timeline Reconstruction

**Initial Infection**:
```
# Look for suspicious downloads or email attachments
-7d | routing/hostname == "victim-host" | NEW_PROCESS | event/PARENT/FILE_PATH contains "OUTLOOK.EXE" or event/PARENT/FILE_PATH contains "chrome.exe" or event/PARENT/FILE_PATH contains "firefox.exe" | event/FILE_PATH contains "Downloads" or event/FILE_PATH contains "Temp" | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline
```

**Execution Chain**:
```
# Process execution timeline
-7d | routing/hostname == "victim-host" | NEW_PROCESS | event/TIMESTAMP as time event/FILE_PATH as process event/PARENT/FILE_PATH as parent event/COMMAND_LINE as cmdline
```

**Ransomware Execution**:
```
# Look for shadow copy deletion (common ransomware behavior)
-7d | routing/hostname == "victim-host" | NEW_PROCESS | event/COMMAND_LINE contains "vssadmin" and event/COMMAND_LINE contains "delete" and event/COMMAND_LINE contains "shadows" | event/TIMESTAMP as time event/COMMAND_LINE as cmd
```

**File Encryption Timeline**:
```
# Mass file modifications
-24h | routing/hostname == "victim-host" | NEW_DOCUMENT FILE_MODIFIED | event/FILE_PATH contains ".encrypted" or event/FILE_PATH contains ".locked" | event/TIMESTAMP as time event/FILE_PATH as file
```

#### Phase 3: Artifact Collection

**Collect Malware**:
```bash
# Hash and collect initial dropper
file_hash C:\Users\victim\Downloads\invoice.exe
artifact_get C:\Users\victim\Downloads\invoice.exe

# Collect ransomware executable
file_hash C:\ProgramData\system32.exe
artifact_get C:\ProgramData\system32.exe
```

**Collect Ransom Note**:
```bash
artifact_get C:\Users\victim\Desktop\HOW_TO_DECRYPT.txt
```

**Collect Event Logs**:
```bash
log_get Security
log_get System
artifact_get C:\Windows\System32\winevt\Logs\Security.evtx
```

#### Phase 4: Memory Analysis

**Memory Dump for Decryption Keys**:
```yaml
# Capture memory before shutdown
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 90
```

**Process Memory for Active Ransomware**:
```bash
# Get PID of ransomware
os_processes

# Extract strings (may contain key)
mem_strings --pid <ransomware_pid>

# Memory map
mem_map --pid <ransomware_pid>
```

#### Phase 5: Network Analysis

**C2 Communications**:
```
# Network connections during timeframe
-24h | routing/hostname == "victim-host" | NETWORK_CONNECTIONS | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process
```

**DNS Queries**:
```
# Ransomware C2 domains
-24h | routing/hostname == "victim-host" | DNS_REQUEST | event/TIMESTAMP as time event/DOMAIN_NAME as domain
```

#### Phase 6: Persistence Analysis

**Check Autoruns**:
```bash
os_autoruns
```

**Registry Persistence**:
```
-7d | routing/hostname == "victim-host" | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\Run" or event/REGISTRY_KEY contains "\\Services" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value
```

#### Phase 7: Impact Assessment

**Encrypted Files**:
```
# Count of encrypted files
-24h | routing/hostname == "victim-host" | NEW_DOCUMENT FILE_MODIFIED | event/FILE_PATH contains ".encrypted" | COUNT(event) as encrypted_files
```

**File Deletion**:
```
# Deleted shadow copies
-24h | routing/hostname == "victim-host" | FILE_DELETE | event/TIMESTAMP as time event/FILE_PATH as file
```

#### Phase 8: Reporting

**Forensic Report Sections**:
1. Initial infection vector (phishing email, malicious download)
2. Dropper execution and deobfuscation
3. Ransomware payload deployment
4. Shadow copy deletion
5. File encryption process
6. Ransom note delivery
7. C2 communication
8. Persistence mechanisms
9. Scope of encryption
10. Recovery recommendations

---

### Scenario 2: Insider Threat Investigation

**Objective**: Investigate suspected data exfiltration by internal user.

#### Phase 1: Scope Identification

**Identify Suspect User Activities**:
```
# All activity by specific user
-30d | plat == windows | NEW_PROCESS | event/USER_NAME == "DOMAIN\\suspect" | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline routing/hostname as host
```

**Login Timeline**:
```
-30d | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/TargetUserName == "suspect" | event/TIMESTAMP as time routing/hostname as host event/EVENT/EventData/LogonType as type event/EVENT/EventData/IpAddress as source
```

#### Phase 2: File Access Analysis

**Sensitive File Access**:
```
# Access to specific file types or locations
-30d | routing/hostname == "suspect-workstation" | FILE_TYPE_ACCESSED | event/FILE_PATH contains "\\Confidential\\" or event/FILE_PATH contains "\\Finance\\" or event/FILE_PATH ends with ".xlsx" or event/FILE_PATH ends with ".docx" | event/TIMESTAMP as time event/FILE_PATH as file
```

**File Copies to External Media**:
```
-30d | routing/hostname == "suspect-workstation" | NEW_DOCUMENT | event/FILE_PATH starts with "E:\\" or event/FILE_PATH starts with "F:\\" | event/TIMESTAMP as time event/FILE_PATH as file
```

#### Phase 3: Network Activity

**Cloud Storage Uploads**:
```
# Connections to cloud storage services
-30d | routing/hostname == "suspect-workstation" | DNS_REQUEST NETWORK_CONNECTIONS | event/* contains "dropbox" or event/* contains "onedrive" or event/* contains "drive.google" | event/TIMESTAMP as time routing/event_type as activity
```

**Large Data Transfers**:
```
-30d | routing/hostname == "suspect-workstation" | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/BYTES_SENT > 10485760 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/BYTES_SENT as bytes event/FILE_PATH as process
```

**Email with Attachments**:
```
# SMTP connections
-30d | routing/hostname == "suspect-workstation" | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT == 25 or event/NETWORK_ACTIVITY/DESTINATION/PORT == 587 or event/NETWORK_ACTIVITY/DESTINATION/PORT == 465 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as smtp_server
```

#### Phase 4: Removable Media

**USB Device Usage**:
```
# Volume mount events
-30d | routing/hostname == "suspect-workstation" | VOLUME_MOUNT VOLUME_UNMOUNT | event/TIMESTAMP as time routing/event_type as activity event/VOLUME_NAME as device
```

**Files Copied to USB**:
```
# Assuming USB mounted as E: or F:
-30d | routing/hostname == "suspect-workstation" | NEW_DOCUMENT | event/FILE_PATH starts with "E:\\" or event/FILE_PATH starts with "F:\\" | event/TIMESTAMP as time event/FILE_PATH as file event/HASH as hash
```

#### Phase 5: Evidence Collection

**Collect Browser History**:
```bash
artifact_get C:\Users\suspect\AppData\Local\Google\Chrome\User Data\Default\History
artifact_get C:\Users\suspect\AppData\Local\Microsoft\Edge\User Data\Default\History
```

**Collect Email Evidence**:
```bash
# Outlook PST files
dir_list C:\Users\suspect\AppData\Local\Microsoft\Outlook
artifact_get C:\Users\suspect\AppData\Local\Microsoft\Outlook\*.pst
```

**Collect Cloud Storage Sync Logs**:
```bash
artifact_get C:\Users\suspect\AppData\Local\Dropbox\*\*.dbx
```

**Collect Recent Files**:
```bash
artifact_get C:\Users\suspect\AppData\Roaming\Microsoft\Windows\Recent\*
```

#### Phase 6: Timeline Creation

**Comprehensive User Activity Timeline**:
```
-30d | routing/hostname == "suspect-workstation" | NEW_PROCESS FILE_TYPE_ACCESSED NEW_DOCUMENT NETWORK_CONNECTIONS VOLUME_MOUNT | event/TIMESTAMP as time routing/event_type as activity event/FILE_PATH as detail
```

#### Phase 7: Reporting

**Key Evidence Points**:
1. Access to sensitive files (dates, times, files)
2. File copies to external media (USB, cloud)
3. Large network transfers (destinations, volumes)
4. Email activity (SMTP connections, timing)
5. Cloud storage usage (services, upload volumes)
6. Timeline correlation with employment events

---

### Scenario 3: Web Shell Investigation

**Objective**: Investigate web server compromise via web shell.

#### Phase 1: Detection and Triage

**Identify Web Shell Execution**:
```
# Web server spawning shells
-24h | plat == linux | NEW_PROCESS | event/PARENT/FILE_PATH contains "apache" or event/PARENT/FILE_PATH contains "nginx" or event/PARENT/FILE_PATH contains "httpd" | event/FILE_PATH ends with "sh" or event/FILE_PATH ends with "bash" | event/TIMESTAMP as time event/FILE_PATH as shell event/COMMAND_LINE as cmd routing/hostname as host
```

**Windows IIS Web Shell**:
```
-24h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "w3wp.exe" | event/FILE_PATH ends with "cmd.exe" or event/FILE_PATH ends with "powershell.exe" | event/TIMESTAMP as time event/COMMAND_LINE as cmd routing/hostname as host
```

#### Phase 2: Web Shell Location

**Find Suspicious Web Files**:
```bash
# List web root
dir_list /var/www/html
dir_list C:\inetpub\wwwroot

# Look for recently modified files
dir_list /var/www/html --sort-by modified
```

**Common Web Shell Names**:
```bash
# Search for suspicious files
# Look for: shell.php, c99.php, r57.php, cmd.php, etc.
```

**Get File Information**:
```bash
file_info /var/www/html/uploads/shell.php
file_hash /var/www/html/uploads/shell.php
```

#### Phase 3: Web Shell Analysis

**Collect Web Shell**:
```bash
artifact_get /var/www/html/uploads/shell.php
```

**Process Timeline from Web Shell**:
```
# All processes spawned by web server
-7d | routing/hostname == "web-server" | NEW_PROCESS | event/PARENT/FILE_PATH contains "httpd" or event/PARENT/FILE_PATH contains "nginx" or event/PARENT/FILE_PATH contains "w3wp" | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline
```

#### Phase 4: Web Server Log Analysis

**Collect Access Logs**:
```bash
# Apache/Nginx
artifact_get /var/log/apache2/access.log
artifact_get /var/log/nginx/access.log
artifact_get /var/log/httpd/access_log

# IIS
artifact_get C:\inetpub\logs\LogFiles\W3SVC1\u_ex*.log
```

**Collect Error Logs**:
```bash
artifact_get /var/log/apache2/error.log
artifact_get /var/log/nginx/error.log
```

#### Phase 5: Commands Executed via Web Shell

**Command Execution Timeline**:
```
# Commands run by web server user
-7d | routing/hostname == "web-server" | NEW_PROCESS | event/USER_NAME == "www-data" or event/USER_NAME == "apache" or event/USER_NAME == "IIS APPPOOL" | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmd
```

**Common Post-Exploitation Commands**:
- id, whoami: User enumeration
- uname -a: System information
- ls, dir: Directory listing
- cat, type: File reading
- wget, curl: File download
- nc, netcat: Reverse shells

#### Phase 6: Network Activity from Web Shell

**Outbound Connections from Web Server**:
```
-7d | routing/hostname == "web-server" | NETWORK_CONNECTIONS | event/FILE_PATH contains "httpd" or event/FILE_PATH contains "nginx" or event/FILE_PATH contains "w3wp" | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/DESTINATION/PORT as port
```

**Reverse Shell Connections**:
```
-7d | routing/hostname == "web-server" | NEW_TCP4_CONNECTION | event/FILE_PATH ends with "sh" or event/FILE_PATH contains "nc" or event/FILE_PATH contains "netcat" | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as c2_ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port
```

#### Phase 7: Persistence and Privilege Escalation

**Check for Cron Jobs**:
```bash
artifact_get /etc/crontab
artifact_get /var/spool/cron/crontabs/*
```

**Check for SSH Keys**:
```bash
artifact_get /root/.ssh/authorized_keys
artifact_get /home/*/.ssh/authorized_keys
```

**Sudo Usage**:
```bash
artifact_get /var/log/auth.log
```

#### Phase 8: Initial Access Vector

**Web Application Vulnerability**:
- Review web logs for exploit attempts
- File upload functionality abuse
- SQL injection leading to file write
- Insecure deserialization
- Path traversal

**Timeline Correlation**:
1. Web shell upload time (file creation)
2. First access to web shell (web logs)
3. First command execution (process events)
4. Privilege escalation attempts
5. Persistence establishment
6. Data access or exfiltration

---

## Reporting and Documentation

### Forensic Report Best Practices

**Clarity and Precision**:
- Use clear, unambiguous language
- Define technical terms
- Provide context for non-technical readers
- Support claims with evidence
- Separate facts from interpretations

**Objectivity**:
- Present findings impartially
- Include evidence that contradicts hypothesis
- Document limitations and uncertainties
- Avoid speculation without labeling it as such
- Let evidence speak

**Reproducibility**:
- Document all tools and versions
- Provide exact commands used
- Include LCQL queries
- Reference collection methods
- Enable peer review and validation

### Report Structure Template

```markdown
# Forensic Investigation Report

## Executive Summary
[High-level overview for management]

## Case Information
- Case Number: INC-2024-001
- Investigator: analyst@company.com
- Date Range: 2024-01-01 to 2024-01-15
- Systems Examined: 5 endpoints, 1 server
- Report Date: 2024-01-20

## Scope and Objectives
[What was investigated and why]

## Investigation Summary
[Key findings in brief]

## Methodology
### Tools Used
- LimaCharlie EDR (version X.Y.Z)
- Volatility Framework 3.0
- Registry Explorer
- Wireshark

### Data Sources
- LimaCharlie telemetry (30 days)
- Windows Event Logs
- Memory dumps (3 systems)
- Artifact collections (files, logs)

## Timeline of Events
[Chronological reconstruction]
| Time (UTC) | Event | System | Evidence |
|------------|-------|--------|----------|
| 2024-01-10 14:32 | Phishing email opened | WS-001 | Email logs |
| 2024-01-10 14:33 | Malicious attachment executed | WS-001 | LC-EVT-12345 |
| ... | ... | ... | ... |

## Detailed Findings
### Finding 1: Initial Compromise
[Detailed analysis with supporting evidence]

### Finding 2: Lateral Movement
[Detailed analysis with supporting evidence]

## Evidence Inventory
[List of all collected evidence with chain of custody]

## Conclusions
[What happened, how, and impact]

## Recommendations
[Remediation and prevention measures]

## Appendices
### Appendix A: LCQL Queries Used
### Appendix B: Hash Values
### Appendix C: IOC List
### Appendix D: Technical Details
```

### Evidence Presentation

**Screenshots**:
- Annotate to highlight key information
- Include timestamp and context
- Reference in report text
- Maintain originals

**Logs and Command Output**:
- Include relevant excerpts
- Provide full logs in appendices
- Highlight key lines
- Maintain formatting

**LCQL Queries**:
```
# Document queries used for reproducibility

# Query 1: Initial malware detection
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH contains "Downloads" and event/PARENT/FILE_PATH contains "OUTLOOK.EXE" | event/TIMESTAMP as time event/FILE_PATH as process event/HASH as hash routing/hostname as host

# Query 2: Lateral movement timeline
-7d | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT == 445 or event/NETWORK_ACTIVITY/DESTINATION/PORT == 3389 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as target routing/hostname as source
```

### Indicator of Compromise (IOC) Documentation

**IOC Format**:
```yaml
iocs:
  file_hashes:
    - hash: abc123def456789...
      type: SHA256
      description: "Initial dropper executable"
      first_seen: "2024-01-10T14:33:00Z"

  domains:
    - domain: "evil-c2.example.com"
      type: C2
      first_seen: "2024-01-10T14:35:00Z"

  ip_addresses:
    - ip: "203.0.113.50"
      type: C2
      first_seen: "2024-01-10T14:35:00Z"

  file_paths:
    - path: "C:\\ProgramData\\system32.exe"
      description: "Malware persistence location"

  registry_keys:
    - key: "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\SystemUpdate"
      value: "C:\\ProgramData\\system32.exe"
      description: "Persistence mechanism"
```

### Lessons Learned and Detection Development

**Convert Findings to Detections**:

Based on investigation findings, create D&R rules:

```yaml
# Example: Detect similar initial access
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/PARENT/FILE_PATH
      value: OUTLOOK.EXE
      case sensitive: false
    - op: contains
      path: event/FILE_PATH
      value: \\Temp\\
    - op: ends with
      path: event/FILE_PATH
      value: .exe
      case sensitive: false

respond:
  - action: report
    name: "Suspicious process from Outlook attachment"
    priority: 4
    metadata:
      mitre: T1566.001
      description: "Based on incident INC-2024-001"
  - action: task
    command: file_hash {{ .event.FILE_PATH }}
  - action: task
    command: artifact_get {{ .event.FILE_PATH }}
    investigation: outlook-attachment-collection
```

**Improvement Recommendations**:
1. Enhanced monitoring in identified gaps
2. Additional detection rules
3. Process improvements
4. Tool additions
5. Training needs

---

## Summary

Digital forensics with LimaCharlie provides comprehensive capabilities for:

1. **Evidence Collection**: Volatile and non-volatile data from endpoints
2. **Timeline Reconstruction**: Chronological event sequences with LCQL
3. **Memory Analysis**: Process, module, and artifact examination
4. **Network Forensics**: Connection analysis and pattern detection
5. **Artifact Examination**: Files, registry, logs, and system state
6. **Evidence Preservation**: Chain of custody and integrity verification
7. **Reporting**: Professional forensic documentation

**Key Forensic Principles**:
- Preserve evidence integrity
- Document chain of custody
- Analyze systematically
- Correlate across data sources
- Report objectively
- Enable reproducibility

**Investigation Workflow**:
1. Identification: Scope and indicators
2. Preservation: Collect volatile data first
3. Collection: Systematic evidence gathering
4. Examination: Timeline and artifact analysis
5. Analysis: Hypothesis testing and correlation
6. Reporting: Professional documentation

**LimaCharlie Forensic Advantages**:
- Real-time and historical visibility
- Comprehensive telemetry (1 year retention)
- Powerful LCQL query language
- Automated artifact collection
- Memory and MFT dumps
- Integration with forensic tools
- Evidence preservation features

Use this skill to guide forensic investigations from initial triage through final reporting, leveraging LimaCharlie's full forensic capabilities to reconstruct incidents, preserve evidence, and deliver actionable intelligence.
