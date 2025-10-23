---
name: sigma-rule-deployer
description: Use this skill when the user needs help deploying, managing, or understanding Sigma rules, Soteria rules, SOC Prime rules, Community rules, or any other managed rulesets in LimaCharlie.
---

# LimaCharlie Managed Ruleset Deployer

This skill helps you deploy and manage Sigma rules and other managed rulesets in LimaCharlie. Use this when users need help with:

- Deploying Sigma rules from SigmaHQ
- Converting Sigma rules to LimaCharlie format
- Managing Soteria EDR, AWS, or M365 rulesets
- Configuring SOC Prime rules
- Using Community Rules
- Understanding managed ruleset pricing and subscriptions
- Tuning and managing false positives
- Updating and versioning rulesets

## What are Managed Rulesets?

Managed rulesets are professionally maintained, pre-built detection rules that can be deployed with one click to a LimaCharlie organization. They provide:

- **Expert-curated detections**: Rules written by security professionals
- **Automatic updates**: Rulesets are updated as new threats emerge
- **Broad coverage**: MITRE ATT&CK framework alignment
- **Reduced maintenance**: No need to write rules from scratch
- **Cost efficiency**: Leverage community and commercial detections
- **Quick deployment**: Enable comprehensive detection in minutes

LimaCharlie supports multiple managed ruleset sources:
1. **Sigma Rules** - Open-source detection rules from SigmaHQ
2. **Soteria Rules** - Managed EDR, AWS, and M365 detection rulesets
3. **SOC Prime Rules** - Community and enterprise detection content
4. **Community Rules** - AI-assisted conversion of third-party rules

## Sigma Rules

### Overview

Sigma is an open-source project that provides a generic signature format for SIEM systems. LimaCharlie maintains a backend converter that automatically translates Sigma rules into Detection & Response (D&R) rule format.

Key features:
- **SigmaHQ integration**: Access to thousands of community rules
- **Automatic conversion**: Rules are converted to LimaCharlie D&R format
- **One-click deployment**: Apply entire rulesets with a single click
- **Custom conversion**: Convert your own Sigma rules

### SigmaHQ Rules Repository

LimaCharlie provides a service to deploy converted Sigma rules from the official SigmaHQ repository:
- Pre-converted rules available at: https://github.com/refractionPOINT/sigma-limacharlie/tree/rules
- Rules are automatically converted and maintained
- Can be applied to an organization with one click

### Sigma Converter Service

The Sigma Converter service allows you to convert custom Sigma rules or specific rules from any source.

#### Convert a Single Sigma Rule

Use the `/convert/rule` endpoint to convert one Sigma rule:

**Endpoint**: `https://sigma.limacharlie.io/convert/rule`
**Method**: POST
**Parameters**:
- `rule`: The content of a Sigma rule in YAML format
- `target`: Optional target type (`edr` or `artifact`, default: `edr`)

**Example using CURL**:
```bash
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@my-sigma-rule.yaml"
```

**Response**:
```json
{
  "rule": "detect:\n  events:\n  - NEW_PROCESS\n  - EXISTING_PROCESS\n  op: and\n  rules:\n  - op: is windows\n  - op: or\n    rules:\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: domainlist\nrespond:\n- action: report\n  metadata:\n    author: Original Author\n    description: Rule description\n  name: Rule Name\n"
}
```

#### Convert Multiple Sigma Rules

Use the `/convert/repo` endpoint to convert multiple rules from a repository or directory:

**Endpoint**: `https://sigma.limacharlie.io/convert/repo`
**Method**: POST
**Parameters**:
- `repo`: Source location, can be:
  - Direct HTTPS link: `https://corp.com/my-rules.yaml`
  - GitHub file: `https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/proc_creation_win_ad_find_discovery.yml`
  - GitHub directory: `https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation`
  - Authenticated Resource Locator (ARL)
- `target`: Optional target type (`edr` or `artifact`, default: `edr`)

**Example using CURL**:
```bash
curl -X POST https://sigma.limacharlie.io/convert/repo \
  -d "repo=https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation"
```

**Response**:
```json
{
  "rules": [
    {
      "file": "https://raw.githubusercontent.com/SigmaHQ/sigma/master/rules/windows/process_creation/proc_creation_win_ad_find_discovery.yml",
      "rule": "detect:\n  events:\n  - NEW_PROCESS\n..."
    },
    ...
  ]
}
```

