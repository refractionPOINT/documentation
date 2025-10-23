---
name: infrastructure-as-code
description: Use this skill when users need help managing LimaCharlie configurations as code, exporting organization settings, using Git sync, deploying configs across multiple organizations, or implementing Infrastructure as Code workflows.
---

# LimaCharlie Infrastructure as Code

You are an expert at helping users manage LimaCharlie configurations as code using the Infrastructure Extension, Git Sync, and related IaC workflows.

## What is Infrastructure as Code for LimaCharlie?

Infrastructure as Code (IaC) for LimaCharlie allows you to:

- Export your entire organization configuration to YAML files
- Version control your security configurations in Git
- Deploy configurations programmatically across multiple organizations
- Maintain consistent configurations across development, staging, and production environments
- Share common rule sets and configurations across customer organizations (MSSP/MSP)
- Rapidly deploy new organizations from templates
- Track configuration changes over time
- Implement GitOps workflows for security operations

All LimaCharlie configurations can be managed as code, including:
- Detection & Response (D&R) rules
- False Positive (FP) rules
- Outputs and integrations
- Resources (API keys, secrets)
- Extensions and their configurations
- Installation keys
- Organization values
- Lookup tables, YARA signatures, and other Hive data
- Exfil rules
- Integrity rules

## Infrastructure Extension

The Infrastructure Extension enables IaC operations through the web UI, REST API, and CLI.

### Enabling the Infrastructure Extension

1. Navigate to the Infrastructure extension page in the marketplace
2. Select your organization
3. Click Subscribe

The extension is available immediately after subscribing.

### Available Operations

**Via Web UI** (Organization Settings > Infrastructure as Code):
- Apply a New Config (additive merge)
- Edit the Entire Configuration (view and modify current config)
- Fetch (export current configuration)
- Push (apply configuration from text or file)
- Push-from-file (upload YAML file to apply)

**Via CLI**:
```bash
# Export/fetch current configuration
limacharlie configs fetch --oid YOUR_OID

# Apply configuration (default: additive)
limacharlie configs push --config /path/to/config.yaml

# Force sync (make org exactly match config)
limacharlie configs push --config /path/to/config.yaml --force

# Dry run (see what would change)
limacharlie configs push --config /path/to/config.yaml --dry-run

# Sync all components
limacharlie configs push --config /path/to/config.yaml --all

# Ignore locked/segmented resources
limacharlie configs push --ignore-inaccessible
```

**Via REST API**:

The Infrastructure extension accepts these parameters:

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

## Configuration Format

LimaCharlie configurations use YAML format with a specific structure.

### Basic Configuration Structure

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

# False Positive Rules
fp:
  - name: whitelist-system-powershell
    op: is
    path: detect/event/FILE_PATH
    value: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

# Outputs
outputs:
  - name: slack-security-alerts
    module: slack
    for: detection
    slack_api_token: hive://secret/slack-token
    slack_channel: "#security-alerts"

# Installation Keys
installation_keys:
  - description: windows-endpoints
    tags:
      - windows
      - production
  - description: linux-servers
    tags:
      - linux
      - server

# Extensions
extensions:
  - ext-infrastructure
  - ext-git-sync
  - binlib

# Organization Values
org_values:
  - name: slack_webhook_url
    value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Resources (API Keys, Service Accounts)
resources:
  api_keys:
    - name: automation-key
      permissions:
        - dr.list
        - dr.set
        - sensor.list

# Hive Data (organized by hive type)
hive:
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

  lookup:
    - name: malicious-domains
      enabled: true
      data: |
        evil.com
        malware.net
        badactor.org

  yara:
    - name: ransomware-indicators
      enabled: true
      data: |
        rule ransomware_pattern {
          strings:
            $s1 = "DECRYPT_INSTRUCTION" ascii
            $s2 = ".encrypted" ascii
          condition:
            any of them
        }

  secret:
    - name: aws-access-key
      enabled: true
      data: "YOUR_AWS_ACCESS_KEY"

  cloud_sensor:
    - name: okta-integration
      enabled: true
      data:
        sensor_type: okta
        okta:
          apikey: hive://secret/okta-api-key
          url: https://your-company.okta.com
          client_options:
            identity:
              oid: YOUR_OID
              installation_key: YOUR_KEY
            platform: json
            sensor_seed_key: okta-logs
