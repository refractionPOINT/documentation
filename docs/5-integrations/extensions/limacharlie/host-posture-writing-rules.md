# Host Posture: Writing Your Own Rules

A [Host Posture](host-posture.md) rule is one document in the `lc-posture/v1` language. It declares what to read on a host (the **probes**), a condition that says when the host has the problem (the **violation**), the evidence to report, and tests. The sensor evaluates it on the host. Nothing runs on the host except reads.

Every rule is equally trusted. A rule you write can do everything a rule of LimaCharlie's default pack can do. The platform keeps the same safety guarantees for all of them: reads only, bounded in time and memory, and a [deny list](#paths-and-the-deny-list) for sensitive files.

Store the finished rule as a record of the [`host_posture_rule`](../../../7-administration/config-hive/host-posture-rule.md) hive. The rules of the default pack, listed with `limacharlie host-posture rules list`, are good examples to copy from.

## A first rule

This rule flags Linux hosts where `fs.protected_symlinks` is off. It is a simplified version of a rule of the default pack:

```yaml
apiVersion: lc-posture/v1
kind: Signature
id: acme.linux.fs.protected-symlinks
version: 1
title: Symlink protection is off
description: >
  With fs.protected_symlinks=0, a local user can trick a privileged program into
  following a symlink planted in a world-writable directory.
severity: medium
platforms: [linux]
requires:
  evaluator: "1.0"
probes:
  sl: { sysctl: fs.protected_symlinks }
violation: 'absent(sl) || sl.value != "1"'
evidence:
  protected_symlinks: 'absent(sl) ? "absent" : sl.value'
remediation:
  text: Set fs.protected_symlinks=1 in /etc/sysctl.d/.
tests:
  - name: on
    probes: { sl: { status: ok, value: "1" } }
    expect: pass
  - name: off
    probes: { sl: { status: ok, value: "0" } }
    expect: fail
  - name: not present
    probes: { sl: { status: absent } }
    expect: fail
  - name: unreadable
    probes: { sl: { status: unreadable } }
    expect: error
```

To store it, wrap it in a record (`rule` is the document as JSON, so convert the YAML if you use the API):

```bash
limacharlie host-posture rules set \
  --key acme.linux.fs.protected-symlinks \
  --input-file protected-symlinks-record.yaml \
  --enabled
```

where the file holds `rule:` with the document above, and an optional `scope:`. The hive validates the whole rule, runs its tests, and refuses the record with the field path of each problem.

## The document

