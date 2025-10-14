I'll synthesize these related documentation pages into cohesive, self-contained topics. Let me validate the content first - I can see these documents are all about LimaCharlie's configuration and API features, covering multiple distinct topics that should be organized logically.

---

# Config Hive: Secrets

Secrets are encrypted key-value pairs that can be used in Detection & Response rules and other LimaCharlie components. They provide a secure way to store sensitive information like API keys, passwords, and tokens.

## Overview

Secrets are stored encrypted at rest and are only decrypted when needed during rule execution. This ensures sensitive data is never exposed in logs or rule definitions.

## Managing Secrets

### Creating Secrets

Secrets can be created through the web interface, API, or SDK:

**Web Interface:**
1. Navigate to **Config Hive** → **Secrets**
2. Click **Add Secret**
3. Provide a name and value
4. Save the secret

**SDK/CLI:**
```bash
# Create a secret
limacharlie secret set my-secret "secret-value"

# List secrets (values are not displayed)
limacharlie secret list

# Delete a secret
limacharlie secret del my-secret
```

### Using Secrets in Rules

Reference secrets in Detection & Response rules and other configurations using the following syntax:

```
{{ secret://secret-name }}
```

Or alternatively:
```
{{ secret.SECRET_NAME }}
```

**Example:**

```yaml
- action: report
  metadata:
    api_key: "{{ secret://my-api-key }}"
```

**Example with Webhook:**
```yaml
- action: webhook
  url: "{{ secret.SLACK_WEBHOOK }}"
```

**Example with Cloud Sensors:**
```json
{
  "platform": "azure",
  "tenant_id": "...",
  "client_id": "...",
  "client_secret": "{{ secret://azure-secret }}",
  "log_sources": ["activity", "nsg_flow"]
}
```

## Best Practices

1. **Unique Names**: Use descriptive, unique names for secrets
2. **Rotation**: Regularly rotate sensitive secrets
3. **Least Privilege**: Only grant access to secrets that are needed
4. **Audit**: Monitor secret usage through audit logs
5. **Never Commit**: Never commit secrets to version control
6. **RBAC Controls**: Limit access using role-based access controls

## Security Considerations

- Secrets are encrypted at rest using industry-standard encryption
- Secret values are never logged or displayed after creation
- Secrets are only shown once during creation - store them securely
- Access to secrets is controlled by organization permissions
- Secret usage is audited and can be tracked
- Secrets are resolved at runtime and never exposed in logs or rule outputs

---

# Config Hive: Lookups

Lookups are reference tables that can be queried during rule execution. They allow you to maintain lists of indicators, configurations, or other data that can be checked dynamically.

## Overview

Lookups provide a way to:
- Store lists of known indicators (IPs, domains, hashes)
- Maintain configuration values
- Create dynamic reference tables
- Perform real-time lookups during detection

Lookups are key-value stores that enable you to maintain lists of indicators, configuration data, or reference information that can be queried during detection and response operations.

## Types of Lookups

### Static Lookups

Static lookups are key-value pairs stored directly in LimaCharlie:

```yaml
key: value
ip-address: 192.168.1.1
domain: example.com
```

### Dynamic Lookups

Dynamic lookups query external sources in real-time (requires API integration).

## Common Use Cases

- IP allowlists/denylists
- Known good/bad hashes
- User account mappings
- Custom threat intelligence feeds
- Configuration parameters
- Threat Intelligence: Maintain lists of malicious indicators
- Allow Lists: Track known-good entities
- Enrichment: Add context to events

## Managing Lookups

### Creating Lookups

Lookups can be created and managed through:

**Web Interface:**
1. Navigate to **Config Hive** → **Lookups**
2. Click **Add Lookup**
3. Provide a name and add key-value pairs
4. Save the lookup table

**API/CLI:**
```bash
# Create a lookup
limacharlie lookup set threat-ips 192.168.1.1 malicious

# Query a lookup
limacharlie lookup get threat-ips 192.168.1.1

# Delete a lookup entry
limacharlie lookup del threat-ips 192.168.1.1
```

