# Syslog Specific Docs: https://docs.limacharlie.io/docs/adapter-types-syslog

sensor_type: "syslog"
  syslog:
    port: 1514
    iface: "0.0.0.0"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_SYSLOG"
      hostname: "syslog-adapter"
      platform: "linux"
      sensor_seed_key: "syslog-collector"
      mapping:
        parsing_grok:
          message: "^<%{INT:pri}>%{SYSLOGTIMESTAMP:timestamp}\\s+%{HOSTNAME:hostname}\\s+%{WORD:tag}(?:\\[%{INT:pid}\\])?:\\s+%{GREEDYDATA:message}"
        sensor_hostname_path: "hostname"
        event_type_path: "tag"
        event_time_path: "timestamp"
    # Optional syslog-specific configuration
    is_udp: false                               # TCP (default) vs UDP
    write_timeout_sec: 30                       # Write timeout
    ssl_cert: "/certs/syslog_server.pem"       # Optional SSL cert
    ssl_key: "/certs/syslog_server.key"        # Optional SSL key
    mutual_tls_cert: "/certs/client_ca.pem"    # Optional mTLS
```

#### Step 3: Configure syslog output to send messages to a local listener

This step will depend on the type of syslog daemon you are using (syslog, rsyslog, syslog-ng, etc.) Within the daemon configuration file, configure the desired facility(-ies) to direct to the local listener. In the following example, we configured `auth` and `authpriv` events to write to both `/var/log/audit.log` and `127.0.0.1:1514`.

```
auth,authpriv.*			/var/log/auth.log
auth,authpriv.*			@@127.0.0.1:1514
```

After applying the appropriate configuration, restart the syslog daemon.

#### Step 4: Confirm that syslog messages are sent to the correct location

Utilizing a tool like `netcat`, you can listen on the appropriate port to confirm that messages are being sent. The following command will spawn a `netcat` listener on port 1514:

```
nc -l -p 1514
```

#### Step 5: Run the LimaCharlie Adapter

Execute the binary Adapter with the syslog configuration file in order to start the LimaCharlie listener. If started correctly, you should see the following messages in `stdout`:

```
DBG <date>: usp-client connecting
DBG <date>: usp-client connected
DBG <date>: listening for connections on :1514
```

Double-check the LimaCharlie Sensors list, and you should see the text adapter with the respective hostname sending `Syslog` events.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

In LimaCharlie, an Organization ID (OID) is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.