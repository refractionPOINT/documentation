# Config Hive: Secrets

Secrets are encrypted key-value pairs that can be used in Detection & Response rules and other LimaCharlie components. They provide a secure way to store sensitive information like API keys, passwords, and tokens.

## Overview

Secrets are stored encrypted at rest and are only decrypted when needed during rule execution. This ensures sensitive data is never exposed in logs or rule definitions.

## Managing Secrets

### Creating Secrets

Secrets can be created through the web interface or API:

1. Navigate to **Config Hive** → **Secrets**
2. Click **Add Secret**
3. Provide a name and value
4. Save the secret

### Using Secrets in Rules

Reference secrets in Detection & Response rules using the following syntax:

```
{{ secret://secret-name }}
```

**Example:**

```yaml
- action: report
  metadata:
    api_key: "{{ secret://my-api-key }}"
```

### API Management

Secrets can be managed via the LimaCharlie API:

```bash
# Create a secret
limacharlie secret set my-secret "secret-value"

# List secrets (values are not displayed)
limacharlie secret list

# Delete a secret
limacharlie secret del my-secret
```

## Best Practices

1. **Unique Names**: Use descriptive, unique names for secrets
2. **Rotation**: Regularly rotate sensitive secrets
3. **Least Privilege**: Only grant access to secrets that are needed
4. **Audit**: Monitor secret usage through audit logs

## Security Considerations

- Secrets are encrypted at rest using industry-standard encryption
- Secret values are never logged or displayed after creation
- Access to secrets is controlled by organization permissions
- Secret usage is audited and can be tracked

---

# Config Hive: Lookups

Lookups are reference tables that can be queried during rule execution. They allow you to maintain lists of indicators, configurations, or other data that can be checked dynamically.

## Overview

Lookups provide a way to:
- Store lists of known indicators (IPs, domains, hashes)
- Maintain configuration values
- Create dynamic reference tables
- Perform real-time lookups during detection

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

## Managing Lookups

### Creating Lookups

1. Navigate to **Config Hive** → **Lookups**
2. Click **Add Lookup**
3. Provide a name and add key-value pairs
4. Save the lookup table

### Using Lookups in Rules

Reference lookups in Detection & Response rules:

```yaml
- action: report
  lookup:
    path: lookup://threat-ips
    key: "{{ .event.IP_ADDRESS }}"
```

**Example Rule:**

```yaml
event: NETWORK_CONNECTIONS
op: lookup
path: lookup://blocked-ips
key: "{{ .event.IP_ADDRESS }}"
action: report
metadata:
  detection: "Connection to blocked IP"
```

### API Management

```bash
# Create a lookup
limacharlie lookup set threat-ips 192.168.1.1 malicious

# Query a lookup
limacharlie lookup get threat-ips 192.168.1.1

# Delete a lookup entry
limacharlie lookup del threat-ips 192.168.1.1
```

## Use Cases

1. **Threat Intelligence**: Maintain lists of malicious indicators
2. **Allow Lists**: Track known-good entities
3. **Configuration**: Store environment-specific settings
4. **Enrichment**: Add context to events

## Best Practices

- Keep lookup tables focused and organized
- Regularly update lookup data
- Use descriptive names and keys
- Monitor lookup performance for large tables

---

# API Keys

API keys provide programmatic access to the LimaCharlie platform. They enable automation, integration, and custom tooling.

## Overview

API keys authenticate requests to the LimaCharlie API and can be scoped with specific permissions.

## Creating API Keys

1. Navigate to **Access** → **API Keys**
2. Click **Create API Key**
3. Provide a name and description
4. Select permissions (scopes)
5. Save and securely store the key

**Important**: API keys are only displayed once during creation. Store them securely.

## Permission Scopes

API keys can be granted various permission levels:

- **Read**: View organization data
- **Write**: Modify configurations
- **Admin**: Full administrative access
- **Sensor**: Sensor-specific operations
- **Custom**: Granular permission selection

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

## Security Best Practices

1. **Least Privilege**: Grant minimum necessary permissions
2. **Rotation**: Regularly rotate API keys
3. **Storage**: Never commit keys to source control
4. **Monitoring**: Track API key usage and audit logs
5. **Revocation**: Immediately revoke compromised keys

## API Key Management

### Listing Keys

View all API keys in your organization (values are masked).

### Revoking Keys

Immediately revoke compromised or unused keys.

### Auditing

Monitor API key usage through audit logs to detect unauthorized access.

---

# LimaCharlie SDK & CLI

The LimaCharlie SDK and CLI provide programmatic and command-line access to the platform.

## SDK (Python)

### Installation

```bash
pip install limacharlie
```

### Basic Usage

```python
from limacharlie import Manager

# Initialize manager
manager = Manager(api_key="YOUR_API_KEY")

# Get organization
org = manager.organization("your-org-id")

# List sensors
sensors = org.sensors()
for sensor in sensors:
    print(sensor.sid, sensor.hostname)

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
```

## CLI

### Installation

```bash
pip install limacharlie
```

### Configuration

```bash
# Configure credentials
limacharlie configure
```

