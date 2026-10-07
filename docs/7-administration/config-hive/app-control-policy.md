# Config Hive: Application Control Policies

The `app_control_policy` hive holds the policies of [Application Control](../../5-integrations/extensions/limacharlie/app-control.md). A policy decides which sensors it covers, whether it blocks or only reports, and what the default answer is for a program that no rule mentions. The rules themselves live in the [`app_control_rule`](app-control-rule.md) hive.

Both hives are partitioned by organization, like the other Config Hive types. Each policy is one record. The record name is the policy name, up to 128 bytes, and rules refer to it by that name.

## Format

```json
{
    "priority": 10,
    "platforms": ["windows"],
    "tags": ["app-control-enforce"],
    "mode": "enforcing",
    "stance": "allowlist",
    "trust_os_vendor": true,
    "on_enable": "report"
}
```

| Field | Required | Description |
| --- | --- | --- |
| `priority` | No | Integer, default `0`. A lower number is evaluated first. Policies with the same priority are ordered by record name, ascending. |
| `platforms` | No | List of `windows` and `macos`. A sensor matches if it runs any one of them. Empty or omitted means every supported platform. |
| `tags` | No | List of sensor tags. A sensor matches only if it carries all of them. Empty or omitted matches any sensor. At most 64 tags, each at most 256 bytes, with no duplicates and no leading or trailing whitespace. |
| `mode` | Yes | `off`, `permissive`, `permissive_sync` or `enforcing`. See [Modes](#modes). |
| `stance` | Yes | `allowlist` or `blocklist`. There is no default, so you always choose one on purpose. See [Stance](#stance). |
| `trust_os_vendor` | No | Boolean, default `true`. When `true`, binaries signed by the operating system vendor are implicitly allowed: Apple platform binaries on macOS and Microsoft-signed binaries on Windows. Deny rules still win. |
| `on_enable` | No | `leave`, `report` or `terminate`. What the sensor does about programs that are already running when the policy arrives. When omitted, the sensor reports them. A blank value is refused. See [Programs that are already running](#programs-that-are-already-running). |

Keywords are case-sensitive and must be lowercase exactly as shown. Unknown fields are refused when you save the record.

!!! warning "A locked-out allowlist is refused"
    An `enforcing` policy with stance `allowlist` and `trust_os_vendor: false` is refused on save. Sensors refuse to enforce an allowlist that does not trust the operating system vendor, so the policy would never take effect.

## Which policy a sensor gets

A sensor receives one policy. LimaCharlie takes the enabled policies, orders them by `priority` and then by record name, and gives the sensor the first one whose `platforms` and `tags` both match. Policies later in the order are ignored for that sensor.

- A sensor that matches no policy is left alone.
- A policy with no `platforms` and no `tags` matches every Windows and macOS sensor. Give it the highest `priority` number so that narrower policies are checked first.
- Disabled records are skipped.

Because the first match wins, you stage a rollout by putting narrow policies (a pilot tag) ahead of a broad one. See [Staged rollout by tag](#staged-rollout-by-tag).

## Modes

| Mode | Behavior |
| --- | --- |
| `off` | The sensor evaluates nothing. |
| `permissive` | The sensor evaluates each execution asynchronously, after the process has started. It reports would-be blocks and blocks nothing. It adds no latency to process start. |
| `permissive_sync` | The sensor runs the same blocking path as `enforcing`, then always allows. Nothing is blocked. Use this as the last soak step before enforcing. |
| `enforcing` | The sensor blocks executions that the policy denies. |

In `permissive` and `permissive_sync`, a would-be block is reported as an `APP_CONTROL_DENIED` event with `APP_CONTROL_IS_ENFORCED` set to `0`. See [Reading would-be blocks](../../5-integrations/extensions/limacharlie/app-control.md#reading-would-be-blocks).

## Stance

The stance sets the answer for a program that no rule matches.

- `allowlist` denies anything not explicitly allowed. This is the strict model. Plan on an inventory phase before you enforce it.
- `blocklist` allows anything not explicitly denied. Under a blocklist an `allow` rule never changes an outcome, because the default is already allow. Use `allow` rules in a blocklist policy only if you intend to switch the stance later.

The sensor works through the policy in a fixed order and stops at the first answer:

1. Deny rules. A matching deny rule always blocks.
2. Allow rules.
3. OS vendor trust, if `trust_os_vendor` is `true`.
4. The stance.

## Programs that are already running

A policy judges a program when it starts. A program that was already running when the policy reached the sensor was never judged. `on_enable` says what the sensor does about those programs, once for each policy generation it installs and again when the sensor restarts.

| Value | Behavior |
| --- | --- |
| `leave` | The sensor does nothing about running programs. The policy applies only to programs that start afterward. |
| `report` | The sensor reports each running program the policy refuses as an `APP_CONTROL_RESIDENT` event and leaves it running. This is the behavior when the field is omitted. |
| `terminate` | The sensor reports them and stops them, but only while `mode` is `enforcing`. In any other mode it reports, as `report` does. |

Nothing happens when `mode` is `off`.

!!! warning "Terminate stops running programs"
    A policy with `"mode": "enforcing"` and `"on_enable": "terminate"` stops the running programs it refuses as soon as sensors receive it. Start with `report`, read the `APP_CONTROL_RESIDENT` events, and add rules for what you need to keep.

A program that is refused only because no rule matched it is reported but not stopped when the policy names [installer rules](app-control-rule.md#installer-rules). Critical Windows processes, the sensor itself and, on macOS, Apple platform binaries are never stopped. See [Programs that are already running](../../5-integrations/extensions/limacharlie/app-control.md#programs-that-are-already-running) for the details.

An `APP_CONTROL_RESIDENT` event is not an execution that was refused, so a detection on `APP_CONTROL_DENIED` does not fire for it. See the [EDR events reference](../../8-reference/edr-events.md#app_control_resident).

## Permissions

Managing records in the `app_control_policy` hive requires:

- `app_control.get` to read policies.
- `app_control.set` to create, edit and delete policies and their metadata.

See [Permissions](../../8-reference/permissions.md#application-control).

## Examples

All examples use the CLI generic hive commands. Pass `--oid <oid>` if your CLI is not already pointed at the organization. Records created without metadata are enabled by default in this hive, and the examples pass `--enabled` anyway so the intent is visible. Setting any metadata on create, such as a comment, tags or an expiry, without also passing `--enabled` stores the record disabled.

### A Windows allowlist policy

Save this as `windows-allowlist.json`. It covers every Windows sensor, evaluates but does not block, and trusts Microsoft-signed binaries.

```json
{
    "priority": 100,
    "platforms": ["windows"],
    "mode": "permissive",
    "stance": "allowlist",
    "trust_os_vendor": true
}
```

```bash
limacharlie hive set \
  --hive-name app_control_policy \
  --key windows-allowlist \
  --input-file windows-allowlist.json \
  --enabled
```

Rules with an empty `policies` list apply to this policy, as do rules that name `windows-allowlist`. The [rule page](app-control-rule.md#examples) has a matching rule set.

Validate a policy before you save it:

```bash
limacharlie hive validate \
  --hive-name app_control_policy \
  --key windows-allowlist \
  --input-file windows-allowlist.json
```

### Stopping unapproved running programs

This policy stops the running programs it refuses. Use it only after a `report` run has shown which programs that is, through `APP_CONTROL_RESIDENT` events, and you have added the rules for the ones you need.

```json
{
    "priority": 10,
    "tags": ["app-control-enforce"],
    "platforms": ["windows"],
    "mode": "enforcing",
    "stance": "allowlist",
    "trust_os_vendor": true,
    "on_enable": "terminate"
}
```

### Staged rollout by tag

Three policies move sensors through the rollout by tag. A sensor that carries `app-control-enforce` is blocked on violations. A sensor with `app-control-soak` runs the full blocking path without blocking. Every other Windows sensor only reports.

```json
{
    "priority": 10,
    "tags": ["app-control-enforce"],
    "platforms": ["windows"],
    "mode": "enforcing",
    "stance": "allowlist",
    "trust_os_vendor": true
}
```

Saved under the key `windows-1-enforce`.

```json
{
    "priority": 20,
    "tags": ["app-control-soak"],
    "platforms": ["windows"],
    "mode": "permissive_sync",
    "stance": "allowlist",
    "trust_os_vendor": true
}
```

Saved under the key `windows-2-soak`.

```json
{
    "priority": 100,
    "platforms": ["windows"],
    "mode": "permissive",
    "stance": "allowlist",
    "trust_os_vendor": true
}
```

Saved under the key `windows-3-observe`.

Priority 10 is checked first, so a sensor tagged both `app-control-enforce` and `app-control-soak` is enforcing. To promote a machine, add the next tag and remove the old one using [sensor tags](../../2-sensors-deployment/sensor-tags.md). The change reaches the sensor on its next sync.

The record names here are only labels. The `priority` values decide the order, and the names only break ties.

### Standing down

Deleting a policy, or unsubscribing from the extension, does not disarm sensors that already hold a policy. They keep enforcing what they last received. To stand enforcement down, set the policy to `mode: off` and let sensors sync before you delete anything.

```bash
limacharlie hive set \
  --hive-name app_control_policy \
  --key windows-1-enforce \
  --input-file windows-off.json \
  --enabled
```

where `windows-off.json` is the same policy with `"mode": "off"`.

## Limits

- Record name: 128 bytes.
- Tags per policy: 64, each at most 256 bytes.
- Rules that apply to a single policy: 10,000.

## See Also

- [Application Control](../../5-integrations/extensions/limacharlie/app-control.md)
- [Application Control rules](app-control-rule.md)
- [Sensor tags](../../2-sensors-deployment/sensor-tags.md)
- [Config Hive overview](index.md)
