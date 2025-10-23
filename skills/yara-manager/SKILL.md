---
name: yara-manager
description: Use this skill when users need help creating, testing, deploying, or managing YARA rules for malware detection in LimaCharlie.
---

# LimaCharlie YARA Manager

This skill provides comprehensive guidance for creating, testing, and deploying YARA rules for malware detection in LimaCharlie. Use this skill when users need help with YARA rule syntax, storage, scanning methods, performance optimization, or integration with Detection & Response rules.

## Table of Contents

1. [YARA Overview](#yara-overview)
2. [YARA Rule Syntax](#yara-rule-syntax)
3. [Rule Storage in Config Hive](#rule-storage-in-config-hive)
4. [Scanning Methods](#scanning-methods)
5. [YARA Manager Extension](#yara-manager-extension)
6. [YARA Extension](#yara-extension)
7. [D&R Integration](#dr-integration)
8. [Performance and Suppression](#performance-and-suppression)
9. [Best Practices](#best-practices)
10. [Complete Examples](#complete-examples)

---

## YARA Overview

### What is YARA?

YARA is a powerful pattern-matching tool designed to help malware researchers identify and classify malware samples. It allows you to create descriptions of malware families (or any files you want to detect) based on textual or binary patterns.

**In LimaCharlie, YARA enables:**
- File-based malware detection (on-disk scanning)
- Memory-based malware detection (in-memory/process scanning)
- Automated scanning triggered by D&R rules
- Manual on-demand scans
- Continuous background scanning across your fleet

### How YARA Works in LimaCharlie

YARA rules can be:
1. **Stored** in the Config Hive (`hive://yara/`)
2. **Referenced** from external sources (GitHub, URLs)
3. **Scanned** manually or automatically via D&R rules
4. **Detected** and reported as `YARA_DETECTION` events

---

## YARA Rule Syntax

### Basic Rule Structure

Every YARA rule follows this structure:

```yara
rule RuleName
{
    meta:
        description = "Description of what this rule detects"
        author = "Your Name"
        date = "2025-01-15"

    strings:
        $string1 = "malicious_string"
        $string2 = { 6A 40 68 00 30 00 00 }
        $regex1 = /md5: [0-9a-fA-F]{32}/

    condition:
        all of them
}
```

### Rule Components

#### 1. Rule Declaration

```yara
rule RuleName
{
    // Rule body
}
```

- Rule identifiers must start with a letter
- Can contain letters, numbers, and underscores
- Cannot exceed 128 characters
- Case-sensitive

**Multiple rules in one file:**

```yara
rule FirstRule
{
    // First rule body
}

rule SecondRule
{
    // Second rule body
}
```

#### 2. Metadata Section (Optional)

Metadata provides context about the rule but doesn't affect matching logic.

```yara
meta:
    description = "Detects Emotet malware"
    author = "Security Team"
    date = "2025-01-15"
    version = "1.0"
    reference = "https://example.com/threat-intel"
    hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    severity = "high"
    mitre_attack = "T1059.001"
```

**Supported metadata types:**
- Strings: `description = "text"`
- Integers: `version = 1`
- Booleans: `in_the_wild = true`

#### 3. Strings Section

The strings section defines patterns to search for.

**Text Strings:**

```yara
strings:
    $text1 = "malicious"
    $text2 = "suspicious" nocase
    $text3 = "wide string" wide
    $text4 = "full word match" fullword
    $text5 = "case insensitive full word" nocase fullword
```

**String modifiers:**
- `nocase`: Case-insensitive matching
- `wide`: Match wide-character (UTF-16) strings
- `ascii`: Match ASCII strings (default)
- `fullword`: Match only if string is not preceded/followed by alphanumeric characters
- `xor`: Match strings encrypted with single-byte XOR

**Hexadecimal Strings:**

```yara
strings:
    $hex1 = { 6A 40 68 00 30 00 00 }
    $hex2 = { 4D 5A 90 00 }  // PE header
    $hex3 = { E? 00 00 00 00 }  // ? = wildcard for single nibble
    $hex4 = { F4 23 [4-6] 62 B4 }  // [4-6] = 4 to 6 variable bytes
    $hex5 = { F4 23 [10-] 62 B4 }  // [10-] = 10 or more bytes
    $hex6 = { F4 23 [-] 62 B4 }  // [-] = unlimited bytes
```

**Regular Expressions:**

```yara
strings:
    $re1 = /md5: [0-9a-fA-F]{32}/
    $re2 = /https?:\/\/[a-z0-9.-]+/i  // i = case insensitive
    $re3 = /admin|root|superuser/
```

**Regular expression modifiers:**
- `i`: Case-insensitive
- `s`: Dot (.) matches newline characters

#### 4. Condition Section (Required)

The condition defines the logic that determines if the rule matches.

**Basic conditions:**

```yara
condition:
    $text1                    // String $text1 appears
    $text1 and $text2        // Both strings appear
    $text1 or $text2         // Either string appears
    not $text1               // String does not appear
    all of them              // All defined strings appear
    any of them              // At least one string appears
    2 of them                // At least 2 strings appear
    any of ($text*)          // Any string starting with $text
```

**Counting conditions:**

```yara
condition:
    #text1 > 5               // String appears more than 5 times
    #text1 == 3              // String appears exactly 3 times
    #text* > 10              // Strings matching $text* appear more than 10 times total
```

**File size conditions:**

```yara
condition:
    filesize < 1MB
    filesize > 500KB and filesize < 2MB
```

**Position-based conditions:**

```yara
condition:
    $text1 at 0              // String at file offset 0
    $text1 in (0..1024)      // String in first 1024 bytes
    @text1 < 100             // First occurrence at offset < 100
```

**Complex conditions:**

```yara
condition:
    (uint16(0) == 0x5A4D) and              // PE header check
    filesize < 2MB and
    (2 of ($text*)) and
    (any of ($hex*))
```

### Special Functions and Variables

**File size:**
```yara
condition:
    filesize > 1MB
    filesize < 100KB
```

**Magic bytes:**
```yara
condition:
    uint16(0) == 0x5A4D      // MZ header (PE file)
    uint32(0) == 0x464C457F   // ELF header
```

**Entry point:**
```yara
condition:
    $code at entrypoint
```

---

## Rule Storage in Config Hive

### Config Hive Format

YARA rules are stored in LimaCharlie's Config Hive under the `yara` namespace.

**Format:**
```json
{
    "rule": "YARA_RULE_CONTENT_HERE"
}
```

The `rule` field contains the complete YARA rule(s) as a string.

### Creating Rules via CLI

**Store a rule from a file:**

```bash
limacharlie hive set yara --key my-rule --data rule.yara --data-key rule
```

**Response:**
```json
{
  "guid": "d88826b7-d583-4bcc-b7d3-4f450a12e1be",
  "hive": {
    "name": "yara",
    "partition": "8cbe27f4-aaaa-bbbb-cccc-138cd51389cd"
  },
  "name": "my-rule"
}
```

### Creating Rules via Web UI

1. Navigate to **Automation → YARA Rules**
2. Click **Add New Rule**
3. Enter rule name
4. Paste YARA rule content
5. Click **Save**

### Referencing Stored Rules

Reference rules using the `hive://` protocol:

```
hive://yara/my-rule
hive://yara/malware-detection
hive://yara/ransomware-rules
```

### Multiple Rules in One Record

A single Config Hive record can contain multiple YARA rules:

```yara
rule MalwareFamily1
{
    strings:
        $s1 = "malicious1"
    condition:
        $s1
}

rule MalwareFamily2
{
    strings:
        $s2 = "malicious2"
    condition:
        $s2
}
```

This is useful for organizing related rules together.

### Permissions

The `yara` hive requires these permissions:

- `yara.get`: View YARA rules
- `yara.set`: Create/update YARA rules
- `yara.del`: Delete YARA rules
- `yara.get.mtd`: View YARA rule metadata
- `yara.set.mtd`: Set YARA rule metadata

---

## Scanning Methods

LimaCharlie provides multiple methods for YARA scanning:

### 1. Manual Sensor Command

Trigger scans directly using the `yara_scan` command.

**Scan a file:**
```
yara_scan hive://yara/my-rule -f "C:\Users\user\Downloads\suspicious.exe"
```

**Scan a process (in memory):**
```
yara_scan hive://yara/my-rule --pid 1234
```

**Scan a directory:**
```
yara_scan hive://yara/my-rule --path "C:\Users\user\Downloads"
```

### 2. Via Sensor Console

1. Navigate to sensor detail page
2. Click **Console** tab
3. Execute `yara_scan` command

### 3. Via D&R Rules

Automatically trigger YARA scans in response to events (see [D&R Integration](#dr-integration)).

### 4. Via YARA Extension

The YARA Extension (ext-yara) provides automated continuous scanning.

### 5. Via API

```python
import limacharlie

lc = limacharlie.Manager()
sensor = lc.sensor('SENSOR_ID')
sensor.task('yara_scan hive://yara/my-rule -f "C:\\malware.exe"')
```

### Where Does YARA Scan?

**Automated YARA Extension scans:**
- All files loaded in memory (exe, dll, etc.)
- Process memory itself

**Manual scans (via command):**
- Specific files on disk
- Specific directories on disk
- Specific process memory (by PID)

---

## YARA Manager Extension

The YARA Manager Extension (`ext-yara-manager`) allows you to reference external YARA rule sources.

### Purpose

Instead of manually copying YARA rules into the Config Hive, the YARA Manager automatically syncs rules from external sources:
- GitHub repositories (public or private)
- Direct URLs to YARA files
- Predefined community rulesets

### Configuration

Access via **Add-ons → Extensions → YARA Manager**

### Option 1: Predefined YARA Rules

LimaCharlie provides curated YARA rule repositories.

**Steps:**
1. Go to YARA Manager extension
2. Click **Add New Yara Configuration**
3. Select **Predefined**
4. Choose from available repositories
5. Click **Save**

Rules automatically sync and appear in **Automation → YARA Rules**.

### Option 2: Public YARA Rules

Reference publicly available YARA rules from GitHub or URLs.

**Example - Single file URL:**
```
https://raw.githubusercontent.com/Yara-Rules/rules/master/email/Email_generic_phishing.yar
```

**Example - Directory via ARL:**
```
[github,Yara-Rules/rules/email]
```

This syncs all YARA rules from the `email` directory in the repository.

**Steps:**
1. Click **Add New Yara Configuration**
2. Enter configuration name
3. Enter URL or ARL
4. Click **Save**

### Option 3: Private GitHub Repository

Use an Authentication Resource Locator (ARL) with a GitHub token.

**Step 1: Create GitHub Token**
1. In GitHub: Settings → Developer settings → Personal access tokens
2. Click **Generate new token**
3. Select **repo** permissions
4. Generate token and copy it

**Step 2: Configure in LimaCharlie**

**Format for single file:**
```
[github,my-org/my-repo-name/path/to/rule.yar,token,YOUR_GITHUB_TOKEN]
```

**Format for directory:**
```
[github,my-org/my-repo-name/path/to/rules_directory,token,YOUR_GITHUB_TOKEN]
```

**Steps:**
1. Click **Add New Yara Configuration**
2. Enter configuration name
3. Enter ARL with token
4. Click **Save**

### Syncing Rules

**Automatic sync:** Rules sync every 24 hours

**Manual sync:** Click **Manual Sync** button on extension page

**Note:** After adding new rule sources, click **Manual Sync** to make them available immediately.

---

## YARA Extension

The YARA Extension (`ext-yara`) provides automated and on-demand scanning capabilities.

### Three Main Sections

1. **Sources**: Define where YARA rules come from (use YARA Manager instead)
2. **Rules**: Define YARA rules directly or reference sources
3. **Scanners**: Configure which sensors scan with which rules

### Rules Section

**Create rules directly:**
1. Go to **Add-ons → Extensions → YARA**
2. Navigate to **Rules** tab
3. Click **Add Rule**
4. Paste YARA rule content
5. Click **Save**

**Reference rules from YARA Manager:**
Rules synced via YARA Manager automatically appear here.

### Scanners Section

Scanners define which sensors scan with which YARA rules.

**Configuration:**
- **Filter Tags**: Tags that must ALL be present (AND condition)
- **Platform**: One of the platforms must match (OR condition)
- **YARA Rules**: Select which rules to apply

**Example:**
- Tags: `production`, `server`
- Platforms: `Windows`
- Rules: `ransomware-detection`, `malware-families`

This applies the selected YARA rules to all Windows sensors with both `production` AND `server` tags.

### Scan Types

**Automated scans:**
Configured scanners run automatically on:
- Files loaded in memory
- Process memory

**Manual scans:**
Trigger via:
- Sensor details page → **Run YARA scan** button
- YARA Scanners page → **Scan** button
- Sensor console
- D&R rule response
- API

### Using YARA in D&R Rules

Trigger YARA scans as a response action:

```yaml
- action: extension request
  extension action: scan
  extension name: ext-yara
  extension request:
    sources: []  # Specify YARA rule sources as strings
    selector: 'plat == windows'  # Sensor selector
    # OR use sid instead:
    # sid: '{{ .routing.sid }}'
    yara_scan_ttl: 86400  # Default: 1 day (86,400 seconds)
```

**Note:** Must specify either `selector` OR `sid`, not both.

---

## D&R Integration

### Triggering YARA Scans from D&R Rules

YARA scanning integrates seamlessly with Detection & Response rules.

### Pattern: Event → YARA Scan → Detection

1. **D&R Rule 1**: Detect suspicious event → trigger YARA scan
2. **Sensor**: Execute YARA scan → emit `YARA_DETECTION` event
3. **D&R Rule 2**: Detect `YARA_DETECTION` event → report detection

### Example 1: Scan New Processes

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
    investigation: Yara Scan Process
    suppression:
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
        - Yara Scan Process
      max_count: 1
      period: 1m
```

**Key points:**
- Detects process execution from Downloads directory
- Scans the process memory with YARA
- Uses suppression to prevent scanning the same process multiple times

### Example 2: Scan New Files

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - case sensitive: false
      op: matches
      path: event/FILE_PATH
      re: .\:\\(users|windows\\temp)\\.*
    - case sensitive: false
      op: matches
      path: event/FILE_PATH
      re: .*\.(exe|dll)

respond:
  - action: report
    name: Executable written to Users or Temp (yara scan)
  - action: task
    command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
    investigation: Yara Scan Executable
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
        - Yara Scan Executable
      max_count: 1
      period: 1m
```

**Key points:**
- Detects executable files written to sensitive directories
- Scans the file on disk with YARA
- Uses suppression to prevent scanning the same file multiple times

### Example 3: Detecting YARA Matches (On-Disk)

```yaml
detect:
  event: YARA_DETECTION
  op: and
  rules:
    - not: true
      op: exists
      path: event/PROCESS/*
    - op: exists
      path: event/RULE_NAME

respond:
  - action: report
    name: YARA Detection on Disk - {{ .event.RULE_NAME }}
    priority: 3
  - action: add tag
    tag: yara_detection_disk
    ttl: 80000
```

**Logic:**
- Detects `YARA_DETECTION` events
- Checks that `event/PROCESS/*` does NOT exist (indicates file scan)
- Reports detection with rule name
- Tags sensor for tracking

### Example 4: Detecting YARA Matches (In-Memory)

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
    name: YARA Detection in Memory - {{ .event.RULE_NAME }}
    priority: 4
  - action: add tag
    tag: yara_detection_memory
    ttl: 80000
  - action: task
    command: history_dump
    investigation: yara-memory-detection
```

**Logic:**
- Detects `YARA_DETECTION` events
- Checks that `event/PROCESS/*` exists (indicates memory scan)
- Reports detection with higher priority (running malware)
- Captures process history for investigation

### YARA_DETECTION Event Structure

```json
{
  "RULE_NAME": "malware_detection_rule",
  "FILE_PATH": "C:\\malicious.exe",
  "HASH": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "PROCESS": {
    "PROCESS_ID": 1234,
    "FILE_PATH": "C:\\malicious.exe"
  }
}
```

**Key fields:**
- `RULE_NAME`: Name of the YARA rule that matched
- `FILE_PATH`: Path to the file scanned
- `HASH`: SHA256 hash of the file
- `PROCESS`: Present only for memory scans (contains PID and process path)

---

## Performance and Suppression

### Resource Utilization Warning

YARA scanning is CPU-intensive and can impact endpoint performance if not properly managed.

**Critical rule:**
**Always use suppression when triggering YARA scans via D&R rules.**

### Suppression Strategy

Suppression prevents the same resource from being scanned repeatedly.

**Suppress by Process ID:**
```yaml
- action: task
  command: yara_scan hive://yara/malware-rule --pid "{{ .event.PROCESS_ID }}"
  suppression:
    is_global: false
    keys:
      - '{{ .event.PROCESS_ID }}'
      - Yara Scan Process
    max_count: 1
    period: 1m
```

**Suppress by File Path:**
```yaml
- action: task
  command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
  suppression:
    is_global: false
    keys:
      - '{{ .event.FILE_PATH }}'
      - Yara Scan File
    max_count: 1
    period: 5m
```

### Suppression Parameters

- `is_global`:
  - `false`: Per-sensor suppression
  - `true`: Organization-wide suppression
- `keys`: List of values to track (use template strings for dynamic values)
- `max_count`: Maximum executions allowed
- `period`: Time window (e.g., `1m`, `5m`, `1h`)

### Best Practices for Performance

1. **Always use suppression** with YARA scan tasks
2. **Target scans** to specific events, not all events
3. **Use appropriate time periods** (1-5 minutes minimum)
4. **Test rules** on small sensor groups before deploying org-wide
5. **Monitor CPU usage** after deploying YARA scans
6. **Optimize YARA rules** to be as specific as possible
7. **Avoid broad directory scans** in automated rules

### Example: Safe YARA Scanning Pattern

```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    # Target specific file types
    - op: ends with
      path: event/FILE_PATH
      value: .exe
      case sensitive: false
    # Target specific directories
    - op: contains
      path: event/FILE_PATH
      value: \Downloads\
      case sensitive: false
    # Size limit to avoid scanning large files
    - op: is lower than
      path: event/FILE_SIZE
      value: 10485760  # 10 MB

respond:
  - action: task
    command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
    investigation: Safe YARA Scan
    suppression:
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
        - Safe YARA Scan
      max_count: 1
      period: 5m
```

This pattern:
- Targets only executables
- Only in Downloads directory
- Only files under 10 MB
- Suppresses duplicate scans for 5 minutes

---

## Best Practices

### Rule Development

1. **Test rules before deployment**
   - Use YARA command-line tool locally
   - Test against known malware samples
   - Test against benign files to check false positives

2. **Use descriptive names**
   ```yara
   rule Emotet_Banking_Trojan_2024
   {
       // Better than: rule malware1
   }
   ```

3. **Include comprehensive metadata**
   ```yara
   meta:
       description = "Detects Emotet banking trojan variant from 2024 campaign"
       author = "Security Team"
       date = "2025-01-15"
       reference = "https://threat-intel.example.com/emotet-2024"
       hash = "abc123..."
       mitre_attack = "T1204.002"
   ```

4. **Be specific with strings**
   ```yara
   // Better
   strings:
       $specific = "UNIQUE_MALWARE_STRING_12345"

   // Avoid
   strings:
       $generic = "Windows"
   ```

5. **Use fullword for common terms**
   ```yara
   strings:
       $cmd = "cmd" fullword  // Matches "cmd" but not "command"
   ```

6. **Optimize conditions**
   ```yara
   condition:
       uint16(0) == 0x5A4D and  // Check PE header first (fast)
       filesize < 2MB and       // Filter by size (fast)
       2 of ($string*)          // Then check strings (slower)
   ```

### Rule Organization

1. **Group related rules**
   - Store malware family rules together
   - Use consistent naming conventions
   - Organize by threat type or campaign

2. **Version your rules**
   ```yara
   meta:
       version = "1.2"
       changelog = "Added detection for new variant"
   ```

3. **Use Config Hive effectively**
   - One rule file per malware family
   - Or multiple related rules in one file
   - Use descriptive hive keys: `hive://yara/emotet-2024`

### Deployment Strategy

1. **Start with high-confidence rules**
   - Deploy well-tested rules first
   - Monitor for false positives
   - Gradually add more rules

2. **Use staged deployment**
   - Test on small sensor group with specific tag
   - Monitor for issues
   - Expand to broader deployment

3. **Monitor performance**
   - Watch CPU usage on endpoints
   - Track scan execution frequency
   - Adjust suppression as needed

4. **Regular updates**
   - Update rules with new threat intelligence
   - Remove outdated rules
   - Test updates before deployment

### Testing Strategy

1. **Unit test rules locally**
   ```bash
   yara my-rule.yar /path/to/test/files/
   ```

2. **Test against known samples**
   - Malware samples (in safe environment)
   - Clean files (check false positives)
   - Edge cases

3. **Use D&R replay for integration testing**
   ```bash
   limacharlie replay --rule-content dr-rule.yaml --events test-events.json
   ```

4. **Monitor initial deployment**
   - Check `YARA_DETECTION` events
   - Review reported detections
   - Investigate any false positives

### False Positive Management

1. **Create exclusions**
   ```yara
   condition:
       (all of ($malware*)) and
       not (filepath matches /^C:\\Windows\\System32/)
   ```

2. **Use FP rules in D&R**
   ```yaml
   # False Positive Rule
   detect:
     event: YARA_DETECTION
     op: and
     rules:
       - op: is
         path: event/RULE_NAME
         value: my_yara_rule
       - op: is
         path: routing/hostname
         value: known-dev-machine
   ```

3. **Refine string patterns**
   - Add more context to strings
   - Use byte patterns instead of text where possible
   - Require multiple strings to match

### Security Considerations

1. **Protect YARA rules**
   - Treat rules as sensitive
   - Use appropriate permissions
   - Don't share private rules publicly

2. **Validate external sources**
   - Review community rules before deploying
   - Understand what each rule detects
   - Check for conflicts with legitimate software

3. **Monitor rule effectiveness**
   - Track detection rates
   - Review detections regularly
   - Update rules based on threat landscape

---

## Complete Examples

### Example 1: Basic Malware Detection

**YARA Rule:**
```yara
rule Basic_Malware_Detection
{
    meta:
        description = "Detects basic malware patterns"
        author = "Security Team"
        date = "2025-01-15"

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

**Store in Config Hive:**
```bash
limacharlie hive set yara --key basic-malware --data basic-malware.yar --data-key rule
```

**D&R Rule to Scan:**
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

**D&R Rule to Detect:**
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
  - action: task
    command: deny_tree <<routing/this>>
  - action: isolate network
```

### Example 2: Ransomware Detection

**YARA Rule:**
```yara
rule Ransomware_Detection
{
    meta:
        description = "Detects common ransomware patterns"
        author = "Security Team"
        date = "2025-01-15"
        mitre_attack = "T1486"

    strings:
        // Ransomware note strings
        $note1 = "your files have been encrypted" nocase
        $note2 = "bitcoin address" nocase
        $note3 = "decrypt_instructions" nocase

        // Encryption-related strings
        $crypt1 = "AES256" nocase
        $crypt2 = "RSA2048" nocase

        // File extension strings
        $ext1 = ".locked" nocase
        $ext2 = ".encrypted" nocase
        $ext3 = ".crypt" nocase

    condition:
        filesize < 10MB and
        (
            (2 of ($note*)) or
            (1 of ($note*) and 1 of ($crypt*)) or
            (2 of ($ext*) and 1 of ($crypt*))
        )
}
```

**D&R Rule to Scan New Documents:**
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

**D&R Rule to Detect and Respond:**
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
  - action: isolate network
  - action: task
    command: history_dump
    investigation: ransomware-incident
  - action: add tag
    tag: ransomware-detected
    ttl: 604800  # 7 days
```

### Example 3: Webshell Detection

**YARA Rule:**
```yara
rule Webshell_Detection
{
    meta:
        description = "Detects common webshell patterns"
        author = "Security Team"
        date = "2025-01-15"
        mitre_attack = "T1505.003"

    strings:
        // PHP webshell patterns
        $php1 = "<?php eval(" nocase
        $php2 = "<?php system(" nocase
        $php3 = "<?php exec(" nocase
        $php4 = "<?php passthru(" nocase
        $php5 = "base64_decode" nocase

        // ASP webshell patterns
        $asp1 = "eval request" nocase
        $asp2 = "execute request" nocase
        $asp3 = "wscript.shell" nocase

        // Common webshell strings
        $web1 = "c99shell" nocase
        $web2 = "r57shell" nocase
        $web3 = "WSO" fullword

    condition:
        filesize < 1MB and
        (
            (2 of ($php*)) or
            (1 of ($php*) and $php5) or
            (2 of ($asp*)) or
            (any of ($web*))
        )
}
```

**D&R Rule for Linux Web Servers:**
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

### Example 4: Credential Stealer Detection

**YARA Rule:**
```yara
rule Credential_Stealer
{
    meta:
        description = "Detects credential stealing malware"
        author = "Security Team"
        date = "2025-01-15"
        mitre_attack = "T1555, T1552"

    strings:
        // Browser credential paths
        $path1 = "\\Google\\Chrome\\User Data" nocase
        $path2 = "\\Mozilla\\Firefox\\Profiles" nocase
        $path3 = "Login Data" nocase

        // Windows credential references
        $win1 = "SAM" fullword
        $win2 = "lsass.exe" nocase
        $win3 = "Credential Manager" nocase

        // Common credential stealer functions
        $func1 = "ReadProcessMemory"
        $func2 = "CryptUnprotectData"
        $func3 = "sqlite3_open"

    condition:
        uint16(0) == 0x5A4D and
        filesize < 3MB and
        (
            (2 of ($path*) and 1 of ($func*)) or
            (2 of ($win*) and 1 of ($func*))
        )
}
```

**D&R Rule to Detect:**
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
  - action: add tag
    tag: credential-stealer-detected
    ttl: 86400
```

### Example 5: External Rule Source (Community Rules)

**Using YARA Manager for Yara-Rules Repository:**

1. Navigate to **Add-ons → Extensions → YARA Manager**
2. Click **Add New Yara Configuration**
3. Enter name: `Community Malware Rules`
4. Enter ARL: `[github,Yara-Rules/rules/malware]`
5. Click **Save**
6. Click **Manual Sync**

**D&R Rule to Use Community Rules:**
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

### Example 6: Comprehensive Multi-Rule Detection

**YARA Rules File (multiple rules):**
```yara
rule APT_Backdoor_Network
{
    meta:
        description = "Detects APT backdoor network behavior"

    strings:
        $net1 = "Mozilla/5.0 (Windows NT 6.1; WOW64)" nocase
        $net2 = "User-Agent:" nocase
        $domain = /https?:\/\/[a-z0-9]{8,12}\.(com|net|org)/

    condition:
        all of them
}

rule APT_Backdoor_Persistence
{
    meta:
        description = "Detects APT backdoor persistence mechanisms"

    strings:
        $reg1 = "Software\\Microsoft\\Windows\\CurrentVersion\\Run" nocase
        $reg2 = "HKEY_LOCAL_MACHINE" nocase
        $svc1 = "CreateService" nocase

    condition:
        1 of ($reg*) or $svc1
}

rule APT_Backdoor_Combined
{
    meta:
        description = "Combined APT backdoor detection"

    condition:
        APT_Backdoor_Network or APT_Backdoor_Persistence
}
```

**Store in Config Hive:**
```bash
limacharlie hive set yara --key apt-backdoor --data apt-backdoor.yar --data-key rule
```

**D&R Rule to Scan:**
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

**D&R Rule to Detect Any APT Rule:**
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
  - action: task
    command: history_dump
    investigation: apt-detection
  - action: task
    command: netstat
    investigation: apt-detection
  - action: isolate network
  - action: add tag
    tag: apt-detected
```

---

## Quick Reference

### YARA Command Syntax

```bash
# Scan a file
yara_scan hive://yara/RULE_NAME -f "FILE_PATH"

# Scan a process
yara_scan hive://yara/RULE_NAME --pid PID

# Scan a directory
yara_scan hive://yara/RULE_NAME --path "DIRECTORY_PATH"
```

### Config Hive CLI Commands

```bash
# Set YARA rule
limacharlie hive set yara --key RULE_NAME --data RULE_FILE --data-key rule

# Get YARA rule
limacharlie hive get yara --key RULE_NAME

# Delete YARA rule
limacharlie hive del yara --key RULE_NAME

# List all YARA rules
limacharlie hive list yara
```

### D&R Pattern: Scan and Detect

```yaml
# Rule 1: Trigger YARA scan
detect:
  event: SOME_EVENT
  # detection logic

respond:
  - action: task
    command: yara_scan hive://yara/RULE_NAME --pid "{{ .event.PROCESS_ID }}"
    suppression:
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m

---

# Rule 2: Detect YARA match
detect:
  event: YARA_DETECTION
  op: is
  path: event/RULE_NAME
  value: YOUR_YARA_RULE_NAME

respond:
  - action: report
    name: "YARA Detection - {{ .event.RULE_NAME }}"
```

### Common YARA Patterns

```yara
# PE file check
condition:
    uint16(0) == 0x5A4D

# File size
condition:
    filesize < 1MB

# String at specific location
condition:
    $string at 0

# Multiple string matches
condition:
    2 of ($str*)
    all of them
    any of them

# Count occurrences
condition:
    #string > 5
```

---

## When to Use This Skill

Use the yara-manager skill when users ask about:

- Creating YARA rules
- YARA rule syntax and structure
- Storing YARA rules in Config Hive
- Scanning files or processes with YARA
- Triggering YARA scans from D&R rules
- Detecting YARA_DETECTION events
- Managing YARA rules (YARA Manager extension)
- External YARA rule sources (GitHub, URLs)
- YARA performance optimization
- Suppression strategies for YARA scans
- Integrating YARA with Detection & Response
- Troubleshooting YARA rules
- YARA best practices
- Malware detection with YARA
- Automated YARA scanning

This skill provides comprehensive, authoritative guidance for all YARA-related operations in LimaCharlie.
