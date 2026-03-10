# Tutorial: Ingesting OpenTelemetry Data via Webhook

LimaCharlie webhook adapters support the [OpenTelemetry Protocol (OTLP)](https://opentelemetry.io/docs/specs/otlp/) over HTTP, allowing you to send OTel **logs**, **traces**, and **metrics** directly into LimaCharlie without running a separate collector.

This builds on the standard [Webhook Adapter](webhook-adapter.md). If you haven't already, review that page first to understand webhook creation and configuration.

## How It Works

OpenTelemetry SDKs and collectors export telemetry by sending HTTP POST requests to an OTLP endpoint. LimaCharlie's webhook gateway recognizes OTLP paths appended to the standard webhook URL and automatically parses the protobuf or JSON payloads into individual events.

The URL pattern is:

```
https://<hook-domain>/<OID>/<HOOKNAME>/<SECRET>/v1/<signal>
```

Where `<signal>` is one of:

| Signal    | Path        | Description                                    |
|-----------|-------------|------------------------------------------------|
| `logs`    | `/v1/logs`    | Log records from OTel logging SDKs           |
| `traces`  | `/v1/traces`  | Spans from OTel tracing SDKs                 |
| `metrics` | `/v1/metrics` | Metric data points from OTel metrics SDKs    |

This matches the standard OTLP HTTP path convention, so OTel SDKs work out of the box by setting the base endpoint URL to your webhook URL.

## Supported Content Types

| Content-Type              | Encoding   |
|---------------------------|------------|
| `application/x-protobuf`  | Protobuf (default for most OTel SDKs) |
| `application/json`        | JSON (OTLP/JSON encoding)             |

## Setup

### 1. Create a Webhook Adapter

Follow the [Webhook Adapter tutorial](webhook-adapter.md) to create a webhook. The configuration is identical - no special settings are needed for OTel support.

For example, using the CLI:

```bash
echo '{
  "sensor_type": "webhook",
  "webhook": {
    "secret": "my-otel-secret",
    "client_options": {
      "hostname": "otel-ingest",
      "identity": {
        "oid": "<YOUR_OID>",
        "installation_key": "<YOUR_INSTALLATION_KEY>"
      },
      "platform": "json",
      "sensor_seed_key": "otel-webhook"
    }
  }
}' | limacharlie hive set cloud_sensor --key otel-hook --data -
```

### 2. Get Your Webhook URL

Retrieve your hook domain:

```bash
limacharlie org urls
```

This returns a domain like `9157798c50af372c.hook.limacharlie.io`. Your full OTLP base endpoint is:

```
https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret
```

### 3. Configure Your OTel SDK or Collector

Set the OTLP HTTP exporter endpoint to your webhook URL. The OTel SDK will automatically append `/v1/logs`, `/v1/traces`, or `/v1/metrics` as needed.

#### Environment Variables (any OTel SDK)

```bash
# Single endpoint for all signals
export OTEL_EXPORTER_OTLP_ENDPOINT="https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
```

You can also configure per-signal endpoints:

```bash
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret/v1/logs"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret/v1/traces"
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret/v1/metrics"
```

#### OTel Collector Configuration

If you're running an [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/), configure an `otlphttp` exporter:

```yaml
exporters:
  otlphttp:
    endpoint: "https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret"

service:
  pipelines:
    logs:
      exporters: [otlphttp]
    traces:
      exporters: [otlphttp]
    metrics:
      exporters: [otlphttp]
```

## Event Format

Each OTel record is converted into a JSON event and ingested as a LimaCharlie event on the webhook sensor's timeline. All events include an `otel_type` field to identify their type.

### Log Events

Each OTel `LogRecord` becomes an event with the following fields:

| Field                       | Description                                                    |
|-----------------------------|----------------------------------------------------------------|
| `otel_type`                 | Always `"log"`                                                 |
| `timestamp_ns`              | Event time in nanoseconds (falls back to observed time)        |
| `severity_text`             | Severity level string (e.g., `"ERROR"`, `"INFO"`)              |
| `severity_number`           | Numeric severity (OTel severity number)                        |
| `body`                      | Log message body (string or structured object)                 |
| `attributes`                | Key-value attributes on the log record                         |
| `resource`                  | Resource attributes (e.g., `service.name`, `host.name`)        |
| `scope`                     | Instrumentation scope (name, version, attributes)              |
| `trace_id`                  | Trace ID (hex string, if present)                              |
| `span_id`                   | Span ID (hex string, if present)                               |
| `event_name`                | OTel event name (if present)                                   |

Example event:

```json
{
  "otel_type": "log",
  "timestamp_ns": 1709726400000000000,
  "severity_text": "ERROR",
  "severity_number": 17,
  "body": "connection refused to database",
  "attributes": {
    "db.system": "postgresql",
    "db.name": "users"
  },
  "resource": {
    "service.name": "api-gateway",
    "host.name": "prod-01"
  },
  "scope": {
    "name": "my-logger",
    "version": "1.0.0"
  },
  "trace_id": "0102030405060708090a0b0c0d0e0f10",
  "span_id": "0102030405060708"
}
```

### Trace Events (Spans)

Each OTel `Span` becomes an event:

| Field                        | Description                                              |
|------------------------------|----------------------------------------------------------|
| `otel_type`                  | Always `"span"`                                          |
| `name`                       | Span operation name                                      |
| `kind`                       | Span kind (e.g., `SPAN_KIND_SERVER`, `SPAN_KIND_CLIENT`) |
| `start_timestamp_ns`         | Span start time in nanoseconds                           |
| `end_timestamp_ns`           | Span end time in nanoseconds                             |
| `trace_id`                   | Trace ID (hex string)                                    |
| `span_id`                    | Span ID (hex string)                                     |
| `parent_span_id`             | Parent span ID (hex string, if present)                  |
| `attributes`                 | Span attributes                                          |
| `resource`                   | Resource attributes                                      |
| `scope`                      | Instrumentation scope                                    |
| `status_code`                | Span status (e.g., `STATUS_CODE_OK`, `STATUS_CODE_ERROR`)|
| `status_message`             | Status message (if present)                              |
| `events`                     | List of span events (if present)                         |
| `links`                      | List of span links (if present)                          |

### Metric Events

Each metric data point becomes a separate event. The `metric_type` field indicates the aggregation type:

| `metric_type`             | Description                          |
|---------------------------|--------------------------------------|
| `gauge`                   | Point-in-time measurement            |
| `sum`                     | Cumulative or delta counter          |
| `histogram`               | Distribution with explicit buckets   |
| `summary`                 | Pre-computed quantiles               |
| `exponential_histogram`   | Distribution with exponential buckets|

Common fields across all metric types:

| Field                  | Description                                             |
|------------------------|---------------------------------------------------------|
| `otel_type`            | Always `"metric"`                                       |
| `metric_name`          | Metric name                                             |
| `metric_type`          | Aggregation type (see above)                            |
| `timestamp_ns`         | Data point timestamp in nanoseconds                     |
| `attributes`           | Data point attributes                                   |
| `resource`             | Resource attributes                                     |
| `scope`                | Instrumentation scope                                   |
| `description`          | Metric description (if provided)                        |
| `unit`                 | Metric unit (if provided)                               |

For `gauge` and `sum` types, the `value` field contains the numeric value. For `sum`, additional fields `is_monotonic` and `aggregation_temporality` are included.

## Writing D&R Rules for OTel Events

OTel events flow through the same D&R rule evaluation as regular webhook events. You can write rules that target the `otel_type` field or any other field in the event.

Example D&R rule to detect error-level OTel logs:

```yaml
detect:
  target: webhook
  event: json/otel_type
  op: is
  value: log
  rules:
    - event: json/severity_text
      op: is
      value: ERROR
respond:
  - action: webhook reject
```

## Backward Compatibility

Standard (non-OTel) webhook requests to `/<OID>/<HOOKNAME>/<SECRET>` continue to work exactly as before. OTel support is activated only when the URL contains the `/v1/logs`, `/v1/traces`, or `/v1/metrics` suffix.

## Related Articles

* [Webhook Adapter Tutorial](webhook-adapter.md)
* [Cloud Sensors Config Hive](../../../7-administration/config-hive/cloud-sensors.md)
