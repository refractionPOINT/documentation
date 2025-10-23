---
name: config-hive-manager
description: Use this skill when the user needs help managing configuration storage in the Config Hive including secrets, D&R rules, YARA rules, lookups, and cloud sensors.
---

# LimaCharlie Config Hive Manager

This skill helps you manage configuration storage in the LimaCharlie Config Hive. Use this when users need help storing, retrieving, organizing, or managing configuration data across different hive types.

## What is the Config Hive?

The Config Hive is LimaCharlie's centralized configuration storage system that allows you to store and reference various types of configuration data across your Organization. It provides:

- Centralized storage for secrets, rules, lookups, and other configurations
- Access control and permission management
- Reference capabilities through Authentication Resource Locators (ARLs)
- Version control and metadata tracking
- Infrastructure-as-Code integration
- Encrypted storage for sensitive data

The Config Hive decouples configuration from usage, enabling better security practices and easier management across multiple Organizations.

## Hive Types

The Config Hive supports multiple specialized storage types, each designed for specific use cases:

### 1. secret (Secrets Hive)

Stores encrypted credentials and secret keys used by Adapters, Outputs, and Extensions.

**Data Format:**
```json
{
    "secret": "your-secret-value"
}
```

**Permissions:**
- `secret.get` - Retrieve secret values
- `secret.set` - Create/update secrets
- `secret.del` - Delete secrets
- `secret.get.mtd` - Get secret metadata
- `secret.set.mtd` - Set secret metadata

**Common Use Cases:**
- API keys for integrations
- Database credentials
- Service account tokens
- Adapter authentication credentials
- Output stream credentials

### 2. dr-general (Detection & Response Rules)

Stores D&R rules created and controlled by your Organization.

**Permissions:**
- `dr.list` - List rules
- `dr.set` - Create/update rules
- `dr.del` - Delete rules

**Related Hive Types:**
- `dr-managed` - Rules managed/curated by third parties (e.g., Soteria rules)
  - Permissions: `dr.list.managed`, `dr.set.managed`, `dr.del.managed`
- `dr-service` - Protected namespace (metadata-only access)
  - Permissions: `dr.list` or `dr.list.managed` (metadata only)

### 3. yara (YARA Rules)

Stores YARA rules for malware detection and file scanning.

**Data Format:**
```json
{
    "rule": "rule_content_here"
}
```

**Permissions:**
- `yara.get` - Retrieve YARA rules
- `yara.set` - Create/update YARA rules
- `yara.del` - Delete YARA rules
- `yara.get.mtd` - Get rule metadata
- `yara.set.mtd` - Set rule metadata

**Features:**
- A single hive record can contain multiple YARA rules
- Rules can be referenced in `yara_scan` commands
- Compatible with ext-yara Extension

### 4. lookup (Lookup Tables)

Stores custom lookup tables for threat intelligence, allow lists, block lists, and custom reference data.

**Data Formats:**

**JSON Format:**
```json
{
  "lookup_data": {
    "key1": {
      "metadata_field1": "value1",
      "metadata_field2": 123
    },
    "key2": {
      "metadata_field1": "value2"
    }
  }
}
```

**Newline Format:**
```json
{
  "newline_content": "value1\nvalue2\nvalue3"
}
```

**YAML Format:**
```json
{
  "yaml_content": "key1:\n  field: value\nkey2:\n  field: value"
}
```

**Permissions:**
- `lookup.get` - Retrieve lookup data
- `lookup.set` - Create/update lookups
- `lookup.del` - Delete lookups
- `lookup.get.mtd` - Get lookup metadata
- `lookup.set.mtd` - Set lookup metadata

**Common Use Cases:**
- Threat intelligence feeds
- Malicious domain lists
- Known good process lists
- IP reputation lists
- Custom indicators of compromise

### 5. cloudsensor (Cloud Sensors)

Stores cloud sensor configurations including webhooks and virtual sensors.

