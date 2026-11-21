# OpenTelemetry Collector Fleet Configuration Reference

!!! warning "Beta"
    Collector fleets are in beta. See [OpenTelemetry Collector Fleets](otel-collector-fleets.md) for what they are and how to set one up.

This page lists every field of a fleet, the rules LimaCharlie applies to fleet configs, what it adds to them, and what blocks a collector.

## The `webhook.opamp` block

A fleet is the `opamp` block of a `cloud_sensor` webhook record:

```yaml
sensor_type: webhook
webhook:
  secret: <required while opamp.enabled is true>
  client_options: {}           # as for any webhook
  opamp:
    enabled: true
    mode: limacharlie          # optional: limacharlie (default) or any_destination
    heartbeat_seconds: 30      # optional
    configs:
      - name: linux-prod
        selector:
          os.type: linux
          deployment.environment: prod
        config: |
          receivers:
            file_log:
              include: [/var/log/syslog]
          service:
            pipelines:
              logs:
                receivers: [file_log]
```

| Field | Type | Rules |
|---|---|---|
| `enabled` | boolean | `true` serves the fleet's OpAMP endpoint. `false` answers `403` to collectors, which keep their last configuration. When `true`, `webhook.secret` must be set. |
| `mode` | string | `limacharlie` (the default, also when absent) or `any_destination`, the paid mode. Saving `any_destination` needs a paid plan, an organization with a sensor quota above 2. Saving the same paid fleet again unchanged, or turning it off, does not check the plan. |
| `heartbeat_seconds` | integer | Optional check-in interval offered to collectors, 5 to 3600. Absent or `0` keeps the supervisor's 30 seconds. |
| `configs` | list | Up to 100 entries, matched in order. |
| `configs[].name` | string | `[a-z0-9][a-z0-9_-]{0,63}`, unique in the fleet. |
| `configs[].selector` | map of string to string | Up to 32 keys. Keys and values up to 256 bytes, without control characters. Empty or absent matches every collector. |
| `configs[].config` | string | The collector configuration, in YAML, up to 256 KiB. See [Config rules](#config-rules). |

The hive validates the block whenever it is present, even while `enabled` is `false`, so a stored fleet can always be turned on. An error names the config and the path in it, for example:

```text
opamp: config "linux-prod": receivers::kafka: receiver type "kafka" is not allowed
```

## Selectors

A collector's attributes are its OpAMP agent description, identifying and non-identifying attributes merged (an identifying attribute wins when both have the same key). The upstream collector reports:

| Attribute | Example |
|---|---|
| `service.name` | `otelcol-contrib` |
| `service.version` | `0.165.0` |
| `service.instance.id` | A UUID |
| `os.type` | `linux`, `windows`, `darwin` |
| `os.description` | The OS name and version |
| `host.arch` | `amd64`, `arm64` |
| `host.name` | The host name |

Add your own under `agent.description` in `supervisor.yaml`. LimaCharlie adds two attributes of its own to Bindplane collectors, `lc.collector.flavor` (`bdot-v1` or `bdot-v2`) and, for BDOT v1, `lc.collector.local_config_visible: false`. Any `lc.collector.*` attribute a collector reports itself is dropped. Attribute values that are not strings (booleans, numbers) are compared as text. LimaCharlie keeps at most 128 attributes per collector, with keys up to 256 bytes and values up to 1024 bytes.

Matching:

- Every key in the selector must be present on the collector, and its value must match.
- A value matches exactly, or as a pattern: `*` matches any run of characters (including none) and `?` exactly one. Every other character, `[` and `\` included, matches itself. Matching is case sensitive.
- The first config, from the top, whose selector matches is the one the collector gets. If none matches, the collector gets nothing and its config status is **No match**.

## Config rules

In the default mode, a fleet config is the collector configuration without exporters. LimaCharlie allows only what is listed here. Anything else is refused when you save. The [Any destination mode](#any-destination-mode) relaxes some of these rules.

### YAML

- One YAML document, and it must be a mapping.
- No anchors, aliases, merge keys or custom tags. Plain scalar types only (string, integer, float, boolean, null).
- No duplicate keys, and no `::` in keys.
- No `${` and no `$$` anywhere. This blocks the collector's config providers (`${env:...}`, `${file:...}`, `${http://...}`) and its escaping.
- At most 256 KiB, 48 levels deep and 65,536 nodes.
- Component ids are `type` or `type/name`: the type is lowercase ASCII letters, digits and `_`, the name is ASCII letters, digits, `_`, `.` and `-`.

### Top-level keys

`receivers`, `processors`, `connectors`, `extensions` and `service`. `exporters` is refused: LimaCharlie adds its own. `service::pipelines` with at least one pipeline is required.

### Receivers

Both spellings are accepted where the collector renamed a component. The new names are the ones collector v0.165.0 uses.

| Receiver | Signals |
|---|---|
| `otlp` | logs, metrics, traces |
| `file_log` (`filelog`) | logs |
| `journald` | logs |
| `syslog` | logs |
| `tcp_log` (`tcplog`) | logs |
| `udp_log` (`udplog`) | logs |
| `windows_event_log` (`windowseventlog`) | logs |
| `k8s_events` | logs |
| `k8s_objects` (`k8sobjects`) | logs |
| `host_metrics` (`hostmetrics`) | metrics |
| `prometheus` | metrics |
| `kubelet_stats` (`kubeletstats`) | metrics |
| `docker_stats` | metrics |
| `iis` | metrics |
| `nginx` | metrics |
| `apache` | metrics |

A receiver used in a pipeline of a signal it does not produce is refused.

### Processors

| Processor | Signals |
|---|---|
| `batch`, `memory_limiter`, `attributes`, `resource`, `filter`, `transform`, `redaction`, `groupbyattrs` | all |
| `resource_detection` (`resourcedetection`) | all |
| `k8s_attributes` (`k8sattributes`) | all |
| `probabilistic_sampler` | logs, traces |
| `tail_sampling` | traces |
| `cumulative_to_delta` (`cumulativetodelta`) | metrics |
| `delta_to_rate` (`deltatorate`) | metrics |
| `metrics_transform` (`metricstransform`) | metrics |

The id `resource/limacharlie` is reserved for LimaCharlie's own processor.

### Connectors

| Connector | In | Out |
|---|---|---|
| `forward`, `routing` | any signal | the same signal |
| `count`, `sum`, `signal_to_metrics` (`signaltometrics`) | any signal | metrics |
| `span_metrics` (`spanmetrics`) | traces | metrics |

### Extensions

| Extension | Restriction |
|---|---|
| `health_check` | `endpoint` must be `localhost`, `127.0.0.1` or `::1` (with an optional port) |
| `file_storage` | `directory` must be an absolute local path (no UNC or network paths) |

`service::extensions` may list only extensions defined in the config, each once. The `opamp` extension is refused: the supervisor adds its own.

### Settings that read local files

Any setting ending in `_file` or `_files` is refused in every component, except the TLS ones (`ca_file`, `cert_file`, `key_file`, `client_ca_file`). Settings such as `bearer_token_file` or `password_file` read a local file and send its content to a server the config names.

### Receivers and processors with a fixed set of settings

These components can open outbound connections with local credentials, so only the settings listed are accepted:

- `prometheus`: `config.global` and `config.scrape_configs`, with `static_configs`, `file_sd_configs` and `kubernetes_sd_configs` (`role`, `namespaces`, `selectors`, `attach_metadata`), relabeling, `tls_config`, and credentials written in the config (`basic_auth`, `authorization`, `bearer_token`). Refused, among others: `scrape_config_files`, `target_allocator`, `api_server`, `http_headers`, `oauth2`, proxy settings and `*_file` credentials.
- `kubelet_stats`: every setting, but with `auth_type: serviceAccount` the `endpoint` must be unset (this node's kubelet) or a loopback address.
- `resource_detection`: the detectors `env`, `system`, `docker`, `ec2`, `ecs`, `eks`, `elastic_beanstalk`, `lambda`, `gcp`, `azure` and `aks`, and their settings. Refused: `openshift`, `consul` and every other detector, and the processor's own HTTP client settings.

### `service`

| Key | Allowed |
|---|---|
| `pipelines` | Pipelines `logs`, `metrics` or `traces`, optionally `/name`. Each has `receivers` (required), `processors` and `exporters`. |
| `extensions` | Extensions defined in the config |
| `telemetry` | Only `logs::level` (`debug`, `info`, `warn`, `error`, `dpanic`, `panic`, `fatal`), `metrics::level` (`none`, `basic`, `normal`, `detailed`) and `resource` |

A pipeline's `exporters` is either empty or lists only connectors defined in the config. The pipeline graph is checked too: every connector used as an exporter must feed a pipeline that receives from it with a compatible signal, `routing` targets must be pipelines fed by that connector, and connectors may not form a cycle. Every path through the graph ends in a pipeline without exporters, which LimaCharlie sends to itself.

### Any destination mode

With `mode: any_destination`, every rule above applies, with these differences:

| Rule | Any destination |
|---|---|
| `exporters` | Allowed, any type. Exporter ids `limacharlie` and `<type>/limacharlie` are reserved. |
| Pipeline `exporters` | Exporters and connectors defined in the config, and the placeholder `limacharlie`. A pipeline with no exporters goes to LimaCharlie only. |
| `${...}` | `${env:NAME}` (NAME is letters, digits and `_`, not starting with a digit, no `:-` default) and `${file:/absolute/path}` (or `C:\...`, `C:/...`; no UNC or network paths) in values. Every other scheme (`http`, `https`, `s3`, `yaml`, secret managers), the bare `${NAME}` form, nested references, `$$`, and any `${` in a key are refused. |
| Extensions | Also `basicauth`, `bearertokenauth`, `oauth2client`, `headers_setter` and `sigv4auth`, with any settings. `opamp` and `http_forwarder` stay refused. |
| Reserved names | Connectors named `<type>/limacharlie` and pipelines named `<signal>/limacharlie`, which LimaCharlie adds itself. |

The receivers, processors and connectors allowed, the settings of the fixed-shape components, the `*_file` rule for receivers and processors, and the `service::telemetry` limits are the same in both modes.

## What LimaCharlie adds

For each collector, LimaCharlie renders the selected config and adds:

```yaml
exporters:
  otlp_http/limacharlie:            # otlphttp/limacharlie on older or unknown versions
    endpoint: https://<hooks-domain>/<OID>/<FLEET NAME>
    headers:
      lc-secret: <the webhook secret>
    compression: gzip
    encoding: proto
processors:
  resource/limacharlie:
    attributes:
      - {key: lc.collector.instance_uid, value: <instance ID>, action: upsert}
      - {key: lc.collector.config, value: <config name>, action: upsert}
      - {key: host.name, value: <host.name the collector reported>, action: insert}
      - {key: lc.collector.host_name, value: <host.name the collector reported>, action: upsert}
```

- Every pipeline without exporters gets `exporters: [otlp_http/limacharlie]` and `resource/limacharlie` as its last processor. Pipelines that export to connectors are left as they are.
- The `host.name` and `lc.collector.host_name` lines are added only when the collector reported a host name. `insert` keeps a `host.name` the record already has, while `lc.collector.host_name` is always the collector's own host name.
- In the Any destination mode, your exporters are kept and LimaCharlie's is added next to them. A pipeline whose only exporter is the placeholder `limacharlie` is rendered like a pipeline without exporters. In a pipeline that lists the placeholder next to other exporters, the placeholder becomes the connector `forward/limacharlie`, which feeds an added `<signal>/limacharlie` pipeline: `resource/limacharlie`, then LimaCharlie's exporter. LimaCharlie's attributes are added only to that copy, never to the data your exporters send. `${env:...}` and `${file:...}` references are kept as written, and the collector expands them on its host.
- The exporter id is `otlp_http/limacharlie` for official OpenTelemetry Collector releases (`otelcol`, `otelcol-contrib`, `otelcol-k8s`, `otelcol-otlp`) from v0.144.0 on. Bindplane collectors get it based on the collector core version their release builds on. Everything else gets `otlphttp/limacharlie`, which collectors up to at least v0.165.0 still accept.
- The output is canonical: keys sorted, comments dropped. The same config gives the same bytes, and its SHA-256 is the config hash shown in the console. A change to the config, the secret or the exporter id changes the hash, and the collector gets the new config.

The supervisor merges this with its own configuration and any local `config_files`, and reports the result as the effective config.

## What blocks a collector

LimaCharlie checks the effective config each collector reports. In every mode, it blocks the collector, and stops sending it configs, when it does not have the `AcceptsRemoteConfig` or the `ReportsEffectiveConfig` capability.

In an **Any destination** fleet whose organization is on a paid plan, that is the only check besides the config itself: the collector is blocked only if the main effective config is missing, empty, larger than 1 MiB, or not a single YAML mapping (and the same for the unexpanded `raw` config when it is reported). Where it sends data is not checked, and BDOT v1 is allowed.

In a paid fleet whose organization is not on a paid plan, the fleet is checked as **LimaCharlie only**. A collector that only the paid mode would allow (it sends data elsewhere, or it is BDOT v1) gets the reason `paid plan required for this fleet mode`, or `paid plan could not be verified for this fleet mode; retrying` while the plan cannot be read. No collector of the fleet receives new configs until the plan is back.

In a **LimaCharlie only** fleet, a BDOT v1 collector is blocked with `BDOT v1 collectors require a paid fleet (mode any_destination)`. Any other collector is blocked when:

- the effective config is not valid YAML, is larger than 1 MiB, or has top-level keys other than `receivers`, `processors`, `exporters`, `connectors`, `extensions` and `service`;
- an exporter is anything other than LimaCharlie's own, `debug` (writing only to stdout, stderr or local files) or `nop`;
- LimaCharlie's exporter is changed: an `endpoint` other than this fleet's, per-signal endpoints, TLS, proxy, auth or any other key than transport tuning (`timeout`, buffer sizes, connection limits, `compression`, `encoding`, `retry_on_failure`, `sending_queue` with `file_storage` only, `keepalive`, `compression_params`), or there are two of them;
- a connector or processor is not allowed. Local files may also use `delta_to_cumulative`, `groupbytrace`, `interval`, `log_dedup`, `metric_start_time`, `metricsgeneration`, `span`, `span_pruning`, `unroll` and `geoip`, which fleet configs cannot;
- an extension is not allowed. Local files may also use `pprof`, `zpages`, `basicauth`, `bearertokenauth`, `oidc`, `headers_setter`, `host_observer`, `k8s_observer`, `docker_observer`, `cgroup_runtime` and `sd_notify`. The only `opamp` extension allowed is the supervisor's own, with id `opamp`, pointing at `ws://` on the loopback address;
- `service::telemetry` sends the collector's own telemetry anywhere: log or trace processors, metric readers other than a Prometheus pull reader, or logs written anywhere but stdout, stderr or local files.

Any receiver is accepted in local files. Receivers only bring data in.

The reason is short and names the setting, for example `exports to non-LimaCharlie destination: exporters::splunk_hec`. While the effective config is not reported yet, the collector is not blocked but gets no config either. Once the local files are fixed, the next report unblocks it.

## Limits

| Limit | Value |
|---|---|
| Configs per fleet | 100 |
| Size of one config | 256 KiB |
| Keys per selector | 32 |
| Collectors per fleet | 50,000. A new collector beyond that gets `429`. |
| OpAMP message | 4 MiB, before and after gzip |
| Effective config checked | 1 MiB |
| Effective config stored for display | 256 KiB, with the webhook secret replaced by `<redacted>` |
| Collector state kept after the last check-in | 7 days |
| Check-in interval | 5 to 3600 seconds, 30 by default |