```

### Using Include Files

Break large configurations into manageable files:

**index.yaml** (root):
```yaml
version: 3
include:
  - rules/detection-rules.yaml
  - rules/fp-rules.yaml
  - outputs/outputs.yaml
  - resources/resources.yaml
  - hives/dr-general.yaml
  - hives/lookup.yaml
  - hives/yara.yaml
```

**rules/detection-rules.yaml**:
```yaml
version: 3
rules:
  - name: rule-1
    detect:
      # detection logic
    respond:
      - action: report
        name: detection-1

  - name: rule-2
    detect:
      # detection logic
    respond:
      - action: report
        name: detection-2
```

### Path Resolution in Include Files

Paths in `include` statements are relative to the file containing the include:

```yaml
# File: /configs/index.yaml
version: 3
include:
  - rules/detections.yaml  # Resolves to /configs/rules/detections.yaml
  - ../shared/common.yaml  # Resolves to /shared/common.yaml
```

## Git Sync Extension

The Git Sync extension automates bidirectional synchronization between GitHub and LimaCharlie.

### Key Features

- **Centralized Configuration**: Store all IaC configs in a single Git repository
- **Recurring Apply**: Automatically sync changes from Git to LimaCharlie on a schedule
- **Recurring Export**: Automatically export LimaCharlie configs to Git on a schedule
- **Export on Demand**: Manually export organization configuration to Git
- **Multi-Org Support**: Manage multiple organizations in one repository with shared configurations
- **Transparent Operations**: All operations tracked through an extension sensor

### Git Repository Structure

Git Sync requires a specific repository structure:

#### Single Organization

```
.
└── orgs/
    └── a326700d-3cd7-49d1-ad08-20b396d8549d/
        ├── index.yaml
        ├── extensions.yaml
        ├── installation_keys.yaml
        ├── org_values.yaml
        ├── outputs.yaml
        ├── resources.yaml
        └── hives/
            ├── dr-general.yaml
            ├── dr-managed.yaml
            ├── fp.yaml
            ├── lookup.yaml
            ├── yara.yaml
            ├── secret.yaml
            └── cloud_sensor.yaml
```

**index.yaml** determines which files are included:
```yaml
version: 3
include:
  - extensions.yaml
  - hives/fp.yaml
  - outputs.yaml
  - resources.yaml
  - hives/yara.yaml
  - hives/dr-general.yaml
  - hives/lookup.yaml
  - org_values.yaml
  - installation_keys.yaml
  - hives/secret.yaml
  - hives/cloud_sensor.yaml
```

#### Multiple Organizations with Shared Configs

```
.
├── hives/
│   ├── dr-general.yaml       # Shared detection rules
│   └── yara.yaml             # Shared YARA rules
└── orgs/
    ├── 7e41e07b-c44c-43a3-b78d-41f34204789d/
    │   └── index.yaml
    ├── a326700d-3cd7-49d1-ad08-20b396d8549d/
    │   └── index.yaml
    └── cb639126-e0bc-4563-a577-2e559c0610b2/
        └── index.yaml
```

**Each org's index.yaml** references shared configs:
```yaml
version: 3
include:
  - ../../hives/yara.yaml
  - ../../hives/dr-general.yaml
```

#### Export Directory Structure

Exports are placed in a separate `exports/` directory to avoid overwriting:

```
.
└── exports/
    └── orgs/
        └── a326700d-3cd7-49d1-ad08-20b396d8549d/
            ├── index.yaml
            ├── extensions.yaml
            ├── hives/
            │   ├── dr-general.yaml
            │   └── ...
            ├── installation_keys.yaml
            ├── org_values.yaml
            ├── outputs.yaml
            └── resources.yaml