**Data Format:**
```json
{
    "sensor_type": "webhook",
    "webhook": {
        "client_options": {
            "hostname": "test-webhook",
            "identity": {
                "installation_key": "key-here",
                "oid": "org-id-here"
            },
            "platform": "json",
            "sensor_seed_key": "test-webhook"
        },
        "secret": "webhook-secret"
    }
}
```

**Permissions:**
- `cloudsensor.get` - Retrieve cloud sensor configs
- `cloudsensor.set` - Create/update cloud sensors
- `cloudsensor.del` - Delete cloud sensors
- `cloudsensor.get.mtd` - Get metadata
- `cloudsensor.set.mtd` - Set metadata

### 6. extension_config (Extension Configurations)

Stores configuration for LimaCharlie extensions like lookup-manager, usage-alerts, etc.

**Common Extensions:**
- `ext-lookup-manager` - Automated lookup synchronization
- `ext-usage-alerts` - Usage threshold alerts
- `ext-yara-manager` - YARA rule management
- Custom extension configurations

## Authentication Resource Locators (ARLs)

ARLs are the primary mechanism for referencing Config Hive data and external resources.

### Hive ARL Format

Reference data stored in the Config Hive:

```
hive://HIVE_TYPE/KEY_NAME
```

**Examples:**
```
hive://secret/my-api-key
hive://yara/malware-detection
hive://lookup/threat-intel
hive://dr-general/suspicious-process
```

### External Resource ARLs

Reference external resources with optional authentication:

**Format with Authentication:**
```
[methodName,methodDest,authType,authData]
```

**Format without Authentication:**
```
[methodName,methodDest]
```

**Components:**
- `methodName`: Transport method (`http`, `https`, `gcs`, `github`)
- `methodDest`: Destination (domain/path for HTTP, bucket/path for GCS)
- `authType`: Authentication type (`basic`, `bearer`, `token`, `gaia`, `otx`)
- `authData`: Authentication credentials

**Examples:**

HTTP GET with no auth:
```
[https,my.corpwebsite.com/resource-data]
```

HTTP GET with basic auth:
```
[https,my.corpwebsite.com/resource-data,basic,username:password]
```

HTTP GET with bearer token:
```
[https,my.corpwebsite.com/resource-data,bearer,token-value-here]
```

Google Cloud Storage:
```
[gcs,bucket-name/blob-prefix,gaia,base64(SERVICE_KEY_JSON)]
```

Public GitHub repository:
```
[github,username/repo-name/path/to/file]
```

Private GitHub with token:
```
[github,username/repo-name/path/to/file,token,github-personal-access-token]
```

GitHub specific branch:
```
[github,username/repo-name/path/to/file?ref=branch-name]
```

## Secrets Management

### Storing Secrets

**Via CLI:**
```bash
# Create a secret from a file
echo "my-secret-value" > secret.txt
limacharlie hive set secret --key my-secret-name --data secret.txt --data-key secret

# Create a secret from stdin
echo "my-secret-value" | limacharlie hive set secret --key my-secret-name --data - --data-key secret
```

**Via Web UI:**
1. Navigate to Organization Settings > Secrets Manager
2. Click "Add Secret"
3. Enter secret name and value
4. Click "Save Secret"

### Using Secrets

Reference secrets in configurations using the hive ARL format:

**In Outputs:**
```yaml
outputs:
  my-output:
    stream: syslog
    dest_host: syslog.example.com
    secret_key: hive://secret/syslog-credentials
```

**In Adapters:**
```yaml
adapters:
  my-adapter:
    type: s3
    credentials: hive://secret/aws-credentials
```

**In Extensions:**
```yaml
extensions:
  ext-virustotal:
    api_key: hive://secret/virustotal-api-key
```

### Updating Secrets

**Via CLI:**
```bash
limacharlie hive update secret --key my-secret-name --data new-secret.txt --data-key secret
```

