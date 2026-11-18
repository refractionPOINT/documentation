# Durable Telemetry Delivery

Durable telemetry delivery is an opt-in mode for the native Endpoint Agent
(Windows, Linux and macOS). In this mode the sensor keeps a bounded, in-memory
copy of the telemetry it sent until LimaCharlie confirms that the telemetry is
stored. If the confirmation does not arrive, for example because a cloud
ingestion node was lost, the sensor sends the telemetry again.

Without this mode, a sensor discards telemetry as soon as it has been written
to its connection to the cloud. If the cloud ingestion node that received it
fails before the telemetry is stored, that telemetry is lost. Durable delivery
removes that loss window, within the limits listed under
[What It Does Not Cover](#what-it-does-not-cover).

## When to Use It

Ask for it when losing the most recently sent telemetry during an infrastructure
failure on the LimaCharlie side is not acceptable for your organization, and
you can tolerate the occasional duplicate described below.

The mode is enabled per organization by LimaCharlie. There is nothing to
configure on the sensor and no setting in the web application. To have it
turned on or off for an organization, contact LimaCharlie support at
[answers@limacharlie.io](mailto:answers@limacharlie.io).

It also needs a sensor version that supports it (see the
[release notes](../../10-release-notes/endpoint-agent.md)). Sensors that do not
support it keep working exactly as before, and sensors that do support it stay
idle until the mode is enabled for the organization.

Turning the mode off for an organization takes effect on its sensors within
about five minutes.

## At-Least-Once Delivery

With durable delivery, an event that the sensor sent reaches LimaCharlie at
least once, within the limits listed under
[What It Does Not Cover](#what-it-does-not-cover). In rare
cases, typically after a sensor reconnects or a cloud node is lost, the same
event is received twice.

To make this visible, an event that the sensor sent again carries
`routing.replayed` set to `true`, and it receives a new `routing.event_id`.
Events that were not sent again do not carry the field at all.

```json
{
  "routing": {
    "event_type": "NEW_PROCESS",
    "event_time": 1656959942437,
    "event_id": "5f0c3a9e-6f0e-4d3e-9a43-4a8d7f2b1c10",
    "sid": "bb4b30af-aaaa-aaaa-aaaa-f014ada33345",
    "hostname": "workstation-01",
    "replayed": true
  },
  "event": {
    "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
    "COMMAND_LINE": "cmd.exe /c whoami"
  }
}
```

The field is documented with the other fields in
[The `routing` Section](../../8-reference/routing.md).

!!! note "No indicator that the mode is on"
    The only sign of the mode in your data is the `routing.replayed` field on
    events that were sent again. Replays are rare, so the absence of the field
    does not show that the mode is off. Ask LimaCharlie support to confirm the
    state for your organization.

## What Changes for Detections, Outputs and Usage

A replayed event is processed like any other event:

- **Detection and Response rules** run on it. A rule that matched the original
  event can match the replayed one, so the same detection can fire a second
  time. A replay can also be the only copy that reaches LimaCharlie, in which
  case it produces a detection that would otherwise have been missed.
- **Outputs** (webhook, S3, and so on) receive the replayed event as well, so
  the receiving system can see the same activity twice.
- **Usage**: a replayed event counts toward your usage like any other event.
- **Event IDs**: because a replayed event has a new `routing.event_id`, you
  cannot detect duplicates by comparing event IDs.

### Excluding Replayed Events in a D&R Rule

A replayed event has `routing/replayed` set to `true`. Events that are not
replays do not have the field, so an `is` check on it does not match them.

To keep an existing rule from firing a second time on a replayed event, add a
negated `is` check on `routing/replayed`:

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: cmd.exe
    - op: is
      not: true
      path: routing/replayed
      value: true
respond:
  - action: report
    name: cmd-exe-launched
```

Think before adding this check to every rule. If the original copy of an event
was lost with a failed cloud node, the replayed copy is the only one, and a rule
that ignores replays does not fire on it. Excluding replays suits rules whose
response is not safe to repeat, or whose duplicate alerts are costly.

To match only replayed events, for example to count them or to review what was
sent again, use:

```yaml
detect:
  event: NEW_PROCESS
  op: is
  path: routing/replayed
  value: true
respond:
  - action: report
    name: replayed-event-seen
```

The same condition works with the `exists` operator on `routing/replayed`. See
[Detection Logic Operators](../../8-reference/detection-logic-operators.md) for
the operators and [Response Actions](../../8-reference/response-actions.md) for
actions such as `suppression`.

### Outputs

The documented output filters are by event type, sensor tag and detection
category (see
[Filtering and Transforming Streams](../../5-integrations/outputs/stream-structures.md#filtering-and-transforming-streams)).
There is no output filter on a field such as `routing.replayed`. If the
system that receives the data should ignore replays, filter on
`routing.replayed` in that system. An event with `"replayed": true` may be a
repeat of one you already received, or the only copy if the original was lost,
so dropping replays trades duplicates for possible loss. Events without the
field were not sent again.

## What It Does Not Cover

- **Sensor restart or host crash.** The copy the sensor keeps is in memory, not
  on disk. If the sensor process or the host stops, the copy is gone.
- **Very high telemetry rates.** The copy is bounded (see below). A sensor that
  produces more telemetry than the bound can hold while it waits for a
  confirmation releases its oldest copies, and those are no longer protected.
  Behavior for them is the same as without the mode.
- **Delivery to your own outputs.** Only the telemetry LimaCharlie stores for
  your organization is confirmed. LimaCharlie does not wait for, or confirm,
  delivery to a webhook, a storage bucket or any other output you configured.
- **Telemetry sent before the mode is on.** After a sensor starts, the first
  telemetry it sends before the cloud enables the mode is not protected.

## Sensor Resource Use

By default, the sensor keeps at most 5,000 events or 25 MiB of recently sent
telemetry, whichever comes first. This copy shares the sensor's existing 50 MiB queue
budget, so the maximum memory of the sensor does not grow. A sensor that sends
little telemetry typically holds little.

When the sensor's queue is full, the copy is released before unsent telemetry is
discarded, so the mode does not make the sensor lose more unsent data than it
would without it.

## Questions

**Will I see duplicates all the time?**
No. Replays happen after a sensor reconnects or a cloud node is lost, and most
events are never replayed.

**Does it change what is stored or how long it is kept?**
No. Retention settings are unchanged. The differences are the possible
duplicates and the `routing.replayed` field on events that were sent again.

**What happens to a sensor that does not support it?**
Nothing. It keeps working as before, and nothing is sent to it.

## Related Documentation

- [The `routing` Section](../../8-reference/routing.md)
- [Detection Logic Operators](../../8-reference/detection-logic-operators.md)
- [Output Stream Structures](../../5-integrations/outputs/stream-structures.md)
- [Endpoint Agent Versioning and Upgrades](versioning-upgrades.md)
