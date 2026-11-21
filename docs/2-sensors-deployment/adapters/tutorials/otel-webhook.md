# Tutorial: Ingesting OpenTelemetry Data via Webhook

LimaCharlie webhook adapters accept the [OpenTelemetry Protocol (OTLP)](https://opentelemetry.io/docs/specs/otlp/) over HTTP. An OpenTelemetry Collector or an OpenTelemetry SDK can send **logs**, **traces** and **metrics** straight to a webhook, and every log record, span and metric data point becomes one LimaCharlie event.

This page builds on the [Webhook Adapter](webhook-adapter.md) tutorial, which explains how to create a webhook. To have LimaCharlie manage the configuration of your collectors as well, see [OpenTelemetry Collector Fleets](otel-collector-fleets.md).

## Endpoints

An OTLP export is a `POST` to the webhook URL followed by `/v1/<signal>`:

| Signal | Path |
|---|---|
| Logs | `/v1/logs` |
| Traces | `/v1/traces` |
| Metrics | `/v1/metrics` |

These are the paths the OTLP/HTTP exporters append to their base endpoint, so you give the exporter the webhook URL and it adds the rest. The secret goes either in the path or in a header:

| Form | URL | Secret |
|---|---|---|
| Secret in the path | `https://<hooks-domain>/<OID>/<HOOKNAME>/<SECRET>/v1/<signal>` | In the URL |
| Secret in a header | `https://<hooks-domain>/<OID>/<HOOKNAME>/v1/<signal>` | `lc-secret: <SECRET>`, or `Authorization` (see below) |

The header form keeps the secret out of URLs, proxy logs and collector debug output, so prefer it.

The `Authorization` header is read only when neither the path nor `lc-secret` carries a secret. It accepts:

- `Authorization: Bearer <SECRET>`
- `Authorization: Basic <base64 of user:SECRET>`: the password is the secret, the user name is ignored.
- `Authorization: <SECRET>`: any other value is compared as a whole.

`<hooks-domain>` is your organization's hooks domain, shown as `hooks` by `limacharlie org urls` (for example `9157798c50af372c.hook.limacharlie.io`).

Plain webhook deliveries to `/<OID>/<HOOKNAME>/<SECRET>` and `/<OID>/<HOOKNAME>` work exactly as before. Only a path ending in `/v1/logs`, `/v1/traces` or `/v1/metrics` is treated as OTLP. If the hook's own secret happens to end in `/v1/logs`, a request whose path is that full secret stays a plain delivery.

## Request format

| Header | Accepted values |
|---|---|
| `Content-Type` | `application/x-protobuf` (OTLP protobuf, the exporter default) or `application/json` (OTLP/JSON). Parameters such as `; charset=utf-8` are ignored. Anything else gets `415`. |
| `Content-Encoding` | `gzip`, `identity` or none. A gzip body is also recognized without the header. `zstd`, `snappy`, `deflate` and any other encoding get `415`, as do several `Content-Encoding` values. |

The OpenTelemetry Collector's OTLP/HTTP exporter compresses with gzip by default, which works as is. Do not set its `compression` to `zstd` or `snappy`.

The type and encoding are checked after the secret, so a request with a wrong secret gets `401` whatever its type.

## Event format

Each record becomes one event on the webhook adapter's timeline:

- one event per `LogRecord`,
- one event per `Span`,
- one event per metric data point (a metric with 10 data points gives 10 events).

The resource and scope of the record are copied into each event.

How values are converted:

- Field names are the OTLP/JSON names (lowerCamelCase), such as `timeUnixNano` or `severityText`.
- Attribute lists become plain maps: `{"db.system": "postgresql"}`.
- Attribute values become native JSON: strings, booleans, numbers, lists and maps. Bytes values become base64 strings.
- Trace and span IDs are lowercase hex strings.
- 64-bit nanosecond times (every field ending in `UnixNano`) are JSON **strings**, as in OTLP/JSON, so that no precision is lost.
- Every other integer is a JSON **number**: `severityNumber`, `asInt`, `count`, `bucketCounts`, `zeroCount`, `flags` and the dropped counts. D&R numeric comparisons work on them.
- Enums are their name strings: `SPAN_KIND_SERVER`, `STATUS_CODE_ERROR`, `AGGREGATION_TEMPORALITY_CUMULATIVE`.
- NaN and infinite doubles become the strings `"NaN"`, `"Infinity"` and `"-Infinity"`.
- Zero and empty values are left out: an empty string, a zero number, `false`, an empty list or map, and the `UNSPECIFIED`/`UNSET` value of an enum. A value the sender set explicitly is kept even when it is zero: `asInt: 0`, `asDouble: 0`, or a histogram `sum` of `0`.

### Fields on every event

| Field | Value |
|---|---|
| `otel_type` | `log`, `span` or `metric` |
| `resource` | The resource attributes, as a map (an empty map when the resource has none) |
| `scope` | The instrumentation scope: `name`, `version` and `attributes`, each when set. Left out when all are empty. |
| `schemaUrl` | The resource's schema URL, when set |

### Log events

| Field | Value |
|---|---|
| `timeUnixNano` | Record time (string) |
| `observedTimeUnixNano` | Time the collector observed the record (string) |
| `severityNumber` | Severity number (number) |
| `severityText` | Severity text, such as `ERROR` |
| `body` | The log body: a string, or a structured value |
| `attributes` | Log record attributes |
| `traceId`, `spanId` | Hex IDs |
| `flags` | Trace flags (number) |
| `eventName` | Event name |
| `droppedAttributesCount` | Number |

### Span events

| Field | Value |
|---|---|
| `traceId`, `spanId`, `parentSpanId` | Hex IDs |
| `traceState` | W3C trace state |
| `name` | Span name |
| `kind` | `SPAN_KIND_INTERNAL`, `SPAN_KIND_SERVER`, `SPAN_KIND_CLIENT`, `SPAN_KIND_PRODUCER` or `SPAN_KIND_CONSUMER` |
| `startTimeUnixNano`, `endTimeUnixNano` | Strings |
| `attributes` | Span attributes |
| `events` | List of span events: `timeUnixNano`, `name`, `attributes`, `droppedAttributesCount` |
| `links` | List of links: `traceId`, `spanId`, `traceState`, `attributes`, `droppedAttributesCount`, `flags` |
| `status` | `code` (`STATUS_CODE_OK` or `STATUS_CODE_ERROR`) and `message`. Left out when the span has no status. |
| `flags` | Number |
| `droppedAttributesCount`, `droppedEventsCount`, `droppedLinksCount` | Numbers |

### Metric events

| Field | Value |
|---|---|
| `metricName`, `metricDescription`, `metricUnit` | From the metric |
| `metricMetadata` | The metric's metadata attributes, as a map |
| `metricType` | `gauge`, `sum`, `histogram`, `exponentialHistogram` or `summary` |
| `attributes` | Data point attributes |
| `startTimeUnixNano`, `timeUnixNano` | Strings |
| `flags` | Number |
| `exemplars` | List: `filteredAttributes`, `timeUnixNano`, `asDouble` or `asInt`, `spanId`, `traceId` |

Fields that depend on the metric type:

| `metricType` | Fields |
|---|---|
| `gauge` | `asDouble` or `asInt` |
| `sum` | `asDouble` or `asInt`, `aggregationTemporality`, `isMonotonic` (only when `true`) |
| `histogram` | `aggregationTemporality`, `count`, `sum`, `bucketCounts`, `explicitBounds`, `min`, `max` |
| `exponentialHistogram` | `aggregationTemporality`, `count`, `sum`, `scale`, `zeroCount`, `zeroThreshold`, `positive` and `negative` (each `offset` and `bucketCounts`), `min`, `max` |
| `summary` | `count`, `sum`, `quantileValues` (a list of `quantile` and `value`) |

### Event time

LimaCharlie takes each event's time from the record, with no mapping needed:

- log: `timeUnixNano`, or `observedTimeUnixNano` when the record has no time (many file receivers set only the observed time);
- span: `startTimeUnixNano`;
- metric data point: `timeUnixNano`.

When the record has no time, the event gets the time it was ingested.

### Example events

A log line read by the collector's file log receiver. It has no record time, so the event time comes from `observedTimeUnixNano`:

```json
{
  "otel_type": "log",
  "resource": {"deployment.environment": "prod"},
  "scope": {
    "name": "github.com/open-telemetry/opentelemetry-collector-contrib/receiver/filelogreceiver",
    "version": "0.165.0"
  },
  "observedTimeUnixNano": "1795218279063392036",
  "body": "2026-11-20T23:45:00Z ERROR disk /var is full",
  "attributes": {"log.file.name": "app.log"}
}
```

A span:

```json
{
  "otel_type": "span",
  "resource": {"deployment.environment": "prod", "service.name": "checkout"},
  "scope": {"name": "checkout"},
  "traceId": "5b8efff798038103d269b633813fc60c",
  "spanId": "eee19b7ec3c1b174",
  "name": "GET /cart",
  "kind": "SPAN_KIND_SERVER",
  "startTimeUnixNano": "1795218296651474959",
  "endTimeUnixNano": "1795218296901474959",
  "attributes": {"http.request.method": "GET", "http.response.status_code": 500},
  "status": {"code": "STATUS_CODE_ERROR", "message": "boom"}
}
```

A metric data point from the host metrics receiver:

```json
{
  "otel_type": "metric",
  "resource": {"deployment.environment": "prod"},
  "scope": {
    "name": "github.com/open-telemetry/opentelemetry-collector-contrib/receiver/hostmetricsreceiver/internal/scraper/memoryscraper",
    "version": "0.165.0"
  },
  "schemaUrl": "https://opentelemetry.io/schemas/1.9.0",
  "metricName": "system.memory.usage",
  "metricDescription": "Bytes of memory in use.",
  "metricUnit": "By",
  "metricType": "sum",
  "attributes": {"state": "used"},
  "startTimeUnixNano": "1794062392000000000",
  "timeUnixNano": "1795218309862679221",
  "asInt": 58600202240,
  "aggregationTemporality": "AGGREGATION_TEMPORALITY_CUMULATIVE"
}
```

`isMonotonic` is missing from the last one because the sum is not monotonic (`false` is left out).

## Responses and retries

LimaCharlie answers like an OTLP/HTTP server, so exporters handle every outcome correctly. A success is `200` with the signal's `Export*ServiceResponse`. An error is a `google.rpc.Status` message. Both use the encoding of the request (protobuf or JSON).

| Status | When | Exporter behavior |
|---|---|---|
| `200` | Accepted. If [webhook D&R rules](#filtering-at-the-webhook) rejected some records, `partial_success` gives their number and the rule. | Done (it logs the partial success) |
| `400` | Invalid OID, a body that is not valid OTLP, `Content-Encoding: gzip` on a body that is not gzip, or attribute values nested more than about 40 levels deep | Drops the data |
| `401` | Wrong or missing secret, unknown organization or hook, or a failed [signature check](webhook-adapter.md#creating-a-webhook-adapter) | Drops the data |
| `413` | The body or its decoded events are over the [limits](#limits) | Drops the data |
| `415` | Unsupported `Content-Type` or `Content-Encoding` | Drops the data |
| `503` with `Retry-After` | Temporary: the webhook's configuration is loading, its queue is full, the gateway is busy, or a signed delivery is still being processed | Retries after `Retry-After` |

The OTLP/HTTP exporter retries `429`, `502`, `503` and `504`, and waits for `Retry-After` on `429` and `503`. Every other error is permanent for it and the batch is dropped, so a misconfigured exporter shows up as errors in the collector's own log.

## Limits

- Request body: 8 MiB as sent, and 16 MiB once gzip is inflated. Larger requests get `413`. Lower the exporter's batch size (the `batch` processor's `send_batch_max_size`, or the exporter's `sending_queue` batch settings) if you hit it.
- A request whose events do not fit the webhook's queue at once gets `413` too. Send smaller batches.
- Attribute values can nest about 40 levels deep.

## Setup

### 1. Create a webhook adapter

Create a webhook as described in the [Webhook Adapter tutorial](webhook-adapter.md). No setting turns OTLP on. Setting `event_type_path` to `otel_type` makes the event type of each event `log`, `span` or `metric`, which D&R rules and searches can use:

```bash
echo '{
  "sensor_type": "webhook",
  "webhook": {
    "secret": "<YOUR_SECRET>",
    "client_options": {
      "hostname": "otel-ingest",
      "identity": {
        "oid": "<YOUR_OID>",
        "installation_key": "<YOUR_INSTALLATION_KEY>"
      },
      "platform": "json",
      "sensor_seed_key": "otel-ingest",
      "mapping": {
        "event_type_path": "otel_type"
      }
    }
  }
}' | limacharlie hive set --hive-name cloud_sensor --key otel-hook --enabled
```

### 2. Get the base URL

```bash
limacharlie org urls
```

With a hooks domain of `9157798c50af372c.hook.limacharlie.io`, the base endpoint for the header form is:

```text
https://9157798c50af372c.hook.limacharlie.io/<YOUR_OID>/otel-hook
```

### 3. Configure the collector or SDK

#### OpenTelemetry Collector

Use the OTLP/HTTP exporter, `otlp_http`. Collectors before v0.144.0 call it `otlphttp`, a name later releases still accept as a deprecated alias. The same goes for receivers: `file_log` was `filelog` before v0.149.0.

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 127.0.0.1:4318
  file_log:
    include: [/var/log/myapp/*.log]

processors:
  batch: {}

exporters:
  otlp_http/limacharlie:
    endpoint: https://9157798c50af372c.hook.limacharlie.io/<YOUR_OID>/otel-hook
    headers:
      lc-secret: <YOUR_SECRET>
    # gzip is the default; zstd and snappy are refused.
    compression: gzip

service:
  pipelines:
    logs:
      receivers: [otlp, file_log]
      processors: [batch]
      exporters: [otlp_http/limacharlie]
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp_http/limacharlie]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp_http/limacharlie]
```

The exporter appends `/v1/logs`, `/v1/traces` and `/v1/metrics` to `endpoint` itself. The example was checked with `otelcol-contrib validate` on v0.165.0.

To keep the secret out of the file, the collector can read it from the environment: `lc-secret: ${env:LC_HOOK_SECRET}`.

#### OpenTelemetry SDKs (environment variables)

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://9157798c50af372c.hook.limacharlie.io/<YOUR_OID>/otel-hook"
export OTEL_EXPORTER_OTLP_HEADERS="lc-secret=<YOUR_SECRET>"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
```

The SDK appends the signal path. Per-signal variables such as `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` take the full URL, `/v1/logs` included. `http/json` works as well. gRPC (`grpc`, port 4317) is not supported: use one of the HTTP protocols.

If a sender cannot set headers, put the secret in the path instead: `https://9157798c50af372c.hook.limacharlie.io/<YOUR_OID>/otel-hook/<YOUR_SECRET>`.

## Writing D&R rules for OTel events

OTel events go through your organization's D&R rules like any other adapter event. With `event_type_path: otel_type` set as above, this rule reports error logs from the `checkout` service:

```yaml
detect:
  event: log
  op: and
  rules:
    - op: is
      path: event/severityText
      value: ERROR
    - op: is
      path: event/resource/service.name
      value: checkout
respond:
  - action: report
    name: checkout-error-log
```

Without `event_type_path`, match on `event/otel_type` instead of `event:`. Numbers can be compared directly, for example `op: is greater than` on `event/severityNumber` with `value: 16` for every log at `ERROR` or above.

### Filtering at the webhook

A webhook can also drop records before they are ingested, with D&R rules evaluated at the webhook (`dr_rules` on the webhook record and rules with `target: webhook`). Each OTLP record is evaluated on its own, under `event/`:

```yaml
detect:
  target: webhook
  op: and
  rules:
    - op: is
      path: event/otel_type
      value: log
    - op: is
      path: event/severityText
      value: DEBUG
respond:
  - action: webhook reject
```

Rejected records are marked `__lc_accepted: false` and counted in the response's `partial_success`, so the exporter does not retry them.

## Related articles

- [Webhook Adapter Tutorial](webhook-adapter.md)
- [OpenTelemetry Collector Fleets](otel-collector-fleets.md)
- [Cloud Sensors Config Hive](../../../7-administration/config-hive/cloud-sensors.md)
