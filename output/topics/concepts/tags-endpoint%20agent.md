# Ingesting Linux Audit Logs

The LimaCharlie sensor can ingest Linux Audit logs and forward them to the LimaCharlie cloud for processing, storage, and analysis.

## Prerequisites

- LimaCharlie sensor installed on a Linux system
- Linux Audit daemon (`auditd`) installed and configured
- Appropriate permissions to read audit logs

## Configuration

To enable Linux Audit log ingestion, you need to configure the sensor to monitor the audit log files.

### Step 1: Configure Linux Audit

First, ensure that `auditd` is installed and running on your Linux system:

```bash
sudo systemctl status auditd
```

If not installed, install it using your package manager:

```bash
# Debian/Ubuntu
sudo apt-get install auditd

# RHEL/CentOS
sudo yum install audit
```

### Step 2: Configure Audit Rules

Configure audit rules to capture the events you're interested in. Edit `/etc/audit/rules.d/audit.rules` or use the `auditctl` command.

Example audit rules:

```bash
# Monitor file access
-w /etc/passwd -p wa -k passwd_changes
-w /etc/shadow -p wa -k shadow_changes

# Monitor system calls
-a always,exit -F arch=b64 -S execve -k exec_commands

# Monitor network connections
-a always,exit -F arch=b64 -S socket -k network_socket
```

Load the rules:

```bash
sudo auditctl -R /etc/audit/rules.d/audit.rules
```

### Step 3: Configure LimaCharlie Sensor

Configure the LimaCharlie sensor to ingest audit logs by creating or modifying the sensor configuration.

You can configure this through the LimaCharlie web interface or via the CLI:

1. Navigate to your organization in the LimaCharlie web interface
2. Go to **Sensors** → select your sensor → **Configurations**
3. Add or modify the configuration to include audit log ingestion

Alternatively, use the LimaCharlie CLI or API to set the configuration:

```yaml
# Example configuration
audit_logs:
  enabled: true
  log_path: /var/log/audit/audit.log
  parser: linux_audit
```

### Step 4: Configure Log Collection

The sensor needs to be configured to collect the audit logs. This is typically done through the sensor's configuration file or via a D&R rule.

Example sensor command to enable audit log collection:

```bash
sensor_config:
  audit:
    enabled: true
    log_file: /var/log/audit/audit.log
```

### Step 5: Verify Ingestion

After configuration, verify that audit logs are being ingested:

1. Generate some audit events (e.g., modify `/etc/passwd`)
2. Check the LimaCharlie timeline for your sensor
3. Look for events with the `AUDIT_LOG` event type

## Event Format

Linux Audit logs ingested by LimaCharlie will appear as events with the following structure:

```json
{
  "event_type": "AUDIT_LOG",
  "timestamp": 1234567890,
  "audit_type": "SYSCALL",
  "audit_data": {
    "type": "SYSCALL",
    "msg": "audit(1234567890.123:456): ...",
    "arch": "x86_64",
    "syscall": "execve",
    "success": "yes",
    // Additional audit fields...
  }
}
```

## Detection and Response

You can create D&R rules to detect and respond to specific audit events. Example rule:

```yaml
detect:
  event: AUDIT_LOG
  op: and
  rules:
    - op: is
      path: event/audit_data/type
      value: EXECVE
    - op: contains
      path: event/audit_data/a0
      value: /bin/bash

respond:
  - action: report
    name: bash_execution_detected
```

## Performance Considerations

- Audit logs can be verbose; configure rules to capture only necessary events
- Monitor sensor resource usage when ingesting audit logs
- Consider log rotation and retention policies
- Use filters to reduce noise and focus on security-relevant events

## Troubleshooting

### Logs Not Appearing

1. Verify `auditd` is running: `sudo systemctl status auditd`
2. Check audit rules are loaded: `sudo auditctl -l`
3. Verify sensor has read permissions for audit log files
4. Check sensor connectivity and status in LimaCharlie console

### High Volume of Events

1. Refine audit rules to be more specific
2. Use exclusion rules to filter out noisy events
3. Adjust audit log buffer size if needed
4. Consider using audit dispatcher for real-time processing

## Best Practices

1. **Start Small**: Begin with a limited set of audit rules and expand as needed
2. **Test Rules**: Validate audit rules in a test environment before production deployment
3. **Monitor Performance**: Track the impact of audit logging on system performance
4. **Regular Review**: Periodically review and update audit rules based on security requirements
5. **Coordinate with SIEM**: If using a SIEM, ensure audit log ingestion complements your existing logging strategy

## Additional Resources

- [Linux Audit Documentation](https://man7.org/linux/man-pages/man8/auditd.8.html)
- [LimaCharlie D&R Rules](/docs/en/detection-and-response-rules)
- [Reference: EDR Events](/docs/en/reference-edr-events)