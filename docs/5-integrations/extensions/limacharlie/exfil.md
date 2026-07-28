# Exfil (Event Collection)

The Exfil Extension helps you manage which real-time [events](../../../8-reference/edr-events.md) the EDR sensors send to LimaCharlie. By default, LimaCharlie Sensors send events to the cloud based on a standard profile. This extension makes those profiles available for customization. With the Exfil extension you can customize Event Collection from LimaCharlie Sensors. You can also mitigate sensors with high I/O or large [detection and response](../../../3-detection-response/examples.md) rulesets.

> Event Collection Rule Synchronization
>
> LimaCharlie synchronizes Exfil (or Event Collection) rule configurations with sensors every few minutes.

## Enabling the Exfil Extension

To enable the Exfil extension, do these steps:

1. Open the [Exfil extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-exfil) in the marketplace.
2. Select the Organization for which you want the extension.
3. Select **Subscribe**.

![exfil 1.png "image(231).png"](../../../assets/images/exfil-1.png "image(231).png")

After you select Subscribe, the Exfil extension becomes available almost immediately.

## Using the Exfil Extension

After you enable the extension, an **Event Collection** option is under **Sensors** in the LimaCharlie web UI.

![exfil 2.png "image(227).png"](../../../assets/images/exfil-2.png "image(227).png")

There are three rule options within the Exfil extension:

- **Event Collection Rules** manage the events that the Sensor sends to the LimaCharlie cloud.
- **Performance Rules** are useful for high I/O servers, but they can affect event accuracy. This feature is available only on Windows Sensors.
- **Watch Rules** give conditional operators for an event. You can specify a list of sensors to help manage high-volume events. The conditional operators for Watch Rule events include:

  - The **event** itself, such as `MODULE_LOAD`.
  - The **path** in the event component that LimaCharlie evaluates, such as `FILE_PATH`.
  - The **operator** that compares the path and the value.
  - The **value** that the operator compares.

A sample **Watch Rule** is:

```text
Event: MODULE_LOAD
Path: FILE_PATH
Operator: ends with
Value: wininet.dll
```

This rule configures the sensor or sensors to send *only* `MODULE_LOAD` events where the `FILE_PATH` ends with the value `wininet.dll`.

### Watch Rule Fields

When you author Watch Rules outside of the web UI (REST API, hive, or git-sync), the schema is strict about types. The most common cause of a Watch Rule that does not apply is a scalar where the schema needs a list.

| Field                | Type                                                        | Required |
|----------------------|-------------------------------------------------------------|----------|
| `event`              | string (single event name, e.g. `FILE_CREATE`)              | yes      |
| `operator`           | enum: `is`, `contains`, `starts with`, `ends with`          | yes      |
| `value`              | string                                                      | yes      |
| `path`               | **list** of strings                                         | yes      |
| `filters.platforms`  | **list** of strings (e.g. `[mac]`, `[windows]`, `[linux]`)  | yes      |
| `filters.tags`       | **list** of strings                                         | optional |

> Common gotcha
>
> `path`, `filters.platforms`, and `filters.tags` must be YAML lists, not bare scalars. `path: FILE_PATH` fails validation. `path: [FILE_PATH]`, or the multi-line `- FILE_PATH` form, is correct. The same is true for `filters.platforms` and `filters.tags`.

### Watch Rule Operators

Watch Rules support exactly four operators. LimaCharlie compares the configured `value` **literally**, not as a pattern, against the string at `path` in the event:

| Operator      | Match condition                                                |
|---------------|----------------------------------------------------------------|
| `is`          | The field value exactly equals the configured value.            |
| `contains`    | The configured value appears anywhere in the field value.       |
| `starts with` | The field value starts with the configured value.               |
| `ends with`   | The field value ends with the configured value.                 |

The operators also have this behavior:

- **No regular expressions, globs, or wildcards.** LimaCharlie matches a value such as `^/Users/[^/]+/(Downloads|Desktop)/` character-for-character. This includes the `^`, `[`, `(`, and other characters. The value does not behave as a regex.
- **Case-insensitive.** LimaCharlie changes the configured value and the event field to lowercase before the comparison. Thus `wininet.dll` and `WININET.DLL` match.
- **String fields only.** LimaCharlie evaluates only string-typed event fields. It skips numeric fields at the configured `path`.
- **Unknown operators are dropped silently.** A Watch Rule with an `operator` that is not one of the four values above does not match any event. Use one of the supported operators above, or combine more than one Watch Rule, to express the condition that you need.

> Performance Rules
>
> You apply performance rules with a tag to a set of Sensors. These rules are useful for high I/O systems. You can set these rules with the web application or the REST API.

### Throughput Limits

If you enable *every* event for Exfil, this can produce a large amount of traffic. First, optimize the events that detection & response rules need, to make sure that all rules are active. Then give priority to the events that contribute to outputs, such as forwarded `DNS_REQUESTS`.

