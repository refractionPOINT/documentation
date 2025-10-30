# Config Hive Usage Examples

Practical examples for common Config Hive usage patterns including secrets management, D&R rules, YARA scanning, lookups, and Infrastructure as Code workflows.

## Secrets Management

### Example 1: Storing and Using API Credentials

Store API credentials securely and reference them in configurations:

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

### Example 2: AWS Credentials for S3 Output

```bash
# Store AWS credentials
cat <<EOF > aws-creds.json
{
  "secret": {
    "access_key": "AKIAIOSFODNN7EXAMPLE",
    "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  }
}
EOF

limacharlie hive set secret --key aws-s3-credentials --data aws-creds.json --data-key secret

# Use in S3 output
cat <<EOF | limacharlie output add s3-logs --data -
{
  "stream": "event",
  "bucket": "my-lc-logs",
  "credentials": "hive://secret/aws-s3-credentials"
}
EOF
```

### Example 3: Database Credentials with Tags

```bash
# Store database credentials with metadata
cat <<EOF > db-creds.txt
host=db.example.com;username=app_user;password=secure_password;database=production
EOF

limacharlie hive set secret --key production-db-credentials \
  --data db-creds.txt \
  --data-key secret \
  --tags production,database,critical \
  --enabled true

# Verify it was stored correctly
limacharlie hive get_mtd secret --key production-db-credentials
```

### Example 4: Multi-Environment Secret Management

```bash
# Development environment
echo "dev-api-key-12345" | limacharlie hive set secret \
  --key api-key-dev \
  --data - \
  --data-key secret \
  --tags development,api-keys

# Staging environment
echo "staging-api-key-67890" | limacharlie hive set secret \
  --key api-key-staging \
  --data - \
  --data-key secret \
  --tags staging,api-keys

# Production environment
echo "prod-api-key-abcdef" | limacharlie hive set secret \
  --key api-key-prod \
  --data - \
  --data-key secret \
  --tags production,api-keys,critical

# Reference environment-specific secret
# In your IaC: hive://secret/api-key-prod
```

### Example 5: External API with Bearer Token

```bash
# Store bearer token
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." | limacharlie hive set secret \
  --key external-api-bearer-token \
  --data - \
  --data-key secret

# Use in Lookup Manager with external feed
cat <<EOF | limacharlie hive set extension_config --key ext-lookup-manager --data -
{
  "lookup_manager_rules": [
    {
      "name": "external-threat-feed",
      "format": "json",
      "arl": "[https,api.threatfeed.com/indicators,bearer,hive://secret/external-api-bearer-token]",
      "tags": ["threat-intel", "external"]
    }
  ]
}
EOF
```

## D&R Rule Storage

### Example 1: Store Simple Detection Rule

```bash
# Create D&R rule file
cat <<EOF > suspicious-process.yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: powershell
      case sensitive: false
    - op: contains
      path: event/COMMAND_LINE
      value: "-enc"
      case sensitive: false
respond:
  - action: report
    name: Suspicious PowerShell Execution
    priority: 3
  - action: add tag
    tag: suspicious-activity
    ttl: 3600
EOF

# Store in hive
limacharlie hive set dr-general --key suspicious-powershell --data suspicious-process.yaml

# Verify
limacharlie hive get dr-general --key suspicious-powershell
```

### Example 2: Detection with Multiple Responses

```yaml
# Store via IaC
hives:
  dr-general:
    credential-dumping-detection:
      data:
        detect:
          event: NEW_PROCESS
          op: and
          rules:
            - op: contains
              path: event/FILE_PATH
              value: "mimikatz"
              case sensitive: false
        respond:
          - action: report
            name: Credential Dumping Attempt
            priority: 5
          - action: add tag
            tag: credential-theft
            ttl: 7200
          - action: task
            command: deny_tree
            investigation: credential-theft-response
          - action: task
            command: mem_map
            investigation: credential-theft-forensics
      usr_mtd:
        enabled: true
        tags:
          - credential-theft
          - high-severity
          - auto-response
        comment: "Detects and responds to credential dumping tools"
```

### Example 3: Rule with Lookup Integration

