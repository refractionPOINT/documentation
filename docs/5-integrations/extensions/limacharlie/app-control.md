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

The console and evidence reports use the following labels. Configuration and raw
JSON retain the API values.

| Console label | API value | What the sensor does |
| --- | --- | --- |
| Off | `off` | Evaluates nothing. |
| Audit | `permissive` | Evaluates executions asynchronously after the process starts. Reports would-be blocks. Blocks nothing and adds no latency. |
| Rehearsal | `permissive_sync` | Runs the same blocking path as `enforcing`, then always allows. The recommended last step before enforcing. |
| Enforcing | `enforcing` | Blocks executions the policy denies. |

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

1. **Observe in Audit (`permissive`).** Create an allowlist policy for the platform with no tag filter. Add the rules you already know you need (your software publishers, your standard install locations). Every execution that the policy would deny shows up as an `APP_CONTROL_DENIED` event with `APP_CONTROL_IS_ENFORCED` set to `0`. Nothing is blocked and process start is not slowed.
2. **Fix the rules.** Read the would-be blocks (see [Reading would-be blocks](#reading-would-be-blocks)). For each legitimate program, add an allow rule. Prefer a `signer` rule for software that updates, and use a `path` rule only for locations ordinary users cannot write to. Repeat until the legitimate noise is gone. Use a [temporary exception](../../../7-administration/config-hive/app-control-rule.md#a-temporary-exception) for one-off cases.
3. **Soak a pilot in Rehearsal (`permissive_sync`).** Add a policy that targets a pilot tag, such as `app-control-soak`, in `permissive_sync`. These sensors run the full blocking path but still allow everything. This is the last chance to find a problem before blocking.
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

The action appears only when the organization is subscribed to the `ext-app-control` extension and you hold `app_control.get`, `app_control.set` and `sensor.tag`. Install mode matters on Windows and macOS hosts only, because Application Control does not run on other platforms. The console warns you when a selected host is on another platform, and tags it anyway. A change reaches the host the next time it syncs.

### How it works

Install mode uses nothing beyond what this page already describes. It is a policy and a sensor tag:

| Piece | What it is |
| --- | --- |
| The `install-mode` policy | A reserved policy record in `app_control_policy`: `mode: permissive`, `stance: allowlist`, `trust_os_vendor: true`, no platform filter, matching the tag `appctl-install-mode`. Its `priority` is one below every other policy except the [lockdown](#lockdown) policy, which is ordered before it, so a sensor resolves it first. |
| The `appctl-install-mode` tag | Added to the host with a time to live equal to the window. A host that carries it gets the `install-mode` policy. When the tag expires, the host matches its normal policy again. |
| The `appctl-install-mode-until-<epoch seconds>` tag | Added in the same call with the same time to live. It records when the window ends so the console can show the time left. It expires together with the tag that does the work. |

Because the `install-mode` policy is `permissive`, executions that your normal policy would have denied are reported as `APP_CONTROL_DENIED` events with `APP_CONTROL_IS_ENFORCED` set to `0`. Read them as described in [Reading would-be blocks](#reading-would-be-blocks) to decide which software to allow afterwards.

### The `install-mode` policy

The console creates the policy the first time you start install mode. It appears on the **Policies** tab with a **System: install mode** badge. For install mode to work the policy must stay enabled, in a mode that does not enforce, matching only the `appctl-install-mode` tag, with no platform filter, and ordered before every other enabled policy except `lockdown`. If a policy is later created with a lower `priority` number, or the record is edited into something that would not work, the Policies tab flags it with **Needs attention**, and starting install mode lists what is wrong and offers to repair the policy. The console never starts a window on top of a policy that would still block.

Anyone who holds `sensor.tag` can add the `appctl-install-mode` tag to a host, with or without a time to live, and the `install-mode` policy then applies to that host ahead of every other policy. The `app_control.set` requirement is enforced by the console only. The **Policies** tab shows how many hosts carry the tag right now, so review that count and the hosts behind it regularly.

If another policy already has the lowest possible priority (`-2147483648`), no policy can be ordered before it. Raise that policy's `priority` number first.

Lockdown takes priority over install mode. A host that carries both the `appctl-lockdown` and `appctl-install-mode` tags stays in [lockdown](#lockdown) until the lockdown tag is removed.

Deleting the `install-mode` policy stops install mode from working until the policy exists again. Starting install mode on a host recreates it. Hosts that are in a window when you delete it return to their normal policy.

### Without the console

Install mode is not a separate feature, so you can do the same through the API. Create the `install-mode` policy with the fields above and a `priority` below your other policies (but above the `lockdown` policy, if you use it), then add the `appctl-install-mode` tag to a sensor with the `ttl` parameter of the sensor tag API, which is a number of seconds. See [Sensor tags](../../../2-sensors-deployment/sensor-tags.md). The countdown in the console needs the `appctl-install-mode-until-<epoch seconds>` tag as well. Without it the console still shows the host as in install mode, but reports that no end time is known.

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
- Other running programs refused by the policy are reported and terminated, except the programs that are never stopped, as listed in [Programs that are already running](#programs-that-are-already-running). New executions refused by the policy are blocked.

Use the Rules tab or rule editor to name `lockdown` when authorizing incident-response tools specifically during containment. A signer or path allow rule can authorize more software than a single-file hash rule; choose the scope deliberately.

The dialog requires a reason. It stores a short URI-encoded reason in a companion sensor tag, visible in sensor tags, events and tag audit records. The reason tag shares any chosen TTL and is removed on release. Do not put secrets in the reason. By default, containment has **no user-selected TTL** and requires an explicit release; you can choose a limited duration instead, as a whole number of hours up to 168. Changes take effect on the next sensor sync, so the presence of a tag is not confirmation that the sensor has already applied containment. The sensor-page banner checks that the lockdown policy remains applicable.

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

Here `ttl: 3600` gives the tag a one-hour lifetime. `ttl` is optional and measured in seconds; **omit that line to require explicit release**. Adding the tag again with a `ttl` restarts its lifetime from that moment. Adding it again without a `ttl` does not remove a lifetime the tag already has. Automated tagging does not require the console dialog's reason or add its companion reason tag. Include incident context in your detection reports or case records.

The console action needs `app_control.get`, `app_control.set`, and `sensor.tag`, and an Application Control subscription. Policy-only setup needs Application Control read/write access. Restrict `sensor.tag` access, and write access to D&R rules: anyone who can add or remove this tag, or who can create a rule that does, can request or release containment.

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
| `APP_CONTROL_SIGNATURE_STATUS` | What the signature check concluded: `0` not checked, `1` valid, `2` unsigned, `3` invalid, `4` untrusted, `5` expired. |
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

## Blocking a file from the console

Wherever the web console shows a SHA-256 hash, you can block that exact file with one action, without writing a rule by hand. **Block with Application Control** is offered on:

- the event detail panel (sensor timeline and the Query Console), as a button for the event's own `HASH` and as an action on any hash field in the event JSON;
- the detection viewer, as an action on the hash fields of the detection;
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

## Managed alerts

Application Control can install managed D&R rules that report detections for operational and enforcement events. All four alerts are **off by default**, including for existing subscriptions. To enable them, open the Application Control extension's **Configuration** view in the console, turn on the alerts you want, and save. Each toggle applies within about 5 minutes of saving, on the next sensor SYNC. Each option is independent of the policy's mode and `on_enable` setting.

| Configuration option | Trigger | Detection name | Suppression |
| --- | --- | --- | --- |
| `alert_policy_refused` | A `SYNC` contains `APP_CONTROL_STATUS/APP_CONTROL_REFUSED`: the sensor reports a policy it declined. | `app-control-policy-refused` | Once per sensor and refused generation for 30 days. |
| `alert_break_glass` | A `SYNC` contains `APP_CONTROL_STATUS/APP_CONTROL_ENFORCED/APP_CONTROL_BREAK_GLASS` equal to `1`. | `app-control-break-glass` | Once per sensor per 24 hours. |
| `alert_enforced_blocks` | `APP_CONTROL_DENIED` with `APP_CONTROL_IS_ENFORCED` equal to `1`: an execution was actually blocked. | `app-control-enforced-block` | Once per sensor and application per 24 hours, identified by `HASH` when available, otherwise `FILE_PATH`. |
| `alert_resident_terminated` | `APP_CONTROL_RESIDENT` with `APP_CONTROL_IS_ENFORCED` equal to `1`: a program already running was stopped when the policy landed. | `app-control-resident-terminated` | Each termination is reported. |

Would-be blocks, unresolved executions, summaries, and resident programs that were only reported do not trigger the enforcement alerts. Turning on the resident alert does not itself stop programs; the policy must specify `on_enable: terminate` and be enforcing.

The detections have priority `3`. The original sensor event is in `detect`, and the following metadata is in `detect_mtd`. Values copied from the event are rendered as strings; an absent optional hash, policy label, or matched rule id is an empty string.

| Detection | Metadata keys |
| --- | --- |
| `app-control-policy-refused` | `refused_generation`, `reason_code`, `reason` (human-readable), `refused_at` (the sensor's refusal timestamp in Unix milliseconds). |
| `app-control-break-glass` | `break_glass`, `enforced_generation`, `policy_label` (the policy held by the sensor). |
| `app-control-enforced-block` | `file_path`, `hash`, `policy_label`, `matched_rule_id`, `generation`, `is_enforced`. |
| `app-control-resident-terminated` | `file_path`, `hash`, `policy_label`, `matched_rule_id`, `generation`, `is_enforced`. |

The refusal reasons are:

| `reason_code` | `reason` |
| --- | --- |
| `21` | invalid signature |
| `22` | foreign sensor or organization |
| `23` | expired policy |
| `24` | unknown signing key |
| `25` | policy refused |
| `26` | generation not newer |
| `27` | policy rolled back |
| `28` | host clock skew |

Other reason codes produce `unknown reason (<code>)`. A refusal report describes the refused generation, which can differ from the policy the sensor still holds. Repeated syncs carrying that generation are suppressed for the maximum supported D&R period, 30 days; an unchanged refusal can alert again after that window. Daily suppression periods are 24-hour windows rather than calendar days.

Rules are installed in `dr-managed` with names prefixed `ext-app-control-alert-`, using the detection name's suffix. The first sensor SYNC or internal extension request carrying changed saved settings reconciles the rules before responding, with an eight-second limit for rule updates. Concurrent requests for the same organization proceed without waiting. Subscription and extension refreshes also repair the rules. Turning an option off removes its rule within about 5 minutes of saving, and unsubscribing removes all four alert rules. A rule-update failure or timeout is logged and leaves the policy response unchanged. Only a fully successful update is cached; failed attempts retry on the next request. If rule updates fail or the service is busy, changes can take longer. Configuration validation rejects non-boolean alert values and leaves the rules unchanged; validating without saving does not enable or disable alerts. Existing detections remain available. The extension's API key needs `dr.set.managed`, `dr.list.managed`, and `dr.del.managed` to manage the rules.

The rules request access to the Resource ACL scopes the extension's API key belongs to. Add that key to the appropriate scopes to include ACL-restricted sensors. On a platform that rejects the ACL scope marker, installation retries without it and logs a warning; those rules cannot reach ACL-restricted sensors.

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

Three console actions need more than the App Control permissions alone. [Install mode](#install-mode) and [lockdown](#lockdown) also need `sensor.tag`, because they tag the host. [Blocking a file from the console](#blocking-a-file-from-the-console) needs both `app_control.get` and `app_control.set`.

## Limits

- 10,000 rules may apply to a single policy.
- Policy record names are limited to 128 bytes and rule ids to 64 bytes.
- A policy can list at most 64 tags.

## Exporting compliance evidence

Open **Application Control**, select **Export compliance evidence**, and choose a
start and end time in UTC. Select **Collect evidence**. The dialog shows collection
progress, including the number of sensors read, and lets you cancel. Once the
files are ready, select **Download evidence bundle** to save a ZIP archive.
The default window is the preceding 30 days.

The export reads data without changing policies, rules, sensors, or observation
triage. Sensor collection pages through the entire organization, including sensors
that have never reported Application Control. It does not export only the Fleet
page currently visible. If pagination fails, repeats records, or returns a changed
sensor total, that section's partial results are discarded and marked unavailable.
If the sensor count changes during collection, the report identifies inventory
changes as the reason. Retry when sensor enrollment and removal are quieter.
Retry the export to collect the section again. Canceling discards the export.

### Files and evidence

The archive contains:

- **report.pdf**: the report metadata, requirement coverage, policies, rule summaries,
  enforcement coverage, observations, and available change history.
- **report.html**: the same localized report as selectable, searchable text. The PDF
  renders text with browser fonts to preserve all supported languages; use the HTML
  companion for text selection and accessibility.
- **evidence.json**: the evidence, section availability, timestamps, and localized
  report content. Its `formatNotes` explicitly identify the raw sections: machine-readable
  field names, API enum values, numeric codes, and boolean flags remain unchanged.
  The `report` field uses the same localized labels as the PDF and HTML.
- **rules.csv**, when policy/rule read permission is available: the complete rule
  list, including action, kind, value, policy scope, enabled state, expiry, comment,
  and hive change metadata. Disabled and expired rules are included.
- **fleet.csv**, when sensor-list permission is available and collection completes:
  every collected sensor's identity and last-reported Application Control posture,
  using console labels for mode, enforcement connection, break-glass, and issues.
- **observations.csv**, when observation collection completes: every retained
  application selected by the window, with console labels for signature status,
  vendor trust (Yes, No, or Unknown), enforcement, and triage status. Executions
  use the console's lower-bound display (for example, **1,234+**), or **none seen** when no executions were reported.

The report identifies the organization, exporting user, generation time, collection
start, and selected window. Policies include targeting, priority, mode, stance,
OS vendor trust, behavior for programs already running, **Notify users of blocks**,
**Show tray icon**, enabled state, and the last
change timestamp and author returned in hive `sys_mtd`. Rule summaries distinguish
all rules from active rules, temporary allow exceptions from other rules, and
trusted installer rules. The PDF, HTML, and CSV values use the current console labels
in the selected language. Omitted notification and tray settings default to No;
the report describes configuration, not proof that an end-user notification appeared.

Fleet evidence counts reporting sensors by mode and held policy, sensors with no
Application Control report, refused policies, break-glass, and degraded enforcement.
It also identifies posture reports older than 24 hours. The inventory includes
unsupported platforms; their presence or absence of a report does not establish
protection. Policy and rule configuration and Fleet posture are current snapshots,
collected at different times, **not proof of continuous enforcement throughout the
selected window**.

Observations count distinct retained applications whose `last_seen` is in the
selected window and whose retained dispositions include a block or would-block.
The report includes the top applications ranked by retained execution lower bounds,
plus the last ingestion time and retained shedding count. **These are not exact
block-event or would-block-event totals for the window.** Dispositions and execution
lower bounds span retained history, and an application can appear in both groups.
An application seen again after the window can be absent from this selection.
Retention, discarded observations, and delayed ingestion can omit activity.
The observation actions do not provide time-bucketed event totals, so the report
explicitly identifies those totals as unavailable.

If retained observations change between pages (for example, an application's
`last_seen` moves past the window end), that section is marked unavailable with
this reason and its partial results are discarded. An earlier end time can reduce
changes caused by applications running during collection.

Available change history comes from retained organization audit entries for
Application Control policy and rule hives in the chosen window. Entries may not
contain before/after values. Missing retained entries do not establish that no
changes occurred, and the export does not reconstruct historical policy state.
The PDF and HTML show the newest 100 matching entries and the total returned;
`evidence.json` includes every fetched matching entry.

### Permissions and unavailable sections

The export respects the exporting user's permissions. It keeps unavailable
sections in the report with an explanation rather than presenting missing data as
zero activity or failing the whole export.

| Section | Required permission |
| --- | --- |
| Policies and rules | `app_control.get` |
| Fleet enforcement coverage | `sensor.list` |
| Observations | `app_control.get` and `ext.request` |
| Change history | `audit.get` |

For example, an export without `audit.get` states
**Not available: missing permission audit.get** in the change-history section.
A section whose collection fails is marked unavailable and includes no partial
inventory. Its CSV is omitted; the PDF, HTML, and JSON explain the omission.

### Coverage statements for an auditor

The report presents evidence and **capability coverage**, not a compliance
certification, a pass/fail decision about the organization, or an Essential Eight
maturity rating. An auditor must assess the actual scope, authorization process,
exceptions, and enforcement gaps. An enforcing allowlist policy can deny program
execution by default and permit exceptions. A blocklist policy, or a policy in Audit or Rehearsal mode, does
not implement allow-by-exception.

| Requirement or application type | Capability coverage | Reason |
| --- | --- | --- |
| CIS Controls v8 2.5, Allowlist Authorized Software | Partially covered | Windows and macOS program execution can be allowlisted. Fleet scope, exceptions, and enforcement must be assessed; scripts and libraries are not controlled. |
| CIS Controls v8 2.7, Allowlist Authorized Scripts | Not covered | Scripts are **not controlled**. Only program execution is controlled. Allowing an interpreter does not authorize or constrain the scripts it runs. |
| Australian Essential Eight, Application control | Partially covered | Executables are supported; the other application types below are not covered. No maturity level is claimed. |
| Executables | Covered capability | Process-start control on supported Windows/macOS sensors. Blocking requires an enforcing policy; allow-by-exception requires allowlist stance. |
| Software libraries / DLLs | Not covered | Library and DLL loading is not controlled. |
| Scripts | Not covered | Script content and execution within an allowed interpreter are not controlled. |
| Installers (MSI) | Not covered | MSI packages are not controlled. Trusted installer rules provide executable trust exceptions, not MSI allowlisting. |
| Compiled HTML / HTA | Not covered | CHM and HTA execution is not controlled. |
| Control panel applets | Not covered | CPL applets are not controlled. |
| NIST SP 800-53 CM-7(5), Authorized Software — Allow-by-exception | Partially covered | Enforcing allowlist policies support deny-by-default with exceptions. This export does not establish the organization's approved inventory, review process, or continuous enforcement. |

Trusted installer rules can trust program descendants or written executables. Treat
them as broad trust exceptions when assessing the allowlist, alongside vendor,
signer, and path-based trust. They do not add script, library, or MSI package control.

The requirement references are the
[CIS Controls v8](https://www.cisecurity.org/controls/v8),
[ASD application control guidance](https://www.cyber.gov.au/business-government/protecting-devices-systems/hardening-systems-applications/system-hardening/implementing-application-control),
and [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final).

## See Also

- [Application Control policies](../../../7-administration/config-hive/app-control-policy.md)
- [Application Control rules](../../../7-administration/config-hive/app-control-rule.md)
- [Sensor tags](../../../2-sensors-deployment/sensor-tags.md)
- [Config Hive overview](../../../7-administration/config-hive/index.md)
- [Permissions](../../../8-reference/permissions.md#application-control)
- [EDR events reference](../../../8-reference/edr-events.md#app_control_denied)