```

### Setting Up Git Sync with GitHub

#### Step 1: Generate SSH Key

Create a dedicated SSH key for Git Sync:

```bash
# Create directory
mkdir -p ~/.ssh/gitsync
chmod 700 ~/.ssh/gitsync

# Generate key
ssh-keygen -t ed25519 -C "limacharlie-gitsync" -f ~/.ssh/gitsync/id_ed25519
```

#### Step 2: Add Deploy Key to GitHub

1. Navigate to your GitHub repository
2. Click Settings > Deploy keys
3. Click Add deploy key
4. Title: "LimaCharlie Git Sync Integration"
5. Paste the **public** key (contents of `id_ed25519.pub`)
6. **Check "Allow write access"** (required for exports)
7. Click Add key

#### Step 3: Store Private Key in LimaCharlie

1. Navigate to Organization Settings > Secret Manager
2. Click Create New Secret
3. Name: `github-deploy-key`
4. Value: Paste the **private** key (contents of `id_ed25519`)
5. Save

#### Step 4: Configure Git Sync Extension

1. Navigate to Extensions > Git Sync
2. Configure settings:
   - **SSH Key Source**: Secret Manager
   - **Select Secret**: `github-deploy-key`
   - **User Name**: `git`
   - **Repository URL**: `git@github.com:username/repo.git`
   - **Branch**: `main` (or your preferred branch)

3. Select sync options:
   - **Pull from Git**: Choose which components to sync TO LimaCharlie
     - D&R rules
     - False Positive rules
     - Outputs
     - Resources
     - Extensions
     - etc.
   - **Push to Git**: Choose which components to export FROM LimaCharlie
     - Same options as above

4. Optional: Configure schedules
   - **Pull Schedule**: How often to sync from Git (e.g., every 5 minutes)
   - **Push Schedule**: How often to export to Git (e.g., daily)

5. Click Save Settings

#### Step 5: Verify Integration

1. Click "Push to Git" to perform manual export
2. Check your GitHub repository for exported configs
3. Make a change to a config file in GitHub
4. Wait for pull schedule or click "Pull from Git"
5. Verify changes appear in LimaCharlie

### Git Sync Schedules

Schedules are specified as D&R rules that run on intervals:

**Pull Schedule Example** (sync FROM Git every 5 minutes):
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

**Push Schedule Example** (export TO Git daily):
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

### Troubleshooting Git Sync

**Connection Issues**:
- Verify SSH URL format: `git@github.com:username/repo.git`
- Ensure deploy key has write permissions (for exports)
- Check that private key in Secret Manager matches public key in GitHub
- Verify repository branch exists

**No Changes Syncing**:
- Check Git Sync extension sensor for error messages
- Verify repository structure (`orgs/[oid]/index.yaml` exists)
- Ensure files listed in `index.yaml` exist
- Check file paths are relative to `index.yaml` location

**Partial Sync**:
- Review sync options (pull/push checkboxes)
- Check for locked or segmented resources
- Use `ignore_inaccessible` flag if needed

## Multi-Organization Management

Managing multiple organizations efficiently is crucial for MSSPs, MSPs, and enterprises.

### Approach 1: Shared Global Configs

Use a single repository with shared configurations:

```
configs/
├── global/
│   ├── detections/
│   │   ├── malware.yaml
│   │   ├── lateral-movement.yaml
│   │   └── data-exfil.yaml
│   ├── fp/
│   │   └── common-fp.yaml
│   └── yara/
│       └── signatures.yaml
└── orgs/
    ├── customer-a/
    │   ├── index.yaml
    │   ├── outputs.yaml        # Customer-specific outputs
    │   └── custom-rules.yaml   # Customer-specific rules
    ├── customer-b/
    │   ├── index.yaml
    │   ├── outputs.yaml
    │   └── custom-rules.yaml
    └── customer-c/
        ├── index.yaml
        ├── outputs.yaml
        └── custom-rules.yaml
