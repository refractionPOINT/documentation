---
name: threat-report-evaluation
description: Evaluate threat reports, breach analyses, and IOC reports to search for compromise indicators across LimaCharlie organizations. Extract IOCs (hashes, domains, IPs, file paths), perform IOC searches, identify malicious behaviors, generate LCQL queries, create D&R rules and lookups. Use when investigating threats, APT reports, malware analysis, breach postmortems, or threat intelligence feeds. Emphasizes working ONLY with data from the report and organization, never making assumptions.
allowed-tools: mcp__plugin_lc-essentials_limacharlie__lc_api_call, mcp__plugin_lc-essentials_limacharlie__generate_lcql_query, mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection, mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond, mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components, Read, Bash, Skill
---

# Threat Report Evaluation & IOC Analysis

Systematically evaluate threat reports, breach analyses, and IOC reports to determine if one or multiple LimaCharlie organizations are affected, then create detection rules.

## When to Use

Use this skill when the user needs to:
- Investigate a threat report, APT analysis, or malware writeup
- Evaluate a breach postmortem or incident report
- Process threat intelligence feeds or IOC lists
- Determine if an organization is affected by a specific threat
- Hunt for indicators of compromise (IOCs) in historical data
- Create detection rules based on threat intelligence

Common scenarios:
- "Check if we're affected by this APT campaign"
- "Analyze this malware report and create detection rules"
- "Search for these IOCs in our environment"
- "Hunt for behavioral indicators from this threat intelligence"

## Critical Principles

**⚠️ WORK ONLY WITH ACTUAL DATA**
- Extract IOCs and behaviors ONLY from the provided report
- Search for IOCs ONLY in the specified LimaCharlie organization
- NEVER make assumptions about data not present in the report or org
- NEVER fabricate IOCs, file paths, domains, or behavioral patterns
- If information is missing, ask the user for clarification

## Required Information

Before starting, gather:
- **Threat Report**: URL, PDF, text, or description of the threat/breach/IOC report
- **Organization ID (OID)**: Target LimaCharlie organization UUID to search
- **Time Window**: How far back to search (default: 7 days for behavioral queries)

## Workflow Overview

This skill follows a systematic 4-step approach:

1. **Evaluate Platforms** - Identify relevant platforms (Windows, Linux, macOS, Office365, AWS, etc.)
2. **Extract & Search IOCs** - Extract all IOCs and perform searches in the organization
3. **Identify Behaviors** - Create and execute LCQL queries for behavioral indicators
4. **Setup Detection** - Generate D&R rules and lookups for ongoing detection

## Step 1: Evaluate Relevant Platforms

### What to Do

1. Read the threat report carefully
2. Identify which platforms are mentioned:
   - **Endpoint platforms**: Windows, Linux, macOS, iOS, Android, Chrome
   - **Cloud platforms**: AWS, GCP, Azure (various services)
   - **SaaS platforms**: Office365, GitHub, Slack, Okta, 1Password
   - **Security products**: CrowdStrike, SentinelOne, Microsoft Defender
   - **Other platforms**: See `./functions/get-platform-names.md` for complete list

3. Get the platforms available in the target organization:

```bash
# Use the limacharlie-call skill to call get-platform-names function
# Read: ./skills/limacharlie-call/functions/get-platform-names.md
```

4. **Filter to relevant platforms**: Only proceed with platforms that:
   - Are mentioned in the threat report
   - Are actually present in the LimaCharlie organization
   - Have telemetry/sensors configured

5. Document your findings:
   - Platforms mentioned in report: [list]
   - Platforms available in org: [list]
   - Relevant platforms to investigate: [intersection of above]

### Example

Report mentions: "Windows endpoints, Office365 mailboxes, AWS S3 buckets"

After checking org:
- Windows: ✓ Found (15 sensors)
- Office365: ✗ Not configured
- AWS: ✓ Found (cloud adapter configured)

