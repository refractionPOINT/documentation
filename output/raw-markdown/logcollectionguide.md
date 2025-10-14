[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v2

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Log Collection Guide

* 21 Aug 2025
* 4 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Log Collection Guide

* Updated on 21 Aug 2025
* 4 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

This guide covers how to collect various Linux system logs into LimaCharlie using USP adapters. LimaCharlie provides flexible log collection capabilities through file monitoring and syslog ingestion.

## Collection Methods

### File Adapter (Recommended for Log Files)

The file adapter monitors log files for changes and streams new entries to LimaCharlie. It supports glob patterns for monitoring multiple files and handles log rotation automatically.

#### Key Features:

* Glob pattern support (/var/log/\*.log)
* Automatic log rotation handling
* Backfill support for historical data
* Multi-line JSON parsing
* Grok pattern parsing for structured log extraction

#### Basic Configuration:

```
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"  # or "json" for structured logs
    sensor_seed_key: "linux-logs"
  file_path: "/path/to/logfile"
  backfill: false  # Set true to read existing content
  no_follow: false # Set true to stop after reading existing content
```

### Syslog Adapter

runs as a syslog server, accepting logs via TCP or UDP. This is useful for centralizing logs from multiple systems or integrating with existing syslog infrastructure.

#### Key Features:

* TCP and UDP support
* TLS encryption support
* Mutual TLS authentication
* RFC 3164/5424 syslog format support

#### Basic Configuration:

```
syslog:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "syslog-server"
  port: 514
  interface: "0.0.0.0"
  is_udp: false  # Use TCP by defaultLog Parsing Options
```

LimaCharlie supports two methods for parsing unstructured log data:

* **parsing\_grok**: Uses Grok patterns (recommended) - pre-built patterns for common log formats, easier to read and maintain
* **parsing\_re**: Uses regular expressions - for custom formats or when Grok patterns don’t meet specific needs

Grok patterns are built on regular expressions but provide named patterns for common elements like timestamps, IP addresses, and log formats. Use Grok when possible for better maintainability.

## Common Log Sources

### System Logs (/var/log/messages, /var/log/syslog)

Traditional system logs contain kernel messages, service logs, and general system events.

**File Adapter Approach:**

```
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
  file_path: "/var/log/messages"  # or /var/log/syslogKernel Logs (/var/log/kern.log)
```

**Kernel-specific messages including hardware events, driver messages, and security events.**

```
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

**Apache Logs (/var/log/httpd/*, /var/log/apache2/*):**

```
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
  file_path: "/var/log/apache2/access.log"  # or /var/log/httpd/access_log
```

**Nginx Logs (/var/log/nginx/\*):**

```
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

Linux audit logs are critical for CIS Controls compliance and security monitoring.

```
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

Modern logging solution that can output in JSON format for structured parsing.

**Method 1: Pipe to Syslog Adapter**

```
# Stream journalctl to syslog adapter
journalctl -f -q --output=json | nc localhost 514
```

**Method 2: Output to File and Monitor**

```
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

```
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "json"  # JSON format for structured data
    sensor_seed_key: "journalctl-logs"
    mapping:
      sensor_hostname_path: "_HOSTNAME"
      event_type_path: "_SYSTEMD_UNIT"
      event_time_path: "__REALTIME_TIMESTAMP"
  file_path: "/var/log/journal-export.json"
```

## Multi-File Collection

For collecting multiple log types simultaneously:

```
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

* **Use JSON format when possible** - Modern logs often support JSON output, which provides better structure and parsing.
* **Configure appropriate Grok patterns** - Grok provides pre-built patterns for common log formats and is easier to maintain than regex. Use `parsing_grok` over `parsing_re` when possible.
* **Set sensor\_seed\_key appropriately** - Use descriptive names that identify the log source for easier management.
* **Monitor file permissions** - Ensure the adapter has read access to log files.
* **Use backfill carefully** - Only enable for initial historical data collection to avoid duplicates.
* **Implement proper field mapping** - Extract hostname, timestamps, and event types for better searchability.
* **Pattern testing** - Test Grok patterns against sample log lines before deployment. Common patterns include %{COMMONAPACHELOG}, %{SYSLOGTIMESTAMP}, and %{NGINXACCESS}.

## Troubleshooting

Common issues:

* **File permission errors**: Check that the adapter process has read access to log files
* **Parse failures**: Validate Grok patterns against actual log formats
* **Missing logs**: Verify file paths and glob patterns
* **Connection issues**: Check network connectivity and authentication credentials

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### What's Next

* [Reference: ID Schema](/docs/reference-id-schema)

Table of contents

+ [Collection Methods](#collection-methods)
+ [Common Log Sources](#common-log-sources)
+ [Journalctl](#journalctl)
+ [Multi-File Collection](#multi-file-collection)
+ [Best Practices](#best-practices)
+ [Troubleshooting](#troubleshooting)