**Via Web UI:**
1. Organization Settings > Secrets Manager
2. Select the secret to update
3. Modify the value
4. Click "Save Secret"

### Security Best Practices

1. **Never hardcode secrets** - Always use hive://secret/ references
2. **Use descriptive names** - Name secrets clearly (e.g., `aws-s3-readonly-key`)
3. **Implement least privilege** - Grant only necessary permissions
4. **Rotate regularly** - Update secrets periodically
5. **Audit access** - Monitor secret usage through metadata
6. **Separate by environment** - Use different secrets for dev/staging/prod

## D&R Rule Storage

### Storing Rules in Hive

**Via CLI:**
```bash
# Add a D&R rule
limacharlie hive set dr-general --key rule-name --data rule.yaml

# List all D&R rules
limacharlie hive list dr-general

# Get a specific rule
limacharlie hive get dr-general --key rule-name

# Remove a rule
limacharlie hive remove dr-general --key rule-name
```

**Via Infrastructure as Code:**
```yaml
version: 3
hives:
  dr-general:
    suspicious-process-execution:
      data:
        detect:
          event: NEW_PROCESS
          op: and
          rules:
            - op: contains
              path: event/FILE_PATH
              value: suspicious
              case sensitive: false
        respond:
          - action: report
            name: Suspicious Process Detected
            priority: 3
      usr_mtd:
        enabled: true
        tags:
          - malware-detection
        comment: "Detects suspicious process execution patterns"
```

### Rule Organization Best Practices

1. **Use descriptive names** - Clear, action-oriented names
2. **Add tags** - Categorize rules (e.g., `malware`, `lateral-movement`)
3. **Include metadata** - Add comments explaining purpose
4. **Version control** - Use Infrastructure as Code for tracking
5. **Test before deploying** - Use replay service for validation
6. **Namespace by purpose** - Group related rules logically

## YARA Storage

### Storing YARA Rules

**Via CLI:**
```bash
# Create YARA rule from file
limacharlie hive set yara --key my-yara-rule --data rule.yara --data-key rule

# List YARA rules
limacharlie hive list yara

# Get YARA rule
limacharlie hive get yara --key my-yara-rule
```

**Rule Format:**
The rule file can contain one or multiple YARA rules:

```yara
rule MalwareDetection {
    meta:
        description = "Detects common malware patterns"
        author = "Security Team"
    strings:
        $a = "malicious_string"
        $b = { 6A 40 68 00 30 00 00 }
    condition:
        $a or $b
}

rule AdditionalRule {
    // Multiple rules can be in the same file
    strings:
        $pattern = "suspicious"
    condition:
        $pattern
}
```

### Using YARA Rules

**In yara_scan commands:**
```bash
# Scan with hive-stored rule
yara_scan hive://yara/my-yara-rule

# Scan specific process
yara_scan hive://yara/my-yara-rule --pid 1234

# Scan file path
yara_scan hive://yara/my-yara-rule --file-path "C:\suspicious\file.exe"
```

**In D&R rules:**
```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/FILE_PATH
  value: Downloads
respond:
  - action: task
    command: yara_scan hive://yara/malware-detection --pid "{{ .event.PROCESS_ID }}"
    suppression:
      max_count: 1
      period: 5m
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
```

**With ext-yara Extension:**
The ext-yara extension can automatically apply YARA rules stored in the hive to files and processes.

### YARA Best Practices

1. **Name rules clearly** - Use descriptive, purpose-driven names
2. **Add metadata** - Include author, description, date
3. **Test thoroughly** - Validate against known samples
4. **Optimize performance** - Avoid overly broad patterns
5. **Version rules** - Track changes over time
6. **Group related rules** - Store related rules together
7. **Document conditions** - Comment complex logic

## Lookups

### Creating Lookups

