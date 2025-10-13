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

# Kernel logs
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "kernel-logs"
  file_path: "/var/log/kern.log"

# Audit logs
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "audit-logs"
  file_path: "/var/log/audit/audit.log"

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