**Conclusion**: Focus investigation on Windows endpoints and AWS, ignore Office365 references.

## Step 2: Extract & Search IOCs

### What to Do

1. **Extract all IOCs** from the threat report:
   - **File hashes**: MD5, SHA1, SHA256
   - **File names**: Exact names mentioned
   - **File paths**: Full paths or path patterns
   - **Domains**: DNS names, C2 domains
   - **IP addresses**: IPv4, IPv6
   - **URLs**: Full URLs
   - **Email addresses**: Sender/receiver addresses
   - **User names**: Account names
   - **Package names**: NPM, PyPI, etc.
   - **Registry keys**: Windows registry paths
   - **Process names**: Specific process executables

2. **Perform IOC searches** using the LimaCharlie IOC search API:

```bash
# Use the limacharlie-call skill to call search-iocs or batch-search-iocs
# Read: ./skills/limacharlie-call/functions/search-iocs.md
# Read: ./skills/limacharlie-call/functions/batch-search-iocs.md
```

3. **Analyze results** for each IOC:
   - **Not found**: IOC not present in historical data
   - **Found and rare** (1-10 occurrences): Possible compromise, investigate further
   - **Found and ubiquitous** (>100 occurrences): Likely false positive or weak IOC
   - **Found and moderate** (10-100 occurrences): Requires manual review

4. **Record your findings** in a structured format:

```
IOC Search Results:
==================

HASHES:
- a1b2c3d4e5f6... (SHA256): NOT FOUND
- 9f8e7d6c5b4a... (MD5): FOUND - 3 occurrences (RARE - INVESTIGATE)

DOMAINS:
- evil-domain.com: FOUND - 147 occurrences (UBIQUITOUS - weak IOC)
- c2-server.xyz: NOT FOUND

IP ADDRESSES:
- 192.0.2.50: FOUND - 8 occurrences (RARE - INVESTIGATE)

FILE PATHS:
- C:\Windows\Temp\malware.exe: NOT FOUND
- /tmp/backdoor.sh: FOUND - 2 occurrences (RARE - INVESTIGATE)
```

### IOC Search Notes

- IOC searches look across **all historical telemetry** (typically 1 year with Insight)
- Results show **when** and **where** (which sensors) IOCs were seen
- Use `search-hosts` to find sensors by hostname or other criteria
- Prevalence analysis helps distinguish targeted attacks from noise

## Step 3: Identify Malicious Behaviors

### What to Do

1. **List behavioral indicators** from the threat report:
   - Specific process execution patterns
   - Command-line argument patterns
   - Network connection behaviors
   - File access patterns
   - Registry modifications
   - Lateral movement techniques
   - Privilege escalation methods
   - Defense evasion tactics

2. **Generate LCQL queries** for each behavior using the AI-powered generation:

```bash
# For each behavioral indicator, use the generate-lcql-query tool
# Example via the limacharlie-call skill:

# Skill: limacharlie-call
# Function: generate-lcql-query
# Read: ./skills/limacharlie-call/functions/generate-lcql-query.md

# Example behavior: "PowerShell execution with encoded commands"
# Generate query: "Show me PowerShell processes with encoded commands in the last 7 days"
```

3. **Review and refine queries**:
   - Check the generated LCQL syntax
   - Adjust time windows (default: `-7d` for 7 days)
   - Add platform filters if needed
   - Refine field selections

4. **Execute LCQL queries** against the organization:

```bash
# Use the limacharlie-call skill to call run-lcql-query
# Read: ./skills/limacharlie-call/functions/run-lcql-query.md
```

5. **Evaluate results**:
   - **No results**: Behavior not observed (good sign)
   - **Few results** (1-10): Investigate each occurrence
   - **Many results** (>100): Likely false positive, refine query

6. **Refine queries with high false positives**:
   - If a query returns too many results, consult the LCQL documentation:
     ```bash
     # Use the lookup-lc-doc skill to search for LCQL documentation
     # Skill: lookup-lc-doc
     ```
   - Add more specific filters
   - Exclude known-good processes/paths
   - Use COUNT_UNIQUE and GROUP BY to analyze patterns
   - Document all refinements in your report