**Via Web UI:**
1. Navigate to Automation > Lookups
2. Click "Add Lookup"
3. Enter name and select format
4. Paste lookup data
5. Click "Save"

**Via CLI:**
```bash
# Create lookup from JSON file
limacharlie hive set lookup --key threat-domains --data domains.json

# Create lookup from inline data
cat <<EOF | limacharlie hive set lookup --key allowlist-ips --data -
{
  "lookup_data": {
    "8.8.8.8": {"type": "dns"},
    "1.1.1.1": {"type": "dns"}
  }
}
EOF
```

**Via Infrastructure as Code:**
```yaml
hives:
  lookup:
    malicious-domains:
      data:
        lookup_data:
          evil.com:
            threat_level: high
            category: malware
          phishing.net:
            threat_level: medium
            category: phishing
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
        comment: "Known malicious domains"
```

### Using Lookups in D&R Rules

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malicious-domains
  case sensitive: false
respond:
  - action: report
    name: "DNS request to known malicious domain"
    priority: 4
```

### Automated Lookup Management

Use the ext-lookup-manager extension for automatic synchronization:

```yaml
hives:
  extension_config:
    ext-lookup-manager:
      data:
        lookup_manager_rules:
          - name: tor-exit-nodes
            format: json
            predefined: '[https,storage.googleapis.com/lc-lookups-bucket/tor-ips.json]'
            tags:
              - tor
              - threat-intel
          - name: custom-threat-feed
            format: json
            arl: '[https,api.example.com/threats,bearer,hive://secret/api-token]'
            tags:
              - custom
      usr_mtd:
        enabled: true
```

The Lookup Manager automatically refreshes lookups every 24 hours, or manually via the "Manual Sync" button.

### Lookup Best Practices

1. **Choose appropriate format** - JSON for metadata, newline for simple lists
2. **Use descriptive keys** - Clear, searchable lookup keys
3. **Add meaningful metadata** - Include context for matches
4. **Keep updated** - Use Lookup Manager for dynamic feeds
5. **Tag appropriately** - Categorize lookups for easy management
6. **Monitor size** - Large lookups impact performance
7. **Test before deployment** - Validate lookup data format

## Access Control

### Permission Model

Hive permissions follow a granular model:

**Operations:**
- `.get` - Retrieve configuration data
- `.set` - Create or update configuration
- `.del` - Delete configuration
- `.get.mtd` - Get metadata only
- `.set.mtd` - Update metadata only
- `.list` - List available keys
- `.list.managed` - List managed resources

**Permission Examples:**
```
secret.get          # Read secrets
secret.set          # Write secrets
dr.list             # List D&R rules
lookup.get.mtd      # Get lookup metadata only
yara.set            # Create/update YARA rules
```

### User Metadata (usr_mtd)

All hive records support metadata for management and organization:

```yaml
usr_mtd:
  enabled: true              # Enable/disable the record
  expiry: 0                  # Unix timestamp (0 = never expires)
  tags:                      # Categorization tags
    - production
    - threat-intel
  comment: "Description"     # Human-readable description
```

### Security Best Practices

1. **Least Privilege** - Grant minimum necessary permissions
2. **Separate Concerns** - Use different secrets for different purposes
3. **Audit Regularly** - Review permissions and access logs
4. **Use Metadata Permissions** - Allow metadata-only access when appropriate
5. **Enable/Disable** - Use `enabled: false` instead of deletion
6. **Tag for Access Control** - Use tags to organize and control access
7. **Document Access** - Use comments to explain permission grants

## CLI Command Reference

### General Hive Commands

```bash
# List all records in a hive
limacharlie hive list HIVE_NAME

# List metadata only
limacharlie hive list_mtd HIVE_NAME

# Get a specific record
limacharlie hive get HIVE_NAME --key KEY_NAME

# Get metadata only
limacharlie hive get_mtd HIVE_NAME --key KEY_NAME