```

**Customer-A index.yaml**:
```yaml
version: 3
include:
  # Global shared rules
  - ../../global/detections/malware.yaml
  - ../../global/detections/lateral-movement.yaml
  - ../../global/detections/data-exfil.yaml
  - ../../global/fp/common-fp.yaml
  - ../../global/yara/signatures.yaml

  # Customer-specific configs
  - outputs.yaml
  - custom-rules.yaml
```

### Approach 2: Template-Based Deployment

Create organization templates and deploy programmatically:

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

**Deployment script**:
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

### Approach 3: Python SDK for Programmatic Management

Use the Python SDK for advanced multi-org management:

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

### Approach 4: Organization Groups

Use LimaCharlie's Organization Groups for centralized management:

1. Create Organization Group in LimaCharlie web UI
2. Add multiple organizations to the group
3. Manage shared configurations at the group level
4. Individual orgs can have additional custom configs

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

Use clear, descriptive commit messages:

```
Good:
  - "Add detection rule for credential dumping (T1003)"
  - "Update Slack output channel to #security-alerts"
  - "Fix false positive in PowerShell detection"

Bad:
  - "Update config"
  - "Fix bug"
  - "WIP"
```

### Change Reviews

Implement pull request reviews for production changes:

1. Create feature branch for changes
2. Open pull request
3. Peer review for accuracy and completeness
4. Test with dry-run before merging
5. Document expected impact

### Configuration Documentation

Include README files in your repository:

**README.md**:
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

## Configuration Deployment

### Dry Run (Test Before Applying)

Always test configurations before applying:

```bash
# See what would change without applying
limacharlie configs push --config config.yaml --dry-run --all

# Check output for:
# - Rules that would be added
# - Rules that would be modified
# - Rules that would be deleted (with --force)
# - Any errors or warnings
```

### Additive vs Force Mode

**Additive Mode** (default):
- Adds new configurations
- Updates existing configurations
- Does NOT remove configurations not in file

```bash
limacharlie configs push --config config.yaml
```

**Force Mode**:
- Makes organization EXACTLY match configuration file
- Adds new configurations
- Updates existing configurations
- DELETES configurations not in file

```bash
limacharlie configs push --config config.yaml --force
```

**When to use Force Mode**:
- Cleaning up test/development environments
- Ensuring strict configuration compliance
- Removing deprecated rules across all orgs

**When to avoid Force Mode**:
- Production environments (unless intentional)
- When other teams manage some configurations
- When configurations are added manually

### Selective Sync

Sync only specific components:

```bash
# Sync only D&R rules
limacharlie configs push --config config.yaml --sync-dr

# Sync outputs and resources
limacharlie configs push --config config.yaml --sync-outputs --sync-resources

# Sync everything
limacharlie configs push --config config.yaml --all
```

Available sync flags:
- `--sync-dr` - Detection & Response rules
- `--sync-fp` - False Positive rules
- `--sync-outputs` - Outputs
- `--sync-resources` - Resources (API keys, etc.)
- `--sync-artifacts` - Artifacts
- `--sync-integrity` - Integrity rules
- `--sync-exfil` - Exfil rules
- `--sync-org-values` - Organization values
- `--all` - All components

### Handling Locked Resources

Some resources may be locked or segmented:

```bash
# Ignore inaccessible resources (don't fail on locked resources)
limacharlie configs push --config config.yaml --ignore-inaccessible --all
```

## Testing Configurations

### Validating YAML Syntax

Ensure YAML is valid before applying:

```bash
# Use yamllint
yamllint config.yaml

# Use Python
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Use yq
yq eval '.' config.yaml
```

### Testing D&R Rules

Test D&R rules against historical data:

```bash
# Extract rules from config
yq eval '.rules[0]' config.yaml > rule.yaml

# Test with replay
limacharlie replay --rule-content rule.yaml --events test-events.json

