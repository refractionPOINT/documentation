# API

## Config Hive: Secrets

Config Hive Secrets provide a secure way to store and manage sensitive information like API keys, passwords, and tokens within LimaCharlie. These secrets can be referenced in Detection & Response rules, integrations, and other configurations without exposing the actual values.

### Creating Secrets

Secrets are stored in the Config Hive and can be created through:
- The web interface under Config Hive > Secrets
- The LimaCharlie SDK/CLI
- Direct API calls

### Using Secrets

Reference secrets in your configurations using the syntax:
```
{{ secret.SECRET_NAME }}
```

Secrets are resolved at runtime and never exposed in logs or rule outputs.

### Best Practices

- Use descriptive names for secrets
- Rotate secrets regularly
- Limit access using RBAC controls
- Never commit secrets to version control

## Config Hive: Lookups

Lookups are key-value stores that enable you to maintain lists of indicators, configuration data, or reference information that can be queried during detection and response operations.

### Common Use Cases

- IP allowlists/denylists
- Known good/bad hashes
- User account mappings
- Custom threat intelligence feeds
- Configuration parameters

### Creating Lookups

Lookups can be created and managed through:
- Web interface: Config Hive > Lookups
- LimaCharlie SDK/CLI
- API endpoints

### Querying Lookups

Use lookups in D&R rules with the `lookup()` function:

```yaml
op: lookup
path: event/IP_ADDRESS
resource: 'lcr://lookup/LOOKUP_NAME'
```

### Lookup Operations

- **Add/Update**: Insert or modify entries
- **Delete**: Remove entries
- **Bulk Import**: Upload CSV or JSON data
- **TTL**: Set expiration times for entries

## API Keys

LimaCharlie uses API keys for programmatic access to the platform. API keys enable automation, integration with external tools, and SDK/CLI usage.

### Creating API Keys

1. Navigate to Organization Settings > API Keys
2. Click "Create API Key"
3. Set permissions and expiration
4. Save the key securely (shown only once)

### API Key Types

- **User Keys**: Associated with a specific user account
- **Service Keys**: For automated systems and integrations
- **Installation Keys**: For sensor deployment

### Permissions

API keys can be scoped with specific permissions:
- Read-only access
- Write access to specific resources
- Full administrative access
- Custom permission sets

### Security Best Practices

- Use service keys for automation
- Set expiration dates
- Rotate keys regularly
- Use minimum required permissions
- Store keys securely (environment variables, secrets managers)
- Never commit keys to version control

### Using API Keys

Include the API key in request headers:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.limacharlie.io/v1/...
```

Or use with the SDK:

```python
from limacharlie import Manager

manager = Manager(api_key="YOUR_API_KEY", oid="YOUR_ORG_ID")
```

## LimaCharlie SDK & CLI

The LimaCharlie SDK and CLI provide programmatic access to the platform for automation, integration, and advanced operations.

### Installation

**Python SDK:**
```bash
pip install limacharlie
```

**CLI:**
```bash
pip install limacharlie-cli
```

### SDK Usage

```python
from limacharlie import Manager

# Initialize
manager = Manager(api_key="YOUR_API_KEY", oid="YOUR_ORG_ID")

# List sensors
sensors = manager.sensors()

# Get specific sensor
sensor = manager.sensor("SENSOR_ID")

# Task sensor
sensor.task("history_dump_recent", {"hours": 24})
```

### CLI Usage

**Authentication:**
```bash
# Set credentials
limacharlie login --api-key YOUR_API_KEY --oid YOUR_ORG_ID

# Or use environment variables
export LC_API_KEY=YOUR_API_KEY
export LC_OID=YOUR_ORG_ID
```

**Common Commands:**
```bash
# List sensors
limacharlie sensors list

# Get sensor details
limacharlie sensor get SENSOR_ID

# Task sensor
limacharlie sensor task SENSOR_ID history_dump_recent

# Deploy D&R rules
limacharlie dr push rules.yaml

# Query events
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

### Advanced Features

- Batch sensor operations
- Event streaming
- Automated response workflows
- Integration with CI/CD pipelines
- Custom automation scripts

### Documentation

