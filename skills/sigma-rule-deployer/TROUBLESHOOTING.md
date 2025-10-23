# Managed Rulesets - Troubleshooting Guide

This document provides solutions to common issues organized by ruleset type.

[Back to Quick Start](SKILL.md) | [See Reference](REFERENCE.md) | [See Examples](EXAMPLES.md)

## Table of Contents

- [Sigma Conversion Issues](#sigma-conversion-issues)
- [Soteria No Detections](#soteria-no-detections)
- [SOC Prime Sync Issues](#soc-prime-sync-issues)
- [Community Conversion Failures](#community-conversion-failures)
- [False Positive Issues](#false-positive-issues)
- [Rule Matching Issues](#rule-matching-issues)
- [Testing Issues](#testing-issues)
- [Performance Problems](#performance-problems)
- [Integration Issues](#integration-issues)

## Sigma Conversion Issues

### Issue: Sigma Rule Conversion Returns Error

**Symptoms**:
- HTTP 400/500 error from conversion API
- Empty or malformed response
- Conversion fails silently

**Diagnostic Steps**:
```bash
# Test with verbose output
curl -v -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@sigma-rule.yaml" 2>&1 | tee conversion-debug.log

# Check response
cat conversion-debug.log | grep "HTTP/"
```

**Solutions**:

**1. Verify Sigma rule syntax**
```bash
# Install sigmac if available
pip install sigma-cli

# Validate Sigma rule
sigmac --target limacharlie sigma-rule.yaml
```

**2. Check for unsupported features**

Common unsupported features:
- Some aggregation functions
- Complex correlation rules
- Time-based correlation across multiple events
- Some logsource types

**Workaround**: Simplify rule or manually convert complex logic.

**3. Try different target type**
```bash
# If EDR fails, try artifact
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@sigma-rule.yaml" \
  -d "target=artifact"
```

**4. Check file encoding**
```bash
# Ensure UTF-8 encoding
file -i sigma-rule.yaml

# Convert if needed
iconv -f ISO-8859-1 -t UTF-8 sigma-rule.yaml > sigma-rule-utf8.yaml
```

**5. Validate YAML format**
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('sigma-rule.yaml'))"
```

### Issue: Converted Rule Has Invalid Syntax

**Symptoms**:
- Rule converts successfully but fails validation
- Syntax errors when deploying
- Invalid operator or path

**Diagnostic Steps**:
```bash
# Extract converted rule
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@sigma-rule.yaml" | \
  jq -r '.rule' > converted.yaml

# Validate
limacharlie replay --validate --rule-content converted.yaml
```

**Solutions**:

**1. Review conversion output**
```bash
cat converted.yaml
```

Look for:
- Incorrect path syntax
- Missing operators
- Malformed YAML indentation
- Incorrect event types

**2. Fix common conversion issues**

**Issue**: Incorrect path
```yaml
# Wrong
path: COMMAND_LINE

# Correct
path: event/COMMAND_LINE
```

**Issue**: Missing event type
```yaml
# Add detect section if missing
detect:
  events:
    - NEW_PROCESS  # Add appropriate event type
  op: and
  rules:
    # ... rest of rule
```

**Issue**: Invalid operator
```yaml
# Wrong
op: equal

# Correct
op: is
```

**3. Manually adjust the rule**
- Start with converted output
- Fix syntax issues
- Test with replay
- Deploy corrected version

**4. Report conversion bugs**
- Document the original Sigma rule
- Note the conversion issue
- Report to LimaCharlie support

### Issue: Converted Rule Doesn't Match Expected Events

**Symptoms**:
- Rule deploys successfully
- No detections generated
- Events should match but don't

**Diagnostic Steps**:
```bash
# Get sample event that should match
limacharlie historic view --sid SENSOR-ID \
  --start TIMESTAMP --end TIMESTAMP > sample-events.json

# Test rule with trace
limacharlie replay --rule-content converted.yaml \
  --events sample-events.json \
  --trace
```

**Solutions**:

**1. Compare Sigma logsource to LC event type**

Sigma logsource mapping:
```yaml
# Sigma
logsource:
  category: process_creation
  product: windows

# Should convert to
detect:
  events:
    - NEW_PROCESS
```

**2. Check field name mappings**

Common Sigma field mappings:
- `CommandLine` → `event/COMMAND_LINE`
- `Image` → `event/FILE_PATH`
- `ParentImage` → `event/PARENT/FILE_PATH`
- `User` → `event/USER_NAME`
- `TargetFilename` → `event/FILE_PATH` (for file events)

**3. Verify event structure**
```bash
# View actual event structure
cat sample-events.json | jq '.[0]'

# Compare with rule paths
grep "path:" converted.yaml
```

**4. Adjust paths in converted rule**
```yaml
# Original conversion might have
path: IMAGE

# Change to correct path
path: event/FILE_PATH
```

**5. Test incrementally**
```bash
# Create minimal test rule
cat > test-minimal.yaml << 'EOF'
detect:
  events:
    - NEW_PROCESS
  op: is windows
respond:
  - action: report
    name: test-windows-process
EOF

# Test - should match all Windows processes
limacharlie replay --rule-content test-minimal.yaml \
  --events sample-events.json

# Gradually add conditions from converted rule
```

### Issue: Batch Conversion Fails for Some Rules

**Symptoms**:
- `/convert/repo` returns partial results
- Some rules missing from output
- No error messages

**Diagnostic Steps**:
```bash
# Convert repo
curl -X POST https://sigma.limacharlie.io/convert/repo \
  -d "repo=https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation" \
  > batch-result.json

# Count results
cat batch-result.json | jq '.rules | length'

# List converted files
cat batch-result.json | jq -r '.rules[].file'
```

**Solutions**:

**1. Convert failed rules individually**
```bash
# Get list of all rules in directory
# (manually or via GitHub API)

# Convert each individually
for rule_url in $(cat rule-urls.txt); do
  echo "Converting: $rule_url"
  curl -X POST https://sigma.limacharlie.io/convert/rule \
    -H 'content-type: application/x-www-form-urlencoded' \
    --data-urlencode "rule=$(curl -s $rule_url)" \
    > "$(basename $rule_url .yml).json" 2>&1
done
```

**2. Check for rule-specific issues**
- Some rules may be too complex
- Some may use unsupported features
- Some may have syntax issues

**3. Use pre-converted repository**
```bash
# Use LimaCharlie's pre-converted rules instead
git clone https://github.com/refractionPOINT/sigma-limacharlie.git
cd sigma-limacharlie/rules
# Use these instead of converting
```

## Soteria No Detections

### Issue: No Detections After Soteria Subscription

**Symptoms**:
- Subscribed to Soteria EDR/AWS/M365
- No detections appearing
- Rules not visible (expected for managed rules)

**Diagnostic Steps**:

**1. Verify subscription status**
```bash
# Via UI
# Navigate to Billing > Subscriptions
# Check Soteria subscription is "Active"

# Via API
curl -X GET https://api.limacharlie.io/v1/org/YOUR-ORG-ID/subscription \
  -H "Authorization: Bearer YOUR-API-KEY" | \
  jq '.subscriptions[] | select(.name | contains("soteria"))'
```

**2. Check subscription date**
- Rules may take 24-48 hours to fully activate
- Check subscription start date

**Solutions**:

### For Soteria EDR:

**1. Verify required events are configured**
```bash
# Via UI
# Navigate to Artifact Collection
# Verify these events are enabled:
# - NEW_PROCESS
# - DNS_REQUEST
# - NETWORK_CONNECTIONS
# - FILE_CREATE
# - FILE_MODIFIED
# - MODULE_LOAD
# - REGISTRY_WRITE
# - REGISTRY_CREATE
# - SENSITIVE_PROCESS_ACCESS
# - THREAD_INJECTION
# - CODE_IDENTITY
# - NEW_DOCUMENT
# - NEW_NAMED_PIPE
# - EXISTING_PROCESS
```

**2. Check sensors are online and reporting**
```bash
# List sensors
limacharlie sensor list

# Check specific sensor
limacharlie sensor view --sid SENSOR-ID

# Verify events are being collected
limacharlie historic view --sid SENSOR-ID \
  --last-seconds 3600 | head -n 20
```

**3. Verify events are applied to sensors**
```bash
# Check installation key configuration
# Via UI: Installation Keys > View Key > Artifact Collection

# Verify existing sensors have event collection enabled
# Via UI: Sensors > Select Sensor > Configure Artifact Collection
```

**4. Wait for activation period**
- Initial activation: 24-48 hours
- Check again after waiting period

**5. Test with known malicious activity**
```bash
# Create test process (safe test)
# On Windows sensor:
whoami /all

# On Linux sensor:
cat /etc/shadow 2>/dev/null

# These should generate events, and may trigger detections
```

### For Soteria AWS:

**1. Verify CloudTrail adapter is configured**
```bash
# Via UI: Integrations > AWS CloudTrail
# Check Status is "Active"

# Test connection
# Click "Test Connection" button
```

**2. Verify GuardDuty adapter is configured**
```bash
# Via UI: Integrations > AWS GuardDuty
# Check Status is "Active"
```

**3. Check for telemetry ingestion**
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

**4. Verify TOR lookup is subscribed**
```bash
# Via UI: Add-On Marketplace
# Search for "tor"
# Verify it's subscribed (required for Soteria AWS)
```

**5. Check AWS IAM permissions**
```bash
# Verify IAM role has required permissions
# CloudTrail: s3:GetObject, s3:ListBucket
# GuardDuty: guardduty:GetFindings, guardduty:ListFindings
```

### For Soteria M365:

**1. Verify Office 365 adapter is configured**
```bash
# Via UI: Integrations > Office 365
# Check Status is "Active"
# Check Last Sync time is recent
```

**2. Check for O365 log ingestion**
```bash
# Check for O365 events
limacharlie artifacts search \
  --artifact-type office365 \
  --last-seconds 3600
```

**3. Verify audit logging is enabled in M365**
```powershell
# In PowerShell (as M365 admin)
Connect-ExchangeOnline
Get-AdminAuditLogConfig | Select UnifiedAuditLogIngestionEnabled

# Should return "True"
```

**4. Verify TOR lookup is subscribed**
```bash
# Same as Soteria AWS - required for M365
```

**5. Check M365 permissions**
- Global Administrator or Security Administrator role required
- Office 365 Management API access enabled
- Audit log search enabled

**6. Generate test activity**
```bash
# In M365:
# - Log in from different location
# - Download multiple files
# - Create email forwarding rule
# - Share files externally
# Wait 15-30 minutes for events to sync
```

### Issue: Soteria Detections Stopped After Working

**Symptoms**:
- Soteria was generating detections
- Detections stopped suddenly
- No configuration changes made

**Diagnostic Steps**:
```bash
# Check subscription status
# Via UI: Billing > Subscriptions

# Check for billing issues
# Via UI: Billing > Payment Methods

# Check detection history
limacharlie detections list --last-seconds 604800 | \
  grep -i soteria | \
  jq -r '.timestamp' | \
  sort
```

**Solutions**:

**1. Check for subscription expiration**
- Verify subscription is still active
- Check for payment failures
- Renew if expired

**2. Verify event collection still enabled**
- Check Artifact Collection settings
- Verify sensors are still reporting events
- Check for configuration changes

**3. Check for sensor issues**
```bash
# List offline sensors
limacharlie sensor list | grep offline

# Check event flow
limacharlie historic view --sid SENSOR-ID --last-seconds 3600
```

**4. Contact support if issue persists**
- Provide organization ID
- Provide subscription details
- Provide timeline of when detections stopped

## SOC Prime Sync Issues

### Issue: SOC Prime Rules Not Syncing

**Symptoms**:
- API key configured
- Content lists selected
- No rules appearing
- Or rules not updating

**Diagnostic Steps**:
```bash
# Check for SOC Prime rules
limacharlie dr list | grep socprime

# Count SOC Prime rules
limacharlie dr list | grep socprime | wc -l

# Via UI: Integrations > SOC Prime
# Check Last Sync time
```

**Solutions**:

**1. Verify API key is valid**

**In SOC Prime Platform**:
1. Log into https://socprime.com/
2. Navigate to Settings > API Access
3. Verify key is listed and active
4. Check expiration date

**In LimaCharlie**:
1. Navigate to Integrations > SOC Prime
2. Re-enter API key
3. Click Update
4. Check if lists load

**2. Verify SOC Prime subscription is active**
- Free accounts cannot access API
- Verify trial or paid subscription is active
- Check subscription status in SOC Prime

**3. Check content lists have rules**

**In SOC Prime Platform**:
1. Navigate to Content Management
2. Open selected list
3. Verify list contains rules
4. Check rule count

**4. Wait for sync cycle**
- Sync occurs every 3 hours
- Wait for next sync cycle
- Check Last Sync time in integration

**5. Check for API errors**
```bash
# Via API - check integration status
curl -X GET https://api.limacharlie.io/v1/org/YOUR-ORG-ID/integration/socprime \
  -H "Authorization: Bearer YOUR-API-KEY" | \
  jq '.'

# Look for error messages
```

**6. Re-configure integration**
1. Remove API key from LimaCharlie
2. Click Update
3. Re-add API key
4. Select content lists again
5. Click Update
6. Wait for sync

**7. Generate new API key**

If key is old or potentially compromised:
1. Generate new key in SOC Prime
2. Update in LimaCharlie
3. Revoke old key in SOC Prime

### Issue: SOC Prime Rules Are Duplicated

**Symptoms**:
- Same detection rule appears multiple times
- Different rule names but same logic
- Clutters rule list

**Solutions**:

**1. Check for overlapping content lists**
- Same rule may be in multiple selected lists
- Review selected lists in integration
- Deselect duplicate lists

**2. Disable duplicate rules**
```bash
# List all socprime rules
limacharlie dr list | grep socprime > socprime-rules.txt

# Identify duplicates (manual review)
# Remove duplicates
limacharlie dr remove --rule-name duplicate-rule-name
```

**3. Use FP rules to suppress duplicate detections**
```yaml
# If duplicates generate same detection name
op: is
path: cat
value: duplicate-detection-name
```

## Community Conversion Failures

### Issue: Community Rule AI Conversion Fails

**Symptoms**:
- Click "Load Rule" but nothing happens
- Error message during conversion
- Conversion produces invalid syntax

**Diagnostic Steps**:
1. Note the specific rule that failed
2. Check browser console for errors (F12)
3. Try again (AI conversion can be inconsistent)

**Solutions**:

**1. Retry conversion**
- AI conversion can fail intermittently
- Wait a few seconds
- Try "Load Rule" again
- May work on second or third attempt

**2. Try similar rule**
- Find similar rule in Community Library
- Convert that rule successfully
- Manually adjust to match desired logic

**3. Check rule complexity**
- Very complex rules may fail conversion
- Simplify source rule if possible
- Or break into multiple simpler rules

**4. Manually convert from source**
- View source code in Community Library
- Understand detection logic
- Manually write LimaCharlie D&R rule
- Use similar converted rule as template

**Example manual conversion process**:
```yaml
# Original Panther rule (Python-like)
def rule(event):
    return (
        event.get('eventName') == 'ConsoleLogin' and
        event.get('userIdentity', {}).get('type') == 'Root'
    )

# Manually convert to LimaCharlie
detect:
  events:
    - cloudtrail
  op: and
  rules:
    - op: is
      path: event/eventName
      value: ConsoleLogin
    - op: is
      path: event/userIdentity/type
      value: Root
respond:
  - action: report
    name: aws-root-console-login
```

**5. Report conversion issues**
- Note which rule failed
- Note the source (Anvilogic, Panther, etc.)
- Report to LimaCharlie support

### Issue: Converted Community Rule Has Poor Quality

**Symptoms**:
- Rule converts but logic seems wrong
- Too many false positives
- Doesn't match expected events
- Missing conditions from original

**Solutions**:

**1. Compare with original source**
- View source code in Community Library
- Compare AI conversion to original
- Identify missing or incorrect conditions

**2. Review conversion comments**
- AI adds explanatory comments
- Read comments for conversion decisions
- May explain limitations or assumptions

**3. Test thoroughly before production**
```bash
# Validate syntax
limacharlie replay --validate --rule-content converted-rule.yaml

# Test with trace
limacharlie replay --rule-content converted-rule.yaml \
  --events sample-events.json \
  --trace

# Test against historical data
limacharlie replay --rule-content converted-rule.yaml \
  --entire-org --last-seconds 86400
```

**4. Manually refine the rule**
- Use conversion as starting point
- Add missing conditions
- Fix incorrect paths or operators
- Improve precision

**5. Add organization-specific context**
```yaml
# Original conversion might be generic
# Add specific exclusions
detect:
  # ... AI converted logic
  op: and
  rules:
    - # ... converted conditions
    # Add org-specific exclusion
    - op: not
      rule:
        op: is
        path: routing/hostname
        value: approved-server
```

## False Positive Issues

### Issue: High False Positive Rate

**Symptoms**:
- Too many detections from a rule
- Most detections are false positives
- Alert fatigue for analysts

**Diagnostic Steps**:
```bash
# Get detections for specific rule
limacharlie detections list --last-seconds 86400 > detections.json

# Count by detection name
cat detections.json | jq -r '.[] | .cat' | sort | uniq -c | sort -rn

# Analyze patterns for specific rule
cat detections.json | jq '.[] | select(.cat=="noisy-rule")' > noisy-detections.json

# Look for patterns
cat noisy-detections.json | jq -r '.routing.hostname' | sort | uniq -c
cat noisy-detections.json | jq -r '.detect.event.FILE_PATH' | sort | uniq -c
cat noisy-detections.json | jq -r '.detect.event.USER_NAME' | sort | uniq -c
```

**Solutions**:

**1. Identify false positive patterns**

Common FP patterns:
- Specific hosts (build servers, test environments)
- Specific users (service accounts, admin accounts)
- Specific processes (legitimate tools, approved software)
- Specific times (scheduled tasks, maintenance windows)

**2. Create targeted FP rules**

**For specific hosts**:
```yaml
op: and
rules:
  - op: is
    path: cat
    value: noisy-rule-name
  - op: or
    rules:
      - op: is
        path: routing/hostname
        value: build-server-01
      - op: is
        path: routing/hostname
        value: test-server-01
      - op: contains
        path: routing/hostname
        value: -dev-
        case sensitive: false
```

**For specific processes**:
```yaml
op: and
rules:
  - op: is
    path: cat
    value: suspicious-process-creation
  - op: ends with
    path: detect/event/FILE_PATH
    value: approved-tool.exe
    case sensitive: false
```

**For service accounts**:
```yaml
op: and
rules:
  - op: is
    path: cat
    value: credential-access-detected
  - op: or
    rules:
      - op: is
        path: detect/event/USER_NAME
        value: svc_backup
        case sensitive: false
      - op: is
        path: detect/event/USER_NAME
        value: svc_monitoring
        case sensitive: false
```

**3. Tune the D&R rule (if you control it)**

For custom rules:
- Add more specific conditions
- Increase thresholds
- Add exclusions directly in rule
- Use suppression

**Example tuning**:
```yaml
# Original rule - too broad
detect:
  events:
    - NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: powershell
  case sensitive: false

# Tuned rule - more specific
detect:
  events:
    - NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/COMMAND_LINE
      value: powershell
      case sensitive: false
    # Add suspicious indicators
    - op: or
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: -enc
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: downloadstring
          case sensitive: false
    # Exclude known-good usage
    - op: not
      rule:
        op: ends with
        path: event/PARENT/FILE_PATH
        value: approved-script-runner.exe
        case sensitive: false
```

**4. Use suppression for noisy rules**
```yaml
# In rule respond section
respond:
  - action: report
    name: noisy-detection
    suppression:
      # Suppress same detection for 1 hour
      max_count: 1
      period: 3600
```

**5. Disable ineffective rules**
```bash
# If rule has very low value
limacharlie dr remove --rule-name low-value-rule
```

**6. Track FP rate over time**
```bash
# Create monitoring script
#!/bin/bash
# fp-rate-monitor.sh

TOTAL=$(limacharlie detections list --last-seconds 86400 | jq '. | length')
echo "Date,Total_Detections,FP_Rate" >> fp-rate.csv
echo "$(date +%Y-%m-%d),$TOTAL,TBD" >> fp-rate.csv

# Manually track true vs false positives
# Update FP_Rate column
```

### Issue: FP Rule Not Working

**Symptoms**:
- Created FP rule
- Detections still appearing
- FP rule doesn't match

**Diagnostic Steps**:
```bash
# Get sample detection that should be suppressed
limacharlie detections list --last-seconds 3600 > recent-detections.json

# Find specific detection
cat recent-detections.json | jq '.[] | select(.cat=="target-detection")' > target.json

# View structure
cat target.json | jq '.'
```

**Solutions**:

**1. Verify FP rule paths match detection structure**

**Common mistakes**:
```yaml
# Wrong - missing detect/ prefix
path: event/FILE_PATH

# Correct - accessing original event
path: detect/event/FILE_PATH
```

**2. Check case sensitivity**
```yaml
# Add case insensitive flag if needed
op: is
path: routing/hostname
value: test-server-01
case sensitive: false  # Add this
```

**3. Check path exists in detection**
```bash
# Verify path exists
cat target.json | jq '.detect.event.FILE_PATH'

# If null, path is wrong
# Check detection structure:
cat target.json | jq '.detect.event | keys'
```

**4. Test FP logic incrementally**

Start simple, add complexity:
```yaml
# Step 1: Match detection name only
op: is
path: cat
value: target-detection

# If this works, add more conditions
# Step 2: Add hostname check
op: and
rules:
  - op: is
    path: cat
    value: target-detection
  - op: is
    path: routing/hostname
    value: test-server-01

# Continue adding conditions until FP rule works
```

**5. Verify FP rule is enabled**
- Navigate to Automation > False Positive Rules
- Check rule is listed and not expired
- Check expiry date if set

**6. Check for typos**
- Detection name spelling
- Hostname spelling
- File path spelling
- Case sensitivity

**7. Wait for FP rule to apply**
- FP rules apply to new detections
- Existing detections in UI are not affected
- Generate new detection to test

## Rule Matching Issues

### Issue: Rule Not Matching Expected Events

**Symptoms**:
- Rule deployed successfully
- Events that should match are occurring
- No detections generated

**Diagnostic Steps**:
```bash
# Get sample event that should match
limacharlie historic view --sid SENSOR-ID \
  --start TIMESTAMP --end TIMESTAMP > sample-event.json

# Test rule with trace
limacharlie replay --rule-content rule.yaml \
  --events sample-event.json \
  --trace

# This shows exactly where matching fails
```

**Solutions**:

**1. Verify event type is correct**
```yaml
# Rule specifies
detect:
  events:
    - NEW_PROCESS

# Verify sample event has matching type
cat sample-event.json | jq '.[0].routing.event_type'
# Should output: "NEW_PROCESS"
```

**2. Check path syntax**

**Common mistakes**:
```yaml
# Wrong - missing event/ prefix
path: COMMAND_LINE

# Correct
path: event/COMMAND_LINE
```

**3. Check field exists in event**
```bash
# View event structure
cat sample-event.json | jq '.[0].event | keys'

# Check specific field
cat sample-event.json | jq '.[0].event.COMMAND_LINE'
```

**4. Check operator usage**

**Common mistakes**:
```yaml
# Wrong - using 'equals'
op: equals

# Correct - use 'is'
op: is
```

```yaml
# Wrong - using 'matches' without 're'
op: matches
path: event/FILE_PATH
value: ".*\\.exe$"

# Correct
op: matches
path: event/FILE_PATH
re: ".*\\.exe$"
```

**5. Check case sensitivity**
```yaml
# If matching fails, try case insensitive
op: contains
path: event/COMMAND_LINE
value: powershell
case sensitive: false  # Add this
```

**6. Check platform matching**
```yaml
# Ensure platform is correct
detect:
  events:
    - NEW_PROCESS
  op: and
  rules:
    - op: is windows  # or: is linux, is macos
    - # ... other conditions
```

**7. Simplify rule to test incrementally**
```yaml
# Start with minimal rule
detect:
  events:
    - NEW_PROCESS
  op: is windows
respond:
  - action: report
    name: test-minimal

# Test - should match all Windows processes
# Then add conditions one at a time
```

**8. Check for logical errors**
```yaml
# Wrong - AND requires all conditions
detect:
  op: and
  rules:
    - op: is
      path: event/FILE_PATH
      value: cmd.exe
    - op: is
      path: event/FILE_PATH
      value: powershell.exe
# FILE_PATH cannot be both - will never match

# Correct - use OR
detect:
  op: or
  rules:
    - op: is
      path: event/FILE_PATH
      value: cmd.exe
    - op: is
      path: event/FILE_PATH
      value: powershell.exe
```

### Issue: Rule Matches Too Much

**Symptoms**:
- Rule matching more than intended
- Too many detections
- Over-broad conditions

**Solutions**:

**1. Add more restrictive conditions**
```yaml
# Original - too broad
detect:
  events:
    - NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: admin

# Improved - more specific
detect:
  events:
    - NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/COMMAND_LINE
      value: admin
      case sensitive: false
    # Add context
    - op: or
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: /add
        - op: contains
          path: event/COMMAND_LINE
          value: /create
    # Exclude known-good
    - op: not
      rule:
        op: ends with
        path: event/FILE_PATH
        value: approved-admin-tool.exe
        case sensitive: false
```

**2. Use AND instead of OR**
```yaml
# Change from OR (matches any)
op: or

# To AND (matches all)
op: and
```

**3. Add parent process checks**
```yaml
# Add parent context
- op: not
  rule:
    op: ends with
    path: event/PARENT/FILE_PATH
    value: expected-parent.exe
    case sensitive: false
```

**4. Add user context**
```yaml
# Exclude service accounts
- op: not
  rule:
    op: starts with
    path: event/USER_NAME
    value: svc_
    case sensitive: false
```

## Testing Issues

### Issue: Replay Validation Fails

**Symptoms**:
- `limacharlie replay --validate` returns errors
- Syntax errors in rule

**Solutions**:

**1. Check YAML syntax**
```bash
# Validate YAML
python3 -c "import yaml; print(yaml.safe_load(open('rule.yaml')))"
```

**2. Check indentation**
- YAML requires consistent indentation
- Use spaces, not tabs
- 2-space indentation recommended

**3. Check for required fields**
```yaml
# Minimal valid rule
detect:
  events:
    - NEW_PROCESS
  op: is windows
respond:
  - action: report
    name: rule-name
```

**4. Check operator syntax**
- Use correct operator names
- Include required parameters

**5. View detailed error**
```bash
# Get full error output
limacharlie replay --validate --rule-content rule.yaml 2>&1
```

### Issue: Replay Returns No Matches

**Symptoms**:
- Rule validates successfully
- Replay against historical data returns empty
- Expected events should match

**Solutions**:

**1. Verify events exist in time range**
```bash
# Check for any events in time range
limacharlie historic view --sid SENSOR-ID \
  --start TIMESTAMP --end TIMESTAMP | head -n 10

# Check for specific event type
limacharlie historic view --sid SENSOR-ID \
  --last-seconds 3600 | \
  jq '.[] | select(.routing.event_type=="NEW_PROCESS")' | head -n 5
```

**2. Broaden time range**
```bash
# Try longer time range
limacharlie replay --rule-content rule.yaml \
  --entire-org --last-seconds 604800  # 7 days
```

**3. Simplify rule to test basic matching**
```bash
# Test with minimal rule
cat > test-minimal.yaml << 'EOF'
detect:
  events:
    - NEW_PROCESS
  op: is windows
respond:
  - action: report
    name: test
EOF

limacharlie replay --rule-content test-minimal.yaml \
  --entire-org --last-seconds 3600
```

**4. Use trace mode**
```bash
# See why rule isn't matching
limacharlie replay --rule-content rule.yaml \
  --events sample-event.json \
  --trace
```

## Performance Problems

### Issue: Slow Detection Processing

**Symptoms**:
- High latency in detection generation
- Delayed alerts
- System slowness

**Diagnostic Steps**:
```bash
# Check rule count
limacharlie dr list | wc -l

# Check for complex rules
limacharlie dr list --format json > rules.json
cat rules.json | jq '.[] | {name: .name, complexity: (.rule | length)}'
```

**Solutions**:

**1. Reduce total rule count**
```bash
# Identify unused rules
# (rules with no detections in past 30 days)

# Disable unused rules
limacharlie dr remove --rule-name unused-rule
```

**2. Optimize rule logic**
```yaml
# Bad - broad event filter
detect:
  events:
    - NEW_PROCESS
    - EXISTING_PROCESS
    - NETWORK_CONNECTIONS
    - FILE_CREATE
  # ... many conditions

# Good - specific event filter
detect:
  events:
    - NEW_PROCESS  # Only one event type
  # ... conditions
```

**3. Put restrictive conditions first**
```yaml
# Bad - expensive check first
detect:
  op: and
  rules:
    - op: matches  # Regex is expensive
      path: event/COMMAND_LINE
      re: "complex.*regex.*pattern"
    - op: is windows  # Simple check should be first

# Good - simple checks first
detect:
  op: and
  rules:
    - op: is windows  # Fast platform check
    - op: contains  # Faster string check
      path: event/COMMAND_LINE
      value: specific-string
    - op: matches  # Expensive regex last
      path: event/COMMAND_LINE
      re: "complex.*pattern"
```

**4. Use suppression for noisy rules**
```yaml
respond:
  - action: report
    name: noisy-rule
    suppression:
      max_count: 1
      period: 3600  # Once per hour max
```

**5. Avoid overly complex nested conditions**
```yaml
# Avoid deep nesting (hard to process)
# Flatten logic where possible
```

**6. Test rule performance**
```bash
# Use replay with metrics
limacharlie replay --rule-content rule.yaml \
  --entire-org --last-seconds 3600 --metrics
```

## Integration Issues

### Issue: AWS Adapter Not Ingesting Events

**Symptoms**:
- CloudTrail/GuardDuty adapter configured
- No events appearing in LimaCharlie

**Solutions**:

See [AWS Security Monitoring](#aws-security-monitoring) section above for complete setup.

**Quick checks**:
1. Test connection in integration UI
2. Verify IAM role permissions
3. Check S3 bucket has logs
4. Verify external ID matches
5. Check bucket region matches config

### Issue: M365 Adapter Not Syncing

**Symptoms**:
- Office 365 adapter configured
- No events appearing

**Solutions**:

See [M365 Threat Detection](#m365-threat-detection) section above for complete setup.

**Quick checks**:
1. Verify audit logging enabled in M365
2. Check admin account permissions
3. Re-authenticate if needed
4. Verify log types are selected
5. Check ingestion frequency

### Issue: Integration Authentication Failed

**Symptoms**:
- Cannot authenticate to AWS/M365/SOC Prime
- API key errors
- Permission errors

**Solutions**:

**1. Re-generate credentials**
- Create new API key or IAM role
- Update in LimaCharlie
- Test connection
- Revoke old credentials

**2. Verify permissions**
- Check required permissions are granted
- Verify account has appropriate role
- Check for permission changes

**3. Check for MFA issues**
- Some integrations require MFA
- Ensure MFA is configured correctly
- Try authentication flow again

[Back to Quick Start](SKILL.md) | [See Reference](REFERENCE.md) | [See Examples](EXAMPLES.md)