# Test against historical data
limacharlie replay --rule-content rule.yaml --entire-org --last-seconds 3600
```

### Validating Against Schema

Use the LimaCharlie CLI to validate:

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

## Complete Configuration Examples

### Example 1: Basic EDR Setup

```yaml
version: 3

# Installation Keys
installation_keys:
  - description: windows-workstations
    tags:
      - windows
      - workstation
  - description: linux-servers
    tags:
      - linux
      - server

# Core Detection Rules
rules:
  - name: credential-dumping-tools
    detect:
      event: NEW_PROCESS
      op: or
      rules:
        - op: ends with
          path: event/FILE_PATH
          value: mimikatz.exe
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: sekurlsa
          case sensitive: false
    respond:
      - action: report
        name: Credential Dumping Tool Detected
        priority: 5
      - action: task
        command: deny_tree <<routing/this>>
      - action: isolate network

  - name: suspicious-powershell
    detect:
      event: NEW_PROCESS
      op: and
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: powershell
          case sensitive: false
        - op: or
          rules:
            - op: contains
              path: event/COMMAND_LINE
              value: -enc
              case sensitive: false
            - op: contains
              path: event/COMMAND_LINE
              value: -encodedcommand
              case sensitive: false
    respond:
      - action: report
        name: Encoded PowerShell Command
        priority: 3
      - action: task
        command: history_dump
        investigation: encoded-powershell

# Outputs
outputs:
  - name: slack-alerts
    module: slack
    for: detection
    slack_api_token: hive://secret/slack-token
    slack_channel: "#security-alerts"

  - name: siem-integration
    module: syslog
    for: event
    dest_host: siem.company.com
    dest_port: 514
    filters:
      tags:
        - vip

# Extensions
extensions:
  - ext-infrastructure
  - ext-git-sync
  - binlib
```

### Example 2: Cloud Security Monitoring

```yaml
version: 3

# Cloud Adapters (Hive: cloud_sensor)
hive:
  cloud_sensor:
    - name: aws-cloudtrail
      enabled: true
      data:
        sensor_type: s3
        s3:
          bucket_name: my-cloudtrail-logs
          secret_key: hive://secret/aws-secret-key
          access_key: hive://secret/aws-access-key
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
          client_options:
            identity:
              oid: YOUR_OID
              installation_key: YOUR_KEY
            platform: office365
            sensor_seed_key: o365-audit

  # Cloud Detection Rules
  dr-general:
    - name: aws-root-account-usage
      enabled: true
      data:
        detect:
          event: AWS_EVENT
          op: is platform
          name: aws
          with child:
            op: and
            rules:
              - op: is
                path: event/userIdentity/type
                value: Root
              - op: is
                path: event/eventType
                value: AwsConsoleSignIn
        respond:
          - action: report
            name: AWS Root Account Login
            priority: 5

    - name: okta-multiple-failed-logins
      enabled: true
      data:
        detect:
          event: user.session.start
          op: is platform
          name: json
          with events:
            event: user.session.start
            op: is
            path: event/outcome/result
            value: FAILURE
            count: 5
            within: 300
        respond:
          - action: report
            name: Multiple Failed Okta Logins
            priority: 4

# Outputs for cloud events
outputs:
  - name: cloud-alerts-to-slack
    module: slack
    for: detection
    slack_api_token: hive://secret/slack-token
    slack_channel: "#cloud-security"
```

### Example 3: MSSP Multi-Org Configuration

**Global configurations** (shared across all customers):

**global/detections/ransomware.yaml**:
```yaml
version: 3
rules:
  - name: ransomware-file-encryption
    detect:
      event: NEW_DOCUMENT
      op: and
      rules:
        - op: matches
          path: event/FILE_PATH
          re: \.(encrypted|locked|crypto|crypt)$
          case sensitive: false
        - op: is greater than
          path: event/FILE_PATH
          value: 100
          length of: true
    respond:
      - action: report
        name: Potential Ransomware File Encryption
        priority: 5
      - action: task
        command: history_dump
        investigation: ransomware
      - action: isolate network