```yaml
hives:
  # First create the lookup
  lookup:
    known-malicious-hashes:
      data:
        lookup_data:
          "5d41402abc4b2a76b9719d911017c592":
            malware_family: "ransomware"
            severity: "critical"
          "098f6bcd4621d373cade4e832627b4f6":
            malware_family: "trojan"
            severity: "high"
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - hashes

  # Then create rule using the lookup
  dr-general:
    malicious-hash-detection:
      data:
        detect:
          event: CODE_IDENTITY
          op: lookup
          path: event/HASH
          resource: hive://lookup/known-malicious-hashes
        respond:
          - action: report
            name: "Known malicious file hash detected"
            priority: 5
          - action: add tag
            tag: malware-detected
            ttl: 86400
      usr_mtd:
        enabled: true
        tags:
          - malware-detection
```

## YARA Rule Management

### Example 1: Basic YARA Rule Storage

```bash
# Create YARA rule file
cat <<EOF > malware-detection.yara
rule SuspiciousStrings {
    meta:
        description = "Detects suspicious strings in files"
        author = "Security Team"
        date = "2024-01-01"
    strings:
        \$cmd1 = "powershell" nocase
        \$cmd2 = "-enc" nocase
        \$cmd3 = "bypass" nocase
        \$cmd4 = "downloadstring" nocase
    condition:
        2 of them
}

rule PEFileAnomalies {
    meta:
        description = "Detects PE file anomalies"
        author = "Security Team"
    strings:
        \$mz = "MZ"
        \$suspicious = { 6A 40 68 00 30 00 00 }
    condition:
        \$mz at 0 and \$suspicious
}
EOF

# Store in hive
limacharlie hive set yara --key malware-detection --data malware-detection.yara --data-key rule

# Verify storage
limacharlie hive list yara
limacharlie hive get yara --key malware-detection
```

### Example 2: YARA Scanning Workflow

```bash
# 1. Store YARA rules
cat <<EOF > ransomware-detection.yara
rule RansomwareIndicators {
    meta:
        description = "Detects common ransomware indicators"
        author = "SOC Team"
    strings:
        \$ransom1 = "YOUR FILES HAVE BEEN ENCRYPTED" nocase
        \$ransom2 = "pay bitcoin" nocase
        \$ransom3 = ".locked" nocase
        \$ransom4 = "decrypt_instructions" nocase
    condition:
        any of them
}
EOF

limacharlie hive set yara --key ransomware-detection --data ransomware-detection.yara --data-key rule

# 2. Create D&R rule to trigger scan on suspicious file writes
cat <<EOF > scan-downloads.yaml
detect:
  event: NEW_DOCUMENT
  op: contains
  path: event/FILE_PATH
  value: Downloads
  case sensitive: false
respond:
  - action: task
    command: yara_scan hive://yara/ransomware-detection --file-path "{{ .event.FILE_PATH }}"
    investigation: ransomware-scan
    suppression:
      max_count: 1
      period: 300
      is_global: false
      keys:
        - '{{ .event.FILE_PATH }}'
EOF

limacharlie hive set dr-general --key scan-downloads --data scan-downloads.yaml

# 3. Manually trigger scan on specific process
# (Run this via sensor command)
yara_scan hive://yara/ransomware-detection --pid 1234
```

### Example 3: Multiple YARA Rule Sets

```yaml
hives:
  yara:
    # Malware detection rules
    malware-general:
      data:
        rule: |
          rule GenericMalware {
            strings: $a = "malicious"
            condition: $a
          }
      usr_mtd:
        enabled: true
        tags:
          - malware
          - general

    # Ransomware-specific rules
    malware-ransomware:
      data:
        rule: |
          rule Ransomware {
            strings: $a = "encrypted"
            condition: $a
          }
      usr_mtd:
        enabled: true
        tags:
          - malware
          - ransomware

    # APT-specific rules
    malware-apt:
      data:
        rule: |
          rule APTIndicators {
            strings: $a = "apt_pattern"
            condition: $a
          }
      usr_mtd:
        enabled: true
        tags:
          - malware
          - apt
          - advanced-threats
```

## Lookup Management

### Example 1: Simple Threat Domain List

```bash
# Create JSON lookup with threat domains
cat <<EOF | limacharlie hive set lookup --key threat-domains --data -
{
  "lookup_data": {
    "evil.com": {
      "threat_level": "high",
      "category": "malware",
      "first_seen": "2024-01-01"
    },
    "phishing.net": {
      "threat_level": "medium",
      "category": "phishing",
      "first_seen": "2024-01-15"
    },
    "suspicious.org": {
      "threat_level": "low",
      "category": "suspicious",
      "first_seen": "2024-02-01"
    }
  }
}
EOF

# Use in D&R rule
cat <<EOF > threat-domain-detection.yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/threat-domains
  case sensitive: false
respond:
  - action: report
    name: "DNS request to known threat domain"
    priority: 4
  - action: add tag
    tag: threat-detected
    ttl: 3600
EOF

limacharlie hive set dr-general --key threat-domain-detection --data threat-domain-detection.yaml
```

