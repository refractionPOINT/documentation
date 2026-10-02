# Application Control

## Overview

The Application Control extension lets the endpoint agent decide, **before a process starts**, whether it may run. Each execution is checked against a policy of rules that match the executable's **path**, its **code signer**, or its **SHA-256**. An execution the policy refuses never runs its first instruction, so this is different from terminating a process after it has started.

!!! warning "Requires endpoint agent 5.4.0 or later"
    Application Control is supported only on endpoint agents version **5.4.0** and later. Agents older than 5.4.0 do not support it. [Upgrade](../../../2-sensors-deployment/endpoint-agent/versioning-upgrades.md) endpoints before you target them with a policy.

A policy takes one of two stances:

- **Allowlist**: only executables that a rule allows (or that the operating system vendor signed, if you trust the vendor) may run. Everything else is denied.
- **Blocklist**: everything runs except executables that a deny rule matches.

Every denial is reported as an event, including denials that were only reported and not enforced. The non-enforcing modes show you exactly what a policy *would* block before you let it block anything.

Policy is **declarative**, as with the [DLP extension](dlp.md). You describe the desired state once in the extension configuration, and it is reconciled onto every matching endpoint when that endpoint syncs. Every policy is signed by LimaCharlie before delivery. The endpoint refuses a policy whose signature does not verify, and keeps a verified copy on disk so that it is enforced again right after a reboot, before the agent has reconnected.

### Scope

- **Process execution only.** A rule governs which executables may start. It does not cover libraries (DLLs or dylibs) loaded into a process that is already running, and it does not see script contents. Denying an interpreter such as `python.exe` stops the interpreter from starting. Allowing it allows every script it runs.
- **New executions only.** Processes already running when a policy arrives are left alone.
- **Windows and macOS only.** Linux endpoints are never sent a policy, whatever the targeting says.

## Requirements

