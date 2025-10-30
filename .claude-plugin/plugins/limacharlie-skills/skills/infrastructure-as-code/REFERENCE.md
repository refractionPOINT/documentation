# Infrastructure as Code - Complete Reference

This document provides the complete configuration format, all YAML sections, REST API parameters, and technical details for LimaCharlie Infrastructure as Code.

## Table of Contents

- [REST API Parameters](#rest-api-parameters)
- [Complete YAML Configuration Structure](#complete-yaml-configuration-structure)
- [Configuration Sections](#configuration-sections)
- [Path Resolution in Include Files](#path-resolution-in-include-files)
- [Git Sync Schedules](#git-sync-schedules)
- [Template-Based Deployment](#template-based-deployment)
- [Python SDK for Programmatic Management](#python-sdk-for-programmatic-management)
- [Organization Groups](#organization-groups)
- [Version Control Best Practices](#version-control-best-practices)
- [Testing Configurations](#testing-configurations)
- [Advanced Use Cases](#advanced-use-cases)

## REST API Parameters

The Infrastructure extension accepts these parameters via REST API:

```json
{
  "action": "push",              // Required: "push" or "fetch"
  "config": "YAML_STRING",       // Config to apply
  "config_source": "ARL",        // ARL where configs are located
  "config_root": "index.yaml",   // Root config filename
  "is_force": true,              // Make org exact copy of config
  "is_dry_run": true,            // Simulate without applying
  "sync_dr": true,               // Apply to D&R rules
  "sync_fp": true,               // Apply to false positive rules
  "sync_outputs": true,          // Apply to outputs
  "sync_resources": true,        // Apply to resources
  "sync_artifacts": true,        // Apply to artifacts
  "sync_integrity": true,        // Apply to integrity rules
  "sync_exfil": true,            // Apply to exfil rules
  "sync_org_values": true,       // Apply to org values
  "ignore_inaccessible": true    // Ignore locked/segmented resources
}
```

## Complete YAML Configuration Structure

### Full Configuration Example

```yaml
version: 3

# Detection & Response Rules
rules:
  - name: suspicious-powershell
    detect:
      event: NEW_PROCESS
      op: contains
      path: event/COMMAND_LINE
      value: powershell
      case sensitive: false
    respond:
      - action: report
        name: Suspicious PowerShell Execution
        priority: 3
        metadata:
          author: Security Team
          version: 1.0
    tests:
      match:
        - - event:
              FILE_PATH: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
              COMMAND_LINE: powershell -enc base64string
              PROCESS_ID: 1234
            routing:
              event_type: NEW_PROCESS
      non_match:
        - - event:
              FILE_PATH: C:\Windows\System32\cmd.exe
              COMMAND_LINE: cmd.exe /c dir
              PROCESS_ID: 5678
            routing:
              event_type: NEW_PROCESS

# False Positive Rules
fp:
  - name: whitelist-system-powershell
    op: is
    path: detect/event/FILE_PATH
    value: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
  - name: whitelist-admin-user
    op: is
    path: detect/event/USER_NAME
    value: admin-automation

# Outputs
outputs:
  - name: slack-security-alerts
    module: slack
    for: detection
    slack_api_token: hive://secret/slack-token
    slack_channel: "#security-alerts"
    is_no_delta: false
    is_delete_on_failure: false

  - name: siem-integration
    module: syslog
    for: event
    dest_host: siem.company.com
    dest_port: 514
    filters:
      tags:
        - vip
        - critical
      platforms:
        - windows
        - linux

  - name: s3-backup
    module: s3
    for: detect
    bucket: security-detections
    key_id: hive://secret/aws-key-id
    secret_key: hive://secret/aws-secret-key
    sec_per_file: 3600
    dir: detections/

# Installation Keys
installation_keys:
  - description: windows-workstations
    tags:
      - windows
      - workstation
      - production
  - description: linux-servers
    tags:
      - linux
      - server
      - production
  - description: mac-endpoints
    tags:
      - macos
      - workstation

# Extensions
extensions:
  - ext-infrastructure
  - ext-git-sync
  - binlib
  - ext-artifact-collection
  - ext-responder

# Organization Values
org_values:
  - name: slack_webhook_url
    value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
  - name: siem_host
    value: siem.company.com
  - name: environment
    value: production

# Resources (API Keys, Service Accounts)
resources:
  api_keys:
    - name: automation-key
      permissions:
        - dr.list
        - dr.set
        - sensor.list
        - sensor.task
    - name: readonly-key
      permissions:
        - dr.list
        - sensor.list

# Hive Data (organized by hive type)
hive:
  # Detection & Response rules in Hive
  dr-general:
    - name: credential-dumping
      enabled: true
      data:
        detect:
          event: NEW_PROCESS
          op: ends with
          path: event/FILE_PATH
          value: mimikatz.exe
          case sensitive: false
        respond:
          - action: report
            name: Credential Dumping Tool Detected
            priority: 5
          - action: task
            command: deny_tree <<routing/this>>
          - action: isolate network

  # Managed D&R rules (from LimaCharlie-managed rules)
  dr-managed:
    - name: lc-managed-ransomware
      enabled: true
      data:
        detect:
          event: NEW_DOCUMENT
          op: matches
          path: event/FILE_PATH
          re: \.(encrypted|locked)$
        respond:
          - action: report
            name: Ransomware File Activity
            priority: 5

  # False Positive rules in Hive
  fp:
    - name: fp-benign-powershell
      enabled: true
      data:
        op: is
        path: detect/event/FILE_PATH
        value: C:\Program Files\App\powershell.exe

  # Lookup tables
  lookup:
    - name: malicious-domains
      enabled: true
      data: |
        evil.com
        malware.net
        badactor.org
        phishing-site.xyz

  # YARA signatures
  yara:
    - name: ransomware-indicators
      enabled: true
      data: |
        rule ransomware_pattern {
          meta:
            author = "Security Team"
            description = "Detects ransomware patterns"
          strings:
            $s1 = "DECRYPT_INSTRUCTION" ascii
            $s2 = ".encrypted" ascii
            $s3 = "bitcoin" nocase
          condition:
            2 of them
        }

  # Secrets
  secret:
    - name: aws-access-key
      enabled: true
      data: "YOUR_AWS_ACCESS_KEY"
    - name: aws-secret-key
      enabled: true
      data: "YOUR_AWS_SECRET_KEY"
    - name: slack-token
      enabled: true
      data: "xoxb-your-slack-token"
    - name: okta-api-key
      enabled: true
      data: "your-okta-api-key"

  # Cloud sensors
  cloud_sensor:
    - name: aws-cloudtrail
      enabled: true
      data:
        sensor_type: s3
        s3:
          bucket_name: my-cloudtrail-logs
          secret_key: hive://secret/aws-secret-key
          access_key: hive://secret/aws-access-key
          is_indexless: false
          client_options:
            identity:
              oid: YOUR_OID
              installation_key: YOUR_KEY
            platform: aws
            sensor_seed_key: aws-cloudtrail

    - name: okta-logs
      enabled: true
      data:
        sensor_type: okta
        okta:
          apikey: hive://secret/okta-api-key
          url: https://company.okta.com
          client_options:
            identity:
              oid: YOUR_OID
              installation_key: YOUR_KEY
            platform: json
            sensor_seed_key: okta-logs

    - name: microsoft-365
      enabled: true
      data:
        sensor_type: office365
        office365:
          tenant_id: hive://secret/o365-tenant-id
          client_id: hive://secret/o365-client-id
          client_secret: hive://secret/o365-client-secret
          content_types:
            - Audit.AzureActiveDirectory
            - Audit.Exchange
            - Audit.SharePoint
            - Audit.General
          client_options:
            identity:
              oid: YOUR_OID
              installation_key: YOUR_KEY
            platform: office365
            sensor_seed_key: o365-audit

    - name: gcp-audit-logs
      enabled: true
      data:
        sensor_type: gcp
        gcp:
          project_id: your-gcp-project
          credentials: hive://secret/gcp-credentials
          client_options:
            identity:
              oid: YOUR_OID
              installation_key: YOUR_KEY
            platform: gcp
            sensor_seed_key: gcp-audit

# Integrity rules
integrity:
  - name: monitor-system32
    patterns:
      - C:\Windows\System32\*.exe
      - C:\Windows\System32\*.dll
    platforms:
      - windows
    tags:
      - critical

# Exfil rules
exfil:
  - name: watch-sensitive-files
    event: NEW_DOCUMENT
    op: starts with
    path: event/FILE_PATH
    value: C:\ProgramData\Sensitive\
    tags:
      - sensitive-data
```

### Include Files Structure

**index.yaml** (root configuration):
```yaml
version: 3
include:
  - rules/detection-rules.yaml
  - rules/fp-rules.yaml
  - outputs/outputs.yaml
  - resources/resources.yaml
  - hives/dr-general.yaml
  - hives/dr-managed.yaml
  - hives/fp.yaml
  - hives/lookup.yaml
  - hives/yara.yaml
  - hives/secret.yaml
  - hives/cloud_sensor.yaml
  - extensions.yaml
  - installation_keys.yaml
  - org_values.yaml
  - integrity.yaml
  - exfil.yaml
```

## Configuration Sections

### Rules Section

D&R rules detect events and trigger responses:

```yaml
rules:
  - name: rule-name
    detect:
      event: EVENT_TYPE
      op: OPERATOR
      path: event/FIELD_PATH
      value: VALUE
      case sensitive: false
    respond:
      - action: report
        name: Detection Name
        priority: 1-5
        metadata:
          key: value
      - action: task
        command: COMMAND_NAME
      - action: isolate network
    tests:
      match:
        - - event:
              FIELD: value
            routing:
              event_type: EVENT_TYPE
      non_match:
        - - event:
              FIELD: value
            routing:
              event_type: EVENT_TYPE
```

**Common Operators**:
- `is` - Exact match
- `contains` - Substring match
- `starts with` - Prefix match
- `ends with` - Suffix match
- `matches` - Regex match (use `re:` parameter)
- `exists` - Field exists
- `and` - Logical AND (use `rules:` list)
- `or` - Logical OR (use `rules:` list)
- `is greater than` - Numeric comparison
- `is lower than` - Numeric comparison

**Common Actions**:
- `report` - Generate detection
- `task` - Execute sensor command
- `isolate network` - Network isolation
- `extension request` - Call extension
- `service request` - Call LimaCharlie service

### False Positive Section

FP rules filter out unwanted detections:

```yaml
fp:
  - name: fp-name
    op: OPERATOR
    path: detect/event/FIELD_PATH
    value: VALUE
    case sensitive: false
```

### Outputs Section

Outputs send data to external systems:

```yaml
outputs:
  - name: output-name
    module: MODULE_TYPE
    for: detection|event|deployment|audit
    # Module-specific parameters
    is_no_delta: false
    is_delete_on_failure: false
    filters:
      tags:
        - tag1
        - tag2
      platforms:
        - windows
        - linux
```

**Common Output Modules**:
- `slack` - Slack integration
- `syslog` - Syslog/SIEM
- `s3` - AWS S3
- `gcs` - Google Cloud Storage
- `webhook` - HTTP webhooks
- `email` - Email notifications
- `humio` - Humio integration
- `kafka` - Apache Kafka
- `splunk` - Splunk HEC

**Slack Output**:
```yaml
outputs:
  - name: slack-alerts
    module: slack
    for: detection
    slack_api_token: hive://secret/slack-token
    slack_channel: "#security-alerts"
```

**Syslog Output**:
```yaml
outputs:
  - name: siem-integration
    module: syslog
    for: event
    dest_host: siem.company.com
    dest_port: 514
    is_tls: true
```

**S3 Output**:
```yaml
outputs:
  - name: s3-backup
    module: s3
    for: detect
    bucket: security-detections
    key_id: hive://secret/aws-key-id
    secret_key: hive://secret/aws-secret-key
    sec_per_file: 3600
    dir: detections/
```

**Webhook Output**:
```yaml
outputs:
  - name: webhook-integration
    module: webhook
    for: detection
    dest_host: https://api.company.com/webhooks/security
    secret_key: hive://secret/webhook-secret
```

### Installation Keys Section

Installation keys for sensor enrollment:

```yaml
installation_keys:
  - description: key-description
    tags:
      - tag1
      - tag2
      - tag3
```

### Extensions Section

Extensions to enable:

```yaml
extensions:
  - ext-infrastructure
  - ext-git-sync
  - binlib
  - ext-artifact-collection
  - ext-responder
  - ext-yara
  - ext-zeek
```

### Organization Values Section

Key-value pairs for organization configuration:

```yaml
org_values:
  - name: variable-name
    value: variable-value
```

### Resources Section

API keys and service accounts:

```yaml
resources:
  api_keys:
    - name: key-name
      permissions:
        - permission1
        - permission2
```

**Common Permissions**:
- `dr.list` - List D&R rules
- `dr.set` - Modify D&R rules
- `sensor.list` - List sensors
- `sensor.task` - Task sensors
- `org.get` - Get org info
- `user.get` - Get user info

### Hive Section

#### Hive: dr-general

General detection rules stored in Hive:

```yaml
hive:
  dr-general:
    - name: rule-name
      enabled: true
      data:
        detect:
          event: EVENT_TYPE
          op: OPERATOR
          path: event/FIELD
          value: VALUE
        respond:
          - action: report
            name: Detection Name
```

#### Hive: dr-managed

Managed detection rules from LimaCharlie:

```yaml
hive:
  dr-managed:
    - name: managed-rule-name
      enabled: true
      data:
        detect:
          # Detection logic
        respond:
          # Response actions
```

#### Hive: fp

False positive rules in Hive:

```yaml
hive:
  fp:
    - name: fp-name
      enabled: true
      data:
        op: OPERATOR
        path: detect/event/FIELD
        value: VALUE
```

#### Hive: lookup

Lookup tables:

```yaml
hive:
  lookup:
    - name: table-name
      enabled: true
      data: |
        value1
        value2
        value3
```

#### Hive: yara

YARA signatures:

```yaml
hive:
  yara:
    - name: yara-rule-name
      enabled: true
      data: |
        rule rule_name {
          meta:
            author = "Security Team"
            description = "Description"
          strings:
            $s1 = "string1" ascii
            $s2 = "string2" wide
          condition:
            any of them
        }
```

#### Hive: secret

Secrets and credentials:

```yaml
hive:
  secret:
    - name: secret-name
      enabled: true
      data: "secret-value"
```

#### Hive: cloud_sensor

Cloud integrations:

```yaml
hive:
  cloud_sensor:
    - name: integration-name
      enabled: true
      data:
        sensor_type: TYPE
        TYPE:
          # Type-specific config
          client_options:
            identity:
              oid: YOUR_OID
              installation_key: YOUR_KEY
            platform: PLATFORM
            sensor_seed_key: SEED_KEY
```

**Supported Cloud Sensor Types**:
- `s3` - AWS S3/CloudTrail
- `okta` - Okta logs
- `office365` - Microsoft 365
- `gcp` - Google Cloud Platform
- `azure` - Azure logs
- `carbon_black` - Carbon Black
- `crowdstrike` - CrowdStrike

### Integrity Section

Integrity monitoring rules:

```yaml
integrity:
  - name: monitor-name
    patterns:
      - /path/to/monitor/*
      - C:\Windows\System32\*.exe
    platforms:
      - windows
      - linux
      - macos
    tags:
      - critical
```

### Exfil Section

Data exfiltration monitoring:

```yaml
exfil:
  - name: exfil-rule-name
    event: EVENT_TYPE
    op: OPERATOR
    path: event/FIELD
    value: VALUE
    tags:
      - sensitive-data
    platforms:
      - windows
      - linux
```

## Path Resolution in Include Files

Paths in `include` statements are relative to the file containing the include:

```yaml
# File: /configs/index.yaml
version: 3
include:
  - rules/detections.yaml      # Resolves to /configs/rules/detections.yaml
  - ../shared/common.yaml       # Resolves to /shared/common.yaml
  - outputs/slack.yaml          # Resolves to /configs/outputs/slack.yaml
```

**Absolute vs Relative Paths**:
- Relative paths are resolved from the file's directory
- Use `../` to navigate up directory levels
- Use `./` for current directory (optional)

## Git Sync Schedules

Schedules are D&R rules that trigger on time intervals:

### Pull Schedule (Sync FROM Git)

```yaml
detect:
  target: schedule
  event: SCHEDULE_EVERY_5_MIN
  op: exists
  path: routing/hostname
respond:
  - action: extension request
    extension name: git-sync
    extension action: pull
```

### Push Schedule (Export TO Git)

```yaml
detect:
  target: schedule
  event: SCHEDULE_DAILY
  op: exists
  path: routing/hostname
respond:
  - action: extension request
    extension name: git-sync
    extension action: push
```

### Available Schedule Events

- `SCHEDULE_EVERY_1_MIN` - Every minute
- `SCHEDULE_EVERY_5_MIN` - Every 5 minutes
- `SCHEDULE_EVERY_15_MIN` - Every 15 minutes
- `SCHEDULE_EVERY_30_MIN` - Every 30 minutes
- `SCHEDULE_HOURLY` - Every hour
- `SCHEDULE_DAILY` - Once per day
- `SCHEDULE_WEEKLY` - Once per week

## Template-Based Deployment

### Creating Templates

**templates/standard-endpoint.yaml**:
```yaml
version: 3
rules:
  - name: suspicious-powershell
    detect:
      event: NEW_PROCESS
      op: contains
      path: event/COMMAND_LINE
      value: powershell
      case sensitive: false
    respond:
      - action: report
        name: Suspicious PowerShell

outputs:
  - name: syslog-output
    module: syslog
    for: detection
    dest_host: PLACEHOLDER_SYSLOG_HOST
    dest_port: 514

installation_keys:
  - description: windows-endpoints
    tags:
      - windows
```

### Deployment Script

```bash
#!/bin/bash

# Deploy template to new organization
ORG_ID="new-org-id"
SYSLOG_HOST="syslog.customer.com"

# Substitute placeholders
sed "s/PLACEHOLDER_SYSLOG_HOST/$SYSLOG_HOST/g" templates/standard-endpoint.yaml > /tmp/config.yaml

# Apply configuration
limacharlie configs push --oid $ORG_ID --config /tmp/config.yaml --all
```

### Using Environment Variables

**config.template.yaml**:
```yaml
version: 3
outputs:
  - name: siem-output
    module: syslog
    for: event
    dest_host: ${SIEM_HOST}
    dest_port: ${SIEM_PORT}

installation_keys:
  - description: ${ENVIRONMENT}-endpoints
    tags:
      - ${ENVIRONMENT}
```

**Deploy script**:
```bash
#!/bin/bash
export ENVIRONMENT="production"
export SIEM_HOST="siem.prod.company.com"
export SIEM_PORT="514"

# Substitute variables
envsubst < config.template.yaml > config.yaml

# Apply
limacharlie configs push --config config.yaml --all
```

## Python SDK for Programmatic Management

### Basic Usage

```python
import limacharlie
import yaml

# Initialize manager
mgr = limacharlie.Manager(
    oid="your-org-id",
    secret_api_key="your-api-key"
)

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Use Configs object to push configuration
configs = limacharlie.Configs(mgr)
configs.push(config, is_force=False)
```

### Multi-Organization Management

```python
import limacharlie
import yaml

# Organizations to manage
orgs = [
    {"oid": "org-1", "api_key": "key-1"},
    {"oid": "org-2", "api_key": "key-2"},
    {"oid": "org-3", "api_key": "key-3"},
]

# Load global configuration
with open("global-rules.yaml", "r") as f:
    global_config = yaml.safe_load(f)

# Apply to all organizations
for org_info in orgs:
    mgr = limacharlie.Manager(
        oid=org_info["oid"],
        secret_api_key=org_info["api_key"]
    )

    # Use Configs object to push configuration
    configs = limacharlie.Configs(mgr)
    configs.push(global_config, is_force=False)

    print(f"Applied config to {org_info['oid']}")
```

### Dry Run with Python SDK

```python
import limacharlie
import yaml

mgr = limacharlie.Manager(oid="org-id", secret_api_key="api-key")

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

configs = limacharlie.Configs(mgr)

# Dry run
result = configs.push(config, is_force=False, is_dry_run=True)

print("Dry run results:")
print(result)
```

## Organization Groups

Organization Groups allow centralized management of multiple organizations:

### Creating Organization Groups

1. Navigate to LimaCharlie web UI
2. Click Organization Groups
3. Create New Group
4. Add organizations to the group

### Benefits

- Centralized billing
- Shared configurations
- Bulk operations
- Unified dashboard
- Consistent policies

### Using with IaC

Organization Groups can be managed alongside individual org configs:

```
.
├── org-groups/
│   └── group-1/
│       ├── index.yaml
│       └── shared-rules.yaml
└── orgs/
    ├── org-1/
    │   └── index.yaml
    └── org-2/
        └── index.yaml
```

## Version Control Best Practices

### Git Workflow

**Branch Strategy**:
```
main (production)
  ↑
staging (testing)
  ↑
development (active work)
```

**Workflow**:
1. Make changes in `development` branch
2. Test thoroughly with dry-run
3. Merge to `staging` and deploy to staging org
4. Validate in staging environment
5. Merge to `main` and sync to production orgs

### Commit Messages

**Good Examples**:
- "Add detection rule for credential dumping (T1003)"
- "Update Slack output channel to #security-alerts"
- "Fix false positive in PowerShell detection"
- "Enable YARA extension for all organizations"

**Bad Examples**:
- "Update config"
- "Fix bug"
- "WIP"
- "Changes"

### Change Reviews

Implement pull request reviews for production changes:

1. Create feature branch for changes
2. Open pull request
3. Peer review for accuracy and completeness
4. Test with dry-run before merging
5. Document expected impact
6. Merge and deploy

### Configuration Documentation

**README.md** example:
```markdown
# LimaCharlie Security Configurations

## Repository Structure
- `global/` - Shared configurations across all organizations
- `orgs/` - Organization-specific configurations
- `templates/` - Deployment templates

## Deployment
See DEPLOYMENT.md for detailed deployment procedures.

## Testing
All changes should be tested with:
```bash
limacharlie configs push --config config.yaml --dry-run
```

## Contacts
- Security Team: security@company.com
- On-Call: oncall@company.com
```

## Testing Configurations

### Validating YAML Syntax

**Using yamllint**:
```bash
yamllint config.yaml
```

**Using Python**:
```bash
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

**Using yq**:
```bash
yq eval '.' config.yaml
```

### Testing D&R Rules

**Test with replay**:
```bash
# Extract rules from config
yq eval '.rules[0]' config.yaml > rule.yaml

# Test with replay
limacharlie replay --rule-content rule.yaml --events test-events.json

# Test against historical data
limacharlie replay --rule-content rule.yaml --entire-org --last-seconds 3600
```

### Validating Against Schema

```bash
# Validate configuration
limacharlie configs push --config config.yaml --dry-run --all

# Check for errors in output
```

### Unit Tests for Rules

Include unit tests in D&R rules:

```yaml
rules:
  - name: test-detection
    detect:
      event: NEW_PROCESS
      op: ends with
      path: event/FILE_PATH
      value: calc.exe
      case sensitive: false
    respond:
      - action: report
        name: calculator-launched
    tests:
      match:
        - - event:
              FILE_PATH: C:\Windows\System32\calc.exe
              PROCESS_ID: 1234
            routing:
              event_type: NEW_PROCESS
      non_match:
        - - event:
              FILE_PATH: C:\Windows\System32\notepad.exe
              PROCESS_ID: 5678
            routing:
              event_type: NEW_PROCESS
```

## Advanced Use Cases

### Configuration Inheritance

Create base configurations and layer organization-specific configs:

**base-config.yaml**:
```yaml
version: 3
rules:
  - name: base-rule-1
    detect:
      event: NEW_PROCESS
      op: exists
      path: event/FILE_PATH
    respond:
      - action: report
        name: base-detection
```

**overlay-config.yaml**:
```yaml
version: 3
include:
  - base-config.yaml

# Additional rules
rules:
  - name: overlay-rule-1
    detect:
      event: NETWORK_CONNECTIONS
      op: exists
      path: event/NETWORK_ACTIVITY
    respond:
      - action: report
        name: overlay-detection
```

### Automated Compliance Checks

Validate configurations meet compliance requirements:

```python
import yaml

def validate_compliance(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    errors = []

    # Check: All D&R rules have metadata
    for rule in config.get('rules', []):
        if 'respond' in rule:
            for action in rule['respond']:
                if action['action'] == 'report':
                    if 'metadata' not in action:
                        errors.append(f"Rule '{rule['name']}' missing metadata")

    # Check: Outputs configured
    if not config.get('outputs'):
        errors.append("No outputs configured")

    # Check: At least one installation key
    if not config.get('installation_keys'):
        errors.append("No installation keys configured")

    return errors

errors = validate_compliance('config.yaml')
if errors:
    print("Compliance errors:")
    for error in errors:
        print(f"  - {error}")
    exit(1)
else:
    print("Configuration compliant")
```

### Dynamic Configuration Generation

Generate configurations programmatically:

```python
import yaml

def generate_org_config(org_name, siem_host):
    config = {
        'version': 3,
        'outputs': [
            {
                'name': f'{org_name}-siem',
                'module': 'syslog',
                'for': 'detection',
                'dest_host': siem_host,
                'dest_port': 514
            }
        ],
        'installation_keys': [
            {
                'description': f'{org_name}-windows',
                'tags': [org_name, 'windows']
            },
            {
                'description': f'{org_name}-linux',
                'tags': [org_name, 'linux']
            }
        ]
    }

    with open(f'orgs/{org_name}/config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

# Generate configs for multiple orgs
orgs = [
    ('customer-a', 'siem-a.company.com'),
    ('customer-b', 'siem-b.company.com'),
    ('customer-c', 'siem-c.company.com')
]

for org_name, siem_host in orgs:
    generate_org_config(org_name, siem_host)
```
