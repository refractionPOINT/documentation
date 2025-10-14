# Response Actions

## Overview

Actions in LimaCharlie Detection & Response (D&R) rules define what happens after a detection is triggered. Common actions include generating reports, tagging sensors, isolating networks, and the frequently used `task` action, which sends commands to an Endpoint Agent to interrogate or take action on the endpoint. This is useful for tasks like gathering system information or isolating a compromised endpoint. Suppression settings manage repetitive alerts by limiting action frequency, ensuring efficient automation and response workflows.

> For more information on how to use Actions, read [Detection & Response rules](/v2/docs/detection-and-response).

## Suppression

Suppression is valuable to help manage repetitive or noisy alerts.

### Reduce Frequency

In some cases, you may want to limit the number of times a specific Action is executed over a certain period of time. You can achieve this through `suppression`. This feature is supported in every Actions.

A suppression descriptor can be added to an Action like:

```yaml
- action: report
  name: evil-process-detected
  suppression:
    max_count: 1
    period: 1h
    is_global: true
    keys:
      - '{{ .event.FILE_PATH }}'
      - 'evil-process-detected'
```

The above example means that the `evil-process-detected` detection will be generated up to once per hour per `FILE_PATH`. Beyond the first `report` with a given `FILE_PATH`, during the one hour period, new `report` actions from this rule will be skipped.

The `is_global: true` means that the suppression should operate globally within the Org (tenant), if the value was `false`, the suppression would be scoped per-Sensor.

The `keys` parameter is a list of strings that support [templating](/v2/docs/template-strings-and-transforms). Together, the unique combination of values of all those strings (ANDed) will be the uniqueness key this suppression rule uses. By adding to the keys the `{{ .event.FILE_PATH }}` template, we indicate that the `FILE_PATH` of the event generating this `report` is part of the key, while the constant string `evil-process detected` is just a convenient way for us to specify a value related to this specific detection. If the `evil process-detected` component of the key was not specified, then *all* actions that also just specify the `{{ .event.FILE_PATH }}` would be contained in this suppression. This means that using `is_global: true` and a complex key set, it is possible to suppress some actions across multiple Actions across multiple D&R rules.

> **Supported Time Period Formats**
>
> LimaCharlie supports the following formats for time periods: **ns**, **us** (or **µs**, both are accepted), **ms**, **s**, **m**, **h** (nanoseconds, microseconds, milliseconds, seconds, minutes, and hours, respectively)

### Threshold Activation

The other way to use suppression is using the `min_count` parameter. When set, the specific action will be suppressed until `min_count` number of activations have been received in that period.

Here's an example of this:

```yaml
- action: report
  name: high-alerts
  suppression:
    min_count: 3
    max_count: 3
    period: 24h
```

The above example means the `high-alerts` detection will be generated once per hour but only after the rule the action belongs to has matched 3 times within that period.

This could be useful if you wanted to create higher order alerts that trigger a different type of detection, or send a page alert to a SOC, when more than X alerts occurred on a single host per period.

> **Note:** Both `min_count` and `max_count` must be specified when setting a threshold.

### Variable Count

It is also possible to increment a suppression by a value that's not one (`1`). This is achieved using the `count_path` parameter, which is a path (like `event/record/v`) pointing to an integer that should be used to increment the suppression counter.

This is useful for things like billing alerts, where we set a threshold activation (meaning "alert me if above X") where the threshold is reached by increments of billable values.

Here's an example of this:

```yaml
detect:
    event: billing_record
    op: is
    path: event/record/k
    target: billing
    value: ext-strelka:bytes_scanned

respond:
    - action: report
      name: strelka-bytes-reached
      suppression:
        count_path: event/record/v
        is_global: true
        keys:
          - strelka-bytes-usage
        max_count: 1048576
        min_count: 1048576
        period: 24h
```

The above will alert (generate a detection in this case) when 1MB (1024 x 1024 x 1) of bytes have been billed by the Strelka Extension based on the `bytes_scanned` SKU, per 24h.