7. **Record all queries and results**:

```
Behavioral Indicators & LCQL Queries:
======================================

BEHAVIOR 1: PowerShell with Encoded Commands
Query: -7d | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell.exe" and event/COMMAND_LINE contains "-enc"
Results: 3 occurrences found
Status: RARE - Review each occurrence
Refinements: None needed

BEHAVIOR 2: Suspicious Network Connections to C2
Query: -7d | plat == windows | NETWORK_CONNECTIONS | event/DESTINATION/IP_ADDRESS == "192.0.2.50"
Results: 0 occurrences
Status: NOT FOUND - No compromise detected
Refinements: N/A

BEHAVIOR 3: File Creation in System32
Query: -7d | plat == windows | NEW_DOCUMENT | event/FILE_PATH contains "\\Windows\\System32\\" and event/FILE_PATH ends with ".exe"
Results: 847 occurrences
Status: TOO MANY - Refined query needed
Refinements: Added exclusion for known Windows Update processes
Refined Query: -7d | plat == windows | NEW_DOCUMENT | event/FILE_PATH contains "\\Windows\\System32\\" and event/FILE_PATH ends with ".exe" and event/PARENT/FILE_PATH not contains "TrustedInstaller"
Refined Results: 12 occurrences
Status: MODERATE - Review each
```

### Behavioral Analysis Notes

- LCQL queries can search across event types: NEW_PROCESS, DNS_REQUEST, NETWORK_CONNECTIONS, WEL, etc.
- Use platform filters: `plat == windows`, `plat == linux`, `plat == macos`, `plat == office365`, etc.
- Combine with IOC filters: `event/DOMAIN_NAME`, `event/IP_ADDRESS`, `event/FILE_PATH`, `event/HASH`
- Aggregate results: `COUNT(event)`, `COUNT_UNIQUE(routing/sid)`, `GROUP BY()`
- See LCQL examples: `./docs/limacharlie/doc/Query_Console/lcql-examples.md`

## Step 4: Setup Detection

### What to Do

This is the final step where you create ongoing detection capabilities. You will:
1. Generate D&R rules for behavioral detections
2. Create Hive lookups for IOC matching
3. Generate D&R rules to match against lookups

**IMPORTANT**: Always ask for user confirmation before creating any objects in LimaCharlie.

**⚠️ CRITICAL: ALWAYS USE AI GENERATION TOOLS**

Never manually write D&R rule components. Always use the AI-powered generation tools to ensure correct syntax, validation against your organization's schema, and comprehensive metadata.

### AI Detection Tools Reference

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `generate-dr-rule-detection` | Generate detection component from natural language | For every D&R rule detection logic |
| `generate-dr-rule-respond` | Generate response component from natural language | For every D&R rule response action |
| `validate-dr-rule-components` | Validate detection + response before creation | Before creating ANY D&R rule |

**Benefits of AI Generation:**
- ✅ Validates against your organization's event schema
- ✅ Ensures correct field paths and operators
- ✅ Includes rich metadata (MITRE ATT&CK, remediation steps, references)
- ✅ Prevents syntax errors
- ✅ Provides explanations and comments

### 4A: Generate D&R Rules for Behaviors

**⚠️ DO NOT manually write YAML - use AI generation for every rule**

For each malicious behavior identified in Step 3, follow this exact workflow:

#### Step-by-Step AI Generation Workflow

**Step 1: Generate Detection Component**

Use the `generate-dr-rule-detection` tool with a clear, descriptive prompt:

```
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection(
  oid="[your-org-id]",
  query="Detect network connections to AWS EC2 metadata service IP address 169.254.169.254"
)
```