# Set/Create a record
limacharlie hive set HIVE_NAME --key KEY_NAME --data FILE_PATH

# Update a record
limacharlie hive update HIVE_NAME --key KEY_NAME --data FILE_PATH

# Remove a record
limacharlie hive remove HIVE_NAME --key KEY_NAME
```

### Advanced Options

```bash
# Use custom partition key (for multi-org scenarios)
limacharlie hive set HIVE_NAME --key KEY --data FILE --partition-key CUSTOM_OID

# Set expiry timestamp
limacharlie hive set HIVE_NAME --key KEY --data FILE --expiry 1735689600000

# Enable/disable record
limacharlie hive set HIVE_NAME --key KEY --data FILE --enabled false

# Add tags
limacharlie hive set HIVE_NAME --key KEY --data FILE --tags tag1,tag2,tag3

# Use etag for conditional updates
limacharlie hive update HIVE_NAME --key KEY --data FILE --etag previous-etag-value

# Read from stdin
echo '{"secret": "value"}' | limacharlie hive set secret --key my-secret --data -
```

### Hive-Specific Examples

**Secrets:**
```bash
limacharlie hive set secret --key aws-key --data secret.txt --data-key secret
limacharlie hive list secret
```

**D&R Rules:**
```bash
limacharlie hive set dr-general --key malware-detect --data rule.yaml
limacharlie hive get dr-general --key malware-detect
```

**YARA Rules:**
```bash
limacharlie hive set yara --key malware-rules --data rules.yara --data-key rule
limacharlie hive list yara
```

**Lookups:**
```bash
limacharlie hive set lookup --key threat-ips --data ips.json
limacharlie hive get lookup --key threat-ips
```

**Cloud Sensors:**
```bash
limacharlie hive set cloudsensor --key my-webhook --data webhook.json
limacharlie hive list cloudsensor
```

## Infrastructure as Code Integration

### IaC Structure

Config Hive integrates seamlessly with LimaCharlie's Infrastructure as Code extension:

```yaml
version: 3
hives:
  secret:
    api-key-example:
      data:
        secret: "encrypted-value-here"
      usr_mtd:
        enabled: true
        tags:
          - production

  dr-general:
    suspicious-activity:
      data:
        detect:
          event: NEW_PROCESS
          # ... detection logic
        respond:
          - action: report
            name: detection-name
      usr_mtd:
        enabled: true
        tags:
          - malware

  yara:
    malware-detection:
      data:
        rule: |
          rule Malware {
            strings: $a = "evil"
            condition: $a
          }
      usr_mtd:
        enabled: true

  lookup:
    threat-domains:
      data:
        lookup_data:
          evil.com: {}
      usr_mtd:
        enabled: true

  extension_config:
    ext-lookup-manager:
      data:
        lookup_manager_rules:
          - name: tor-nodes
            format: json
            predefined: '[https,example.com/tor.json]'
      usr_mtd:
        enabled: true
```

### IaC Operations

**Fetch Current Configuration:**
```bash
# Via CLI
limacharlie infra fetch > current-config.yaml

# Via REST API
POST /extension/ext-infrastructure
{
  "action": "fetch"
}
```

**Push Configuration:**
```bash
# Additive push (merge with existing)
limacharlie infra push -f config.yaml

# Force push (exact copy, destructive)
limacharlie infra push -f config.yaml --force

# Dry run (validate without applying)
limacharlie infra push -f config.yaml --dry-run

# Sync specific components
limacharlie infra push -f config.yaml --sync-dr --sync-outputs
```

**Sync Options:**
- `--sync-dr` - Sync D&R rules
- `--sync-outputs` - Sync outputs
- `--sync-resources` - Sync resources
- `--sync-artifacts` - Sync artifact collection rules
- `--sync-integrity` - Sync integrity rules
- `--sync-fp` - Sync false positive rules
- `--sync-exfil` - Sync exfiltration rules
- `--sync-org-values` - Sync organization values

### Multi-Organization Management

Use IaC to manage configurations across multiple Organizations:

```bash
# Export from source org
limacharlie -o source-org infra fetch > template.yaml

