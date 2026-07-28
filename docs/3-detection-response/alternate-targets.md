# Detection on Alternate Targets

Detection & Response rules run against `edr` events by default. There are 7 other targets:

- `detection`
- `deployment`
- `artifact`
- `artifact_event`
- `schedule`
- `audit`
- `billing`

This page gives examples of what these targets are for and how to use them.

## Target: detection

You can run rules on the detections that other rules generate. These rules let you filter
existing detections and add a response for special cases.

In the `detection` target, the `event:` or `events:` field refers to the `name` of the detection
in the `report` action of the original detection.

The `detection` target supports the same operators and actions as regular `edr` rules.

### Example

```python
# Detection
target: detection
op: and
rules:
- op: is
  path: cat
  value: virus-total-hit
- op: is
  path: routing/hostname
  value: ceo-laptop

# Response
- action: extension request
  extension name: ext-pagerduty
  extension action: run
  extension request:
    group: '{{ "lc-alerts" }}'
    severity: '{{ "critical" }}'
    component: '{{ "vip-alert" }}'
    summary: '{{ "Alert on a VIP endpoint." }}'
    source: '{{ "limacharlie.io" }}'
    class: '{{ "dr-rules" }}'
```

This rule takes an existing detection report with the name `virus-total-hit`. If the detection
occurs on a specific hostname, the rule sends it to PagerDuty.

## Target: deployment

Deployment events are about sensors that connect to the cloud: `enrollment`, `sensor_clone`, `sensor_over_quota`, `deleted_sensor`.

The `sensor_clone` event is an example. This event can occur when a sensor is installed in a VM image. Duplicate sensor IDs then connect to the cloud. When the cloud detects this, you can use the event to de-duplicate the sensor automatically.

The `deployment` target supports the same operators and actions as regular `edr` rules.

### Example

```yaml
# Detection
target: deployment
event: sensor_clone
op: is windows

# Response
- action: task
  command: file_del %windir%\system32\hcp.dat
- action: task
  command: file_del %windir%\system32\hcp_hbs.dat
- action: task
  command: file_del %windir%\system32\hcp_conf.dat
- action: task
  command: restart
```

This rule de-duplicates sensors on Windows. It deletes the `.dat` files of the Windows installation, then it sends a `restart` command to the sensor.

> For samples of each `deployment` event type, see [Reference: Platform Events](../8-reference/platform-events.md).

## Target: artifact

The rule engine can process parsed artifacts as if they are regular `edr` events, but there are differences. Artifacts support only a subset of the operators and actions, and they add special parameters.

### Example

This rule targets parsed `/var/log/auth.log` entries and finds authentication failures.

```yaml
# Detection
target: artifact
artifact type: txt
artifact path: /var/log/auth.log
op: matches
re: .*(authentication failure|Failed password).*
path: /text
case sensitive: false

# Response
- action: report
  name: Failed Auth
```

### Supported Operators

- `is`
- `and`
- `or`
- `exists`
- `contains`
- `starts with`
- `ends with`
- `is greater than`
- `is lower than`
- `matches`
- `string distance`

### Supported Resources

Rules support the `lookup` and `external` resources, the same as the `edr` target.

### Supported Actions

The `artifact` target supports only the `report` response action.

### Special Parameters

- `artifact path`: matches the start of the artifact's `path` string, e.g. `/auth.log`
- `artifact type`: matches the artifact's `type` string, e.g. `pcap`, `zeek`, `auth`, `wel`
- `artifact source`: matches the artifact's `source` string, e.g. `hostname-123`

> Note: for duplicate ingestions of Windows Event Logs, the rule engine uses the `EventRecordID` of the log. This makes sure that a rule does not run more than one time on the same record.

## Target: artifact\_event

For unparsed logs, use the `ingest` and `export_complete` lifecycle events of the `artifact_event` target. These events let you automate a response to artifacts.

> For samples of `ingest` and `export_complete`, see [Reference: Platform Events](../8-reference/platform-events.md).

### Example

```yaml
# Detection
target: artifact_event
event: export_complete
op: starts with
path: routing/log_type
value: pcap
case sensitive: false

# Response
- action: report
  name: PCAP Artifact ready to Download
```

## Target: schedule

Schedule events occur automatically at different intervals for each organization or for each sensor. Rules see these events through the `schedule` target.

For more information, see [Reference: Schedule Events](../8-reference/schedule-events.md)

## Target: audit

The LimaCharlie cloud generates audit events. They track changes and events in the cloud, such as tasking, replays, and hive changes. To see these events, use the "Platform Logs" menu or the events from the `audit-logs` sensor.

## Target: billing

The LimaCharlie cloud generates billing events. They are about quotas, thresholds, and other events related to cost. For an example, see the [Usage Alerts Extension](../5-integrations/extensions/limacharlie/usage-alerts.md) documentation
