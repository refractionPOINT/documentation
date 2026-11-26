# OpenTelemetry Collector Fleets

!!! warning "Beta"
    Collector fleets are in beta. The console pages are behind a feature flag, and the OpAMP hostname of each site may still change. Always take the URLs from the fleet's **Setup** tab or from `limacharlie org urls`, never from this page.

A collector fleet lets LimaCharlie manage the configuration of [OpenTelemetry Collectors](https://opentelemetry.io/docs/collector/) running on your hosts. Each collector connects to LimaCharlie over [OpAMP](https://opentelemetry.io/docs/specs/opamp/), the OpenTelemetry agent management protocol. LimaCharlie sends it the collector configuration that matches the host, and the collector sends everything it collects back to LimaCharlie. Each collector shows up as its own sensor.

You write the configuration once in LimaCharlie, and every matching collector applies it within one check-in. Changing it later needs no login on the hosts.

A fleet is a [webhook adapter](webhook-adapter.md) with an `opamp` block. The data path is the webhook's [OTLP ingestion](otel-webhook.md), so events have the same format, and the fleet's configuration lives in the webhook's `cloud_sensor` record. Permissions (`cloudsensor.get`, `cloudsensor.set`), Infrastructure as Code, Git Sync and Hive secrets work on it like on any other webhook.

The full list of fields, limits and allowed components is in the [fleet configuration reference](otel-collector-fleet-reference.md).

## Fleet modes

A fleet runs in one of two modes, set with `opamp.mode` or **Fleet mode** on the Configs tab:

| Mode | `opamp.mode` | Where collectors may send data | Price |
|---|---|---|---|
| LimaCharlie only | `limacharlie` (the default, also when absent) | LimaCharlie only | Included |
| Any destination | `any_destination` | LimaCharlie and any other backend | $0.75 per managed collector per month, billed per collector-day. Needs a paid plan. |

### LimaCharlie only

A managed collector sends its data to LimaCharlie and nowhere else. LimaCharlie enforces this in four places:

1. **Fleet configs contain no exporters.** You write receivers, processors, connectors and pipelines. LimaCharlie adds its own exporter to every pipeline when it renders the config for a collector. Saving a config that has an `exporters` section, an unknown component, or a `${...}` reference fails with an error naming the config and the setting.
2. **The effective config is checked.** Every collector reports the configuration it actually runs, which includes any local configuration files on the host. If that configuration sends data anywhere other than this webhook, or sends the collector's own telemetry somewhere, LimaCharlie marks the collector **Blocked** and stops sending it configurations. It keeps running whatever it runs, and the console shows why it is blocked.
3. **A collector must report its effective config and accept remote config.** One that does not is blocked until its supervisor turns both on.
4. **Bindplane BDOT v1 collectors are blocked.** BDOT v1 reports only its main configuration file, so files passed with extra `--config` flags cannot be checked. It is blocked with `BDOT v1 collectors require a paid fleet (mode any_destination)`.

Exporters that keep data on the host are allowed in local files: `debug` (stdout, stderr or local files) and `nop`.

### Any destination (paid)

In this mode, collectors may send data to other backends as well as to LimaCharlie:

- Fleet configs may define their own exporters, of any type, and list them in pipelines.
- A pipeline with no exporters still goes to LimaCharlie only. To send a pipeline both to your own exporters and to LimaCharlie, list the placeholder exporter `limacharlie` in it. Do not define it under `exporters`: LimaCharlie replaces it with its own exporter.
- Configs may use `${env:NAME}` and `${file:/absolute/path}` references, for example for a backend's API key. Every other `${...}` reference is still refused.
- Configs may define the authenticator extensions exporters use: `basicauth`, `bearertokenauth`, `oauth2client`, `headers_setter` and `sigv4auth`.
- The effective config is not checked for where data goes. A collector is blocked only if it does not report its effective config or accept remote config, or if the config it reports is not valid YAML.
- BDOT v1 collectors are allowed.

The receivers, processors and connectors you can use are the same in both modes. See the [reference](otel-collector-fleet-reference.md#any-destination-mode) for every rule.

A paid plan means an organization whose sensor quota is above 2. Saving a fleet in this mode in an organization without one fails with `paid plan required for fleet mode any_destination`. If an organization stops being on a paid plan, its paid fleets behave as **LimaCharlie only**: collectors that send data elsewhere, and BDOT v1 collectors, are blocked with `paid plan required for this fleet mode`, no fleet collector receives new configs, and nothing is billed. They are checked again and unblocked once the plan is back. While LimaCharlie cannot read the plan, the reason is `paid plan could not be verified for this fleet mode; retrying`, and it clears on its own.

#### Billing

A paid fleet costs $0.75 per managed collector per month, counted as collector-days at $0.025 each. A collector counts for a day when it checks in that day, is not blocked, and has reported its effective config. A collector that is blocked or offline all day, and every collector of a **LimaCharlie only** fleet, is not counted. The organization's usage shows the count as **Managed OpenTelemetry collectors**.

## Supported collectors

| Collector | How it connects | Notes |
|---|---|---|
| Upstream `otelcol-contrib` under the upstream `opampsupervisor`, v0.165.0 | OpAMP over HTTPS (polling) | The reference setup. The console's setup steps install it. Both fleet modes. |
| Bindplane BDOT v2, under its supervisor | OpAMP over HTTPS | Use the same `supervisor.yaml` with `agent.executable` pointing at the BDOT binary. Both fleet modes. |
| Bindplane BDOT v1 (1.x) | OpAMP over WebSocket (`wss://`) | **Any destination fleets only.** Needs the site's OpAMP host. Local `--config` files are not visible: the console marks these collectors with `lc.collector.local_config_visible: false`. |

Other collectors built on the OpenTelemetry Collector work under `opampsupervisor` if they include the components your configs use. LimaCharlie picks the exporter name from the version the collector reports: `otlp_http/limacharlie` for official OpenTelemetry Collector releases from v0.144.0 on, `otlphttp/limacharlie` for anything older or unknown.

## How it works

1. You create the fleet: a webhook with `opamp.enabled: true` and an ordered list of named configs, each with a selector.
2. The supervisor on each host connects to the fleet's OpAMP endpoint with the webhook secret and describes the collector: `service.name`, `service.version`, `os.type`, `host.name` and any attribute you add.
3. LimaCharlie checks the effective config the collector reports. If it is clean, LimaCharlie picks the first config whose selector matches the collector's attributes.
4. It adds the LimaCharlie exporter and a resource processor that tags every record with the collector's instance ID, host name and config name, and sends the result.
5. The supervisor applies it and reports `APPLIED`, or `FAILED` with the collector's error. A config that failed is not sent again until you change it.
6. On every check-in (30 seconds by default) the collector reports changes, and receives the new config if you edited it.

Fleet state (status, health, effective config) is kept for 7 days after a collector was last seen. A collector silent for longer drops out of the list and registers again if it comes back.

## Create a fleet

### In the console

Open **Sensors > OpenTelemetry Fleets** and click **New fleet**. Give it a name (lowercase letters, digits, dots, dashes and underscores) and pick an installation key. The console creates the webhook with:

- a random 256-bit secret,
- `opamp.enabled: true` and no configs yet,
- a mapping that makes each collector its own sensor (see [Collectors as sensors](#collectors-as-sensors)).

You need `cloudsensor.set` and `ikey.list`.

### With the CLI or Infrastructure as Code

The same record, as YAML:

```yaml
sensor_type: webhook
webhook:
  secret: <A LONG RANDOM SECRET>        # or hive://secret/<name>
  client_options:
    identity:
      oid: <YOUR OID>
      installation_key: <INSTALLATION KEY>
    platform: json
    hostname: otel-fleet
    sensor_seed_key: otel-fleet
    mapping:
      sensor_key_path: resource/lc.collector.instance_uid
      sensor_hostname_path: resource/lc.collector.host_name
      event_type_path: otel_type
  opamp:
    enabled: true
    mode: limacharlie   # or any_destination (paid)
    configs:
      - name: linux-hosts
        selector:
          os.type: linux
        config: |
          receivers:
            file_log:
              include: [/var/log/syslog]
          processors:
            batch: {}
          service:
            pipelines:
              logs:
                receivers: [file_log]
                processors: [batch]
```

```bash
limacharlie hive set --hive-name cloud_sensor --key otel-fleet --input-file otel-fleet.yaml --enabled
```

`--enabled` matters: a new `cloud_sensor` record is created disabled otherwise, and a disabled webhook serves nothing. The hive checks the whole `opamp` block when you save. A secret is required while `opamp.enabled` is `true`, and `mode: any_destination` needs a paid plan.

## Connect collectors

The fleet's **Setup** tab shows the supervisor configuration with the right URL and secret filled in, and the install commands for each platform. The steps below are the same.

The OpAMP endpoint is:

```text
https://<hooks-domain>/<OID>/<FLEET NAME>/v1/opamp
```

`<hooks-domain>` is `hooks` in `limacharlie org urls`. The supervisor authenticates with `Authorization: Bearer <secret>`. The secret in the URL path is refused for OpAMP.

Hosts need outbound HTTPS to the hooks domain, both for OpAMP and for the data the collector sends.

### Supervisor configuration

On Linux, save this as `/etc/opampsupervisor/config.yaml`:

```yaml
server:
  endpoint: "https://<hooks-domain>/<OID>/<FLEET NAME>/v1/opamp"
  headers:
    Authorization: "Bearer <SECRET>"
capabilities:
  accepts_remote_config: true
  reports_effective_config: true
  reports_health: true
  # Lets the fleet's check-in interval apply to this collector.
  accepts_opamp_connection_settings: true
  reports_own_metrics: false
  reports_own_logs: false
  reports_own_traces: false
agent:
  executable: "/usr/bin/otelcol-contrib"
storage:
  directory: "/var/lib/opampsupervisor"
```

`accepts_remote_config` and `reports_effective_config` are required: without them the collector is blocked. The collector's own telemetry stays off because LimaCharlie offers no destination for it.

On Windows, the file is `C:\Program Files\OpenTelemetry OpAMP Supervisor\config.yaml`, with:

```yaml
agent:
  executable: "C:\\Program Files\\OpenTelemetry OpAMP Supervisor\\otelcol-contrib.exe"
storage:
  directory: "C:\\ProgramData\\opampsupervisor"
```

In Docker (see below), use:

```yaml
agent:
  executable: "/usr/local/bin/otelcol-contrib"
storage:
  directory: "/home/opampsupervisor/storage"
```

To give the collector attributes that selectors can match, add them under `agent.description`:

```yaml
agent:
  executable: "/usr/bin/otelcol-contrib"
  description:
    non_identifying_attributes:
      deployment.environment: prod
      team: payments
```

### Install on Linux (Debian or Ubuntu)

```bash
VERSION=0.165.0
ARCH=amd64  # arm64 on ARM hosts
BASE=https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download
COLLECTOR=otelcol-contrib_${VERSION}_linux_${ARCH}.deb
SUPERVISOR=opampsupervisor_${VERSION}_linux_${ARCH}.deb
curl -fsSLO "$BASE/v$VERSION/$COLLECTOR"
curl -fsSLO "$BASE/cmd%2Fopampsupervisor%2Fv$VERSION/$SUPERVISOR"
echo "$(curl -fsSL "$BASE/v$VERSION/$COLLECTOR.sha256")  $COLLECTOR" | sha256sum -c -
echo "$(curl -fsSL "$BASE/cmd%2Fopampsupervisor%2Fv$VERSION/$SUPERVISOR.sha256")  $SUPERVISOR" | sha256sum -c -
sudo dpkg -i "$COLLECTOR" "$SUPERVISOR"
# The supervisor starts the collector itself: turn off the collector package's own service.
sudo systemctl disable --now otelcol-contrib
# Save the supervisor configuration as /etc/opampsupervisor/config.yaml, then:
sudo systemctl enable --now opampsupervisor
```

The supervisor runs as the `opampsupervisor` user. To read files it cannot open, such as `/var/log/syslog`, add that user to their group, for example `sudo usermod -aG adm opampsupervisor`.

### Install on Windows

In PowerShell, as Administrator:

```powershell
$Version = "0.165.0"
$Base = "https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download"
$Dir = "C:\Program Files\OpenTelemetry OpAMP Supervisor"
Set-Location $env:TEMP
$Files = @{
  "opampsupervisor.msi" = "$Base/cmd%2Fopampsupervisor%2Fv$Version/opampsupervisor_${Version}_windows_x64.msi"
  "otelcol-contrib.tar.gz" = "$Base/v$Version/otelcol-contrib_${Version}_windows_amd64.tar.gz"
}
foreach ($f in $Files.Keys) {
  Invoke-WebRequest $Files[$f] -OutFile $f
  Invoke-WebRequest "$($Files[$f]).sha256" -OutFile "$f.sha256"
  $Expected = (Get-Content "$f.sha256" -Raw).Trim()
  if ((Get-FileHash $f -Algorithm SHA256).Hash -ne $Expected) { throw "Checksum mismatch: $f" }
}
Start-Process msiexec.exe -Wait -ArgumentList '/i', 'opampsupervisor.msi', '/qn'
tar -xzf otelcol-contrib.tar.gz -C $Dir otelcol-contrib.exe
# Save the supervisor configuration as C:\Program Files\OpenTelemetry OpAMP Supervisor\config.yaml, then:
Restart-Service opampsupervisor
```

### Run in Docker

The upstream supervisor image has no collector in it, so build one that adds it:

```dockerfile
FROM ghcr.io/open-telemetry/opentelemetry-collector-releases/opentelemetry-collector-contrib:0.165.0 AS collector
FROM ghcr.io/open-telemetry/opentelemetry-collector-releases/opentelemetry-collector-opampsupervisor:0.165.0
COPY --from=collector /otelcol-contrib /usr/local/bin/otelcol-contrib
RUN mkdir -p /home/opampsupervisor/storage
```

Save the supervisor configuration as `supervisor.yaml` next to the Dockerfile, then:

```bash
docker build -t lc-otel-supervisor:0.165.0 .
docker run -d --name lc-otel-supervisor --restart unless-stopped \
  -v "$PWD/supervisor.yaml:/etc/opampsupervisor/config.yaml:ro" \
  -v lc-otel-supervisor-data:/home/opampsupervisor/storage \
  lc-otel-supervisor:0.165.0 --config=/etc/opampsupervisor/config.yaml
```

To read host files, mount them read-only, for example `-v /var/log:/var/log:ro`.

### Bindplane BDOT v2

BDOT v2 runs under the same OpAMP supervisor. Use the supervisor configuration above with `agent.executable` pointing at the BDOT collector binary, and the `https://` endpoint: the hooks domain does not accept WebSocket. The `Authorization: Secret-Key <secret>` header that the Bindplane installer writes is accepted as well as `Bearer`.

### Bindplane BDOT v1

BDOT v1 collectors are supported only in **Any destination** fleets. In a **LimaCharlie only** fleet they are blocked.

BDOT v1 has its own OpAMP client, which only speaks WebSocket, and does not use the supervisor. It connects to the site's OpAMP host, not the hooks domain. The Setup tab of a paid fleet shows the full `manager.yaml`. Set these two keys in it:

```yaml
endpoint: "wss://<opamp-host>/<OID>/<FLEET NAME>/v1/opamp"
secret_key: "<SECRET>"
```

Keep the `agent_id` and `labels` the file already has, then restart the collector. BDOT v1 sends `Authorization: Secret-Key <secret>`, which the fleet accepts.

BDOT v1 receives the full collector configuration, which replaces its `collector.yaml`. It reports no health, so the console shows its health as unknown. Its labels reach LimaCharlie as the `service.labels` attribute, which selectors can match (`service.labels: "*env=prod*"`).

A collector appears on the **Collectors** tab as soon as it connects. It runs nothing new until a config matches it.

## Write fleet configs

Open the fleet's **Configs** tab. Each config has a name, a selector and the collector YAML. The order matters: each collector gets the first config, from the top, whose selector matches.

- A selector lists attributes that must all match. A value matches exactly, or as a pattern where `*` matches any text and `?` one character: `host.name: web-*`. An empty selector matches every collector, which makes it a good last entry.
- Collectors report `service.name`, `service.version`, `service.instance.id`, `os.type` (`linux`, `windows`, `darwin`), `os.description`, `host.arch`, `host.name`, and whatever you set under `agent.description` in the supervisor configuration.
- In a **LimaCharlie only** fleet, leave pipeline `exporters` empty. LimaCharlie sends every pipeline to itself. A pipeline may list connectors as exporters, to route data into another pipeline.

An example for Windows hosts, placed before a catch-all:

```yaml
receivers:
  windows_event_log/security:
    channel: security
  windows_event_log/system:
    channel: system
  host_metrics:
    collection_interval: 60s
    scrapers:
      cpu: {}
      memory: {}
      filesystem: {}
processors:
  batch: {}
  resource_detection:
    detectors: [system]
service:
  pipelines:
    logs:
      receivers: [windows_event_log/security, windows_event_log/system]
      processors: [resource_detection, batch]
    metrics:
      receivers: [host_metrics]
      processors: [batch]
```

In an **Any destination** fleet, a config can send to your own backend too. This one sends logs both to an OTLP backend of your own and to LimaCharlie, and host metrics to LimaCharlie only:

```yaml
receivers:
  file_log:
    include: [/var/log/syslog]
  host_metrics:
    scrapers:
      cpu: {}
      memory: {}
exporters:
  otlp_http/archive:
    endpoint: https://otel.example.com
    headers:
      Authorization: "Bearer ${env:ARCHIVE_TOKEN}"
processors:
  batch: {}
service:
  pipelines:
    logs:
      receivers: [file_log]
      processors: [batch]
      exporters: [otlp_http/archive, limacharlie]
    metrics:
      receivers: [host_metrics]
      processors: [batch]
```

`${env:ARCHIVE_TOKEN}` is read from the collector's environment on the host, so the token never goes through LimaCharlie. LimaCharlie's resource attributes are added only to the copy it receives, not to the data sent to your backend.

Click **Save configs**. If LimaCharlie refuses the configs, its message names the config and the setting at fault, for example `opamp: config "windows-hosts": exporters: not allowed, LimaCharlie adds its own exporter (pipelines without exporters are sent to LimaCharlie)`. Collectors pick up the change at their next check-in.

**Manage collectors** turns the fleet off and on (`opamp.enabled`). While it is off, collectors are refused and keep running the configuration they last received.

The [reference](otel-collector-fleet-reference.md) lists every allowed receiver, processor, connector and extension, and what LimaCharlie adds to each config.

### Check-in interval

Collectors check in every 30 seconds by default. A config change reaches a collector at its next check-in, and its status one check-in later. To change the interval, set **Check-in interval** on the Configs tab (`opamp.heartbeat_seconds`, 5 to 3600 seconds). Shorter means faster changes and more requests.

It reaches only collectors whose supervisor has `accepts_opamp_connection_settings: true`. LimaCharlie offers the interval as OpAMP connection settings, which carry the same endpoint and `Authorization` header, since the supervisor replaces its own headers with offered ones. Removing the setting offers the 30-second default back to collectors still running an interval it offered.

BDOT v1 collectors keep their WebSocket open, and configuration changes are pushed to them right away. The check-in interval does not apply to them.

## Collectors as sensors

LimaCharlie tags every record a managed collector sends with resource attributes:

| Attribute | Value |
|---|---|
| `lc.collector.instance_uid` | The collector's OpAMP instance ID |
| `lc.collector.host_name` | The host name the collector reported in its description |
| `lc.collector.config` | The name of the config it runs |
| `host.name` | The same host name, added only if the record has no `host.name` of its own |

The fleet's mapping turns each collector into its own sensor:

```yaml
mapping:
  sensor_key_path: resource/lc.collector.instance_uid
  sensor_hostname_path: resource/lc.collector.host_name
  event_type_path: otel_type
```

Each collector's sensor is named after the host the collector runs on, whatever `host.name` the records themselves carry, and `event_type_path: otel_type` sets the event type to `log`, `span`, `metric` or `opamp_status`. The console sets this mapping when it creates a fleet. Fleets created with `sensor_hostname_path: resource/host.name` keep working, but a record's own `host.name` then names the sensor.

[Fleet status events](#fleet-status-events) carry the same `lc.collector.*` resource attributes, so they appear on the collector's sensor next to its data.

OTLP sent directly to the fleet's webhook, by an SDK or a collector the fleet does not manage, has no `lc.collector.instance_uid`. It appears on the fleet's own sensor, the one named after `client_options.hostname`, and its own `host.name` does not rename that sensor.

See [Ingesting OpenTelemetry Data via Webhook](otel-webhook.md#event-format) for the fields of each event.

## Fleet status events

When a collector's state changes, LimaCharlie adds an event to the fleet's webhook with `otel_type: opamp_status`:

| Field | Value |
|---|---|
| `otel_type` | `opamp_status` |
| `resource` | `lc.collector.instance_uid`, plus `lc.collector.host_name` and `host.name` when the collector reported a host name |
| `change` | `connected`, `config_applied`, `config_failed`, `blocked`, `unblocked`, `unhealthy` or `healthy` |
| `instanceUid` | The collector's instance ID |
| `hostName` | Its host name, when reported |
| `configName` | The config assigned to it |
| `configHash` | For `config_applied` and `config_failed`, the hash the collector reported. Otherwise the hash of the config assigned to it. |
| `error` | For `config_failed`, the collector's error. For `unhealthy`, its health error. |
| `blockedReason` | For `blocked`, why |

Empty fields are left out. A new collector gets `connected`, plus `blocked` if it starts blocked. Each change is normally sent once, and can rarely arrive twice after a network error. If the webhook's queue is full, status events are dropped rather than delaying configurations.

Every config apply restarts the collector, which reports a short `unhealthy` followed by `healthy`. Do not alert on `unhealthy` alone.

This rule reports collectors that refuse their config or get blocked:

```yaml
detect:
  event: opamp_status
  op: or
  rules:
    - op: is
      path: event/change
      value: config_failed
    - op: is
      path: event/change
      value: blocked
respond:
  - action: report
    name: otel-collector-needs-attention
```

It relies on `event_type_path: otel_type`. Without it, match `event/otel_type` with `value: opamp_status` instead of `event:`.

## The console

### A fleet

**Sensors > OpenTelemetry Fleets** lists the organization's fleets, with their status, number of configs, collectors online out of total, and how many are blocked or failed. Open a fleet to get three tabs:

- **Collectors**: every collector, with its host, status (Online, Offline or Blocked with its reason), health, assigned config, config status (Applied, Applying, Failed with its error, or No match), version and last seen. Filters and search run over every collector of the fleet, read to the last page first. Click a collector to see its attributes, capabilities and effective configuration (what it really runs, with the webhook secret redacted). **Forget collector** removes an offline collector from the fleet. If it connects again, it comes back as a new collector. Its sensor and events stay.
- **Configs**: the ordered configs, **Fleet mode**, **Manage collectors** and **Check-in interval**. **Any destination** can only be picked in an organization on a paid plan. In a paid fleet whose organization is no longer on one, the console asks you to switch back to **LimaCharlie only** before it saves. Saving writes the whole record. If someone else saved the fleet after you opened it, the console refuses the save and keeps your edits until you reload.
- **Setup**: the supervisor configuration for Linux, Windows and Docker, the install commands, the base URL for sending OTLP directly and, in paid fleets, the BDOT v1 `manager.yaml`. The secret is masked until you reveal it. If it is a `hive://secret/` reference, showing it needs `secret.get`.

A collector blocked because of the fleet mode or the plan gets an explanation next to its reason in the collector drawer.

A collector is online when it checked in within three check-in intervals.

### All organizations

The **OpenTelemetry Fleets** link in the top navigation lists the fleets of every organization you can access, or of the organizations you pick. It shows each fleet's counts and one table with every collector, its organization and fleet. Organizations where you lack `cloudsensor.get` are left out and listed as such. The table, its filters and its counts open once every organization and fleet has been read, so they always cover everything. Organizations or fleets that could not be read are named with the error.

## Fleet API

The fleet's collectors are available from the REST API. The fleet's configuration is the webhook's `cloud_sensor` record, read and written through Hive.

| Method and path | Permission | Returns |
|---|---|---|
| `GET /v1/otel/{oid}/{hook}/collectors?limit=&cursor=` | `cloudsensor.get` | `collectors` (most recently seen first, no effective config), `next_cursor` (empty on the last page) and `total`. `limit` is 1 to 500, 100 by default. |
| `GET /v1/otel/{oid}/{hook}/collectors/{uid}` | `cloudsensor.get` | `collector`, with `effective_config` |
| `DELETE /v1/otel/{oid}/{hook}/collectors/{uid}` | `cloudsensor.set` | Forgets the collector, and writes an `otel_collector_delete` entry in the audit log |

The host is `api.limacharlie.io`. `{hook}` is the fleet name and `{uid}` the 32-character hex instance ID. An unknown collector is a `404`. With the CLI:

```bash
limacharlie api 'otel/{oid}/otel-fleet/collectors?limit=500'
limacharlie api -X DELETE 'otel/{oid}/otel-fleet/collectors/<uid>'
```

A collector:

```json
{
  "instance_uid": "019a1b2c3d4e5f60718293a4b5c6d7e8",
  "host_name": "web-01",
  "attributes": {"service.name": "otelcol-contrib", "service.version": "0.165.0", "os.type": "linux", "host.name": "web-01"},
  "agent_version": "0.165.0",
  "online": true,
  "first_seen": 1795215199000,
  "last_seen": 1795215230000,
  "healthy": true,
  "health_status": "StatusOK",
  "health_error": "",
  "assigned_config": "linux-hosts",
  "assigned_hash": "ab12...",
  "remote_config_status": "APPLIED",
  "remote_config_hash": "ab12...",
  "remote_config_error": "",
  "blocked_reason": "",
  "capabilities": ["ReportsStatus", "AcceptsRemoteConfig", "ReportsEffectiveConfig", "ReportsHealth", "AcceptsOpAMPConnectionSettings"]
}
```

Times are Unix milliseconds. `remote_config_status` is `UNSET`, `APPLYING`, `APPLIED` or `FAILED`.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| The supervisor logs `401` | Wrong or missing secret. Check the `Authorization: Bearer` header, and that the secret is not in the URL path. |
| The supervisor logs `403` | The fleet does not exist, or **Manage collectors** is off (`opamp.enabled: false`). |
| The supervisor logs `400` about WebSocket or `Content-Type` | The endpoint starts with `ws://` or `wss://`. The upstream supervisor needs the `https://` URL. |
| `429` | The fleet already tracks 50,000 collectors. Forget offline ones or use another fleet. |
| `503` | Temporary. The supervisor retries on its own. |
| Saving fails with `paid plan required for fleet mode any_destination` | The organization is not on a paid plan (sensor quota above 2), or its plan could not be read. Raise the sensor quota, or use `mode: limacharlie`. |
| Blocked: `BDOT v1 collectors require a paid fleet (mode any_destination)` | BDOT v1 joined a **LimaCharlie only** fleet. Switch the fleet to **Any destination**, or connect the collector to a paid fleet. |
| Blocked: `paid plan required for this fleet mode` | The fleet is in **Any destination** mode but the organization is no longer on a paid plan. Raise the sensor quota, or switch the fleet to **LimaCharlie only** and remove the other destinations. |
| Blocked: `paid plan could not be verified for this fleet mode; retrying` | LimaCharlie could not read the organization's plan. It clears on its own once the plan is read. |
| Blocked: `collector does not accept remote config` or `does not report its effective config` | Set `accepts_remote_config: true` and `reports_effective_config: true` in `supervisor.yaml` and restart the supervisor. |
| Blocked: `exports to non-LimaCharlie destination: exporters::<id>` | In a **LimaCharlie only** fleet, a local configuration file on the host adds an exporter. Remove it (only `debug` and `nop` may stay), or switch the fleet to **Any destination**. |
| Blocked: `LimaCharlie exporter changed: ...` | A local file changes LimaCharlie's exporter (endpoint, TLS, proxy, extra keys). Remove the override. |
| Blocked: `own telemetry exported: service::telemetry::...` | The collector's own logs, metrics or traces are sent somewhere. Keep `reports_own_*: false` and remove `service::telemetry` readers or processors from local files. |
| Blocked: `opamp extension ...` or `extension not allowed: ...` | A local file adds an extension LimaCharlie does not allow, or changes the supervisor's own `opamp` extension. |
| Config status **Failed** | The collector refused the config. The error is on the collector's row, often a component the binary does not include or a file it cannot read. The same config is not sent again until you change it. |
| **No match** | No selector matches the collector. Compare its attributes in the collector drawer with your selectors, or add a last config with an empty selector. |
| Collector online but no data | Check that the config's receivers produce data on that host (file permissions for `file_log`, for example), and that the host reaches the hooks domain over HTTPS. |

After you fix a blocked collector's local files, it is checked again at its next check-in and gets `unblocked`.

## Related articles

- [Fleet configuration reference](otel-collector-fleet-reference.md)
- [Ingesting OpenTelemetry Data via Webhook](otel-webhook.md)
- [Webhook Adapter](webhook-adapter.md)
- [Cloud-Managed Adapters](../cloud-managed.md)
