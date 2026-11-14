# Config Hive: Host Posture Rules

The `host_posture_rule` hive holds the rules of [Host Posture](../../5-integrations/extensions/limacharlie/host-posture.md). Each record is one rule: a check that the Host Posture extension runs on your Windows, macOS and Linux sensors to find misconfigurations. The record name is the rule's `id`.

Like the Application Control hives, `host_posture_rule` is partitioned by organization. The extension ships no rules of its own. The rules you see here are the ones you [installed from the default pack](../../5-integrations/extensions/limacharlie/host-posture.md#the-default-rule-pack) and the ones you wrote. All of them are ordinary records: you can edit, disable and delete any of them.

## Format

```json
{
    "rule": {
        "apiVersion": "lc-posture/v1",
        "kind": "Signature",
        "id": "lc.linux.kernel.ptrace-scope",
        "version": 1,
        "title": "ptrace is not restricted to administrators",
        "...": "the rest of the rule"
    },
    "scope": {
        "sensor_tags": ["prod"],
        "exclude_sensor_tags": ["kiosk"]
    }
}
```

| Field | Required | Description |
| --- | --- | --- |
| `rule` | Yes | One rule in the `lc-posture/v1` language, as a JSON object. See [Writing your own rules](../../5-integrations/extensions/limacharlie/host-posture-writing-rules.md) for the fields. The rule may carry its own `tests`. |
| `scope` | No | Limits the rule to some of your sensors, by tag. See [Scope](#scope). |

Keywords are case-sensitive. The record accepts no other top-level key, and an unknown field is refused when you save the record.

The `rule` object is the same document you would write in YAML. Convert YAML to JSON before you save it through an API that takes JSON. The CLI accepts either, since it reads the file into an object.

Two things live in the record's metadata rather than in its data:

- **Enabled.** Only enabled records run. Disabling a rule stops it on every sensor at the next sweep.
- **Expiry.** A metadata `expiry` turns the rule off at that time. See [A temporary rule](#a-temporary-rule).

A comment explaining why the rule exists goes in the metadata `comment`.

!!! note
    Pass `--enabled` when you create a record with the CLI, as in the examples below, so that the rule starts running. Saving or enabling a rule also needs the `sensor.task` permission. See [Permissions](#permissions).

## The record name is the rule id

The record name must equal `rule.id`. The hive refuses a record whose name differs, with an error that names both.

A rule id is lowercase and dot-separated, for example `lc.linux.kernel.ptrace-scope` or `acme.windows.rdp.no-nla`. Any prefix is allowed. The default pack uses the `lc.` prefix to show where a rule came from. That is only a label, and an `lc.` rule is treated exactly like any other.

## Scope

By default a rule runs on every sensor whose platform is listed in `rule.platforms`. The optional `scope` narrows that by sensor tag. Platform targeting stays in `rule.platforms`.

| Field | Description |
| --- | --- |
| `sensor_tags` | If not empty, the rule runs only on sensors that carry at least one of these tags. |
| `exclude_sensor_tags` | A sensor that carries any of these tags is skipped. |

`exclude_sensor_tags` wins: a sensor that carries a tag from both lists is skipped. Each list holds at most 32 tags, and each tag is at most 128 bytes.

!!! note
    `scope` uses your sensor tags. It is not the same as the `tags` field inside `rule`, which labels the rule itself (for example `baseline:windows`).

Scope is combined with the extension's own [`scope_tags`](../../5-integrations/extensions/limacharlie/host-posture.md#extension-configuration), which limits which sensors are swept at all. A rule runs on a sensor only if both admit it.

## Validation

The hive checks a rule completely when you save it, and refuses a rule with a list of every problem, each naming the field path. It checks:

- The whole document: fields, types, the language version and the minimum evaluator version it asks for.
- Every limit of the language: probes per rule, expression size and nesting, the cost of each expression, instance and evidence sizes.
- Every probe type against the evaluator version the rule declares in `requires.evaluator`.
- Every condition expression: it must compile, type-check and use only the functions the language provides.
- The rule's embedded `tests`, when it has any. Tests are optional, but if a rule carries them they must all pass.

A rule document is at most 128 KiB as JSON.

Because tests run at save time, you can develop a rule by adding the cases you care about to `tests` and saving until the hive accepts it. See [Writing your own rules](../../5-integrations/extensions/limacharlie/host-posture-writing-rules.md#testing-a-rule).

## Permissions

Managing records in the `host_posture_rule` hive requires:

| Action | Permissions |
| --- | --- |
| Read rules and their metadata | `host_posture.get` |
| Create or edit a rule | `host_posture.set` and `sensor.task` |
| Enable, disable or set the expiry of a rule | `host_posture.set` and `sensor.task` |
| Delete a rule | `host_posture.set` |

Saving, enabling and disabling need `sensor.task` because a rule is code that LimaCharlie runs on your sensors, and enabling it decides whether it runs. The permission is checked when you save or change the record, not on every sweep. Deleting a rule needs only `host_posture.set`, since it removes something from your sensors.

By default the Owner, Administrator and Operator roles can do all of the above, and the Viewer role has `host_posture.get`. See [Permissions](../../8-reference/permissions.md#host-posture).

## Examples

The examples use the CLI generic hive commands. Pass `--oid <oid>` if your CLI is not already pointed at the organization.

### Installing the default pack

The quickest way to start is to write LimaCharlie's pack of rules into the hive:

```bash
limacharlie host-posture install-defaults
```

See [The default rule pack](../../5-integrations/extensions/limacharlie/host-posture.md#the-default-rule-pack) for what the command does and does not overwrite.

### A rule from the pack, kept to production servers

This is the `lc.linux.kernel.ptrace-scope` rule of the default pack. It flags Linux hosts where any process can attach to another with `ptrace`, the precondition of [CVE-2026-46333](https://nvd.nist.gov/vuln/detail/CVE-2026-46333). The `scope` here keeps it off developer workstations, where debuggers need `ptrace`. Save it as `ptrace.json`:

```json
{
    "rule": {
        "apiVersion": "lc-posture/v1",
        "kind": "Signature",
        "id": "lc.linux.kernel.ptrace-scope",
        "version": 1,
        "title": "ptrace is not restricted to administrators",
        "description": "CVE-2026-46333 lets a local user steal file descriptors from exiting setuid programs (chage, ssh-keysign, pkexec) through ptrace and pidfd_getfd, which exposes /etc/shadow and SSH host keys. Setting kernel.yama.ptrace_scope to 2 or higher blocks the technique.",
        "severity": "medium",
        "platforms": ["linux"],
        "tags": ["threat-pack:linux-kernel-attack-surface"],
        "threat_refs": { "cves": ["CVE-2026-46333"] },
        "requires": { "evaluator": "1.0" },
        "probes": {
            "ps": { "state": "linux.sysctl.kernel.yama.ptrace_scope" }
        },
        "violation": "absent(ps) || num(ps.value) < 2",
        "evidence": {
            "ptrace_scope": "absent(ps) ? \"absent (no Yama LSM)\" : ps.value"
        },
        "remediation": {
            "action": "set-sysctl",
            "args": { "key": "kernel.yama.ptrace_scope", "value": "2" },
            "text": "Set kernel.yama.ptrace_scope=2 in /etc/sysctl.d/. Debuggers then need root, so leave developer workstations at 1 if needed."
        },
        "tests": [
            { "name": "ubuntu default (1)", "probes": { "ps": { "status": "ok", "value": "1" } }, "expect": "fail" },
            { "name": "admin-only (2)", "probes": { "ps": { "status": "ok", "value": "2" } }, "expect": "pass" },
            { "name": "no attach (3)", "probes": { "ps": { "status": "ok", "value": "3" } }, "expect": "pass" },
            { "name": "yama not built", "probes": { "ps": { "status": "absent" } }, "expect": "fail" },
            { "name": "unreadable", "probes": { "ps": { "status": "unreadable" } }, "expect": "error" }
        ]
    },
    "scope": {
        "exclude_sensor_tags": ["developer-workstations"]
    }
}
```

```bash
limacharlie hive set \
  --hive-name host_posture_rule \
  --key lc.linux.kernel.ptrace-scope \
  --input-file ptrace.json \
  --enabled \
  --comment "Developer workstations excluded: debuggers need ptrace"
```

The same command is available as `limacharlie host-posture rules set --key ... --input-file ...`.

### A rule for your own fleet

Rules are not limited to the default pack. This one, saved under your own prefix, checks the SMB signing setting on Windows servers you tag `file-servers`. It reuses the registry reads of the pack's `lc.windows.network.smb-signing-not-required`, without that rule's per-build exceptions:

```json
{
    "rule": {
        "apiVersion": "lc-posture/v1",
        "kind": "Signature",
        "id": "acme.windows.smb.signing-required",
        "version": 1,
        "title": "File server does not require SMB signing",
        "description": "File servers must require SMB signing so that relayed NTLM authentication cannot be used against them.",
        "severity": "high",
        "platforms": ["windows"],
        "requires": { "evaluator": "1.0" },
        "probes": {
            "req": {
                "registry": {
                    "key": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters",
                    "value": "RequireSecuritySignature"
                }
            }
        },
        "violation": "absent(req) || req.value != \"1\"",
        "evidence": {
            "require_security_signature": "absent(req) ? \"absent\" : req.value"
        },
        "remediation": {
            "text": "Enable the policy \"Microsoft network server: Digitally sign communications (always)\"."
        },
        "tests": [
            { "name": "required", "probes": { "req": { "status": "ok", "value": "1" } }, "expect": "pass" },
            { "name": "not required", "probes": { "req": { "status": "ok", "value": "0" } }, "expect": "fail" },
            { "name": "absent", "probes": { "req": { "status": "absent" } }, "expect": "fail" },
            { "name": "unreadable", "probes": { "req": { "status": "unreadable" } }, "expect": "error" }
        ]
    },
    "scope": {
        "sensor_tags": ["file-servers"]
    }
}
```

```bash
limacharlie host-posture rules set \
  --key acme.windows.smb.signing-required \
  --input-file smb.json \
  --enabled
```

### A temporary rule

Run a check for a limited time, for example during an incident. Set the expiry with the CLI `--expiry` flag, which takes Unix epoch **seconds**:

```bash
limacharlie hive set \
  --hive-name host_posture_rule \
  --key acme.linux.incident.check \
  --input-file check.json \
  --enabled \
  --expiry 1797292800 \
  --comment "Incident check: remove after the window"
```

`1797292800` is 2026-12-15 00:00:00 UTC. Replace it with the end of your own window (`date -d '2026-12-15 00:00:00 UTC' +%s` prints it), since a rule with an expiry in the past never runs. The hive stores expiry in milliseconds, so `hive get` shows `1797292800000`. If you write the record with a `usr_mtd` block instead of the flag, give the expiry in milliseconds there.

### Listing, reading, disabling and deleting rules

```bash
limacharlie host-posture rules list
limacharlie host-posture rules get --key lc.linux.kernel.ptrace-scope
limacharlie host-posture rules disable --key lc.linux.kernel.ptrace-scope
limacharlie host-posture rules delete --key acme.windows.smb.signing-required --confirm
```

## What happens when a rule changes

- The extension reads the enabled records of the hive and caches them for about a minute, so a change reaches the next sweep, not instantly.
- A rule with a new `version` replaces the old one. Findings it raised keep their history.
- A disabled, expired or deleted rule stops running. The per-host findings it raised close with the reason `retired`, and in [Cloud Security](../../cloud-security/index.md) the rule's finding closes as "rule removed", not as resolved. A rule shows as resolved only when the hosts assessed against it actually pass.
- A record that fails to parse when the extension reads it is skipped and reported in the extension's `status`. It does not stop the other rules.

## Limits

- Record name (the rule id): the id syntax of the language, lowercase and dot-separated.
- Rule document: 128 KiB as JSON.
- `scope.sensor_tags` and `scope.exclude_sensor_tags`: 32 tags each, 128 bytes per tag.
- Rules per sweep: bounded by what one sweep can carry to a sensor (512 KB and 256 rules per request). A rule that does not fit is reported as an `error` result with the reason `over_capacity`. It is never dropped silently.

## See Also

- [Host Posture](../../5-integrations/extensions/limacharlie/host-posture.md)
- [Writing your own rules](../../5-integrations/extensions/limacharlie/host-posture-writing-rules.md)
- [Config Hive overview](index.md)
