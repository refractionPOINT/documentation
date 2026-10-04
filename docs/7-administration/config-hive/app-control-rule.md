# Config Hive: Application Control Rules

The `app_control_rule` hive holds the allow and deny rules of [Application Control](../../5-integrations/extensions/limacharlie/app-control.md). Each rule is one record. The record name is the rule id, up to 64 bytes. A rule says what to match (a path, a signer, a file hash) and whether to allow or deny it, and it can be limited to specific [policies](app-control-policy.md).

Like the policy hive, `app_control_rule` is partitioned by organization.

## Format

```json
{
    "action": "allow",
    "kind": "path",
    "value": "C:\\Program Files\\",
    "policies": ["windows-allowlist"]
}
```

| Field | Required | Description |
| --- | --- | --- |
| `action` | Yes | `allow` or `deny`. |
| `kind` | Yes | What `value` matches. One of `path`, `signer`, `signing_id`, `signer_root`, `sha256`. See [Rule kinds](#rule-kinds). |
| `value` | Yes | The value to match. No leading or trailing whitespace, at most 1024 bytes. |
| `policies` | No | List of `app_control_policy` record names the rule applies to. Empty or omitted means the rule applies to every policy. At most 64 entries, with no duplicates. |

Keywords are case-sensitive and must be lowercase exactly as shown. Unknown fields are refused when you save the record.

Two things live in the record's metadata rather than in its data:

- A comment explaining why the rule exists goes in the metadata `comment`.
- A temporary exception takes a metadata `expiry`. See [A temporary exception](#a-temporary-exception).

Only enabled records apply. Records created without metadata are enabled by default in this hive.

## Rule kinds

| Kind | Matches | Platforms |
| --- | --- | --- |
| `path` | An exact file path. If the value ends with `\` or `/`, it matches every file under that directory instead. | Windows, macOS |
| `signer` | The Authenticode subject of the signing certificate on Windows, or the Apple Team ID on macOS. | Windows, macOS |
| `signing_id` | The macOS code-signing identifier. | macOS |
| `signer_root` | The SHA-256 thumbprint of any certificate in the validated certificate chain. | Windows |
| `sha256` | The SHA-256 hash of the file, as 64 hex characters. | Windows, macOS |

Notes on each kind:

- **`path`.** There are no wildcards. `*` and `?` are literal characters. Matching is case-insensitive for ASCII characters.
- **`signer_root`.** Use the 64-character SHA-256 thumbprint. Windows shows the 40-character SHA-1 thumbprint by default, and that value does not match. The rule matches if any certificate in the chain, root or intermediate, has the thumbprint.
- **`sha256`.** A hash rule pins one exact build of one file. It stops matching when the vendor ships an update, so it suits denying a known bad file better than allowing software that updates.

A path rule that allows a directory also allows whatever a user can write into it. Prefer signer rules for software that installs somewhere users can write, and keep path allows to locations that only administrators can change.

## How rules are evaluated

The sensor evaluates the rules that apply to the sensor's policy in this order and stops at the first answer:

1. Deny rules. If any deny rule matches, the execution is denied.
2. Allow rules.
3. OS vendor trust, if the policy has `trust_os_vendor: true`.
4. The policy stance. An `allowlist` denies anything not allowed. A `blocklist` allows anything not denied.

So a deny rule always wins over an allow rule, whatever their order or names. Under a `blocklist`, an allow rule never changes an outcome.

At most 10,000 rules may apply to a single policy. A rule with an empty `policies` list counts toward every policy.

## Permissions

Managing records in the `app_control_rule` hive requires:

- `app_control.get` to read rules.
- `app_control.set` to create, edit and delete rules and their metadata.

See [Permissions](../../8-reference/permissions.md#application-control).

## Examples

The examples use the CLI generic hive commands. Pass `--oid <oid>` if your CLI is not already pointed at the organization. They build on the `windows-allowlist` policy from the [policy page](app-control-policy.md#a-windows-allowlist-policy).

### An allow rule for a directory

Save this as `rule.json`. The trailing backslash makes it a directory prefix. In JSON, each backslash is written twice.

```json
{
    "action": "allow",
    "kind": "path",
    "value": "C:\\Program Files\\",
    "policies": ["windows-allowlist"]
}
```

```bash
limacharlie hive set \
  --hive-name app_control_rule \
  --key allow-program-files \
  --input-file rule.json \
  --enabled \
  --comment "Software installed by administrators"
```

### An allow rule for a signer

This allows everything signed by a company. The `value` is the Authenticode subject of the signing certificate.

```json
{
    "action": "allow",
    "kind": "signer",
    "value": "C=US, S=California, L=San Francisco, O=Example Corp, CN=Example Corp",
    "policies": ["windows-allowlist"]
}
```

Take the exact string from a real execution rather than typing it. The `APP_CONTROL_SIGNER` field of an `APP_CONTROL_DENIED` event shows the signer the sensor saw. See [Reading would-be blocks](../../5-integrations/extensions/limacharlie/app-control.md#reading-would-be-blocks).

### A deny rule that overrides allows

Because deny rules are evaluated first, this blocks a user-writable location even though other rules allow broad areas.

```json
{
    "action": "deny",
    "kind": "path",
    "value": "C:\\Users\\Public\\"
}
```

With no `policies` list it applies to every policy.

### Denying a known file by hash

```json
{
    "action": "deny",
    "kind": "sha256",
    "value": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
}
```

The value above is a placeholder. Use the real SHA-256 of the file.

### A temporary exception

Give a vendor installer a time-limited allow. Set the expiry with the CLI `--expiry` flag, which takes Unix epoch **seconds**.

```json
{
    "action": "allow",
    "kind": "path",
    "value": "C:\\Temp\\vendor-setup.exe",
    "policies": ["windows-allowlist"]
}
```

```bash
limacharlie hive set \
  --hive-name app_control_rule \
  --key temp-allow-vendor-setup \
  --input-file temp-rule.json \
  --enabled \
  --expiry 1793491200 \
  --comment "Vendor installer, approved for the November maintenance window"
```

`1793491200` is 2026-11-01 00:00:00 UTC. The hive stores expiry in milliseconds, so `hive get` shows `1793491200000`. If you write the record with a `usr_mtd` block instead of the flag, give the expiry in milliseconds there.

### Listing and reading rules

```bash
limacharlie hive list --hive-name app_control_rule
limacharlie hive get --hive-name app_control_rule --key allow-program-files
```

## Limits

- Record name (the rule id): 64 bytes.
- `value`: 1024 bytes.
- `policies` entries per rule: 64.
- Rules applying to a single policy: 10,000.

## See Also

- [Application Control](../../5-integrations/extensions/limacharlie/app-control.md)
- [Application Control policies](app-control-policy.md)
- [Config Hive overview](index.md)