### Example 2: IP Allow List (Newline Format)

```bash
# Create newline format lookup
cat <<EOF | limacharlie hive set lookup --key corporate-ips --data -
{
  "newline_content": "192.168.1.0/24\n10.0.0.0/8\n172.16.0.0/12"
}
EOF

# Use in D&R rule with NOT lookup (alert on non-corporate IPs)
cat <<EOF > non-corporate-connection.yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: lookup
      not: true
      path: event/IP_ADDRESS
      resource: hive://lookup/corporate-ips
    - op: is
      path: event/STATE
      value: ESTABLISHED
respond:
  - action: report
    name: "Connection to non-corporate IP"
    priority: 2
EOF

limacharlie hive set dr-general --key non-corporate-connection --data non-corporate-connection.yaml
```

### Example 3: Process Allow List

```yaml
hives:
  lookup:
    known-good-processes:
      data:
        lookup_data:
          "c:\\windows\\system32\\svchost.exe":
            category: "windows-system"
            verified: true
            notes: "Windows Service Host"
          "c:\\windows\\system32\\lsass.exe":
            category: "windows-system"
            verified: true
            notes: "Local Security Authority Subsystem"
          "c:\\program files\\company\\app.exe":
            category: "corporate-app"
            verified: true
            notes: "Corporate application"
          "c:\\program files\\google\\chrome\\application\\chrome.exe":
            category: "approved-browser"
            verified: true
            notes: "Chrome browser"
      usr_mtd:
        enabled: true
        tags:
          - allowlist
          - processes
          - verified
        comment: "Known good processes - reviewed monthly"

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
              not: true
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
          - allowlist-enforcement
```

### Example 4: Automated Threat Feed Sync

```yaml
hives:
  # Store API key for threat feed
  secret:
    threatfeed-api-key:
      data:
        secret: "your-api-key-here"
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - api-keys

  # Configure Lookup Manager to sync feeds
  extension_config:
    ext-lookup-manager:
      data:
        lookup_manager_rules:
          # Tor exit nodes
          - name: tor-exit-nodes
            format: json
            predefined: '[https,storage.googleapis.com/lc-lookups-bucket/tor-ips.json]'
            tags:
              - tor
              - anonymization

          # Custom threat feed with authentication
          - name: custom-threat-domains
            format: json
            arl: '[https,api.threatfeed.com/domains,bearer,hive://secret/threatfeed-api-key]'
            tags:
              - threat-intel
              - domains

          # AlienVault OTX feed
          - name: otx-malware-hashes
            format: json
            arl: '[https,otx.alienvault.com/api/v1/pulses/12345/indicators,bearer,hive://secret/otx-api-key]'
            tags:
              - threat-intel
              - hashes
              - otx
      usr_mtd:
        enabled: true
        comment: "Automated threat feed synchronization - runs every 24 hours"

  # Use the synced lookups in D&R rules
  dr-general:
    tor-connection-detection:
      data:
        detect:
          event: NETWORK_CONNECTIONS
          op: lookup
          path: event/IP_ADDRESS
          resource: hive://lookup/tor-exit-nodes
        respond:
          - action: report
            name: "Connection to Tor exit node"
            priority: 3
      usr_mtd:
        enabled: true
        tags:
          - tor
          - anonymization
```

## Infrastructure as Code

### Example 1: Complete Organization Configuration

