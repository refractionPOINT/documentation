# Ingesting Linux Audit Logs

Linux Audit is a native kernel-level auditing framework that provides detailed logging of system calls, file access, and security events. LimaCharlie can ingest and process these audit logs alongside native EDR telemetry.

## Overview

The Linux Audit framework (auditd) generates logs that are valuable for security monitoring and compliance. LimaCharlie's sensor can ingest these logs and normalize them into the event stream for detection and response.

## Prerequisites

- Linux system with audit framework installed (`auditd` package)
- LimaCharlie sensor installed and running
- Appropriate permissions to read audit logs

## Configuration

### 1. Enable Audit Log Ingestion

Configure the sensor to ingest audit logs by adding a log ingestion rule:

```yaml
- log_type: audit
  log_path: /var/log/audit/audit.log
  format: audit
```

### 2. Set Up Audit Rules

Configure audit rules to capture relevant events. Example audit rules:

```bash
# Monitor file access
auditctl -w /etc/passwd -p rwxa -k passwd_changes
auditctl -w /etc/shadow -p rwxa -k shadow_changes

# Monitor system calls
auditctl -a always,exit -F arch=b64 -S execve -k exec_tracking

# Monitor network connections
auditctl -a always,exit -F arch=b64 -S socket -S connect -k network_activity
```

### 3. Sensor Configuration

Add the ingestion configuration to the sensor via the web UI or API:

```json
{
  "log_ingestion": {
    "audit": {
      "enabled": true,
      "log_path": "/var/log/audit/audit.log",
      "parser": "audit"
    }
  }
}
```

## Event Format

Audit logs are normalized into LimaCharlie events with the following structure:

```json
{
  "event_type": "AUDIT_LOG",
  "audit": {
    "type": "EXECVE",
    "timestamp": "2025-10-10T12:34:56.789Z",
    "serial": 12345,
    "pid": 1234,
    "uid": 1000,
    "gid": 1000,
    "command": "/usr/bin/example",
    "key": "exec_tracking",
    "raw": "type=EXECVE msg=audit(1696944896.789:12345): argc=2 a0=\"/usr/bin/example\" a1=\"arg1\""
  }
}
```

## Detection Rules

Create detection rules that leverage audit log data:

```yaml
event: AUDIT_LOG
op: and
rules:
  - path: audit/type
    op: is
    value: EXECVE
  - path: audit/command
    op: contains
    value: suspicious_binary
respond:
  - action: report
    name: suspicious_audit_execution
```

## Common Use Cases

### Monitor Privileged Access

```bash
# Track sudo usage
auditctl -w /usr/bin/sudo -p x -k sudo_usage

# Track su command
auditctl -w /bin/su -p x -k su_usage
```

### File Integrity Monitoring

```bash
# Monitor critical system files
auditctl -w /bin -p wa -k binary_changes
auditctl -w /sbin -p wa -k system_binary_changes
auditctl -w /usr/bin -p wa -k user_binary_changes
```

### Network Monitoring

```bash
# Track network connections
auditctl -a always,exit -F arch=b64 -S socket -S connect -S bind -k network_events
```

## Performance Considerations

- Audit logs can be verbose; filter appropriately to reduce volume
- Use specific audit rules rather than broad wildcards
- Monitor sensor resource usage when enabling audit ingestion
- Consider log rotation policies to manage disk space

## Troubleshooting

### Logs Not Appearing

1. Verify audit daemon is running: `systemctl status auditd`
2. Check audit rules are loaded: `auditctl -l`
3. Verify log file permissions allow sensor to read
4. Check sensor logs for ingestion errors

### High Volume Issues

- Review and refine audit rules to reduce noise
- Implement rate limiting at the audit level
- Use audit dispatcher filters
- Consider sampling for high-frequency events

## Additional Resources

- Linux Audit documentation: `man auditd`
- Audit rules examples: `man auditctl`
- LimaCharlie sensor configuration reference