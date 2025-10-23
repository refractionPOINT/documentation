# Managed Rulesets - Complete Reference

This document provides complete API documentation, configuration details, and advanced features for all managed ruleset types.

[Back to Quick Start](SKILL.md)

## Table of Contents

- [Sigma Conversion API](#sigma-conversion-api)
- [Soteria EDR Details](#soteria-edr-details)
- [Soteria AWS Details](#soteria-aws-details)
- [Soteria M365 Details](#soteria-m365-details)
- [SOC Prime Configuration](#soc-prime-configuration)
- [Community Rules Sources](#community-rules-sources)
- [False Positive Rules](#false-positive-rules)
- [Rule Versioning](#rule-versioning)
- [Ruleset Selection Guide](#ruleset-selection-guide)
- [Best Practices Detailed](#best-practices-detailed)

## Sigma Conversion API

### Overview

The Sigma Converter service translates Sigma rules (YAML format) into LimaCharlie Detection & Response (D&R) rules. The service is accessible at `https://sigma.limacharlie.io/`.

### Convert Single Rule Endpoint

**Endpoint**: `https://sigma.limacharlie.io/convert/rule`
**Method**: POST
**Content-Type**: `application/x-www-form-urlencoded`

**Parameters**:
- `rule` (required): The content of a Sigma rule in YAML format
- `target` (optional): Target type, either `edr` or `artifact` (default: `edr`)

**Example using CURL**:
```bash
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@my-sigma-rule.yaml"
```

**Example with target parameter**:
```bash
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@my-sigma-rule.yaml" \
  -d "target=artifact"
```

**Response Format**:
```json
{
  "rule": "detect:\n  events:\n  - NEW_PROCESS\n  - EXISTING_PROCESS\n  op: and\n  rules:\n  - op: is windows\n  - op: or\n    rules:\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: domainlist\nrespond:\n- action: report\n  metadata:\n    author: Original Author\n    description: Rule description\n  name: Rule Name\n"
}
```

**Extracting the Rule**:
```bash
# Save response to file
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@sigma-rule.yaml" > response.json

# Extract rule content
cat response.json | jq -r '.rule' > lc-rule.yaml
```

### Convert Repository Endpoint

**Endpoint**: `https://sigma.limacharlie.io/convert/repo`
**Method**: POST
**Content-Type**: `application/x-www-form-urlencoded`

**Parameters**:
- `repo` (required): Source location, can be:
  - Direct HTTPS link: `https://corp.com/my-rules.yaml`
  - GitHub file: `https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/proc_creation_win_ad_find_discovery.yml`
  - GitHub directory: `https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation`
  - Authenticated Resource Locator (ARL)
- `target` (optional): Target type, either `edr` or `artifact` (default: `edr`)

**Example using CURL**:
```bash
# Convert directory of rules
curl -X POST https://sigma.limacharlie.io/convert/repo \
  -d "repo=https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation"

# Convert with artifact target
curl -X POST https://sigma.limacharlie.io/convert/repo \
  -d "repo=https://github.com/SigmaHQ/sigma/blob/master/rules/linux" \
  -d "target=artifact"
```

**Response Format**:
```json
{
  "rules": [
    {
      "file": "https://raw.githubusercontent.com/SigmaHQ/sigma/master/rules/windows/process_creation/proc_creation_win_ad_find_discovery.yml",
      "rule": "detect:\n  events:\n  - NEW_PROCESS\n..."
    },
    {
      "file": "https://raw.githubusercontent.com/SigmaHQ/sigma/master/rules/windows/process_creation/proc_creation_win_susp_cmd.yml",
      "rule": "detect:\n  events:\n  - NEW_PROCESS\n..."
    }
  ]
}
```

**Processing Multiple Rules**:
```bash
# Convert and extract all rules
curl -X POST https://sigma.limacharlie.io/convert/repo \
  -d "repo=https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation" \
  > rules.json

# Extract individual rules with jq
cat rules.json | jq -r '.rules[] | .rule' > all-rules.yaml

# Or process each rule separately
cat rules.json | jq -c '.rules[]' | while read rule; do
  file=$(echo $rule | jq -r '.file' | sed 's/.*\///' | sed 's/.yml$//')
  echo $rule | jq -r '.rule' > "rule-${file}.yaml"
done
```

### Sigma Target Types

**EDR Target** (`target=edr`):
- For endpoint detection on sensor events
- Processes events like: NEW_PROCESS, FILE_CREATE, NETWORK_CONNECTIONS, REGISTRY_WRITE
- Default target type
- Best for real-time endpoint monitoring

**Artifact Target** (`target=artifact`):
- For artifact collection and log analysis
- Processes collected logs and forensic data
- Best for historical analysis and log aggregation
- Used with artifact collection rules

### SigmaHQ Repository

LimaCharlie maintains a repository of pre-converted Sigma rules from the official SigmaHQ repository:

**Repository**: https://github.com/refractionPOINT/sigma-limacharlie/tree/rules

**Benefits**:
- Pre-converted rules ready to deploy
- Regularly updated from SigmaHQ
- Organized by platform and category
- Can be applied with one click or via IaC

**Usage**:
```bash
# Clone the repository
git clone https://github.com/refractionPOINT/sigma-limacharlie.git
cd sigma-limacharlie/rules

# Deploy specific rules
limacharlie dr add --rule-name sigma-suspicious-cmd \
  --rule-file windows/process_creation/proc_creation_win_susp_cmd.yaml
```

### Sigma Conversion Best Practices

1. **Review converted rules**: Always review the output before deployment
2. **Validate syntax**: Use `limacharlie replay --validate` to check syntax
3. **Test with replay**: Test against historical data before production
4. **Check event availability**: Ensure required events are configured
5. **Optimize performance**: Put restrictive conditions first
6. **Add context**: Include metadata about the original Sigma rule
7. **Version control**: Store converted rules in Git
8. **Namespace organization**: Use prefixes like `sigma-windows-*`

## Soteria EDR Details

### Overview

Soteria EDR rules provide comprehensive managed detection coverage for endpoints across Windows, Linux, and macOS platforms. Rules are maintained by Soteria and automatically updated.

### Key Characteristics

- **Managed service**: You cannot view or edit the rules
- **No data access**: Soteria doesn't access your data (LimaCharlie acts as broker)
- **Automatic updates**: Rules updated by Soteria team
- **Professional maintenance**: Expert-curated detections
- **MITRE ATT&CK aligned**: Full framework coverage

### Required Events

The following events must be configured in your organization for Soteria EDR rules to function properly:

- `CODE_IDENTITY` - Code signing and identity information
- `DNS_REQUEST` - DNS query events
- `EXISTING_PROCESS` - Snapshot of running processes
- `FILE_CREATE` - File creation events
- `FILE_MODIFIED` - File modification events
- `MODULE_LOAD` - DLL/library loading events
- `NETWORK_CONNECTIONS` - Network connection events
- `NEW_DOCUMENT` - Document creation events
- `NEW_NAMED_PIPE` - Named pipe creation events
- `NEW_PROCESS` - Process creation events
- `REGISTRY_WRITE` - Registry write operations
- `REGISTRY_CREATE` - Registry key creation
- `SENSITIVE_PROCESS_ACCESS` - Access to sensitive processes
- `THREAD_INJECTION` - Thread injection detection

**Configuring Events**:
1. Events are automatically suggested during Soteria subscription
2. Can be manually configured in **Artifact Collection** page
3. Apply events to installation keys or specific sensors
4. Monitor event volume in **Sensors** page

### MITRE ATT&CK Coverage

Soteria EDR provides extensive MITRE ATT&CK coverage. View dynamic coverage maps:

**All Platforms**:
https://mitre-attack.github.io/attack-navigator/#layerURL=https%3A%2F%2Fstorage.googleapis.com%2Fsoteria-detector-mapping%2F%2Fall.json

**Windows**:
https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//windows.json

**Linux**:
https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//linux.json

**macOS**:
https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//mac.json

### Deployment Methods

**Via Web UI**:
1. Navigate to **Add-On Marketplace**
2. Go to **Extensions** section
3. Search for "Soteria" or select `soteria-rules-edr`
4. Select the organization from the dropdown
5. Click **Subscribe**
6. Review and enable required events
7. Manage subscription from **Billing > Subscriptions**

**Via Infrastructure as Code**:
```yaml
# hive.yaml example
extensions:
  soteria-rules-edr:
    enabled: true
```

### Subscription Management

**Check Subscription Status**:
1. Navigate to **Billing > Subscriptions**
2. View active Soteria subscriptions
3. Check renewal dates and pricing

**Unsubscribe**:
1. Navigate to **Billing > Subscriptions**
2. Find `soteria-rules-edr`
3. Click **Cancel Subscription**
4. Confirm cancellation

**Multi-Organization Management**:
- Subscribe each organization individually
- Use IaC for consistent deployment
- Track costs per organization
- Consider consolidated billing

### Tuning Soteria EDR

Since you cannot edit Soteria rules directly, use False Positive rules:

1. **Identify false positives** from detections
2. **Create FP rules** to filter unwanted detections
3. **Use specific conditions** to avoid over-filtering
4. **Document reasoning** for each FP rule
5. **Review periodically** as rules are updated

## Soteria AWS Details

### Overview

Soteria AWS rules provide managed threat detection for AWS environments using CloudTrail and GuardDuty telemetry.

### Supported AWS Services

**AWS CloudTrail**:
- API activity monitoring
- Account activity tracking
- Resource change tracking
- Compliance logging

**AWS GuardDuty**:
- Threat intelligence feeds
- Machine learning anomaly detection
- Attack pattern recognition
- Security findings

### Prerequisites

1. **AWS CloudTrail Adapter**:
   - Configure CloudTrail in AWS account
   - Set up S3 bucket for logs
   - Configure LimaCharlie CloudTrail adapter
   - Verify log ingestion

2. **AWS GuardDuty Adapter**:
   - Enable GuardDuty in AWS account
   - Configure findings export
   - Set up LimaCharlie GuardDuty adapter
   - Verify findings ingestion

3. **TOR Lookup**:
   - Subscribe to `tor` extension (free)
   - Required for TOR IP detection

4. **Soteria AWS Subscription**:
   - Subscribe to `soteria-rules-aws`
   - Verify subscription is active

### CloudTrail Adapter Configuration

**Setup Steps**:
1. Navigate to **Integrations** in LimaCharlie
2. Select **AWS CloudTrail**
3. Provide AWS credentials or role ARN
4. Configure S3 bucket location
5. Set ingestion frequency
6. Test connection
7. Enable adapter

**Required AWS Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-cloudtrail-bucket/*",
        "arn:aws:s3:::your-cloudtrail-bucket"
      ]
    }
  ]
}
```

### GuardDuty Adapter Configuration

**Setup Steps**:
1. Navigate to **Integrations** in LimaCharlie
2. Select **AWS GuardDuty**
3. Provide AWS credentials or role ARN
4. Configure findings export
5. Set ingestion frequency
6. Test connection
7. Enable adapter

**Required AWS Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "guardduty:GetFindings",
        "guardduty:ListFindings"
      ],
      "Resource": "*"
    }
  ]
}
```

### Deployment

**Via Web UI**:
1. Ensure CloudTrail and GuardDuty adapters are configured
2. Navigate to **Add-On Marketplace**
3. Subscribe to `tor` extension (if not already subscribed)
4. Subscribe to `soteria-rules-aws`
5. Verify subscription in **Billing > Subscriptions**

**Via Infrastructure as Code**:
```yaml
# hive.yaml example
extensions:
  tor:
    enabled: true
  soteria-rules-aws:
    enabled: true

integrations:
  aws-cloudtrail:
    enabled: true
    bucket: your-cloudtrail-bucket
    region: us-east-1
  aws-guardduty:
    enabled: true
    region: us-east-1
```

## Soteria M365 Details

### Overview

Soteria M365 rules provide managed threat detection for Microsoft 365 environments, monitoring user activity and security events across M365 applications.

### Supported M365 Applications

- **Teams**: Chat, calls, meetings, file sharing
- **Word**: Document creation, editing, sharing
- **Excel**: Spreadsheet activity
- **PowerPoint**: Presentation activity
- **Outlook**: Email and calendar activity
- **OneDrive**: File storage and sharing
- **SharePoint**: Collaboration and content management
- **Other M365 Apps**: Full suite coverage

### Prerequisites

1. **Office 365 Adapter**:
   - Configure O365 audit log collection
   - Set up LimaCharlie O365 adapter
   - Verify log ingestion

2. **TOR Lookup**:
   - Subscribe to `tor` extension (free)
   - Required for TOR IP detection

3. **Soteria M365 Subscription**:
   - Subscribe to `soteria-rules-o365`
   - Verify subscription is active

### Office 365 Adapter Configuration

**Setup Steps**:
1. Navigate to **Integrations** in LimaCharlie
2. Select **Office 365**
3. Authenticate with M365 admin account
4. Grant required permissions
5. Configure log types to collect
6. Set ingestion frequency
7. Test connection
8. Enable adapter

**Required M365 Permissions**:
- Global Administrator or Security Administrator role
- Access to Office 365 Management API
- Audit log search enabled in M365

**Audit Log Types**:
- Exchange (email activity)
- SharePoint (file and site activity)
- Azure Active Directory (authentication and user activity)
- DLP events (data loss prevention)
- Security and Compliance Center events

### Deployment

**Via Web UI**:
1. Ensure Office 365 adapter is configured
2. Navigate to **Add-On Marketplace**
3. Subscribe to `tor` extension (if not already subscribed)
4. Subscribe to `soteria-rules-o365`
5. Verify subscription in **Billing > Subscriptions**

**Via Infrastructure as Code**:
```yaml
# hive.yaml example
extensions:
  tor:
    enabled: true
  soteria-rules-o365:
    enabled: true

integrations:
  office365:
    enabled: true
    tenant_id: your-tenant-id
    log_types:
      - Exchange
      - SharePoint
      - AzureActiveDirectory
```

### Common M365 Detection Scenarios

Soteria M365 rules cover:
- Impossible travel scenarios
- Suspicious login patterns
- Mass file downloads
- External file sharing anomalies
- Email forwarding rules
- Privilege escalation
- Data exfiltration attempts
- Compliance violations

## SOC Prime Configuration

### Overview

SOC Prime provides a platform for threat detection content with continuous updates. The integration synchronizes detection rules from SOC Prime content lists to LimaCharlie every 3 hours.

### Prerequisites

**SOC Prime Account**:
- Free accounts cannot access the API
- Trial or paid subscription required
- API access enabled

**API Key**:
- Generated from SOC Prime platform
- Required for LimaCharlie integration
- Keep secure and rotate periodically

**Content Lists**:
- Create and configure in SOC Prime platform
- Organize detections by use case
- Can have multiple lists

### Content List Configuration

**In SOC Prime Platform**:
1. Log into SOC Prime platform
2. Navigate to **Content Management**
3. Create a new list or use existing
4. Add detection rules to the list
5. Configure list settings
6. Generate API key (if not already done)

**Learn More**:
https://socprime.com/blog/enable-continuous-content-management-with-the-soc-prime-platform/

### LimaCharlie Integration Setup

**Step 1: Enable the Add-on**
1. Navigate to **Add-On Marketplace** in LimaCharlie
2. Search for "SOC Prime"
3. Enable the `socprime` add-on

**Step 2: Configure Integration**
1. Go to **Integrations** page
2. Select **SOC Prime**
3. Enter your API key
4. Click **Update**

**Step 3: Select Content Lists**
1. After saving API key, available lists will load
2. Select the lists you want to synchronize
3. Click **Update** to save selection

**Step 4: Verify Sync**
1. Wait for initial sync (up to 3 hours)
2. Check **D&R Rules** for rules with `socprime` author
3. Monitor **Detections** for SOC Prime alerts

### Sync Behavior

**Sync Frequency**: Every 3 hours

**What Gets Synchronized**:
- New rules added to selected lists
- Updates to existing rules
- Rule metadata and tags
- MITRE ATT&CK mappings

**What Doesn't Sync**:
- Rules removed from lists (remain in LimaCharlie until manually deleted)
- Disabled rules (you must disable manually in LimaCharlie)
- Custom modifications (rules are overwritten on sync)

**Attribution**:
- All detections show `socprime` as author
- Original rule metadata preserved
- SOC Prime rule ID included

### Managing SOC Prime Rules

**View SOC Prime Rules**:
```bash
# List all SOC Prime rules
limacharlie dr list | grep socprime
```

**Disable Specific Rules**:
1. Create False Positive rule matching the detection name
2. Or remove the rule entirely (will return on next sync if still in list)

**Update Content Lists**:
1. Modify lists in SOC Prime platform
2. Changes sync within 3 hours
3. No action needed in LimaCharlie

**Troubleshooting Sync Issues**:
1. Verify API key is valid
2. Check SOC Prime subscription status
3. Ensure content lists have rules
4. Wait for next sync cycle
5. Check LimaCharlie logs for errors

### API Key Management

**Generate API Key**:
1. Log into SOC Prime platform
2. Navigate to **Settings** > **API Access**
3. Generate new key
4. Copy and store securely

**Rotate API Key**:
1. Generate new key in SOC Prime
2. Update key in LimaCharlie integration
3. Revoke old key in SOC Prime

**Security Best Practices**:
- Rotate keys periodically (every 90 days)
- Store in secure credential management system
- Use separate keys for different environments
- Monitor API usage in SOC Prime

## Community Rules Sources

### Overview

Community Rules leverage AI to convert detection rules from various third-party sources into LimaCharlie D&R format. The AI conversion process analyzes the original rule logic and translates it to LimaCharlie syntax.

### Supported Sources

**Anvilogic**:
- Cloud and endpoint detections
- AWS, Azure, GCP coverage
- Threat hunting rules
- Compliance detections

**Sigma**:
- SigmaHQ community rules (alternative to converter API)
- Thousands of community-contributed rules
- Platform-agnostic format
- Extensive Windows coverage

**Panther**:
- Cloud security detections
- AWS, GCP, Okta rules
- SIEM and log analysis rules
- Compliance frameworks

**Okta**:
- Identity and access management
- Authentication detections
- Account compromise indicators
- Suspicious login patterns

### Search Capabilities

**By CVE Number**:
- Search: `CVE-2023-1234`
- Finds rules detecting specific vulnerabilities
- Useful for rapid response to new CVEs

**By Keyword**:
- Search: `ransomware`, `mimikatz`, `lateral movement`
- Broad search across rule descriptions
- Finds related detections

**By MITRE ATT&CK**:
- Search: `T1059` (Command and Scripting Interpreter)
- Filter by technique ID
- Map coverage to ATT&CK framework

**By Tag**:
- Platform tags: `windows`, `linux`, `aws`, `azure`
- Technique tags: `credential-access`, `defense-evasion`
- Source tags: `sigma`, `panther`, `anvilogic`

### Conversion Process

**AI Conversion Steps**:
1. Parse original rule syntax
2. Identify detection logic and conditions
3. Map to LimaCharlie event types
4. Translate operators and paths
5. Generate respond actions
6. Add explanatory comments

**Conversion Quality**:
- Generally high quality for common patterns
- May require adjustment for complex rules
- Comments explain conversion decisions
- Test thoroughly before production use

**Limitations**:
- Complex aggregations may not convert perfectly
- Some source-specific features may be lost
- Conversion can be inconsistent (AI-based)
- Always review and test converted rules

### Rule Details Available

**Source Code**:
- View original rule in source format
- Compare with converted LimaCharlie version
- Understand original intent

**Licensing**:
- View license information
- Ensure compliance with terms
- Some rules require attribution

**References**:
- Links to original source
- Related documentation
- CVE references
- Blog posts and advisories

**Metadata**:
- Original author
- MITRE ATT&CK techniques
- Platforms supported
- Severity/confidence ratings

### Customization After Conversion

**Review Detect Logic**:
- Check event types are available
- Verify paths match your data
- Adjust operators if needed
- Add organization-specific conditions

**Review Respond Actions**:
- Customize alert severity
- Add organization-specific metadata
- Configure outputs and integrations
- Add suppression if needed

**Add False Positive Filtering**:
- Exclude known-good activity
- Add environment-specific exceptions
- Use FP rules for global filtering

**Test Thoroughly**:
- Validate syntax
- Test with replay against historical data
- Monitor initial detections
- Refine based on results

### Best Practices

1. **Always review converted rules**: Don't blindly deploy
2. **Test with replay**: Use historical data to validate
3. **Check licensing**: Ensure compliance
4. **Add context**: Include comments about customizations
5. **Monitor performance**: Some rules may need optimization
6. **Version control**: Store in Git with conversion notes
7. **Report issues**: Help improve conversion quality

## False Positive Rules

### Overview

False Positive (FP) rules filter unwanted detections globally across all D&R rules. They apply after detections are generated by `report` actions and can prevent alert fatigue by suppressing known-good activity.

### How FP Rules Work

1. D&R rule generates a detection (via `report` action)
2. FP rules evaluate the detection
3. If FP rule matches, detection is suppressed
4. If no FP rules match, detection is recorded

### FP Rule Structure

FP rules use the same operator syntax as D&R rules but match against detection content rather than raw events.

**Basic Structure**:
```yaml
op: <operator>
path: <field-path>
value: <match-value>
```

**Available Fields**:
- `cat`: Detection name/category
- `detect/*`: Original event fields (use `detect/event/FIELD_NAME`)
- `routing/*`: Routing information (hostname, IP, sensor ID, etc.)
- `metadata/*`: Detection metadata

### Common FP Rule Patterns

**Suppress Specific Detection**:
```yaml
op: is
path: cat
value: my-detection-name
```

**Suppress for Specific File**:
```yaml
op: ends with
path: detect/event/FILE_PATH
value: legitimate-tool.exe
case sensitive: false
```

**Suppress for Specific Host**:
```yaml
op: is
path: routing/hostname
value: build-server-01
```

**Suppress for Multiple Hosts**:
```yaml
op: or
rules:
  - op: is
    path: routing/hostname
    value: dev-server-1
  - op: is
    path: routing/hostname
    value: dev-server-2
  - op: is
    path: routing/hostname
    value: test-server-1
```

**Suppress by IP Address**:
```yaml
op: is
path: routing/ext_ip
value: 203.0.113.10
```

**Suppress by Command Line Pattern**:
```yaml
op: contains
path: detect/event/COMMAND_LINE
value: /path/to/known/script.sh
case sensitive: false
```

**Suppress by File Path and Detection**:
```yaml
op: and
rules:
  - op: is
    path: cat
    value: suspicious-process-creation
  - op: ends with
    path: detect/event/FILE_PATH
    value: approved-automation.exe
    case sensitive: false
```

**Suppress by User**:
```yaml
op: is
path: detect/event/USER_NAME
value: service-account
case sensitive: false
```

**Suppress by Parent Process**:
```yaml
op: and
rules:
  - op: is
    path: cat
    value: my-detection
  - op: contains
    path: detect/event/PARENT/FILE_PATH
    value: jenkins
    case sensitive: false
```

### Expiry Dates

FP rules can have expiration dates for temporary exclusions.

**Use Cases**:
- Maintenance windows
- Known testing periods
- Temporary deployments
- Scheduled activities

**Setting Expiry**:
1. Create or edit FP rule in UI
2. Set expiry date/time
3. Date must be in user's local timezone (not UTC)
4. Rule automatically disabled after expiry

**Example Scenario**:
```yaml
# Suppress during deployment window (set expiry in UI)
op: and
rules:
  - op: is
    path: cat
    value: unauthorized-software-installation
  - op: is
    path: routing/hostname
    value: app-server-prod-1
```

### Advanced FP Patterns

**Combine Multiple Conditions**:
```yaml
op: and
rules:
  - op: is
    path: cat
    value: lateral-movement-detected
  - op: or
    rules:
      - op: contains
        path: routing/hostname
        value: -dev-
        case sensitive: false
      - op: contains
        path: routing/hostname
        value: -test-
        case sensitive: false
```

**Regex Matching** (use `matches` operator):
```yaml
op: matches
path: detect/event/FILE_PATH
re: ^C:\\Program Files\\Company\\.*\\.exe$
```

**Nested Event Access**:
```yaml
# For detections from rules that access nested event data
op: contains
path: detect/event/PARENT/PARENT/FILE_PATH
value: grandparent-process.exe
case sensitive: false
```

### FP Rule Best Practices

1. **Be specific**: Make rules as narrow as possible to avoid over-suppression
2. **Use expiry dates**: For temporary exclusions (maintenance, testing)
3. **Document reasoning**: Use clear rule names explaining why
4. **Regular review**: Periodically review and remove outdated FP rules
5. **Test impact**: Verify FP rules don't suppress real threats
6. **Prefer tuning**: When possible, tune the D&R rule instead of using FP
7. **Combine conditions**: Use AND logic to make rules more specific
8. **Monitor metrics**: Track how many detections each FP rule suppresses

### Managing FP Rules

**Via Web UI**:
1. Navigate to **Automation > False Positive Rules**
2. View all active FP rules
3. Click rule to edit or delete
4. Add new rule with **New Rule** button

**Via CLI**:
```bash
# FP rules are managed through the REST API
# No direct CLI commands, but can use API calls
```

**Via API**:
```bash
# List FP rules
curl -X GET https://api.limacharlie.io/v1/org/{oid}/fp \
  -H "Authorization: Bearer {api-key}"

# Add FP rule
curl -X POST https://api.limacharlie.io/v1/org/{oid}/fp \
  -H "Authorization: Bearer {api-key}" \
  -d '{"name": "my-fp-rule", "rule": {...}}'

# Delete FP rule
curl -X DELETE https://api.limacharlie.io/v1/org/{oid}/fp/{rule-name} \
  -H "Authorization: Bearer {api-key}"
```

### Troubleshooting FP Rules

**FP Rule Not Working**:
1. Check path syntax (use exact field names from detection)
2. Verify case sensitivity settings
3. Test with single condition first, then add complexity
4. Check for typos in values
5. Ensure rule is enabled and not expired

**Too Many Detections Suppressed**:
1. Review FP rule conditions (may be too broad)
2. Add more specific conditions
3. Remove overly generic FP rules
4. Monitor FP rule hit counts

**Can't Access Event Fields**:
1. Use `detect/event/FIELD_NAME` prefix
2. Check detection structure in Timeline
3. Verify field exists in the detection
4. Check field name capitalization

## Rule Versioning

### Version Control with Git

Store all rules in version control for tracking changes and collaboration.

**Repository Structure**:
```
rules/
  sigma/
    windows/
      process-creation/
        rule1.yaml
        rule2.yaml
    linux/
      process-creation/
        rule1.yaml
  custom/
    ransomware/
      rule1.yaml
    lateral-movement/
      rule1.yaml
  fp-rules/
    global.yaml
    dev-environment.yaml
```

**Commit Messages**:
```bash
git commit -m "Add Sigma rule for credential dumping (T1003)"
git commit -m "Tune ransomware rule - reduce false positives"
git commit -m "Add FP rule for Jenkins build servers"
```

### Rule Metadata for Versioning

Include version information in rule metadata:

```yaml
detect:
  # ... detection logic
respond:
  - action: report
    name: my-detection
    metadata:
      version: "1.2.0"
      author: "Security Team"
      created: "2024-01-15"
      modified: "2024-03-20"
      changelog: "Added parent process check to reduce FPs"
      mitre_attack: "T1059.001"
```

### Infrastructure as Code (IaC)

Use LimaCharlie's IaC functionality for versioned deployments:

**hive.yaml Example**:
```yaml
rules:
  sigma-suspicious-cmd:
    detect:
      events:
        - NEW_PROCESS
      op: and
      rules:
        - op: is windows
        - op: contains
          path: event/COMMAND_LINE
          value: "suspicious-pattern"
    respond:
      - action: report
        name: sigma-suspicious-cmd
        metadata:
          version: "1.0.0"
          source: "sigma"
```

**Deployment**:
```bash
# Deploy rules from IaC config
limacharlie configs push --hive hive.yaml

# Or use directory sync
limacharlie configs sync --dir ./configs
```

### Backup and Export

**Export All Rules**:
```bash
# Export to JSON
limacharlie dr list --format json > rules-backup-$(date +%Y%m%d).json

# Export to YAML (requires jq and yq)
limacharlie dr list --format json | jq -r '.[] | .rule' > rules-backup.yaml
```

**Automated Backups**:
```bash
#!/bin/bash
# backup-rules.sh
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

limacharlie dr list --format json > "$BACKUP_DIR/rules-$DATE.json"
git -C $BACKUP_DIR add .
git -C $BACKUP_DIR commit -m "Automated backup $DATE"
git -C $BACKUP_DIR push
```

### Change Management

**Before Deploying Changes**:
1. Export current rules (backup)
2. Test new rule with replay
3. Deploy to staging/test organization first
4. Monitor for 24-48 hours
5. Deploy to production
6. Commit to version control

**Rollback Procedure**:
```bash
# Remove problematic rule
limacharlie dr remove --rule-name problematic-rule

# Restore from backup
cat rules-backup.json | jq -r '.[] | select(.name=="good-rule") | .rule' > restore.yaml
limacharlie dr add --rule-name good-rule --rule-file restore.yaml
```

## Ruleset Selection Guide

### Decision Matrix

Choose rulesets based on your organization's needs:

| Criteria | Sigma | Soteria EDR | Soteria AWS | Soteria M365 | SOC Prime | Community |
|----------|-------|-------------|-------------|--------------|-----------|-----------|
| **Cost** | Free | Paid | Paid | Paid | Paid* | Free |
| **Maintenance** | Manual | Auto | Auto | Auto | Auto | Manual |
| **Customization** | Full | None | None | None | Full | Full |
| **Coverage Breadth** | Wide | Deep | Focused | Focused | Variable | Variable |
| **Update Frequency** | Community | Continuous | Continuous | Continuous | 3 hours | Manual |
| **Rule Visibility** | Full | None | None | None | Full | Full |
| **Best For** | Custom/Open | EDR | AWS | M365 | Enterprise | Specific |

*Requires separate SOC Prime subscription

### Selection by Use Case

**New Organization, Limited Budget**:
1. Start with Sigma rules (free)
2. Add Community Rules for specific threats
3. Create custom rules as needed
4. Consider Soteria when budget allows

**Enterprise with Security Team**:
1. Deploy Soteria EDR for baseline
2. Add SOC Prime for content management
3. Supplement with custom Sigma rules
4. Use Community Rules for rapid response

**AWS-Heavy Environment**:
1. Soteria AWS for managed coverage
2. Sigma AWS rules for customization
3. Custom rules for org-specific AWS policies
4. Community Rules for AWS vulnerabilities

**M365-Focused Organization**:
1. Soteria M365 for managed coverage
2. Custom rules for org-specific policies
3. Community Rules for M365-specific threats

**MSSP/Multi-Tenant**:
1. Soteria EDR as baseline for all clients
2. SOC Prime for content management
3. Sigma/Community for client-specific needs
4. IaC for consistent deployment
5. Client-specific FP rules

### Coverage Overlap Considerations

**Sigma + Soteria EDR**:
- Some overlap in common threat detection
- Sigma provides visibility and customization
- Soteria provides expert maintenance
- Use both for defense in depth

**SOC Prime + Other Sources**:
- SOC Prime may include Sigma-based rules
- Check for duplicates by detection name
- Use namespacing to organize
- Disable duplicates via FP rules if needed

**Multiple Soteria Subscriptions**:
- EDR + AWS: No overlap (different telemetry)
- EDR + M365: No overlap (different telemetry)
- All three provide comprehensive coverage

## Best Practices Detailed

### Deployment Approach

**Phase 1: Planning (Week 1)**
- Assess environment and requirements
- Choose appropriate rulesets
- Plan phased rollout
- Set up test organization
- Configure required integrations

**Phase 2: Testing (Week 2-3)**
- Deploy to test organization
- Use replay against historical data
- Monitor for false positives
- Create initial FP rules
- Tune thresholds and conditions

**Phase 3: Limited Production (Week 4-5)**
- Deploy to subset of production
- Monitor closely for 48 hours
- Refine FP rules based on real data
- Document common false positives
- Prepare runbooks for analysts

**Phase 4: Full Production (Week 6+)**
- Deploy to all production systems
- Continue monitoring and tuning
- Regular review of detection quality
- Track metrics (detection rate, FP rate)
- Continuous improvement

### Rule Tuning Process

**Baseline Period (1-2 weeks)**:
- Deploy rules in monitoring mode
- Collect detections without alerting
- Analyze patterns and frequencies
- Identify false positive sources
- Document legitimate activity

**Categorization**:
- **True Positives**: Actual threats or policy violations
- **False Positives**: Legitimate business activity
- **Benign True Positives**: Matches rule but not threat
- **Noise**: High-volume low-value detections

**Tuning Actions**:
- Create FP rules for legitimate activity
- Add suppression for noisy rules
- Tune thresholds (count, time windows)
- Add context to improve precision
- Disable ineffective rules

**Iteration**:
- Measure false positive rate weekly
- Track time to triage per alert
- Monitor analyst feedback
- Adjust rules based on changes
- Quarterly comprehensive review

### Performance Optimization

**Rule Design**:
- Put restrictive conditions first
- Use specific event types
- Avoid overly broad wildcards
- Limit complex nested conditions
- Test performance with replay metrics

**Rule Management**:
- Don't deploy all rules at once
- Start with high-priority threats
- Disable unused or ineffective rules
- Use namespaces for organization
- Archive old rules instead of deleting

**Suppression Strategy**:
- Use suppression for time-based rules
- Configure appropriate windows
- Avoid over-suppressing
- Monitor suppression hit counts
- Review suppression effectiveness

**Resource Monitoring**:
```bash
# Test rule performance
limacharlie replay --rule-content rule.yaml \
  --entire-org --last-seconds 3600 --metrics

# Monitor overall rule performance
# Check evaluation times in rule metrics
```

### Multi-Organization Management

**Template Architecture**:
```
templates/
  base/
    hive.yaml                 # Common rules for all orgs
    soteria-edr.yaml         # Soteria subscription config
    fp-rules/
      common.yaml            # FP rules for all orgs
  overlays/
    client-a/
      hive.yaml              # Client-specific rules
      fp-rules.yaml          # Client-specific FP rules
    client-b/
      hive.yaml
      fp-rules.yaml
```

**Deployment Script**:
```bash
#!/bin/bash
# deploy-rules.sh

ORG_ID=$1
OVERLAY=$2

# Deploy base rules
limacharlie configs push --oid $ORG_ID --hive templates/base/hive.yaml

# Deploy overlay
if [ -n "$OVERLAY" ]; then
  limacharlie configs push --oid $ORG_ID --hive templates/overlays/$OVERLAY/hive.yaml
fi

echo "Deployed rules to organization: $ORG_ID"
```

**Change Management**:
1. Test changes in template organization
2. Update base template or overlay
3. Commit to version control
4. Deploy to staging organizations
5. Monitor for 48 hours
6. Deploy to production organizations
7. Document changes in changelog

### Security and Compliance

**Coverage Validation**:
```bash
# Export all rules
limacharlie dr list --format json > current-rules.json

# Analyze MITRE coverage
cat current-rules.json | jq -r '.[] | .metadata.mitre_attack' | sort | uniq

# Compare against framework
# Use MITRE ATT&CK Navigator to visualize
```

**Audit Trail**:
- Store rules in Git (automatic audit trail)
- Include metadata about changes
- Tag releases with version numbers
- Maintain changelog
- Track who approved changes

**Compliance Mapping**:
```yaml
# Example rule with compliance metadata
respond:
  - action: report
    name: pci-dss-system-access
    metadata:
      compliance:
        - PCI-DSS: "10.2.5"
        - HIPAA: "164.312(b)"
        - SOC2: "CC6.1"
      mitre_attack: "T1078"
```

**Regular Reviews**:
- Weekly: High false positive rules
- Monthly: New threat intelligence
- Quarterly: Full ruleset effectiveness
- Annually: Compliance alignment
- After incidents: Gaps in coverage

### Documentation Standards

**Rule Documentation**:
```yaml
respond:
  - action: report
    name: descriptive-detection-name
    metadata:
      author: "Security Team"
      version: "1.2.0"
      created: "2024-01-15"
      description: "Detects suspicious PowerShell encoded commands"
      severity: "high"
      mitre_attack: "T1059.001"
      references:
        - "https://attack.mitre.org/techniques/T1059/001/"
      changelog:
        - "1.2.0: Added parent process check"
        - "1.1.0: Improved command line parsing"
        - "1.0.0: Initial version"
```

**FP Rule Documentation**:
- Use descriptive names: `fp-jenkins-builds-network-scan`
- Include reason in UI notes
- Document expiry reasons
- Track creation date and author

**Runbook Documentation**:
- Create playbooks for each detection type
- Include investigation steps
- Document common false positive scenarios
- Provide response procedures
- Link to MITRE ATT&CK techniques

[Back to Quick Start](SKILL.md) | [See Examples](EXAMPLES.md) | [See Troubleshooting](TROUBLESHOOTING.md)
