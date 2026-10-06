# Application Control

## Overview

Application Control lets you decide which programs may run on your endpoints. You write an allowlist (only approved software runs) or a blocklist (everything runs except what you deny), and the LimaCharlie sensor enforces it at the moment a process starts.

- Windows and macOS are supported. Linux is not.
- The policy is declarative. You describe the desired state in two [Config Hive](../../../7-administration/config-hive/index.md) types, and the extension reconciles it onto every matching sensor each time that sensor syncs.
- The LimaCharlie cloud signs each policy before it reaches a sensor, and the sensor verifies the signature.
- Each policy has a mode, so you can watch what would be blocked before you block anything.

## Requirements

- The `ext-app-control` extension subscribed in the organization. See [Enabling the extension](#enabling-the-extension).
- Endpoint agent **5.4.0** or later. [Upgrade](../../../2-sensors-deployment/endpoint-agent/versioning-upgrades.md) older sensors first.
- Windows or macOS.
- The `app_control.get` and `app_control.set` [permissions](../../../8-reference/permissions.md#application-control) to read and write policies.

## Enabling the extension

Open the Application Control page in the Add-Ons marketplace, choose the organization and select **Subscribe**.

Subscribing installs a managed D&R rule named `ext-app-control-sync`. That rule reconciles policy onto each sensor every time it syncs. Leave it in place. The extension re-creates it if it drifts and removes it when you unsubscribe.

!!! note
    Subscribing changes nothing on its own. A sensor is left untouched until a policy matches it.

## How it works

Two hives hold the configuration. Both are partitioned by organization.

| Hive | One record is | Page |
| --- | --- | --- |
| `app_control_policy` | A policy. It says which sensors it covers (by platform and tag), the mode, the stance (allowlist or blocklist) and whether to trust the OS vendor. | [Policies](../../../7-administration/config-hive/app-control-policy.md) |
| `app_control_rule` | A rule. It allows or denies one path, signer, signing identifier, certificate-chain thumbprint or file hash, for all policies or only the ones you name. | [Rules](../../../7-administration/config-hive/app-control-rule.md) |

A sensor gets the first enabled policy, ordered by `priority` and then by name, whose platform and tags match it. When the sensor starts a process, it checks the rules that apply to its policy in this order and stops at the first answer:

1. Deny rules.
2. Allow rules.
3. OS vendor trust (Apple platform binaries, Microsoft-signed binaries), unless the policy turns it off.
4. The stance. An allowlist denies anything not allowed. A blocklist allows anything not denied.

A deny rule always wins.

### Modes

| Mode | What the sensor does |
| --- | --- |
| `off` | Evaluates nothing. |
| `permissive` | Evaluates executions asynchronously after the process starts. Reports would-be blocks. Blocks nothing and adds no latency. |
| `permissive_sync` | Runs the same blocking path as `enforcing`, then always allows. The recommended last step before enforcing. |
| `enforcing` | Blocks executions the policy denies. |

## Rolling out

Start in a mode that cannot block and move forward only once the reports are quiet. Tags make this easy because a policy can target a tag, and moving a sensor between stages is a tag change. The [policy page](../../../7-administration/config-hive/app-control-policy.md#staged-rollout-by-tag) has the three policies for this flow.

1. **Observe in `permissive`.** Create an allowlist policy for the platform with no tag filter. Add the rules you already know you need (your software publishers, your standard install locations). Every execution that the policy would deny shows up as an `APP_CONTROL_DENIED` event with `APP_CONTROL_IS_ENFORCED` set to `0`. Nothing is blocked and process start is not slowed.
2. **Fix the rules.** Read the would-be blocks (see [Reading would-be blocks](#reading-would-be-blocks)). For each legitimate program, add an allow rule. Prefer a `signer` rule for software that updates, and use a `path` rule only for locations ordinary users cannot write to. Repeat until the legitimate noise is gone. Use a [temporary exception](../../../7-administration/config-hive/app-control-rule.md#a-temporary-exception) for one-off cases.
3. **Soak a pilot in `permissive_sync`.** Add a policy that targets a pilot tag, such as `app-control-soak`, in `permissive_sync`. These sensors run the full blocking path but still allow everything. This is the last chance to find a problem before blocking.
4. **Enforce the pilot.** Add a policy with a lower priority number than the other two that targets `app-control-enforce` in `enforcing`. Tag a small group of machines and watch them.
5. **Widen.** Tag more machines. Keep a broad `permissive` policy at the end of the order so that untagged machines keep reporting.

To step back at any point, set the policy to `permissive` or `off`, or remove the tag so that the sensor falls through to the broad `permissive` policy. A sensor that no longer matches any policy keeps the last policy it received, so keep that broad policy in place. The change reaches sensors on their next sync.

!!! warning "Deleting does not disarm"
    Removing a policy, or unsubscribing from the extension, does not disarm sensors that already hold a policy. They keep enforcing it. To stand enforcement down, set the policy to `mode: off` and let sensors sync before you remove anything.

!!! note
    An `enforcing` allowlist with `trust_os_vendor: false` is refused on save, because a sensor cannot apply it.

## Install mode

Install mode lets you put one host, or a selection of hosts, in a temporary window where Application Control only reports and never blocks. Use it to install or update software on an endpoint that an `enforcing` policy would otherwise stop, then review what ran. When the window ends the host goes back to its normal policy on its own.

### Starting install mode

- **One host.** Open the sensor in the web console and select **App Control install mode...**.
- **Several hosts.** In the sensors list, select the hosts and choose **App Control install mode...** from the bulk actions. **End App Control install mode** is next to it.

Choose 1 hour, 4 hours, 24 hours, or a custom number of whole hours up to 168. Starting again on a host that is already in install mode restarts its window. While a window is on, the sensor page shows the time left, with **Restart window...** and **End install mode**.

The action appears only when the organization is subscribed to the `ext-app-control` extension and you hold `app_control.get`, `app_control.set` and `sensor.tag`. Install mode applies to Windows and macOS hosts, because Application Control does not run on other platforms. A change reaches the host the next time it syncs.

### How it works

Install mode uses nothing beyond what this page already describes. It is a policy and a sensor tag:

| Piece | What it is |
| --- | --- |
| The `install-mode` policy | A reserved policy record in `app_control_policy`: `mode: permissive`, `stance: allowlist`, `trust_os_vendor: true`, no platform filter, matching the tag `appctl-install-mode`. Its `priority` is one below every other policy, so a sensor resolves it first. |
| The `appctl-install-mode` tag | Added to the host with a time to live equal to the window. A host that carries it gets the `install-mode` policy. When the tag expires, the host matches its normal policy again. |
| The `appctl-install-mode-until-<epoch seconds>` tag | Added in the same call with the same time to live. It records when the window ends so the console can show the time left. It expires together with the tag that does the work. |

Because the `install-mode` policy is `permissive`, executions that your normal policy would have denied are reported as `APP_CONTROL_DENIED` events with `APP_CONTROL_IS_ENFORCED` set to `0`. Read them as described in [Reading would-be blocks](#reading-would-be-blocks) to decide which software to allow afterwards.

### The `install-mode` policy

The console creates the policy the first time you start install mode. It appears on the **Policies** tab with a **System: install mode** badge. For install mode to work the policy must stay enabled, in a mode that does not enforce, matching only the `appctl-install-mode` tag, with no platform filter, and ordered before every other enabled policy. If a policy is later created with a lower `priority` number, or the record is edited into something that would not work, the Policies tab flags it with **Needs attention**, and starting install mode lists what is wrong and offers to repair the policy. The console never starts a window on top of a policy that would still block.

If another policy already has the lowest possible priority (`-2147483648`), no policy can be ordered before it. Raise that policy's `priority` number first.

Deleting the `install-mode` policy stops install mode from working until the policy exists again. Starting install mode on a host recreates it. Hosts that are in a window when you delete it return to their normal policy.

### Without the console

Install mode is not a separate feature, so you can do the same through the API. Create the `install-mode` policy with the fields above and a `priority` below your other policies, then add the `appctl-install-mode` tag to a sensor with the `ttl` parameter of the sensor tag API, which is a number of seconds. See [Sensor tags](../../../2-sensors-deployment/sensor-tags.md). The countdown in the console needs the `appctl-install-mode-until-<epoch seconds>` tag as well. Without it the console still shows the host as in install mode, but reports that no end time is known.

## Reading would-be blocks

Application Control reports through two events, available on Windows and macOS. See the [EDR events reference](../../../8-reference/edr-events.md#app_control_denied) for the full fields.

`APP_CONTROL_DENIED` means the policy denied an execution. If `APP_CONTROL_IS_ENFORCED` is `1`, the sensor blocked it. If it is `0`, the sensor is in `permissive` or `permissive_sync` and only reports what it would have blocked.

`APP_CONTROL_UNRESOLVED` means the sensor could not evaluate an execution and allowed it.

Useful fields on `APP_CONTROL_DENIED`:

| Field | Meaning |
| --- | --- |
| `FILE_PATH` | The program that was denied. |
| `HASH` | The file's SHA-256, when available. |
| `APP_CONTROL_SIGNER` | The signer the sensor saw. |
| `APP_CONTROL_SIGNING_ID` | The macOS code-signing identifier the sensor saw. |
| `APP_CONTROL_REASON` | Why the sensor reached the decision. |
| `APP_CONTROL_MATCHED_RULE` | Optional. The rule that matched, when there is one. |
| `APP_CONTROL_MODE` | The mode of the policy in effect, as a number: `0` off, `1` permissive, `2` permissive_sync, `3` enforcing. |
| `APP_CONTROL_GENERATION` | The generation of the policy the sensor was running. |

To turn would-be blocks into something you can list and count, write a D&R rule that reports them:

```yaml
detect:
  event: APP_CONTROL_DENIED
  op: is
  path: event/APP_CONTROL_IS_ENFORCED
  value: 0
respond:
  - action: report
    name: app-control-would-block
```

Group the resulting detections by `FILE_PATH` or signer to see which programs matter most. A signer that appears on many machines is a candidate for a `signer` allow rule. A path seen on one machine is usually a one-off. To alert on actual blocks instead, match `1` and change the report name.

Watch `APP_CONTROL_UNRESOLVED` during the `permissive_sync` soak. Each one is an execution the sensor let through because it could not check it in time, for example when the file hash was not available.

## Blocking a file from the console

Wherever the web console shows a SHA-256 hash, you can block that exact file with one action, without writing a rule by hand. **Block with Application Control** is offered on:

- the event detail panel (sensor timeline and the Query Console), as a button for the event's own `HASH` and as an action on any hash field in the event JSON;
- the detection viewer, on the hash fields of the detection's event;
- the sensor's file hash view, and the modules of a process.

The action opens a confirmation that shows the hash and, when the event has one, the file path. You can add a comment and, optionally, an expiry. Confirming creates a rule in `app_control_rule`:

```json
{
    "action": "deny",
    "kind": "sha256",
    "value": "<the hash, in lowercase hex>"
}
```

The rule applies to every policy. Its record name is `deny-sha256-` followed by the first 16 hex characters of the hash, for example `deny-sha256-0123456789abcdef`, so blocking the same file twice never creates two rules. If that name already belongs to a different rule, the console uses the next free name (`...-2`, `...-3`). The rule is created, never overwritten, and it is stored enabled.

The dialog also tells you:

- **Already blocked.** An enabled deny for the same hash that applies to every policy and does not expire is already there, so nothing is created. A deny that is disabled, expired, limited to some policies, or temporary does not count: the dialog mentions it and still offers to create the block.
- **Only enforcing blocks.** A deny rule blocks only on sensors whose policy is in `enforcing` mode. Under `permissive` and `permissive_sync` the sensor reports the execution it would have blocked. If no enabled policy is in `enforcing` mode, the dialog warns that the rule will not block anything yet.
- **Allow rules.** An allow rule for the same hash does not defeat the block, because a deny always wins.

The action is offered only when the organization is subscribed to the `ext-app-control` extension and you hold `app_control.get` and `app_control.set`. The console reads the existing rules to choose a free name and to tell you when a file is already blocked, so `app_control.set` alone is not enough.

## Managing from the CLI

The two hives work with the generic hive commands.

```bash
# List the policies and rules.
limacharlie hive list --hive-name app_control_policy
limacharlie hive list --hive-name app_control_rule

# Create or update a rule.
limacharlie hive set \
  --hive-name app_control_rule \
  --key allow-program-files \
  --input-file rule.json \
  --enabled
```

Examples of both record types are on the [policy](../../../7-administration/config-hive/app-control-policy.md#examples) and [rule](../../../7-administration/config-hive/app-control-rule.md#examples) pages.

## Permissions

| Permission | Allows |
| --- | --- |
| `app_control.get` | Read policies and rules. |
| `app_control.set` | Create, edit and delete policies and rules, and their metadata. |

By default the Owner, Administrator and Operator roles have both. The Viewer role has `app_control.get`.

Two console actions need more than the App Control permissions alone. [Install mode](#install-mode) also needs `sensor.tag`, because it tags the host. [Blocking a file from the console](#blocking-a-file-from-the-console) needs both `app_control.get` and `app_control.set`.

## Limits

- 10,000 rules may apply to a single policy.
- Policy record names are limited to 256 bytes and rule ids to 64 bytes.
- A policy can list at most 64 tags.

## See Also

- [Application Control policies](../../../7-administration/config-hive/app-control-policy.md)
- [Application Control rules](../../../7-administration/config-hive/app-control-rule.md)
- [Sensor tags](../../../2-sensors-deployment/sensor-tags.md)
- [Config Hive overview](../../../7-administration/config-hive/index.md)
- [Permissions](../../../8-reference/permissions.md#application-control)
- [EDR events reference](../../../8-reference/edr-events.md#app_control_denied)
