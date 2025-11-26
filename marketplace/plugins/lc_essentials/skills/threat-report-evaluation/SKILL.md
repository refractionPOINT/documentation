---
name: threat-report-evaluation
description: Evaluate threat reports, breach analyses, and IOC reports to search for compromise indicators across LimaCharlie organizations. Extract IOCs (hashes, domains, IPs, file paths), perform IOC searches, identify malicious behaviors, generate LCQL queries, create D&R rules and lookups. Use when investigating threats, APT reports, malware analysis, breach postmortems, or threat intelligence feeds. Emphasizes working ONLY with data from the report and organization, never making assumptions.
allowed-tools: mcp__plugin_lc-essentials_limacharlie__lc_call_tool, mcp__plugin_lc-essentials_limacharlie__generate_lcql_query, mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection, mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond, mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components, Read, Bash, Skill
---

# Threat Report Evaluation & IOC Analysis

Systematically evaluate threat reports to determine organizational impact and create comprehensive defense-in-depth detections.

## Critical Principles

- Extract IOCs and behaviors ONLY from the provided report
- Search ONLY in the specified LimaCharlie organization
- NEVER fabricate or assume data not present
- ALWAYS use AI generation tools for rules—never write YAML manually
- If the report is PDF or other rich file, download it, convert it to markdown and use that
- Ask for user confirmation before creating any resources

## Required Information

Before starting, obtain:
- **Threat Report**: URL, PDF, or text
- **Organization ID (OID)**: Target LimaCharlie org
- **Time Window**: Search depth (default: 7 days)

---

## Step 1: Platform Check

1. Read the threat report and identify mentioned platforms
2. Get platforms in org via `get_platform_names` function
3. Proceed only with platforms present in BOTH report AND organization

---

## Step 2: Extract & Search IOCs

### Extract from Report

- File hashes (MD5, SHA1, SHA256)
- File names and paths
- Domains and URLs
- IP addresses
- Email addresses
- User/package names
- Registry keys
- Process names

### Search IOCs

Use `search_iocs` or `batch_search_iocs` for each IOC type.

### Classify Results

- **NOT FOUND**: Clean
- **RARE (1-10)**: Investigate immediately
- **MODERATE (10-100)**: Manual review required
- **UBIQUITOUS (>100)**: Weak IOC, possible false positive

---

## Step 3: Behavioral Analysis

### Extract Behaviors from Report

- Process execution patterns
- Command-line arguments
- Network behaviors
- File operations
- Registry modifications
- Lateral movement techniques
- Privilege escalation methods
- Defense evasion tactics

### Generate & Execute LCQL Queries

For each behavior:
1. Use `generate_lcql_query` with specific natural language description
2. Execute via `run_lcql_query`
3. If >100 results: refine query with exclusions
4. Document all queries and results

---

## Step 4: Defense-in-Depth Detection Setup

**Create comprehensive, layered detections covering all attack surfaces. Complete the Detection Checklist below.**

### Detection Generation Workflow

For EVERY detection:
1. `generate_dr_rule_detection` → detection component
2. `generate_dr_rule_respond` → response component
3. `validate_dr_rule_components` → validate before creation
4. Present to user → get approval
5. Create via `set_dr_general_rule`

**Testing & Refinement**: For comprehensive testing of created rules (unit tests, historical replay, multi-org parallel testing), use the `detection-engineering` skill which provides iterative test-refine workflows.

---

### Layer 1: Process-Based Detections

Create rules for:

**A. Process Execution**
- Detect specific malicious process names
- Prompt: "Detect process execution of [process.exe] on [platform]"

**B. Command-Line Patterns**
- Detect suspicious arguments, encoded commands, LOLBins abuse
- Prompt: "Detect [process] with command line containing [pattern]"

**C. Parent-Child Anomalies**
- Detect unusual parent-child relationships (e.g., excel.exe spawning cmd.exe)
- Prompt: "Detect [child process] spawned by [parent process]"

**D. Process Path Anomalies**
- Detect execution from suspicious locations (temp, appdata, public folders)
- Prompt: "Detect process execution from path containing [suspicious_path]"

**E. Module Loading**
- Detect suspicious DLL loads
- Prompt: "Detect MODULE_LOAD where module path contains [malicious_dll]"

---

### Layer 2: Network-Based Detections

Create rules for:

**A. DNS Requests**
- Match domains against lookups
- Prompt: "Detect DNS_REQUEST where domain matches [lookup-name] lookup"

**B. Network Connections**
- Match IPs and ports
- Prompt: "Detect NETWORK_CONNECTIONS to IP [ip_address] or port [port]"