**Example Output:**
```yaml
# Detect network connections to AWS EC2 metadata service IP
# This rule identifies attempts to access the EC2 instance metadata service,
# which could indicate reconnaissance or credential harvesting.
event: NETWORK_CONNECTIONS
op: is
path: event/NETWORK_ACTIVITY/?/DESTINATION/IP_ADDRESS
value: 169.254.169.254
```

**Step 2: Generate Response Component**

Use the `generate-dr-rule-respond` tool to create the response actions:

```
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond(
  oid="[your-org-id]",
  query="Report detection with priority 8, add tag 'aws-metadata-access' with 24h TTL, include SSRF attack metadata"
)
```

**Example Output:**
```yaml
- action: report
  name: "Potential SSRF: AWS Metadata Access on {{ .routing.hostname }}"
  publish: true
  priority: 8
  metadata:
    author: security-team@company.com
    description: "Detected AWS metadata service access attempt"
    mitre_attack:
      - "T1190"  # Exploit Public-Facing Application
      - "T1592.002"  # Gather Victim Host Information
    level: high
    remediation: "Investigate source, review for SSRF vulnerability, rotate credentials if needed"
- action: add tag
  tag: aws-metadata-access
  ttl: 86400
```

**Step 3: Validate the Rule**

ALWAYS validate before creating:

```
mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components(
  detect={...detection from step 1...},
  respond=[...response from step 2...]
)
```

**Expected Result:**
```json
{
  "valid": true,
  "message": "D&R rule components are valid"
}
```

**Step 4: Review with User**

Present the generated rule to the user:
- Explain the detection logic
- Describe the response actions
- Highlight any MITRE ATT&CK mappings
- Ask for confirmation or refinements

**Step 5: Create the Rule**

Only after user approval:

```bash
# Use the set-dr-general-rule function
# Read: ./skills/limacharlie-call/functions/set-dr-general-rule.md
```

### 4B: Create Hive Lookups for IOCs

Organize IOCs by type and create lookups:

1. **Group IOCs by type**:
   - Domains: `threat-report-domains`
   - IP addresses: `threat-report-ips`
   - File hashes: `threat-report-hashes`
   - File paths: `threat-report-paths`

2. **Prepare lookup data** in the correct format:

```json
{
  "lookup_data": {
    "evil-domain.com": {
      "threat": "APT-X Campaign",
      "severity": "high",
      "source": "Threat Report 2024-01"
    },
    "c2-server.xyz": {
      "threat": "APT-X Campaign",
      "severity": "critical",
      "source": "Threat Report 2024-01"
    }
  }
}
```

3. **Review with user**:
   - Show the IOCs that will be added to lookups
   - Explain the lookup structure
   - Ask for confirmation

4. **Create lookups** after approval:

```bash
# Use the set-lookup function
# Read: ./skills/limacharlie-call/functions/set-lookup.md
```

### 4C: Create D&R Rules for IOC Matching

**⚠️ DO NOT manually write lookup rules - use AI generation**

Even for simple lookup-based rules, ALWAYS use AI generation to ensure correct syntax and comprehensive metadata.

For each IOC type, generate a D&R rule that checks events against the lookup:

#### AI-Generated Lookup Rule Example

**Scenario:** Create a rule to detect DNS requests matching the `threat-report-domains` lookup

**Step 1: Generate Detection (for Domain Lookup)**

```
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection(
  oid="[your-org-id]",
  query="Detect DNS requests where the domain matches entries in the threat-report-domains lookup"
)
```

**AI-Generated Output:**
```yaml
event: DNS_REQUEST
op: lookup
path: event/DOMAIN_NAME
resource: hive://lookup/threat-report-domains
case sensitive: false
```

**Step 2: Generate Response**

```
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond(
  oid="[your-org-id]",
  query="Report the detection with priority 9, include threat campaign metadata, add threat-detected tag with 7 day TTL"
)
```