# Push to target orgs
limacharlie -o target-org-1 infra push -f template.yaml
limacharlie -o target-org-2 infra push -f template.yaml
```

### Version Control Integration

Store IaC configs in Git for version control:

```bash
# Initialize repo
git init limacharlie-config
cd limacharlie-config

# Fetch and commit current state
limacharlie infra fetch > config.yaml
git add config.yaml
git commit -m "Initial configuration snapshot"

# Make changes and track
# ... edit config.yaml ...
git diff config.yaml
git add config.yaml
git commit -m "Add new detection rules"

# Deploy from version control
git checkout production
limacharlie infra push -f config.yaml
```

## Best Practices

### Naming Conventions

1. **Use kebab-case** - `my-secret-name` not `mySecretName` or `my_secret_name`
2. **Be descriptive** - `aws-s3-readonly-credentials` not `aws-key`
3. **Include environment** - `prod-api-key`, `dev-api-key`
4. **Namespace by function** - `threat-intel-virustotal`, `threat-intel-otx`
5. **Version when needed** - `yara-rules-v2`, `detection-pack-2024`

### Organization

1. **Tag Everything** - Use tags for categorization and filtering
2. **Add Comments** - Document purpose and usage in metadata
3. **Group Related Items** - Keep related configurations together
4. **Use Consistent Structure** - Follow same patterns across hives
5. **Enable/Disable** - Use flags instead of deletion for testing

### Version Control

1. **Use IaC** - Manage all configs through Infrastructure as Code
2. **Store in Git** - Version control your IaC YAML files
3. **Branching Strategy** - Separate dev/staging/production branches
4. **Review Changes** - Use pull requests for configuration changes
5. **Automate Deployment** - Use CI/CD for config pushes
6. **Document Changes** - Write clear commit messages

### Security

1. **Never Commit Secrets** - Never put actual secrets in IaC files
2. **Use Hive References** - Always use `hive://secret/` ARLs
3. **Rotate Credentials** - Regular rotation schedule
4. **Audit Access** - Review who has hive permissions
5. **Least Privilege** - Grant minimum necessary permissions
6. **Encrypt at Rest** - Hive does this automatically
7. **Monitor Usage** - Track secret and config access

### Performance

1. **Optimize Lookups** - Keep lookup tables reasonably sized
2. **Use Caching** - Leverage hive caching mechanisms
3. **Minimize References** - Don't create unnecessary hive lookups
4. **Archive Old Data** - Disable instead of delete, remove when truly obsolete
5. **Monitor Costs** - Track hive storage and access patterns

### Testing

1. **Test in Dev First** - Never deploy untested configs to production
2. **Use Dry Runs** - Always use `--dry-run` flag first
3. **Validate Rules** - Use replay service for D&R rules
4. **Test YARA Rules** - Validate against known samples
5. **Verify Lookups** - Ensure lookup data is correctly formatted
6. **Check References** - Verify all ARLs resolve correctly

## Common Examples

### Example 1: Storing and Using API Credentials

```bash
# Store API key as secret
echo "sk_live_abc123xyz789" | limacharlie hive set secret --key stripe-api-key --data - --data-key secret

# Reference in adapter configuration
cat <<EOF | limacharlie adapter add stripe-events --data -
{
  "type": "webhook",
  "api_key": "hive://secret/stripe-api-key",
  "endpoint": "https://api.stripe.com/v1/events"
}
EOF
```

### Example 2: Threat Intelligence Lookup Pipeline