**C. HTTP/SSL Patterns**
- Detect suspicious user agents, URLs, JA3 hashes
- Prompt: "Detect HTTP requests with user agent containing [pattern]"

**D. Beaconing Behavior**
- Detect periodic callbacks to C2
- Prompt: "Detect repeated network connections to same destination within [timeframe]"

**E. External Data Transfer**
- Detect large outbound transfers
- Prompt: "Detect NETWORK_CONNECTIONS with bytes sent exceeding [threshold]"

---

### Layer 3: File-Based Detections

Create rules for:

**A. File Creation**
- Detect malicious file drops
- Prompt: "Detect NEW_DOCUMENT where file path matches [path_pattern]"

**B. File Modification**
- Detect tampering with critical files
- Prompt: "Detect FILE_MOD in [critical_directory]"

**C. File Hash Matching**
- Match against hash lookups
- Prompt: "Detect file activity where hash matches [lookup-name] lookup"

**D. YARA Rules**
- Scan files for malicious content patterns
- Create YARA rule targeting strings/patterns from report
- Deploy via `set_yara_rule` function

**E. Suspicious Extensions**
- Detect double extensions, script files in unexpected locations
- Prompt: "Detect file creation with extension [.hta/.scr/.js] in user directories"

---

### Layer 4: Persistence & System Modification

Create rules for:

**A. Registry Persistence (Windows)**
- Run keys, services, scheduled tasks via registry
- Prompt: "Detect registry modification to [Run key path]"

**B. Scheduled Tasks / Cron Jobs**
- Detect task creation
- Prompt: "Detect NEW_PROCESS of schtasks.exe or at.exe with /create"

**C. Service Installation**
- Detect new services
- Prompt: "Detect service creation events in Windows Event Log"

**D. Startup Folder Modifications**
- Detect drops in startup locations
- Prompt: "Detect NEW_DOCUMENT in startup folder paths"

**E. WMI Persistence**
- Detect WMI event subscriptions
- Prompt: "Detect WMI process creation with EventConsumer or EventFilter"

**F. Linux Persistence**
- Cron, systemd, init.d modifications
- Prompt: "Detect file modification in /etc/cron* or /etc/systemd/"

---

### Layer 5: Credential & Privilege Escalation

Create rules for:

**A. Credential Dumping**
- LSASS access, SAM/SECURITY hive access
- Prompt: "Detect process accessing lsass.exe memory"

**B. Privilege Escalation Tools**
- Detect known priv-esc tools
- Prompt: "Detect execution of [mimikatz/rubeus/potato] variants"

**C. Token Manipulation**
- Detect token theft/impersonation
- Prompt: "Detect process with SeDebugPrivilege or SeImpersonatePrivilege abuse"

---

### Layer 6: Lateral Movement

Create rules for:

**A. Remote Execution**
- PsExec, WMI, WinRM, SSH
- Prompt: "Detect [psexec/wmic/winrs] with remote execution arguments"

**B. Pass-the-Hash/Ticket**
- Detect anomalous authentication patterns
- Prompt: "Detect authentication events with suspicious logon type"

**C. RDP/VNC Activity**
- Detect unexpected remote desktop
- Prompt: "Detect mstsc.exe or vnc execution from non-admin systems"

---

### Layer 7: Defense Evasion

Create rules for:

**A. Log Clearing**
- Detect event log clearing
- Prompt: "Detect wevtutil or Clear-EventLog execution"

**B. Security Tool Tampering**
- Detect AV/EDR disabling
- Prompt: "Detect process terminating security product processes"

**C. Timestomping**
- Detect file timestamp manipulation
- Prompt: "Detect timestomp tool execution or suspicious SetFileTime calls"

**D. Masquerading**
- Detect processes mimicking legitimate names in wrong locations
- Prompt: "Detect svchost.exe execution from non-System32 path"

---

### Layer 8: Stateful & Threshold Rules

Create rules for:

**A. Chained Detections**
- Detect sequence: recon → exploitation → persistence
- Use stateful rules with `with child` or `with descendant` operators

**B. Threshold Alerts**
- Detect high-frequency events
- Prompt: "Detect more than [N] failed logins within [timeframe]"

**C. Aggregation Rules**
- Detect patterns across multiple sensors
- Use `COUNT_UNIQUE` in LCQL to identify scope

---

### Layer 9: IOC Lookups

Create lookups for ALL extracted IOCs:

| Lookup Name | IOC Type | Example |
|-------------|----------|---------|
| `[threat]-hashes` | SHA256, SHA1, MD5 | Malware samples |
| `[threat]-domains` | DNS names | C2 domains |
| `[threat]-ips` | IPv4/IPv6 | C2 infrastructure |
| `[threat]-paths` | File paths | Persistence locations |
| `[threat]-urls` | Full URLs | Payload delivery |
| `[threat]-emails` | Email addresses | Phishing senders |

For each lookup, create matching D&R rules:
- DNS_REQUEST → domain lookup
- NETWORK_CONNECTIONS → IP lookup
- NEW_PROCESS/NEW_DOCUMENT → hash lookup
- File events → path lookup

---

### Layer 10: False Positive Management

**A. Identify Noisy Rules**
- Rules with >50 hits/day need tuning

**B. Create FP Suppression Rules**
- Exclude known-good software, paths, users
- Prompt: "Detect [behavior] excluding processes signed by [vendor]"

**C. Exclusion Lookups**
- Create allowlist lookups for legitimate software
- Reference in rules with `op: lookup` negation

---

## Detection Checklist

**Claude MUST complete this checklist for every threat report:**

### Process Detections
- [ ] Malicious process names detected
- [ ] Command-line patterns detected
- [ ] Parent-child anomalies detected
- [ ] Suspicious execution paths detected
- [ ] Module loading detected (if applicable)

### Network Detections
- [ ] DNS lookups for threat domains created
- [ ] Network connections to threat IPs created
- [ ] HTTP/URL patterns detected
- [ ] Beaconing patterns detected (if applicable)

### File Detections
- [ ] File creation in persistence locations detected
- [ ] File hash matching via lookups created
- [ ] YARA rules created (if file samples available)
- [ ] Suspicious file extensions detected

### Persistence Detections
- [ ] Registry persistence detected (Windows)
- [ ] Scheduled task creation detected
- [ ] Service installation detected
- [ ] Startup modifications detected
- [ ] WMI/cron persistence detected

### Credential/Privilege Detections
- [ ] Credential dumping detected
- [ ] Known priv-esc tools detected

### Lateral Movement Detections
- [ ] Remote execution tools detected
- [ ] Anomalous authentication detected

### Defense Evasion Detections
- [ ] Log clearing detected
- [ ] Security tool tampering detected
- [ ] Masquerading detected

### IOC Lookups
- [ ] Hash lookup created and referenced
- [ ] Domain lookup created and referenced
- [ ] IP lookup created and referenced
- [ ] Path lookup created and referenced

### Validation
- [ ] All rules validated via `validate_dr_rule_components`
- [ ] FP suppression rules created for noisy detections
- [ ] User approved all detections before creation

---

## Rule Naming Convention

Use consistent naming: `[threat-name]-[detection-type]-[indicator]`

Examples:
- `apt-x-process-encoded-powershell`
- `apt-x-network-c2-domain`
- `apt-x-file-persistence-path`
- `apt-x-registry-runkey`

---

## Response Actions

For each rule, include appropriate responses:

**High Priority (8-10):**
- Report with publish: true
- Add tag with 7-day TTL
- Consider sensor isolation for critical hits

**Medium Priority (5-7):**
- Report with publish: true
- Add tag with 3-day TTL

**Low Priority (1-4):**
- Report only
- Add informational tag

Always include metadata:
- MITRE ATT&CK technique IDs
- Threat campaign name
- Remediation steps
- Report source reference

---

## Final Report Template

```markdown
# Threat Report Evaluation: [Report Name]
Date: [YYYY-MM-DD]
Organization: [OID]

## Executive Summary
[2-3 sentences on findings]

## IOC Search Results
| IOC Type | Value | Status | Occurrences |
|----------|-------|--------|-------------|

## Behavioral Query Results
| Behavior | Query | Results | Status |
|----------|-------|---------|--------|

## Detections Created

### D&R Rules
| Rule Name | Detection Type | Priority |
|-----------|---------------|----------|

### Lookups
| Lookup Name | IOC Count | Types |
|-------------|-----------|-------|

### YARA Rules
| Rule Name | Target |
|-----------|--------|

## Affected Sensors
| Sensor | Reason | Action Required |
|--------|--------|-----------------|

## Detection Checklist Status
[Include completed checklist]

## Recommendations
1. [Action items]
```

---

## Troubleshooting

**Validation fails**: Refine your AI generation prompt—don't manually edit YAML.

**Too many results**: Add exclusions to your detection prompt.

**IOC ubiquitous**: Mark as weak IOC, consider excluding from detections.

**Platform missing**: Skip that platform's detections, document in report.

**Query errors**: Use `lookup-lc-doc` skill for LCQL syntax reference.