### Using Lookups in Rules

Reference lookups in Detection & Response rules using the `lookup` operator:

```yaml
event: NETWORK_CONNECTIONS
op: lookup
path: lookup://threat-ips
key: "{{ .event.IP_ADDRESS }}"
action: report
metadata:
  detection: "Connection to blocked IP"
```

**Alternative syntax:**
```yaml
op: lookup
path: event/IP_ADDRESS
resource: 'lcr://lookup/LOOKUP_NAME'
```

**Example Rule:**

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: lookup://blocked-ips
  key: "{{ .event.DESTINATION.IP_ADDRESS }}"
respond:
  - action: report
    metadata:
      detection: "Connection to blocked IP"
  - action: isolate
```

## Lookup Operations

- **Add/Update**: Insert or modify entries
- **Delete**: Remove entries
- **Bulk Import**: Upload CSV or JSON data
- **TTL**: Set expiration times for entries

## Best Practices

- Keep lookup tables focused and organized
- Regularly update lookup data
- Use descriptive names and keys
- Monitor lookup performance for large tables
- Use minimum required data to optimize performance

---

# API Keys

API keys provide programmatic access to the LimaCharlie platform. They enable automation, integration, and custom tooling.

## Overview

API keys authenticate requests to the LimaCharlie API and can be scoped with specific permissions. They enable automation, integration with external tools, and SDK/CLI usage.

## Creating API Keys

**Web Interface:**
1. Navigate to **Access** → **API Keys** (or **Organization Settings** → **API Keys**)
2. Click **Create API Key**
3. Provide a name and description
4. Select permissions (scopes)
5. Set expiration date (optional)
6. Save and securely store the key

**Important**: API keys are only displayed once during creation. Store them securely.

## API Key Types

- **User Keys**: Associated with a specific user account
- **Service Keys**: For automated systems and integrations
- **Installation Keys**: For sensor deployment

## Permission Scopes

API keys can be granted various permission levels:

- **Read**: View organization data (read-only access)
- **Write**: Modify configurations (write access to specific resources)
- **Admin**: Full administrative access
- **Sensor**: Sensor-specific operations
- **Custom**: Granular permission selection (custom permission sets)

## Using API Keys

### Authentication

Include the API key in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.limacharlie.io/v1/...
```

### SDK Usage

```python
from limacharlie import Manager

manager = Manager(api_key="YOUR_API_KEY")
```

Or with organization ID:

```python
manager = Manager(api_key="YOUR_API_KEY", oid="YOUR_ORG_ID")
```

### CLI Authentication

```bash
# Set credentials
limacharlie login --api-key YOUR_API_KEY --oid YOUR_ORG_ID

# Or use environment variables
export LC_API_KEY=YOUR_API_KEY
export LC_OID=YOUR_ORG_ID
```

## Security Best Practices

1. **Least Privilege**: Grant minimum necessary permissions; use service keys for automation
2. **Rotation**: Regularly rotate API keys
3. **Storage**: Never commit keys to source control; store keys securely (environment variables, secrets managers)
4. **Monitoring**: Track API key usage and audit logs
5. **Revocation**: Immediately revoke compromised keys
6. **Expiration**: Set expiration dates on API keys

## API Key Management

### Listing Keys

View all API keys in your organization (values are masked).

### Revoking Keys

Immediately revoke compromised or unused keys.

### Auditing

Monitor API key usage through audit logs to detect unauthorized access.

---

# LimaCharlie SDK & CLI

The LimaCharlie SDK and CLI provide programmatic and command-line access to the platform for automation, integration, and advanced operations.

## Installation

**Python SDK:**
```bash
pip install limacharlie
```

**CLI:**
```bash
pip install limacharlie-cli
```

## SDK (Python)

### Basic Usage

