# Tutorial: Ingesting OpenTelemetry Data via Webhook

LimaCharlie webhook adapters support the [OpenTelemetry Protocol (OTLP)](https://opentelemetry.io/docs/specs/otlp/) over HTTP. You can send OTel **logs**, **traces**, and **metrics** directly into LimaCharlie without a separate collector.

This tutorial builds on the standard [Webhook Adapter](webhook-adapter.md). Read that page first to learn how to create and configure a webhook.

## How It Works

OpenTelemetry SDKs and collectors export telemetry with HTTP POST requests to an OTLP endpoint. The LimaCharlie webhook gateway recognizes OTLP paths that you add to the standard webhook URL. It parses the protobuf or JSON payloads into single events.

The URL pattern is:

```text
https://<hook-domain>/<OID>/<HOOKNAME>/<SECRET>/v1/<signal>
```

Where `<signal>` is one of:

| Signal    | Path        | Description                                    |
|-----------|-------------|------------------------------------------------|
| `logs`    | `/v1/logs`    | Log records from OTel logging SDKs           |
| `traces`  | `/v1/traces`  | Spans from OTel tracing SDKs                 |
| `metrics` | `/v1/metrics` | Metric data points from OTel metrics SDKs    |

This is the standard OTLP HTTP path convention. Set the base endpoint URL of the OTel SDK to your webhook URL, and the SDK operates correctly.

## Supported Content Types

| Content-Type              | Encoding   |
|---------------------------|------------|
| `application/x-protobuf`  | Protobuf (default for most OTel SDKs) |
| `application/json`        | JSON (OTLP/JSON encoding)             |

## Setup

### 1. Create a Webhook Adapter

Obey the [Webhook Adapter tutorial](webhook-adapter.md) to create a webhook. The configuration is the same - OTel support needs no special settings.

For example, with the CLI:

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

Get your hook domain:

```bash
limacharlie org urls
```

The command returns a domain such as `9157798c50af372c.hook.limacharlie.io`. Your full OTLP base endpoint is:

```text
https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret
```

### 3. Configure Your OTel SDK or Collector

Set the OTLP HTTP exporter endpoint to your webhook URL. The OTel SDK adds `/v1/logs`, `/v1/traces`, or `/v1/metrics` automatically, as necessary.

#### Environment Variables (any OTel SDK)

```bash
# Single endpoint for all signals
export OTEL_EXPORTER_OTLP_ENDPOINT="https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
```

You can also configure an endpoint for each signal:

```bash
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret/v1/logs"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret/v1/traces"
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="https://9157798c50af372c.hook.limacharlie.io/<OID>/otel-hook/my-otel-secret/v1/metrics"
```

#### OTel Collector Configuration

If you run an [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/), configure an `otlphttp` exporter:

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

LimaCharlie converts each OTel record into a JSON event. It ingests the event on the timeline of the webhook sensor. Each event has an `otel_type` field that identifies the type.

### Log Events

Each OTel `LogRecord` becomes an event with these fields:

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

Each metric data point becomes a separate event. The `metric_type` field shows the aggregation type:

| `metric_type`             | Description                          |
|---------------------------|--------------------------------------|
| `gauge`                   | Point-in-time measurement            |
| `sum`                     | Cumulative or delta counter          |
| `histogram`               | Distribution with explicit buckets   |
| `summary`                 | Pre-computed quantiles               |
| `exponential_histogram`   | Distribution with exponential buckets|

Common fields for all metric types:

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

For the `gauge` and `sum` types, the `value` field contains the numeric value. The `sum` type also has the `is_monotonic` and `aggregation_temporality` fields.

## Writing D&R Rules for OTel Events

The same D&R rule evaluation applies to OTel events and to other webhook events. You can write rules that target the `otel_type` field, or any other field in the event.

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

Standard (non-OTel) webhook requests to `/<OID>/<HOOKNAME>/<SECRET>` continue to operate as before. OTel support starts only when the URL contains the `/v1/logs`, `/v1/traces`, or `/v1/metrics` suffix.

## Related Articles

- [Webhook Adapter Tutorial](webhook-adapter.md)
- [Cloud Sensors Config Hive](../../../7-administration/config-hive/cloud-sensors.md)
