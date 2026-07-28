# Syslog

Syslog is a protocol and a common log format. It sends events to a central location for storage. On \*nix systems, Syslog usually writes to set locations, such as `/var/log`. You can configure the LimaCharlie Adapter as a Syslog endpoint that collects events over TCP or UDP.

LimaCharlie can also ingest Syslog data through other data platforms, such as an S3 bucket.

Syslog events appear in LimaCharlie as the `text` platform.

The [Log Collection Guide](../../log-collection-guide.md) gives more detail about syslog collection.

## Adapter Deployment

Syslog is common, and many methods can ingest it in text/log formats and in streaming formats. For non-streaming methods, use the applicable Adapter type, such as [S3](s3.md) or [GCP](google-cloud-pubsub.md).

### Syslog-specific Configurations

All Adapters share the [common client configuration options](../usage.md). A syslog Adapter also has these unique configuration options:

- `port`: port to listen for syslog from.
- `iface`: the interface name to listen for new connections/packets from, defaults to all.
- `is_udp`: if `true`, listen over UDP instead of TCP. Cannot be combined with SSL/TLS.
- `ssl_cert`: path to a file with the SSL cert to use to receive logs over TCP.
- `ssl_key`: path to a file with the SSL key to use to receive logs over TCP.
- `mutual_tls_cert`: path to a CA certificate file for mutual TLS client authentication.
- `write_timeout_sec`: number of seconds before a write to LimaCharlie times out (default: 600).

### Collecting Syslog via Docker

The example below shows how to configure a Docker container as a syslog Adapter.

```bash
docker run --rm -it -p 1514:1514 refractionpoint/lc-adapter:latest syslog port=1514 \
  client_options.identity.installation_key=e9a3bcdf-efa2-47ae-b6df-579a02f3a54d \
  client_options.identity.oid=8cbe27f4-bfa1-4afb-ba19-138cd51389cd \
  client_options.platform=text "client_options.mapping.parsing_grok=%{DATESTAMP:date} %{HOSTNAME:host} %{WORD:exe}\[%{INT:pid}\]: %{GREEDYDATA:msg}" \
  client_options.sensor_seed_key=testclient1 \
  client_options.mapping.rename_only=true \
  "client_options.mapping.mapping[0].src_field=host" \
  "client_options.mapping.mapping[0].dst_field=syslog_hostname"
```

The example uses these options:

- `docker run --rm`: run a container and delete its contents when the container stops.
- `-it`: make the container interactive, so that you can stop it with ctrl-c.
- `-p 1514:1514`: let the container listen on port `1514` on the local host and use the same port in the container.
- `refractionpoint/lc-adapter:latest`: the name of the public container from LimaCharlie.
- `syslog`: the method that the Adapter uses to collect data locally. The `syslog` value operates as a syslog endpoint on the TCP port that you specify.
- `port=1514`: the TCP port that the Adapter listens on. The default is a normal TCP connection (not SSL), but SSL options exist.
- `client_options.identity.installation_key=....`: the Installation Key from LimaCharlie.
- `client_options.identity.`OID`=....`: the Organization ID from LimaCharlie that the installation key above belongs to.
- `client_options.platform=text`: the type of data that this adapter receives. For syslog, this is `text` lines.
- `client_options.mapping.parsing_grok=....`: the grok expression that shows how to interpret the text lines and how to convert them to JSON.
- `client_options.sensor_seed_key=....`: the value that identifies this instance of the Adapter. Record this value. It lets you re-use the Sensor of this Adapter if you must re-install the Adapter.
- `client_options.mapping.rename_only=true`: rename only the field in the mapping below, and keep the other original fields.
- `client_options.mapping.mapping[0].src_field=....`: the source field of the first mapping record.
- `client_options.mapping.mapping[0].dst_field=....`: the destination field of the first mapping record.

To test the Adapter from the same Debian machine as the container, pipe the syslog to the container:

```text
journalctl -f -q | netcat 127.0.0.1 1514
```

### Collecting Syslog via Binary Adapter

You can deploy the LimaCharlie binary Adapter as a syslog listener. With this option, you can send many syslog outputs to one listener and ingest many types of events with one Adapter.

#### Step 1: Create an installation key

Use a unique installation key for this deployment, with a `syslog` Tag. Tags let you separate this data in rules and outputs.

#### Step 2: Create an Adapter config file

LimaCharlie usually ingests syslog events as `text`, but the events often have a specific structure. A config file lets you manage the regex string that extracts the necessary fields from the syslog output.

Use the example config file below as a start. You can change the regex to match your messages.

```yaml
syslog:
  port: 1514
  iface: "0.0.0.0"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_SYSLOG"
    hostname: "syslog-adapter"
    platform: "text"
    sensor_seed_key: "syslog-collector"
    mapping:
      parsing_grok:
        message: "^<%{INT:pri}>%{SYSLOGTIMESTAMP:timestamp}\\s+%{HOSTNAME:hostname}\\s+%{WORD:tag}(?:\\[%{INT:pid}\\])?:\\s+%{GREEDYDATA:message}"
      sensor_hostname_path: "hostname"
      event_type_path: "tag"
      event_time_path: "timestamp"
      event_time_timezone: "America/New_York"  # Required if logs use local time (SYSLOGTIMESTAMP has no timezone)
  # Optional syslog-specific configuration
  is_udp: false                               # TCP (default) vs UDP
  write_timeout_sec: 30                       # Write timeout
  ssl_cert: "/certs/syslog_server.pem"       # Optional SSL cert
  ssl_key: "/certs/syslog_server.key"        # Optional SSL key
  mutual_tls_cert: "/certs/client_ca.pem"    # Optional mTLS
```

#### Step 3: Configure syslog output to send messages to a local listener

This step depends on the syslog daemon that you use (syslog, rsyslog, syslog-ng, and others). In the daemon configuration file, send the necessary facilities to the local listener. The example below writes `auth` and `authpriv` events to `/var/log/audit.log` and to `127.0.0.1:1514`.

```text
auth,authpriv.*   /var/log/auth.log
auth,authpriv.*   @@127.0.0.1:1514
```

After you apply the configuration, restart the syslog daemon.

#### Step 4: Confirm that syslog messages are sent to the correct location

Use a tool such as `netcat` to listen on the port and confirm that the daemon sends messages. The command below starts a `netcat` listener on port 1514:

```text
nc -l -p 1514
```

#### Step 5: Run the LimaCharlie Adapter

Run the binary Adapter with the syslog configuration file to start the LimaCharlie listener. If the Adapter starts correctly, `stdout` shows these messages:

```text
DBG <date>: usp-client connecting
DBG <date>: usp-client connected
DBG <date>: listening for connections on :1514
```

Open the LimaCharlie Sensors list. The text adapter with the applicable hostname sends `Syslog` events.
