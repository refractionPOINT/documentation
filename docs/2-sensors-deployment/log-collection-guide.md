# Log Collection Guide

This guide explains how to collect system logs into LimaCharlie with USP adapters. The examples show common Linux log paths. The same adapter configurations work on each supported platform (FreeBSD, macOS, and others). Change the file paths for your OS.

## Collection Methods

### File Adapter (Recommended for Log Files)

The file adapter monitors log files for changes. It sends new entries to LimaCharlie. It supports glob patterns to monitor many files, and it handles log rotation automatically.

#### Key Features

- Glob pattern support (/var/log/*.log)
- Automatic handling of log rotation, with detection based on the inode
- Polling mode for reliable collection on BSD, on network filesystems, and across log rotations
- Backfill of historical data
- Multi-line JSON parsing
- Grok pattern parsing to extract structured fields

#### Basic Configuration

```yaml
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"  # or "json" for structured logs
    sensor_seed_key: "linux-logs"
  file_path: "/path/to/logfile"
  backfill: false  # Set true to read existing content
  no_follow: false # Set true to stop after reading existing content
```

### Syslog Adapter

The syslog adapter runs as a syslog server. It accepts logs through TCP or UDP. Use it to centralize logs from many systems, or to connect it to a syslog infrastructure that exists.

#### Key Features

- TCP and UDP support
- TLS encryption support
- Mutual TLS authentication
- RFC 3164/5424 syslog format support

#### Basic Configuration

```yaml
syslog:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "syslog-server"
  port: 514
  iface: "0.0.0.0"
  is_udp: false  # Use TCP by default
```

## Log Parsing Options

LimaCharlie supports two methods to parse unstructured log data:

- **parsing_grok**: Uses Grok patterns (recommended) - pre-built patterns for common log formats, easier to read and to maintain
- **parsing_re**: Uses regular expressions - for custom formats, or when Grok patterns do not meet your needs

Grok patterns are built on regular expressions, but they give named patterns for common elements such as timestamps, IP addresses, and log formats. Use Grok when possible, because it is easier to maintain.

## Common Log Sources

### System Logs (/var/log/messages, /var/log/syslog)

Traditional system logs contain kernel messages, service logs, and general system events.

**File Adapter Approach:**

```yaml
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "system-logs"
    mapping:
      parsing_grok:
        message: "%{SYSLOGTIMESTAMP:date} %{HOSTNAME:host} %{DATA:service}(?:\\[%{POSINT:pid}\\])?: %{GREEDYDATA:message}"
      sensor_hostname_path: "host"
      event_type_path: "service"
  file_path: "/var/log/messages"  # or /var/log/syslog
```

### Kernel Logs (/var/log/kern.log)

Kernel messages that include hardware events, driver messages, and security events.

```yaml
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "kernel-logs"
    mapping:
      parsing_grok:
        message: "%{SYSLOGTIMESTAMP:date} %{HOSTNAME:host} kernel: %{GREEDYDATA:message}"
      sensor_hostname_path: "host"
      event_type_path: "kernel"
  file_path: "/var/log/kern.log"
```

### Apache Logs (/var/log/httpd/*, /var/log/apache2/*)

```yaml
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "apache-logs"
    mapping:
      parsing_grok:
        message: "%{COMMONAPACHELOG}"
      event_type_path: "verb"
  file_path: "/var/log/apache2/access.log"  # or /var/log/httpd/access_log
```

### Nginx Logs (/var/log/nginx/*)

```yaml
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "nginx-logs"
    mapping:
      parsing_grok:
        message: "%{NGINXACCESS}"
      event_type_path: "verb"
  file_path: "/var/log/nginx/access.log"
```

### Audit Logs (/var/log/audit/audit.log)

Linux audit logs are critical for compliance with CIS Controls and for security monitoring.

```yaml
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "audit-logs"
    mapping:
      parsing_grok:
        message: "type=%{DATA:audit_type} msg=audit\\(%{NUMBER:timestamp}:%{NUMBER:serial}\\): %{GREEDYDATA:audit_data}"
      event_type_path: "audit_type"
      event_time_path: "timestamp"
  file_path: "/var/log/audit/audit.log"
```

## Journalctl

A modern logging solution that can output JSON format for structured parsing.

### Method 1: Pipe to Stdin Adapter

```bash
# Stream journalctl JSON output into the stdin adapter
journalctl -f -q --output=json | /path/to/lc_adapter stdin \
  client_options.identity.installation_key=$INSTALLATION_KEY \
  client_options.identity.oid=$OID \
  client_options.platform=json \
  client_options.sensor_seed_key=journalctl-logs \
  client_options.hostname=my-server
```

## Method 2: Output to File and Monitor

```bash
# Create a systemd service to write journal to file
sudo tee /etc/systemd/system/journal-export.service << EOF
[Unit]
Description=Export systemd journal to file
After=systemd-journald.service

[Service]
ExecStart=/usr/bin/journalctl -f -q --output=json
StandardOutput=append:/var/log/journal-export.json
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable journal-export.service
sudo systemctl start journal-export.service
```

Then monitor the file:

```yaml
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "json"  # JSON format for structured data
    sensor_seed_key: "journalctl-logs"
    mapping:
      sensor_hostname_path: "_HOSTNAME"
      event_type_path: "_SYSTEMD_UNIT"
      event_time_path: "__REALTIME_TIMESTAMP"
  file_path: "/var/log/journal-export.json"
```

## Multi-File Collection

To collect many log types at the same time:

```yaml
# /var/log/messages
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "system-logs"
  file_path: "/var/log/messages"

---

# Kernel logs
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "kernel-logs"
  file_path: "/var/log/kern.log"

---

# Audit logs
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "audit-logs"
  file_path: "/var/log/audit/audit.log"

---

# Web server logs (glob pattern for multiple files)
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "web-logs"
  file_path: "/var/log/nginx/*.log"
```

## Best Practices

- **Use JSON format when possible** - Modern logs often support JSON output. JSON gives better structure and parsing.
- **Configure appropriate Grok patterns** - Grok gives pre-built patterns for common log formats, and it is easier to maintain than regex. Use `parsing_grok` instead of `parsing_re` when possible.
- **Set sensor_seed_key appropriately** - Use descriptive names that identify the log source. Descriptive names make management easier.
- **Monitor file permissions** - Make sure that the adapter has read access to the log files.
- **Use backfill carefully** - Enable backfill only for the first collection of historical data. This stops duplicates.
- **Enable polling when needed** - Set `poll: true` if the adapter stops collection after log rotation. Also set it on FreeBSD and BSD systems, and on network filesystems. See the [File Adapter documentation](adapters/types/file.md#polling-mode) for details.
- **Implement proper field mapping** - Extract the hostname, the timestamps, and the event types. These fields make the logs easier to search.
- **Pattern testing** - Test Grok patterns against sample log lines before you deploy them. Common patterns include %{COMMONAPACHELOG}, %{SYSLOGTIMESTAMP}, and %{NGINXACCESS}.

## Troubleshooting

Common issues:

- **File permission errors**: Check that the adapter process has read access to log files
- **Parse failures**: Validate Grok patterns against actual log formats
- **Missing logs**: Check the file paths and the glob patterns
- **Adapter stops collecting after log rotation**: Set `poll: true` in the configuration of your file adapter. The adapter then uses polling instead of filesystem event notifications. Polling reliably detects new data after a log rotation tool (for example `newsyslog` or `logrotate`) replaces the file. This problem is common on FreeBSD and other BSD systems
- **Connection issues**: Check the network connectivity and the authentication credentials
