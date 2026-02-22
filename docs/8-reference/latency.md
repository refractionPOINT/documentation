# Understanding Latency

## D&R Engine Latency

The LimaCharlie Detection & Response (D&R) engine processes events in real-time with very low latency. You can expect D&R rule evaluation to complete in under 100ms in typical conditions.

There is no long-term backlog queue — events are processed in real-time as they arrive. If a sensor generates data at an unsustainable rate (thousands of events per second over an extended period), the platform will eventually emit a **queue drop** event rather than silently falling behind.

## Output Latency

Some outputs are delivered in batches (e.g., Amazon S3, SFTP, Google Cloud Storage), where you can configure the maximum batch size and time window. Live outputs such as Syslog deliver data immediately.

## Understanding `routing.latency`

Detections include a `routing.latency` field, which is the delta between `routing.event_time` and `gen_time` (detection creation time), expressed in milliseconds. This value represents the **total end-to-end time** from when the event originally occurred to when LimaCharlie created the detection — it is **not** a measure of D&R engine processing time.

The `routing.event_time` is the timestamp of the original event as reported by the source. This means `routing.latency` includes all delays that occur **before** the event reaches LimaCharlie, such as:

- Time spent in third-party pipelines (e.g., Microsoft O365, AWS CloudTrail)
- Time between when an OS records an event internally and when it becomes available to the sensor (e.g., macOS Unified Logs, Windows Event Logs)
- Network transit time from the sensor to the LimaCharlie cloud

## Common Causes of High `routing.latency`

### External Data Sources (USP/Adapters)

When ingesting data from external platforms via adapters, the source platform controls when events become available. For example, Microsoft 365 events can be delayed anywhere from minutes to several hours in Microsoft's own pipeline before LimaCharlie can pull them. LimaCharlie has no control over these upstream delays.

### Sensor Sleep/Wake Cycles

If a laptop goes to sleep and wakes up hours later, events generated before sleep are transmitted only after the sensor reconnects. An event from 12 hours ago that arrives after wake-up will show a `routing.latency` of 12+ hours, even though the D&R engine processed it instantly upon receipt.

### Network Interruptions

If a sensor loses internet connectivity, it buffers events locally and transmits them when the connection is restored. This can produce a burst of events with high `routing.latency` values.

### OS-Level Delays

Operating systems do not always emit internal events immediately. macOS and Windows may delay writing certain events to their respective log systems (Unified Logs, Event Logs), which means the sensor cannot transmit them until they are available.

## How to Diagnose Latency

To assess whether the LimaCharlie processing pipeline is healthy, **look at the minimum `routing.latency` value for a given sensor** rather than the maximum or average. Because events from a sensor are processed first-in-first-out in real-time, if you see some events processed in a few hundred milliseconds, the pipeline is working correctly. High latency on specific events alongside low latency on others indicates the delays are on the source side, not in the LimaCharlie pipeline.

## What Can Affect D&R Processing Time

While the D&R engine itself is sub-100ms, certain configurations can introduce additional processing time:

- **Blocking D&R actions**: Rules that use `wait` or perform external lookups (e.g., VirusTotal queries) block processing while waiting for a response. Heavy use of these across many rules can introduce back-pressure.
- **Blocking outputs**: Single-event webhook outputs that receive high volumes can create back-pressure if the destination is slow to respond.

In practice, these factors typically add milliseconds to seconds, not minutes or hours.

## Architecture

LimaCharlie's infrastructure is multi-tenant. There is no per-organization queue — events are processed across hundreds of services where each sensor's events are handled independently. This means latency issues in one organization do not affect others.
