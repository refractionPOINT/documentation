# Ingesting Linux Audit Logs

The LimaCharlie sensor can ingest Linux audit logs and forward them as telemetry events. This guide shows you how to configure audit log ingestion.

## Prerequisites

- LimaCharlie sensor installed on Linux system
- Root/sudo access to configure audit rules
- Linux audit daemon (auditd) installed

## Configuration

### 1. Enable Audit Log Collection

Configure the sensor to monitor audit logs by adding the audit configuration to your sensor's configuration file or through the LimaCharlie web interface.

```yaml
audit:
  enabled: true
  rules:
    - path: /var/log/audit/audit.log
      format: auditd
```

### 2. Configure Audit Rules

Add audit rules to track specific system events. Example audit rules:

```bash
# Monitor file access
auditctl -w /etc/passwd -p wa -k passwd_changes
auditctl -w /etc/shadow -p wa -k shadow_changes

# Monitor system calls
auditctl -a always,exit -F arch=b64 -S execve -k exec_tracking

# Monitor network connections
auditctl -a always,exit -F arch=b64 -S socket -S connect -k network_tracking
```

### 3. Verify Configuration

Check that audit rules are active:

```bash
auditctl -l
```

Verify the sensor is reading audit logs:

```bash
journalctl -u limacharlie -f
```

## Event Format

Ingested audit logs will appear in LimaCharlie with the event type `AUDIT_LOG` and contain:

- `audit_type`: The audit event type (e.g., SYSCALL, EXECVE, PATH)
- `audit_msg`: The raw audit message
- `timestamp`: Event timestamp
- `node`: Node identifier
- Additional parsed fields depending on the audit event type

## Example Events

### File Access Event

```json
{
  "event_type": "AUDIT_LOG",
  "audit_type": "PATH",
  "path": "/etc/passwd",
  "operation": "write",
  "user": "root",
  "timestamp": 1696867200
}
```

### Process Execution Event

```json
{
  "event_type": "AUDIT_LOG",
  "audit_type": "EXECVE",
  "command": "/bin/bash",
  "arguments": ["-c", "whoami"],
  "user": "ubuntu",
  "timestamp": 1696867200
}
```

## Filtering and Rules

You can create D&R rules to detect specific audit events:

```yaml
detect:
  event: AUDIT_LOG
  op: and
  rules:
    - op: is
      path: audit_type
      value: EXECVE
    - op: contains
      path: command
      value: suspicious_binary

respond:
  - action: report
    name: suspicious_execution_detected
```

## Performance Considerations

- Audit logs can be high volume on busy systems
- Consider filtering rules to focus on security-relevant events
- Monitor sensor resource usage when enabling audit ingestion
- Use audit rules judiciously to avoid performance impact

## Troubleshooting

### Logs Not Appearing

1. Check sensor configuration is correct
2. Verify audit daemon is running: `systemctl status auditd`
3. Check file permissions on audit.log
4. Review sensor logs for errors

### High Volume

1. Refine audit rules to reduce noise
2. Use exclusion patterns in sensor configuration
3. Consider sampling for high-frequency events

## Related Documentation

- [Reference: EDR Events](/docs/en/reference-edr-events)
- [Reference: Platform Events](/docs/en/reference-platform-events)
- [Tutorial: Ingesting Telemetry from Cloud-Based External Sources](/docs/en/tutorial-ingesting-telemetry-from-cloud-based-external-sources)