```yaml
# Infrastructure as Code configuration
hives:
  # Store API key for threat feed
  secret:
    virustotal-api-key:
      data:
        secret: "actual-api-key-here"
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - production

  # Configure lookup manager to sync feeds
  extension_config:
    ext-lookup-manager:
      data:
        lookup_manager_rules:
          - name: malware-domains
            format: json
            arl: '[https,api.threatfeed.com/domains,bearer,hive://secret/virustotal-api-key]'
            tags:
              - threat-intel
              - domains
      usr_mtd:
        enabled: true

  # Create D&R rule to use lookup
  dr-general:
    threat-domain-detection:
      data:
        detect:
          event: DNS_REQUEST
          op: lookup
          path: event/DOMAIN_NAME
          resource: hive://lookup/malware-domains
          case sensitive: false
        respond:
          - action: report
            name: "Malicious domain accessed"
            priority: 4
          - action: add tag
            tag: threat-detected
            ttl: 3600
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
```

### Example 3: YARA Scanning Workflow

```bash
# 1. Store YARA rules
cat <<EOF > malware.yara
rule SuspiciousStrings {
    meta:
        description = "Detects suspicious strings"
        author = "Security Team"
    strings:
        \$cmd1 = "powershell" nocase
        \$cmd2 = "-enc" nocase
        \$cmd3 = "bypass" nocase
    condition:
        2 of them
}
EOF

limacharlie hive set yara --key malware-detection --data malware.yara --data-key rule

# 2. Create D&R rule to trigger scan
cat <<EOF > scan-rule.yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/FILE_PATH
  value: Downloads
  case sensitive: false
respond:
  - action: task
    command: yara_scan hive://yara/malware-detection --pid "{{ .event.PROCESS_ID }}"
    investigation: downloads-yara-scan
    suppression:
      max_count: 1
      period: 5m
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
        - downloads-yara-scan
EOF

limacharlie hive set dr-general --key scan-downloads --data scan-rule.yaml
```

### Example 4: Multi-Organization Secrets Management

```bash
# 1. Create secret in parent org
limacharlie -o parent-org hive set secret --key shared-api-key --data api-key.txt --data-key secret

# 2. Export IaC configuration
limacharlie -o parent-org infra fetch > shared-config.yaml

# 3. Filter only secrets (manual edit or script)
cat <<EOF > secrets-only.yaml
version: 3
hives:
  secret:
    shared-api-key:
      data:
        secret: "key-value-here"
      usr_mtd:
        enabled: true
        tags:
          - shared
          - production
EOF

# 4. Deploy to child organizations
for org in child-org-1 child-org-2 child-org-3; do
  limacharlie -o $org infra push -f secrets-only.yaml
done
```

### Example 5: Lookup-Based Allow List

```yaml
hives:
  # Create allow list lookup
  lookup:
    known-good-processes:
      data:
        lookup_data:
          "c:\\windows\\system32\\svchost.exe":
            category: "windows-system"
            verified: true
          "c:\\windows\\system32\\lsass.exe":
            category: "windows-system"
            verified: true
          "c:\\program files\\company\\app.exe":
            category: "corporate-app"
            verified: true
      usr_mtd:
        enabled: true
        tags:
          - allowlist
          - processes

  # Create D&R rule that excludes allow list
  dr-general:
    unsigned-process-not-allowlisted:
      data:
        detect:
          event: CODE_IDENTITY
          op: and
          rules:
            - op: is
              path: event/SIGNATURE/CERT_CHAIN/VERIFICATION
              value: false
            - op: lookup
              not: true  # NOT in allowlist
              path: event/FILE_PATH
              resource: hive://lookup/known-good-processes
              case sensitive: false
        respond:
          - action: report
            name: "Unsigned process not in allowlist"
            priority: 2
      usr_mtd:
        enabled: true
        tags:
          - code-signing
```

## Troubleshooting

### Common Issues

**Issue: "Permission denied" when accessing hive**
- Check user permissions (`secret.get`, `dr.list`, etc.)
- Verify organization access
- Ensure API key has correct permissions

