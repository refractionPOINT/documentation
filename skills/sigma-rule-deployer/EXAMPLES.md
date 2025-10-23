# Managed Rulesets - Deployment Examples

This document provides step-by-step deployment scenarios and examples for all managed ruleset types.

[Back to Quick Start](SKILL.md) | [See Reference](REFERENCE.md) | [See Troubleshooting](TROUBLESHOOTING.md)

## Table of Contents

- [Sigma Deployment Scenarios](#sigma-deployment-scenarios)
- [Soteria EDR Deployment](#soteria-edr-deployment)
- [AWS Security Monitoring](#aws-security-monitoring)
- [M365 Threat Detection](#m365-threat-detection)
- [SOC Prime Integration](#soc-prime-integration)
- [Community Rule Deployment](#community-rule-deployment)
- [Testing Workflows](#testing-workflows)
- [Multi-Organization Deployment](#multi-organization-deployment)
- [Complete Deployment Examples](#complete-deployment-examples)

## Sigma Deployment Scenarios

### Scenario 1: Convert and Deploy Single Sigma Rule

**Use case**: You have a custom Sigma rule or found a specific rule you want to deploy.

**Step 1: Create or obtain Sigma rule**
```yaml
# suspicious-powershell.yaml
title: Suspicious PowerShell Encoded Command
status: test
description: Detects suspicious PowerShell execution with encoded commands
references:
    - https://attack.mitre.org/techniques/T1059/001/
author: Security Team
date: 2024/01/15
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        CommandLine|contains:
            - '-enc '
            - '-encodedcommand '
    condition: selection
falsepositives:
    - Legitimate scripts using encoded commands
level: medium
```

**Step 2: Convert the rule**
```bash
# Convert using the API
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@suspicious-powershell.yaml" \
  > converted.json

# Extract the rule
cat converted.json | jq -r '.rule' > lc-powershell-rule.yaml
```

**Step 3: Review the converted rule**
```bash
cat lc-powershell-rule.yaml
```

**Step 4: Validate syntax**
```bash
limacharlie replay --validate --rule-content lc-powershell-rule.yaml
```

**Step 5: Test against historical data**
```bash
# Test against last 7 days
limacharlie replay --rule-content lc-powershell-rule.yaml \
  --entire-org --last-seconds 604800
```

**Step 6: Deploy the rule**
```bash
limacharlie dr add --rule-name sigma-suspicious-powershell \
  --rule-file lc-powershell-rule.yaml
```

**Step 7: Monitor and tune**
```bash
# Check for detections
limacharlie detections list --last-seconds 3600

# Create FP rule if needed (via UI)
```

### Scenario 2: Bulk Convert Sigma Rules from GitHub

**Use case**: Deploy multiple related Sigma rules from a GitHub directory.

**Step 1: Convert entire directory**
```bash
# Convert all Windows process creation rules
curl -X POST https://sigma.limacharlie.io/convert/repo \
  -d "repo=https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation" \
  > windows-process-rules.json
```

**Step 2: Extract individual rules**
```bash
# Create directory for rules
mkdir -p sigma-rules/windows-process

# Extract each rule to separate file
cat windows-process-rules.json | jq -c '.rules[]' | while read rule; do
  # Get filename from URL
  filename=$(echo $rule | jq -r '.file' | sed 's/.*\///' | sed 's/.yml$/.yaml/')

  # Extract rule content
  echo $rule | jq -r '.rule' > "sigma-rules/windows-process/$filename"

  echo "Extracted: $filename"
done
```

**Step 3: Review and select rules**
```bash
# List extracted rules
ls -lh sigma-rules/windows-process/

# Review specific rule
cat sigma-rules/windows-process/proc_creation_win_susp_cmd.yaml
```

**Step 4: Validate selected rules**
```bash
# Validate all rules
for rule in sigma-rules/windows-process/*.yaml; do
  echo "Validating: $(basename $rule)"
  limacharlie replay --validate --rule-content "$rule" || echo "FAILED: $rule"
done
```

**Step 5: Test high-priority rules**
```bash
# Test against historical data
limacharlie replay --rule-content sigma-rules/windows-process/proc_creation_win_susp_cmd.yaml \
  --entire-org --last-seconds 86400
```

**Step 6: Deploy selected rules**
```bash
# Deploy rules with sigma- prefix
for rule in sigma-rules/windows-process/*.yaml; do
  name="sigma-$(basename $rule .yaml)"
  limacharlie dr add --rule-name "$name" --rule-file "$rule"
  echo "Deployed: $name"
done
```

### Scenario 3: Deploy Pre-Converted SigmaHQ Rules

**Use case**: Use LimaCharlie's pre-converted Sigma rule repository for quick deployment.

**Step 1: Clone the repository**
```bash
git clone https://github.com/refractionPOINT/sigma-limacharlie.git
cd sigma-limacharlie
```

**Step 2: Browse available rules**
```bash
# View rule categories
ls -la rules/

# View Windows rules
ls -la rules/windows/

# View specific category
ls -la rules/windows/process_creation/
```

**Step 3: Select rules to deploy**
```bash
# Review rule
cat rules/windows/process_creation/proc_creation_win_susp_powershell_parent.yaml
```

**Step 4: Deploy rules**
```bash
# Deploy single rule
limacharlie dr add \
  --rule-name sigma-susp-powershell-parent \
  --rule-file rules/windows/process_creation/proc_creation_win_susp_powershell_parent.yaml

# Or deploy all rules in a category
for rule in rules/windows/process_creation/*.yaml; do
  name="sigma-$(basename $rule .yaml)"
  limacharlie dr add --rule-name "$name" --rule-file "$rule"
  echo "Deployed: $name"
done
```

**Step 5: Keep rules updated**
```bash
# Pull latest updates
cd sigma-limacharlie
git pull origin master

# Re-deploy updated rules
# (Use same deployment command as Step 4)
```

## Soteria EDR Deployment

### Scenario 1: First-Time Soteria EDR Setup

**Use case**: New organization wants comprehensive EDR coverage.

**Step 1: Subscribe via UI**
1. Log into LimaCharlie
2. Navigate to **Add-On Marketplace**
3. Click **Extensions** tab
4. Search for "Soteria" or scroll to `soteria-rules-edr`
5. Click on the extension

**Step 2: Configure subscription**
1. Select your organization from dropdown
2. Click **Subscribe**
3. Review required events list
4. Click **Enable Required Events** (if offered)
5. Confirm subscription

**Step 3: Verify event configuration**
1. Navigate to **Artifact Collection** page
2. Verify these events are enabled:
   - `NEW_PROCESS`
   - `DNS_REQUEST`
   - `NETWORK_CONNECTIONS`
   - `FILE_CREATE`
   - `FILE_MODIFIED`
   - `MODULE_LOAD`
   - `REGISTRY_WRITE`
   - `REGISTRY_CREATE`
   - `SENSITIVE_PROCESS_ACCESS`
   - `THREAD_INJECTION`
   - `CODE_IDENTITY`
   - `NEW_DOCUMENT`
   - `NEW_NAMED_PIPE`
   - `EXISTING_PROCESS`

**Step 4: Apply to installation keys**
1. In **Artifact Collection**, select events
2. Click **Apply to Installation Key**
3. Select installation key(s)
4. Click **Apply**
5. New sensors will automatically collect these events

**Step 5: Apply to existing sensors**
1. Navigate to **Sensors** page
2. Select sensors to update
3. Click **Configure Artifact Collection**
4. Enable required events
5. Click **Apply**

**Step 6: Monitor activation**
1. Wait 24-48 hours for full rule activation
2. Navigate to **Detections** page
3. Monitor for Soteria detections
4. Check that sensors are reporting events

**Step 7: View MITRE coverage**
1. Open coverage map: https://mitre-attack.github.io/attack-navigator/#layerURL=https%3A%2F%2Fstorage.googleapis.com%2Fsoteria-detector-mapping%2F%2Fall.json
2. Review coverage by platform
3. Identify any gaps in your environment

### Scenario 2: Soteria EDR with Infrastructure as Code

**Use case**: MSSP deploying Soteria EDR across multiple client organizations.

**Step 1: Create base configuration**
```yaml
# base-config.yaml
extensions:
  soteria-rules-edr:
    enabled: true

artifact_collection:
  - event: NEW_PROCESS
  - event: DNS_REQUEST
  - event: NETWORK_CONNECTIONS
  - event: FILE_CREATE
  - event: FILE_MODIFIED
  - event: MODULE_LOAD
  - event: REGISTRY_WRITE
  - event: REGISTRY_CREATE
  - event: SENSITIVE_PROCESS_ACCESS
  - event: THREAD_INJECTION
  - event: CODE_IDENTITY
  - event: NEW_DOCUMENT
  - event: NEW_NAMED_PIPE
  - event: EXISTING_PROCESS
```

**Step 2: Create deployment script**
```bash
#!/bin/bash
# deploy-soteria.sh

ORG_IDS=(
  "org-id-client-a"
  "org-id-client-b"
  "org-id-client-c"
)

for ORG_ID in "${ORG_IDS[@]}"; do
  echo "Deploying to $ORG_ID..."

  # Subscribe to extension (via API)
  curl -X POST https://api.limacharlie.io/v1/org/$ORG_ID/extension/soteria-rules-edr \
    -H "Authorization: Bearer $LC_API_KEY" \
    -d '{"enabled": true}'

  # Apply configuration
  limacharlie configs push --oid $ORG_ID --hive base-config.yaml

  echo "Completed: $ORG_ID"
done
```

**Step 3: Execute deployment**
```bash
chmod +x deploy-soteria.sh
./deploy-soteria.sh
```

**Step 4: Verify deployment**
```bash
# Check subscription status for each org
for ORG_ID in "${ORG_IDS[@]}"; do
  echo "Checking $ORG_ID..."
  curl -X GET https://api.limacharlie.io/v1/org/$ORG_ID/subscription \
    -H "Authorization: Bearer $LC_API_KEY" | jq '.subscriptions[] | select(.name=="soteria-rules-edr")'
done
```

## AWS Security Monitoring

### Scenario 1: Complete AWS Security Setup

**Use case**: Organization wants to monitor AWS environment with CloudTrail and GuardDuty.

**Step 1: Configure AWS CloudTrail**

**In AWS Console**:
1. Navigate to CloudTrail service
2. Create new trail or use existing
3. Configure S3 bucket for logs
4. Enable management events
5. Enable data events (if needed)
6. Note S3 bucket name and region

**Step 2: Create IAM role for LimaCharlie**

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

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::292661820299:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "your-limacharlie-oid"
        }
      }
    }
  ]
}
```

**Step 3: Configure CloudTrail adapter in LimaCharlie**
1. Navigate to **Integrations** page
2. Select **AWS CloudTrail**
3. Click **Add Integration**
4. Enter configuration:
   - Role ARN: `arn:aws:iam::ACCOUNT-ID:role/LimaCharlieCloudTrail`
   - External ID: Your organization ID
   - S3 Bucket: `your-cloudtrail-bucket`
   - Region: `us-east-1` (or your region)
5. Click **Test Connection**
6. Click **Save**

**Step 4: Enable AWS GuardDuty**

**In AWS Console**:
1. Navigate to GuardDuty service
2. Click **Get Started**
3. Enable GuardDuty
4. Note region where enabled

**Step 5: Create IAM role for GuardDuty**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "guardduty:GetFindings",
        "guardduty:ListFindings",
        "guardduty:ListDetectors"
      ],
      "Resource": "*"
    }
  ]
}
```

**Step 6: Configure GuardDuty adapter in LimaCharlie**
1. Navigate to **Integrations** page
2. Select **AWS GuardDuty**
3. Click **Add Integration**
4. Enter configuration:
   - Role ARN: `arn:aws:iam::ACCOUNT-ID:role/LimaCharlieGuardDuty`
   - External ID: Your organization ID
   - Region: `us-east-1` (or your region)
5. Click **Test Connection**
6. Click **Save**

**Step 7: Subscribe to TOR lookup**
1. Navigate to **Add-On Marketplace**
2. Search for "TOR" or select `tor`
3. Click **Subscribe** (free)

**Step 8: Subscribe to Soteria AWS**
1. Navigate to **Add-On Marketplace**
2. Search for "Soteria AWS" or select `soteria-rules-aws`
3. Click **Subscribe**
4. Confirm subscription

**Step 9: Verify ingestion**
```bash
# Check for CloudTrail events
limacharlie artifacts search \
  --artifact-type cloudtrail \
  --last-seconds 3600

# Check for GuardDuty findings
limacharlie artifacts search \
  --artifact-type guardduty \
  --last-seconds 3600
```

**Step 10: Monitor detections**
1. Wait 24-48 hours for rules to activate
2. Navigate to **Detections** page
3. Monitor for AWS-related detections
4. Create FP rules as needed

## M365 Threat Detection

### Scenario 1: Microsoft 365 Security Monitoring

**Use case**: Organization wants to monitor M365 for security threats.

**Step 1: Configure Office 365 adapter**

**Prerequisites**:
- Global Administrator or Security Administrator role
- Audit log search enabled in M365
- Modern authentication enabled

**In LimaCharlie**:
1. Navigate to **Integrations** page
2. Select **Office 365**
3. Click **Add Integration**
4. Click **Authenticate with Microsoft**
5. Sign in with admin account
6. Grant requested permissions
7. Configure log types:
   - Exchange (email activity)
   - SharePoint (file activity)
   - Azure Active Directory (authentication)
   - DLP (data loss prevention)
8. Set ingestion frequency (recommended: 5 minutes)
9. Click **Save**

**Step 2: Verify audit log collection**

**In M365 Admin Center**:
1. Navigate to **Security & Compliance Center**
2. Go to **Search** > **Audit log search**
3. Verify audit logging is enabled
4. Check recent activities are logged

**Step 3: Subscribe to TOR lookup**
1. Navigate to **Add-On Marketplace** in LimaCharlie
2. Search for "TOR" or select `tor`
3. Click **Subscribe** (free)

**Step 4: Subscribe to Soteria M365**
1. Navigate to **Add-On Marketplace**
2. Search for "Soteria M365" or select `soteria-rules-o365`
3. Click **Subscribe**
4. Confirm subscription

**Step 5: Verify log ingestion**
```bash
# Check for O365 events
limacharlie artifacts search \
  --artifact-type office365 \
  --last-seconds 3600

# View sample events
limacharlie artifacts search \
  --artifact-type office365 \
  --last-seconds 3600 \
  --limit 5
```

**Step 6: Test detection coverage**

**Create test activities**:
1. Log in from different locations
2. Download multiple files
3. Create email forwarding rule
4. Share files externally
5. Modify user permissions

**Check for detections**:
1. Navigate to **Detections** page
2. Monitor for M365-related detections
3. Verify appropriate activities trigger alerts

**Step 7: Tune for false positives**
```bash
# Analyze detections
limacharlie detections list --last-seconds 86400 > m365-detections.json

# Identify patterns
cat m365-detections.json | jq '.[] | .cat' | sort | uniq -c
```

Create FP rules for legitimate activities (via UI).

## SOC Prime Integration

### Scenario 1: SOC Prime Content List Integration

**Use case**: Organization with SOC Prime subscription wants continuous rule updates.

**Step 1: Set up content lists in SOC Prime**

**In SOC Prime Platform**:
1. Log into https://socprime.com/
2. Navigate to **Content Management**
3. Click **Create New List**
4. Name the list (e.g., "LimaCharlie Production")
5. Select detection rules to include:
   - Browse by MITRE ATT&CK technique
   - Search by keyword or CVE
   - Filter by platform (Windows, Linux, AWS, etc.)
6. Click **Add to List** for each rule
7. Save the list

**Step 2: Generate API key**

**In SOC Prime Platform**:
1. Navigate to **Settings** > **API Access**
2. Click **Generate New Key**
3. Name the key: "LimaCharlie Integration"
4. Copy the API key (store securely)
5. Click **Save**

**Step 3: Enable SOC Prime add-on in LimaCharlie**
1. Log into LimaCharlie
2. Navigate to **Add-On Marketplace**
3. Search for "SOC Prime" or select `socprime`
4. Click **Subscribe**

**Step 4: Configure integration**
1. Navigate to **Integrations** page
2. Select **SOC Prime**
3. Paste API key
4. Click **Update**
5. Wait for content lists to load (5-10 seconds)

**Step 5: Select content lists**
1. Available lists will appear
2. Check boxes for lists to sync
3. Click **Update**

**Step 6: Verify initial sync**
```bash
# Wait up to 3 hours for first sync
# Then check for SOC Prime rules
limacharlie dr list | grep socprime

# Count rules
limacharlie dr list | grep socprime | wc -l
```

**Step 7: Monitor sync status**
1. Navigate to **Integrations** > **SOC Prime**
2. Check last sync time
3. Verify sync errors (if any)

**Step 8: Test detections**
```bash
# List recent SOC Prime detections
limacharlie detections list --last-seconds 86400 | grep socprime
```

### Scenario 2: Managing Multiple SOC Prime Lists

**Use case**: Different lists for different environments or clients.

**Step 1: Create environment-specific lists**

**In SOC Prime Platform**:
1. Create list: "LimaCharlie - Production"
   - High-confidence rules
   - Well-tested detections
   - Low false positive rate

2. Create list: "LimaCharlie - Testing"
   - New rules
   - Experimental detections
   - Higher FP tolerance

3. Create list: "LimaCharlie - Compliance"
   - PCI-DSS related rules
   - HIPAA monitoring
   - Compliance-specific detections

**Step 2: Use separate organizations**
- Production org: Subscribe to "Production" list only
- Staging org: Subscribe to "Testing" list
- Compliance org: Subscribe to "Compliance" list

**Step 3: Track updates per list**
```bash
# Export rules with metadata
limacharlie dr list --format json > soc-prime-rules.json

# Analyze by metadata (if SOC Prime includes list info)
cat soc-prime-rules.json | jq '.[] | select(.author=="socprime") | .metadata'
```

## Community Rule Deployment

### Scenario 1: Deploy Rule for Specific CVE

**Use case**: New CVE announced, need quick detection coverage.

**Step 1: Search Community Library**
1. Navigate to **Automation > Rules**
2. Click **Add Rule**
3. Click **Community Library** (upper right)
4. Search: `CVE-2024-1234` (example CVE)
5. Review results

**Step 2: Review rule details**
1. Click on relevant rule
2. Review **Source Code** (original format)
3. Check **Licensing** information
4. Review **References** for context
5. Check **Metadata** (MITRE ATT&CK, severity, etc.)

**Step 3: Load and convert**
1. Click **Load Rule** button
2. Wait 5-10 seconds for AI conversion
3. Review converted LimaCharlie syntax
4. Read explanatory comments added by AI

**Step 4: Customize for your environment**
```yaml
# Example: Add organization-specific exclusions
detect:
  events:
    - NEW_PROCESS
  op: and
  rules:
    - op: is windows
    - op: contains
      path: event/COMMAND_LINE
      value: vulnerable-pattern
    # Add exclusion for known-good usage
    - op: not
      rule:
        op: ends with
        path: event/FILE_PATH
        value: approved-tool.exe
        case sensitive: false
```

**Step 5: Test the rule**
```bash
# Save rule to file
cat > cve-2024-1234-rule.yaml << 'EOF'
[paste converted rule here]
EOF

# Validate syntax
limacharlie replay --validate --rule-content cve-2024-1234-rule.yaml

# Test against recent data
limacharlie replay --rule-content cve-2024-1234-rule.yaml \
  --entire-org --last-seconds 604800
```

**Step 6: Deploy**
1. Back in Community Library conversion view
2. Enter rule name: `cve-2024-1234-detection`
3. Click **Save**
4. Verify in **D&R Rules** list

**Step 7: Monitor**
```bash
# Check for detections
limacharlie detections list --last-seconds 3600 | grep cve-2024-1234
```

### Scenario 2: Build Detection Stack from Community Rules

**Use case**: New environment needs coverage for common threats.

**Step 1: Identify priority techniques**
1. Review MITRE ATT&CK framework
2. Identify techniques relevant to environment
3. Create prioritized list:
   - T1059 (Command and Scripting Interpreter)
   - T1003 (OS Credential Dumping)
   - T1055 (Process Injection)
   - T1071 (Application Layer Protocol)
   - T1486 (Data Encrypted for Impact)

**Step 2: Search Community Library by technique**
1. Navigate to **Community Library**
2. Search: `T1059`
3. Filter by platform (Windows, Linux, etc.)
4. Review available rules

**Step 3: Select and convert rules**

For each technique:
1. Find 2-3 high-quality rules
2. Click **Load Rule** to convert
3. Review and customize
4. Name with technique prefix: `T1059-powershell-encoded-cmd`
5. Save

**Step 4: Document coverage**
```bash
# Export deployed rules
limacharlie dr list --format json > community-rules.json

# List MITRE coverage
cat community-rules.json | jq -r '.[] | .metadata.mitre_attack' | sort | uniq

# Create coverage matrix
cat community-rules.json | jq -r '.[] | "\(.metadata.mitre_attack),\(.name)"'
```

**Step 5: Test coverage**
```bash
# Test all new rules against historical data
for rule in T1059-* T1003-* T1055-* T1071-* T1486-*; do
  echo "Testing $rule..."
  limacharlie dr get --rule-name "$rule" --format yaml > "/tmp/$rule.yaml"
  limacharlie replay --rule-content "/tmp/$rule.yaml" --entire-org --last-seconds 86400
done
```

## Testing Workflows

### Workflow 1: Test New Rule Before Deployment

**Step 1: Validate syntax**
```bash
limacharlie replay --validate --rule-content new-rule.yaml
```

**Step 2: Test with sample event**
```yaml
# Create sample-event.json
[
  {
    "event": {
      "COMMAND_LINE": "powershell.exe -enc ABC123...",
      "FILE_PATH": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
      "USER_NAME": "testuser"
    },
    "routing": {
      "event_type": "NEW_PROCESS",
      "hostname": "test-host",
      "platform": "windows"
    }
  }
]
```

```bash
limacharlie replay --rule-content new-rule.yaml \
  --events sample-event.json
```

**Step 3: Test with trace for debugging**
```bash
limacharlie replay --rule-content new-rule.yaml \
  --events sample-event.json \
  --trace
```

**Step 4: Test against historical data**
```bash
# Last 24 hours
limacharlie replay --rule-content new-rule.yaml \
  --entire-org --last-seconds 86400

# Specific time range
limacharlie replay --rule-content new-rule.yaml \
  --entire-org --start 1640000000 --end 1640086400

# Specific sensor
limacharlie replay --rule-content new-rule.yaml \
  --sid SENSOR-ID --last-seconds 604800
```

**Step 5: Analyze results**
```bash
# Save replay results
limacharlie replay --rule-content new-rule.yaml \
  --entire-org --last-seconds 86400 > replay-results.json

# Count matches
cat replay-results.json | jq '. | length'

# Review matched events
cat replay-results.json | jq '.[] | {hostname: .routing.hostname, command: .event.COMMAND_LINE}'
```

**Step 6: Refine rule based on results**
- Too many matches: Add more restrictive conditions
- No matches: Verify event structure and paths
- False positives: Add exclusions

**Step 7: Deploy after validation**
```bash
limacharlie dr add --rule-name validated-rule \
  --rule-file new-rule.yaml
```

### Workflow 2: Test FP Rule Effectiveness

**Step 1: Identify false positive pattern**
```bash
# Get recent false positive detections
limacharlie detections list --last-seconds 86400 > recent-detections.json

# Analyze patterns
cat recent-detections.json | jq '.[] | select(.cat=="noisy-rule") | .routing.hostname' | sort | uniq -c
```

**Step 2: Create FP rule**
```yaml
# fp-test.yaml
op: and
rules:
  - op: is
    path: cat
    value: noisy-rule
  - op: is
    path: routing/hostname
    value: build-server-01
```

**Step 3: Test FP rule against detections**

Create test detection file:
```json
[
  {
    "cat": "noisy-rule",
    "routing": {
      "hostname": "build-server-01"
    },
    "detect": {
      "event": {
        "COMMAND_LINE": "test command"
      }
    }
  }
]
```

**Step 4: Manually verify FP logic**
- Review detection structure in Timeline
- Confirm FP rule paths are correct
- Test with variations

**Step 5: Deploy FP rule**
1. Navigate to **Automation > False Positive Rules**
2. Click **New Rule**
3. Paste FP rule logic
4. Name: `fp-build-server-noisy-rule`
5. Save

**Step 6: Monitor impact**
```bash
# Before FP rule
COUNT_BEFORE=$(limacharlie detections list --last-seconds 86400 | jq '. | length')

# Wait 24 hours

# After FP rule
COUNT_AFTER=$(limacharlie detections list --last-seconds 86400 | jq '. | length')

echo "Detections reduced by: $((COUNT_BEFORE - COUNT_AFTER))"
```

## Multi-Organization Deployment

### Scenario 1: MSSP Baseline Deployment

**Use case**: Deploy standard ruleset across 50+ client organizations.

**Step 1: Create baseline structure**
```
mssp-baseline/
  hive.yaml                    # Base configuration
  rules/
    sigma/                     # Sigma rules
      windows/
      linux/
    custom/                    # Custom rules
      common-threats.yaml
  fp-rules/
    common-fps.yaml            # Common FP rules
  extensions/
    soteria.yaml               # Extension configs
```

**Step 2: Define base hive.yaml**
```yaml
# hive.yaml
rules:
  # Include rules from files
  sigma-suspicious-cmd:
    from: rules/sigma/windows/proc_creation_win_susp_cmd.yaml

  sigma-lateral-movement:
    from: rules/sigma/windows/proc_creation_win_lateral_movement.yaml

  custom-ransomware:
    from: rules/custom/common-threats.yaml

fp_rules:
  common-fps:
    from: fp-rules/common-fps.yaml

extensions:
  soteria-rules-edr:
    enabled: true

artifact_collection:
  - event: NEW_PROCESS
  - event: DNS_REQUEST
  - event: NETWORK_CONNECTIONS
  - event: FILE_CREATE
  # ... (all required events)
```

**Step 3: Create client overlay structure**
```
clients/
  client-a/
    hive.yaml                  # Client-specific config
    rules/
      custom-client-a.yaml     # Client-specific rules
    fp-rules/
      client-a-fps.yaml        # Client-specific FPs
  client-b/
    hive.yaml
    # ...
```

**Step 4: Client-specific overlay**
```yaml
# clients/client-a/hive.yaml
rules:
  # Inherit base rules (via merge)
  # Add client-specific rules
  client-a-approved-software:
    from: rules/custom-client-a.yaml

fp_rules:
  # Client-specific FP rules
  client-a-fps:
    from: fp-rules/client-a-fps.yaml
```

**Step 5: Create deployment script**
```bash
#!/bin/bash
# deploy-to-all-clients.sh

# Load client organization IDs
CLIENT_ORGS=(
  "client-a:org-id-aaa"
  "client-b:org-id-bbb"
  "client-c:org-id-ccc"
  # ... 50+ clients
)

for CLIENT in "${CLIENT_ORGS[@]}"; do
  CLIENT_NAME=$(echo $CLIENT | cut -d':' -f1)
  ORG_ID=$(echo $CLIENT | cut -d':' -f2)

  echo "========================================  "
  echo "Deploying to: $CLIENT_NAME ($ORG_ID)"
  echo "========================================"

  # Deploy baseline
  echo "Deploying baseline..."
  limacharlie configs push --oid $ORG_ID --hive mssp-baseline/hive.yaml

  # Deploy client overlay if exists
  if [ -f "clients/$CLIENT_NAME/hive.yaml" ]; then
    echo "Deploying client overlay..."
    limacharlie configs push --oid $ORG_ID --hive "clients/$CLIENT_NAME/hive.yaml"
  fi

  # Subscribe to extensions
  echo "Subscribing to extensions..."
  curl -X POST https://api.limacharlie.io/v1/org/$ORG_ID/extension/soteria-rules-edr \
    -H "Authorization: Bearer $LC_API_KEY" \
    -d '{"enabled": true}'

  echo "Completed: $CLIENT_NAME"
  echo ""
done

echo "Deployment complete for all clients"
```

**Step 6: Execute deployment**
```bash
chmod +x deploy-to-all-clients.sh
./deploy-to-all-clients.sh > deployment-log-$(date +%Y%m%d).txt 2>&1
```

**Step 7: Verify deployment**
```bash
#!/bin/bash
# verify-deployment.sh

for CLIENT in "${CLIENT_ORGS[@]}"; do
  CLIENT_NAME=$(echo $CLIENT | cut -d':' -f1)
  ORG_ID=$(echo $CLIENT | cut -d':' -f2)

  echo "Verifying: $CLIENT_NAME"

  # Count rules
  RULE_COUNT=$(limacharlie --oid $ORG_ID dr list | wc -l)
  echo "  Rules deployed: $RULE_COUNT"

  # Check Soteria subscription
  SOTERIA_STATUS=$(curl -s -X GET https://api.limacharlie.io/v1/org/$ORG_ID/subscription \
    -H "Authorization: Bearer $LC_API_KEY" | \
    jq -r '.subscriptions[] | select(.name=="soteria-rules-edr") | .status')
  echo "  Soteria status: $SOTERIA_STATUS"

  echo ""
done
```

## Complete Deployment Examples

### Example 1: New Organization - Full Stack

**Scenario**: New company setting up complete security monitoring.

**Environment**:
- 100 Windows endpoints
- 20 Linux servers
- AWS infrastructure
- Microsoft 365

**Deployment Plan**:

**Week 1: Foundation**
```bash
# 1. Subscribe to Soteria EDR
# (via UI, as documented above)

# 2. Deploy critical Sigma rules
curl -X POST https://sigma.limacharlie.io/convert/repo \
  -d "repo=https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation" \
  > sigma-windows-critical.json

# Extract and deploy
mkdir sigma-rules
cat sigma-windows-critical.json | jq -c '.rules[]' | while read rule; do
  filename=$(echo $rule | jq -r '.file' | sed 's/.*\///' | sed 's/.yml$/.yaml/')
  echo $rule | jq -r '.rule' > "sigma-rules/$filename"

  # Deploy
  limacharlie dr add --rule-name "sigma-$(basename $filename .yaml)" \
    --rule-file "sigma-rules/$filename"
done

# 3. Configure outputs
limacharlie outputs add slack \
  --webhook-url "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --name security-alerts
```

**Week 2: Cloud Coverage**
```bash
# 1. Configure AWS CloudTrail (via UI)
# 2. Configure AWS GuardDuty (via UI)
# 3. Subscribe to Soteria AWS (via UI)
# 4. Subscribe to TOR lookup (via UI)

# 5. Add custom AWS rules
cat > aws-suspicious-activity.yaml << 'EOF'
detect:
  events:
    - cloudtrail
  op: or
  rules:
    - op: is
      path: event/eventName
      value: DeleteTrail
    - op: is
      path: event/eventName
      value: StopLogging
    - op: is
      path: event/eventName
      value: DeleteFlowLogs
respond:
  - action: report
    name: aws-suspicious-log-deletion
    metadata:
      severity: high
      description: Suspicious AWS logging deletion detected
EOF

limacharlie dr add --rule-name aws-suspicious-activity \
  --rule-file aws-suspicious-activity.yaml
```

**Week 3: M365 Integration**
```bash
# 1. Configure Office 365 adapter (via UI)
# 2. Subscribe to Soteria M365 (via UI)

# 3. Create custom M365 rules for org policies
cat > m365-policy-violations.yaml << 'EOF'
detect:
  events:
    - office365
  op: and
  rules:
    - op: is
      path: event/Operation
      value: FileDownloadedToLocal
    - op: is greater than
      path: event/ItemCount
      value: 100
      length of: false
respond:
  - action: report
    name: m365-mass-download
    metadata:
      severity: medium
      description: User downloaded more than 100 files
EOF

limacharlie dr add --rule-name m365-policy-violations \
  --rule-file m365-policy-violations.yaml
```

**Week 4: Tuning**
```bash
# 1. Export detections from past 3 weeks
limacharlie detections list --last-seconds 1814400 > all-detections.json

# 2. Analyze false positives
cat all-detections.json | jq -r '.[] | .cat' | sort | uniq -c | sort -rn > detection-counts.txt

# 3. Create FP rules for common false positives (via UI)

# 4. Document baseline
cat > deployment-summary.md << 'EOF'
# Security Monitoring Deployment Summary

## Coverage
- Soteria EDR: Windows, Linux endpoints
- Soteria AWS: CloudTrail, GuardDuty
- Soteria M365: Full suite
- Sigma Rules: 45 rules (Windows process creation)
- Custom Rules: 5 rules (AWS, M365 policies)

## Metrics (First Month)
- Total Detections: 1,247
- True Positives: 23
- False Positives: 1,224 (tuned with 8 FP rules)
- Current FP Rate: <5%

## Next Steps
- Deploy Linux Sigma rules
- Add threat hunting rules
- Integrate with SIEM
- Monthly rule review process
EOF
```

[Back to Quick Start](SKILL.md) | [See Reference](REFERENCE.md) | [See Troubleshooting](TROUBLESHOOTING.md)