```python
from limacharlie import Manager

# Initialize manager
manager = Manager(api_key="YOUR_API_KEY")

# With organization ID
manager = Manager(api_key="YOUR_API_KEY", oid="YOUR_ORG_ID")

# Get organization
org = manager.organization("your-org-id")

# List sensors
sensors = org.sensors()
for sensor in sensors:
    print(sensor.sid, sensor.hostname)

# Get specific sensor
sensor = manager.sensor("SENSOR_ID")

# Task sensor
sensor.task("history_dump_recent", {"hours": 24})
sensor.task("os_version")

# Create D&R rule
rule = {
    "name": "example-rule",
    "detect": {...},
    "respond": [...]
}
org.dr_rule_create(rule)
```

### Common Operations

```python
# Sensor management
sensor = org.sensor("sensor-id")
sensor.task("os_version")

# Event queries
events = org.get_events(event_type="NETWORK_CONNECTIONS", limit=100)

# Outputs
outputs = org.outputs()

# Yara rules
manager.add_yara_rule("rule_name", yara_source)

# Annex operations
artifacts = manager.annexes()
artifact = manager.annex("ARTIFACT_ID")
data = artifact.download()
```

## CLI

### Configuration

```bash
# Configure credentials
limacharlie configure

# Or login with credentials
limacharlie login --api-key YOUR_API_KEY --oid YOUR_ORG_ID

# Or use environment variables
export LC_API_KEY=YOUR_API_KEY
export LC_OID=YOUR_ORG_ID
```

### Common Commands

**Sensor Management:**
```bash
# List sensors
limacharlie sensor list
limacharlie sensors list

# Get sensor info
limacharlie sensor info SENSOR_ID
limacharlie sensor get SENSOR_ID

# Task a sensor
limacharlie sensor task SENSOR_ID os_version
limacharlie sensor task SENSOR_ID history_dump_recent
```

**D&R Rules:**
```bash
# Manage D&R rules
limacharlie dr list
limacharlie dr add rule.yaml
limacharlie dr del rule-name
limacharlie dr push rules.yaml
limacharlie dr export rules.yaml
limacharlie dr import rules.yaml

# Deploy rules from directory
limacharlie dr push rules/ --org-name prod
```

**Secrets Management:**
```bash
limacharlie secret set my-secret "value"
limacharlie secret list
limacharlie secret del my-secret
```

**Lookup Management:**
```bash
limacharlie lookup set table-name key value
limacharlie lookup get table-name key
limacharlie lookup del table-name key
```

**Yara Rules:**
```bash
limacharlie hive yara add rule_name rule_file.yara
```

**Secure Annex:**
```bash
limacharlie annex list
limacharlie annex download ARTIFACT_ID
```

**Event Queries:**
```bash
limacharlie search "event_type:NEW_PROCESS" --days 1
```

### Configuration Management

```bash
# Export configuration
limacharlie hive export config.yaml

# Import configuration
limacharlie hive import config.yaml

# Sync configurations
limacharlie hive sync
```

## Advanced Features

- Batch sensor operations
- Event streaming
- Automated response workflows
- Integration with CI/CD pipelines
- Custom automation scripts
- Version control for D&R rules (store in Git and deploy via CI/CD)

## Documentation