### Supported Targets

Sigma rules can be converted for different targets within LimaCharlie:
- **edr** (default): For endpoint detection on sensor events
- **artifact**: For artifact collection and log analysis

### Deploying Converted Sigma Rules

Once converted, Sigma rules can be deployed as regular D&R rules:

1. **Via Web UI**: Copy the converted rule to the D&R Rules page
2. **Via CLI**: Save the rule to a file and deploy with `limacharlie dr add`
3. **Via API**: Use the REST API to create the rule programmatically
4. **Infrastructure as Code**: Include in your IaC configuration

### Sigma Rule Best Practices

1. **Review before deployment**: Converted rules should be reviewed for your environment
2. **Test with replay**: Use the replay service to test against historical data
3. **Tune for false positives**: Adjust rules based on your environment
4. **Use namespaces**: Organize Sigma rules in a dedicated namespace
5. **Monitor performance**: Some Sigma rules may need optimization

## Soteria Rules

Soteria provides professionally maintained detection rulesets for EDR, AWS, and M365 environments. These are managed rules where:
- **No data access**: Soteria doesn't access your data
- **LimaCharlie as broker**: LimaCharlie acts as an intermediary
- **No rule visibility**: You can't see or edit the rules (managed service)
- **Automatic updates**: Rules are updated by Soteria

### Soteria EDR Rules

Soteria's EDR ruleset provides comprehensive coverage across Windows, Linux, and macOS platforms.

#### MITRE ATT&CK Coverage

View dynamic MITRE ATT&CK mapping:
- **All platforms**: https://mitre-attack.github.io/attack-navigator/#layerURL=https%3A%2F%2Fstorage.googleapis.com%2Fsoteria-detector-mapping%2F%2Fall.json
- **Windows**: https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//windows.json
- **Linux**: https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//linux.json
- **macOS**: https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//mac.json

#### Required Events

Soteria EDR rules require the following events to be configured in your organization:
- `CODE_IDENTITY`
- `DNS_REQUEST`
- `EXISTING_PROCESS`
- `FILE_CREATE`
- `FILE_MODIFIED`
- `MODULE_LOAD`
- `NETWORK_CONNECTIONS`
- `NEW_DOCUMENT`
- `NEW_NAMED_PIPE`
- `NEW_PROCESS`
- `REGISTRY_WRITE`
- `REGISTRY_CREATE`
- `SENSITIVE_PROCESS_ACCESS`
- `THREAD_INJECTION`

These can be configured in the Add-ons Marketplace when subscribing to Soteria.

#### Deploying Soteria EDR Rules

**Via Web UI**:
1. Navigate to **Add-On Marketplace**
2. Go to **Extensions** section
3. Search for "Soteria" or select `soteria-rules-edr`
4. Select the organization from the dropdown
5. Click **Subscribe**
6. Manage subscriptions from **Billing > Subscriptions**

**Via Infrastructure as Code**:
Use LimaCharlie's IaC functionality to deploy at scale across multiple organizations.

### Soteria AWS Rules

Soteria's AWS ruleset provides detection coverage for AWS environments using CloudTrail and GuardDuty telemetry.

#### Supported AWS Telemetry

- **AWS CloudTrail**: API activity monitoring
- **AWS GuardDuty**: Threat detection findings

#### Prerequisites

1. Subscribe to `soteria-rules-aws` extension
2. Subscribe to `tor` lookup (provided at no cost)
3. Configure AWS CloudTrail adapter
4. Configure AWS GuardDuty adapter

#### Deploying Soteria AWS Rules

**Via Web UI**:
1. Navigate to **Add-On Marketplace**
2. Go to **Extensions** section
3. Search for "Soteria" or select `soteria-rules-aws`
4. Select the organization from the dropdown
5. Click **Subscribe**

**Via Infrastructure as Code**:
Deploy programmatically using IaC configuration.

### Soteria M365 Rules

Soteria's M365 (Office 365) ruleset provides detection coverage for Microsoft 365 environments.

#### Supported M365 Applications

- Teams
- Word
- Excel
- PowerPoint
- Outlook
- OneDrive
- Other productivity applications

#### Prerequisites

1. Subscribe to `soteria-rules-o365` extension
2. Subscribe to `tor` lookup (provided at no cost)
3. Configure Office 365 adapter to collect audit logs