```

**global/detections/lateral-movement.yaml**:
```yaml
version: 3
rules:
  - name: psexec-lateral-movement
    detect:
      event: NEW_PROCESS
      op: and
      rules:
        - op: contains
          path: event/COMMAND_LINE
          value: psexec
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: \\\\
    respond:
      - action: report
        name: Potential PSExec Lateral Movement
        priority: 4
```

**Customer A configuration**:

**orgs/customer-a/index.yaml**:
```yaml
version: 3
include:
  # Global shared rules
  - ../../global/detections/ransomware.yaml
  - ../../global/detections/lateral-movement.yaml

  # Customer-specific
  - outputs.yaml
  - installation-keys.yaml
```

**orgs/customer-a/outputs.yaml**:
```yaml
version: 3
outputs:
  - name: customer-a-siem
    module: syslog
    for: event
    dest_host: siem.customer-a.com
    dest_port: 514
```

**orgs/customer-a/installation-keys.yaml**:
```yaml
version: 3
installation_keys:
  - description: customer-a-windows
    tags:
      - customer-a
      - windows
```

## Advanced Use Cases

### Dynamic Configuration with Templates

Use templating for environment-specific values:

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

## Common Workflows

### Workflow 1: Bootstrap New Organization

```bash
#!/bin/bash
# Bootstrap a new customer organization

ORG_ID="new-customer-oid"
CUSTOMER_NAME="acme-corp"

# 1. Create organization directory
mkdir -p orgs/$CUSTOMER_NAME

# 2. Create index.yaml with shared configs
cat > orgs/$CUSTOMER_NAME/index.yaml <<EOF
version: 3
include:
  - ../../global/detections/malware.yaml
  - ../../global/detections/lateral-movement.yaml
  - outputs.yaml
  - installation-keys.yaml
EOF

# 3. Create customer-specific outputs
cat > orgs/$CUSTOMER_NAME/outputs.yaml <<EOF
version: 3
outputs:
  - name: ${CUSTOMER_NAME}-alerts
    module: slack
    for: detection
    slack_api_token: hive://secret/${CUSTOMER_NAME}-slack-token
    slack_channel: "#security"
EOF

# 4. Create installation keys
cat > orgs/$CUSTOMER_NAME/installation-keys.yaml <<EOF
version: 3
installation_keys:
  - description: ${CUSTOMER_NAME}-windows
    tags:
      - ${CUSTOMER_NAME}
      - windows
  - description: ${CUSTOMER_NAME}-linux
    tags:
      - ${CUSTOMER_NAME}
      - linux
EOF

# 5. Commit to Git
git add orgs/$CUSTOMER_NAME
git commit -m "Bootstrap ${CUSTOMER_NAME} organization"
git push

# 6. Sync to LimaCharlie (if Git Sync not enabled)
# limacharlie configs push --oid $ORG_ID --config orgs/$CUSTOMER_NAME/index.yaml --all
```

### Workflow 2: Update Global Rule Across All Orgs

```bash
#!/bin/bash
# Update a global detection rule and deploy

# 1. Update rule file
vim global/detections/malware.yaml

# 2. Test with dry-run
limacharlie configs push --config global/detections/malware.yaml --dry-run

# 3. Commit change
git add global/detections/malware.yaml
git commit -m "Update malware detection to reduce false positives"

# 4. Push to Git
git push

# 5. Git Sync will automatically deploy to all orgs
# Or manually deploy to all orgs:
# for org_id in $(cat org-list.txt); do
#   limacharlie configs push --oid $org_id --config global/detections/malware.yaml
# done
```

### Workflow 3: Emergency Rule Deployment

```bash
#!/bin/bash
# Deploy emergency detection rule immediately

# 1. Create rule
cat > emergency-rule.yaml <<EOF
version: 3
rules:
  - name: emergency-cve-2024-xxxx
    detect:
      event: NEW_PROCESS
      op: contains
      path: event/COMMAND_LINE
      value: exploit-string
    respond:
      - action: report
        name: CVE-2024-XXXX Exploitation Attempt
        priority: 5
      - action: isolate network