| Field | Required | Description |
| --- | --- | --- |
| `apiVersion` | Yes | `lc-posture/v1`. |
| `kind` | Yes | `Signature`. |
| `id` | Yes | Lowercase, dot-separated, for example `acme.windows.rdp.no-nla`. Any prefix is allowed. Must equal the record name. Ids are never reused: a different question gets a new id. |
| `version` | Yes | An integer. Raise it whenever you change the probes or the conditions. |
| `title` | Recommended | One line, shown in findings and results. |
| `description` | Recommended | What is wrong and why it matters, in plain language. |
| `severity` | Yes | `critical`, `high`, `medium`, `low` or `info`. |
| `platforms` | Yes | One or more of `linux`, `windows`, `macos`. |
| `tags` | No | Labels for the rule itself, such as `baseline:windows`. Not sensor tags: for those use the record's [scope](../../../7-administration/config-hive/host-posture-rule.md#scope). |
| `threat_refs` | No | `cves`, `kev` (true if a listed CVE is in the CISA KEV catalog) and `links`. |
| `standards` | No | Maps a framework (`cce`, `cis`, `stig`, `nist`, `pcidss`) to control ids. Used to report how hosts do against each standard. |
| `requires.evaluator` | No | The minimum sensor evaluator version, as `<major>.<minor>`, for example `"1.0"`. A sensor below it reports the rule as `unsupported`. |
| `probes` | Yes | Name to probe. At most 16. |
| `applies_when` | No | A condition. If false the rule is `not_applicable` on the host. |
| `violation` | Yes | A condition that is true when the host has the problem. |
| `evidence` | No | Label to expression, evaluated only when the rule fails. |
| `absent_is_pass` | No | Probes whose absence genuinely means the host is not exposed. See [Absence](#absence). |
| `tolerate_unreadable` | No | Probes that count as readable even when they could not be read. See [Reading errors](#reading-errors). |
| `remediation` | Yes | `text` with the manual steps. Optionally `action` and `args`, naming a reversible remediation. |
| `limitations` | No | What the rule cannot see. Worth writing. |
| `tests` | No | Test cases. See [Testing a rule](#testing-a-rule). |

Fields not listed here are refused, so a misspelled field cannot be silently ignored. A probe's own settings are checked the same way.

Probe names are lowercase identifiers (`[a-z_][a-z0-9_]*`) and cannot be a CEL reserved word, nor `now` or `instance`. They are the variables your conditions use.

## Probes

A probe is a read on the host. Each has a `status`:

| `status` | Meaning |
| --- | --- |
| `ok` | The thing was read. Its value fields are present. |
| `absent` | It does not exist: a missing sysctl, file or registry value. |
| `unreadable` | It exists, or should, but could not be read: permissions, an I/O error, a timeout, a budget. |
| `invalid` | It was read, but its content was not what it must be, such as a file that does not parse. |
| `unsupported` | The evaluator cannot run this probe on this platform or at this version. |

Value fields exist **only** when the status is `ok`. Reading a value that is not there is an error in the condition, and the result is `error`, never `pass`. All values read from the host are strings: use `num()` to compare as a number.

A probe that hit a cap carries `truncated: true`. A truncated read can prove a failure but never a pass.

| Probe | Reads | Result |
| --- | --- | --- |
| `state` | A catalog item, a `sysctl` (Linux), or a `registry` value (Windows). | `{status, value, source}` |
| `registry_values` | Every value of one registry key (Windows), for lists such as Defender exclusions. | `{status, source, values: [{name, value}], truncated}` |
| `modules` | Loaded kernel modules, those available and built in, and modprobe rules (Linux). | `{status, loaded, available, builtin, rules, ...}` |
| `config` | Selected keys from configuration files. | per-file entries with `matches` |
| `file` | File metadata: mode, owner, size, type, modification time. | `{status, mode, uid, gid, size, type, mtime}` |
| `certs` | Certificates in the trust stores. | `{status, truncated, certificates: [...]}` |
| `packages` | Installed packages. | `{status, truncated, packages: [{name, version, scheme, source}]}` |
| `yara` | Content of files and process memory, with YARA rules. | matches per target |

The forms of `state`:

```yaml
probes:
  ps:   { state: linux.sysctl.kernel.yama.ptrace_scope }   # a catalog item
  io:   { sysctl: kernel.io_uring_disabled }               # any sysctl under kernel., fs., net., user., vm. or dev.
  ppl:  { registry: { key: 'HKLM\SYSTEM\CurrentControlSet\Control\Lsa', value: RunAsPPL } }
```

A `registry` key must be under `HKLM\SYSTEM\CurrentControlSet\`, `HKLM\SOFTWARE\Policies\`, `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\`, `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\` or `HKLM\SOFTWARE\Microsoft\Windows Defender\`. A DWORD reads as decimal text.

### Configuration files

`config` parses files and returns only the keys you select:

```yaml
sshd:
  config:
    format: sshd                       # sshd | ini | json | yaml | nginx | raw
    paths: [/etc/ssh/sshd_config]      # absolute; * and ? allowed inside one path segment; at most 32 after expansion
    discover:                          # optional: bounded directory discovery
      - { dir: /etc/ssh/sshd_config.d, file_regex: '\.conf$', max: 10 }
    selectors: [PermitRootLogin]
```

What a selector is depends on the format:

| Format | Selector |
| --- | --- |
| `sshd` | A keyword, case-insensitive. Every occurrence is reported, with the enclosing `Match` line as its context. |
| `ini` | A key name. The section header is the context. |
| `json`, `yaml` | A dotted path with `[n]` indexes. A `*` is allowed in a non-final segment. A list of scalars reports one match per element. |
| `nginx` | A dotted directive path, or a bare directive name that matches at any depth. The enclosing blocks are reported. Included files are read in their include context. |
| `raw` | `content`: the whole file, at most 4 KB. |

The probe returns `files`, one entry per file, with its `path`, its own `status` and its `matches` (`selector`, `found`, `key`, `value`, `line`, `context`). Files are read up to 10 MB, a value is cut at 4 KB, and a file or probe that hits a cap is `truncated`.

## Conditions

`applies_when`, `violation` and each `evidence` entry are [CEL](https://github.com/google/cel-spec) expressions. CEL is not Turing-complete, and every expression has a cost limit. Each probe is a variable of the same name.

The language provides exactly the following, and refuses any other function when you save the rule:

- Standard CEL: operators, `size`, `has()`, `in`, `string()`, the macros `exists`, `all`, `exists_one`, `filter` and `map`, and the string functions `contains`, `startsWith`, `endsWith` and `matches` (RE2 regular expressions, with a pattern that must be a string literal).
- `lowerAscii()`, `upperAscii()`, `split(sep)` with a literal separator, and `trim()`.
- Helpers:

| Helper | Returns |
| --- | --- |
| `ok(x)`, `absent(x)`, `unreadable(x)`, `invalid(x)` | Whether a probe or file entry has that status. |
| `num(s)` | The integer in a string (decimal or `0x` hex). An error for anything else. |
| `loaded(mods, name)`, `blacklisted(mods, name)`, `blocked(mods, name)` | Whether a kernel module is loaded, blacklisted, or blocked by an `install` rule. |
| `found(file, selector)`, `first(file, selector)`, `last(file, selector)`, `global_first(file, selector)` | Config matches in one file: the first or last one, or the first one outside any `Match` or block context. |
| `innermost(m)` | The innermost nginx block of a match. |
| `version_cmp(a, b, scheme)` | -1, 0 or 1, comparing versions with `dpkg`, `rpm` or `semver` rules. |
| `fixed_in_branch(version, fixed_map, scheme)` | Whether a version is fixed, for software that ships fixes per release branch. |
| `yara_hit(p, rule)`, `yara_paths(p, rule)` | Whether a YARA rule matched, and the matching paths. |
| `days_until(ts)` | Days until a timestamp, negative when it is past. |
| `now` | The evaluation time. |

`applies_when` must be a boolean. `violation` is a boolean or a list of strings, the [instances](#instances).

Prefer `!absent(p) && p.value == "0"` to `ok(p) && p.value == "0"` in guards, and write absence explicitly when absence is the problem: `absent(ps) || num(ps.value) < 2`. A condition cannot index a probe dynamically.

## How a result is decided

The evaluator applies the same steps to every rule:

1. If the evaluator is older than `requires.evaluator`, or the platform does not match, or a required probe is `unsupported`: `unsupported`.
2. Evaluate `applies_when` (default true). If it is false, and everything it read was readable and complete: `not_applicable`. If it read something unreadable: `error`.
3. Evaluate `violation`. If it is true (or a non-empty list): `fail`. A hit is a hit, even when something unrelated was unreadable.
4. Otherwise the result is `pass`, but only if every probe the conditions read was readable and complete. If not: `error`. If the pass depended on an absent item you did not declare in [`absent_is_pass`](#absence), the result is `not_applicable` by absence instead, and open findings are not closed.

The rule is simple: **a pass has to be proven.** An unreadable or truncated input never produces a `pass` or a `not_applicable`, except for a probe you listed in [`tolerate_unreadable`](#reading-errors). This is enforced by the evaluator, not by how you write your guards.

### Reading errors

An `error` finding is raised for a rule that could not be decided on a host. It carries a reason such as `unreadable:<probe>`, `invalid:<probe>`, `truncated:<probe>:<cap>` or `expression:violation:<message>`. It opens a finding, so a persistent problem is visible, but it does not count against severity totals.

If a probe may be unreadable without the rule being undecided, list it in `tolerate_unreadable`. The rule is then decided as if that probe had been read: a `pass` can result, and a truncated read still cannot prove one. An open failure is not closed on a reading where a tolerated probe was unreadable.

### Absence

An absent item usually does not mean "safe". A missing sysctl on a kernel that lacks the feature may mean the host is exposed or not. By default, a rule that would pass **because** something was absent reports `not_applicable` by absence instead, and does not close an existing finding. The finding is marked as not found, and closes only when a later scan proves the problem gone.

When absence really does mean "not exposed", list the probe in `absent_is_pass`:

```yaml
absent_is_pass: [sshd]   # no sshd_config means sshd is not installed
```

That is a claim you make as the author, so make it deliberately. Deleting a configuration file should never hide a setting that has a risky default without the file.

### Instances

`violation` can return a list of strings instead of a boolean. Each distinct string is one instance, and each instance is its own finding on the host, for example one per configuration file or per listener.

```yaml
violation: >
  sshd.files.filter(f, ok(f) && f.matches.exists(m, m.found && m.value.lowerAscii() == "yes"))
    .map(f, f.path)
```

At most 64 instances of at most 512 bytes are kept. When an instance no longer appears, it closes, but only if everything the rule read was readable and complete. A shorter list from a truncated read does not close anything.

An `evidence` expression can use the variable `instance` to give per-instance evidence.

### Evidence

`evidence` maps a label to an expression, evaluated only when the rule fails. Each value is capped at 1 KB and all of a finding's evidence at 8 KB. Write evidence that helps the person fixing the host (the value you found, the file it came from) and nothing more. Only declared evidence leaves the host.

Evidence goes through a [deny list](#paths-and-the-deny-list) that keeps secrets from reaching findings.

## Testing a rule

A rule can carry `tests`. Each test mocks the probes and states the expected result:

```yaml
tests:
  - name: sysctl is 1
    probes:
      sl: { status: ok, value: "1" }
    expect: pass
  - name: one config file sets yes
    probes: { ... }
    expect: fail
    instances: ["/etc/ssh/sshd_config"]        # optional, checked when present
    evidence: { set_in: "..." }                # optional, only the listed labels are compared
```

Tests are optional, but when a rule has them they must all pass or the hive refuses the record. A probe left out of a test is mocked as `unsupported`. A test of a rule that reads `now` must set `now:` (RFC 3339).

Good tests include at least one `fail`, one `pass` and one `error`, and one `not_applicable` when the rule has an `applies_when`.

A mocked result has to be one a real host could produce. A test that mocks a value on an `unreadable` probe, for example, is refused. Write tests for the awkward cases too: the probe absent, the probe unreadable, the config file that does not parse.

## Paths and the deny list

Paths are resolved on the host for real: `.` and `..` are resolved, symlinks are followed at every component, and Windows paths are compared case-insensitively. A path that leaves the allowed root through a symlink is refused. These are always refused: `/proc/<pid>/root`, `cwd` and `fd`, Windows `\\?\` and `\\.\` prefixes, UNC paths, alternate data streams and 8.3 short names.

A deny list covers sensitive locations for every rule, however it is written. A rule cannot read the content of:

- memory in file form, such as `/proc/**`, core dumps, swap and hibernation files and crash dumps;
- credentials and keys, such as `/etc/shadow`, SSH keys, certificate private keys, cloud credential files and browser credential stores;
- the Windows credential stores (`SAM`, `SECURITY`, `NTDS`, DPAPI keys) and registry values whose names suggest a secret.

A read of such a path is refused, and the refusal is reported, not hidden. A `file` probe reads metadata only, which is why a rule can still check that `/etc/shadow` has safe permissions.

## Limits

| Limit | Value |
| --- | --- |
| Probes per rule | 16 |
| Expanded paths per `config` probe | 32 |
| `discover` entries per probe | 8, each depth at most 3 and at most 64 directories |
| File read | 10 MB per config file, 4 KB for `raw` |
| `certs` | 4,096 certificates |
| `packages` | 4,096 matching packages |
| Condition | 4 KB of source, 32 levels of nesting, a bounded cost |
| Instances | 64 per rule per host, 512 bytes each |
| Evidence | 1 KB per value, 8 KB per finding |
| Rule document | 128 KiB as JSON |
| One sweep on a host | 300 s of wall clock, 60 s of CPU and 256 MB of memory |

Probes the host did not reach before the budget ran out are reported as unreadable, so a rule that could not finish is an `error`, never a `pass`.

## Tips

- Keep one question per rule. Findings, standards and severity are per rule.
- Begin with the closest rule of the default pack. Copy it under your own prefix, give it a new id and change only what you need.
- Write the `description` for the person who gets the finding, and say what the rule cannot see in `limitations`.
- Do not flag a stock configuration unless the default itself is the problem. If you do, say so in the `description`.
- Bump `version` when you change what a rule reads or decides.

## See Also

- [Host Posture](host-posture.md)
- [Host Posture rules (Config Hive)](../../../7-administration/config-hive/host-posture-rule.md)
- [Permissions](../../../8-reference/permissions.md#host-posture)