**AI-Generated Output:**
```yaml
- action: report
  name: "Threat Domain Detected: {{ event/DOMAIN_NAME }} on {{ .routing.hostname }}"
  publish: true
  priority: 9
  metadata:
    threat_type: "APT-X Campaign"
    ioc_type: "domain"
    severity: high
    description: "DNS request matched known threat domain from APT-X campaign"
    remediation: "Isolate sensor, investigate process making the request, review network logs"
- action: add tag
  tag: threat-detected
  ttl: 604800
```

**Step 3: Validate and Create**

Follow the same validation and creation process as in Section 4A:
1. Use `validate-dr-rule-components` to validate
2. Review with user
3. Create after approval

**Other IOC Types:**

Use AI generation for all IOC types:
- **IP addresses**: "Detect network connections to IPs in the threat-report-ips lookup"
- **File hashes**: "Detect file activity where the hash matches the threat-report-hashes lookup"
- **File paths**: "Detect file creation where the path matches the threat-report-paths lookup"

### Detection Setup Notes

- **Naming convention**: Use descriptive names like `apt-x-powershell-encoded`, `apt-x-c2-communication`
- **Metadata**: Include threat name, report source, date in rule metadata
- **Priorities**: Set appropriate priorities (1-10, higher = more critical)
- **Tags**: Use tags to track affected sensors: `threat-detected`, `apt-x-compromise`
- **Suppression**: Consider adding suppression to avoid alert fatigue
- **False Positive rules**: If needed, create FP rules to exclude known-good patterns

### Writing Effective AI Generation Prompts

The quality of AI-generated rules depends on clear, descriptive prompts. Follow these guidelines:

#### For Detection Prompts

**✅ GOOD Prompts (Specific and Clear):**
- "Detect network connections to IP address 169.254.169.254 on any platform"
- "Detect PowerShell executions with encoded commands on Windows systems"
- "Detect DNS requests where the domain matches entries in the threat-intel-domains lookup"
- "Detect process execution of curl or wget with suspicious command-line arguments containing IP addresses"

**❌ BAD Prompts (Vague or Incomplete):**
- "metadata service rule" (too vague - what type of event?)
- "detect bad stuff" (no specifics)
- "powershell" (missing context - detect what about PowerShell?)

**Prompt Structure:**
1. Start with "Detect"
2. Specify the event type (network connection, DNS request, process execution)
3. Include specific indicators (IP, domain, file path, command pattern)
4. Add platform filters if relevant (Windows, Linux, AWS)

#### For Response Prompts

**✅ GOOD Prompts (Actionable and Complete):**
- "Report with priority 8, add tag 'ssrf-attempt' with 24h TTL, include MITRE ATT&CK metadata for T1190"
- "Report detection with high priority, tag sensor as 'compromised', include remediation steps for SSRF"
- "Create low-priority report, add informational tag, include reference to threat intelligence report"

**❌ BAD Prompts (Missing Details):**
- "report it" (missing priority, tags, metadata)
- "tag the sensor" (which tag? how long?)

**Prompt Structure:**
1. Specify action type (report, add tag, isolate)
2. Include priority level (1-10 or low/medium/high)
3. Describe tags and TTL
4. Request metadata (MITRE ATT&CK, remediation, references)

#### Refinement Tips

If the AI-generated rule isn't quite right:
1. **Don't manually edit the YAML** - refine your prompt instead
2. Be more specific about field paths or conditions
3. Add examples to your prompt: "like the NETWORK_CONNECTIONS event"
4. Request specific operators: "using the lookup operator"

## Complete Workflow Example

**Scenario**: User provides a report about "APT-X" targeting Windows systems

### Step 1: Platform Evaluation

```
User provides: APT-X report (Windows endpoints)
Check platforms: Windows sensors found (23 active)
Focus: Windows endpoint telemetry
```

### Step 2: IOC Extraction & Search