```yaml
version: 3

hives:
  # Secrets
  secret:
    virustotal-api-key:
      data:
        secret: "your-vt-api-key"
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - production

    syslog-credentials:
      data:
        secret: "syslog-token-12345"
      usr_mtd:
        enabled: true
        tags:
          - outputs
          - production

  # Lookups
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
          - domains

  # D&R Rules
  dr-general:
    threat-domain-detection:
      data:
        detect:
          event: DNS_REQUEST
          op: lookup
          path: event/DOMAIN_NAME
          resource: hive://lookup/malicious-domains
          case sensitive: false
        respond:
          - action: report
            name: "Malicious domain accessed"
            priority: 4
      usr_mtd:
        enabled: true
        tags:
          - threat-intel

    credential-dumping:
      data:
        detect:
          event: NEW_PROCESS
          op: contains
          path: event/FILE_PATH
          value: mimikatz
          case sensitive: false
        respond:
          - action: report
            name: "Credential dumping tool detected"
            priority: 5
          - action: task
            command: deny_tree
      usr_mtd:
        enabled: true
        tags:
          - credential-theft
          - high-severity

  # YARA Rules
  yara:
    malware-detection:
      data:
        rule: |
          rule GenericMalware {
            meta:
              description = "Generic malware patterns"
            strings:
              $a = "malicious"
            condition:
              $a
          }
      usr_mtd:
        enabled: true
        tags:
          - malware

  # Extension Configs
  extension_config:
    ext-lookup-manager:
      data:
        lookup_manager_rules:
          - name: tor-nodes
            format: json
            predefined: '[https,storage.googleapis.com/lc-lookups-bucket/tor-ips.json]'
            tags:
              - tor
      usr_mtd:
        enabled: true
```

### Example 2: Multi-Organization Deployment

```bash
# 1. Export configuration from source organization
limacharlie -o source-org infra fetch > base-config.yaml

# 2. Create organization-specific overrides
cat <<EOF > prod-org-overrides.yaml
version: 3
hives:
  secret:
    environment-marker:
      data:
        secret: "production"
      usr_mtd:
        enabled: true
        tags:
          - production
EOF

cat <<EOF > staging-org-overrides.yaml
version: 3
hives:
  secret:
    environment-marker:
      data:
        secret: "staging"
      usr_mtd:
        enabled: true
        tags:
          - staging
EOF

# 3. Deploy to production
limacharlie -o prod-org infra push -f base-config.yaml
limacharlie -o prod-org infra push -f prod-org-overrides.yaml

# 4. Deploy to staging
limacharlie -o staging-org infra push -f base-config.yaml
limacharlie -o staging-org infra push -f staging-org-overrides.yaml

# 5. Verify deployment
limacharlie -o prod-org hive get secret --key environment-marker
limacharlie -o staging-org hive get secret --key environment-marker
```

### Example 3: Threat Intelligence Pipeline

Complete end-to-end threat intelligence pipeline:

```yaml
version: 3

hives:
  # Step 1: Store API credentials
  secret:
    virustotal-api-key:
      data:
        secret: "vt-api-key-here"
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - api-keys

    otx-api-key:
      data:
        secret: "otx-api-key-here"
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - api-keys

    custom-feed-bearer-token:
      data:
        secret: "bearer-token-here"
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - api-keys

  # Step 2: Configure automated lookup sync
  extension_config:
    ext-lookup-manager:
      data:
        lookup_manager_rules:
          # Public threat feeds
          - name: tor-exit-nodes
            format: json
            predefined: '[https,storage.googleapis.com/lc-lookups-bucket/tor-ips.json]'
            tags:
              - tor
              - threat-intel

          # Custom threat feed with auth
          - name: malware-domains
            format: json
            arl: '[https,api.threatfeed.com/domains,bearer,hive://secret/custom-feed-bearer-token]'
            tags:
              - threat-intel
              - domains

          # Hash-based indicators
          - name: malware-hashes
            format: json
            arl: '[https,api.threatfeed.com/hashes,bearer,hive://secret/custom-feed-bearer-token]'
            tags:
              - threat-intel
              - hashes
      usr_mtd:
        enabled: true

  # Step 3: Create detection rules using lookups
  dr-general:
    # Domain-based detection
    malicious-domain-detection:
      data:
        detect:
          event: DNS_REQUEST
          op: lookup
          path: event/DOMAIN_NAME
          resource: hive://lookup/malware-domains
          case sensitive: false
        respond:
          - action: report
            name: "DNS request to known malicious domain"
            priority: 4
          - action: add tag
            tag: malware-domain
            ttl: 3600
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - dns

    # Hash-based detection
    malicious-hash-detection:
      data:
        detect:
          event: CODE_IDENTITY
          op: lookup
          path: event/HASH
          resource: hive://lookup/malware-hashes
        respond:
          - action: report
            name: "Known malicious file hash detected"
            priority: 5
          - action: task
            command: deny_tree
          - action: add tag
            tag: malware-hash
            ttl: 86400
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - file-hash
          - auto-response

    # Tor detection
    tor-connection-detection:
      data:
        detect:
          event: NETWORK_CONNECTIONS
          op: and
          rules:
            - op: lookup
              path: event/IP_ADDRESS
              resource: hive://lookup/tor-exit-nodes
            - op: is
              path: event/STATE
              value: ESTABLISHED
        respond:
          - action: report
            name: "Connection to Tor exit node"
            priority: 3
          - action: add tag
            tag: tor-connection
            ttl: 7200
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - tor
          - anonymization

  # Step 4: YARA rules for additional detection
  yara:
    threat-intel-yara:
      data:
        rule: |
          rule MalwareIndicators {
            meta:
              description = "Common malware indicators"
              author = "Threat Intel Team"
            strings:
              $a = "malicious_string"
              $b = { 6A 40 68 00 30 00 00 }
            condition:
              $a or $b
          }
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - malware

  # Step 5: Automated YARA scanning on suspicious files
  dr-general:
    yara-scan-downloads:
      data:
        detect:
          event: NEW_DOCUMENT
          op: contains
          path: event/FILE_PATH
          value: Downloads
          case sensitive: false
        respond:
          - action: task
            command: yara_scan hive://yara/threat-intel-yara --file-path "{{ .event.FILE_PATH }}"
            investigation: threat-intel-scan
            suppression:
              max_count: 1
              period: 300
              is_global: false
              keys:
                - '{{ .event.FILE_PATH }}'
      usr_mtd:
        enabled: true
        tags:
          - threat-intel
          - yara
          - file-scanning
```