- The Application Control extension enabled on the Organization. See [Enabling the extension](#enabling-the-extension).
- Endpoint agent **5.4.0** or higher. Earlier versions do not support Application Control. [Upgrade](../../../2-sensors-deployment/endpoint-agent/versioning-upgrades.md) if necessary.
- **Windows**: the agent's kernel driver must be installed and running. The decision to deny an execution is made in the driver, so an agent deployed in user mode only cannot enforce a policy.
- **macOS**: macOS 11 (Big Sur) or later, with the agent's system extension approved and running. Earlier macOS versions cannot deny an execution. On those hosts every execution is allowed and reported as unresolved.

## How a decision is made

For every execution, the endpoint applies the following steps in order and stops at the first one that decides:

| Step | Outcome |
| --- | --- |
| 1. The executable is the LimaCharlie agent itself | **Allow**. The agent can never be blocked, not even by a deny rule that names it, so a policy cannot cut the endpoint off from the cloud. |
| 2. A **deny** rule matches | **Deny** |
| 3. An **allow** rule matches | **Allow** |
| 4. `trust_os_vendor` is on and the executable is signed by the OS vendor | **Allow** |
| 5. Nothing matched | **Allowlist**: deny. **Blocklist**: allow. |

The order is fixed. Rules have no priorities, and where a rule sits in the list does not change the outcome. A deny always beats an allow, whatever order you write them in.

If the endpoint cannot reach a decision, the execution is **allowed** and reported as an `APP_CONTROL_UNRESOLVED` event. This happens, for example, when a hash it needed could not be computed in time, or a signature check could not complete. Application control is designed to fail open, so a fault in the agent never stops an endpoint from booting or running. An `APP_CONTROL_UNRESOLVED` event is distinct from an allow. It means "this ran and could not be checked".

### OS-vendor trust

With `trust_os_vendor` on, executables signed by the operating system vendor are allowed without a rule. Use it with an allowlist. Without it you would have to list every system binary yourself.

- **macOS**: Apple platform binaries, meaning the ones the OS itself identifies as Apple's. Third-party applications signed with an Apple-issued Developer ID certificate are **not** included.
- **Windows**: binaries whose signature chains to Microsoft's own code-signing authorities. Third-party code that Microsoft has merely countersigned, such as attestation-signed drivers and their companion programs, is **not** included.

Deny rules still override vendor trust. In a blocklist, vendor trust has no effect, because anything no deny rule matches already runs.

## Modes

A mode controls how hard the endpoint acts on its decisions. It is set per policy, separately from the rules.

| Mode | What happens | Performance cost |
| --- | --- | --- |
| `off` | Nothing is evaluated. On macOS the agent does not even subscribe to executions. | None |
| `permissive` | Each decision is computed shortly *after* the process starts, from normal process telemetry. Would-be denials are reported, and nothing is blocked. | None |
| `permissive_sync` | Every execution goes through the full pre-execution path, exactly as it would when enforcing. The decision is logged, and the execution is **always allowed**. | Same as `enforcing` |
| `enforcing` | Every execution goes through the full pre-execution path, and denials are applied. | Production |

`permissive` is the safe way to author a policy: it costs nothing and cannot block. `permissive_sync` is the dress rehearsal. It exercises everything enforcement does, including timing, under real load, but it cannot deny anything. Move from `permissive` to `permissive_sync` to `enforcing`. Do not skip the middle step.

The same `APP_CONTROL_DENIED` event is emitted in every mode. Its `APP_CONTROL_IS_ENFORCED` field says whether the execution was actually stopped. A D&R rule written during a permissive rollout therefore keeps matching once you turn enforcement on.

## Enabling the extension

Navigate to the [Application Control extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-app-control) in the Add-Ons marketplace, choose the target Organization, and select **Subscribe**.

Subscribing installs a single managed D&R rule, `ext-app-control-sync`, in your Organization's `dr-managed` hive. That rule triggers reconciliation each time an endpoint syncs. Leave it in place: the extension re-creates it if it drifts.

!!! note
    Subscribing on its own changes nothing. Until you add a policy, no endpoint matches one and every endpoint is left untouched.

## Configuring policies

Open the extension's **Configuration** view. The configuration is one ordered list, **Application Control Policies**. Each policy has three form fields that decide *who* gets the policy and *how hard* it applies, plus one JSON document that says *what* the policy is:

| Field | Type | Meaning |
| --- | --- | --- |
| `platforms` | list of platform (`windows`, `macos`) | The endpoint must run **one of** these platforms. Empty matches both. |
| `tags` | list of sensor tags | The endpoint must carry **all** of these tags. Empty matches any endpoint. |
| `mode` | `off`, `permissive`, `permissive_sync`, `enforcing` | How hard to act on decisions. See [Modes](#modes). Required. |
| `document` | JSON | The policy body: stance, vendor trust, and rules. See [The policy document](#the-policy-document). Required. |

The mode is kept out of the document on purpose. Moving a rollout from `permissive_sync` to `enforcing` is then a single dropdown change that cannot touch the rules.

### Targeting

Policies are evaluated **top to bottom, and the first match wins**. Each endpoint gets the first policy whose `platforms` and `tags` filters match the platform and tags it reports. The rest are ignored.

- An endpoint that matches **no** policy is left unmanaged.
- A policy with **no** `platforms` and **no** `tags` matches every Windows and macOS endpoint. Use it as a fleet-wide default and place it **last**, because anything below it is unreachable.
- Put narrow policies above broad ones.

Policies cannot reference a Sensor ID directly. To scope a policy to a single endpoint, give that endpoint a [tag](../../../2-sensors-deployment/sensor-tags.md) that nothing else carries, and target the tag. Rolling out by tag is also the supported way to stage enforcement. See [Rolling out a policy](#rolling-out-a-policy).

### The policy document

The document is a single JSON object:

```json
{
    "stance": "allowlist",
    "trust_os_vendor": true,
    "rules": [
        {
            "id": "program-files",
            "action": "allow",
            "kind": "path",
            "value": "C:\\Program Files\\",
            "comment": "Installed applications"
        }
    ]
}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `stance` | yes | `allowlist` denies anything no rule allows. `blocklist` allows anything no rule denies. There is no default: either guess would be harmful, so a document without a stance is refused. |
| `trust_os_vendor` | no | `true` (the default) implicitly allows OS-vendor-signed executables. See [OS-vendor trust](#os-vendor-trust). |
| `rules` | no | The list of rules, described below. Up to 10,000 rules. |
| `max_age_sec` | no | How long, in seconds, an endpoint may keep enforcing this policy without receiving a fresh copy. Omitted or `0` means the policy never expires. See [Policy expiry](#policy-expiry). |

Each rule has these fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `action` | yes | `allow` or `deny` |
| `kind` | yes | What the rule matches on. See [Rule kinds](#rule-kinds). |
| `value` | yes | The value to match, up to 1,024 characters |
| `id` | no | A short name for the rule, up to 64 characters, unique within the document. It is the name you will see when the rule fires, so give every rule one. |
| `comment` | no | Free text for your own reference |

The document is validated strictly when you save it:

- Unknown fields are **refused** rather than ignored, both at the top level and inside a rule. A typo such as `"hash"` for `"sha256"` therefore fails at save time instead of silently producing a rule that matches nothing.
- `mode`, `platforms` and `tags` are refused inside the document. They belong in the form fields.
- Trailing content after the JSON object, such as a second object pasted by accident, is refused.

Reformatting a document, for example re-indenting it or reordering its keys, does not trigger a new push to your endpoints. Changing the rules does, including changing their order.

### Policy expiry

By default a policy never expires. An endpoint keeps enforcing the last policy it received for as long as it runs, including while it is offline and across reboots.

Setting `max_age_sec` makes a policy expire. Once that many seconds have passed since the policy was issued, an endpoint that has not received a fresh copy keeps the policy but lowers its mode to `permissive`. It keeps reporting what the policy would deny, and it stops blocking. It returns to the configured mode as soon as it receives a fresh copy.

Expiry is a recovery mechanism for an endpoint that cannot be reached. Without it, a policy that cuts an endpoint off from LimaCharlie stays in force on that endpoint until someone fixes the endpoint locally, because no corrected policy can reach it. An allowlist that blocks the endpoint's VPN client or proxy agent is an example. The cost is that an endpoint offline for longer than the age, such as a laptop on a long trip, stops blocking until it reconnects.

```json
{
    "stance": "allowlist",
    "trust_os_vendor": true,
    "max_age_sec": 1209600,
    "rules": [ ... ]
}
```

`1209600` is 14 days. The value is in seconds.

An online endpoint does not expire on schedule: it requests a fresh copy of its policy from halfway through the maximum age, so only an endpoint that stays out of reach for the whole age expires. Agent 5.4.0 does not make that request. On 5.4.0 an online endpoint receives a fresh copy only when the policy changes or the agent restarts, so give it a maximum age well beyond your normal interval between policy changes, or leave the field out.

### Rule kinds

| `kind` | Platforms | Matches | Example `value` |
| --- | --- | --- | --- |
| `path` | Windows, macOS | The executable's full path. A value ending in a separator (`\` or `/`) is a **directory prefix** that matches everything beneath it. Any other value is an **exact** path. | `C:\Program Files\Contoso\` or `/usr/local/bin/agent` |
| `signer` | Windows, macOS | The code signer. On Windows, this is the Authenticode certificate's subject. On macOS, it is the developer's Team ID. | `ABCDE12345` |
| `signing_id` | macOS | The code-signing identifier of the app or binary | `com.contoso.agent` |
| `signer_root` | Windows | The **SHA-256** thumbprint of a certificate in the executable's validated signing chain. Use it to allow everything issued under a given certificate authority. | 64 hex characters |
| `sha256` | Windows, macOS | The SHA-256 of the file's contents. The rule follows the binary wherever it is copied. | 64 hex characters |

Matching details:

- **Paths** are compared case-insensitively, and repeated separators are collapsed. On Windows, `\\?\C:\…` and `\??\C:\…` are treated as `C:\…`. A prefix must end in a separator, so `C:\Prog` matches only a file named exactly `C:\Prog`, and never `C:\Program Files\app.exe`.
- **There are no wildcards.** `*` and `?` in a path are matched literally, so a rule containing them almost certainly matches nothing.
- **Signers** are compared case-insensitively, with surrounding whitespace ignored. The Windows subject must be the full subject string, not only its `CN`. The most reliable source for the exact value is the `APP_CONTROL_SIGNER` field of an event from a permissive rollout. That field is always in the form a `signer` rule matches. See [Events](#events).
- **`signer_root` and `sha256`** values must be exactly 64 hexadecimal characters, in either case. Windows certificate tools show the 40-character **SHA-1** thumbprint by default. That value is refused, with an error saying so.
- **Hash rules have a cost.** A `sha256` rule is the only kind that requires the endpoint to read and hash the file. Hashes are cached, but files larger than 50 MiB are never hashed. A decision that depends on hashing such a file is unresolved, and the execution is allowed. Prefer `signer` and `path` rules where you can.

## Examples

### Allowlist: approved software only

A Windows policy for workstations. It allows installed applications and the organization's own signed tools, and explicitly denies anything run from user-writable locations, even if a signer or path rule would otherwise allow it:

```json
{
    "stance": "allowlist",
    "trust_os_vendor": true,
    "rules": [
        { "id": "program-files",     "action": "allow", "kind": "path",   "value": "C:\\Program Files\\" },
        { "id": "program-files-x86", "action": "allow", "kind": "path",   "value": "C:\\Program Files (x86)\\" },
        { "id": "contoso-signed",    "action": "allow", "kind": "signer", "value": "CN=\"Contoso, Inc.\", O=\"Contoso, Inc.\", L=Redmond, S=Washington, C=US" },
        { "id": "no-temp",           "action": "deny",  "kind": "path",   "value": "C:\\Windows\\Temp\\" },
        { "id": "no-downloads",      "action": "deny",  "kind": "path",   "value": "C:\\Users\\Public\\Downloads\\" }
    ]
}
```

In JSON, every backslash in a Windows path is written twice (`\\`), and quotation marks inside a value are written as `\"`.

### Allowlist on macOS

```json
{
    "stance": "allowlist",
    "trust_os_vendor": true,
    "rules": [
        { "id": "applications",   "action": "allow", "kind": "path",       "value": "/Applications/" },
        { "id": "homebrew",       "action": "allow", "kind": "path",       "value": "/opt/homebrew/" },
        { "id": "contoso-team",   "action": "allow", "kind": "signer",     "value": "ABCDE12345" },
        { "id": "no-remote-tool", "action": "deny",  "kind": "signing_id", "value": "com.example.remotetool" }
    ]
}
```

### Blocklist: deny specific tools

Everything runs except the executables that are named. Under a blocklist, `allow` rules decide nothing, so the document contains only `deny` rules:

```json
{
    "stance": "blocklist",
    "rules": [
        { "id": "banned-tool-hash", "action": "deny", "kind": "sha256", "value": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", "comment": "Known-bad build" },
        { "id": "banned-vendor",    "action": "deny", "kind": "signer", "value": "CN=Example Remote Access Ltd, O=Example Remote Access Ltd, C=GB" }
    ]
}
```

### Targeting and staged rollout

Viewed as YAML, a configuration with a pilot group, an enforced group, and a fleet-wide observation default looks like this. Each `document` is the JSON policy body, carried as a string:

```yaml
policies:
  # Finance workstations: soak complete, enforcing.
  - platforms: [windows]
    tags: [appctl-finance]
    mode: enforcing
    document: |
      {
        "stance": "allowlist",
        "trust_os_vendor": true,
        "rules": [
          { "id": "program-files", "action": "allow", "kind": "path", "value": "C:\\Program Files\\" },
          { "id": "program-files-x86", "action": "allow", "kind": "path", "value": "C:\\Program Files (x86)\\" }
        ]
      }
  # Pilot group: full pre-execution path, never blocks.
  - platforms: [windows]
    tags: [appctl-pilot]
    mode: permissive_sync
    document: |
      {
        "stance": "allowlist",
        "trust_os_vendor": true,
        "rules": [
          { "id": "program-files", "action": "allow", "kind": "path", "value": "C:\\Program Files\\" },
          { "id": "program-files-x86", "action": "allow", "kind": "path", "value": "C:\\Program Files (x86)\\" }
        ]
      }
  # Everyone else: report what the allowlist would block, at no cost.
  - mode: permissive
    document: |
      {
        "stance": "allowlist",
        "trust_os_vendor": true,
        "rules": [
          { "id": "program-files", "action": "allow", "kind": "path", "value": "C:\\Program Files\\" },
          { "id": "program-files-x86", "action": "allow", "kind": "path", "value": "C:\\Program Files (x86)\\" },
          { "id": "applications", "action": "allow", "kind": "path", "value": "/Applications/" }
        ]
      }
```

Because evaluation is first-match-wins, the tagged policies must sit **above** the untagged default.

## Rolling out a policy

An allowlist that misses something the business depends on stops that software from running, so build one from evidence rather than from memory:

1. **Observe in `permissive`.** Target a broad set of endpoints with your draft policy in `permissive` mode. This adds no execution latency and blocks nothing. Every execution the policy would deny produces an `APP_CONTROL_DENIED` event with `APP_CONTROL_IS_ENFORCED` set to `false`.
2. **Refine.** Group the would-be denials by `FILE_PATH` and `APP_CONTROL_SIGNER`, and add allow rules for the legitimate ones. A `signer` rule usually covers far more than a list of hashes, and it survives software updates. Keep observing long enough to see software that runs rarely, such as month-end jobs, backup agents and installers.
3. **Rehearse in `permissive_sync`.** Tag a pilot group and move it to `permissive_sync`. This exercises the full pre-execution path at production rate while still never denying anything. Confirm the endpoints show no `APP_CONTROL_UNRESOLVED` events for timeouts or overload, and that users notice no slowdown.
4. **Enforce in stages.** Move the pilot tag to `enforcing`, then widen it tag by tag. A broader policy below it in `permissive` or `permissive_sync` is your rollback: removing an endpoint's tag returns it to that policy on its next sync.

## Points to watch

- **Removing a policy does not disarm an endpoint.** An endpoint that stops matching any policy (because its tag was removed, or the policy was deleted) keeps the policy it last received, including an enforcing one. This is deliberate. Otherwise an unrelated configuration edit could silently take a host from enforcing to unprotected. To stand enforcement down, push a policy with `mode: off`, and let it converge **before** you delete the policy or unsubscribe.
- **Keep `trust_os_vendor` on for an enforcing allowlist.** With vendor trust off, an allowlist must cover every operating system binary itself, and the endpoint has no way to check that. The extension refuses to save an enforcing allowlist with no allow rules and vendor trust off. The endpoint goes further, and refuses to install *any* enforcing allowlist with vendor trust off. It keeps the policy it already has and reports the refusal.
- **A deny always wins.** A deny rule overrides every allow rule and vendor trust. The only exception is the LimaCharlie agent itself, which is never blocked.
- **Under a blocklist, allow rules do nothing.** Anything no deny rule matches already runs. An `allow` rule with kind `sha256` in a blocklist is worse than useless, because it makes endpoints hash files to reach a decision that was going to be "allow" anyway.
- **An empty allowlist with vendor trust on** allows only OS-vendor-signed executables. Nothing else on the endpoint will run once it is enforcing.
- **There is no local override.** No command or file on the endpoint turns application control off. A local override would be the first thing malware went after. Change the mode from the extension configuration instead. As a last resort on Windows, booting into Safe Mode stops the driver from denying executions for that boot. The endpoint reports this, so a host disarmed this way is never mistaken for one that is enforcing.

## Configuration via Hive

The full configuration is stored as a single record in the `extension_config` [hive](../../../7-administration/config-hive/index.md), at the key `ext-app-control`. You can manage it with [git-sync](git-sync.md) (under `hives/extension_config.yaml`) or directly with the LimaCharlie CLI. Reading the record requires the `ext.conf.get` [permission](../../../8-reference/permissions.md), and writing it requires `ext.conf.set`.

Read the current configuration:

```bash
limacharlie hive get \
  --hive-name extension_config \
  --key ext-app-control \
  --oid <oid> --output yaml
```

The record's `data` is the YAML structure shown in [Targeting and staged rollout](#targeting-and-staged-rollout): a top-level `policies` list. Validate a file against the live schema without writing it:

```bash
limacharlie hive validate \
  --hive-name extension_config \
  --key ext-app-control \
  --input-file my-app-control.yaml \
  --oid <oid> --output yaml
```

Then write it:

```bash
limacharlie hive set \
  --hive-name extension_config \
  --key ext-app-control \
  --input-file my-app-control.yaml \
  --enabled \
  --oid <oid> --output yaml
```

The validation the web UI applies when you save also applies here, and an invalid record is rejected.

## Verifying the applied policy

A policy converges on each endpoint at its next sync. To see what an endpoint is actually running, task it with `app_control_policy`, from the Sensor Console or the API. The command takes no arguments, and it works on Windows and macOS only. It succeeds even when no policy is installed: "this endpoint is enforcing nothing" is a valid answer.

The `APP_CONTROL_POLICY_REP` reply carries:

| Field | Description |
| --- | --- |
| `APP_CONTROL_STATUS` | The endpoint's application control posture. See [Status fields](#status-fields). |
| `FILE_PATH` | Where the endpoint keeps its cached copy of the signed policy. Reported even when no policy is installed. |
| `APP_CONTROL_KEY_ID` | The IDs of the signing keys the endpoint accepts a policy from. If every policy is refused, compare these with the key the policy was signed with. |
| `APP_CONTROL_N_RULES` | The total number of rules in the installed policy |
| `APP_CONTROL_RULES` | The rules themselves, each with its `APP_CONTROL_RULE_ID`, `APP_CONTROL_RULE_ACTION` (`0` allow, `1` deny), `APP_CONTROL_RULE_KIND` (`0` path, `1` signer, `2` signing ID, `3` signer root, `4` sha256) and `APP_CONTROL_RULE_VALUE`. At most 256 rules are listed. If `APP_CONTROL_N_RULES` is larger than the list, the list was truncated. |

### Status fields

`APP_CONTROL_STATUS` is the same posture block the endpoint sends the cloud on every sync:

| Field | Description |
| --- | --- |
| `APP_CONTROL_MODE` | The mode in force: `0` off, `1` permissive, `2` permissive_sync, `3` enforcing. This can be lower than the mode in your policy. See `POLICY_STALE` in [Degraded flags](#degraded-flags). |
| `APP_CONTROL_STANCE` | What happens to an executable no rule matched: `0` blocklist (it runs), `1` allowlist (it is denied) |
| `APP_CONTROL_GENERATION` | The installed policy's generation: the time, in epoch seconds, at which LimaCharlie issued it. `0` means no policy is installed. |
| `APP_CONTROL_POLICY_AGE_SEC` | Seconds since the installed policy was issued. Absent when no policy is installed. |
| `APP_CONTROL_N_EVALUATED` | Executions evaluated since the agent started |
| `APP_CONTROL_N_DENIED` | Of those, how many the policy denied, whether enforced or only reported |
| `APP_CONTROL_N_UNRESOLVED` | Of those, how many reached no decision and were therefore allowed |
| `APP_CONTROL_DEGRADED` | A bit mask of the reasons enforcement is not complete. `0` means nothing is wrong. See [Degraded flags](#degraded-flags). |
| `APP_CONTROL_ENFORCED` | What the enforcement component itself reports. See below. Absent when the component did not answer, which means "unknown", never "all is well". |

The counters are cumulative, and they reset when the agent restarts. Subtract two samples to get a rate.

The component that actually allows or denies an execution is separate from the agent process. On Windows it is the kernel driver, which asks the agent for each decision. On macOS it is the system extension, which holds its own copy of the policy and decides by itself. `APP_CONTROL_ENFORCED` reports what that component holds, using the same field names as the status block around it, so any disagreement shows up as two different values of the same field:

| Field | Description |
| --- | --- |
| `APP_CONTROL_MODE` | The mode the enforcement component is applying |
| `APP_CONTROL_GENERATION` | The policy generation it holds. If this differs from the status block's generation, the component is applying a different policy from the one the agent installed. |
| `APP_CONTROL_N_RULES` | The number of rules it holds. macOS only, because the Windows driver holds no rules. |
| `APP_CONTROL_N_ASKED` | How many executions it has asked the agent to decide. Windows only. On an endpoint that is enforcing, a value that never increases means no execution is actually being checked. |
| `APP_CONTROL_N_OVERLOADED` | Executions it allowed without a decision, because it was at capacity or a decision did not arrive in time. Always reported, including when it is `0`. |
| `APP_CONTROL_IS_CONNECTED` | `1` if the agent is connected to answer it. A Windows driver with no agent connected cannot enforce. The macOS system extension always reports `1`. |
| `APP_CONTROL_BREAK_GLASS` | `1` if a local break-glass is in effect, such as a Windows Safe Mode boot. Executions are then not denied until the next normal boot, whatever the mode says. |

### Degraded flags

`APP_CONTROL_DEGRADED` is a bit mask, and several flags can be set at once. For example, `68` (`0x44`) is `HASH_UNAVAILABLE` together with `LEASE_LAPSED`.

| Value | Flag | Meaning | What to do |
| --- | --- | --- | --- |
| `1` (`0x1`) | `NO_POLICY` | No policy is installed. Either none has been received, or the cached copy could not be used. | Check that a policy targets this endpoint. If one does, look for `APP_CONTROL_UNRESOLVED` events with a reason in the `20`–`28` range. |
| `2` (`0x2`) | `POLICY_STALE` | The installed policy is older than the `max_age_sec` its document sets. The endpoint keeps it, but lowers its mode to permissive, so it is no longer blocking. Never set for a policy without a maximum age. See [Policy expiry](#policy-expiry). | Get a fresh copy of the policy onto the endpoint. A host that has been offline gets one on its next sync. |
| `4` (`0x4`) | `HASH_UNAVAILABLE` | A decision needed the file's SHA-256 and could not get it, for example because the file is larger than 50 MiB. That execution was allowed. The flag stays set until the agent restarts. | Look at the `APP_CONTROL_UNRESOLVED` events with reason `50`, and replace the `sha256` rules involved with `signer` or `path` rules. |
| `8` (`0x8`) | `NOT_ENFORCED` | A policy is installed, but no enforcement component has it, so nothing on the endpoint is acting on it. | Check that the Windows kernel driver or the macOS system extension is installed and running. |
| `16` (`0x10`) | `ENFORCED_SKEW` | The enforcement component holds a different policy generation from the agent, so the wrong policy is deciding executions. Compare the two `APP_CONTROL_GENERATION` values. | Usually clears on its own once the component catches up. If it persists, contact support. |
| `32` (`0x20`) | `NO_ENFORCED_KEY` | The macOS system extension has no signing key, so it refuses every policy it is given. | Contact support. |
| `64` (`0x40`) | `LEASE_LAPSED` | The enforcement component has not heard from the agent recently, so it has dropped to permissive whatever its mode says. This is the safety mechanism that stops a hung agent from blocking a host. | Check the agent's health on that endpoint. The component re-arms as soon as the agent responds again. |
| `128` (`0x80`) | `ON_ENABLE_IGNORED` | The policy asks for something to be done about processes already running when enforcement starts, and this agent does not support that. Running processes are left alone. Policies from the Application Control extension never ask for this. | None needed. |
| `256` (`0x100`) | `SENSOR_IDS_NOT_APPLIED` | The endpoint is not using the list of LimaCharlie's own signing identities that came with the policy. It keeps exempting the identities it already knew instead. Your rules are still applied. This usually means the endpoint runs an agent build signed with an identity LimaCharlie has since retired. | [Upgrade](../../../2-sensors-deployment/endpoint-agent/versioning-upgrades.md) the agent. |

## Events

| Event | Emitted when |
| --- | --- |
| `APP_CONTROL_DENIED` | The policy refused an execution, whether it was stopped (`enforcing`) or only reported (`permissive`, `permissive_sync`) |
| `APP_CONTROL_UNRESOLVED` | No decision could be reached, so the execution was allowed |
| `APP_CONTROL_POLICY_REP` | Reply to the `app_control_policy` command |

`APP_CONTROL_DENIED` and `APP_CONTROL_UNRESOLVED` carry:

| Field | Description |
| --- | --- |
| `FILE_PATH` | Path of the executable that was judged |
| `PROCESS_ID` | Process ID of the execution |
| `HASH` | SHA-256 of the executable, when it was computed |
| `APP_CONTROL_SIGNER` | Who signed the executable, in the exact form a `signer` rule matches. Present only for a signature the OS verified. |
| `APP_CONTROL_SIGNING_ID` | The code-signing identifier, in the form a `signing_id` rule matches (macOS only) |
| `APP_CONTROL_MATCHED_RULE` | The rule that produced the decision, as `action:kind:value` |
| `APP_CONTROL_DECISION` | `0` allow, `1` deny, `2` unresolved |
| `APP_CONTROL_REASON` | Why the decision was reached. See below. |
| `APP_CONTROL_IS_ENFORCED` | `true` if the execution was actually stopped. `false` if it was only reported. |
| `APP_CONTROL_MODE` | The mode in force: `0` off, `1` permissive, `2` permissive_sync, `3` enforcing |
| `APP_CONTROL_GENERATION` | Generation of the policy that made the decision |

Common `APP_CONTROL_REASON` values:

| Code | Meaning |
| --- | --- |
| `10` | A deny rule matched |
| `11` | Nothing matched, and the stance is allowlist |
| `20`–`28` | No usable policy, for example none received yet, failed verification, expired, or refused by the endpoint |
| `30`–`33` | No enforcement channel, for example a driver or OS version that cannot deny executions |
| `40`–`45` | The decision ran out of time or capacity |
| `50`–`52` | The executable could not be examined reliably, for example it was too large to hash |

All three events are in the default event collection set on Windows and macOS. If you have customized event collection under **Sensors** / **Event Collection**, add:

```text
APP_CONTROL_DENIED,APP_CONTROL_UNRESOLVED,APP_CONTROL_POLICY_REP
```

You can write [D&R rules](../../../3-detection-response/index.md) on these events like on any other. For example, you could alert when `APP_CONTROL_IS_ENFORCED` is `true` on a server, or open a case when an endpoint reports a burst of `APP_CONTROL_UNRESOLVED`.

## See Also

- [DLP](dlp.md): USB device control, configured the same way
- [Exfil](exfil.md): event collection configuration
- [Sensor Tags](../../../2-sensors-deployment/sensor-tags.md): targeting policies
- [D&R Rules](../../../7-administration/config-hive/dr-rules.md): managed rules, including `ext-app-control-sync`