Full SDK documentation: [https://doc.limacharlie.io](https://doc.limacharlie.io)

## Secure Annex

Secure Annex is LimaCharlie's encrypted cloud storage service for sensitive data and artifacts collected from endpoints.

### Features

- **Encrypted Storage**: End-to-end encryption
- **Artifact Collection**: Store files, memory dumps, forensic data
- **Retention Policies**: Automatic expiration
- **Access Control**: RBAC integration
- **Audit Logging**: Complete access history

### Collecting Artifacts

Task sensors to upload artifacts to Secure Annex:

```yaml
- action: artifact_get
  artifact: path/to/file
  upload_to_annex: true
```

Via SDK:
```python
sensor.task("artifact_get", {
    "artifact": "/path/to/file",
    "upload_to_annex": True
})
```

### Retrieving Artifacts

```python
# List artifacts
artifacts = manager.annexes()

# Download artifact
artifact = manager.annex("ARTIFACT_ID")
data = artifact.download()
```

Via CLI:
```bash
limacharlie annex list
limacharlie annex download ARTIFACT_ID
```

### Retention Policies

Set automatic expiration:
- 24 hours
- 7 days
- 30 days
- 90 days
- Custom duration

### Use Cases

- Memory dump analysis
- Suspicious file collection
- Forensic investigations
- Malware sample collection
- Log file preservation

## Config Hive: Yara

Config Hive Yara enables you to deploy and manage Yara rules for file and memory scanning across your fleet.

### Creating Yara Rules

Store Yara rules in Config Hive for centralized management:

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

### Deploying Yara Rules

**Via Web Interface:**
1. Navigate to Config Hive > Yara
2. Create or upload rule
3. Apply to organization or specific tags

**Via SDK:**
```python
manager.add_yara_rule("rule_name", yara_source)
```

**Via CLI:**
```bash
limacharlie hive yara add rule_name rule_file.yara
```

### Scanning Operations

**File Scanning:**
```python
sensor.task("yara_scan", {
    "file_path": "C:\\suspect.exe",
    "rules": ["rule_name"]
})
```

**Memory Scanning:**
```python
sensor.task("yara_scan", {
    "pid": 1234,
    "rules": ["rule_name"]
})
```

### Automated Scanning

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

### Performance Considerations

- Use targeted rules to minimize CPU impact
- Limit concurrent scans
- Scan specific paths rather than entire filesystems
- Use rule namespaces for organization

## Config Hive: Detection & Response Rules

Detection & Response (D&R) rules are the core of LimaCharlie's automated threat detection and response capabilities.

### Rule Structure

```yaml
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
  - action: task
    command: deny_tree
```

### Detection Operators

- `is` / `is not`: Exact match
- `contains` / `not contains`: Substring match
- `starts with` / `ends with`: Prefix/suffix match
- `matches` / `not matches`: Regex match
- `exists`: Field presence check
- `greater than` / `less than`: Numeric comparison
- `lookup`: Query Config Hive lookup

### Common Event Types

- `NEW_PROCESS`: Process creation
- `NETWORK_CONNECTIONS`: Network activity
- `DNS_REQUEST`: DNS queries
- `FILE_CREATE` / `FILE_DELETE`: File operations
- `REGISTRY_CREATE` / `REGISTRY_DELETE`: Registry changes
- `NEW_DOCUMENT`: Document downloads
- `USER_OBSERVED`: User activity

### Response Actions

- `report`: Generate detection alert
- `task`: Execute sensor command
- `add tag`: Tag the sensor
- `remove tag`: Remove sensor tag
- `isolate`: Network isolate sensor
- `webhook`: Send to external system

### Example Rules

**Detect Suspicious PowerShell:**
```yaml
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

**Detect Lateral Movement:**
```yaml
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

### Rule Management

**Import/Export:**
```bash
limacharlie dr export rules.yaml
limacharlie dr import rules.yaml
```

**Version Control:**
Store D&R rules in Git and deploy via CI/CD:
```bash
limacharlie dr push rules/ --org-name prod
```

### Testing Rules

Use the D&R rule tester in the web interface to validate rules against historical events before deployment.

## Config Hive: Cloud Sensors

Cloud Sensors enable monitoring of cloud infrastructure and services including AWS, Azure, GCP, and other cloud platforms.

### Supported Platforms

- **AWS**: CloudTrail, GuardDuty, S3 access logs
- **Azure**: Activity logs, Security Center
- **GCP**: Cloud Logging, Security Command Center
- **Office 365**: Audit logs
- **Okta**: System logs

### Setting Up Cloud Sensors

**AWS CloudTrail:**
1. Navigate to Config Hive > Cloud Sensors
2. Select AWS CloudTrail
3. Provide IAM credentials or assume role ARN
4. Configure S3 bucket and SNS topic
5. Apply to organization

**Azure:**
1. Select Azure integration
2. Configure Azure AD application
3. Grant required permissions
4. Configure Event Hub connection

### Cloud Event Detection

D&R rules can detect cloud events:

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

### Common Use Cases

- Unauthorized access attempts
- Configuration changes
- Resource creation/deletion
- Permission modifications
- API abuse detection
- Compliance monitoring

### Best Practices

- Enable CloudTrail/logging in all regions
- Use dedicated IAM roles with minimal permissions
- Configure alerts for critical events
- Integrate with SIEM for correlation
- Regular review of cloud activity
- Automated response to policy violations