**Issue: "Hive record not found"**
- Verify key name (case-sensitive)
- Check hive type is correct
- Use `list` command to see available keys

**Issue: "Invalid ARL format"**
- Check ARL syntax: `hive://TYPE/KEY`
- Ensure hive type is valid
- Verify key exists

**Issue: "Secret not decrypting in output"**
- Confirm ARL format: `hive://secret/KEY`
- Check secret exists with `hive get secret --key KEY`
- Verify output has permission to access secrets

**Issue: "YARA rule not found"**
- Verify rule stored with `--data-key rule`
- Check rule name in hive
- Confirm ARL: `hive://yara/RULE_NAME`

**Issue: "Lookup not matching expected values"**
- Verify lookup data format
- Check case sensitivity settings
- Test lookup with known values
- Review lookup metadata

**Issue: "IaC push failing"**
- Use `--dry-run` to see what would change
- Check YAML syntax
- Verify permissions for all resources
- Review error messages for specific failures

### Debugging Tips

1. **List Available Records**
   ```bash
   limacharlie hive list HIVE_NAME
   ```

2. **Check Metadata Only**
   ```bash
   limacharlie hive get_mtd HIVE_NAME --key KEY
   ```

3. **Validate ARL Resolution**
   Test ARLs in a simple D&R rule or output first

4. **Review Permissions**
   ```bash
   limacharlie user get --user-email EMAIL
   ```

5. **Test in Isolation**
   Create test hive records to validate behavior

6. **Check Logs**
   Review detection logs for hive-related errors

7. **Use Dry Run**
   ```bash
   limacharlie infra push -f config.yaml --dry-run
   ```

## Additional Resources

### CLI Commands Quick Reference

```bash
# List operations
limacharlie hive list secret
limacharlie hive list dr-general
limacharlie hive list yara
limacharlie hive list lookup
limacharlie hive list cloudsensor

# Get operations
limacharlie hive get secret --key KEY
limacharlie hive get dr-general --key KEY
limacharlie hive get yara --key KEY

# Set operations
limacharlie hive set secret --key KEY --data FILE --data-key secret
limacharlie hive set dr-general --key KEY --data FILE
limacharlie hive set yara --key KEY --data FILE --data-key rule
limacharlie hive set lookup --key KEY --data FILE

# Remove operations
limacharlie hive remove secret --key KEY
limacharlie hive remove dr-general --key KEY
```

### Web UI Locations

- **Secrets**: Organization Settings > Secrets Manager
- **D&R Rules**: Automation > D&R Rules
- **YARA Rules**: Automation > YARA Rules (if ext-yara enabled)
- **Lookups**: Automation > Lookups
- **Cloud Sensors**: Sensors > Cloud Sensors
- **Infrastructure as Code**: Organization Settings > Infrastructure as Code

### Related Extensions

- **ext-infrastructure** - Infrastructure as Code management
- **ext-lookup-manager** - Automated lookup synchronization
- **ext-yara** - YARA rule scanning
- **ext-yara-manager** - YARA rule management
- **ext-artifact** - Artifact collection (uses hive for config)
- **ext-reliable-tasking** - Task management (uses hive)

## Key Reminders

1. Always use `hive://TYPE/KEY` format for references
2. Never hardcode secrets - use hive://secret/ ARLs
3. Tag and comment all hive records for organization
4. Use Infrastructure as Code for version control
5. Test configurations before production deployment
6. Use appropriate permissions for least privilege
7. Enable/disable instead of delete for testing
8. Store YARA rules with `--data-key rule`
9. Store secrets with `--data-key secret`
10. Use Lookup Manager for dynamic threat feeds
11. Reference external resources with proper ARLs
12. Audit hive access regularly
13. Rotate secrets on a schedule
14. Document all configurations clearly
15. Use dry-run before pushing IaC changes

This skill provides comprehensive guidance for managing the Config Hive. When helping users, always encourage proper security practices and testing before production deployment.