LimaCharlie tries to process all events in real time. If events fall behind, LimaCharlie puts them in a queue up to a limit. The queue can be dropped if it reaches that limit, for example during a long burst or if you enable *all* events at the same time. LimaCharlie then sends an error to the platform logs.

If you see event collection errors, it is possible that you must do one of these actions:

1. Reduce the number of events that you collect.
2. Reduce the number of rules that you run, or their complexity.
3. Use Watch Rules that return only the events with specific values.
4. Enable the IR mode (below).

#### Afterburner

Before LimaCharlie drops a queue with a backlog, it tries to increase performance. It enters a special mode with the name "afterburner". This mode addresses one common cause of a large influx of data: processes that start again and again. This occurs when software is built, because executables such as `devenv.exe` or `git` can be called hundreds of times per second. The afterburner mode tries to (1) de-duplicate those processes and (2) assess only each one through the D&R rules and Outputs.

#### IR Mode

The afterburner mode does not address all possible causes or situations. For these, LimaCharlie supplies "IR mode". To enable this mode, tag a LimaCharlie sensor with the tag `ir`. "IR mode" is for users who must record a large number of events, but do not need to run D&R rules over all of them. "IR mode" does not de-duplicate events. Also, LimaCharlie runs D&R rules *only* against the following event types:

1. `CODE_IDENTITY`
2. `DNS_REQUEST`
3. `NETWORK_CONNECTIONS`
4. `NEW_PROCESS`

IR mode gives a balance between the record of all events and basic D&R rule capabilities.

## Configuration via Hive

The full Exfil configuration is stored under the `extension_config` hive at the key `ext-exfil`. You can manage it with the web UI, with the REST actions below, with [git-sync](git-sync.md), or directly with the LimaCharlie CLI.

This is a complete, valid Watch Rule:

```yaml
exfil_rules:
  watch:
    Mac User Downloads File Events:
      event: FILE_CREATE
      operator: contains
      value: /Downloads/
      path:
        - FILE_PATH
      filters:
        platforms:
          - mac
        tags:
          - file-watch
```

The example uses the YAML list form (`-`) for `path`, `filters.platforms`, and `filters.tags`. For the full schema, see [Watch Rule Fields](#watch-rule-fields).

### Validate Before Pushing

If a hive `set` against `extension_config/ext-exfil` fails or times out with no clear error, the most likely cause is a schema-validation failure. Before you write a config, you can test it against the live schema:

```bash
limacharlie hive validate \
  --hive-name extension_config \
  --key ext-exfil \
  --input-file my-exfil-config.yaml \
  --output yaml
```

An empty (`{}`) response means that the record is valid and that a subsequent `hive set` accepts it. Any other output describes the validation failure. Correct the bad field and run `validate` again until it returns empty.

`validate` is read-only. It never changes the stored configuration, whatever the result.

## Actions via REST API

You can send these REST API actions to the Exfil extension:

### List Rules

```json
{
  "action": "list_rules"
}
```

### Event Collection Rules

#### Add Event Collection Rule

```json
{
  "action": "add_event_rule",
  "name": "windows-vip",
  "events": [
    "NEW_TCP4_CONNECTION",
    "NEW_TCP6_CONNECTION"
  ],
  "tags": [
    "vip"
  ],
  "platforms": [
    "windows"
  ]
}
```

#### Remove Event Collection Rule

```json
{
  "action": "remove_event_rule",
  "name": "windows-vip"
}
```

### Watch Rules

#### Add Watch Rule

```json
{
  "action": "add_watch",
  "name": "wininet-loading",
  "event": "MODULE_LOAD",
  "operator": "ends with",
  "value": "wininet.dll",
  "path": [
    "FILE_PATH"
  ],
  "tags": [
    "server"
  ],
  "platforms": [
    "windows"
  ]
}
```

#### Remove Watch Rule

```json
{
  "action": "remove_watch",
  "name": "wininet-loading"
}
```

### Performance Rules

#### Add Performance Rule

```json
{
  "action": "add_perf_rule",
  "name": "sql-servers",
  "tags": [
    "sql"
  ],
  "platforms": [
    "windows"
  ]
}
```

#### Remove Performance Rule

```json
{
  "action": "remove_perf_rule",
  "name": "sql-servers"
}
```

## See Also

- [Compliance Frameworks](../../../9-ai-sessions/compliance/frameworks.md) -- Exfil rules are part of the recommended baseline of every framework. The `compliance-baseline-deploy` skill writes them under `data.exfil_rules.list` and keeps the existing default rules (for example, `default-chrome` and `default-linux`).
- [Compliance Gap Analysis](../../../9-ai-sessions/compliance/gap-analysis.md) -- Section A of the gap report lists the missing exfil events for each framework and for each platform, with the relevant control citations.
