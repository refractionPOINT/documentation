# Atomic Red Team

Atomic Red Team is a library of tests mapped to the MITRE ATT&CK framework. Security teams can use these tests to validate their detection capabilities and security controls. The LimaCharlie Atomic Red Team integration allows you to run these security tests directly from the LimaCharlie platform.

## Overview

The Atomic Red Team add-on enables you to:

- Execute atomic tests from the Atomic Red Team library on your endpoints
- Validate detection and response rules
- Test security controls across the MITRE ATT&CK framework
- Integrate adversary emulation into your security testing workflow

## Prerequisites

- Active LimaCharlie organization
- Sensors deployed on endpoints where you want to run tests
- Appropriate permissions to execute commands on endpoints

## Installation

1. Navigate to the Add-ons section in your LimaCharlie organization
2. Find the Atomic Red Team add-on
3. Click "Subscribe" or "Enable"
4. Configure any required settings

## Usage

### Running Atomic Tests

You can execute Atomic Red Team tests through:

1. **Web Interface**: Select tests from the catalog and run them directly
2. **API**: Programmatically execute tests via the LimaCharlie API
3. **Detection & Response Rules**: Trigger tests as part of automated workflows

### Test Selection

Tests are organized by:

- MITRE ATT&CK Technique ID
- Platform (Windows, Linux, macOS)
- Test complexity
- Required dependencies

### Monitoring Results

Test execution results are captured as standard LimaCharlie telemetry:

- Command execution events
- Process creation events
- Network activity
- File system changes

You can create Detection & Response rules to alert on or respond to test activities.

## Best Practices

1. **Test in Non-Production First**: Always validate tests in a controlled environment
2. **Document Testing**: Keep records of which tests were run and when
3. **Review Test Details**: Understand what each test does before execution
4. **Monitor for Detection**: Verify your security controls detect the test activities
5. **Clean Up**: Some tests may leave artifacts; ensure proper cleanup procedures

## Example Workflow

1. Identify a MITRE ATT&CK technique you want to test (e.g., T1059.001 - PowerShell)
2. Select relevant atomic tests for your environment
3. Run the test on a designated test endpoint
4. Review LimaCharlie telemetry to confirm the activity was captured
5. Verify your Detection & Response rules triggered appropriately
6. Document results and gaps
7. Refine detection rules as needed

## Security Considerations

> **Warning**: Atomic Red Team tests simulate real adversary behavior. Some tests may:
> - Modify system configurations
> - Create files or registry entries
> - Execute potentially suspicious commands
> - Trigger security alerts

Always ensure you have proper authorization and are testing in appropriate environments.

## Additional Resources

- [Atomic Red Team GitHub Repository](https://github.com/redcanaryco/atomic-red-team)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- LimaCharlie Detection & Response documentation

---

# Integrity

The Integrity add-on provides file integrity monitoring (FIM) capabilities for your endpoints. It tracks changes to critical files and directories, helping you detect unauthorized modifications that could indicate a security breach or system compromise.

## Overview

File Integrity Monitoring helps you:

- Detect unauthorized changes to critical system files
- Monitor configuration file modifications
- Track changes to sensitive directories
- Maintain compliance requirements
- Identify potential indicators of compromise

## Features

- Real-time file change detection
- Configurable monitoring paths
- Change detail capture (content hash, timestamps, permissions)
- Integration with Detection & Response rules
- Historical change tracking

## Prerequisites

- Active LimaCharlie organization
- Deployed sensors on endpoints to monitor
- Appropriate storage allocation for change logs

## Installation

1. Navigate to Add-ons in your LimaCharlie organization
2. Locate the Integrity add-on
3. Click "Subscribe" or "Enable"
4. Configure monitoring parameters

## Configuration

### Defining Monitoring Paths

Specify which files and directories to monitor:

**Windows Example:**
```
C:\Windows\System32\drivers\
C:\Windows\System32\config\
C:\Program Files\
```

**Linux Example:**
```
/etc/
/usr/bin/
/usr/sbin/
/boot/
```

**macOS Example:**
```
/System/Library/
/Library/
/usr/bin/
/usr/sbin/
```

### Monitoring Options

Configure what changes to track:

- **Content Changes**: Hash-based detection of file modifications
- **Attribute Changes**: Permissions, ownership, timestamps
- **Creation/Deletion**: New files or removed files
- **Recursive Monitoring**: Include subdirectories

### Exclusions

Define patterns to exclude from monitoring:

- Temporary files
- Log files that change frequently
- Cache directories
- Known benign application updates

## Event Types

The Integrity add-on generates events for:

1. **FILE_MODIFIED**: Content hash changed
2. **FILE_CREATED**: New file detected
3. **FILE_DELETED**: File removed
4. **FILE_ATTRIBUTES_CHANGED**: Permissions, ownership, or timestamps modified

## Detection & Response Integration

### Example Rule: Alert on Critical System File Change

```yaml
detect:
  event: FILE_MODIFIED
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: "/etc/passwd"
respond:
  - action: report
    name: critical_file_modified
  - action: task
    command: history_dump
```

### Example Rule: Monitor Windows Registry Hive Changes

```yaml
detect:
  event: FILE_MODIFIED
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: "\\System32\\config\\"
respond:
  - action: report
    name: registry_hive_modified
```

## Best Practices

1. **Start Small**: Begin monitoring critical paths before expanding scope
2. **Tune Exclusions**: Reduce noise by excluding expected changes
3. **Baseline Normal Activity**: Understand typical change patterns
4. **Prioritize Alerts**: Focus on the most critical assets first
5. **Regular Reviews**: Periodically review and update monitoring configurations
6. **Storage Management**: Monitor storage usage for integrity logs

## Common Use Cases

### Compliance Monitoring

Monitor files required by compliance frameworks:

- PCI-DSS: Payment system configuration files
- HIPAA: Healthcare application configurations
- SOX: Financial system files

### Malware Detection

Detect indicators of compromise:

- System binary modifications
- Startup location changes
- Configuration file tampering

### Incident Response

During investigations:

- Identify compromised files
- Establish timeline of changes
- Determine scope of breach

## Performance Considerations

File integrity monitoring can impact system performance:

- **Monitor Selectively**: Only track truly critical paths
- **Avoid High-Change Directories**: Exclude logs, temp files, caches
- **Hash Algorithm**: Balance security with performance needs
- **Polling Frequency**: Adjust based on criticality and system capacity

## Troubleshooting

### High Volume of Events

- Review and expand exclusion patterns
- Reduce monitoring scope
- Check for applications causing frequent changes

### Missing Events

- Verify paths are correctly specified
- Check sensor connectivity
- Confirm sufficient permissions for file access

### Storage Issues

- Implement retention policies
- Archive older integrity logs
- Adjust monitoring scope

## Additional Resources

- LimaCharlie Detection & Response documentation
- Sensor configuration guides
- Compliance framework requirements