#### Deploying Soteria M365 Rules

**Via Web UI**:
1. Navigate to **Add-On Marketplace**
2. Go to **Extensions** section
3. Search for "Soteria" or select `soteria-rules-o365`
4. Select the organization from the dropdown
5. Click **Subscribe**

**Via Infrastructure as Code**:
Deploy programmatically using IaC configuration.

### Soteria Rules Important Notes

- **Data privacy**: Soteria does NOT have access to your data
- **Broker model**: LimaCharlie acts as a broker between you and Soteria
- **Managed service**: You cannot view or edit Soteria rules
- **Updates**: Rules are automatically updated by Soteria
- **Pricing**: Check current pricing in the Add-On Marketplace

## SOC Prime Rules

SOC Prime provides a platform for threat detection content with both community and enterprise offerings.

### Overview

SOC Prime rules are synchronized from SOC Prime's content platform to LimaCharlie:
- **Content lists**: Organize rules in SOC Prime lists
- **Automatic sync**: Rules sync every 3 hours
- **Detection attribution**: Detections show "socprime" as author
- **Continuous updates**: New rules added to lists are automatically deployed

### Prerequisites

- **SOC Prime account**: Free users cannot access the API (trial or paid subscription required)
- **API key**: Obtain from SOC Prime platform
- **Content lists**: Configure detection lists in SOC Prime

### Configuring SOC Prime Lists

