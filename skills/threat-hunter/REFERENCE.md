# Threat Hunting Reference

Complete LCQL hunt queries organized by MITRE ATT&CK tactics and techniques.

## Table of Contents

- [Process-Based Hunting](#process-based-hunting)
- [Network-Based Hunting](#network-based-hunting)
- [Persistence Mechanisms](#persistence-mechanisms)
- [Credential Access](#credential-access)
- [Lateral Movement](#lateral-movement)
- [Data Exfiltration](#data-exfiltration)
- [Hunt Templates by MITRE ATT&CK](#hunt-templates-by-mitre-attck)

## Process-Based Hunting

### Suspicious PowerShell Usage

Search for encoded or obfuscated PowerShell commands:

```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" and (event/COMMAND_LINE contains "-enc" or event/COMMAND_LINE contains "-e " or event/COMMAND_LINE contains "bypass") | event/FILE_PATH as path event/COMMAND_LINE as cmd routing/hostname as host
```

### Living Off the Land Binaries (LOLBins)

Hunt for suspicious use of legitimate Windows utilities:

```
-12h | plat == windows | NEW_PROCESS | (event/FILE_PATH ends with "certutil.exe" or event/FILE_PATH ends with "bitsadmin.exe" or event/FILE_PATH ends with "mshta.exe") | event/FILE_PATH as binary event/COMMAND_LINE as cmd routing/hostname as host
```

### Process Injection Indicators

Look for processes creating remote threads:

```
-6h | plat == windows | NEW_REMOTE_THREAD | event/PARENT_PROCESS_ID as injector event/PROCESS_ID as target routing/hostname as host
```

### Unsigned or Suspicious Binaries

Find unsigned executables running from unusual locations:

```
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 and (event/FILE_PATH contains "\\Users\\" or event/FILE_PATH contains "\\Temp\\") | event/FILE_PATH as path event/HASH as hash routing/hostname as host
```

### Parent-Child Process Relationships

Stack unusual parent-child relationships:

```
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "excel.exe" | event/PARENT/FILE_PATH as parent event/FILE_PATH as child COUNT(event) as count GROUP BY(parent child)
```

### Office Applications Spawning Shells

Hunt for macro malware or malicious documents:

```
-12h | plat == windows | NEW_PROCESS | (event/PARENT/FILE_PATH contains "winword.exe" or event/PARENT/FILE_PATH contains "excel.exe" or event/PARENT/FILE_PATH contains "outlook.exe") and (event/FILE_PATH contains "cmd.exe" or event/FILE_PATH contains "powershell.exe" or event/FILE_PATH contains "wscript.exe") | event/PARENT/FILE_PATH as parent event/FILE_PATH as child event/COMMAND_LINE as cmd routing/hostname as host
```

### Services Spawning Unusual Processes

Detect potentially compromised services:

```
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "svchost.exe" and (event/FILE_PATH contains "cmd.exe" or event/FILE_PATH contains "powershell.exe") | event/PARENT/COMMAND_LINE as parent_cmd event/FILE_PATH as child event/COMMAND_LINE as cmd routing/hostname as host
```

### Module Memory/Disk Mismatch

Detect process hollowing or module tampering:

```
-12h | plat == windows | MODULE_MEM_DISK_MISMATCH | event/FILE_PATH as module routing/hostname as host
```

### Least Common Processes

Find rare executables (potential malware):

```
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH as process event/HASH as hash COUNT(event) as count GROUP BY(process hash) ORDER BY(count) | count <= 3
```

## Network-Based Hunting

### Suspicious Domain Resolution

Hunt for domains with characteristics of C2 or DGA:

```
-6h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME not contains "." or event/DOMAIN_NAME contains ".tk" or event/DOMAIN_NAME contains ".cc" | event/DOMAIN_NAME as domain COUNT(event) as count routing/hostname as host GROUP BY(domain host)
```

### Rare Domain Analysis

Find domains only resolved by one or two systems (low prevalence):

```
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as sensor_count GROUP BY(domain) | sensor_count <= 2
```

### External RDP Connections

Look for RDP from non-RFC1918 addresses:

```
-12h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH == "C:\\WINDOWS\\System32\\svchost.exe" and event/COMMAND_LINE contains "TermService" | event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS as src_ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port routing/hostname as host
```

### Beaconing Behavior

Find consistent outbound connections (potential C2):

```
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/FILE_PATH as process COUNT(event) as conn_count GROUP BY(dst_ip process) | conn_count > 50
```

### Non-Standard Ports

Hunt for common protocols on unusual ports:

```
-12h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT not in (80, 443, 8080, 8443) and event/NETWORK_ACTIVITY/DESTINATION/PORT < 1024 | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process routing/hostname as host
```

### Domain Generation Algorithm (DGA) Detection

Hunt for high-entropy or suspicious domain names:

```
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME not contains "." or LENGTH(event/DOMAIN_NAME) > 30 | event/DOMAIN_NAME as domain routing/hostname as host COUNT(event) as count GROUP BY(domain host)
```

### Least Common Network Destinations

Find unusual outbound connections:

```
-7d | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst COUNT_UNIQUE(routing/sid) as sensors GROUP BY(dst) ORDER BY(sensors) | sensors <= 2
```

### Processes with Most Network Connections

Identify potential data exfiltration or C2:

```
-24h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH as process COUNT(event) as connections routing/hostname as host GROUP BY(process host) ORDER BY(connections DESC)
```

### Port Scanning Detection

Look for connections to many unique ports:

```
-6h | plat == windows | NEW_TCP4_CONNECTION | event/SOURCE/IP_ADDRESS as src event/DESTINATION/PORT as port COUNT_UNIQUE(port) as unique_ports GROUP BY(src) | unique_ports > 20
```

## Persistence Mechanisms

### Autorun Analysis

Search for new autorun entries:

```
-7d | plat == windows | AUTORUN_CHANGE | event/REGISTRY_KEY as key routing/hostname as host event/TIMESTAMP as when
```

### Scheduled Tasks

Hunt for suspicious scheduled task creation (via WEL):

```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4698" | event/EVENT/EventData/TaskName as task event/EVENT/EventData/SubjectUserName as user routing/hostname as host
```

### Service Creation

Look for new service installations:

```
-24h | plat == windows | SERVICE_CHANGE | event/SVC_STATE == 1 and event/SVC_TYPE == 16 | event/SVC_NAME as service event/EXECUTABLE as exe routing/hostname as host
```

### Registry Persistence Keys

Monitor common persistence registry locations:

```
-12h | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\CurrentVersion\\Run" or event/REGISTRY_KEY contains "\\Winlogon\\" | event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

### Service Creation via Event Logs

Detect suspicious service creation patterns:

```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "7045" and event/EVENT/EventData/ImagePath not contains "\\windows\\" | event/EVENT/EventData/ServiceName as service event/EVENT/EventData/ImagePath as path routing/hostname as host
```

## Credential Access

### LSASS Access

Detect processes accessing LSASS memory:

```
-12h | plat == windows | SENSITIVE_PROCESS_ACCESS | event/EVENTS/*/event/FILE_PATH contains "lsass.exe" | routing/hostname as host event/EVENTS/*/event/PROCESS_ID as pid
```

### Mimikatz Indicators

Search for common Mimikatz command lines or modules:

```
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "sekurlsa" or event/COMMAND_LINE contains "lsadump" or event/FILE_PATH contains "mimikatz" | event/FILE_PATH as path event/COMMAND_LINE as cmd routing/hostname as host
```

### Overpass-the-Hash Detection

Hunt for logon type 9 with specific auth packages (via WEL):

```
-12h | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "9" and event/EVENT/EventData/AuthenticationPackageName == "Negotiate" | event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as src_ip routing/hostname as host
```

### Brute Force Detection

Hunt for multiple failed logons:

```
-1h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as src_ip COUNT(event) as attempts GROUP BY(user src_ip) | attempts >= 5
```

## Lateral Movement

### PsExec Usage

Search for PsExec execution patterns:

```
-12h | plat == windows | * | event/* contains "psexec" | routing/event_type as type event/* as data routing/hostname as host
```

### WMI-Based Lateral Movement

Hunt for WMI process creation:

```
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "wmiprvse.exe" | event/FILE_PATH as child event/COMMAND_LINE as cmd routing/hostname as host
```

### RDP Session Analysis

Look for successful RDP logons:

```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "10" | event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as src_ip routing/hostname as dst_host
```

### SMB Named Pipe Activity

Monitor for suspicious named pipe operations:

```
-6h | plat == windows | OPEN_NAMED_PIPE | event/FILE_PATH not contains "\\Device\\NamedPipe\\LOCAL\\" | event/FILE_PATH as pipe event/PROCESS_ID as pid routing/hostname as host
```

### Admin Share Usage

Look for connections to admin shares:

```
-12h | plat == windows | WEL | event/EVENT/System/EventID == "5140" and event/EVENT/EventData/ShareName ends with "$" | event/EVENT/EventData/ShareName as share event/EVENT/EventData/IpAddress as src routing/hostname as host
```

## Data Exfiltration

### Large Outbound Transfers

Hunt for unusual data upload volumes:

```
-12h | plat == windows | NETWORK_SUMMARY | event/BYTES_SENT > 10485760 | event/BYTES_SENT as bytes event/DESTINATION/IP_ADDRESS as dst_ip routing/hostname as host
```

### Cloud Storage Domains

Search for uploads to file sharing services:

```
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "dropbox" or event/DOMAIN_NAME contains "mega.nz" or event/DOMAIN_NAME contains "wetransfer" | event/DOMAIN_NAME as domain routing/hostname as host COUNT(event) as requests GROUP BY(domain host)
```

### Archive File Creation

Look for creation of archive files (potential staging):

```
-12h | plat == windows | NEW_DOCUMENT | event/FILE_PATH ends with ".zip" or event/FILE_PATH ends with ".rar" or event/FILE_PATH ends with ".7z" | event/FILE_PATH as archive routing/hostname as host
```

### DNS Tunneling Detection

Look for large DNS queries (potential DNS tunneling):

```
-12h | plat == windows | DNS_REQUEST | LENGTH(event/DOMAIN_NAME) > 50 | event/DOMAIN_NAME as domain routing/hostname as host
```

### Cloud Storage Service Usage

Hunt for exfiltration to cloud storage:

```
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "dropbox" or event/DOMAIN_NAME contains "mega.nz" or event/DOMAIN_NAME contains "wetransfer" or event/DOMAIN_NAME contains "onedrive" | event/DOMAIN_NAME as domain routing/hostname as host
```

### Archiving Tools Usage

Hunt for data staging/compression:

```
-12h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "7z.exe" or event/FILE_PATH contains "winrar.exe" or event/COMMAND_LINE contains "zip" | event/COMMAND_LINE as cmd routing/hostname as host
```

## Hunt Templates by MITRE ATT&CK

### Initial Access (TA0001)

#### T1566.001 - Phishing: Spearphishing Attachment

Look for Office documents spawning processes:

```
-7d | plat == windows | NEW_DOCUMENT | event/FILE_PATH ends with ".docm" or event/FILE_PATH ends with ".xlsm" | event/FILE_PATH as doc routing/hostname as host
```

### Execution (TA0002)

#### T1059.001 - Command and Scripting Interpreter: PowerShell

Hunt for suspicious PowerShell execution:

```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" and (event/COMMAND_LINE contains "bypass" or event/COMMAND_LINE contains "-enc" or event/COMMAND_LINE contains "downloadstring") | event/COMMAND_LINE as cmd routing/hostname as host
```

#### T1053.005 - Scheduled Task/Job: Scheduled Task

Monitor scheduled task creation:

```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4698" | event/EVENT/EventData/TaskName as task routing/hostname as host
```

#### T1047 - Windows Management Instrumentation

Detect WMI process creation:

```
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "wmiprvse.exe" | event/FILE_PATH as child event/COMMAND_LINE as cmd routing/hostname as host
```

### Persistence (TA0003)

#### T1547.001 - Boot or Logon Autostart Execution: Registry Run Keys

Hunt for new autorun entries:

```
-7d | plat == windows | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\Run" or event/REGISTRY_KEY contains "\\RunOnce" | event/REGISTRY_KEY as key event/REGISTRY_VALUE as value routing/hostname as host
```

#### T1543.003 - Create or Modify System Process: Windows Service

Look for new service creation:

```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "7045" | event/EVENT/EventData/ServiceName as service event/EVENT/EventData/ImagePath as path routing/hostname as host
```

#### T1053.005 - Scheduled Task Persistence

Detect scheduled task creation for persistence:

```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4698" | event/EVENT/EventData/TaskName as task event/EVENT/EventData/SubjectUserName as user routing/hostname as host
```

### Privilege Escalation (TA0004)

#### T1055 - Process Injection

Detect remote thread creation:

```
-12h | plat == windows | NEW_REMOTE_THREAD | event/PARENT_PROCESS_ID as injector event/PROCESS_ID as target routing/hostname as host
```

#### T1134 - Access Token Manipulation

Look for SeDebugPrivilege usage:

```
-12h | plat == windows | WEL | event/EVENT/System/EventID == "4703" | event/EVENT/EventData/PrivilegeList as privileges routing/hostname as host
```

#### T1543.003 - Service Creation for Privilege Escalation

Detect suspicious service creation:

```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "7045" and event/EVENT/EventData/ImagePath not contains "\\windows\\" | event/EVENT/EventData/ServiceName as service event/EVENT/EventData/ImagePath as path routing/hostname as host
```

### Defense Evasion (TA0005)

#### T1070.001 - Indicator Removal: Clear Windows Event Logs

Monitor for log clearing:

```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "1102" | routing/hostname as host event/EVENT/EventData/SubjectUserName as user
```

#### T1218 - System Binary Proxy Execution

Hunt for LOLBin abuse:

```
-12h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with "rundll32.exe" and event/COMMAND_LINE contains "javascript" | event/COMMAND_LINE as cmd routing/hostname as host
```

#### T1218.011 - Rundll32

Detect suspicious rundll32 usage:

```
-12h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with "rundll32.exe" and event/COMMAND_LINE contains "javascript" | event/COMMAND_LINE as cmd routing/hostname as host
```

#### T1055 - Process Hollowing Detection

Detect module memory/disk mismatch:

```
-12h | plat == windows | MODULE_MEM_DISK_MISMATCH | event/FILE_PATH as module routing/hostname as host
```

### Credential Access (TA0006)

#### T1003.001 - OS Credential Dumping: LSASS Memory

Detect LSASS access:

```
-12h | plat == windows | SENSITIVE_PROCESS_ACCESS | routing/hostname as host
```

#### T1110 - Brute Force

Hunt for multiple failed logons:

```
-1h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as src_ip COUNT(event) as attempts GROUP BY(user src_ip) | attempts >= 5
```

#### T1558 - Kerberos Ticket Abuse

Look for unusual Kerberos activity:

```
-12h | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "9" and event/EVENT/EventData/AuthenticationPackageName == "Negotiate" | event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as src_ip routing/hostname as host
```

### Discovery (TA0007)

#### T1046 - Network Service Discovery

Look for port scanning activity:

```
-6h | plat == windows | NEW_TCP4_CONNECTION | event/SOURCE/IP_ADDRESS as src event/DESTINATION/PORT as port COUNT_UNIQUE(port) as unique_ports GROUP BY(src) | unique_ports > 20
```

#### T1087 - Account Discovery

Hunt for enumeration commands:

```
-12h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "net user" or event/COMMAND_LINE contains "net group" or event/COMMAND_LINE contains "whoami" | event/COMMAND_LINE as cmd routing/hostname as host
```

#### T1082 - System Information Discovery

Detect system reconnaissance:

```
-12h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "systeminfo" or event/COMMAND_LINE contains "ipconfig" or event/COMMAND_LINE contains "tasklist" | event/COMMAND_LINE as cmd routing/hostname as host
```

### Lateral Movement (TA0008)

#### T1021.001 - Remote Services: Remote Desktop Protocol

Monitor RDP connections:

```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "10" | event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as src routing/hostname as dst
```

#### T1021.002 - Remote Services: SMB/Windows Admin Shares

Look for admin share usage:

```
-12h | plat == windows | WEL | event/EVENT/System/EventID == "5140" and event/EVENT/EventData/ShareName ends with "$" | event/EVENT/EventData/ShareName as share event/EVENT/EventData/IpAddress as src routing/hostname as host
```

#### T1021.006 - Remote Services: Windows Remote Management

Detect WinRM usage:

```
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "wsmprovhost.exe" | event/FILE_PATH as child event/COMMAND_LINE as cmd routing/hostname as host
```

#### T1570 - Lateral Tool Transfer

Hunt for file transfers over network shares:

```
-12h | plat == windows | WEL | event/EVENT/System/EventID == "5145" | event/EVENT/EventData/ShareName as share event/EVENT/EventData/RelativeTargetName as file routing/hostname as host
```

### Collection (TA0009)

#### T1119 - Automated Collection

Hunt for archiving tools:

```
-12h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "7z.exe" or event/FILE_PATH contains "winrar.exe" or event/COMMAND_LINE contains "zip" | event/COMMAND_LINE as cmd routing/hostname as host
```

#### T1113 - Screen Capture

Detect screenshot utilities:

```
-12h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "screenshot" or event/FILE_PATH contains "snip" | event/COMMAND_LINE as cmd routing/hostname as host
```

### Command and Control (TA0011)

#### T1071.001 - Application Layer Protocol: Web Protocols

Look for unusual user agents or HTTP activity:

```
-24h | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH not contains "\\windows\\" and event/NETWORK_ACTIVITY/DESTINATION/PORT in (80, 443, 8080) | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst COUNT(event) as connections GROUP BY(process dst)
```

#### T1572 - Protocol Tunneling

Hunt for unusual protocols or ports:

```
-12h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT not in (80, 443, 53, 445, 139, 3389) | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process routing/hostname as host
```

#### T1095 - Non-Application Layer Protocol

Detect unusual network protocols:

```
-12h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT not in (80, 443, 53, 445, 139, 3389) | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process routing/hostname as host
```

#### T1573 - Encrypted Channel

Hunt for encrypted C2 communications:

```
-24h | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT in (443, 8443) and event/FILE_PATH not contains "\\windows\\" | event/FILE_PATH as process event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst COUNT(event) as connections GROUP BY(process dst)
```

### Exfiltration (TA0010)

#### T1048.003 - Exfiltration Over Alternative Protocol

Look for large DNS queries (DNS tunneling):

```
-12h | plat == windows | DNS_REQUEST | LENGTH(event/DOMAIN_NAME) > 50 | event/DOMAIN_NAME as domain routing/hostname as host
```

#### T1567.002 - Exfiltration Over Web Service: Cloud Storage

Hunt for cloud storage usage:

```
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "dropbox" or event/DOMAIN_NAME contains "mega.nz" or event/DOMAIN_NAME contains "wetransfer" or event/DOMAIN_NAME contains "onedrive" | event/DOMAIN_NAME as domain routing/hostname as host
```

#### T1041 - Exfiltration Over C2 Channel

Detect large outbound transfers:

```
-12h | plat == windows | NETWORK_SUMMARY | event/BYTES_SENT > 10485760 | event/BYTES_SENT as bytes event/DESTINATION/IP_ADDRESS as dst_ip routing/hostname as host
```

### Impact (TA0040)

#### T1486 - Data Encrypted for Impact

Hunt for ransomware indicators:

```
-12h | plat == windows | FILE_MODIFIED | event/FILE_PATH as path routing/event_time as time
# Check for volume of file modifications
```

#### T1490 - Inhibit System Recovery

Detect shadow copy deletion:

```
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "vssadmin" and event/COMMAND_LINE contains "delete" | event/COMMAND_LINE as cmd routing/hostname as host
```
