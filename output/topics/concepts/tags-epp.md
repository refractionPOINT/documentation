# Endpoint Protection Platform (EPP)

## Overview

The Endpoint Protection Platform (EPP) extension provides traditional anti-malware capabilities within LimaCharlie, combining signature-based detection with behavioral analysis to protect endpoints from known and emerging threats. EPP continuously monitors endpoints for malicious activity and automatically takes protective actions based on detected threats.

## Key Features

- **Real-time File Scanning**: Monitors and scans files as they are accessed on protected endpoints
- **Signature-based Malware Detection**: Checks files against updated malware signature databases
- **Behavioral Analysis**: Detects anomalous behavior patterns and suspicious activities
- **File Reputation**: Validates file hashes against known malware databases
- **Threat Intelligence Integration**: Leverages up-to-date threat intelligence feeds
- **Automated Response**: Takes immediate action when threats are detected
- **Integration with D&R Rules**: Seamlessly works with LimaCharlie's Detection & Response engine
- **Centralized Management and Reporting**: Unified interface for configuration and monitoring

## Detection Capabilities

The EPP extension provides detection for:

- Malware execution
- Ransomware activity
- Credential dumping
- Lateral movement
- Suspicious PowerShell usage
- Living-off-the-land (LOLBin) abuse
- Process injection
- Persistence mechanisms

## Installation

To enable EPP for your organization:

1. Navigate to the **Add-ons** section in the LimaCharlie web interface
2. Find **Endpoint Protection** in the available extensions
3. Click **Subscribe** to activate the extension
4. Configure your EPP policies and rules

## Configuration

### Basic Setup

EPP works by scanning files as they are accessed on protected endpoints. Configure the extension in your organization settings with the desired protection policies and response actions. You can control scanning behavior through Detection & Response rules that trigger EPP scans.

### Creating EPP Scan Rules

Create Detection & Response rules to specify when and what to scan:

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: exists
      path: event/FILE_PATH
    - op: matches
      path: event/FILE_PATH
      re: '.*\.exe$'

respond:
  - action: epp_scan
    metadata:
      path: event/FILE_PATH
```

### Response Actions

When malware is detected, EPP can trigger automated responses:

- **quarantine**: Isolate the malicious file
- **delete**: Remove the file from the system
- **report**: Log the detection without taking action
- **block**: Prevent the file from executing
- **Process termination**: Kill malicious processes
- **Network isolation**: Isolate compromised endpoints
- **Alert generation**: Trigger notifications
- **Custom remediation actions**: Execute custom response workflows

Example response configuration:

```yaml
respond:
  - action: epp_scan
    metadata:
      path: event/FILE_PATH
      on_detection: quarantine
```

## Signature Updates

EPP signatures are automatically updated to protect against the latest threats. Updates occur in the background without requiring manual intervention or endpoint restarts, ensuring continuous protection against emerging threats.

## Integration with Detection & Response

EPP seamlessly integrates with LimaCharlie's Detection & Response engine. You can:

- Create rules that trigger EPP scans based on behavioral indicators
- Combine EPP results with other telemetry for enriched detection logic
- Chain EPP scans with other response actions
- Use EPP alongside behavioral D&R rules for comprehensive, layered defense

## Monitoring and Alerts

EPP detections appear in your organization's detections feed and can trigger alerts through configured notification channels. Each detection includes:

- File hash (MD5, SHA1, SHA256)
- File path and name
- Detection signature name
- Threat severity level
- Timestamp and endpoint identifier

Regularly review EPP alerts to identify false positives and tune detection sensitivity based on your environment.

## API Integration

EPP functionality is available through the LimaCharlie API, allowing you to:

- Trigger on-demand scans
- Retrieve detection results
- Manage EPP configurations programmatically

Example API call for on-demand scan:

```bash
curl -X POST https://api.limacharlie.io/v1/org/{oid}/extension/epp/scan \
  -H "Authorization: Bearer {jwt_token}" \
  -d '{
    "sid": "sensor_id",
    "path": "/path/to/file"
  }'
```

## Best Practices

1. **Layered Defense**: Use EPP alongside behavioral D&R rules for comprehensive protection
2. **Test Response Actions**: Validate automated responses in a test environment first. Test rules in report-only mode before enabling automated responses
3. **Tune Detection Rules**: Adjust sensitivity based on your environment to balance security and operational impact
4. **Monitor Alerts**: Regularly review EPP alerts for false positives and detection accuracy
5. **Update Threat Intelligence**: Keep threat intelligence feeds current (handled automatically)
6. **Document Exceptions**: Maintain a list of approved exceptions and whitelists for known-good files
7. **Regular Review**: Periodically audit your EPP configuration and update scanning policies as needed
8. **Use File Reputation**: Supplement EPP decisions with file reputation data for improved accuracy

## Troubleshooting

### Scans Not Triggering

- Verify EPP extension is active for your organization
- Check that D&R rules targeting EPP are enabled
- Ensure sensors have network connectivity to receive signature updates

### High False Positive Rate

- Review detection signatures and adjust sensitivity
- Create allowlist rules for known-good files
- Consider using file reputation data to supplement EPP decisions

### Performance Impact

- EPP scanning is optimized for minimal performance impact
- Adjust scan triggers to balance security and performance
- Consider scanning only high-risk file types or locations

## Support

For EPP-related issues or questions, contact LimaCharlie support through the web interface or email support@limacharlie.io.