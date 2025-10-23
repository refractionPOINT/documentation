# YARA Rule Examples

Complete examples of YARA rules with D&R integration for LimaCharlie.

**See also:**
- [SKILL.md](./SKILL.md): Overview and quick start
- [REFERENCE.md](./REFERENCE.md): Complete syntax reference
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md): Performance and debugging

---

## Table of Contents

1. [Basic Malware Detection](#example-1-basic-malware-detection)
2. [Ransomware Detection](#example-2-ransomware-detection)
3. [Webshell Detection](#example-3-webshell-detection)
4. [Credential Stealer Detection](#example-4-credential-stealer-detection)
5. [External Rule Source](#example-5-external-rule-source-community-rules)
6. [Multi-Rule APT Detection](#example-6-comprehensive-multi-rule-apt-detection)
7. [Process Scanning Workflows](#example-7-process-scanning-workflows)
8. [File Scanning Workflows](#example-8-file-scanning-workflows)

---

## Example 1: Basic Malware Detection

### YARA Rule

```yara
rule Basic_Malware_Detection
{
    meta:
        description = "Detects basic malware patterns"
        author = "Security Team"
        date = "2025-01-15"
        severity = "high"

    strings:
        $mz = "MZ"
        $str1 = "malicious_function" nocase
        $str2 = "backdoor_connect" nocase
        $hex1 = { 6A 40 68 00 30 00 00 }

    condition:
        $mz at 0 and
        filesize < 5MB and
        2 of ($str*, $hex*)
}
```

### Store in Config Hive

**Via CLI:**
```bash
limacharlie hive set yara --key basic-malware --data basic-malware.yar --data-key rule
```

**Via Web UI:**
1. Navigate to **Automation → YARA Rules**
2. Click **Add New Rule**
3. Enter key: `basic-malware`
4. Paste YARA rule content
5. Click **Save**

### D&R Rule: Trigger Scan

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: \Temp\
      case sensitive: false

respond:
  - action: task
    command: yara_scan hive://yara/basic-malware --pid "{{ .event.PROCESS_ID }}"
    investigation: Basic Malware Scan
    suppression:
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 2m
```

### D&R Rule: Detect and Respond

```yaml
detect:
  event: YARA_DETECTION
  op: is
  path: event/RULE_NAME
  value: Basic_Malware_Detection

respond:
  - action: report
    name: "Basic Malware Detected - {{ .event.FILE_PATH }}"
    priority: 4
    metadata:
      file_path: "{{ .event.FILE_PATH }}"
      file_hash: "{{ .event.HASH }}"
      rule_name: "{{ .event.RULE_NAME }}"
  - action: task
    command: deny_tree <<routing/this>>
  - action: isolate network
  - action: add tag
    tag: malware-detected
    ttl: 86400
```

---

## Example 2: Ransomware Detection

### YARA Rule

```yara
rule Ransomware_Detection
{
    meta:
        description = "Detects common ransomware patterns"
        author = "Security Team"
        date = "2025-01-15"
        mitre_attack = "T1486"
        severity = "critical"

    strings:
        // Ransomware note strings
        $note1 = "your files have been encrypted" nocase
        $note2 = "bitcoin address" nocase
        $note3 = "decrypt_instructions" nocase
        $note4 = "pay ransom" nocase

        // Encryption-related strings
        $crypt1 = "AES256" nocase
        $crypt2 = "RSA2048" nocase
        $crypt3 = "CryptEncrypt"

        // File extension strings
        $ext1 = ".locked" nocase
        $ext2 = ".encrypted" nocase
        $ext3 = ".crypt" nocase
        $ext4 = ".wncry" nocase

    condition:
        filesize < 10MB and
        (
            (2 of ($note*)) or
            (1 of ($note*) and 1 of ($crypt*)) or
            (2 of ($ext*) and 1 of ($crypt*))
        )
}
```

### Store in Config Hive

```bash
limacharlie hive set yara --key ransomware --data ransomware.yar --data-key rule
```

### D&R Rule: Scan New Documents

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: matches
      path: event/FILE_PATH
      re: .*\.(txt|html|readme)$
      case sensitive: false
    - op: is lower than
      path: event/FILE_SIZE
      value: 102400  # 100 KB

respond:
  - action: task
    command: yara_scan hive://yara/ransomware -f "{{ .event.FILE_PATH }}"
    investigation: Ransomware Note Scan
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 10m
```

### D&R Rule: Detect and Respond

```yaml
detect:
  event: YARA_DETECTION
  op: is
  path: event/RULE_NAME
  value: Ransomware_Detection

respond:
  - action: report
    name: "RANSOMWARE DETECTED - {{ .routing.hostname }}"
    priority: 5
    metadata:
      severity: critical
      response_required: immediate
      file_path: "{{ .event.FILE_PATH }}"
      file_hash: "{{ .event.HASH }}"
      hostname: "{{ .routing.hostname }}"
  - action: isolate network
  - action: task
    command: history_dump
    investigation: ransomware-incident
  - action: task
    command: deny_tree <<routing/this>>
  - action: add tag
    tag: ransomware-detected
    ttl: 604800  # 7 days
```

---

## Example 3: Webshell Detection

### YARA Rule

```yara
rule Webshell_Detection
{
    meta:
        description = "Detects common webshell patterns"
        author = "Security Team"
        date = "2025-01-15"
        mitre_attack = "T1505.003"
        severity = "high"

    strings:
        // PHP webshell patterns
        $php1 = "<?php eval(" nocase
        $php2 = "<?php system(" nocase
        $php3 = "<?php exec(" nocase
        $php4 = "<?php passthru(" nocase
        $php5 = "<?php shell_exec(" nocase
        $php6 = "base64_decode" nocase

        // ASP webshell patterns
        $asp1 = "eval request" nocase
        $asp2 = "execute request" nocase
        $asp3 = "wscript.shell" nocase
        $asp4 = "Server.CreateObject" nocase

        // JSP webshell patterns
        $jsp1 = "Runtime.getRuntime().exec" nocase
        $jsp2 = "ProcessBuilder" nocase

        // Common webshell strings
        $web1 = "c99shell" nocase
        $web2 = "r57shell" nocase
        $web3 = "WSO" fullword
        $web4 = "b374k" nocase
        $web5 = "phpspy" nocase

    condition:
        filesize < 1MB and
        (
            (2 of ($php*)) or
            (1 of ($php*) and $php6) or
            (2 of ($asp*)) or
            (1 of ($jsp*)) or
            (any of ($web*))
        )
}
```

### Store in Config Hive

```bash
limacharlie hive set yara --key webshell --data webshell.yar --data-key rule
```

### D&R Rule: Linux Web Servers

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: is platform
      name: linux
    - op: contains
      path: event/FILE_PATH
      value: /var/www/
    - op: matches
      path: event/FILE_PATH
      re: .*\.(php|asp|aspx|jsp)$
      case sensitive: false

respond:
  - action: report
    name: Web file created in /var/www/
  - action: task
    command: yara_scan hive://yara/webshell -f "{{ .event.FILE_PATH }}"
    investigation: Webshell Scan
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 5m
```

### D&R Rule: Windows IIS Servers

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: is platform
      name: windows
    - op: matches
      path: event/FILE_PATH
      re: .*\\inetpub\\wwwroot\\.*
      case sensitive: false
    - op: matches
      path: event/FILE_PATH
      re: .*\.(asp|aspx|ashx)$
      case sensitive: false

respond:
  - action: report
    name: Web file created in IIS directory
  - action: task
    command: yara_scan hive://yara/webshell -f "{{ .event.FILE_PATH }}"
    investigation: Webshell Scan IIS
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 5m
```

### D&R Rule: Detect and Respond

```yaml
detect:
  event: YARA_DETECTION
  op: is
  path: event/RULE_NAME
  value: Webshell_Detection

respond:
  - action: report
    name: "Webshell Detected - {{ .event.FILE_PATH }}"
    priority: 5
    metadata:
      severity: critical
      file_path: "{{ .event.FILE_PATH }}"
      file_hash: "{{ .event.HASH }}"
  - action: task
    command: history_dump
    investigation: webshell-detection
  - action: add tag
    tag: webshell-detected
    ttl: 86400
```

---

## Example 4: Credential Stealer Detection

### YARA Rule

```yara
rule Credential_Stealer
{
    meta:
        description = "Detects credential stealing malware"
        author = "Security Team"
        date = "2025-01-15"
        mitre_attack = "T1555, T1552"
        severity = "high"

    strings:
        // Browser credential paths
        $path1 = "\\Google\\Chrome\\User Data" nocase
        $path2 = "\\Mozilla\\Firefox\\Profiles" nocase
        $path3 = "Login Data" nocase
        $path4 = "key4.db" nocase
        $path5 = "logins.json" nocase

        // Windows credential references
        $win1 = "SAM" fullword
        $win2 = "lsass.exe" nocase
        $win3 = "Credential Manager" nocase
        $win4 = "SECURITY" fullword

        // Common credential stealer functions
        $func1 = "ReadProcessMemory"
        $func2 = "CryptUnprotectData"
        $func3 = "sqlite3_open"
        $func4 = "RegOpenKeyEx"

        // Network exfiltration
        $net1 = "Content-Type: application/json"
        $net2 = "Authorization: Bearer"
        $net3 = "POST" fullword

    condition:
        uint16(0) == 0x5A4D and
        filesize < 3MB and
        (
            (2 of ($path*) and 1 of ($func*)) or
            (2 of ($win*) and 1 of ($func*)) or
            (1 of ($path*) and 1 of ($win*) and 1 of ($net*))
        )
}
```

### Store in Config Hive

```bash
limacharlie hive set yara --key credential-stealer --data credential-stealer.yar --data-key rule
```

### D&R Rule: Scan Suspicious Processes

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: or
      rules:
        - op: contains
          path: event/FILE_PATH
          value: \Downloads\
        - op: contains
          path: event/FILE_PATH
          value: \AppData\Local\Temp\

respond:
  - action: task
    command: yara_scan hive://yara/credential-stealer --pid "{{ .event.PROCESS_ID }}"
    investigation: Credential Stealer Scan
    suppression:
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
```

### D&R Rule: Detect and Respond

```yaml
detect:
  event: YARA_DETECTION
  op: is
  path: event/RULE_NAME
  value: Credential_Stealer

respond:
  - action: report
    name: "Credential Stealer Detected - {{ .event.FILE_PATH }}"
    priority: 5
    detect_data:
      file_path: "{{ .event.FILE_PATH }}"
      file_hash: "{{ .event.HASH }}"
      hostname: "{{ .routing.hostname }}"
  - action: task
    command: history_dump
    investigation: credential-theft
  - action: task
    command: deny_tree <<routing/this>>
  - action: isolate network
  - action: add tag
    tag: credential-stealer-detected
    ttl: 86400
```

---

## Example 5: External Rule Source (Community Rules)

### Using YARA Manager for Community Rules

**Step 1: Configure YARA Manager**

1. Navigate to **Add-ons → Extensions → YARA Manager**
2. Click **Add New Yara Configuration**
3. Enter name: `Community Malware Rules`
4. Enter ARL: `[github,Yara-Rules/rules/malware]`
5. Click **Save**
6. Click **Manual Sync**

**Step 2: Wait for sync**

Rules will appear in **Automation → YARA Rules** after sync completes.

### D&R Rule: Use Community Rules

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: is platform
      name: windows
    - op: matches
      path: event/FILE_PATH
      re: .*\.(exe|dll|sys)$
      case sensitive: false
    - op: is lower than
      path: event/FILE_SIZE
      value: 10485760  # 10 MB

respond:
  - action: task
    command: yara_scan hive://yara/community-malware-rules -f "{{ .event.FILE_PATH }}"
    investigation: Community Rule Scan
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 5m
```

### D&R Rule: Detect Any Community Rule Match

```yaml
detect:
  event: YARA_DETECTION
  op: exists
  path: event/RULE_NAME

respond:
  - action: report
    name: "Community Rule Match - {{ .event.RULE_NAME }}"
    priority: 3
    metadata:
      rule: "{{ .event.RULE_NAME }}"
      file_path: "{{ .event.FILE_PATH }}"
      file_hash: "{{ .event.HASH }}"
  - action: add tag
    tag: yara-community-match
    ttl: 86400
```

---

## Example 6: Comprehensive Multi-Rule APT Detection

### YARA Rules File (Multiple Rules)

```yara
rule APT_Backdoor_Network
{
    meta:
        description = "Detects APT backdoor network behavior"
        author = "Security Team"
        date = "2025-01-15"
        mitre_attack = "T1071.001"

    strings:
        $ua1 = "Mozilla/5.0 (Windows NT 6.1; WOW64)" nocase
        $ua2 = "Mozilla/4.0 (compatible; MSIE 8.0;" nocase
        $header1 = "User-Agent:" nocase
        $header2 = "Accept-Language:" nocase
        $domain = /https?:\/\/[a-z0-9]{8,12}\.(com|net|org)/

    condition:
        3 of them
}

rule APT_Backdoor_Persistence
{
    meta:
        description = "Detects APT backdoor persistence mechanisms"
        author = "Security Team"
        date = "2025-01-15"
        mitre_attack = "T1547.001"

    strings:
        $reg1 = "Software\\Microsoft\\Windows\\CurrentVersion\\Run" nocase
        $reg2 = "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" nocase
        $reg3 = "HKEY_LOCAL_MACHINE" nocase
        $svc1 = "CreateService" nocase
        $svc2 = "StartService" nocase
        $task1 = "SchTasks" nocase

    condition:
        uint16(0) == 0x5A4D and
        (
            (1 of ($reg*) and $reg3) or
            (1 of ($svc*)) or
            ($task1)
        )
}

rule APT_Backdoor_CommandControl
{
    meta:
        description = "Detects APT backdoor command and control"
        author = "Security Team"
        date = "2025-01-15"
        mitre_attack = "T1059"

    strings:
        $cmd1 = "cmd.exe /c" nocase
        $cmd2 = "powershell.exe -" nocase
        $cmd3 = "wscript" nocase
        $cmd4 = "cscript" nocase
        $enc1 = "base64" nocase
        $enc2 = "-enc" nocase

    condition:
        2 of ($cmd*) and 1 of ($enc*)
}

rule APT_Backdoor_Combined
{
    meta:
        description = "Combined APT backdoor detection"
        author = "Security Team"
        date = "2025-01-15"
        severity = "critical"

    condition:
        APT_Backdoor_Network or APT_Backdoor_Persistence or APT_Backdoor_CommandControl
}
```

### Store in Config Hive

```bash
limacharlie hive set yara --key apt-backdoor --data apt-backdoor.yar --data-key rule
```

### D&R Rule: Scan Service Processes

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: is
      path: event/PARENT/FILE_PATH
      value: C:\Windows\System32\services.exe

respond:
  - action: report
    name: Service Process Started
  - action: task
    command: yara_scan hive://yara/apt-backdoor --pid "{{ .event.PROCESS_ID }}"
    investigation: APT Backdoor Scan
    suppression:
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
```

### D&R Rule: Detect Any APT Rule

```yaml
detect:
  event: YARA_DETECTION
  op: starts with
  path: event/RULE_NAME
  value: APT_Backdoor

respond:
  - action: report
    name: "APT Backdoor Activity - {{ .event.RULE_NAME }}"
    priority: 5
    metadata:
      threat_type: APT
      rule_matched: "{{ .event.RULE_NAME }}"
      file_path: "{{ .event.FILE_PATH }}"
      file_hash: "{{ .event.HASH }}"
  - action: task
    command: history_dump
    investigation: apt-detection
  - action: task
    command: netstat
    investigation: apt-detection
  - action: isolate network
  - action: add tag
    tag: apt-detected
    ttl: 604800  # 7 days
```

---

## Example 7: Process Scanning Workflows

### Workflow 1: Scan Processes from Downloads Directory

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: starts with
      path: event/FILE_PATH
      value: C:\Users\
    - op: contains
      path: event/FILE_PATH
      value: \Downloads\

respond:
  - action: report
    name: Execution from Downloads directory
  - action: task
    command: yara_scan hive://yara/malware-rule --pid "{{ .event.PROCESS_ID }}"
    investigation: Yara Scan Process Downloads
    suppression:
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
        - Yara Scan Process Downloads
      max_count: 1
      period: 1m
```

### Workflow 2: Scan Unsigned Processes

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - not: true
      op: exists
      path: event/SIGNATURE/CERT_CHAIN/*/CERT_ISSUER

respond:
  - action: report
    name: Unsigned executable started
  - action: task
    command: yara_scan hive://yara/malware-rule --pid "{{ .event.PROCESS_ID }}"
    investigation: Yara Scan Unsigned Process
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
        - Yara Scan Unsigned Process
      max_count: 1
      period: 5m
```

### Workflow 3: Scan Processes with Network Activity

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is
      path: event/STATE
      value: ESTABLISHED
    - not: true
      op: exists
      path: event/SIGNATURE/CERT_CHAIN/*/CERT_ISSUER

respond:
  - action: report
    name: Unsigned process with network connection
  - action: task
    command: yara_scan hive://yara/malware-rule --pid "{{ .event.PROCESS_ID }}"
    investigation: Yara Scan Network Process
    suppression:
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 10m
```

---

## Example 8: File Scanning Workflows

### Workflow 1: Scan New Executables in Temp Directories

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - case sensitive: false
      op: matches
      path: event/FILE_PATH
      re: .*\\(temp|tmp)\\.*
    - case sensitive: false
      op: matches
      path: event/FILE_PATH
      re: .*\.(exe|dll)$
    - op: is lower than
      path: event/FILE_SIZE
      value: 10485760  # 10 MB

respond:
  - action: report
    name: Executable written to Temp directory
  - action: task
    command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
    investigation: Yara Scan Temp Executable
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 5m
```

### Workflow 2: Scan Files Written by Office Applications

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: is platform
      name: windows
    - op: or
      rules:
        - op: ends with
          path: event/PARENT/FILE_PATH
          value: WINWORD.EXE
          case sensitive: false
        - op: ends with
          path: event/PARENT/FILE_PATH
          value: EXCEL.EXE
          case sensitive: false
        - op: ends with
          path: event/PARENT/FILE_PATH
          value: POWERPNT.EXE
          case sensitive: false
    - op: matches
      path: event/FILE_PATH
      re: .*\.(exe|dll|vbs|js|hta)$
      case sensitive: false

respond:
  - action: report
    name: Suspicious file created by Office application
    priority: 4
  - action: task
    command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
    investigation: Yara Scan Office Spawned File
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 5m
```

### Workflow 3: Scan Archive Contents

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: matches
      path: event/FILE_PATH
      re: .*\.(exe|dll|scr)$
      case sensitive: false
    - op: contains
      path: event/FILE_PATH
      value: .zip_
      case sensitive: false

respond:
  - action: report
    name: Executable extracted from archive
  - action: task
    command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
    investigation: Yara Scan Archive Contents
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 5m
```

### Workflow 4: Scan Macro-Enabled Office Documents

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: matches
      path: event/FILE_PATH
      re: .*\.(docm|xlsm|pptm)$
      case sensitive: false
    - op: is lower than
      path: event/FILE_SIZE
      value: 5242880  # 5 MB

respond:
  - action: report
    name: Macro-enabled Office document created
  - action: task
    command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
    investigation: Yara Scan Macro Document
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 10m
```

---

## Complete Detection Pipeline Example

This example shows a complete detection pipeline from scan trigger to incident response.

### Step 1: Store YARA Rule

```bash
limacharlie hive set yara --key production-malware --data malware.yar --data-key rule
```

### Step 2: D&R Rule - Trigger Scan

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: is platform
      name: windows
    - op: matches
      path: event/FILE_PATH
      re: .*\.(exe|dll|sys)$
      case sensitive: false
    - op: or
      rules:
        - op: contains
          path: event/FILE_PATH
          value: \Downloads\
        - op: contains
          path: event/FILE_PATH
          value: \Temp\
    - op: is lower than
      path: event/FILE_SIZE
      value: 10485760  # 10 MB

respond:
  - action: report
    name: Suspicious executable written to disk
    priority: 2
  - action: task
    command: yara_scan hive://yara/production-malware -f "{{ .event.FILE_PATH }}"
    investigation: Production Malware Scan
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
      max_count: 1
      period: 5m
```

### Step 3: D&R Rule - Detect and Alert

```yaml
detect:
  event: YARA_DETECTION
  op: exists
  path: event/RULE_NAME

respond:
  - action: report
    name: "MALWARE DETECTED - {{ .event.RULE_NAME }}"
    priority: 5
    metadata:
      rule_name: "{{ .event.RULE_NAME }}"
      file_path: "{{ .event.FILE_PATH }}"
      file_hash: "{{ .event.HASH }}"
      hostname: "{{ .routing.hostname }}"
      sensor_id: "{{ .routing.sid }}"
  - action: add tag
    tag: malware-detected
    ttl: 604800
```

### Step 4: D&R Rule - Containment

```yaml
detect:
  event: YARA_DETECTION
  op: and
  rules:
    - op: exists
      path: event/RULE_NAME
    - op: exists
      path: event/PROCESS/*

respond:
  - action: report
    name: "Malware running in memory - initiating containment"
    priority: 5
  - action: task
    command: deny_tree <<routing/this>>
  - action: task
    command: history_dump
    investigation: malware-containment
  - action: isolate network
```

### Step 5: D&R Rule - Collection

```yaml
detect:
  event: YARA_DETECTION
  op: exists
  path: event/FILE_PATH

respond:
  - action: report
    name: "Collecting forensic artifacts"
  - action: task
    command: mem_map --pid "{{ .event.PROCESS/PROCESS_ID }}"
    investigation: malware-forensics
  - action: task
    command: os_processes
    investigation: malware-forensics
  - action: task
    command: netstat
    investigation: malware-forensics
```

---

For syntax details, see [REFERENCE.md](./REFERENCE.md). For troubleshooting, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).