```
IOCs extracted:
- SHA256: a1b2c3d4e5f6... (malware payload)
- Domain: evil-apt-x.com (C2 server)
- IP: 203.0.113.50 (C2 IP)
- Path: C:\ProgramData\update.exe (persistence)

Search results:
- Hash a1b2c3d4e5f6...: NOT FOUND ✓
- Domain evil-apt-x.com: NOT FOUND ✓
- IP 203.0.113.50: FOUND - 2 occurrences ⚠
  - Sensor: web-server-01
  - Timestamps: 2024-01-15 14:23:11, 2024-01-15 14:25:33
- Path C:\ProgramData\update.exe: NOT FOUND ✓

CONCLUSION: Possible compromise on web-server-01, investigate further
```

### Step 3: Behavioral Analysis

```
Behaviors from report:
1. PowerShell with Base64 encoding
2. WMI lateral movement
3. Registry Run key persistence

Generated LCQL queries:

QUERY 1: PowerShell Base64
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell.exe" and (event/COMMAND_LINE contains "-enc" or event/COMMAND_LINE contains "-encoded")

Results: 5 occurrences
- 3 on web-server-01 (INVESTIGATE)
- 2 on admin-workstation (review scripts)

QUERY 2: WMI Lateral Movement
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH contains "wmic.exe" and event/COMMAND_LINE contains "process call create"

Results: 0 occurrences ✓

QUERY 3: Registry Run Key
-7d | plat == windows | WEL | event/EVENT/System/EventID == "13" and event/EVENT/EventData/TargetObject contains "\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"

Results: 147 occurrences
Refined: Added filter to exclude known software
Refined results: 3 occurrences (2 on web-server-01)
```

### Step 4: Detection Setup

```
Generate D&R rules using AI tools:

RULE 1: PowerShell with Encoding
----------------------------------
Step 1 - Generate detection:
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="Detect PowerShell executions with encoded commands on Windows"
)

Result: [AI generates detection component with proper event/FILE_PATH and event/COMMAND_LINE checks]

Step 2 - Generate response:
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="Report with priority 7, tag sensor with apt-x-suspect, include MITRE T1059.001 metadata"
)

Result: [AI generates response with report action, tags, and metadata]

Step 3 - Validate:
mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components(...)
Result: ✅ Valid

RULE 2: Registry Persistence
-----------------------------
[Same AI generation workflow for registry run key detection]

LOOKUPS: Create IOC Lookups
----------------------------
1. Create lookup: apt-x-ioc-domains
   - Contains: evil-apt-x.com
   - Metadata: {"threat": "APT-X Campaign", "severity": "critical"}

2. Create lookup: apt-x-ioc-ips
   - Contains: 203.0.113.50
   - Metadata: {"threat": "APT-X Campaign", "severity": "high"}

RULE 3: Domain Lookup
----------------------
Step 1 - Generate detection:
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="Detect DNS requests where domain matches apt-x-ioc-domains lookup"
)

Step 2 - Generate response:
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="Report with priority 9, add threat-detected tag with 7 day TTL"
)

Step 3 - Validate and create

Ask user for confirmation:
"I've generated 3 D&R rules and 2 lookups using AI tools. All rules have been validated.
Proceed with creating these detections? (yes/no)"

After user confirms, create each resource and report success.
```

## Final Report Structure

After completing all steps, provide a comprehensive report:

```markdown
# Threat Report Evaluation: [Report Name]
Date: [YYYY-MM-DD]
Organization: [OID]
Analyst: Claude AI

## Executive Summary
[Brief summary of findings]

## Platform Coverage
- Platforms in report: [list]
- Platforms available: [list]
- Platforms investigated: [list]

## IOC Search Results
### Hashes
- [hash]: [status]

### Domains
- [domain]: [status]

### IP Addresses
- [IP]: [status]

### File Paths
- [path]: [status]

## Behavioral Indicators
### Behavior 1: [Name]
- Query: [LCQL]
- Results: [count and status]
- Refinements: [if any]

### Behavior 2: [Name]
...

## Detections Created
### D&R Rules
1. [rule-name]: [description]
2. [rule-name]: [description]

### Lookups
1. [lookup-name]: [IOC count and types]
2. [lookup-name]: [IOC count and types]

## Affected Sensors
- [sensor-id / hostname]: [reason]

## Recommendations
1. [Action item 1]
2. [Action item 2]

## Next Steps
- Monitor detections for [X days]
- Investigate flagged sensors: [list]
- Review and tune rules for false positives
```