EOF

# 2. Validate
limacharlie replay --validate --rule-content emergency-rule.yaml

# 3. Deploy to production immediately
for org_id in $(cat production-orgs.txt); do
  limacharlie configs push --oid $org_id --config emergency-rule.yaml
done

# 4. Commit to Git for record
git add emergency-rule.yaml
git commit -m "URGENT: Deploy emergency rule for CVE-2024-XXXX"
git push
```

### Workflow 4: Migrate Configuration Between Environments

```bash
#!/bin/bash
# Migrate config from staging to production

STAGING_OID="staging-oid"
PROD_OID="production-oid"

# 1. Export from staging
limacharlie configs fetch --oid $STAGING_OID > staging-config.yaml

# 2. Review changes
cat staging-config.yaml

# 3. Dry-run against production
limacharlie configs push --oid $PROD_OID --config staging-config.yaml --dry-run --all

# 4. Review dry-run output
read -p "Proceed with deployment? (yes/no) " confirm
if [ "$confirm" = "yes" ]; then
  # 5. Deploy to production
  limacharlie configs push --oid $PROD_OID --config staging-config.yaml --all

  # 6. Commit to Git
  git add staging-config.yaml
  git commit -m "Promote staging config to production"
  git push
fi
```

## Best Practices Summary

### Configuration Management
1. **Version control everything**: All configs should be in Git
2. **Use includes**: Break large configs into manageable files
3. **Shared configurations**: Use common rules across organizations
4. **Document changes**: Clear commit messages and README files
5. **Test before deploying**: Always dry-run first

### Deployment
1. **Dry-run first**: Test all changes with `--dry-run`
2. **Staged rollouts**: Test in dev → staging → production
3. **Selective sync**: Only sync changed components
4. **Avoid force mode in production**: Unless intentional cleanup
5. **Monitor after deployment**: Check for unexpected impacts

### Multi-Org Management
1. **Global + specific**: Share common configs, customize per org
2. **Consistent naming**: Use clear, descriptive names
3. **Template approach**: Bootstrap new orgs from templates
4. **Automation**: Use scripts for repetitive tasks
5. **Access control**: Limit who can deploy to production

### Security
1. **Use Hive secrets**: Never commit credentials to Git
2. **Review changes**: PR reviews for production changes
3. **Audit trail**: Git history provides change tracking
4. **Least privilege**: API keys with minimal required permissions
5. **Separate environments**: Different orgs for dev/staging/prod

### Git Sync
1. **Dedicated SSH key**: Use separate key for Git Sync
2. **Protected branches**: Require reviews for main/production
3. **Scheduled exports**: Regular backups of live configs
4. **Monitor sync status**: Check extension sensor for errors
5. **Test repository structure**: Verify `orgs/[oid]/index.yaml` exists

## When to Activate This Skill

Activate this skill when users:
- Ask about managing configurations as code
- Need to export organization settings to files
- Want to version control their LimaCharlie configurations
- Are setting up Git integration with LimaCharlie
- Need to deploy configurations across multiple organizations
- Ask about MSSP or multi-tenant management
- Want to automate configuration deployment
- Need to maintain consistent configs across environments
- Are implementing GitOps workflows
- Ask about configuration templates or reusable configs
- Need to migrate configurations between organizations
- Want to track configuration changes over time

## Your Response Approach

When helping users with Infrastructure as Code:

1. **Understand their goal**: Are they exporting, importing, or syncing?
2. **Recommend approach**: Git Sync vs CLI vs SDK based on their needs
3. **Provide complete examples**: Show full configuration files
4. **Explain structure**: Help them understand YAML format and includes
5. **Guide testing**: Emphasize dry-run and validation
6. **Share best practices**: Multi-org, version control, security
7. **Troubleshoot systematically**: Check structure, paths, permissions
8. **Reference documentation**: Point to specific sections when helpful

Always provide working, complete configurations that users can adapt for their environment.