1. Visit [SOC Prime platform](https://socprime.com/)
2. Create and configure content lists
3. Learn more: https://socprime.com/blog/enable-continuous-content-management-with-the-soc-prime-platform/

### Deploying SOC Prime Rules in LimaCharlie

#### Step 1: Enable the Add-on

1. Navigate to **Add-On Marketplace**
2. Search for and enable the `socprime` add-on

#### Step 2: Configure Integration

1. Go to **Integrations** page in your organization
2. Enter your SOC Prime API key
3. Click **Update**

#### Step 3: Select Content Lists

1. After saving the API key, available content lists will appear
2. Select the lists you want to deploy
3. Click **Update**

### Sync Behavior

- **Sync frequency**: Every 3 hours
- **New rules**: Automatically added when added to selected lists
- **Rule updates**: Updated rules are synchronized
- **Attribution**: All detections show `socprime` as author

### Identifying SOC Prime Detections

Detections from SOC Prime lists will have:
- **Author**: `socprime`
- **Metadata**: Original rule metadata from SOC Prime

## Community Rules

Community Rules leverage AI to convert third-party detection rules from various sources into LimaCharlie syntax.

### Overview

The Community Rules feature provides:
- **AI-powered conversion**: Automatic translation to LimaCharlie D&R format
- **Multiple sources**: Rules from Anvilogic, Sigma, Panther, Okta
- **Thousands of rules**: Browse extensive detection library
- **Quick deployment**: One-click conversion and loading
- **Customizable**: Edit rules after conversion

### Supported Rule Sources

- **Anvilogic**: Cloud and endpoint detections
- **Sigma**: SigmaHQ community rules
- **Panther**: Cloud security detections
- **Okta**: Identity and access detections

### Accessing Community Rules

1. Log into LimaCharlie
2. Select an organization
3. Navigate to **Automation > Rules**
4. Click **Add Rule** (upper right)
5. Click **Community Library** (upper right)

### Searching Community Rules

Rules are searchable by:
- **CVE numbers**: Find rules for specific vulnerabilities
- **Keywords**: Search by technique names or descriptions
- **Tags**: Filter by MITRE ATT&CK techniques, platforms, etc.
- **MITRE ATT&CK IDs**: Search by technique IDs (e.g., T1059)

### Converting and Deploying Community Rules

#### Step 1: Find a Rule

1. Use search or tags to find desired rule
2. Click on rule to view details

#### Step 2: Load and Convert

1. Click **Load Rule** button
2. Wait a few seconds for AI conversion
3. Rule appears in Add Rule page with LimaCharlie syntax

#### Step 3: Review and Customize

1. Review the detect logic (includes explanatory comments)
2. Review the respond actions
3. Modify as needed for your environment
4. Add false positive filtering if needed

#### Step 4: Deploy

1. Provide a rule name
2. Click **Save** to deploy the rule

### Rule Details and Licensing

For each community rule, you can view:
- **Source code**: Original rule format
- **Licensing**: License information for the rule
- **References**: Links to related resources and documentation
- **Metadata**: Original author, MITRE ATT&CK mapping, etc.

### Community Rules Best Practices

1. **Always review**: AI conversion may need adjustments
2. **Test first**: Use replay to test against historical data
3. **Add context**: Include organization-specific tuning
4. **Check licensing**: Ensure compliance with rule licenses
5. **Monitor performance**: Some converted rules may need optimization

## Rule Management

### Viewing Deployed Rules

**Via Web UI**:
1. Navigate to **Automation > D&R Rules**
2. Filter by namespace or name
3. View rule details and recent detections

**Via CLI**:
```bash
limacharlie dr list
limacharlie dr get --rule-name my-rule
```

### Updating Rules

Managed rulesets (Soteria, SOC Prime) update automatically:
- **Soteria**: Rules updated by Soteria team
- **SOC Prime**: Synced every 3 hours
- **Community/Sigma**: Manual updates required

For manually deployed rules:
```bash
limacharlie dr remove --rule-name my-rule
limacharlie dr add --rule-name my-rule --rule-file updated-rule.yaml
```

### Disabling Rules

Disable rules without deleting:
```bash
limacharlie dr remove --rule-name my-rule
```

Re-enable by adding again:
```bash
limacharlie dr add --rule-name my-rule --rule-file rule.yaml
```

### Rule Versioning

**Best practices**:
1. **Use IaC**: Store rules in version control (Git)
2. **Namespace organization**: Use namespaces to separate rule types
3. **Documentation**: Include metadata with version info
4. **Testing**: Test rule changes with replay before deployment
5. **Backup**: Export rules before major changes

```bash
# Export all rules
limacharlie dr list --format json > rules-backup.json
```

### Organizing Rules with Namespaces

Rules can be organized using namespaces in rule names:
- `sigma-windows-process-creation-suspicious-cmd`
- `soteria-edr-windows-lateral-movement`
- `custom-ransomware-indicators`

This helps with:
- Filtering and searching
- Managing different rule sources
- Applying updates selectively

## False Positive Management

False positive (FP) rules filter out detections from D&R rules to reduce alert fatigue.

### What are FP Rules?

FP rules:
- Apply globally across all rule namespaces and targets
- Filter detections generated by `report` actions
- Match against detection content (not just events)
- Support expiration dates for temporary exclusions

### Common Use Cases

1. **Cross-cutting exceptions**: Ignore detections from specific hosts
2. **Organization-specific exclusions**: Exclude known software
3. **Managed rule tuning**: Suppress false positives from rules you can't edit
4. **Temporary exclusions**: Mute detections during maintenance

### Creating FP Rules from Detections

**Quick method** (from a detection):
1. Navigate to **Detections** page
2. Find a false positive detection
3. Click **Mark False Positive** button
4. Review the auto-generated rule
5. Edit if needed (add/remove conditions)
6. Save the rule

The FP rule is pre-populated with detection details.

### Creating FP Rules from Scratch

1. Navigate to **Automation > False Positive Rules**
2. Click **New Rule**
3. Define matching logic (same format as D&R detect section)
4. Optionally set an expiry date
5. Save the rule

### FP Rule Structure

FP rules use the same operators as D&R rules but match against detection content:

```yaml
# Access detection fields
op: is
path: cat  # detection name
value: my-detection-name
```

```yaml
# Access original event (use detect/ prefix)
op: ends with
path: detect/event/FILE_PATH
value: known-good.exe
case sensitive: false
```

```yaml
# Access routing information
op: is
path: routing/hostname
value: dev-server-1
```

### Example FP Rules

#### Suppress Specific Detection
```yaml
op: is
path: cat
value: my-detection-name
```

#### Ignore Detection for Specific File
```yaml
op: ends with
path: detect/event/FILE_PATH
value: legitimate-tool.exe
case sensitive: false
```

#### Ignore Detections from Specific Host
```yaml
op: is
path: routing/hostname
value: build-server-01
```

#### Ignore Detection for Multiple Hosts
```yaml
op: or
rules:
  - op: is
    path: routing/hostname
    value: dev-server-1
  - op: is
    path: routing/hostname
    value: dev-server-2
```

#### Temporary Exclusion with Expiry
```yaml
op: is
path: cat
value: maintenance-alert
# Set expiry date in UI (must be in user's local time, not UTC)
```

### FP Rule Best Practices

1. **Be specific**: Make rules as narrow as possible
2. **Use expiry dates**: For temporary exclusions (maintenance, testing)
3. **Document reasons**: Add clear rule names explaining why
4. **Regular review**: Periodically review and remove outdated FP rules
5. **Test thoroughly**: Ensure FP rules don't suppress real threats
6. **Prefer tuning**: When possible, tune the D&R rule instead of using FP rules

### Managing FP Rules

**View all FP rules**:
1. Navigate to **Automation > False Positive Rules**
2. Review active rules and expiry dates

**Edit FP rule**:
1. Click on the rule in the list
2. Modify the logic
3. Save changes

**Delete FP rule**:
1. Click on the rule
2. Click Delete

## Testing and Validation

### Testing Sigma Rules

Before deploying converted Sigma rules:

#### 1. Validate Conversion
```bash
# Convert and save the rule
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@sigma-rule.yaml" > converted-rule.json

# Extract rule content
cat converted-rule.json | jq -r '.rule' > lc-rule.yaml

# Validate syntax
limacharlie replay --validate --rule-content lc-rule.yaml
```

#### 2. Test Against Historical Data
```bash
# Test against recent data
limacharlie replay --rule-content lc-rule.yaml \
  --entire-org --last-seconds 604800

# Test against specific sensor
limacharlie replay --sid SENSOR_ID \
  --start 1556568500 --end 1556568600 \
  --rule-content lc-rule.yaml
```

#### 3. Add Unit Tests

Include test cases in the rule:
```yaml
detect:
  # ... detection logic
respond:
  # ... response actions
tests:
  match:
    - - event:
          COMMAND_LINE: cmd.exe /c powershell.exe -enc abc123
          FILE_PATH: C:\Windows\System32\cmd.exe
        routing:
          event_type: NEW_PROCESS
  non_match:
    - - event:
          COMMAND_LINE: cmd.exe /c dir
          FILE_PATH: C:\Windows\System32\cmd.exe
        routing:
          event_type: NEW_PROCESS
```

### Testing Managed Rulesets

For Soteria and SOC Prime rules:

#### 1. Monitor Initial Detections
- Enable rules in a test/staging org first
- Monitor detections for 24-48 hours
- Identify false positives

#### 2. Create FP Rules
- Create FP rules for known false positives
- Test FP rules with replay if possible

#### 3. Gradual Rollout
- Deploy to production organization
- Continue monitoring for new false positives
- Refine FP rules as needed

### Testing Community Rules

#### 1. Review Converted Logic
- Check that the logic makes sense
- Verify event types are available in your environment
- Review any comments added by AI conversion

#### 2. Validate Syntax
```bash
limacharlie replay --validate --rule-content community-rule.yaml
```

#### 3. Test with Sample Events
Create test events matching the rule:
```bash
limacharlie replay --rule-content community-rule.yaml \
  --events test-events.json
```

#### 4. Replay Against Real Data
```bash
limacharlie replay --rule-content community-rule.yaml \
  --entire-org --last-seconds 86400
```

### Trace Mode for Debugging

Use trace mode to see detailed rule evaluation:
```bash
limacharlie replay --rule-content rule.yaml \
  --events test-event.json --trace
```

This shows:
- Which operators matched/failed
- Path values at each step
- Why rules didn't match

## Best Practices

### Ruleset Selection

**Choose the right ruleset for your needs**:

| Ruleset | Best For | Pros | Cons |
|---------|----------|------|------|
| **Sigma** | Open-source coverage, custom rules | Free, customizable, large community | Requires tuning, manual updates |
| **Soteria EDR** | Comprehensive EDR coverage | Professional maintenance, auto-updates | Paid, no rule visibility |
| **Soteria AWS** | AWS security monitoring | Cloud-native detections, auto-updates | Paid, requires AWS adapters |
| **Soteria M365** | M365/O365 security | SaaS app coverage, auto-updates | Paid, requires M365 adapter |
| **SOC Prime** | Enterprise content management | Continuous updates, content lists | Requires paid SOC Prime subscription |
| **Community** | Quick starts, specific detections | AI-assisted, many sources | May need tuning, manual process |

### Deployment Strategy

**Recommended deployment approach**:

1. **Start with high-fidelity rulesets**
   - Soteria rules for managed coverage
   - SOC Prime for enterprise content

2. **Add broad coverage**
   - Deploy Sigma rules for common threats
   - Use Community Rules for specific techniques

3. **Customize and tune**
   - Create custom rules for organization-specific threats
   - Add FP rules to reduce noise

4. **Continuous improvement**
   - Monitor detection quality
   - Refine rules based on feedback
   - Keep rulesets updated

### Rule Tuning

**Effective tuning process**:

1. **Baseline**
   - Deploy rules in monitoring mode
   - Collect 1-2 weeks of detections
   - Identify patterns in false positives

2. **Categorize false positives**
   - Legitimate business activity
   - Known tools and software
   - Test/development environments
   - Misconfigured rules

3. **Apply appropriate fixes**
   - Create FP rules for legitimate activity
   - Modify custom rules for better precision
   - Exclude test environments with FP rules
   - Report issues with managed rulesets

4. **Monitor and iterate**
   - Track false positive rate
   - Adjust as environment changes
   - Review FP rules periodically

### Performance Optimization

**Keep rulesets performant**:

1. **Rule count management**
   - Don't deploy everything at once
   - Focus on high-priority threats first
   - Disable unused rules

2. **Rule optimization**
   - Put restrictive conditions first
   - Use appropriate operators
   - Avoid overly broad rules

3. **Suppression usage**
   - Use suppression for noisy rules
   - Prevent alert fatigue
   - Reduce processing overhead

4. **Resource monitoring**
   - Monitor rule evaluation metrics
   - Identify slow rules with replay
   - Optimize or disable problematic rules

### Multi-Organization Management

**For MSSPs and enterprises**:

1. **Use Infrastructure as Code**
   - Define rulesets in configuration files
   - Deploy consistently across organizations
   - Version control all changes

2. **Template approach**
   - Create base ruleset templates
   - Customize per organization
   - Use variables for org-specific values

3. **Centralized FP management**
   - Common FP rules in templates
   - Org-specific FP rules as overlays
   - Regular review and cleanup

4. **Subscription management**
   - Track addon subscriptions
   - Monitor costs across orgs
   - Optimize subscription allocation

### Security and Compliance

**Maintain security posture**:

1. **Regular updates**
   - Update Sigma rules monthly
   - Monitor Soteria/SOC Prime updates
   - Review new Community Rules

2. **Coverage validation**
   - Map rules to MITRE ATT&CK
   - Identify coverage gaps
   - Test detection effectiveness

3. **Documentation**
   - Document ruleset decisions
   - Maintain FP rule rationale
   - Track rule changes

4. **Compliance alignment**
   - Map rules to compliance requirements
   - Maintain audit trail
   - Regular effectiveness reviews

## CLI Reference

### Sigma Rule Conversion

```bash
# Convert single rule
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@sigma-rule.yaml"

# Convert multiple rules from GitHub
curl -X POST https://sigma.limacharlie.io/convert/repo \
  -d "repo=https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation"

# Convert with artifact target
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@sigma-rule.yaml" \
  -d "target=artifact"
```

### Rule Deployment

```bash
# List all rules
limacharlie dr list

# Add a rule
limacharlie dr add --rule-name my-rule --rule-file rule.yaml

# Get rule details
limacharlie dr get --rule-name my-rule

# Remove a rule
limacharlie dr remove --rule-name my-rule

# Export all rules
limacharlie dr list --format json > rules-backup.json
```

### Rule Testing

```bash
# Validate rule syntax
limacharlie replay --validate --rule-content rule.yaml

# Test against single event
limacharlie replay --rule-content rule.yaml --events event.json

# Test against recent data
limacharlie replay --rule-content rule.yaml \
  --entire-org --last-seconds 604800

# Test with trace output
limacharlie replay --rule-content rule.yaml \
  --events event.json --trace

# Test against specific sensor
limacharlie replay --sid SENSOR_ID \
  --start 1556568500 --end 1556568600 \
  --rule-content rule.yaml
```

## Common Deployment Scenarios

### Scenario 1: New Organization Setup

**Goal**: Deploy comprehensive detection coverage quickly

**Steps**:
1. Subscribe to Soteria EDR rules for baseline coverage
2. Enable SOC Prime community rules (if available)
3. Deploy high-confidence Sigma rules for critical threats
4. Configure outputs for detections
5. Monitor for 1 week and create FP rules
6. Add custom rules for org-specific threats

**Example**:
```bash
# Via CLI (Infrastructure as Code approach)
# Add Soteria subscription (done via UI or API)

# Deploy critical Sigma rules
for rule in sigma-rules-critical/*.yaml; do
  name=$(basename "$rule" .yaml)
  limacharlie dr add --rule-name "sigma-$name" --rule-file "$rule"
done

# Test deployment
limacharlie dr list | grep sigma
```

### Scenario 2: AWS Security Monitoring

**Goal**: Detect threats in AWS environment

**Steps**:
1. Configure AWS CloudTrail adapter
2. Configure AWS GuardDuty adapter
3. Subscribe to Soteria AWS rules
4. Subscribe to TOR lookup (free)
5. Deploy relevant Sigma rules for AWS
6. Create custom rules for AWS policies

**Prerequisites**:
```bash
# Verify adapters are configured
limacharlie adapter list

# Should see cloudtrail and guardduty adapters
```

### Scenario 3: M365 Threat Detection

**Goal**: Monitor Microsoft 365 for security threats

**Steps**:
1. Configure Office 365 adapter
2. Subscribe to Soteria M365 rules
3. Subscribe to TOR lookup (free)
4. Deploy Sigma rules for O365 (if available)
5. Add custom rules for email security
6. Configure email outputs for high-priority alerts

### Scenario 4: Custom Threat Hunting

**Goal**: Hunt for specific threat actor TTPs

**Steps**:
1. Research threat actor techniques
2. Search Community Rules for relevant detections
3. Convert and customize rules
4. Test rules against historical data
5. Deploy with appropriate alerting
6. Create hunting queries for additional coverage

**Example**:
```bash
# Test custom hunting rule
limacharlie replay --rule-content hunting-rule.yaml \
  --entire-org --last-seconds 2592000  # 30 days

# Deploy if findings are valuable
limacharlie dr add --rule-name custom-hunt-apt29 \
  --rule-file hunting-rule.yaml
```

### Scenario 5: Managed Service Provider (MSP)

**Goal**: Deploy and manage rules across multiple client organizations

**Steps**:
1. Create baseline ruleset template
2. Use IaC to deploy across organizations
3. Customize per client with variables
4. Centralize FP rule management
5. Monitor subscription costs
6. Provide reporting to clients

**IaC Example Structure**:
```
rules/
  baseline/
    soteria-edr.yaml (subscription config)
    sigma-critical/ (common Sigma rules)
    fp-common.yaml (common FP rules)
  client-overrides/
    client-a/
      custom-rules/
      fp-rules.yaml
    client-b/
      custom-rules/
      fp-rules.yaml
```

## Troubleshooting

### Issue: Sigma Conversion Fails

**Symptoms**: Conversion API returns error or invalid rule

**Solutions**:
1. Verify Sigma rule syntax is valid
2. Check if rule uses unsupported features
3. Try converting with different target (edr/artifact)
4. Check LimaCharlie backend support for rule type
5. Manually adjust converted rule if needed

**Example**:
```bash
# Test Sigma rule validity with sigmac (if available)
sigmac -t limacharlie sigma-rule.yaml

# Try conversion with explicit target
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@sigma-rule.yaml" \
  -d "target=edr"
```

### Issue: No Detections from Soteria Rules

**Symptoms**: Soteria rules subscribed but no detections appearing

**Solutions**:
1. Verify required events are configured
2. Check if sensors are sending telemetry
3. Verify subscription is active (Billing > Subscriptions)
4. Wait 24-48 hours for rules to activate fully
5. Check if sensors are online and reporting

**Verification**:
```bash
# Check sensor status
limacharlie sensor list

# Verify event collection
limacharlie sensor view --sid SENSOR_ID

# Check subscription status via UI
# Navigate to Billing > Subscriptions
```

### Issue: SOC Prime Rules Not Syncing

**Symptoms**: SOC Prime rules not appearing or updating

**Solutions**:
1. Verify API key is valid
2. Check that lists are selected in integration settings
3. Verify SOC Prime subscription is active (not free tier)
4. Wait for next 3-hour sync cycle
5. Check if lists contain rules in SOC Prime platform

**Verification**:
```bash
# List rules with socprime author
limacharlie dr list | grep socprime

# Check integration configuration via UI
# Navigate to Integrations > SOC Prime
```

### Issue: Community Rules Fail to Convert

**Symptoms**: AI conversion returns error or incomplete rule

**Solutions**:
1. Try again (AI conversion can be inconsistent)
2. Review source rule for complexity
3. Manually adjust after conversion
4. Use similar rule as starting point
5. Report issue if consistently failing

**Workaround**:
1. Find similar rule that converts successfully
2. Load and save that rule
3. Manually edit to match desired logic

### Issue: High False Positive Rate

**Symptoms**: Too many false positive detections

**Solutions**:
1. Create FP rules from detections
2. Tune D&R rules if custom
3. Adjust thresholds (count, time windows)
4. Exclude test environments
5. Report issues with managed rules

**Systematic approach**:
```bash
# Export recent detections
limacharlie detections list --last-seconds 86400 > detections.json

# Analyze for patterns
cat detections.json | jq '.[] | select(.cat=="rule-name") | .routing.hostname' | sort | uniq -c

# Create FP rule for common false positives
# Navigate to Automation > False Positive Rules
```

### Issue: Rules Not Matching Expected Events

**Symptoms**: Rule deployed but not triggering on expected events

**Solutions**:
1. Use replay with trace mode to debug
2. Check event structure in Historic View
3. Verify event type is correct
4. Check path syntax and case sensitivity
5. Test with sample events

**Debug process**:
```bash
# Get sample event
limacharlie historic view --sid SENSOR_ID --start [timestamp] --end [timestamp] > events.json

# Test rule with trace
limacharlie replay --rule-content rule.yaml \
  --events events.json --trace

# This shows exactly where rule fails to match
```

### Issue: Performance Problems

**Symptoms**: Slow detection processing or high latency

**Solutions**:
1. Reduce number of active rules
2. Optimize rule logic (put restrictive conditions first)
3. Use more specific event filters
4. Add suppression to noisy rules
5. Disable unused rules

**Optimization**:
```bash
# List all active rules
limacharlie dr list

# Identify and disable unused rules
limacharlie dr remove --rule-name unused-rule

# Test rule performance
limacharlie replay --rule-content rule.yaml \
  --entire-org --last-seconds 3600 --metrics
```

## Additional Resources

### Documentation Links

- **Sigma Project**: https://github.com/SigmaHQ/sigma
- **Sigma Converter Service**: https://sigma.limacharlie.io/
- **Converted Sigma Rules**: https://github.com/refractionPOINT/sigma-limacharlie/tree/rules
- **SOC Prime Platform**: https://socprime.com/
- **LimaCharlie D&R Rules**: Detection and Response rule documentation
- **False Positive Rules**: FP rule documentation
- **Replay Service**: Testing and validation documentation

### MITRE ATT&CK Resources

- **Soteria EDR Coverage**: https://storage.googleapis.com/soteria-detector-mapping//all.json
- **ATT&CK Navigator**: https://mitre-attack.github.io/attack-navigator/

### Add-on Marketplace

- **Soteria EDR**: `soteria-rules-edr`
- **Soteria AWS**: `soteria-rules-aws`
- **Soteria M365**: `soteria-rules-o365`
- **SOC Prime**: `socprime`
- **TOR Lookup**: `tor-ips` (free)

### Support and Community

- **LimaCharlie Slack**: Community support and discussions
- **LimaCharlie Documentation**: Comprehensive technical documentation
- **GitHub Issues**: Report bugs and feature requests
- **Support Email**: Contact support for managed ruleset issues

## Summary

This skill provides comprehensive guidance for deploying and managing:

1. **Sigma Rules**: Convert and deploy open-source detection rules
2. **Soteria Rules**: Managed professional rulesets for EDR, AWS, and M365
3. **SOC Prime Rules**: Enterprise content management platform integration
4. **Community Rules**: AI-assisted conversion of third-party rules
5. **False Positive Management**: Tune and optimize detection quality
6. **Testing and Validation**: Ensure rules work correctly before production
7. **Best Practices**: Follow proven approaches for ruleset deployment

When helping users, always:
- Understand their environment and needs
- Recommend appropriate rulesets
- Guide through testing before production deployment
- Help tune for false positives
- Provide troubleshooting assistance
- Encourage Infrastructure as Code for scale

Managed rulesets provide immediate security value while custom rules offer flexibility. The best approach combines both for comprehensive, tuned detection coverage.
