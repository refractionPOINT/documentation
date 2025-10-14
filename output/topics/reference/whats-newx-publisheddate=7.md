# YARA

LimaCharlie supports YARA for pattern matching and malware detection through both sensor commands and extensions.

## YARA Sensor Command

The YARA sensor command allows you to scan files on endpoints using YARA rules.

### Usage

```
yara_scan <rule_name> <target_path>
```

**Parameters:**
- `rule_name`: The name of the YARA rule to use for scanning
- `target_path`: The file or directory path to scan

### Example

```
yara_scan malware_detection C:\Users\*\Downloads\*
```

## YARA Extension

LimaCharlie provides a third-party YARA extension for more advanced scanning capabilities.

### Features

- Automated YARA scanning across your fleet
- Integration with YARA rule repositories
- Custom rule management
- Continuous monitoring and alerting

### Configuration

The YARA extension can be configured through the LimaCharlie web interface or API to:

- Define scanning schedules
- Specify target paths
- Set up alerting rules
- Manage YARA rule sets

## Building Reports with BigQuery + Looker Studio

You can create comprehensive reports by exporting LimaCharlie data to BigQuery and visualizing it with Looker Studio.

### Setup Steps

1. Configure BigQuery export in LimaCharlie
2. Connect BigQuery to Looker Studio
3. Create custom dashboards and reports
4. Set up automated report delivery

### Use Cases

- Security metrics and KPIs
- Threat detection trends
- Compliance reporting
- Incident response analytics

## Ingesting Windows Event Logs

LimaCharlie can ingest and process Windows Event Logs for enhanced visibility and detection.

### Configuration

Enable Windows Event Log collection through:

```yaml
event_logs:
  - channel: Security
    enabled: true
  - channel: System
    enabled: true
  - channel: Application
    enabled: true
```

### Supported Event Channels

- Security
- System
- Application
- PowerShell
- Windows Defender
- Custom channels

### Detection and Response

Use D&R rules to:
- Detect suspicious authentication events
- Monitor privilege escalation
- Track application crashes
- Identify malware activity

## Ingesting MacOS Unified Logs

LimaCharlie supports ingesting MacOS Unified Logs for comprehensive endpoint visibility on MacOS systems.

### Configuration

Enable MacOS Unified Log collection:

```yaml
unified_logs:
  enabled: true
  predicates:
    - 'eventType == "logEvent"'
    - 'processImagePath CONTAINS "suspicious"'
```

### Log Filtering

Use predicates to filter logs by:
- Process name
- Event type
- Subsystem
- Category
- Log level

### Detection Capabilities

Create D&R rules to detect:
- Suspicious process execution
- Authentication events
- System modifications
- Application behavior