It does so by incrementing the suppression counter by the billed value (found in `event/record/v`), resetting after 24h, and if the value of 1MB is reached, alert once and only once.

## Available Actions

Actions allow you to specify "what" happens after a detection is found.

### add tag, remove tag

```yaml
- action: add tag
  tag: vip
  entire_device: false # defaults to false
  ttl: 30 # optional
```

Adds or removes Tags on the sensor.

#### Optional Parameters

The `add tag` action can optionally take a `ttl` parameter that is a number of seconds the tag should remain applied to the sensor.

The `add tag` action can optionally have the `entire_device` parameter set to `true`. When enabled, the new tag will apply to the entire Device ID, meaning that every sensor that shares this Device ID will have the tag applied (and relevant TTL). If a Device ID is unavailable for the sensor, it will still be tagged.

This can be used as a mechanism to synchronize and operate changes across an entire device. A D&R rule could detect a behavior and then tag all sensors on the device so they may act accordingly, like start doing full pcap.

For example, this would apply the `full_pcap` to all sensors on the device for 5 minutes:

```yaml
- action: add tag
  tag: full_pcap
  ttl: 300
  entire_device: true
```

### add var, del var

Add or remove a value from the variables associated with a sensor.

```yaml
- action: add var
  name: my-variable
  value: <<event/VOLUME_PATH>>
  ttl: 30 # optional
```

The `add var` action can optionally take a `ttl` parameter that is a number of seconds the variable should remain in state for the sensor.

### extension request

Perform an asynchronous request to an extension the Organization is subscribed to.

```yaml
- action: extension request
  extension name: dumper # name of the extension
  extension action: dump # action to trigger
  extension request:     # request parameters
    sid: '{{ .routing.sid }}'
    pid: event.PROCESS_ID
```