### Example 4: Version Control Workflow

```bash
# Initialize Git repository for IaC
mkdir limacharlie-config
cd limacharlie-config
git init

# Fetch current configuration
limacharlie infra fetch > config.yaml
git add config.yaml
git commit -m "Initial configuration snapshot"

# Create feature branch for new detection rules
git checkout -b feature/add-ransomware-detection

# Edit configuration to add new rules
cat <<EOF >> config.yaml
  dr-general:
    ransomware-detection:
      data:
        detect:
          event: NEW_DOCUMENT
          op: contains
          path: event/FILE_PATH
          value: .locked
        respond:
          - action: report
            name: "Possible ransomware activity"
            priority: 5
      usr_mtd:
        enabled: true
        tags:
          - ransomware
EOF

# Test with dry-run
limacharlie infra push -f config.yaml --dry-run

# Commit changes
git add config.yaml
git commit -m "Add ransomware detection rule"

# Merge to main and deploy
git checkout main
git merge feature/add-ransomware-detection

# Deploy to production
limacharlie -o production infra push -f config.yaml

# Tag the release
git tag -a v1.1.0 -m "Release: Added ransomware detection"
git push origin v1.1.0
```

## Cloud Sensor Configuration

### Example 1: Webhook Sensor

```bash
# Create webhook sensor configuration
cat <<EOF > webhook-sensor.json
{
  "sensor_type": "webhook",
  "webhook": {
    "client_options": {
      "hostname": "security-webhook",
      "identity": {
        "installation_key": "your-installation-key",
        "oid": "your-org-id"
      },
      "platform": "json",
      "sensor_seed_key": "webhook-seed-key"
    },
    "secret": "webhook-secret-token"
  }
}
EOF

# Store in hive
limacharlie hive set cloudsensor --key security-webhook --data webhook-sensor.json

# Get the webhook URL (from web UI or API)
# Use the webhook to ingest security events from external sources
```

### Example 2: Multiple Webhook Sensors via IaC

```yaml
hives:
  cloudsensor:
    firewall-webhook:
      data:
        sensor_type: webhook
        webhook:
          client_options:
            hostname: firewall-events
            platform: syslog
            sensor_seed_key: firewall-seed
      usr_mtd:
        enabled: true
        tags:
          - firewall
          - network

    waf-webhook:
      data:
        sensor_type: webhook
        webhook:
          client_options:
            hostname: waf-events
            platform: json
            sensor_seed_key: waf-seed
      usr_mtd:
        enabled: true
        tags:
          - waf
          - web-security

    custom-app-webhook:
      data:
        sensor_type: webhook
        webhook:
          client_options:
            hostname: app-events
            platform: json
            sensor_seed_key: app-seed
      usr_mtd:
        enabled: true
        tags:
          - application
          - custom
```
