# Response Actions

## Overview

Actions in LimaCharlie Detection & Response () rules define what happens after a detection triggers. Common actions generate reports, tag sensors, and isolate networks. The `task` action is used often: it sends commands to an Endpoint Agent to interrogate the endpoint or to act on it. Use it to collect system information or to isolate a compromised endpoint. Suppression settings manage repetitive alerts because they limit how often an action runs.

> For more information on how to use Actions, read Detection & Response rules.

## Suppression

Suppression helps you manage repetitive or noisy alerts.

### Reduce Frequency

To limit how many times a specific Action runs in a period of time, use `suppression`. Every Action supports this feature.

Add a suppression descriptor to an Action like this:

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

In the example, the `evil-process-detected` detection is generated a maximum of one time each hour for each `FILE_PATH`. After the first `report` with a given `FILE_PATH`, the rule skips new `report` actions for the one hour period.

`is_global: true` makes the suppression operate globally in the Org (tenant). If the value is `false`, the suppression is scoped for each Sensor.

The `keys` parameter is a list of strings that support [templating](../4-data-queries/template-transforms.md). Together, the unique combination of the values of all these strings (ANDed) is the uniqueness key that this suppression rule uses. The `{{ .event.FILE_PATH }}` template in the keys makes the `FILE_PATH` of the event that generates this `report` part of the key. The constant string `evil process-detected` sets a value that is related to this specific detection. Without the `evil process-detected` component of the key, this suppression contains *all* actions that also specify only `{{ .event.FILE_PATH }}`. With `is_global: true` and a complex key set, you can suppress actions across many Actions and many D&R rules.

Key templates support three namespaces:

- `{{ .event.* }}` — fields from the event payload
- `{{ .routing.* }}` — routing metadata (sid, hostname, etc.)
- `{{ .mtd.* }}` — detection metadata from lookup operators (e.g., GeoIP country, threat intel category)

The `.mtd` namespace contains the metadata that lookup operators return in the detection. Suppression keys can therefore use derived values. This example uses the [IP Geolocation](../5-integrations/api-integrations/ip-geolocation.md) lookup to key suppression on the resolved country:

```yaml
detect:
  event: USER_LOGIN
  op: lookup
  path: event/SOURCE_IP
  resource: lcr://api/ip-geo

respond:
  - action: report
    name: first-login-from-country
    suppression:
      max_count: 1
      period: 720h
      is_global: true
      keys:
        - 'first-country'
        - '{{ .event.USER_NAME }}'
        - '{{ .mtd.lcr___api_ip_geo.country.iso_code }}'
```

The metadata key name comes from the resource name, with underscores in place of special characters. For more patterns, see [Behavioral Detection](../3-detection-response/behavioral-detection.md).

> Supported Time Period Formats
>
> LimaCharlie supports these formats for time periods: **ns**, **us** (or **µs**, both are accepted), **ms**, **s**, **m**, **h** (nanoseconds, microseconds, milliseconds, seconds, minutes, and hours, respectively)

### Threshold Activation

The other way to use suppression is the `min_count` parameter. When it is set, the action is suppressed until the cloud receives `min_count` activations in that period.

Here is an example:

```yaml
- action: report
  name: high-alerts
  suppression:
    min_count: 3
    max_count: 3
    period: 24h
```

In the example, the `high-alerts` detection is generated one time each hour, but only after the rule that contains the action matches 3 times in that period.

Use this to create higher order alerts. These alerts trigger a different type of detection, or send a page alert to a SOC, when more than X alerts occur on a single host in a period.

> Note: You must specify both `min_count` and `max_count` when you set a threshold.

### Variable Count

You can also increment a suppression by a value that is not one (`1`). Use the `count_path` parameter. It is a path (like `event/record/v`) to an integer that increments the suppression counter.

This is useful for billing alerts. You set a threshold activation (it means "alert me if above X"), and increments of billable values get to the threshold.

Here is an example:

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

The example alerts (it generates a detection) when the Strelka Extension bills 1MB (1024 x 1024 x 1) of bytes for the `bytes_scanned` SKU in 24h.

It increments the suppression counter by the billed value from `event/record/v`. The counter resets after 24h. When the value gets to 1MB, the rule alerts one time only.

## Available Actions

Actions specify what happens after a detection is found.

### add tag, remove tag

```yaml
- action: add tag
  tag: vip
  entire_device: false # defaults to false
  ttl: 30 # optional
```

Adds or removes Tags on the sensor.

#### Optional Parameters

The `add tag` action can take an optional `ttl` parameter. It is the number of seconds that the tag stays applied to the sensor.

The `add tag` action can also set the optional `entire_device` parameter to `true`. The new tag then applies to the entire Device ID: every sensor that shares this Device ID gets the tag and the relevant TTL. If the sensor has no Device ID, the sensor is still tagged.