The `extension request` parameters will vary depending on the extension (see the relevant extension's schema). The `extension request` parameter is a [transform](/v2/docs/template-strings-and-transforms).

You can also specify a `based on report: true` parameter. When true (defaults to false), the transform for the `extension request` will be based on the latest `report` action's report instead of the original event. This means you MUST have a `report` action *before* the `extension request`.

### isolate network

Isolates the sensor from the network in a persistent fashion (if the sensor/host reboots, it will remain isolated). Only works on platforms supporting the `segregate_network` [sensor command](/v2/docs/reference-endpoint-agent-commands#segregatenetwork).

```yaml
- action: isolate network
```

When the network isolation feature is used, LimaCharlie will block connections to all destinations other than the LimaCharlie cloud (so that you can perform an investigation, take remediation actions, and then ultimately remove the isolation to resume normal network operation). The host will maintain internet connectivity to allow for you to perform those actions.

> The `segregate_network` command is stateless, so if the endpoint reboots, it will not be in effect. The isolate network command in D&R rules is stateful, so it sets a flag in the cloud to make sure the endpoint remains isolated even after reboots.

### seal

Seals the sensor in a persistent fashion (if the sensor/host reboots, it will remain sealed). Only works on platforms supporting the `seal` [sensor command](/v2/docs/reference-endpoint-agent-commands#seal).

```yaml
- action: seal
```

Sealing a sensor enables tamper resistance, preventing direct modifications to the installed EDR.

> The `seal` command is stateless, so if the endpoint reboots, it will not be in effect. The seal command in D&R rules is stateful, so it sets a flag in the cloud to make sure the endpoint remains sealed even after reboots.

### unseal

Removes the seal status of a sensor that had it set using `seal`.

```yaml
- action: unseal
```

### output

Forwards the matched event to an Output identified by `name` in the `tailored` [stream](/v2/docs/outputs).

This allows you to create highly granular Outputs for specific events.

The `name` parameter is the name of the Output.

Example:

```yaml
- action: output
  name: my-output
```

### rejoin network

Removes the isolation status of a sensor that had it set using `isolate network`.

```yaml
- action: rejoin network
```

### report

```yaml
- action: report
  name: my-detection-name
  publish: true # defaults to true
  priority: 3   # optional
  metadata:     # optional & free-form
    author: Alice (alice@wonderland.com)
  detect_data:  # additional free-form field that can be used for extraction of specific elements
```

Reports the match as a detection. Think of it as an alert. Detections go a few places:

* The `detection` Output stream
* The organization's Detections page (if `insight` is enabled)
* The D&R rule engine, for chaining detections

The `name`, `metadata` and `detect_data` parameters support [string templates](/v2/docs/template-strings-and-transforms) like `detected {{ .cat }} on {{ .routing.hostname }}`, note that the context of the transform is the detection itself and not the original event, so you would refer to `.detect.event.USER_NAME` and not `.event.USER_NAME` for example.

The `metadata` is generally used to populate information about the rule, its author, remediation etc.

The `detect_data` is generally used to extract specific parts of the detected event into a known format that can be common across multiple detection, like extracting the `domain` or `hash` field for example.

#### Limiting Scope

There is a mechanism for limiting scope of a `report`, prefixing `name` with `__` (double underscore). This will cause the detection generated to be visible to chained D&R rules and Services, but the detection will *not* be sent to the Outputs for storage.

This is a useful mechanism to automate behavior using D&R rules without generating extra traffic that is not useful.

#### Optional Parameters

The `priority` parameter, if set, should be an integer. It will be added to the root of the detection report as `priority`.

The `metadata` parameter, if set, can include any data. It will be added to the root of the detection report as `detect_mtd`. This can be used to include information for internal use like reference numbers or URLs.

### task

```yaml
- action: task
  command: history_dump
  investigation: susp-process-inv
```

Sends a task in the `command` parameter to the sensor that the event under evaluation is from.

An optional `investigation` parameter can be given to create a unique identifier for the task and any events emitted from the sensor as a result of the task.

The `command` parameter supports [string templates](/v2/docs/template-strings-and-transforms) like `artifact_get {{ .event.FILE_PATH }}`.

> To view all possible commands, see [Endpoint Agent Commands](/v2/docs/reference-endpoint-agent-commands)

### undelete sensor

Un-deletes a sensor that was previously deleted.

```yaml
detect:
    target: deployment
    event: deleted_sensor
    op: is
    path: routing/event_type
    value: deleted_sensor
respond:
    - action: undelete sensor
```

This can be used in conjunction with the `deleted_sensor` event to allow sensors to rejoin the fleet.

### wait

Adds a delay (up to 1 minute) before running the next response action.

This can be useful if a previous response action needs to finish running (i.e. a command or payload run via `task`) before you can execute the next action.

> The `wait` action will block processing any events from that sensor for the specified duration of time. This is because D&R rules are run at wire-speed and in-order.

The `duration` parameter supports two types of values:

* A string describing a duration, like `5s` for 5 seconds or `10ms` for 10 milliseconds, as defined by [this function call](https://pkg.go.dev/time#ParseDuration).
* An integer representing a number of seconds.

Example:

```yaml
- action: wait
  duration: 10s
```

and

```yaml
- action: wait
  duration: 5
```

### add hive tag

Adds a tag to a Hive record. This can be used to mark some Hive records like D&R rules automatically.

```yaml
- action: add hive tag
  hive name: dr-general
  record name: my-rule
  tag: high-hit
```

Unless the rule is not expected to hit often, you likely want to couple this with a `suppression` statement to avoid doing a lot of tagging of the same rules like:

```yaml
- action: add hive tag
  hive name: dr-general
  record name: my-rule
  tag: high-hit
  suppression:
    max_count: 1
    period: 1h
    is_global: true
    keys:
      - 'high-hit'
      - 'hive-tag'
```

### remove hive tag

Removes a tag from a Hive record.

```yaml
- action: remove hive tag
  hive name: dr-general
  record name: my-rule
  tag: high-hit
```