- [Python SDK Documentation](https://github.com/refractionPOINT/python-limacharlie)
- [API Reference](https://doc.limacharlie.io/docs/api)
- Full SDK documentation: [https://doc.limacharlie.io](https://doc.limacharlie.io)

---

# Secure Annex

Secure Annex provides encrypted storage for sensitive files and data within LimaCharlie. It is LimaCharlie's encrypted cloud storage service for sensitive data and artifacts collected from endpoints.

## Overview

Secure Annex allows you to:
- Store sensitive files securely
- Store files, memory dumps, and forensic data
- Reference files in Detection & Response rules
- Manage encrypted artifacts
- Maintain compliance with data security requirements

## Features

- **Encryption**: All data encrypted at rest (end-to-end encryption)
- **Access Control**: Granular permissions (RBAC integration)
- **Versioning**: Track file changes
- **Integration**: Use in rules and automations
- **Audit Logging**: Complete access history
- **Retention Policies**: Automatic expiration

## Collecting Artifacts

### Task Sensors to Upload

Task sensors to upload artifacts to Secure Annex:

**In D&R Rules:**
```yaml
- action: artifact_get
  artifact: path/to/file
  upload_to_annex: true
```

**Via SDK:**
```python
sensor.task("artifact_get", {
    "artifact": "/path/to/file",
    "upload_to_annex": True
})
```

## Uploading Files

**Web Interface:**
1. Navigate to **Secure Annex**
2. Click **Upload File**
3. Select file and provide metadata
4. Save

**Via SDK:**
```python
# Upload file
org.annex_upload("file.txt", content)

# Download file
content = org.annex_download("file.txt")

# List files
files = org.annex_list()
```

## Retrieving Artifacts

**Via SDK:**
```python
# List artifacts
artifacts = manager.annexes()

# Download artifact
artifact = manager.annex("ARTIFACT_ID")
data = artifact.download()
```

**Via CLI:**
```bash
limacharlie annex list
limacharlie annex download ARTIFACT_ID
```

## Referencing in Rules

```yaml
- action: report
  file: annex://sensitive-config.json
```

## Retention Policies

Set automatic expiration:
- 24 hours
- 7 days
- 30 days
- 90 days
- Custom duration

## Use Cases

- Memory dump analysis
- Suspicious file collection
- Forensic investigations
- Malware sample collection
- Log file preservation

## Best Practices

1. **Encryption**: Store only sensitive data in Annex
2. **Access Control**: Limit access to necessary personnel
3. **Versioning**: Track changes for audit purposes
4. **Cleanup**: Remove obsolete files regularly

---

# Config Hive: Yara

YARA rules can be used in LimaCharlie for file and memory scanning to detect malware and suspicious patterns. Config Hive Yara enables you to deploy and manage Yara rules for file and memory scanning across your fleet.

## Overview

LimaCharlie supports YARA rules for:
- File scanning
- Memory scanning
- Process analysis
- Artifact detection

## Managing YARA Rules

### Adding YARA Rules

**Web Interface:**
1. Navigate to **Config Hive** → **YARA**
2. Click **Add Rule**
3. Paste your YARA rule
4. Apply to organization or specific tags
5. Save and enable

**Via SDK:**
```python
manager.add_yara_rule("rule_name", yara_source)
```

**Via CLI:**
```bash
limacharlie hive yara add rule_name rule_file.yara
```

### YARA Rule Format

```yara
rule ExampleRule {
    meta:
        description = "Example YARA rule"
        author = "Security Team"
    strings:
        $str1 = "malicious_string"
        $str2 = { 6D 61 6C 77 61 72 65 }
    condition:
        any of them
}
```

**Example with PowerShell Detection:**
```yara
rule SuspiciousPowerShell {
    meta:
        description = "Detects suspicious PowerShell patterns"
        author = "Security Team"
    
    strings:
        $s1 = "IEX" nocase
        $s2 = "DownloadString" nocase
        $s3 = "-EncodedCommand"
    
    condition:
        2 of them
}
```

## Using YARA in Rules

### File Scanning

**Manual Scan:**
```yaml
event: NEW_DOCUMENT
op: yara_scan
path: "{{ .event.FILE_PATH }}"
ruleset: custom-rules
action: report
```

**Via SDK:**
```python
sensor.task("yara_scan", {
    "file_path": "C:\\suspect.exe",
    "rules": ["rule_name"]
})
```

### Memory Scanning

**Manual Scan:**
```yaml
event: NEW_PROCESS
op: yara_scan_process
pid: "{{ .event.PROCESS_ID }}"
ruleset: memory-rules
action: isolate
```

**Via SDK:**
```python
sensor.task("yara_scan", {
    "pid": 1234,
    "rules": ["rule_name"]
})
```

## Automated Scanning

Trigger Yara scans automatically in D&R rules:

```yaml
detect:
  event: NEW_DOCUMENT
  op: ends with
  path: event/FILE_PATH
  value: .exe

respond:
  - action: task
    command: yara_scan
    investigation: true
    file_path: "{{ event.FILE_PATH }}"
```

## Integration with Detection

YARA results can trigger Detection & Response rules:

```yaml
event: YARA_DETECTION
target: artifact
op: is
value: suspicious-file
action: report
```

## Performance Considerations

- Use targeted rules to minimize CPU impact
- Limit concurrent scans
- Scan specific paths rather than entire filesystems
- Use rule namespaces for organization

## Best Practices

1. **Testing**: Test rules before deployment
2. **Performance**: Optimize rules to avoid performance impact
3. **Maintenance**: Regularly update rule sets
4. **Documentation**: Document rule purpose and logic

---

# Config Hive: Detection & Response Rules

Detection & Response (D&R) rules are the core of LimaCharlie's detection engine and automated threat detection and response capabilities. They define how to detect threats and respond automatically.

## Overview

D&R rules consist of:
- **Detect**: Conditions that trigger the rule (detection logic)
- **Respond**: Actions to take when triggered (response actions)

## Rule Structure

```yaml
name: example-rule
detect:
  # Detection logic
  event: EVENT_TYPE
  op: is
  path: event/FIELD
  value: TARGET_VALUE
respond:
  # Response actions
  - action: report
    name: rule_name
    metadata:
      detection: "Description of detection"
  - action: task
    command: deny_tree
```

**Detailed Example:**
```yaml
name: example-rule
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is
      path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
      value: 192.168.1.1
respond:
  - action: report
    metadata:
      detection: "Connection to suspicious IP"
  - action: isolate
```

## Detection Operators

- `is` / `is not`: Exact match
- `contains` / `not contains`: Substring match
- `starts with` / `ends with`: Prefix/suffix match
- `matches` / `not matches`: Regex match
- `exists`: Field presence check
- `greater than` / `less than`: Numeric comparison
- `lookup`: Query Config Hive lookup
- `and`: Logical AND of multiple rules
- `or`: Logical OR of multiple rules

## Common Event Types

- `NEW_PROCESS`: Process creation
- `NETWORK_CONNECTIONS`: Network activity
- `DNS_REQUEST`: DNS queries
- `FILE_CREATE` / `FILE_DELETE`: File operations
- `REGISTRY_CREATE` / `REGISTRY_DELETE`: Registry changes
- `NEW_DOCUMENT`: Document downloads
- `USER_OBSERVED`: User activity
- `YARA_DETECTION`: YARA rule matches
- `CLOUD_AWS`: AWS CloudTrail events

## Response Actions

- `report`: Create detection alert/Generate detection alert
- `task`: Execute sensor command/task
- `add tag`: Tag the sensor
- `remove tag`: Remove sensor tag
- `isolate`: Network isolate sensor
- `webhook`: Send to external system/Send webhook notification

## Example Rules

### Detect Suspicious Process

```yaml
name: suspicious-process
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: "powershell.exe"
    - op: contains
      path: event/COMMAND_LINE
      value: "downloadstring"
respond:
  - action: report
    metadata:
      detection: "Suspicious PowerShell execution"
```

**Detect Suspicious PowerShell (Alternative):**
```yaml
name: suspicious_powershell
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/COMMAND_LINE
      value: powershell
    - op: contains
      path: event/COMMAND_LINE
      value: "-EncodedCommand"
respond:
  - action: report
    name: suspicious_powershell
  - action: task
    command: deny_tree
```

### Detect Network Connection

```yaml
name: suspicious-connection
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: lookup://threat-ips
  key: "{{ .event.DESTINATION.IP_ADDRESS }}"
respond:
  - action: report
  - action: isolate
```

### Detect Lateral Movement

```yaml
name: lateral_movement_detected
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is
      path: event/FILE_PATH
      value: psexec.exe
    - op: is
      path: event/PARENT/FILE_PATH
      value: services.exe
respond:
  - action: report
    name: lateral_movement_detected
  - action: isolate
```

## Rule Management

### Import/Export

**Via CLI:**
```bash
limacharlie dr export rules.yaml
limacharlie dr import rules.yaml
```

**Via CLI:**
```bash
# List rules
limacharlie dr list

# Add rule
limacharlie dr add rule.yaml

# Delete rule
limacharlie dr del rule-name

# Push rules
limacharlie dr push rules.yaml
```

### Version Control

Store D&R rules in Git and deploy via CI/CD:
```bash
limacharlie dr push rules/ --org-name prod
```

## Testing Rules

Use the D&R rule tester in the web interface to validate rules against historical events before deployment.

## Best Practices

1. **Testing**: Test in report-only mode first; test rules before deployment
2. **Documentation**: Comment rule purpose
3. **Tuning**: Iterate to reduce false positives
4. **Performance**: Keep rules efficient
5. **Organization**: Use naming conventions

---

# Config Hive: Cloud Sensors

Cloud Sensors extend LimaCharlie's visibility to cloud environments and SaaS applications. They enable monitoring of cloud infrastructure and services including AWS, Azure, GCP, and other cloud platforms.

## Overview

Cloud Sensors provide:
- Cloud infrastructure monitoring (AWS, Azure, GCP)
- SaaS application logging (O365, GSuite)
- Cloud storage monitoring
- Identity and access management visibility

## Supported Platforms

### AWS
- CloudTrail logs
- VPC Flow Logs
- GuardDuty findings
- S3 access logs

### Azure
- Activity logs
- Network Security Group logs
- Security Center alerts

### GCP
- Cloud Audit logs
- VPC Flow Logs
- Security Command Center findings

### SaaS
- Office 365 (Audit logs)
- Google Workspace
- Okta (System logs)
- Other via API

## Configuration

### AWS Setup

**Web Interface:**
1. Navigate to **Config Hive** → **Cloud Sensors**
2. Select **AWS** (or **AWS CloudTrail**)
3. Provide IAM credentials or role ARN (assume role ARN)
4. Select log sources (Configure S3 bucket and SNS topic)
5. Apply to organization
6. Save configuration

**Configuration Example:**
```json
{
  "platform": "aws",
  "role_arn": "arn:aws:iam::123456789:role/LimaCharlie",
  "log_sources": ["cloudtrail", "vpc_flow"]
}
```

### Azure Setup

**Web Interface:**
1. Select Azure integration
2. Configure Azure AD application
3. Grant required permissions
4. Configure Event Hub connection

**Configuration Example:**
```json
{
  "platform": "azure",
  "tenant_id": "...",
  "client_id": "...",
  "client_secret": "{{ secret://azure-secret }}",
  "log_sources": ["activity", "nsg_flow"]
}
```

## Using Cloud Data in Rules

### AWS CloudTrail Events

```yaml
event: CLOUD_AWS
detect:
  op: is
  path: event/eventName
  value: "DeleteBucket"
respond:
  - action: report
    metadata:
      detection: "AWS S3 bucket deleted"
```

**Alternative - Console Login Failures:**
```yaml
detect:
  event: CLOUD_AWS
  op: and
  rules:
    - op: is
      path: event/eventName
      value: ConsoleLogin
    - op: is
      path: event/responseElements/ConsoleLogin
      value: Failure
respond:
  - action: report
    name: aws_console_login_failure
  - action: webhook
    url: "{{ secret.SLACK_WEBHOOK }}"
```

## Common Use Cases

- Unauthorized access attempts
- Configuration changes
- Resource creation/deletion
- Permission modifications
- API abuse detection
- Compliance monitoring

## Best Practices

1. **Least Privilege**: Use minimal required permissions; use dedicated IAM roles with minimal permissions
2. **Cost Management**: Monitor ingestion costs
3. **Filtering**: Ingest only necessary logs
4. **Integration**: Correlate cloud and endpoint events; integrate with SIEM for correlation
5. **Regional Coverage**: Enable CloudTrail/logging in all regions
6. **Alerting**: Configure alerts for critical events
7. **Review**: Regular review of cloud activity
8. **Automation**: Automated response to policy violations

## Security Considerations

- Use dedicated service accounts with minimal required permissions
- Monitor costs associated with log ingestion
- Filter logs to reduce noise and costs
- Correlate cloud events with endpoint telemetry for comprehensive visibility