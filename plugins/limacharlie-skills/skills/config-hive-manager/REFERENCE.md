# Config Hive Technical Reference

Complete technical reference for LimaCharlie Config Hive types, ARLs, permissions, and CLI commands.

## Hive Types

### secret (Secrets Hive)

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

**CLI Examples:**
```bash
# Create secret from file
limacharlie hive set secret --key aws-key --data secret.txt --data-key secret

# Create secret from stdin
echo "secret-value" | limacharlie hive set secret --key aws-key --data - --data-key secret

# List all secrets
limacharlie hive list secret

# Get secret (only shows metadata unless you have secret.get permission)
limacharlie hive get secret --key aws-key

# Get metadata only
limacharlie hive get_mtd secret --key aws-key

# Delete secret
limacharlie hive remove secret --key aws-key
```

### dr-general (Detection & Response Rules)

Stores D&R rules created and controlled by your Organization.

**Data Format:**
```yaml
detect:
  event: EVENT_TYPE
  op: operator
  # ... detection logic
respond:
  - action: ACTION_TYPE
    # ... response configuration
```

**Permissions:**
- `dr.list` - List rules
- `dr.set` - Create/update rules
- `dr.del` - Delete rules

**Related Hive Types:**
- `dr-managed` - Rules managed/curated by third parties (e.g., Soteria rules)
  - Permissions: `dr.list.managed`, `dr.set.managed`, `dr.del.managed`
- `dr-service` - Protected namespace (metadata-only access)
  - Permissions: `dr.list` or `dr.list.managed` (metadata only)

**CLI Examples:**
```bash
# Add D&R rule
limacharlie hive set dr-general --key rule-name --data rule.yaml

# List all D&R rules
limacharlie hive list dr-general

# Get specific rule
limacharlie hive get dr-general --key rule-name

# Remove rule
limacharlie hive remove dr-general --key rule-name
```

### yara (YARA Rules)

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

**Rule Format:**
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

**CLI Examples:**
```bash
# Create YARA rule from file
limacharlie hive set yara --key my-yara-rule --data rule.yara --data-key rule

# List YARA rules
limacharlie hive list yara

# Get YARA rule
limacharlie hive get yara --key my-yara-rule

# Delete YARA rule
limacharlie hive remove yara --key my-yara-rule
```

### lookup (Lookup Tables)

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

**CLI Examples:**
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

# List lookups
limacharlie hive list lookup

# Get lookup
limacharlie hive get lookup --key threat-domains

# Delete lookup
limacharlie hive remove lookup --key threat-domains
```

### cloudsensor (Cloud Sensors)

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

**CLI Examples:**
```bash
# Create cloud sensor
limacharlie hive set cloudsensor --key my-webhook --data webhook.json

# List cloud sensors
limacharlie hive list cloudsensor

# Get cloud sensor
limacharlie hive get cloudsensor --key my-webhook

# Delete cloud sensor
limacharlie hive remove cloudsensor --key my-webhook
```

### extension_config (Extension Configurations)

Stores configuration for LimaCharlie extensions like lookup-manager, usage-alerts, etc.

**Common Extensions:**
- `ext-lookup-manager` - Automated lookup synchronization
- `ext-usage-alerts` - Usage threshold alerts
- `ext-yara-manager` - YARA rule management
- Custom extension configurations

**Example Configuration:**
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
      usr_mtd:
        enabled: true
```

**CLI Examples:**
```bash
# Create extension config
limacharlie hive set extension_config --key ext-lookup-manager --data config.json

# List extension configs
limacharlie hive list extension_config

# Get extension config
limacharlie hive get extension_config --key ext-lookup-manager
```

