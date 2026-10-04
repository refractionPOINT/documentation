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
