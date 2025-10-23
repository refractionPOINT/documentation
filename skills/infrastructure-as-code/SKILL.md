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

## Quick Start

### 1. Enable Infrastructure Extension

1. Navigate to the Infrastructure extension page in the marketplace
2. Select your organization
3. Click Subscribe

### 2. Export Your Configuration

**Via CLI**:
```bash
# Export current configuration
limacharlie configs fetch --oid YOUR_OID > config.yaml
```

**Via Web UI**:
- Navigate to Organization Settings > Infrastructure as Code
- Click "Fetch" to export current configuration

### 3. Modify Configuration

Edit the exported YAML file to add, update, or remove configurations.

### 4. Deploy Configuration

**Via CLI**:
```bash
# Dry run (test first)
limacharlie configs push --config config.yaml --dry-run --all

# Apply configuration (additive)
limacharlie configs push --config config.yaml --all

# Force sync (make org exactly match config)
limacharlie configs push --config config.yaml --force --all
```

**Via Web UI**:
- Navigate to Organization Settings > Infrastructure as Code
- Click "Push" and paste your YAML
- Or use "Push-from-file" to upload a file

## Configuration Format (Condensed)

See [REFERENCE.md](./REFERENCE.md) for complete YAML structure and all configuration sections.

### Basic Structure

```yaml
version: 3

# Main sections
rules:                    # Detection & Response rules
  - name: rule-name
    detect: {...}
    respond: [...]

fp:                       # False Positive rules
  - name: fp-name
    op: OPERATOR
    path: detect/event/FIELD
    value: VALUE

outputs:                  # Outputs (Slack, SIEM, etc.)
  - name: output-name
    module: slack
    for: detection
    # module-specific params

installation_keys:        # Sensor installation keys
  - description: key-desc
    tags: [...]

extensions:               # Extensions to enable
  - ext-infrastructure
  - ext-git-sync

hive:                     # Hive data (secrets, lookup tables, etc.)
  secret:
    - name: secret-name
      enabled: true
      data: "value"
  lookup:
    - name: table-name
      enabled: true
      data: |
        value1
        value2
```

### Using Include Files

```yaml
# index.yaml
version: 3
include:
  - rules/detection-rules.yaml
  - outputs/outputs.yaml
```

Paths in `include` are relative to the file containing the include.

## Git Sync Extension

### Key Features

- **Centralized Configuration**: Store all IaC configs in a single Git repository
- **Recurring Apply**: Automatically sync changes from Git to LimaCharlie on a schedule
- **Recurring Export**: Automatically export LimaCharlie configs to Git on a schedule
- **Export on Demand**: Manually export organization configuration to Git
- **Multi-Org Support**: Manage multiple organizations in one repository with shared configurations
- **Transparent Operations**: All operations tracked through an extension sensor

### Quick Setup (GitHub)

**1. Generate SSH Key**:
```bash
mkdir -p ~/.ssh/gitsync
ssh-keygen -t ed25519 -C "limacharlie-gitsync" -f ~/.ssh/gitsync/id_ed25519
```

**2. Add Deploy Key to GitHub**:
- Navigate to GitHub repository > Settings > Deploy keys
- Add deploy key with the **public** key content
- **Check "Allow write access"** (required for exports)

**3. Store Private Key in LimaCharlie**:
- Navigate to Organization Settings > Secret Manager
- Create new secret named `github-deploy-key`
- Paste the **private** key content

**4. Configure Git Sync Extension**:
- Navigate to Extensions > Git Sync
- SSH Key Source: Secret Manager
- Select Secret: `github-deploy-key`
- User Name: `git`
- Repository URL: `git@github.com:username/repo.git`
- Branch: `main`
- Select sync options (pull/push components)
- Configure schedules (optional)

**5. Verify**:
- Click "Push to Git" to export current config
- Check GitHub repository for exported configs
- Make a test change in GitHub
- Click "Pull from Git" to sync changes

### Repository Structure

Single org: `orgs/[org-id]/index.yaml`

Multi-org with shared configs:
```
hives/dr-general.yaml  # Shared rules
orgs/org-1/index.yaml  # References ../hives/dr-general.yaml
orgs/org-2/index.yaml  # References ../hives/dr-general.yaml
```

## Common Workflows

### 1. Bootstrap New Organization

```bash
mkdir -p orgs/customer-name
cat > orgs/customer-name/index.yaml <<EOF
version: 3
include:
  - ../../global/detections/malware.yaml
  - outputs.yaml
EOF
git add orgs/customer-name && git commit -m "Bootstrap customer" && git push
```

### 2. Update Global Rule

```bash
vim global/detections/malware.yaml
limacharlie configs push --config global/detections/malware.yaml --dry-run
git add global/detections/malware.yaml && git commit -m "Update malware detection" && git push
```

### 3. Emergency Deployment

```bash
# Deploy immediately to all orgs
for org_id in $(cat production-orgs.txt); do
  limacharlie configs push --oid $org_id --config emergency-rule.yaml
done
```

### 4. Migrate Between Environments

```bash
limacharlie configs fetch --oid staging-oid > staging.yaml
limacharlie configs push --oid prod-oid --config staging.yaml --dry-run --all
limacharlie configs push --oid prod-oid --config staging.yaml --all
```

### 5. Export Current Config

```bash
limacharlie configs fetch --oid YOUR_OID > current-config.yaml
```

## CLI Operations

### Available Commands

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

## Multi-Organization Management

Share common configurations across multiple organizations:

```
global/detections/malware.yaml     # Shared rules
orgs/customer-a/index.yaml         # Includes ../../global/detections/malware.yaml
orgs/customer-b/index.yaml         # Includes ../../global/detections/malware.yaml
```

See [EXAMPLES.md](./EXAMPLES.md) for complete MSSP multi-org examples.

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

### Security
1. **Use Hive secrets**: Never commit credentials to Git
2. **Review changes**: PR reviews for production changes
3. **Audit trail**: Git history provides change tracking
4. **Least privilege**: API keys with minimal required permissions
5. **Separate environments**: Different orgs for dev/staging/prod

## Navigation

For detailed information, see:
- **[REFERENCE.md](./REFERENCE.md)** - Complete configuration format, all YAML sections, REST API parameters
- **[EXAMPLES.md](./EXAMPLES.md)** - Complete IaC examples (EDR setup, cloud monitoring, MSSP)
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Git sync issues, deployment problems, validation errors

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