## Authentication Resource Locators (ARLs)

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
hive://cloudsensor/webhook-config
hive://extension_config/ext-lookup-manager
```

### External Resource ARLs

Reference external resources with optional authentication.

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

### HTTP/HTTPS ARLs

**HTTP GET with no authentication:**
```
[https,my.corpwebsite.com/resource-data]
```

**HTTP GET with basic authentication:**
```
[https,my.corpwebsite.com/resource-data,basic,username:password]
```

**HTTP GET with bearer token:**
```
[https,my.corpwebsite.com/resource-data,bearer,token-value-here]
```

**HTTP GET with bearer token from hive:**
```
[https,api.example.com/data,bearer,hive://secret/api-token]
```

**HTTP with custom headers:**
```
[https,api.example.com/data,token,hive://secret/api-key]
```

### Google Cloud Storage ARLs

**Public GCS bucket:**
```
[gcs,bucket-name/blob-prefix]
```

**Private GCS bucket with service account:**
```
[gcs,bucket-name/blob-prefix,gaia,base64(SERVICE_KEY_JSON)]
```

**GCS with service key from hive:**
```
[gcs,bucket-name/blob-prefix,gaia,hive://secret/gcs-service-key]
```

### GitHub ARLs

**Public GitHub repository:**
```
[github,username/repo-name/path/to/file]
```

**Private GitHub with personal access token:**
```
[github,username/repo-name/path/to/file,token,github-personal-access-token]
```

**GitHub with token from hive:**
```
[github,username/repo-name/path/to/file,token,hive://secret/github-token]
```

**GitHub specific branch:**
```
[github,username/repo-name/path/to/file?ref=branch-name]
```

**GitHub specific tag:**
```
[github,username/repo-name/path/to/file?ref=v1.0.0]
```

### OTX (AlienVault) ARLs

**OTX threat feed:**
```
[otx,pulse-id,otx,api-key]
```

**OTX with key from hive:**
```
[otx,pulse-id,otx,hive://secret/otx-api-key]
```

## Access Control

### Permission Model

Hive permissions follow a granular model with the following operations:

**Operations:**
- `.get` - Retrieve configuration data
- `.set` - Create or update configuration
- `.del` - Delete configuration
- `.get.mtd` - Get metadata only (without exposing sensitive data)
- `.set.mtd` - Update metadata only (without changing data)
- `.list` - List available keys
- `.list.managed` - List managed resources (for dr-managed)

**Permission Examples:**

```
secret.get          # Read secret values
secret.set          # Create/update secrets
secret.del          # Delete secrets
secret.get.mtd      # Get secret metadata only
secret.set.mtd      # Update secret metadata only

dr.list             # List D&R rules
dr.set              # Create/update D&R rules
dr.del              # Delete D&R rules
dr.list.managed     # List managed D&R rules
dr.set.managed      # Create/update managed D&R rules
dr.del.managed      # Delete managed D&R rules

yara.get            # Read YARA rules
yara.set            # Create/update YARA rules
yara.del            # Delete YARA rules
yara.get.mtd        # Get YARA metadata only
yara.set.mtd        # Update YARA metadata only

lookup.get          # Read lookup data
lookup.set          # Create/update lookups
lookup.del          # Delete lookups
lookup.get.mtd      # Get lookup metadata only
lookup.set.mtd      # Update lookup metadata only

cloudsensor.get     # Read cloud sensor configs
cloudsensor.set     # Create/update cloud sensors
cloudsensor.del     # Delete cloud sensors
cloudsensor.get.mtd # Get cloud sensor metadata
cloudsensor.set.mtd # Update cloud sensor metadata
```

### User Metadata (usr_mtd)

All hive records support metadata for management and organization:

```yaml
usr_mtd:
  enabled: true              # Enable/disable the record
  expiry: 0                  # Unix timestamp (0 = never expires)
  tags:                      # Categorization tags (array of strings)
    - production
    - threat-intel
    - critical
  comment: "Description"     # Human-readable description
```

**Fields:**
- `enabled` (boolean) - Whether the record is active (default: true)
- `expiry` (integer) - Unix timestamp in milliseconds when record expires (0 = never)
- `tags` (array) - List of tags for categorization and filtering
- `comment` (string) - Description or notes about the record

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

**List all records in a hive:**
```bash
limacharlie hive list HIVE_NAME
```

**List metadata only:**
```bash
limacharlie hive list_mtd HIVE_NAME
```

**Get a specific record:**
```bash
limacharlie hive get HIVE_NAME --key KEY_NAME
```

**Get metadata only:**
```bash
limacharlie hive get_mtd HIVE_NAME --key KEY_NAME
```

**Set/Create a record:**
```bash
limacharlie hive set HIVE_NAME --key KEY_NAME --data FILE_PATH
```

**Update a record:**
```bash
limacharlie hive update HIVE_NAME --key KEY_NAME --data FILE_PATH
```

**Remove a record:**
```bash
limacharlie hive remove HIVE_NAME --key KEY_NAME
```

### Advanced CLI Options

**Use custom partition key (for multi-org scenarios):**
```bash
limacharlie hive set HIVE_NAME --key KEY --data FILE --partition-key CUSTOM_OID
```

**Set expiry timestamp:**
```bash
limacharlie hive set HIVE_NAME --key KEY --data FILE --expiry 1735689600000
```

**Enable/disable record:**
```bash
limacharlie hive set HIVE_NAME --key KEY --data FILE --enabled false
```

**Add tags:**
```bash
limacharlie hive set HIVE_NAME --key KEY --data FILE --tags tag1,tag2,tag3
```

**Use etag for conditional updates:**
```bash
limacharlie hive update HIVE_NAME --key KEY --data FILE --etag previous-etag-value
```

**Read from stdin:**
```bash
echo '{"secret": "value"}' | limacharlie hive set secret --key my-secret --data -
```

**Specify data key for nested data:**
```bash
limacharlie hive set secret --key my-secret --data secret.txt --data-key secret
limacharlie hive set yara --key my-rule --data rule.yara --data-key rule
```

### Hive-Specific CLI Examples

**Secrets:**
```bash
# Create secret
limacharlie hive set secret --key aws-key --data secret.txt --data-key secret

# List secrets
limacharlie hive list secret

# Get secret
limacharlie hive get secret --key aws-key

# Delete secret
limacharlie hive remove secret --key aws-key
```

**D&R Rules:**
```bash
# Create rule
limacharlie hive set dr-general --key malware-detect --data rule.yaml

# List rules
limacharlie hive list dr-general

# Get rule
limacharlie hive get dr-general --key malware-detect

# Delete rule
limacharlie hive remove dr-general --key malware-detect
```

**YARA Rules:**
```bash
# Create YARA rule
limacharlie hive set yara --key malware-rules --data rules.yara --data-key rule

# List YARA rules
limacharlie hive list yara

# Get YARA rule
limacharlie hive get yara --key malware-rules

# Delete YARA rule
limacharlie hive remove yara --key malware-rules
```

**Lookups:**
```bash
# Create lookup
limacharlie hive set lookup --key threat-ips --data ips.json

# List lookups
limacharlie hive list lookup

# Get lookup
limacharlie hive get lookup --key threat-ips

# Delete lookup
limacharlie hive remove lookup --key threat-ips
```

**Cloud Sensors:**
```bash
# Create cloud sensor
limacharlie hive set cloudsensor --key my-webhook --data webhook.json

# List cloud sensors
limacharlie hive list cloudsensor

# Get cloud sensor
limacharlie hive get cloudsensor --key my-webhook

# Delete cloud sensor
limacharlie hive remove cloudsensor --key my-webhook
```

**Extension Configs:**
```bash
# Create extension config
limacharlie hive set extension_config --key ext-lookup-manager --data config.json

# List extension configs
limacharlie hive list extension_config

# Get extension config
limacharlie hive get extension_config --key ext-lookup-manager

# Delete extension config
limacharlie hive remove extension_config --key ext-lookup-manager
```

## Infrastructure as Code API

### REST API Endpoints

**Fetch configuration:**
```
POST /extension/ext-infrastructure
{
  "action": "fetch"
}
```

**Push configuration:**
```
POST /extension/ext-infrastructure
{
  "action": "push",
  "config": { ... },
  "is_dry_run": false,
  "is_force": false
}
```

### CLI IaC Operations

**Fetch current configuration:**
```bash
limacharlie infra fetch > current-config.yaml
```

**Push configuration (additive merge):**
```bash
limacharlie infra push -f config.yaml
```

**Force push (exact copy, destructive):**
```bash
limacharlie infra push -f config.yaml --force
```

**Dry run (validate without applying):**
```bash
limacharlie infra push -f config.yaml --dry-run
```

### Sync Options

**Sync specific components:**
```bash
limacharlie infra push -f config.yaml --sync-dr --sync-outputs
```

**Available sync flags:**
- `--sync-dr` - Sync D&R rules
- `--sync-outputs` - Sync outputs
- `--sync-resources` - Sync resources
- `--sync-artifacts` - Sync artifact collection rules
- `--sync-integrity` - Sync integrity rules
- `--sync-fp` - Sync false positive rules
- `--sync-exfil` - Sync exfiltration rules
- `--sync-org-values` - Sync organization values

## Web UI Locations

Access Config Hive resources through the LimaCharlie web interface:

- **Secrets**: Organization Settings > Secrets Manager
- **D&R Rules**: Automation > D&R Rules
- **YARA Rules**: Automation > YARA Rules (if ext-yara enabled)
- **Lookups**: Automation > Lookups
- **Cloud Sensors**: Sensors > Cloud Sensors
- **Infrastructure as Code**: Organization Settings > Infrastructure as Code

## Related Extensions

- **ext-infrastructure** - Infrastructure as Code management
- **ext-lookup-manager** - Automated lookup synchronization
- **ext-yara** - YARA rule scanning
- **ext-yara-manager** - YARA rule management
- **ext-artifact** - Artifact collection (uses hive for config)
- **ext-reliable-tasking** - Task management (uses hive)
- **ext-usage-alerts** - Usage monitoring and alerts

## API Reference

### Hive Data Structure

All hive records follow this structure:

```json
{
  "data": {
    // Hive-specific data structure
  },
  "usr_mtd": {
    "enabled": true,
    "expiry": 0,
    "tags": ["tag1", "tag2"],
    "comment": "Description"
  },
  "sys_mtd": {
    "created": 1234567890000,
    "modified": 1234567890000,
    "etag": "hash-value"
  }
}
```

### Data Key Requirements

Different hive types have specific data key requirements:

- **secret**: Must use `--data-key secret`
- **yara**: Must use `--data-key rule`
- **lookup**: Data can be `lookup_data`, `newline_content`, or `yaml_content`
- **dr-general**: Direct YAML structure
- **cloudsensor**: Direct JSON structure
- **extension_config**: Extension-specific structure

### ETag Usage

ETags enable conditional updates to prevent conflicts:

```bash
# Get current etag
ETAG=$(limacharlie hive get_mtd secret --key my-secret | jq -r '.sys_mtd.etag')

# Update with etag check
limacharlie hive update secret --key my-secret --data new-value.txt --etag "$ETAG"
```

If the etag doesn't match (someone else modified the record), the update will fail.