Use this mechanism to synchronize changes across an entire device. A D&R rule can detect a behavior and then tag all sensors on the device, so that each sensor acts accordingly, for example to start full pcap.

For example, this applies the `full_pcap` to all sensors on the device for 5 minutes:

```yaml
- action: add tag
  tag: full_pcap
  ttl: 300
  entire_device: true
```

### add var, del var

Add or remove a value in the [sensor variables](../3-detection-response/sensor-variables.md) of a sensor. Detection rules can refer to these variables with the `[[variable_name]]` syntax.

```yaml
- action: add var
  name: my-variable
  value: <<event/VOLUME_PATH>>
  ttl: 30 # optional
```

The `add var` action can take an optional `ttl` parameter. It is the number of seconds that the variable stays in the state of the sensor. The `value` parameter supports lookback syntax (`<<path>>`) that extracts values from the event that triggers the rule.

For detailed usage, including how to read variables in detection rules, see [Sensor Variables](../3-detection-response/sensor-variables.md).

### extension request

Send an asynchronous request to an extension that the Organization subscribes to.

```yaml
- action: extension request
  extension name: dumper # name of the extension
  extension action: dump # action to trigger
  extension request:     # request parameters
    sid: '{{ .routing.sid }}'
    pid: event.PROCESS_ID
```

The `extension request` parameters change with the extension (see the schema of that extension). The `extension request` parameter is a [transform](../4-data-queries/template-transforms.md).

You can also specify a `based on report: true` parameter. When it is true (the default is false), the transform for the `extension request` uses the report of the most recent `report` action, not the original event. You MUST then put a `report` action *before* the `extension request`.

### isolate network

