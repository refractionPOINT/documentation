# Advanced Forensic Analysis Techniques

Deep-dive analysis techniques for memory forensics, registry analysis, network forensics, and advanced investigation methods.

## Table of Contents

1. [Advanced Memory Analysis](#advanced-memory-analysis)
2. [Advanced Registry Forensics](#advanced-registry-forensics)
3. [Advanced Network Forensics](#advanced-network-forensics)
4. [Process Injection Detection](#process-injection-detection)
5. [Timeline Reconstruction Techniques](#timeline-reconstruction-techniques)

---

## Advanced Memory Analysis

### Memory Forensics Fundamentals

Memory contains volatile artifacts not present on disk:
- Running processes and loaded modules
- Decrypted data and credentials
- Network connections and artifacts
- Injected code and rootkits
- Malware operating only in memory
- Encryption keys and secrets

### Live Memory Analysis

#### Process Memory Map Analysis

**View loaded modules and memory regions**:
```bash
mem_map --pid <process_id>
```

**What to look for**:
- **Unusual DLLs or modules**: Libraries loaded from non-standard paths
- **Executable memory regions**: Memory with EXECUTE permissions, especially without backing files
- **Reflectively loaded code**: Code loaded directly into memory without touching disk
- **Memory-only malware**: Executable regions without file backing
- **Hidden or unbacked regions**: Suspicious memory allocations

**Analysis workflow**:
```bash
# 1. Get process list
os_processes

# 2. Identify suspicious process (unusual name, path, parent)
# PID: 2468, Path: C:\Users\victim\AppData\Local\Temp\update.exe

# 3. Map memory for suspicious process
mem_map --pid 2468

# 4. Analyze output for:
# - DLLs from unusual paths (C:\Users\*, C:\Temp\*)
# - Executable memory without backing file (MEM_PRIVATE with PAGE_EXECUTE_READWRITE)
# - Known malicious module names
# - Hidden or unbacked regions
```

**Memory region types**:
- **MEM_IMAGE**: Mapped from file (DLL, EXE)
- **MEM_MAPPED**: Mapped file or shared memory
- **MEM_PRIVATE**: Private memory allocation (heap, stack, or suspicious)

**Protection flags to watch**:
- **PAGE_EXECUTE_READWRITE**: Allows code execution and modification (very suspicious)
- **PAGE_EXECUTE_READ**: Allows code execution
- **PAGE_EXECUTE_WRITECOPY**: Copy-on-write executable memory

---

#### Memory String Extraction

**Extract readable strings from process memory**:
```bash
mem_strings --pid <process_id>
```

**Use cases**:
- Find URLs, domains, IP addresses for C2 infrastructure
- Discover credentials, API keys, tokens
- Identify configuration data embedded in malware
- Locate command strings used by malware
- Extract file paths to additional malware components
- Find registry keys for persistence
- Identify encryption keys or passwords

**Analysis technique**:
```bash
# Extract strings
mem_strings --pid 2468

# In the response, look for:
# - IP addresses: 203.0.113.50, 192.168.1.100
# - Domains: evil-c2.com, malicious-domain.org
# - URLs: http://evil-c2.com/beacon.php
# - File paths: C:\Windows\System32\malware.dll
# - Registry keys: HKLM\Software\Microsoft\Windows\CurrentVersion\Run
# - Commands: cmd.exe /c whoami
# - Credentials: username=admin, password=P@ssw0rd
# - API keys: AIzaSyD...
```

**Pattern recognition**:
- Base64-encoded strings (potential encoded payloads)
- Hex strings (potential shellcode or encrypted data)
- User-Agent strings (network communication patterns)
- SQL queries (database interaction)
- PowerShell commands (scripting attacks)

---

#### Targeted Memory String Search

**Search for specific strings in memory**:
```bash
mem_find_string --pid <process_id> --string "<search_term>"
```

**Targeted search strategies**:

**Search for known IOCs**:
```bash
mem_find_string --pid 2468 --string "malicious-domain.com"
mem_find_string --pid 2468 --string "203.0.113.50"
```

**Search for credential keywords**:
```bash
mem_find_string --pid 2468 --string "username"
mem_find_string --pid 2468 --string "password"
mem_find_string --pid 2468 --string "token"
mem_find_string --pid 2468 --string "api_key"
```

**Search for file paths**:
```bash
mem_find_string --pid 2468 --string "C:\ProgramData"
mem_find_string --pid 2468 --string "C:\Users"
mem_find_string --pid 2468 --string ".dll"
mem_find_string --pid 2468 --string ".exe"
```

**Search for registry keys**:
```bash
mem_find_string --pid 2468 --string "CurrentVersion\Run"
mem_find_string --pid 2468 --string "Services"
```

**Search for commands**:
```bash
mem_find_string --pid 2468 --string "cmd.exe"
mem_find_string --pid 2468 --string "powershell"
mem_find_string --pid 2468 --string "wget"
```

---

#### Memory Region Reading

**Read specific memory regions**:
```bash
mem_read --pid <process_id> --base <address> --size <bytes>
```

**When to use**:
- After identifying interesting addresses via mem_map
- To extract specific code or data structures
- To analyze suspected injection points
- To retrieve configuration blocks
- To extract shellcode or payloads

**Workflow example**:
```bash
# 1. Get memory map
mem_map --pid 1234

# 2. Identify suspicious region from output:
# Base: 0x7FFF0000
# Size: 65536
# Protect: PAGE_EXECUTE_READWRITE
# Type: MEM_PRIVATE
# State: MEM_COMMIT

# 3. Read the region
mem_read --pid 1234 --base 0x7FFF0000 --size 65536

# 4. Analyze dumped bytes:
# - Look for PE header (MZ signature: 0x4D5A)
# - Search for shellcode patterns
# - Identify API calls
# - Extract configuration data
```

**What to analyze in dumped memory**:
- **PE headers**: MZ (0x4D5A) and PE (0x5045) signatures indicate executable code
- **Shellcode patterns**: Common instruction sequences (e.g., GetProcAddress, LoadLibrary)
- **String tables**: Embedded strings revealing functionality
- **API calls**: Imported Windows API functions
- **Configuration blocks**: C2 servers, encryption keys, command syntax

---

#### Handle Analysis (Windows)

**List open handles**:
```bash
mem_handles --pid <process_id>
```

**Handle types and forensic value**:
- **File handles**: Files being accessed or locked
- **Registry key handles**: Registry keys being modified
- **Named pipe handles**: IPC mechanisms (potential for process injection)
- **Process handles**: Other processes being accessed (potential injection target)
- **Thread handles**: Threads in other processes (potential injection)
- **Event/Mutex handles**: Synchronization objects (malware infection markers)

**Find specific handles**:
```bash
mem_find_handle --pid <process_id> --path "<path_to_find>"
```

**Use cases**:
```bash
# Find which process has a file open
mem_find_handle --pid 2468 --path "C:\Windows\System32\drivers\malware.sys"

# Find registry key access
mem_find_handle --pid 2468 --path "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"

# Find named pipes (IPC, potential C2 or injection)
mem_find_handle --pid 2468 --path "\\Device\\NamedPipe"
```

**Suspicious handle patterns**:
- Handles to lsass.exe (credential dumping)
- Handles to sensitive files (config files, databases)
- Named pipes with unusual names
- Cross-process handles (injection indicators)
- Handles to system processes from user processes

---

### Full Memory Dumps

#### When to Capture Full Memory

- **Advanced persistent threat (APT) investigation**: Comprehensive analysis required
- **Rootkit or bootkit analysis**: Kernel-level malware suspected
- **Complete system state preservation**: Legal evidence requirements
- **Kernel-level malware suspected**: Analysis requires kernel memory
- **Offline analysis needed**: Tools like Volatility required
- **Credential extraction**: Need to extract passwords, hashes, tickets

#### Capture Memory Dump

**Via Dumper extension**:
```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 90  # days
```

**Process**:
1. Request dump via D&R rule or API
2. Wait for completion (can take several minutes for large memory)
3. Download from Artifact Collection UI or API
4. Verify integrity (check file size, hash if provided)

---

### Offline Memory Analysis with Volatility

#### Volatility Framework Setup

**Installation**:
```bash
# Volatility 3
pip3 install volatility3

# Or download standalone binaries
```

**Identify memory profile**:
```bash
# Volatility 2 (profile identification)
vol.py -f memory.dmp imageinfo

# Volatility 3 (auto-detection)
vol3 -f memory.dmp windows.info
```

---

#### Process Analysis

**List processes**:
```bash
# Volatility 3
vol3 -f memory.dmp windows.pslist
vol3 -f memory.dmp windows.pstree  # Process tree view
```

**Find hidden processes**:
```bash
# Volatility 3
vol3 -f memory.dmp windows.psscan  # Scan for EPROCESS structures
```

**Compare outputs**:
- Processes in pslist but not psscan: Normal
- Processes in psscan but not pslist: **HIDDEN PROCESS** (rootkit indicator)

**Dump process memory**:
```bash
# Volatility 3
vol3 -f memory.dmp -o /output/dir windows.memmap --pid 1234 --dump

# Volatility 2
vol.py -f memory.dmp --profile=Win10x64 procdump -p 1234 -D /output/dir
```

---

#### Network Connections

**Active connections**:
```bash
# Volatility 3
vol3 -f memory.dmp windows.netscan
```

**Analysis points**:
- Unusual ports or protocols
- Connections to public IPs from system processes
- High-numbered source ports (ephemeral port abuse)
- Connections from unexpected processes
- Foreign addresses (geolocation, reputation)

---

#### Code Injection Detection

**Find injected code (malfind)**:
```bash
# Volatility 3
vol3 -f memory.dmp windows.malfind
```

**What malfind detects**:
- Memory regions with PAGE_EXECUTE_READWRITE (unusual for legitimate code)
- Private memory containing executable code
- Sections not backed by a file on disk
- Potentially injected or reflectively loaded code

**Analysis workflow**:
1. Run malfind to identify suspicious memory regions
2. Extract memory region for analysis
3. Disassemble code with tools (IDA, Ghidra, etc.)
4. Identify malicious functionality
5. Extract IOCs (domains, IPs, file paths)

---

#### DLL and Driver Analysis

**List loaded DLLs**:
```bash
# Volatility 3
vol3 -f memory.dmp windows.dlllist --pid 1234
```

**Look for**:
- DLLs loaded from unusual paths (Temp, user directories)
- Unsigned DLLs in signed processes
- DLLs with suspicious names
- Mismatches between memory and disk versions

**List drivers**:
```bash
# Volatility 3
vol3 -f memory.dmp windows.modules
vol3 -f memory.dmp windows.driverscan  # Find hidden drivers
```

**Suspicious drivers**:
- Unsigned drivers
- Drivers from unusual paths
- Rootkit driver names (common patterns)
- Hidden drivers (driverscan vs. modules)

---

#### Registry Analysis from Memory

**List registry hives**:
```bash
# Volatility 3
vol3 -f memory.dmp windows.registry.hivelist
```

**Print specific registry key**:
```bash
# Volatility 3
vol3 -f memory.dmp windows.registry.printkey --key "Software\Microsoft\Windows\CurrentVersion\Run"
```

**Common persistence keys to check**:
```bash
# Run keys
--key "Software\Microsoft\Windows\CurrentVersion\Run"
--key "Software\Microsoft\Windows\CurrentVersion\RunOnce"

# Services
--key "System\CurrentControlSet\Services"

# Winlogon
--key "Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

---

#### Credential Extraction

**Extract passwords and hashes**:
```bash
# Volatility 3
vol3 -f memory.dmp windows.hashdump  # Local account hashes
vol3 -f memory.dmp windows.lsadump   # LSA secrets
vol3 -f memory.dmp windows.cachedump # Cached domain credentials
```

**Note**: Credential extraction requires appropriate privileges and legal authorization.

---

#### Command History

**Extract command line history**:
```bash
# Volatility 3
vol3 -f memory.dmp windows.cmdline  # Process command lines
vol3 -f memory.dmp windows.consoles # Console history (cmd.exe)
```

**Volatility 2**:
```bash
vol.py -f memory.dmp --profile=Win10x64 cmdscan
vol.py -f memory.dmp --profile=Win10x64 consoles
```

**Forensic value**:
- Commands executed by attacker
- Script parameters and arguments
- Credential usage in clear text
- File paths and operations
- Network commands (wget, curl, etc.)

---

### Memory Analysis Best Practices

**Prioritize volatile data**:
1. Capture memory before disk artifacts (memory is most volatile)
2. Network connections change rapidly
3. Running processes may terminate
4. Memory cleared on reboot or shutdown
5. Encryption keys may be cleared

**Correlate with disk evidence**:
- Compare memory modules with files on disk
- Verify process binaries on disk
- Check for memory/disk mismatches (potential packing, in-memory patching)
- Identify packed or protected executables
- Validate file integrity

**Document context**:
- System state at time of capture
- Running applications and services
- User activity at time of capture
- Network state (connections, adapters)
- Time and date (timezone important)
- Reason for capture (incident, suspicious activity)

**Look for anomalies**:
- Processes without disk backing (memory-only malware)
- Modules loaded from unusual paths
- Hidden or unnamed processes
- Executable memory in unexpected locations
- Suspicious parent-child relationships
- Processes running under wrong user account

---

## Advanced Registry Forensics

### Registry Structure and Hives

**Registry hives**:
- **SYSTEM**: System configuration, hardware, drivers, services
- **SOFTWARE**: Installed applications, system-wide software configuration
- **SAM**: Local user accounts, password hashes
- **SECURITY**: Security policies, cached credentials
- **NTUSER.DAT**: Per-user settings (one per user)
- **UsrClass.dat**: Per-user shellbags, file associations

**Hive locations**:
```
# System hives
C:\Windows\System32\config\SYSTEM
C:\Windows\System32\config\SOFTWARE
C:\Windows\System32\config\SAM
C:\Windows\System32\config\SECURITY

# User hives
C:\Users\<username>\NTUSER.DAT
C:\Users\<username>\AppData\Local\Microsoft\Windows\UsrClass.dat
```

---

### Live Registry Analysis

#### Monitor Registry Changes

**Registry writes**:
```
-24h | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY as key event/REGISTRY_VALUE as value event/TIMESTAMP as time event/PROCESS_ID as pid routing/hostname as host
```

**Registry creation**:
```
-24h | plat == windows | REGISTRY_CREATE | event/REGISTRY_KEY as key event/TIMESTAMP as time routing/hostname as host
```

**Registry deletion**:
```
-24h | plat == windows | REGISTRY_DELETE | event/REGISTRY_KEY as key event/TIMESTAMP as time routing/hostname as host
```

---

### Persistence via Registry

#### Autorun Keys

**Run and RunOnce keys**:
```
# Monitor Run key modifications
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\CurrentVersion\\Run" and not event/REGISTRY_KEY contains "\\RunOnce" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host

# RunOnce keys
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\CurrentVersion\\RunOnce" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

**Key locations**:
```
# HKLM (all users)
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce

# HKCU (current user)
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce

# Additional locations
HKLM\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Run  # 32-bit on 64-bit
HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run
```

---

#### Service Persistence

**Monitor service registry changes**:
```
-7d | plat == windows | REGISTRY_WRITE REGISTRY_CREATE | event/REGISTRY_KEY contains "\\CurrentControlSet\\Services" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

**Service key structure**:
```
HKLM\System\CurrentControlSet\Services\<ServiceName>
  - ImagePath: Path to service executable
  - Start: Start type (0=Boot, 1=System, 2=Automatic, 3=Manual, 4=Disabled)
  - Type: Service type
  - DisplayName: Friendly name
```

---

#### Winlogon Persistence

**Winlogon keys**:
```
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\Winlogon" and (event/REGISTRY_KEY contains "Shell" or event/REGISTRY_KEY contains "Userinit" or event/REGISTRY_KEY contains "Notify") | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

**Key locations**:
```
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell
  - Normal: explorer.exe
  - Malicious: explorer.exe, malware.exe

HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit
  - Normal: C:\Windows\system32\userinit.exe,
  - Malicious: C:\Windows\system32\userinit.exe,C:\malware.exe

HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Notify
  - DLL loaded by Winlogon (deprecated in Win7+, but still usable)
```

---

#### AppInit DLLs

**Monitor AppInit_DLLs**:
```
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "AppInit_DLLs" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

**Key location**:
```
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs
  - DLLs loaded into every process using User32.dll
  - Effective but causes stability issues
  - Disabled by default in Windows 8+
```

---

#### Image File Execution Options (IFEO)

**Debugger hijacking**:
```
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "Image File Execution Options" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

**Mechanism**:
```
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<executable>
  - Debugger: <path_to_malware>

# When <executable> runs, Windows launches the Debugger instead
# Legitimate use: Debugging, Application compatibility
# Malicious use: Hijacking sethc.exe (Sticky Keys) for backdoor access
```

---

### Forensic Registry Collection

**Collect registry hives**:
```bash
# System hives
artifact_get C:\Windows\System32\config\SYSTEM --investigation forensic-001
artifact_get C:\Windows\System32\config\SOFTWARE --investigation forensic-001
artifact_get C:\Windows\System32\config\SAM --investigation forensic-001
artifact_get C:\Windows\System32\config\SECURITY --investigation forensic-001

# User hives (all users)
artifact_get C:\Users\*\NTUSER.DAT --investigation forensic-001
artifact_get "C:\Users\*\AppData\Local\Microsoft\Windows\UsrClass.dat" --investigation forensic-001

# Transaction logs (for hive reconstruction)
artifact_get C:\Windows\System32\config\*.LOG* --investigation forensic-001
```

---

### Offline Registry Analysis

#### Analysis Tools

**Registry Explorer (Eric Zimmerman)**:
- GUI tool for browsing registry hives
- Excellent for manual analysis
- Bookmark important keys
- Search functionality
- Timeline view

**RegRipper**:
- Automated registry parsing
- Plugin-based architecture
- Extracts specific artifacts
- Timeline generation
- Command-line friendly

**Registry Decoder (RegistryDecoder)**:
- Commercial tool with free version
- Automated analysis
- Timeline creation
- Keyword search

---

#### Key Registry Artifacts

**UserAssist**:
- **Location**: `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist`
- **Value**: Programs executed via Explorer (ROT13-encoded)
- **Data**: Execution count, last execution time, focus time
- **Forensic value**: Proves program execution by user

**MUICache**:
- **Location**: `NTUSER.DAT\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache`
- **Value**: Executed applications with friendly names
- **Forensic value**: Evidence of execution, even if deleted

**RecentDocs**:
- **Location**: `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs`
- **Value**: Recently opened documents
- **Data**: MRU (Most Recently Used) list by file extension
- **Forensic value**: Files accessed by user

**TypedURLs**:
- **Location**: `NTUSER.DAT\Software\Microsoft\Internet Explorer\TypedURLs`
- **Value**: URLs typed in IE/Edge address bar
- **Forensic value**: Websites visited, potential phishing sites

**Shimcache (AppCompatCache)**:
- **Location**: `SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache`
- **Value**: Executed programs with modification times
- **Capacity**: Up to 1024 entries
- **Forensic value**: Execution artifacts, file modification times
- **Note**: Presence does NOT confirm execution, only that file was assessed

**AmCache**:
- **Location**: `C:\Windows\AppCompat\Programs\Amcache.hve` (separate hive file)
- **Value**: Program execution evidence
- **Data**: First run time, SHA1 hash, file size, publisher
- **Forensic value**: Strong execution evidence with detailed metadata

**BAM/DAM** (Windows 10+):
- **Location**: `SYSTEM\CurrentControlSet\Services\bam\UserSettings\{SID}`, `SYSTEM\CurrentControlSet\Services\dam\UserSettings\{SID}`
- **Value**: Background Activity Moderator / Desktop Activity Moderator
- **Data**: Full path, last execution timestamp
- **Forensic value**: Recent execution evidence with precise timestamps

---

### Registry Timeline Analysis

**Create timeline from registry events**:
```
-30d | plat == windows | REGISTRY_WRITE REGISTRY_CREATE REGISTRY_DELETE | event/TIMESTAMP as time routing/event_type as activity event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

**Focus on persistence keys**:
```
-30d | plat == windows | REGISTRY_WRITE REGISTRY_CREATE | event/REGISTRY_KEY contains "\\Run" or event/REGISTRY_KEY contains "\\Services" or event/REGISTRY_KEY contains "\\Winlogon" or event/REGISTRY_KEY contains "Image File Execution Options" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value event/PROCESS_ID as pid routing/hostname as host
```

---

### Registry Forensics Workflow

1. **Collect Hives**:
   - Live collection via artifact_get
   - Or from forensic disk image
   - Include transaction logs (.LOG files)

2. **Parse with Tools**:
   - Extract autorun entries (Registry Explorer, autoruns)
   - Parse execution artifacts (UserAssist, Shimcache, AmCache, BAM)
   - Identify installed software (SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall)
   - Extract user activity (RecentDocs, TypedURLs, MUICache)
   - Analyze shellbags for folder access

3. **Correlate with Telemetry**:
   - Match registry writes with REGISTRY_WRITE events
   - Correlate timestamps with file/process events
   - Validate persistence mechanisms
   - Identify processes that created registry entries

4. **Timeline Integration**:
   - Add registry artifacts to master timeline
   - Cross-reference with process execution
   - Identify discrepancies or anomalies
   - Build narrative of attacker activity

---

## Advanced Network Forensics

### Network Connection Analysis

#### Current Network State

**Active connections**:
```bash
netstat
```

**Analysis points**:
- **STATE**: ESTABLISHED (active), LISTENING (server), TIME_WAIT (closing)
- **Unusual ports**: Non-standard ports for common services
- **Unexpected processes**: System binaries making external connections
- **Foreign addresses**: Public IPs, geolocation, reputation
- **High-numbered ports**: Ephemeral port abuse or port scanning

---

### Network Timeline Reconstruction

**All network connections**:
```
-24h | plat == windows | NETWORK_CONNECTIONS | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process routing/hostname as host
```

**TCP connections by type**:
```
# IPv4 TCP connections
-12h | plat == windows | NEW_TCP4_CONNECTION TERMINATE_TCP4_CONNECTION | event/TIMESTAMP as time routing/event_type as activity event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process routing/hostname as host
```

**UDP traffic**:
```
-12h | plat == windows | NEW_UDP4_CONNECTION TERMINATE_UDP4_CONNECTION | event/TIMESTAMP as time routing/event_type as activity event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/DESTINATION/PORT as port routing/hostname as host
```

---

### DNS Analysis

**All DNS queries**:
```
-24h | plat == windows | DNS_REQUEST | event/TIMESTAMP as time event/DOMAIN_NAME as domain event/PROCESS_ID as pid routing/hostname as host
```

**Suspicious DNS patterns**:

**DGA domains (Domain Generation Algorithms)**:
```
# Long or random-looking domains
-12h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME length > 20 | event/DOMAIN_NAME as domain routing/hostname as host COUNT(event) as count GROUP BY(domain)

# Unusual TLDs
-12h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME ends with ".tk" or event/DOMAIN_NAME ends with ".cc" or event/DOMAIN_NAME ends with ".xyz" or event/DOMAIN_NAME ends with ".top" | event/DOMAIN_NAME as domain routing/hostname as host
```

**DNS tunneling (data exfiltration via DNS)**:
```
# Excessive subdomain length (base64-encoded data)
-12h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME length > 50 | event/TIMESTAMP as time event/DOMAIN_NAME as domain routing/hostname as host

# High query volume to single domain
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT(event) as queries GROUP BY(domain) | queries > 100

# Many unique subdomains
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "tunneling-domain.com" | event/DOMAIN_NAME as subdomain COUNT_UNIQUE(subdomain) as unique_queries
```

**Low prevalence domains (rare domains, potential C2)**:
```
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as sensor_count GROUP BY(domain) | sensor_count <= 2
```

---

### Connection Pattern Analysis

**Beaconing detection** (regular C2 communication):
```
# Repetitive connections to same destination
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/FILE_PATH as process COUNT(event) as conn_count GROUP BY(dst_ip process) | conn_count > 50
```

**Analysis**:
- Count connections per destination
- Look for regular intervals
- Identify processes with repetitive behavior
- Correlate with DNS queries

**Port scanning**:
```
# Many destinations, same source
-6h | plat == windows | NEW_TCP4_CONNECTION | routing/hostname as source event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst COUNT_UNIQUE(dst) as target_count GROUP BY(source) | target_count > 20

# Many ports, same destination
-6h | plat == windows | NEW_TCP4_CONNECTION | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/DESTINATION/PORT as port COUNT_UNIQUE(port) as port_count GROUP BY(dst) | port_count > 20
```

**Unusual protocols/ports**:
```
# Non-standard ports for common services
-12h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT not in (80, 443, 53, 22, 3389, 445, 139, 135, 389) and event/NETWORK_ACTIVITY/DESTINATION/PORT < 1024 | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process routing/hostname as host
```

**Data transfer volume**:
```
# Large outbound transfers
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/BYTES_SENT > 104857600 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/BYTES_SENT as bytes event/FILE_PATH as process routing/hostname as host
```

---

### Process-Network Correlation

**Network activity by process**:
```
-12h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip COUNT(event) as connections GROUP BY(process dst_ip)
```

**Unusual process network activity**:
```
# System binaries making external connections
-12h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH contains "\\System32\\" and event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is public | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst routing/hostname as host

# Office apps making network connections (potential macro malware)
-12h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH contains "WINWORD.EXE" or event/FILE_PATH contains "EXCEL.EXE" or event/FILE_PATH contains "POWERPNT.EXE" | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst routing/hostname as host
```

---

### PCAP Analysis

**PCAP collection (Linux only)**:
```yaml
# Configure in Artifact Collection
# Pattern: pcap://<interface>
# Example: pcap://eth0
```

**Trigger PCAP capture**:
- Via sensor tag matching Artifact Collection rule
- D&R rule response action
- Manual trigger via UI

**Download and analyze**:
1. Download PCAP from Artifact Collection
2. Open in Wireshark or tcpdump
3. Apply filters for analysis

**Wireshark filters**:
```
# HTTP requests
http.request

# DNS queries
dns.qry.name contains "malicious"

# TLS/SSL handshakes
tls.handshake.type == 1

# Specific IP
ip.addr == 203.0.113.50

# Large transfers
tcp.len > 1400

# Unusual ports
tcp.port > 10000 and tcp.port < 65535
```

**Analysis focus**:
- Protocol-level details
- Payload extraction (HTTP, FTP, etc.)
- Encrypted traffic metadata (TLS SNI, certificate details)
- Communication patterns (beaconing intervals)
- Data exfiltration evidence (large uploads)

---

### Geographic and Threat Intelligence Enrichment

**Identify public IPs**:
```
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is public | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as ip COUNT(event) as connections GROUP BY(ip)
```

**External enrichment**:
- **VirusTotal**: IP and domain reputation, malware associations
- **AbuseIPDB**: IP abuse reports, confidence score
- **AlienVault OTX**: Open threat intelligence
- **Shodan**: IP service enumeration
- **MaxMind GeoIP**: Geolocation data
- **WHOIS**: Domain registration data

**Integration with threat feeds**:
```
# Lookup in LimaCharlie threat feed
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is lookup in resource: "hive://lookup/malicious-ips" | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as ip routing/hostname as host
```

---

## Process Injection Detection

### Injection Techniques

**Common injection methods**:
1. **CreateRemoteThread**: Create thread in remote process
2. **Process Hollowing**: Unmap legitimate process memory, replace with malicious code
3. **Reflective DLL Injection**: Load DLL from memory without touching disk
4. **APC Injection**: Queue APC to existing thread
5. **SetWindowsHookEx**: Install hook DLL
6. **Process Doppelgänging**: Abuse NTFS transactions
7. **AtomBombing**: Abuse atom tables
8. **Shim Injection**: Abuse application compatibility shims

---

### Detection Queries

**Remote thread creation**:
```
-6h | plat == windows | NEW_REMOTE_THREAD | event/PROCESS_ID as target_pid event/PARENT_PROCESS_ID as injector_pid event/TIMESTAMP as time routing/hostname as host
```

**Thread injection events**:
```
-6h | plat == windows | THREAD_INJECTION | event/INJECTED_ADDRESS as address event/PROCESS_ID as pid event/SOURCE_PROCESS_ID as source event/TIMESTAMP as time routing/hostname as host
```

**Sensitive process access**:
```
-12h | plat == windows | SENSITIVE_PROCESS_ACCESS | event/TARGET_PROCESS_ID as target event/TARGET_PROCESS_PATH as target_path event/SOURCE_PROCESS_ID as source event/SOURCE_PROCESS_PATH as source_path event/TIMESTAMP as time routing/hostname as host
```

**Module memory/disk mismatch** (process hollowing indicator):
```
-12h | plat == windows | MODULE_MEM_DISK_MISMATCH | event/PROCESS_ID as pid event/FILE_PATH as process event/MISMATCHED_MODULE as module event/TIMESTAMP as time routing/hostname as host
```

---

### Analysis Workflow

1. **Identify injection event**:
   - NEW_REMOTE_THREAD, SENSITIVE_PROCESS_ACCESS, etc.
   - Note source and target PIDs

2. **Correlate with process timeline**:
   - What was the source process doing?
   - Is target process sensitive (lsass, services, etc.)?

3. **Memory analysis**:
   - mem_map on target process
   - Look for PAGE_EXECUTE_READWRITE regions
   - Check for unbacked executable memory

4. **Extract injected code**:
   - mem_read on suspicious region
   - Analyze with disassembler
   - Extract IOCs

---

## Timeline Reconstruction Techniques

### Multi-Source Timeline

**Comprehensive timeline query**:
```
-24h | plat == windows | NEW_PROCESS NETWORK_CONNECTIONS NEW_DOCUMENT FILE_MODIFIED REGISTRY_WRITE SERVICE_CHANGE VOLUME_MOUNT | event/TIMESTAMP as time routing/event_type as event_type routing/hostname as host
```

**Event type priority**:
1. STARTING_UP, SHUTTING_DOWN: System events
2. NEW_PROCESS, TERMINATE_PROCESS: Execution
3. NETWORK_CONNECTIONS, DNS_REQUEST: Network activity
4. NEW_DOCUMENT, FILE_MODIFIED, FILE_DELETE: File operations
5. REGISTRY_WRITE, REGISTRY_CREATE: Persistence
6. WEL: Authentication, privileges

---

### Attack Phase Mapping

**Map timeline to MITRE ATT&CK**:

1. **Initial Access**: How attacker got in
2. **Execution**: What was run
3. **Persistence**: How attacker maintains access
4. **Privilege Escalation**: How attacker elevated
5. **Defense Evasion**: What attacker hid
6. **Credential Access**: Credentials stolen
7. **Discovery**: Enumeration activity
8. **Lateral Movement**: Spread to other systems
9. **Collection**: Data gathered
10. **Exfiltration**: Data stolen
11. **Impact**: Damage inflicted (encryption, deletion)

---

### Correlation Techniques

**User-based correlation**:
```
-24h | plat == windows | * | event/USER_NAME == "DOMAIN\\victim" | event/TIMESTAMP as time routing/event_type as activity
```

**Hash-based correlation** (track file across systems):
```
-7d | plat == windows | CODE_IDENTITY | event/HASH == "abc123..." | event/TIMESTAMP as time event/FILE_PATH as path routing/hostname as host
```

**Network-based correlation** (track lateral movement):
```
-7d | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT == 445 or event/NETWORK_ACTIVITY/DESTINATION/PORT == 3389 or event/NETWORK_ACTIVITY/DESTINATION/PORT == 5985 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as target routing/hostname as source
```

---

## Additional Resources

**For command reference**: See REFERENCE.md

**For investigation scenarios**: See EXAMPLES.md

**For troubleshooting**: See TROUBLESHOOTING.md

**For core methodology**: See SKILL.md
