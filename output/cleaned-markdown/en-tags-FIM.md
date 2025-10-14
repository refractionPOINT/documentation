# File Integrity Monitoring (FIM) Deployments

File Integrity Monitoring (FIM) allows you to track changes to critical files and registry keys on your endpoints. This capability is essential for detecting unauthorized modifications to system files, configuration files, and other sensitive resources.

## Overview

LimaCharlie's FIM implementation monitors specified files and registry locations for changes, reporting events when modifications occur. This enables you to:

- Detect unauthorized changes to critical system files
- Monitor configuration file modifications
- Track registry key changes (Windows)
- Maintain audit trails of file system changes
- Create detection and response rules based on file modifications

## Configuration

FIM is configured through D&R (Detection & Response) rules that specify which files or registry keys to monitor and what actions to trigger when changes are detected.

### Basic FIM Rule Structure

```yaml
detect:
  event: FIM_*
  op: and
  rules:
    - path: /path/to/monitor
      
respond:
  - action: report
    name: file_modification_detected
```

## Monitoring Files

To monitor specific files or directories:

```yaml
detect:
  event: FIM_MODIFIED
  op: and
  rules:
    - path: /etc/passwd
      
respond:
  - action: report
    name: critical_file_modified
```

### Recursive Directory Monitoring

Monitor all files within a directory recursively:

```yaml
detect:
  event: FIM_MODIFIED
  op: and
  rules:
    - path: /etc/
      is_recursive: true
      
respond:
  - action: report
    name: etc_directory_change
```

## Monitoring Registry Keys (Windows)

For Windows systems, monitor registry keys:

```yaml
detect:
  event: FIM_MODIFIED
  op: and
  rules:
    - path: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run
      
respond:
  - action: report
    name: autorun_registry_modified
```

## FIM Events

LimaCharlie generates the following FIM events:

- **FIM_MODIFIED**: File or registry key content changed
- **FIM_CREATED**: New file or registry key created
- **FIM_DELETED**: File or registry key deleted

## Best Practices

1. **Start Small**: Begin monitoring critical system files before expanding to broader directories
2. **Use Filters**: Apply appropriate filters to reduce noise from expected changes
3. **Baseline Normal Activity**: Understand normal file modification patterns before alerting
4. **Prioritize Critical Assets**: Focus on files that impact security and system integrity
5. **Combine with Other Rules**: Use FIM events in combination with other detection rules for better context

## Example Use Cases

### Monitor SSH Configuration

```yaml
detect:
  event: FIM_MODIFIED
  op: and
  rules:
    - path: /etc/ssh/sshd_config
      
respond:
  - action: report
    name: ssh_config_modified
  - action: task
    command: report_ssh_config_change
```

### Monitor Windows Startup Programs

```yaml
detect:
  event: FIM_CREATED
  op: and
  rules:
    - path: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run
      
respond:
  - action: report
    name: new_autorun_program
  - action: task
    command: investigate_startup_item
```

### Monitor Web Server Configuration

```yaml
detect:
  event: FIM_MODIFIED
  op: and
  rules:
    - path: /etc/nginx/
      is_recursive: true
      
respond:
  - action: report
    name: nginx_config_changed
```