## Key Reminders

1. **Never fabricate data** - Work only with report content and org data
2. **Always ask for confirmation** - Before creating any LC resources
3. **Document refinements** - Track all query/rule adjustments
4. **Analyze prevalence** - Distinguish targeted attacks from noise
5. **ALWAYS use AI generation - NEVER manually write rules**
   - Use `generate-dr-rule-detection` for ALL detection components
   - Use `generate-dr-rule-respond` for ALL response components
   - Use `generate-lcql-query` for ALL LCQL queries
   - AI ensures correct syntax and validates against org schema
   - AI includes rich metadata (MITRE ATT&CK, remediation, references)
   - Manual YAML writing leads to syntax errors and missing validation
6. **Validate before creating** - Use `validate-dr-rule-components` for every rule
7. **Provide complete reports** - Include all findings and actions

## Additional Resources

- LimaCharlie Docs: `./docs/limacharlie/doc/`
- Detection & Response: `./docs/limacharlie/doc/Detection_and_Response/`
- LCQL Examples: `./docs/limacharlie/doc/Query_Console/lcql-examples.md`
- IOC Search: Via `search-iocs` and `batch-search-iocs` functions
- Platform List: Via `get-platform-names` function
- Lookup Format: `./docs/limacharlie/doc/Platform_Management/Config_Hive/config-hive-lookups.md`
- D&R Rules: `./docs/limacharlie/doc/Detection_and_Response/writing-and-testing-rules.md`

## Troubleshooting

**Problem**: IOC search returns too many results
**Solution**: This may indicate a weak IOC. Document as "ubiquitous" and consider excluding from detections.

**Problem**: LCQL query returns errors
**Solution**: Use lookup-lc-doc skill to search for LCQL syntax documentation and examples.

**Problem**: D&R rule validation fails
**Solution**: The AI-generated rule has a syntax error. DO NOT manually fix the YAML. Instead:
1. Review the validation error message
2. Refine your prompt to be more specific
3. Re-generate using the AI tool with the improved prompt
4. If repeatedly failing, consult `./docs/limacharlie/doc/Detection_and_Response/Reference/detection-logic-operators.md` and improve your prompt based on correct operators

**Problem**: AI-generated rule doesn't match expected behavior
**Solution**: Refine your prompt, don't manually edit the YAML:
1. Be more specific about event types and field paths
2. Add examples to your prompt: "like NETWORK_CONNECTIONS events"
3. Specify exact operators: "using the lookup operator"
4. Re-generate with the improved prompt
5. Review the "Writing Effective AI Generation Prompts" section above

**Problem**: AI-generated rule is too broad/noisy
**Solution**: Refine the detection prompt to be more specific:
1. Add platform filters: "on Windows systems only"
2. Add exclusions: "excluding known-good processes like svchost.exe"
3. Add additional conditions: "and the command line contains suspicious keywords"
4. Re-generate the detection component

**Problem**: Lookup creation fails
**Solution**: Verify JSON format matches the lookup_data structure in config-hive-lookups.md

**Problem**: Platform not found in organization
**Solution**: Skip that platform's IOCs/behaviors. Document in report that platform was not available for investigation.

**Problem**: Manually wrote a D&R rule and it's not working
**Solution**: Delete the manual rule and use AI generation instead:
1. Use `generate-dr-rule-detection` with a clear prompt
2. Use `generate-dr-rule-respond` with specific requirements
3. Use `validate-dr-rule-components` before creating
4. Manual YAML writing is error-prone and not supported by this workflow
