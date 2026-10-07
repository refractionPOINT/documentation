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
- For [trusted installers](#self-updating-software-and-trusted-installers) and for [`on_enable`](#programs-that-are-already-running), a sensor version that supports them. An older sensor applies the rest of the policy and ignores the installers. It does not act on `on_enable`.
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
| `app_control_policy` | A policy. It says which sensors it covers (by platform and tag), the mode, the stance (allowlist or blocklist), whether to trust the OS vendor and what to do about programs that are already running. | [Policies](../../../7-administration/config-hive/app-control-policy.md) |
| `app_control_rule` | A rule. It allows or denies one path, signer, signing identifier, certificate-chain thumbprint or file hash, or names a trusted installer, for all policies or only the ones you name. | [Rules](../../../7-administration/config-hive/app-control-rule.md) |

A sensor gets the first enabled policy, ordered by `priority` and then by name, whose platform and tags match it. When the sensor starts a process, it checks the rules that apply to its policy in this order and stops at the first answer:

1. Deny rules.
2. Allow rules.
3. OS vendor trust (Apple platform binaries, Microsoft-signed binaries), unless the policy turns it off.
4. Trusted installers: a process started by a trusted installer, or a file one wrote. See [below](#self-updating-software-and-trusted-installers).
5. The stance. An allowlist denies anything not allowed. A blocklist allows anything not denied.

A deny rule always wins.

### Modes

| Mode | What the sensor does |
| --- | --- |
| `off` | Evaluates nothing. |
| `permissive` | Evaluates executions asynchronously after the process starts. Reports would-be blocks. Blocks nothing and adds no latency. |
| `permissive_sync` | Runs the same blocking path as `enforcing`, then always allows. The recommended last step before enforcing. |
| `enforcing` | Blocks executions the policy denies. |

## Self-updating software and trusted installers

A hash or path rule stops matching as soon as an updater ships a new binary. A `signer` rule survives updates, so prefer it. It cannot cover what an updater unpacks without a signature: helpers, installer custom actions, or in-house tools pushed by a deployment system. For those, add an **installer rule** that names the updater.

An installer rule is a record in the [`app_control_rule`](../../../7-administration/config-hive/app-control-rule.md#installer-rules) hive with `"action": "installer"`. It gives the named program two kinds of trust:

- **Processes it starts.** A process that matches the rule, and every process it starts after that, is a trusted installer. Whatever a trusted installer launches is allowed.
- **Files it writes.** A file a trusted installer wrote may run later, from any location and started by anyone. The sensor records the file by its digest, so a copy keeps the trust and a modified file loses it.

What it does not do:

- Deny rules still win.
- An installer rule does not allow the updater itself. The updater needs its own allow rule, or OS vendor trust, to run.
- It only has an effect under an `allowlist`. A blocklist already allows what no deny rule matches.
- Removing or editing the rule withdraws everything it trusted.
- An installer is named by `path`, `signer`, `signing_id` or `signer_root`, never by `sha256`. The hash of an updater is what its next update changes, so the hive refuses it.

An installer rule is broad: everything the updater starts, and everything it writes, is trusted. Name the narrowest identity that works, and review it like a signer rule.

Under an allowlist, a policy that names installers makes the sensor hash each program that nothing cheaper allowed, because only the digest says whether an installer wrote it. Those programs would be denied anyway, so the cost falls on executions that are about to be refused.

Caveats:

- The record of what installers wrote lives on the sensor. On macOS it is held in memory by the endpoint security extension, and it is lost when that extension restarts.
- Files an installer wrote before the policy arrived are not trusted, because the sensor did not see them written. See also [programs that are already running](#programs-that-are-already-running).

## Programs that are already running

A policy judges a program when it starts. Programs that were already running when the policy reached the sensor were never judged. The policy's `on_enable` setting says what the sensor does about them:

| Value | What the sensor does |
| --- | --- |
| `leave` | Nothing. The policy only applies to programs that start afterward. |
| `report` | Reports each running program the policy refuses, as an `APP_CONTROL_RESIDENT` event. Nothing is blocked or stopped. This is what the sensor does when the setting is omitted. |
| `terminate` | Reports them and stops them. It only stops anything while the policy's mode is `enforcing`. In any other mode it reports, like `report`. |

The sensor looks at running programs once for each policy generation it installs, and again when the sensor itself restarts. A change to the policy is a new generation. A mode of `off` does nothing.

The sensor checks the process creation time before it stops a process, so a reused process ID cannot be hit. Some programs are never stopped:

- Critical Windows processes, such as `csrss` and `wininit`, the sensor itself, and processes with a very low ID.
- On macOS, Apple platform binaries.
- A program that is refused only because no rule matched it, when the policy names installers. The lineage that would have allowed it is only held while the installer runs, so the sensor reports it and leaves it alone. A deny rule still stops it.

!!! warning "Terminate stops programs"
    With `terminate` in an `enforcing` policy, saving the policy stops the running programs it refuses as soon as sensors receive it, and again whenever a sensor restarts. Read the `APP_CONTROL_RESIDENT` events from a `report` first, and only then switch to `terminate`.

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

## Lockdown

**Lock down host…** on a sensor page, or in the sensor list's bulk actions, requests incident-response containment through Application Control. The host can still use the network. Application Control enforces on **Windows and macOS only**; the bulk dialog skips other platforms, including Linux.

The console creates a reserved, explicitly enabled `lockdown` policy in `app_control_policy` before adding the sensor tag `appctl-lockdown`:

```yaml
priority: -2  # Example only: must be lower than every other policy, including install-mode.
platforms: []
tags: [appctl-lockdown]
mode: enforcing
stance: allowlist
trust_os_vendor: true
on_enable: terminate
```

The console chooses a priority strictly lower than every other policy, including disabled policies and the reserved `install-mode` policy. It refuses if the lowest possible priority is already occupied. It creates the record conditionally so an existing policy is not overwritten; an altered or disabled lockdown policy needs an explicit repair before containment starts. Repair affects all hosts carrying the lockdown tag.

When the policy reaches the host:

- OS-vendor software and the LimaCharlie sensor can keep running.
- Enabled, unexpired Application Control rules apply if their `policies` list is empty (every policy) or names `lockdown`. Allow rules authorize software; deny rules still take precedence. Rules scoped only to the host's ordinary policy do not carry over.
- Applicable trusted-installer rules can also allow installer descendants and files written by those installers. Review these rules when defining containment. Already-running installer descendants whose lineage is no longer retained are reported and left running unless a deny rule matches, as described in [Programs that are already running](#programs-that-are-already-running).
- Other running programs refused by the policy are reported and terminated. New executions refused by the policy are blocked.

Use the Rules tab or rule editor to name `lockdown` when authorizing incident-response tools specifically during containment. A signer or path allow rule can authorize more software than a single-file hash rule; choose the scope deliberately.

The dialog requires a reason. It stores a short URI-encoded reason in a companion sensor tag, visible in sensor tags, events and tag audit records. The reason tag shares any chosen TTL and is removed on release. Do not put secrets in the reason. By default, containment has **no user-selected TTL** and requires an explicit release; you can choose a limited duration instead. Changes take effect on the next sensor sync, so the presence of a tag is not confirmation that the sensor has already applied containment. The sensor-page banner checks that the lockdown policy remains applicable.

**Release lockdown** removes the tag, checking the host's current tags even if the sensor list is stale. The host receives its next matching enabled policy on its next sync. If install mode is still tagged and matches, that policy can apply again; install mode cannot override lockdown while both tags are present. Terminated programs are not restarted.

!!! warning "Keep a fallback policy"
    Keep an enabled policy that matches the host after release. If no other policy matches, the sensor keeps enforcing the last policy it received, including lockdown. Deleting or disabling the lockdown policy does not guarantee release either. Use a matching replacement policy, or set enforcement to `off` and let the sensor sync before removing the policy.

### Automate lockdown with D&R

First create the reserved policy **once per organization** using **Set up lockdown** on the Policies tab. This only sets up the policy; it does not tag hosts. Starting lockdown from a host dialog also creates it. Keep the policy enabled and correctly configured before relying on automation: adding a tag alone does not create or repair the policy.

A D&R [add tag response](../../../8-reference/response-actions.md#add-tag-remove-tag) with `tag: appctl-lockdown` requests lockdown automatically. Use a sensor event as the trigger so the response can identify the host. The following example locks down a host executing a confirmed malicious file; replace the placeholder hash and adapt the trigger to your incident signal before enabling it:

```yaml
detect:
  event: NEW_PROCESS
  op: is
  path: event/HASH
  value: REPLACE_WITH_CONFIRMED_MALICIOUS_SHA256
respond:
  - action: add tag
    tag: appctl-lockdown
    ttl: 3600
```

Here `ttl: 3600` gives the tag a one-hour lifetime. `ttl` is optional and measured in seconds; **omit that line to require explicit release**. Repeated tagging can extend the lifetime. Automated tagging does not require the console dialog's reason or add its companion reason tag. Include incident context in your detection reports or case records.

The console action needs `app_control.get`, `app_control.set`, and `sensor.tag`, and an Application Control subscription. Policy-only setup needs Application Control read/write access. Automation must be authorized to tag the sensor. Restrict `sensor.tag` access: anyone who can add or remove this tag can request or release containment.

## Reading would-be blocks

Application Control reports through these events, available on Windows and macOS. See the [EDR events reference](../../../8-reference/edr-events.md#app_control_denied) for the full fields.

`APP_CONTROL_DENIED` means the policy denied an execution. If `APP_CONTROL_IS_ENFORCED` is `1`, the sensor blocked it. If it is `0`, the sensor is in `permissive` or `permissive_sync` and only reports what it would have blocked.

`APP_CONTROL_UNRESOLVED` means the sensor could not evaluate an execution and allowed it.

`APP_CONTROL_RESIDENT` means a program was already running when the policy arrived and the policy refuses it. No execution was refused, so it is a separate event and a detection on `APP_CONTROL_DENIED` does not fire for it. `APP_CONTROL_IS_ENFORCED` is `1` if the sensor stopped the program. See [Programs that are already running](#programs-that-are-already-running).

When the same program draws the same verdict repeatedly, the first occurrence is reported right away as `APP_CONTROL_DENIED` and the repeats within the next five minutes are folded into a single `APP_CONTROL_DENIED_SUMMARY` event. It carries `APP_CONTROL_COUNT` (the first occurrence included) and the first and last time seen in `APP_CONTROL_FIRST_TS` and `APP_CONTROL_LAST_TS`. A summary has its own event name, so a rule written against `APP_CONTROL_DENIED` is not triggered again for occurrences it was already told about.

Events carry the name of the policy that produced them in `APP_CONTROL_POLICY_LABEL`, which is the record name of the policy.

Useful fields on `APP_CONTROL_DENIED`:

| Field | Meaning |
| --- | --- |
| `FILE_PATH` | The program that was denied. |
| `HASH` | The file's SHA-256, when available. |
| `APP_CONTROL_SIGNER` | The signer the sensor saw. |
| `APP_CONTROL_SIGNING_ID` | The macOS code-signing identifier the sensor saw. |
| `APP_CONTROL_REASON` | Why the sensor reached the decision. |
| `APP_CONTROL_MATCHED_RULE` | Optional. The rule that matched, when there is one. |
| `APP_CONTROL_MATCHED_RULE_ID` | Optional. The id (record name) of the rule that matched. |
| `APP_CONTROL_POLICY_LABEL` | The name of the policy that produced the event. |
| `APP_CONTROL_SIGNATURE_STATUS` | What the signature check concluded: `1` valid, `2` unsigned, `3` invalid, `4` untrusted, `5` expired. |
| `APP_CONTROL_MODE` | The mode of the policy in effect, as a number: `0` off, `1` permissive, `2` permissive_sync, `3` enforcing. |
| `APP_CONTROL_GENERATION` | The generation of the policy the sensor was running. |

The events also carry who ran the program (`USER_ID`, `USER_NAME`), the launching process (`PARENT`), and, where the platform provides them, the vendor trust (`APP_CONTROL_VENDOR_TRUSTED`), the issuer and root certificate thumbprints on Windows (`APP_CONTROL_ISSUER_THUMBPRINT`, `APP_CONTROL_ROOT_THUMBPRINT`, which you can paste into a `signer_root` rule), and the application's identity: the bundle on macOS, the version resource on Windows. See the [EDR events reference](../../../8-reference/edr-events.md#app_control_denied) for all of them.

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
- Policy record names are limited to 128 bytes and rule ids to 64 bytes.
- A policy can list at most 64 tags.

## See Also

- [Application Control policies](../../../7-administration/config-hive/app-control-policy.md)
- [Application Control rules](../../../7-administration/config-hive/app-control-rule.md)
- [Sensor tags](../../../2-sensors-deployment/sensor-tags.md)
- [Config Hive overview](../../../7-administration/config-hive/index.md)
- [Permissions](../../../8-reference/permissions.md#application-control)
- [EDR events reference](../../../8-reference/edr-events.md#app_control_denied)
