# Infrastructure as Code - Complete Examples

This document provides complete, production-ready examples of LimaCharlie Infrastructure as Code configurations for various use cases.

## Table of Contents

- [Example 1: Basic EDR Setup](#example-1-basic-edr-setup)
- [Example 2: Cloud Security Monitoring](#example-2-cloud-security-monitoring)
- [Example 3: MSSP Multi-Organization Configuration](#example-3-mssp-multi-organization-configuration)
- [Example 4: Complete Enterprise Setup](#example-4-complete-enterprise-setup)

## Example 1: Basic EDR Setup

A complete configuration for a basic endpoint detection and response setup with Windows and Linux endpoints.

### Complete Configuration

```yaml
version: 3

# Installation Keys
installation_keys:
  - description: windows-workstations
    tags:
      - windows
      - workstation
      - production
  - description: windows-servers
    tags:
      - windows
      - server
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
      - production

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
        - op: ends with
          path: event/FILE_PATH
          value: procdump.exe
          case sensitive: false
    respond:
      - action: report
        name: Credential Dumping Tool Detected
        priority: 5
        metadata:
          attack: T1003
          category: credential-access
      - action: task
        command: deny_tree <<routing/this>>
      - action: isolate network
      - action: task
        command: history_dump
        investigation: credential-dumping

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
            - op: contains
              path: event/COMMAND_LINE
              value: downloadstring
              case sensitive: false
    respond:
      - action: report
        name: Encoded PowerShell Command
        priority: 3
        metadata:
          attack: T1059.001
          category: execution
      - action: task
        command: history_dump
        investigation: encoded-powershell

  - name: lateral-movement-psexec
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
        metadata:
          attack: T1021.002
          category: lateral-movement
      - action: task
        command: history_dump
        investigation: lateral-movement

  - name: ransomware-file-encryption
    detect:
      event: NEW_DOCUMENT
      op: and
      rules:
        - op: matches
          path: event/FILE_PATH
          re: \.(encrypted|locked|crypto|crypt|wcry|wncry)$
          case sensitive: false
        - op: is greater than
          path: event/FILE_PATH
          value: 100
          length of: true
    respond:
      - action: report
        name: Potential Ransomware File Encryption
        priority: 5
        metadata:
          attack: T1486
          category: impact
      - action: task
        command: history_dump
        investigation: ransomware
      - action: isolate network

  - name: suspicious-linux-shells
    detect:
      event: NEW_PROCESS
      op: and
      rules:
        - op: or
          rules:
            - op: ends with
              path: event/FILE_PATH
              value: /bash
            - op: ends with
              path: event/FILE_PATH
              value: /sh
        - op: contains
          path: event/COMMAND_LINE
          value: -i
    respond:
      - action: report
        name: Suspicious Interactive Shell
        priority: 3
        metadata:
          attack: T1059.004
          category: execution

# False Positive Rules
fp:
  - name: whitelist-system-powershell
    op: is
    path: detect/event/FILE_PATH
    value: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

  - name: whitelist-admin-automation
    op: is
    path: detect/event/USER_NAME
    value: admin-automation

  - name: whitelist-backup-software
    op: contains
    path: detect/event/FILE_PATH
    value: Veeam

# Outputs
outputs:
  - name: slack-alerts
    module: slack
    for: detection
    slack_api_token: hive://secret/slack-token
    slack_channel: "#security-alerts"
    filters:
      min_priority: 3

  - name: siem-integration
    module: syslog
    for: event
    dest_host: siem.company.com
    dest_port: 514
    filters:
      tags:
        - production

  - name: s3-detection-backup
    module: s3
    for: detect
    bucket: security-detections
    key_id: hive://secret/aws-key-id
    secret_key: hive://secret/aws-secret-key
    sec_per_file: 3600
    dir: detections/

# Extensions
extensions:
  - ext-infrastructure
  - ext-git-sync
  - binlib
  - ext-yara

# Organization Values
org_values:
  - name: environment
    value: production
  - name: alert_email
    value: security@company.com

# Hive: YARA Rules
hive:
  yara:
    - name: malware-signatures
      enabled: true
      data: |
        rule ransomware_wannacry {
          meta:
            author = "Security Team"
            description = "Detects WannaCry ransomware"
          strings:
            $s1 = "WNcry@2ol7" ascii
            $s2 = ".WNCRYT" ascii
            $s3 = "tasksche.exe" ascii
          condition:
            any of them
        }

        rule credential_dumper_mimikatz {
          meta:
            author = "Security Team"
            description = "Detects Mimikatz credential dumper"
          strings:
            $s1 = "sekurlsa::logonpasswords" ascii
            $s2 = "privilege::debug" ascii
            $s3 = "Benjamin DELPY" ascii
          condition:
            any of them
        }

  # Secrets
  secret:
    - name: slack-token
      enabled: true
      data: "xoxb-your-slack-token"
    - name: aws-key-id
      enabled: true
      data: "YOUR_AWS_ACCESS_KEY_ID"
    - name: aws-secret-key
      enabled: true
      data: "YOUR_AWS_SECRET_ACCESS_KEY"
```

### Usage

```bash
# Test configuration
limacharlie configs push --config edr-setup.yaml --dry-run --all

# Deploy to organization
limacharlie configs push --oid YOUR_OID --config edr-setup.yaml --all
```

## Example 2: Cloud Security Monitoring

A complete configuration for monitoring cloud services including AWS, Okta, and Microsoft 365.

### Complete Configuration

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
            metadata:
              category: initial-access
              severity: critical

    - name: aws-security-group-changes
      enabled: true
      data:
        detect:
          event: AWS_EVENT
          op: is platform
          name: aws
          with child:
            op: or
            rules:
              - op: is
                path: event/eventName
                value: AuthorizeSecurityGroupIngress
              - op: is
                path: event/eventName
                value: RevokeSecurityGroupIngress
              - op: is
                path: event/eventName
                value: AuthorizeSecurityGroupEgress
              - op: is
                path: event/eventName
                value: RevokeSecurityGroupEgress
        respond:
          - action: report
            name: AWS Security Group Modified
            priority: 3
            metadata:
              category: defense-evasion

    - name: aws-iam-policy-changes
      enabled: true
      data:
        detect:
          event: AWS_EVENT
          op: is platform
          name: aws
          with child:
            op: or
            rules:
              - op: contains
                path: event/eventName
                value: PutUserPolicy
              - op: contains
                path: event/eventName
                value: PutRolePolicy
              - op: contains
                path: event/eventName
                value: PutGroupPolicy
        respond:
          - action: report
            name: AWS IAM Policy Changed
            priority: 4
            metadata:
              category: privilege-escalation

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
            metadata:
              category: credential-access
              attack: T1110

    - name: okta-user-account-locked
      enabled: true
      data:
        detect:
          event: user.account.lock
          op: is platform
          name: json
        respond:
          - action: report
            name: Okta User Account Locked
            priority: 3
            metadata:
              category: impact

    - name: okta-mfa-deactivated
      enabled: true
      data:
        detect:
          event: user.mfa.factor.deactivate
          op: is platform
          name: json
        respond:
          - action: report
            name: Okta MFA Factor Deactivated
            priority: 5
            metadata:
              category: defense-evasion
              severity: critical

    - name: o365-suspicious-inbox-rule
      enabled: true
      data:
        detect:
          event: OFFICE365_EVENT
          op: is platform
          name: office365
          with child:
            op: and
            rules:
              - op: is
                path: event/Operation
                value: New-InboxRule
              - op: or
                rules:
                  - op: contains
                    path: event/Parameters/ForwardTo
                    value: "@"
                  - op: contains
                    path: event/Parameters/DeleteMessage
                    value: "true"
        respond:
          - action: report
            name: Suspicious Office 365 Inbox Rule Created
            priority: 5
            metadata:
              category: collection
              attack: T1114

    - name: o365-mass-file-download
      enabled: true
      data:
        detect:
          event: FileDownloaded
          op: is platform
          name: office365
          with events:
            event: FileDownloaded
            op: exists
            path: event/UserId
            count: 50
            within: 300
        respond:
          - action: report
            name: Office 365 Mass File Download
            priority: 4
            metadata:
              category: exfiltration

    - name: gcp-project-iam-changes
      enabled: true
      data:
        detect:
          event: GCP_EVENT
          op: is platform
          name: gcp
          with child:
            op: contains
            path: event/protoPayload/methodName
            value: setIamPolicy
        respond:
          - action: report
            name: GCP Project IAM Policy Changed
            priority: 4
            metadata:
              category: privilege-escalation

  # Secrets for cloud integrations
  secret:
    - name: aws-access-key
      enabled: true
      data: "YOUR_AWS_ACCESS_KEY"
    - name: aws-secret-key
      enabled: true
      data: "YOUR_AWS_SECRET_KEY"
    - name: okta-api-key
      enabled: true
      data: "YOUR_OKTA_API_KEY"
    - name: o365-tenant-id
      enabled: true
      data: "YOUR_O365_TENANT_ID"
    - name: o365-client-id
      enabled: true
      data: "YOUR_O365_CLIENT_ID"
    - name: o365-client-secret
      enabled: true
      data: "YOUR_O365_CLIENT_SECRET"
    - name: gcp-credentials
      enabled: true
      data: "YOUR_GCP_CREDENTIALS_JSON"

# Outputs for cloud events
outputs:
  - name: cloud-alerts-to-slack
    module: slack
    for: detection
    slack_api_token: hive://secret/slack-token
    slack_channel: "#cloud-security"
    filters:
      min_priority: 3

  - name: cloud-events-to-siem
    module: syslog
    for: event
    dest_host: siem.company.com
    dest_port: 514
    filters:
      platforms:
        - aws
        - json
        - office365
        - gcp

  - name: high-priority-email
    module: email
    for: detection
    smtp_server: smtp.company.com
    smtp_port: 587
    smtp_from: security@company.com
    smtp_to: soc@company.com
    smtp_username: hive://secret/smtp-username
    smtp_password: hive://secret/smtp-password
    filters:
      min_priority: 5

# Extensions
extensions:
  - ext-infrastructure
  - ext-git-sync

# Organization Values
org_values:
  - name: environment
    value: production
  - name: cloud_monitoring_enabled
    value: "true"
```

### Usage

```bash
# Deploy cloud monitoring configuration
limacharlie configs push --oid YOUR_OID --config cloud-monitoring.yaml --all

# Update only cloud sensors
limacharlie configs push --oid YOUR_OID --config cloud-monitoring.yaml --sync-artifacts
```

## Example 3: MSSP Multi-Organization Configuration

A complete MSSP setup with shared global rules and customer-specific configurations.

### Repository Structure

```
.
├── global/
│   ├── detections/
│   │   ├── ransomware.yaml
│   │   ├── lateral-movement.yaml
│   │   ├── malware.yaml
│   │   └── data-exfil.yaml
│   ├── fp/
│   │   └── common-fp.yaml
│   └── yara/
│       └── signatures.yaml
└── orgs/
    ├── customer-a/
    │   ├── index.yaml
    │   ├── outputs.yaml
    │   └── installation-keys.yaml
    ├── customer-b/
    │   ├── index.yaml
    │   ├── outputs.yaml
    │   └── installation-keys.yaml
    └── customer-c/
        ├── index.yaml
        ├── outputs.yaml
        └── installation-keys.yaml
```

### Global Configurations

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
        metadata:
          attack: T1486
          category: impact
          managed_by: mssp
      - action: task
        command: history_dump
        investigation: ransomware
      - action: isolate network

  - name: ransomware-note-creation
    detect:
      event: NEW_DOCUMENT
      op: or
      rules:
        - op: matches
          path: event/FILE_PATH
          re: READ_?ME\.(txt|html)$
          case sensitive: false
        - op: matches
          path: event/FILE_PATH
          re: DECRYPT.*\.(txt|html)$
          case sensitive: false
        - op: contains
          path: event/FILE_PATH
          value: HOW_TO_DECRYPT
          case sensitive: false
    respond:
      - action: report
        name: Ransomware Note Created
        priority: 5
        metadata:
          attack: T1486
          category: impact
          managed_by: mssp
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
        metadata:
          attack: T1021.002
          category: lateral-movement
          managed_by: mssp

  - name: wmi-lateral-movement
    detect:
      event: WMI_PROCESS_CREATE
      op: exists
      path: event/COMMAND_LINE
    respond:
      - action: report
        name: WMI Process Creation (Potential Lateral Movement)
        priority: 3
        metadata:
          attack: T1047
          category: lateral-movement
          managed_by: mssp

  - name: rdp-bruteforce
    detect:
      event: FAILED_LOGIN
      op: exists
      path: event/USER_NAME
      with events:
        event: FAILED_LOGIN
        op: exists
        path: event/USER_NAME
        count: 10
        within: 300
    respond:
      - action: report
        name: RDP Brute Force Attempt
        priority: 4
        metadata:
          attack: T1110
          category: credential-access
          managed_by: mssp
```

**global/detections/malware.yaml**:
```yaml
version: 3
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
        - op: ends with
          path: event/FILE_PATH
          value: procdump.exe
          case sensitive: false
    respond:
      - action: report
        name: Credential Dumping Tool Detected
        priority: 5
        metadata:
          attack: T1003
          category: credential-access
          managed_by: mssp
      - action: task
        command: deny_tree <<routing/this>>
      - action: isolate network
```

**global/fp/common-fp.yaml**:
```yaml
version: 3
fp:
  - name: whitelist-windows-defender
    op: contains
    path: detect/event/FILE_PATH
    value: Windows Defender

  - name: whitelist-system-processes
    op: or
    rules:
      - op: is
        path: detect/event/FILE_PATH
        value: C:\Windows\System32\svchost.exe
      - op: is
        path: detect/event/FILE_PATH
        value: C:\Windows\System32\services.exe
```

**global/yara/signatures.yaml**:
```yaml
version: 3
hive:
  yara:
    - name: mssp-malware-signatures
      enabled: true
      data: |
        rule ransomware_wannacry {
          meta:
            author = "MSSP Security Team"
            description = "Detects WannaCry ransomware"
          strings:
            $s1 = "WNcry@2ol7" ascii
            $s2 = ".WNCRYT" ascii
          condition:
            any of them
        }

        rule credential_dumper_mimikatz {
          meta:
            author = "MSSP Security Team"
            description = "Detects Mimikatz"
          strings:
            $s1 = "sekurlsa::logonpasswords" ascii
            $s2 = "privilege::debug" ascii
          condition:
            any of them
        }
```

### Customer-Specific Configurations

**orgs/customer-a/index.yaml**:
```yaml
version: 3
include:
  # Global shared rules
  - ../../global/detections/ransomware.yaml
  - ../../global/detections/lateral-movement.yaml
  - ../../global/detections/malware.yaml
  - ../../global/fp/common-fp.yaml
  - ../../global/yara/signatures.yaml

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

  - name: customer-a-alerts
    module: slack
    for: detection
    slack_api_token: hive://secret/customer-a-slack-token
    slack_channel: "#security"
    filters:
      min_priority: 3

  - name: mssp-dashboard
    module: webhook
    for: detection
    dest_host: https://mssp.company.com/api/webhooks/customer-a
    secret_key: hive://secret/mssp-webhook-secret
```

**orgs/customer-a/installation-keys.yaml**:
```yaml
version: 3
installation_keys:
  - description: customer-a-windows
    tags:
      - customer-a
      - windows
      - production
  - description: customer-a-linux
    tags:
      - customer-a
      - linux
      - production
```

**orgs/customer-b/index.yaml**:
```yaml
version: 3
include:
  # Global shared rules (same as customer-a)
  - ../../global/detections/ransomware.yaml
  - ../../global/detections/lateral-movement.yaml
  - ../../global/detections/malware.yaml
  - ../../global/fp/common-fp.yaml
  - ../../global/yara/signatures.yaml

  # Customer-specific
  - outputs.yaml
  - installation-keys.yaml
  - custom-rules.yaml  # Customer-B specific rules
```

**orgs/customer-b/outputs.yaml**:
```yaml
version: 3
outputs:
  - name: customer-b-email
    module: email
    for: detection
    smtp_server: smtp.customer-b.com
    smtp_port: 587
    smtp_from: security@customer-b.com
    smtp_to: soc@customer-b.com
    smtp_username: hive://secret/customer-b-smtp-user
    smtp_password: hive://secret/customer-b-smtp-pass
    filters:
      min_priority: 4

  - name: mssp-dashboard
    module: webhook
    for: detection
    dest_host: https://mssp.company.com/api/webhooks/customer-b
    secret_key: hive://secret/mssp-webhook-secret
```

**orgs/customer-b/custom-rules.yaml**:
```yaml
version: 3
rules:
  - name: customer-b-custom-app-monitoring
    detect:
      event: NEW_PROCESS
      op: contains
      path: event/FILE_PATH
      value: CustomerApp.exe
    respond:
      - action: report
        name: Customer B Custom App Started
        priority: 2
        metadata:
          customer: customer-b
          custom_rule: true
```

### Deployment Scripts

**deploy-all-customers.sh**:
```bash
#!/bin/bash
# Deploy configurations to all customer organizations

CUSTOMERS=(
  "customer-a:org-id-a"
  "customer-b:org-id-b"
  "customer-c:org-id-c"
)

for customer in "${CUSTOMERS[@]}"; do
  IFS=':' read -r name oid <<< "$customer"

  echo "Deploying configuration for $name (OID: $oid)..."

  # Dry run first
  limacharlie configs push \
    --oid "$oid" \
    --config "orgs/$name/index.yaml" \
    --dry-run \
    --all

  # If dry run looks good, deploy
  read -p "Deploy to $name? (y/n) " confirm
  if [ "$confirm" = "y" ]; then
    limacharlie configs push \
      --oid "$oid" \
      --config "orgs/$name/index.yaml" \
      --all
    echo "Deployed to $name successfully"
  fi
done
```

**update-global-rule.sh**:
```bash
#!/bin/bash
# Update a global rule and deploy to all customers

RULE_FILE=$1

if [ -z "$RULE_FILE" ]; then
  echo "Usage: $0 <rule-file>"
  exit 1
fi

# Commit changes
git add "$RULE_FILE"
git commit -m "Update global rule: $RULE_FILE"
git push

echo "Updated $RULE_FILE in Git"
echo "Git Sync will automatically deploy to all customer organizations"
echo "Or manually trigger sync via Git Sync extension UI"
```

## Example 4: Complete Enterprise Setup

A comprehensive enterprise configuration with all components.

### Complete Configuration

```yaml
version: 3

# Installation Keys
installation_keys:
  - description: windows-workstations
    tags:
      - windows
      - workstation
      - production
  - description: windows-servers
    tags:
      - windows
      - server
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
      - production
  - description: dev-environment
    tags:
      - development
      - all-platforms

# Detection Rules
rules:
  - name: malware-execution
    detect:
      event: NEW_PROCESS
      op: or
      rules:
        - op: ends with
          path: event/FILE_PATH
          value: mimikatz.exe
          case sensitive: false
        - op: ends with
          path: event/FILE_PATH
          value: procdump.exe
          case sensitive: false
        - op: contains
          path: event/COMMAND_LINE
          value: sekurlsa
          case sensitive: false
    respond:
      - action: report
        name: Malicious Tool Execution
        priority: 5
      - action: task
        command: deny_tree <<routing/this>>
      - action: isolate network

# False Positive Rules
fp:
  - name: whitelist-approved-tools
    op: contains
    path: detect/event/FILE_PATH
    value: C:\ApprovedTools\

# Outputs
outputs:
  - name: primary-siem
    module: syslog
    for: event
    dest_host: siem.enterprise.com
    dest_port: 514
    is_tls: true

  - name: slack-critical-alerts
    module: slack
    for: detection
    slack_api_token: hive://secret/slack-token
    slack_channel: "#security-critical"
    filters:
      min_priority: 4

  - name: email-high-priority
    module: email
    for: detection
    smtp_server: smtp.enterprise.com
    smtp_port: 587
    smtp_from: security@enterprise.com
    smtp_to: soc@enterprise.com
    smtp_username: hive://secret/smtp-user
    smtp_password: hive://secret/smtp-pass
    filters:
      min_priority: 5

  - name: s3-archive
    module: s3
    for: event
    bucket: security-logs-archive
    key_id: hive://secret/aws-key-id
    secret_key: hive://secret/aws-secret-key
    sec_per_file: 3600

# Extensions
extensions:
  - ext-infrastructure
  - ext-git-sync
  - binlib
  - ext-yara
  - ext-artifact-collection
  - ext-responder

# Organization Values
org_values:
  - name: environment
    value: production
  - name: company_name
    value: Enterprise Corp
  - name: compliance_framework
    value: NIST

# Resources
resources:
  api_keys:
    - name: automation-api-key
      permissions:
        - dr.list
        - dr.set
        - sensor.list
        - sensor.task
    - name: readonly-api-key
      permissions:
        - dr.list
        - sensor.list

# Hive Configurations
hive:
  dr-general:
    - name: advanced-threat-detection
      enabled: true
      data:
        detect:
          event: NEW_PROCESS
          op: and
          rules:
            - op: contains
              path: event/COMMAND_LINE
              value: powershell
            - op: contains
              path: event/COMMAND_LINE
              value: -encodedcommand
        respond:
          - action: report
            name: Advanced Threat Detected
            priority: 4

  yara:
    - name: enterprise-signatures
      enabled: true
      data: |
        rule enterprise_malware {
          meta:
            author = "Enterprise Security"
          strings:
            $s1 = "malicious_string"
          condition:
            $s1
        }

  secret:
    - name: slack-token
      enabled: true
      data: "xoxb-token"
    - name: aws-key-id
      enabled: true
      data: "AKIAXXXXX"
    - name: aws-secret-key
      enabled: true
      data: "secret"
    - name: smtp-user
      enabled: true
      data: "security@enterprise.com"
    - name: smtp-pass
      enabled: true
      data: "password"

# Integrity Monitoring
integrity:
  - name: monitor-critical-files
    patterns:
      - C:\Windows\System32\*.exe
      - /etc/passwd
      - /etc/shadow
    platforms:
      - windows
      - linux
    tags:
      - critical

# Exfiltration Detection
exfil:
  - name: sensitive-data-movement
    event: NEW_DOCUMENT
    op: starts with
    path: event/FILE_PATH
    value: C:\Sensitive\
    tags:
      - sensitive
```

### Usage

```bash
# Deploy complete enterprise configuration
limacharlie configs push --oid YOUR_OID --config enterprise-setup.yaml --all
```
