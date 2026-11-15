# Host Posture

## Overview

Host Posture checks your Windows, macOS and Linux sensors for misconfigurations: a firewall that is off, an SSH server that allows root login, a kernel setting that leaves a known exploit open. It tells you which hosts fail which check, shows the evidence, and says how to fix it.

- The checks are **rules** stored in your organization's [`host_posture_rule`](../../../7-administration/config-hive/host-posture-rule.md) hive. You install LimaCharlie's default pack, edit it, and add your own.
- Rules run **on the host**, inside the sensor. They only read: no command is executed and nothing is changed. Only the evidence a rule declares leaves the host.
- Hosts are checked on a **schedule** and **on demand**. Results are kept **per host**.
- If the organization is also subscribed to Cloud Security, each failing rule additionally becomes one rolled-up finding there. See [Cloud Security integration](#cloud-security-integration).

## Requirements

- The `ext-host-posture` extension subscribed in the organization. See [Enabling the extension](#enabling-the-extension).
- Windows, macOS or Linux sensors on a version that supports the posture scan. A sensor that does not support it is reported as `unsupported` for every rule and is never reported as passing.
- The `host_posture.get` and `host_posture.set` [permissions](../../../8-reference/permissions.md#host-posture). Saving a rule, and enabling, disabling or setting the expiry of one, also needs `sensor.task`.

## Enabling the extension

Open the Host Posture page in the Add-Ons marketplace, choose the organization and select **Subscribe**.

Subscribing sets up the extension's adapter and the managed rules that turn findings into events and detections. It does not install any host posture rule, so by itself it checks nothing. Install the [default pack](#the-default-rule-pack) next.

## How it works

1. A **rule** says what to read on the host and what counts as a problem. Rules live in the `host_posture_rule` hive, one record per rule.
2. At each sweep the extension picks, for each sensor, the enabled rules whose platform matches and whose [scope](../../../7-administration/config-hive/host-posture-rule.md#scope) admits the sensor's tags.
3. It sends the selected rules to the sensor in one task per sensor, sized to what the sensor accepts per request (512 KB and 256 rules). A rule that does not fit is reported as an `error` result with the reason `over_capacity`. It is never dropped silently.
4. The sensor evaluates every rule and replies. The extension stores one result per host, rule and instance, and raises `config_finding` events when something changes.

Every rule is equally trusted. A rule from LimaCharlie's pack and a rule you wrote run the same way and have the same abilities. The `lc.` prefix of the pack's rule ids only tells you where a rule came from.

### Results

Every rule gets one result on every host it was evaluated on:

| Result | Meaning |
| --- | --- |
| `pass` | Everything the rule needed was read, and the host is not affected. |
| `fail` | The host has the problem. Each affected item is an instance, with its evidence. |
| `error` | The rule could not be decided, for example because a file was unreadable. An error is never treated as a pass, and it never closes an existing failure. |
| `not_applicable` | The rule does not apply to this host, for example because the software it checks is not installed. |
| `unsupported` | The sensor cannot run the rule: an older sensor or evaluator, or a platform the rule does not cover. |

A failure stays open until a later check proves it gone. A check that errors, or that cannot see the subject any more, leaves it as it was.

## The default rule pack

LimaCharlie maintains a pack of rules for common misconfigurations and for recent local-exploit preconditions. It covers, among other things, Windows credential protection, SMB and RDP settings, Defender and firewall state, Linux kernel and filesystem hardening, SSH and nginx settings, container runtime exposure, and macOS protections such as SIP, FileVault and Gatekeeper.

The pack is not applied for you. You install it into your own hive, and from then on its rules are ordinary records:

- In the web app, open the Host Posture page and choose **Install default rule pack**.
- With the CLI:

```bash
limacharlie host-posture install-defaults
```

Both write the rules with **your** permissions, so you need `host_posture.set` and `sensor.task`.

`install-defaults` is careful with what you already have:

- A rule that is not in your hive is created and enabled. Pass `--disabled` to create them disabled and review them first.
- A rule that already exists is left alone. The command lists what it skipped.
- `--update` replaces a rule with a newer version from the pack, but only a rule you have not edited. The replacement is conditional on the record not having changed since it was read. Your enabled or disabled state, expiry and comment are kept.
- A rule you edited, or one whose version is higher than the pack's, is never overwritten unless you pass `--force`.
- If a rule changes while the command runs (a new rule that appeared, or an update that lost the race), nothing is retried: the rule is skipped, and the output shows the state it is in now (`state_now`).
- `--dry-run` shows what would happen and writes nothing.

To decide what to do, the command asks the extension how each rule of your hive compares with the pack. Each pack rule is in one of these states:

| State | Meaning |
| --- | --- |
| `new` | You have no record for it. It is created. |
| `current` | Your record is the pack's rule, unedited, at the same version. Nothing to do. |
| `update_available` | Your record is unedited and the pack has a newer version. `--update` replaces it. |
| `edited` | Your record differs from what the pack installed, or has no digest tag. This is checked first. Needs `--force`. |
| `org_newer` | Your record is unedited but its version is higher than the pack's. Needs `--force`. |

Rules the command writes carry the tag `lc:default-pack`, a tag `lc:pack-sha256:<digest>` and a comment naming the pack version. The extension computes the digest of what it handed out, and recognizes an edit by comparing it with the record as it is now. A rule without the digest tag, for example one you created yourself, counts as edited.

Because the pack lives in your hive, you can disable a rule that does not suit your environment, change its [scope](../../../7-administration/config-hive/host-posture-rule.md#scope), or delete it. Disabling or deleting a rule you installed does not come back on its own: the pack is only written when you ask for it.

## Scheduled and on-demand scans

### Scheduled sweeps

The extension sweeps your sensors on the `schedule` of its [configuration](#extension-configuration): daily by default, or weekly, or off. Sweeps use [reliable tasking](reliable-tasking.md), so a sensor that is offline when the sweep starts is checked when it comes back, and start times are spread out so that your fleet does not report at once.

Rules are sent only to sensors that need them: a sweep sends each sensor the rules for its platform and its tags.

### Sweep now

Start a sweep without waiting for the schedule, for all supported sensors or for the ones carrying given tags:

```bash
limacharlie host-posture sweep
limacharlie host-posture sweep --tag prod --tag web
```

A sweep reaches offline sensors the same way a scheduled one does. The response gives a `job_id` and the number of sensors tasked.

### Scan one host

Check one online sensor right away, for example after you fixed something:

```bash
limacharlie host-posture scan --sid 11111111-2222-3333-4444-555555555555
```

The response gives a `job_id`, the sensor's platform and the number of tasks issued. The scan needs the sensor to be online. Use `sweep` for sensors that may be offline. The results show up on the host as the sensor replies.

## Reading the results

Results are stored per host, in a store the extension owns. You read them in the web app's Host Posture page and with the CLI:

```bash
# Counts across the org: hosts assessed and failing, results by status,
# failing by severity, enabled rules, last sweep, Cloud Security state
limacharlie host-posture results summary

# Hosts, worst first, filtered on the server
limacharlie host-posture results hosts --severity high --platform windows

# One host: every rule, its status, evidence and when it was first and last seen
limacharlie host-posture results host --sid 11111111-2222-3333-4444-555555555555

# Rules with their pass and fail counts, and the hosts failing one rule
limacharlie host-posture results rules --severity critical
limacharlie host-posture results rule-hosts --rule-id lc.windows.network.smb-signing-not-required --status fail

# How hosts do against each standard
limacharlie host-posture results standards --framework cis
```

Lists are filtered and paged on the server. Use the `next_cursor` of a page, as `--cursor`, to get the next one. `--limit` defaults to 50 and is at most 200.

Statuses are `pass`, `fail`, `error`, `not_applicable` and `unsupported`. Severities are `critical`, `high`, `medium`, `low` and `info`.

Check the extension's own health, including the number of rules and any record it could not read:

```bash
limacharlie host-posture status
```

## Extension configuration

Organization-wide settings are the extension's configuration (the `extension_config` hive, key `ext-host-posture`):

```json
{
    "schedule": "daily",
    "scope_tags": []
}
```

| Field | Default | Description |
| --- | --- | --- |
| `schedule` | `daily` | `daily`, `weekly` or `off`. Scheduled sweeps use reliable tasking with jitter. |
| `scope_tags` | `[]` | If not empty, sweeps cover only sensors that carry at least one of these tags. Empty means every supported sensor. |

There are no other settings. Per-rule targeting is in each rule's [`scope`](../../../7-administration/config-hive/host-posture-rule.md#scope).

```bash
limacharlie extension config-set --name ext-host-posture --input-file config.json
```

## Cloud Security integration

Host Posture and [Cloud Security](../../../cloud-security/index.md) are separate subscriptions that work independently.

- **Only Host Posture:** you get every per-host result, in the web app, the CLI and as events.
- **Both subscribed:** the extension also sends Cloud Security a rolled-up view, one finding per failing rule (class `host_config`) rather than one per host. The finding carries the rule's severity, its standards, the number of assessed and failing hosts and a sample of the failing hosts with their evidence. The risk of a finding can rise when failing hosts are critical assets. The per-host results stay in Host Posture.

How the finding follows the rule:

- It exists while at least one assessed host fails the rule.
- It **resolves** only when hosts were assessed against the rule and they all pass. A host that errored does not count as passing.
- It closes as **"rule removed"**, not as resolved, when you disable, delete or expire the rule. Removing a rule never shows a problem as fixed.
- It closes as **"no hosts in scope"**, not as resolved, when no host is in scope for the rule any more, for example because you changed its scope tags or the sensors were removed.
- It closes as **"source turned off"** when you unsubscribe from Host Posture.

`limacharlie host-posture results summary` reports `cloud_security` as `published`, `not_subscribed` or `error`. An organization that subscribes to Cloud Security later is picked up within about an hour, and the full set of findings is sent as soon as the connection works.

## Events and detections

Each time a host's state for a rule changes, the extension emits an event through its adapter. An unchanged failure emits nothing, so a host that fails the same five rules every day produces five events on the first day and none after.

| Event | When |
| --- | --- |
| `config_finding` | A finding opens for a host (one per instance), or an `error` finding opens or changes its reason. |
| `config_finding_closed` | A finding closes: the host now passes, the rule no longer applies, or the rule was retired. |
| `config_finding_subject_not_found` | A finding's subject disappeared (for example its configuration file was deleted), so it can no longer be checked. The finding keeps its history and closes later, when a check proves the problem gone. |

A `config_finding` event carries the host (`sid`, `hostname`), the rule (`rule_id`, `signature_version`, `severity`, `title`, `description`), the remediation text, the rule's standards and references, the `instance` and its evidence, and the evaluator version that produced it. A managed D&R rule reports each `config_finding` as a detection. Because that rule is in your organization, you can tune it, for example to alert only on `high` and `critical`, or to send findings to an output.

## Writing your own rules

A rule is a YAML or JSON document in the `lc-posture/v1` language. See [Writing your own rules](host-posture-writing-rules.md) for the document, the probes that read the host, the condition language and how to test a rule. To store one, see [Host Posture rules](../../../7-administration/config-hive/host-posture-rule.md).

## Permissions

| Permission | Allows |
| --- | --- |
| `host_posture.get` | Read rules, and read results through the extension. |
| `host_posture.set` | Create, edit, enable, disable and delete rules, and their metadata. |

Saving a rule, and enabling, disabling or setting the expiry of one, also needs `sensor.task`, because a rule runs on your sensors. Deleting a rule needs only `host_posture.set`. The permissions are checked when you change a rule, not at each sweep.

By default the Owner, Administrator and Operator roles have all of them, and the Viewer role has `host_posture.get`. See [Permissions](../../../8-reference/permissions.md#host-posture).

## Limits

- A rule document: 128 KiB as JSON.
- A sweep carries at most 512 KB and 256 rules to a sensor, and the extension runs at most 2,000 enabled rules per organization (in record-name order). Rules beyond either limit are reported as `error` with the reason `over_capacity`.
- A host runs the rules of one sweep within a fixed budget of time, CPU and memory. A rule the host did not get to is reported as unreadable (an `error`), never as passing.
- At most 64 instances per rule per host, with evidence capped in size.

## See Also

- [Host Posture rules (Config Hive)](../../../7-administration/config-hive/host-posture-rule.md)
- [Writing your own rules](host-posture-writing-rules.md)
- [Vulnerability Reporting](vulnerability-reporting.md)
- [Reliable Tasking](reliable-tasking.md)
- [Permissions](../../../8-reference/permissions.md#host-posture)