### Common Commands

```bash
# List sensors
limacharlie sensor list

# Get sensor info
limacharlie sensor info SENSOR_ID

# Task a sensor
limacharlie sensor task SENSOR_ID os_version

# Manage D&R rules
limacharlie dr list
limacharlie dr add rule.yaml
limacharlie dr del rule-name

# Secrets management
limacharlie secret set my-secret "value"
limacharlie secret list

# Lookup management
limacharlie lookup set table-name key value
```

## Documentation

- [Python SDK Documentation](https://github.com/refractionPOINT/python-limacharlie)
- [API Reference](https://doc.limacharlie.io/docs/api)

---

# Secure Annex

Secure Annex provides encrypted storage for sensitive files and data within LimaCharlie.

## Overview

Secure Annex allows you to:
- Store sensitive files securely
- Reference files in Detection & Response rules
- Manage encrypted artifacts
- Maintain compliance with data security requirements

## Features

- **Encryption**: All data encrypted at rest
- **Access Control**: Granular permissions
- **Versioning**: Track file changes
- **Integration**: Use in rules and automations

## Usage

### Uploading Files

1. Navigate to **Secure Annex**
2. Click **Upload File**
3. Select file and provide metadata
4. Save

### Referencing in Rules

```yaml
- action: report
  file: annex://sensitive-config.json
```

### API Access

```python
# Upload file
org.annex_upload("file.txt", content)

# Download file
content = org.annex_download("file.txt")

# List files
files = org.annex_list()
```

## Best Practices

1. **Encryption**: Store only sensitive data in Annex
2. **Access Control**: Limit access to necessary personnel
3. **Versioning**: Track changes for audit purposes
4. **Cleanup**: Remove obsolete files regularly

---

# Config Hive: Yara

YARA rules can be used in LimaCharlie for file and memory scanning to detect malware and suspicious patterns.

## Overview

LimaCharlie supports YARA rules for:
- File scanning
- Memory scanning
- Process analysis
- Artifact detection

## Managing YARA Rules

### Adding YARA Rules

1. Navigate to **Config Hive** → **YARA**
2. Click **Add Rule**
3. Paste your YARA rule
4. Save and enable

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

## Using YARA in Rules

### File Scanning

```yaml
event: NEW_DOCUMENT
op: yara_scan
path: "{{ .event.FILE_PATH }}"
ruleset: custom-rules
action: report
```

### Memory Scanning

```yaml
event: NEW_PROCESS
op: yara_scan_process
pid: "{{ .event.PROCESS_ID }}"
ruleset: memory-rules
action: isolate
```

## Best Practices

1. **Testing**: Test rules before deployment
2. **Performance**: Optimize rules to avoid performance impact
3. **Maintenance**: Regularly update rule sets
4. **Documentation**: Document rule purpose and logic

## Integration with Detection

YARA results can trigger Detection & Response rules:

```yaml
event: YARA_DETECTION
target: artifact
op: is
value: suspicious-file
action: report
```

---

# Config Hive: Detection & Response Rules

Detection & Response (D&R) rules are the core of LimaCharlie's detection engine. They define how to detect threats and respond automatically.

## Overview

D&R rules consist of:
- **Detect**: Conditions that trigger the rule
- **Respond**: Actions to take when triggered

## Rule Structure

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

## Common Operators

- `is`: Exact match
- `contains`: Substring match
- `starts with`: Prefix match
- `ends with`: Suffix match
- `matches`: Regex match
- `greater than`: Numeric comparison
- `less than`: Numeric comparison

## Common Actions

- `report`: Create detection alert
- `isolate`: Network isolate sensor
- `task`: Execute sensor task
- `tag`: Add sensor tag
- `webhook`: Send webhook notification

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

## Best Practices

1. **Testing**: Test in report-only mode first
2. **Documentation**: Comment rule purpose
3. **Tuning**: Iterate to reduce false positives
4. **Performance**: Keep rules efficient
5. **Organization**: Use naming conventions

---

# Config Hive: Cloud Sensors

Cloud Sensors extend LimaCharlie's visibility to cloud environments and SaaS applications.

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
- Office 365
- Google Workspace
- Okta
- Other via API

## Configuration

### AWS Setup

1. Navigate to **Config Hive** → **Cloud Sensors**
2. Select **AWS**
3. Provide IAM credentials or role ARN
4. Select log sources
5. Save configuration

```json
{
  "platform": "aws",
  "role_arn": "arn:aws:iam::123456789:role/LimaCharlie",
  "log_sources": ["cloudtrail", "vpc_flow"]
}
```

### Azure Setup

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

```yaml
event: AWS_CLOUDTRAIL
detect:
  op: is
  path: event/eventName
  value: "DeleteBucket"
respond:
  - action: report
    metadata:
      detection: "AWS S3 bucket deleted"
```

## Best Practices

1. **Least Privilege**: Use minimal required permissions
2. **Cost Management**: Monitor ingestion costs
3. **Filtering**: Ingest only necessary logs
4. **Integration**: Correlate cloud and endpoint events