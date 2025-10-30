# Threat Hunting Examples

Complete hunt-to-detection workflows with detailed examples and advanced hunting techniques.

## Table of Contents

- [Converting Hunts to Detections](#converting-hunts-to-detections)
- [Complete Hunting Workflow Example](#complete-hunting-workflow-example)
- [Advanced Hunting Techniques](#advanced-hunting-techniques)

## Converting Hunts to Detections

### Example 1: Office Document Spawning PowerShell

**Hunt Query:**
```
-7d | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "winword.exe" and event/FILE_PATH contains "powershell.exe" and event/COMMAND_LINE contains "-enc"
```

**D&R Rule:**
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
  with child:
    op: and
    rules:
      - op: ends with
        event: NEW_PROCESS
        path: event/FILE_PATH
        value: powershell.exe
        case sensitive: false
      - op: contains
        path: event/COMMAND_LINE
        value: -enc
        case sensitive: false
respond:
  - action: report
    name: Office Application Spawning Encoded PowerShell
    priority: 4
    metadata:
      mitre: T1059.001, T1566.001
      description: Office document spawned PowerShell with encoded command
  - action: task
    command: history_dump
    investigation: office-powershell
  - action: add tag
    tag: potential-macro-malware
    ttl: 3600
```

### Example 2: Rare Domain Detection

**Hunt Query:**
```
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as sensors GROUP BY(domain) | sensors == 1
```

**D&R Rule with Lookup:**

First, create a lookup of known-good domains. Then:

```yaml
detect:
  event: DNS_REQUEST
  op: and
  rules:
    - op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/malware-domains
      case sensitive: false
      not: true  # NOT in malware list
    - op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/whitelist-domains
      case sensitive: false
      not: true  # NOT in whitelist
respond:
  - action: report
    name: "Rare domain resolved: {{ .event.DOMAIN_NAME }}"
    priority: 2
    suppression:
      max_count: 1
      period: 24h
      is_global: true
      keys:
        - '{{ .event.DOMAIN_NAME }}'
```

### Example 3: LOLBin Abuse

**Hunt Query:**
```
-12h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with "certutil.exe" and event/COMMAND_LINE contains "http"
```

**D&R Rule:**
```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows
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
                  value: urlcache
                - op: contains
                  path: event/COMMAND_LINE
                  value: http
        - op: and
          rules:
            - op: ends with
              path: event/FILE_PATH
              value: bitsadmin.exe
              case sensitive: false
            - op: contains
              path: event/COMMAND_LINE
              value: /transfer
respond:
  - action: report
    name: "LOLBin Download Activity - {{ .event.FILE_PATH }}"
    priority: 3
    metadata:
      mitre: T1105
      description: Legitimate Windows binary used to download files
  - action: task
    command: history_dump
    investigation: lolbin-download
```

### Example 4: Suspicious Parent-Child Relationships

**Hunt Query:**
```
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "svchost.exe" and (event/FILE_PATH contains "cmd.exe" or event/FILE_PATH contains "powershell.exe")
```

**D&R Rule:**
```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: ends with
      path: event/PARENT/FILE_PATH
      value: svchost.exe
      case sensitive: false
  with child:
    op: or
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
respond:
  - action: report
    name: "Svchost Spawning Shell"
    priority: 3
    metadata:
      mitre: T1059
      description: Svchost spawned cmd.exe or powershell.exe
  - action: task
    command: history_dump
    investigation: svchost-shell
```

### Example 5: LSASS Memory Access

**Hunt Query:**
```
-12h | plat == windows | SENSITIVE_PROCESS_ACCESS | event/EVENTS/*/event/FILE_PATH contains "lsass.exe"
```

**D&R Rule:**
```yaml
detect:
  event: SENSITIVE_PROCESS_ACCESS
  op: is platform
  name: windows
respond:
  - action: report
    name: "LSASS Memory Access Detected"
    priority: 5
    metadata:
      mitre: T1003.001
      description: Process accessed LSASS memory - potential credential dumping
  - action: task
    command: history_dump
    investigation: lsass-access
  - action: task
    command: mem_strings --pid {{ .event.EVENTS.0.event.PROCESS_ID }}
    investigation: lsass-access-memstrings
  - action: add tag
    tag: credential-access-attempt
    ttl: 7200
```

### Example 6: Beaconing Detection

**Hunt Query:**
```
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/FILE_PATH as process COUNT(event) as conn_count GROUP BY(dst_ip process) | conn_count > 50
```

**D&R Rule with Stateful Detection:**
```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: stateful event
      keys:
        - '{{ .event.NETWORK_ACTIVITY.DESTINATION.IP_ADDRESS }}'
        - '{{ .routing.sid }}'
      count: 50
      within: 3600
respond:
  - action: report
    name: "Potential C2 Beaconing - {{ .event.FILE_PATH }}"
    priority: 4
    metadata:
      mitre: T1071
      description: Process made > 50 connections to same destination
    suppression:
      max_count: 1
      period: 3600
      keys:
        - '{{ .event.NETWORK_ACTIVITY.DESTINATION.IP_ADDRESS }}'
        - '{{ .routing.sid }}'
  - action: task
    command: netstat
    investigation: beaconing-netstat
```

### Example 7: Privilege Escalation via Service

**Hunt Query:**
```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "7045" and event/EVENT/EventData/ImagePath not contains "\\windows\\"
```

**D&R Rule:**
```yaml
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '7045'
    - op: contains
      path: event/EVENT/EventData/ImagePath
      value: \windows\
      case sensitive: false
      not: true
respond:
  - action: report
    name: "Suspicious Service Creation"
    priority: 4
    metadata:
      mitre: T1543.003
      description: Service created with non-Windows path
  - action: task
    command: os_services
    investigation: suspicious-service
```

### Example 8: Data Exfiltration to Cloud Storage

**Hunt Query:**
```
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "dropbox" or event/DOMAIN_NAME contains "mega.nz" or event/DOMAIN_NAME contains "wetransfer"
```

**D&R Rule:**
```yaml
detect:
  event: DNS_REQUEST
  op: or
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
respond:
  - action: report
    name: "Cloud Storage Access - {{ .event.DOMAIN_NAME }}"
    priority: 2
    metadata:
      mitre: T1567.002
      description: Access to cloud storage service detected
    suppression:
      max_count: 1
      period: 86400
      keys:
        - '{{ .event.DOMAIN_NAME }}'
        - '{{ .routing.sid }}'
  - action: task
    command: netstat
    investigation: cloud-storage-access
```

## Complete Hunting Workflow Example

### Scenario: Hunting for Ransomware Precursors

**Step 1: Hypothesis**

"Ransomware operators are using RDP to gain initial access and then deploying ransomware payloads."

**Step 2: Hunt for RDP from External IPs**

```
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "10" | event/EVENT/EventData/IpAddress as src_ip event/EVENT/EventData/TargetUserName as user routing/hostname as host
```

**Analysis:**
- Review source IPs for non-RFC1918 addresses
- Identify unusual logon times (off-hours)
- Note hostnames and users involved

**Step 3: Pivot on Suspicious Hosts**

After identifying suspicious RDP logons to host "WKS-FINANCE-01":

```
-7d | hostname == "WKS-FINANCE-01" | NEW_PROCESS | event/FILE_PATH as process event/COMMAND_LINE as cmd routing/event_time as time
```

**Analysis:**
- Review process execution timeline
- Look for unsigned executables
- Identify reconnaissance activity

**Step 4: Look for File Enumeration**

```
-7d | hostname == "WKS-FINANCE-01" | NEW_PROCESS | event/COMMAND_LINE contains "dir " or event/COMMAND_LINE contains "tree" | event/COMMAND_LINE as cmd
```

**Findings:**
- Multiple directory listing commands executed
- Focus on network shares and sensitive directories

**Step 5: Check for Encryption Tools**

```
-7d | hostname == "WKS-FINANCE-01" | CODE_IDENTITY | event/FILE_PATH contains "\\Users\\" | event/FILE_PATH as path event/HASH as hash event/SIGNATURE/FILE_IS_SIGNED as signed
```

**Findings:**
- Unsigned executable: `C:\Users\admin\AppData\Local\Temp\encrypt.exe`
- Hash: `abc123def456...`

**Step 6: Look for Mass File Operations**

```
-7d | hostname == "WKS-FINANCE-01" | FILE_MODIFIED | event/FILE_PATH as path routing/event_time as time
```

**Analysis:**
- Check for volume of file modifications
- Look for file extension changes (.encrypted, .locked, etc.)

**Step 7: Network Activity Check**

```
-7d | hostname == "WKS-FINANCE-01" | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/FILE_PATH as process
```

**Findings:**
- Connection to suspicious IP: 198.51.100.42
- Process: `C:\Users\admin\AppData\Local\Temp\encrypt.exe`

**Step 8: Shadow Copy Deletion**

```
-7d | hostname == "WKS-FINANCE-01" | NEW_PROCESS | event/COMMAND_LINE contains "vssadmin" and event/COMMAND_LINE contains "delete"
```

**Findings:**
- Command: `vssadmin delete shadows /all /quiet`
- Executed by: encrypt.exe

**Step 9: Create Detection Rule**

Based on findings, create D&R rule to detect:
- RDP from external IPs
- Followed by unsigned executable execution
- Followed by shadow copy deletion

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
      value: '10'
    - op: is public address
      path: event/EVENT/EventData/IpAddress
  with descendant:
    event: NEW_PROCESS
    op: and
    rules:
      - op: is
        path: event/SIGNATURE/FILE_IS_SIGNED
        value: 0
      - op: contains
        path: event/FILE_PATH
        value: \Users\
    within: 3600
    with descendant:
      event: NEW_PROCESS
      op: and
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: vssadmin
        - op: contains
          path: event/COMMAND_LINE
          value: delete shadows
      within: 1800
respond:
  - action: report
    name: "Potential Ransomware Attack Chain"
    priority: 5
    metadata:
      mitre: T1486, T1490
      description: External RDP followed by unsigned executable and shadow copy deletion
  - action: task
    command: history_dump
    investigation: ransomware-chain
  - action: isolate network
    investigation: ransomware-chain
```

**Step 10: Proactive Response**

Additional response actions:
1. Isolate affected host
2. Capture memory dump for forensics
3. Get file hash and signature
4. Search for hash across all endpoints
5. Review recent backups

```
# Sensor commands to execute
isolate
mem_dump
file_get C:\Users\admin\AppData\Local\Temp\encrypt.exe
dir_find_hash abc123def456... C:\
```

## Advanced Hunting Techniques

### Baseline and Anomaly Detection

#### 1. Baseline Process Relationships

Over 30 days, map normal parent-child relationships:

```
-30d | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH as parent event/FILE_PATH as child COUNT(event) as occurrences GROUP BY(parent child)
```

Then look for rare combinations (last 24 hours):

```
-24h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH as parent event/FILE_PATH as child COUNT(event) as occurrences GROUP BY(parent child) | occurrences <= 5
```

**Analysis Approach:**
- Export baseline data
- Compare new findings against baseline
- Focus on never-before-seen combinations
- Investigate low-occurrence pairs

#### 2. Baseline Network Connections

Map typical outbound destinations per process (30-day baseline):

```
-30d | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst COUNT(event) as count GROUP BY(process dst)
```

Hunt for new destinations (last 24 hours):

```
-24h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst routing/hostname as host
```

**Analysis Approach:**
- Compare against baseline to find new destinations
- Focus on processes with new IPs
- Validate legitimacy of new connections

#### 3. User Behavior Baselines

Identify unusual logon times:

```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" | event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/LogonType as type routing/event_time as time routing/hostname as host
```

**Analysis Approach:**
- Look for logons outside normal business hours
- Identify unusual user-host combinations
- Focus on administrative accounts
- Check for impossible travel scenarios

### Stack Ranking and Frequency Analysis

#### Least Common Processes

Find rare executables (potential malware):

```
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH as process event/HASH as hash COUNT(event) as count GROUP BY(process hash) ORDER BY(count) | count <= 3
```

**Analysis Approach:**
- Review processes with count ≤ 3
- Check file signatures and reputation
- Investigate unusual file paths
- Validate hashes against threat intelligence

#### Least Common Network Destinations

Find unusual outbound connections:

```
-7d | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst COUNT_UNIQUE(routing/sid) as sensors GROUP BY(dst) ORDER BY(sensors) | sensors <= 2
```

**Analysis Approach:**
- Focus on IPs contacted by 1-2 sensors only
- Check IP reputation and geolocation
- Correlate with process information
- Validate against known infrastructure

#### Processes with Most Network Connections

Identify potential data exfiltration or C2:

```
-24h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH as process COUNT(event) as connections routing/hostname as host GROUP BY(process host) ORDER BY(connections DESC)
```

**Analysis Approach:**
- Review top 10 processes by connection count
- Look for unusual processes with high counts
- Check for beaconing patterns
- Validate against baseline behavior

### Temporal Analysis

#### After-Hours Process Execution

Hunt for activity at unusual times:

```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH as process routing/event_time as time routing/hostname as host
```

**Analysis Approach:**
- Filter results for timestamps outside 8am-6pm local time
- Focus on administrative or sensitive processes
- Correlate with user logon times
- Identify automated tasks vs. manual execution

#### Weekend Activity

Hunt for suspicious weekend activity:

```
-7d | plat == windows | * | routing/event_time as time routing/event_type as type routing/hostname as host
```

**Analysis Approach:**
- Analyze results for Saturday/Sunday timestamps
- Look for administrative activity
- Check for data transfers
- Validate against change management schedules

### Correlation Hunting

Connect multiple data points to build attack chains.

#### Example: Initial Access -> Execution -> Persistence

**Step 1: Look for document execution**

```
-7d | plat == windows | NEW_DOCUMENT | event/FILE_PATH contains "\\Downloads\\" and event/FILE_PATH ends with ".docm"
```

**Step 2: Find processes spawned from Office apps**

```
-7d | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "winword.exe"
```

**Step 3: Check for persistence mechanisms**

```
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\Run"
```

**Step 4: Correlate by hostname and timestamp**

Manual correlation steps:
1. Identify hosts with macro-enabled documents
2. Check for process execution within 5 minutes
3. Look for persistence within 15 minutes
4. Build complete attack timeline

#### Example: Credential Access -> Lateral Movement

**Step 1: LSASS access**

```
-7d | plat == windows | SENSITIVE_PROCESS_ACCESS | routing/hostname as host
```

**Step 2: RDP connections from same host**

```
-7d | hostname == "IDENTIFIED-HOST" | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "10"
```

**Step 3: Process execution on target hosts**

```
-7d | hostname == "TARGET-HOST" | NEW_PROCESS | event/PARENT/FILE_PATH contains "wmiprvse.exe"
```

**Analysis:**
- Timeline credential access to lateral movement
- Identify compromised accounts
- Map lateral movement paths
- Create detection for attack chain

### Memory Analysis

Hunt for in-memory threats using sensor commands.

#### Search Memory for Strings

When you identify a suspicious process:

```
# Hunt query to find suspicious process
-1h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "\\Temp\\" | event/FILE_PATH as path event/PROCESS_ID as pid routing/hostname as host
```

Then use sensor command:
```
mem_strings --pid <pid>
```

**Analysis:**
- Look for URLs, IPs, domains in memory
- Search for encoded PowerShell
- Identify shellcode patterns
- Find configuration data

#### Find Handles to Sensitive Objects

```
# Sensor command
mem_find_handle --pid <pid> lsass
```

**Analysis:**
- Identify processes with handles to LSASS
- Detect credential dumping attempts
- Validate legitimate access patterns

#### Scan Memory with YARA

```
# On suspicious processes
yara_scan hive://yara/malware-rules --pid <pid>
```

**Workflow:**
1. Create or import YARA rules for known malware families
2. Identify suspicious processes via hunting
3. Scan process memory with YARA
4. Analyze hits for malware indicators

### Pivoting Strategies

#### Pivot on File Hash

**Initial Hunt:**
```
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/HASH as hash event/FILE_PATH as path routing/hostname as host
```

**Pivot 1: Find all instances of suspicious hash**
```
-7d | plat == windows | CODE_IDENTITY | event/HASH == "abc123def456..." | routing/hostname as host event/FILE_PATH as path routing/event_time as time
```

**Pivot 2: Find network activity from process**
```
-7d | plat == windows | NETWORK_CONNECTIONS | event/HASH == "abc123def456..." | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst routing/hostname as host
```

**Pivot 3: Check all sensors for file**
```
# Use sensor command across org
dir_find_hash abc123def456... C:\
```

#### Pivot on Domain

**Initial Hunt:**
```
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as sensors GROUP BY(domain) | sensors == 1
```

**Pivot 1: Find all processes resolving domain**
```
-7d | plat == windows | DNS_REQUEST | event/DOMAIN_NAME == "suspicious.example.com" | routing/hostname as host routing/event_time as time
```

**Pivot 2: Network connections to domain**
```
-7d | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS == "198.51.100.42" | event/FILE_PATH as process routing/hostname as host
```

**Pivot 3: Process lineage**
```
# Use sensor command
history_dump
```

#### Pivot on IP Address

**Initial Hunt:**
```
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT not in (80, 443, 53) | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as ip routing/hostname as host
```

**Pivot 1: All connections to suspicious IP**
```
-7d | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS == "198.51.100.42" | event/FILE_PATH as process routing/hostname as host routing/event_time as time
```

**Pivot 2: DNS resolutions for IP**
```
-7d | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain routing/hostname as host
# Manually correlate with IP
```

**Pivot 3: Process information**
```
-7d | plat == windows | CODE_IDENTITY | event/FILE_PATH == "C:\\suspicious\\malware.exe" | event/HASH as hash event/SIGNATURE as sig
```
