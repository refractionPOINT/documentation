# Understanding Latency

## D&R Engine Latency

The LimaCharlie Detection & Response (D&R) engine processes events in real time with very low latency. In normal conditions, the evaluation of a D&R rule completes in less than 100ms.

There is no long-term backlog queue — the engine processes events in real time when they arrive. If a sensor generates data at a rate that the platform cannot keep (thousands of events each second for a long period), the platform emits a **queue drop** event. The platform does not fall behind silently.

## Output Latency

Some outputs send data in batches (e.g., Amazon S3, SFTP, Google Cloud Storage). For these outputs, you configure the maximum batch size and the time window. Live outputs such as Syslog send data immediately.

## Understanding `routing.latency`

Detections include a `routing.latency` field. It is the delta between `routing.event_time` and `gen_time` (detection creation time), in milliseconds. This value is the **total end-to-end time** from the moment of the original event to the moment when LimaCharlie created the detection — it is **not** a measure of the processing time of the D&R engine.

The `routing.event_time` is the timestamp of the original event from the source. Thus, `routing.latency` includes all delays that occur **before** the event comes to LimaCharlie, such as:

- The time in third-party pipelines (e.g., Microsoft O365, AWS CloudTrail)
- The time between the internal record of an event by an OS and the availability of that event to the sensor (e.g., macOS Unified Logs, Windows Event Logs)
- The network transit time from the sensor to the LimaCharlie cloud

## Common Causes of High `routing.latency`

### External Data Sources (USP/Adapters)

When you ingest data from external platforms with adapters, the source platform controls when the events become available. For example, the Microsoft pipeline can delay Microsoft 365 events from minutes to several hours before LimaCharlie can pull them. LimaCharlie has no control of these upstream delays.

### Sensor Sleep/Wake Cycles

If a laptop sleeps and wakes hours later, the sensor transmits the events from before the sleep only after it connects again. An event from 12 hours before shows a `routing.latency` of 12+ hours, but the D&R engine processed it immediately at receipt.

### Network Interruptions

If a sensor loses the internet connection, it buffers the events locally and transmits them when the connection comes back. This can cause a burst of events with high `routing.latency` values.

### OS-Level Delays

Operating systems do not always emit internal events immediately. macOS and Windows can delay the write of some events to their log systems (Unified Logs, Event Logs). The sensor cannot transmit these events until they are available.

## How to Diagnose Latency

To find whether the LimaCharlie processing pipeline is healthy, **look at the minimum `routing.latency` value for a given sensor** and not at the maximum or the average. The pipeline processes the events from a sensor first-in-first-out in real time. If some events are processed in a few hundred milliseconds, the pipeline operates correctly. High latency on some events with low latency on others shows that the delays are on the source side, and not in the LimaCharlie pipeline.

## What Can Affect D&R Processing Time

The D&R engine itself is sub-100ms, but some configurations add processing time:

- **Blocking D&R actions**: Rules that use `wait` or that do external lookups (e.g., VirusTotal queries) block the processing until a response comes. Much use of these actions across many rules can cause back-pressure.
- **Blocking outputs**: Single-event webhook outputs with high volumes can cause back-pressure if the destination responds slowly.

In practice, these factors usually add milliseconds to seconds, and not minutes or hours.

## Architecture

The LimaCharlie infrastructure is multi-tenant. There is no queue for each organization — hundreds of services process the events, and the events of each sensor are handled independently. Thus, latency problems in one organization do not affect other organizations.