Isolates the sensor from the network persistently. If the sensor or host reboots, the sensor stays isolated. This action works only on platforms that support the `segregate_network` [sensor command](endpoint-commands.md#segregate_network).

```text
- action: isolate network
```

When you use network isolation, LimaCharlie blocks connections to all destinations other than the LimaCharlie cloud. You can then investigate, do remediation actions, and finally remove the isolation to start normal network operation again. The host keeps internet connectivity so that you can do those actions.

> The `segregate_network` command is stateless. If the endpoint reboots, the command is no longer in effect. The isolate network command in D&R rules is stateful. It sets a flag in the cloud that keeps the endpoint isolated after a reboot.

### seal

Seals the sensor persistently. If the sensor or host reboots, the sensor stays sealed. This action works only on platforms that support the `seal` [sensor command](endpoint-commands.md).

```text
- action: seal
```

A sealed sensor has tamper resistance. Tamper resistance stops direct changes to the installed EDR.

> The `seal` command is stateless. If the endpoint reboots, the command is no longer in effect. The seal command in D&R rules is stateful. It sets a flag in the cloud that keeps the endpoint sealed after a reboot.

### unseal

Removes the seal status of a sensor that was sealed with `seal`.

```text
- action: unseal
```

### output

Forwards the matched event to an Output identified by `name` in the `tailored` stream.

You can create granular Outputs for specific events.

The `name` parameter is the name of the Output.

Example:

```yaml
- action: output
  name: my-output
```

### rejoin network

Removes the isolation status of a sensor that was isolated with `isolate network`.

```text
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

Reports the match as a detection. A detection is an alert. Detections go to these destinations:

- The `detection` Output stream
- The organization's Detections page (if `insight` is enabled)
- The D&R rule engine, for chaining detections

The `name`, `metadata` and `detect_data` parameters support [string templates](../4-data-queries/template-transforms.md) like `detected {{ .cat }} on {{ .routing.hostname }}`. The context of the transform is the detection itself, not the original event. For example, refer to `.detect.event.USER_NAME` and not to `.event.USER_NAME`.

The `metadata` usually holds information about the rule, its author, remediation etc.

The `detect_data` usually extracts specific parts of the detected event into a known format that many detections can share, for example the `domain` field or the `hash` field.

#### Limiting Scope

To limit the scope of a `report`, put the prefix `__` (double underscore) on `name`. Chained D&R rules and Services
then see the detection, but the detection is *not* sent to the Outputs for storage.

Use this mechanism to automate behavior with D&R rules and not generate extra traffic that has no use.

#### Optional Parameters

The `priority` parameter, if set, must be an integer. It is added to the root of the detection report as `priority`.

The `metadata` parameter, if set, can include any data. It is added to the root of the detection report as `detect_mtd`. Use it for internal information such as reference numbers or URLs.

### task

```yaml
- action: task
  command: history_dump
  investigation: susp-process-inv
```

Sends the task in the `command` parameter to the sensor that sent the event under evaluation.

Give the optional `investigation` parameter to create a unique identifier. The identifier applies to the task and to the events that the sensor emits because of the task.

The `command` parameter supports [string templates](../4-data-queries/template-transforms.md) like `artifact_get {{ .event.FILE_PATH }}`.

> To view all possible commands, see [Endpoint Agent Commands](endpoint-commands.md)

### undelete sensor

Un-deletes a sensor that was deleted before.

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

Use this action with the `deleted_sensor` event to let sensors rejoin the fleet.

### wait

Adds a delay (a maximum of 1 minute) before the next response action runs.

Use this action if a previous response action must finish (for example a command or payload that `task` runs) before the next action can run.

> The `wait` action blocks all events from that sensor for the specified duration of time. This is because D&R rules run at wire-speed and in-order.

The `duration` parameter supports two types of values:

- A string that describes a duration, like `5s` for 5 seconds or `10ms` for 10 milliseconds, as defined by [the ParseDuration function](https://pkg.go.dev/time#ParseDuration).
- An integer that is a number of seconds.

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

Adds a tag to a Hive record. Use it to mark Hive records such as D&R rules automatically.

```yaml
- action: add hive tag
  hive name: dr-general
  record name: my-rule
  tag: high-hit
```

If you expect the rule to hit often, couple this action with a `suppression` statement. Suppression stops repeated tagging of the same rules:

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

### start ai agent

Starts a Claude AI session that does automated investigation, analysis, or response actions. For full documentation, see [AI Sessions](../9-ai-sessions/index.md).

This action supports two modes: **inline mode** (all parameters in the rule) and **definition mode** (a reference to a pre-configured AI agent from the Hive with `definition: hive://ai_agent/<name>`).

#### Inline Mode

```yaml
- action: start ai agent
  prompt: "Investigate this detection and provide a summary..."
  anthropic_secret: hive://secret/my-anthropic-key
```

#### Definition Mode

```yaml
- action: start ai agent
  definition: hive://ai_agent/my-triage-bot
```

This action starts a fully-managed Claude Code session. The session can investigate events, query LimaCharlie data with the auto-installed `limacharlie` CLI, and generate reports.

#### Required Parameters (Inline Mode)

| Parameter | Description |
|-----------|-------------|
| `prompt` | Instructions for Claude. Supports [template strings](../4-data-queries/template-transforms.md). |
| `anthropic_secret` | Your Anthropic API key. Use `hive://secret/<name>` to refer to a [Hive Secret](../7-administration/config-hive/secrets.md). |

#### Required Parameters (Definition Mode)

| Parameter | Description |
|-----------|-------------|
| `definition` | Reference to a pre-configured AI agent in the Hive: `hive://ai_agent/<name>`. |

#### Optional Parameters

| Parameter | Description |
|-----------|-------------|
| `name` | Session name. Supports template strings. (Inline mode only.) |
| `lc_api_key_secret` | LimaCharlie API key for org-level API access. Use `hive://secret/<name>`. (Inline mode only.) |
| `lc_uid_secret` | LimaCharlie User ID. Needed when `lc_api_key_secret` is a user API key. Use `hive://secret/<name>`. (Inline mode only.) |
| `idempotent_key` | Unique key that stops duplicate sessions. Supports template strings. (Inline mode only.) |
| `debounce_key` | Serializes sessions: only one active session for each key. New requests wait behind the active session and start when it ends. Supports template strings. (Both modes.) |
| `data` | Extract event fields to include in the prompt as JSON. (Inline mode only.) |
| `profile` | Inline session configuration (tools, model, limits, external MCP servers). (Inline mode only.) |
| `profile_name` | Refer to a saved profile by name. (Inline mode only.) |

#### Example: Inline Mode

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: mimikatz

respond:
  - action: report
    name: mimikatz-detected
  - action: start ai agent
    prompt: |
      A Mimikatz-related process was detected.
      Investigate the process tree, check for credential dumping activity,
      and provide a detailed incident report.
    anthropic_secret: hive://secret/anthropic-key
    lc_api_key_secret: hive://secret/lc-api-key
    idempotent_key: "{{ .routing.event_id }}"
    data:
      hostname: "{{ .routing.hostname }}"
      process: "{{ .event.FILE_PATH }}"
      command_line: "{{ .event.COMMAND_LINE }}"
    profile:
      allowed_tools:
        - Bash
        - Read
        - Grep
      max_turns: 50
      max_budget_usd: 5.0
      one_shot: true
```

#### Example: Definition Mode

```yaml
respond:
  - action: start ai agent
    definition: hive://ai_agent/l1-triage-bot
    debounce_key: "triage-{{ .routing.sid }}"
```

For detailed configuration options, see [D&R-Driven AI Sessions](../9-ai-sessions/dr-sessions.md).

---

## See Also

- [D&R Rules Overview](../3-detection-response/index.md)
- [Detection Operators](detection-logic-operators.md)
- [Endpoint Commands](endpoint-commands.md)
- [AI Sessions](../9-ai-sessions/index.md)
