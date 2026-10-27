# Sensor Cull

The Sensor Cull extension (`ext-sensor-cull`) deletes sensors that have not connected to your organization for a set number of days. It suits environments that enroll sensors repeatedly for short periods, such as autoscaling cloud fleets, VM templates and container nodes.

You define rules in the extension's configuration. Each rule picks a set of sensors (by tag, by [selector](../../../8-reference/sensor-selector-expressions.md), or both) and an inactivity limit in days. Once a day the extension checks every rule and deletes the sensors that match it and have been offline longer than its limit. You can also run all rules, or the rules with a given name, on demand.

!!! warning "Culling deletes sensors"
    A sensor deleted by a rule is removed from the organization. Scheduled runs do not ask for confirmation, and you cannot switch the extension to a dry-run mode. Check which sensors a rule's tag and selector match in the sensor list before you save it, and read [Rule safety](#rule-safety).

## Enabling the extension

Subscribe to `ext-sensor-cull` from the [Extensions page](https://app.limacharlie.io/add-ons/extension-detail/ext-sensor-cull) of the web UI, or with the CLI:

```bash
limacharlie extension subscribe --name ext-sensor-cull --oid <oid>
```

Subscribing installs a rule named `sensor-cull-recurring` in the `dr-service` hive. That rule schedules the daily run (see [How it runs](#how-it-runs)). Unsubscribing removes it.

## Using the web UI

Once subscribed, a **Sensor Cull** page appears under **Sensors** in the sidebar. It lists the rules in a table with the columns Name, Tag, Selector and Inactivity limit.

- **Add rule** opens a form with a name, a tag, a selector and the days of inactivity. The name and the days are required. You must fill in the tag, the selector, or both. The form only accepts an inactivity limit of 1 day or more.
- **Run all rules** (shown once at least one rule exists) asks for confirmation, then runs every rule immediately.
- Each row has edit and delete actions.

Adding, editing and deleting rules needs the `ext.conf.set` [permission](../../../8-reference/permissions.md). **Run all rules** needs `ext.request`.

## Configuration

The rules live in the `extension_config` [hive](../../../7-administration/config-hive/index.md), in the record named `ext-sensor-cull`. The record's `data` is an object with one key, `rules`, a list of rule objects. Reading the record needs `ext.conf.get`; writing it needs `ext.conf.set`.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `rule_name` | string | Yes | Name of the rule. It is not unique: several rules may share a name. |
| `ttl` | integer | Yes | Days a sensor can stay unconnected before the rule deletes it. Use 1 or more (see [Rule safety](#rule-safety)). |
| `tag` | string | One of `tag` or `selector` | Applies the rule to sensors that have this tag. |
| `selector` | string | One of `tag` or `selector` | A [sensor selector expression](../../../8-reference/sensor-selector-expressions.md) that picks the sensors the rule applies to. |

When a rule has both `tag` and `selector`, a sensor must match both. The extension rejects a configuration where a rule has no `rule_name`, or has neither `tag` nor `selector`. It does not check `ttl`.

Rules are positional. The extension identifies a rule by its place in the list, not by its name, so you can reuse a name across rules that target different sensors.

### Infrastructure as code

The same configuration as it appears in an IaC definition or a [Git Sync](git-sync.md) `hives/extension_config.yaml` file:

```yaml
hives:
    extension_config:
        ext-sensor-cull:
            data:
                rules:
                    - rule_name: Delete ephemeral sensors after 7 days
                      tag: ephemeral
                      ttl: 7
                    - rule_name: Delete Linux sensors after 120 days
                      selector: plat == linux
                      ttl: 120
                    - rule_name: Delete Windows sensors after 90 days unless tagged vip
                      selector: plat == windows and "vip" not in tags
                      ttl: 90
            usr_mtd:
                enabled: true
                expiry: 0
                tags: []
                comment: ""
```

### CLI

Put the `data` of the record in a file and set it:

```yaml
# sensor-cull.yaml
rules:
  - rule_name: Delete ephemeral sensors after 7 days
    tag: ephemeral
    ttl: 7
```

```bash
limacharlie hive set \
  --hive-name extension_config \
  --key ext-sensor-cull \
  --input-file sensor-cull.yaml \
  --enabled \
  --oid <oid>
```

Dry-run a configuration against the extension's validation before writing it:

```bash
limacharlie hive validate \
  --hive-name extension_config \
  --key ext-sensor-cull \
  --input-file sensor-cull.yaml \
  --oid <oid>
```

Read the current configuration:

```bash
limacharlie hive get --hive-name extension_config --key ext-sensor-cull --oid <oid>
```

`limacharlie extension config-get --name ext-sensor-cull` and `limacharlie extension config-set --name ext-sensor-cull --input-file sensor-cull.yaml` read and write the same record.

### Selectors

The extension builds one selector from the rule and asks the platform for the matching sensors:

| Rule | Selector sent |
| --- | --- |
| `tag: linux` | `` `linux` in tags `` |
| `selector: plat == windows` | `(plat == windows)` |
| `tag: prod` and `selector: plat == linux` | `` `prod` in tags and (plat == linux) `` |
| `selector: "*"` | `*` (every sensor) |
| `tag: prod` and `selector: "*"` | `` `prod` in tags `` |

The platform evaluates the selector with the same [expression language](../../../8-reference/sensor-selector-expressions.md) used elsewhere, so every operator on that page works in a rule. A selector that excludes a tag is valid, for example `"vip" not in tags`, or `plat == windows and "vip" not in tags` to cull Windows sensors that do not carry the `vip` tag. A selector the platform cannot parse makes the run fail with an error and deletes nothing for that rule.

The inactivity test is separate from the selector. The extension compares each sensor's last-seen time with `ttl` itself, after the platform returns the matching sensors, so express the inactivity limit with `ttl` and not in the selector.

## How it runs

- **Schedule.** The `sensor-cull-recurring` rule responds to the `24h_per_org` [scheduling event](../../../8-reference/schedule-events.md) and sends the extension a `run` request with no parameters, which runs every rule. LimaCharlie only generates `24h_per_org` for organizations that had at least one sensor online in the last 7 days.
- **Inactivity test.** For each sensor the rule selects, the extension compares the sensor's last-seen time (the `alive` value, in UTC) with the current time. The sensor is deleted when it was last seen more than `ttl` days ago. A sensor with no last-seen time is skipped.
- **Deletion.** The extension deletes each sensor through the LimaCharlie API, using the API key it received when you subscribed, not your credentials. A sensor that matches several rules is deleted once per run.
- **Large organizations.** The extension reads matching sensors 500 at a time and continues automatically until it has seen them all. Per-sensor failures are logged and reported as an error for the run, and the extension carries on with the other sensors.
- **No report.** The extension does not emit an event or keep a list of the sensors it deleted.

!!! note "Resource ACLs"
    The extension writes the `sensor-cull-recurring` rule with `acl_scopes: ["*"]`. On organizations that use [Resource ACLs](../../../7-administration/access/resource-acls.md), `*` stands for the scopes the extension's own API key is a member of when the rule fires, so an administrator controls how far scheduled runs reach by adding the key to a scope or removing it. See [Building Extensions](../../../6-developer-guide/extensions/building-extensions.md).

## Rule safety

- `ttl` is not validated by the extension. A rule with `ttl: 0`, or without `ttl`, treats every matching sensor that is not connected right now as expired and deletes it on the next run. The web UI refuses a limit below 1 day, but the API, the CLI and IaC do not.
- A rule that has only `selector: "*"` matches every sensor in the organization.
- A deleted sensor that later tries to reconnect is refused and produces a [`deleted_sensor`](../../../8-reference/platform-events.md#deleted_sensor) event. A rule can bring it back with [`undelete sensor`](../../../8-reference/response-actions.md#undelete-sensor), which would undo the cull.

## Actions

The extension has one action, `run`. Rules are managed by writing the [configuration](#configuration), not through requests. It does not support `get_rules`, `add_rule` or `del_rule`; those belonged to an earlier version of the extension.

### run

Runs the rules immediately, without waiting for the daily schedule. It is not impersonated: it runs with the extension's own permissions, and the caller needs `ext.request`.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `rule_name` | string | No | Run only the rules with this name. Without it, every rule runs. A name that no rule has runs nothing. |
| `continuation_token` | string | No | Used internally to resume a long run. Leave it empty. |

Run every rule:

=== "CLI"

    ```bash
    limacharlie extension request \
      --name ext-sensor-cull \
      --action run \
      --oid <oid>
    ```

=== "REST API"

    ```bash
    curl -s -X POST \
      "https://api.limacharlie.io/v1/extension/request/ext-sensor-cull" \
      -H "Authorization: Bearer $LC_JWT" \
      -d oid="<oid>" \
      -d action="run" \
      -d data='{}'
    ```

=== "D&R response"

    ```yaml
    - action: extension request
      extension name: ext-sensor-cull
      extension action: run
      extension request: {}
    ```

Run only the rules named `Delete Linux sensors after 120 days`:

=== "CLI"

    ```bash
    limacharlie extension request \
      --name ext-sensor-cull \
      --action run \
      --data '{"rule_name": "Delete Linux sensors after 120 days"}' \
      --oid <oid>
    ```

=== "REST API"

    ```bash
    curl -s -X POST \
      "https://api.limacharlie.io/v1/extension/request/ext-sensor-cull" \
      -H "Authorization: Bearer $LC_JWT" \
      -d oid="<oid>" \
      -d action="run" \
      -d data='{"rule_name": "Delete Linux sensors after 120 days"}'
    ```

=== "D&R response"

    ```yaml
    - action: extension request
      extension name: ext-sensor-cull
      extension action: run
      extension request:
        rule_name: '{{ "Delete Linux sensors after 120 days" }}'
    ```

The call returns once the first batch is processed. On a large organization the extension schedules the remaining batches itself.

## Permissions summary

| To | You need |
| --- | --- |
| Subscribe or unsubscribe | `ext.sub` |
| View rules | `ext.conf.get` |
| Add, edit or delete rules | `ext.conf.set` |
| Run rules on demand | `ext.request` |

See [Permissions](../../../8-reference/permissions.md) for the full list.
