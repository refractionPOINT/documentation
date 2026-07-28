# Config Hive

The Config Hive is the hierarchical configuration store of LimaCharlie. It gives you one central place to manage configurations that the platform can reference.

## Hive Types

- [D&R Rules](dr-rules.md) - Storage for detection and response rules
- [Lookups](lookups.md) - Key-value lookup tables for enrichment
- [Secrets](secrets.md) - Secure management of credentials
- [YARA](yara.md) - Storage and management of YARA rules
- [Cloud Sensors](cloud-sensors.md) - Configurations for cloud sensors
- [Apps](apps.md) - Mini web applications that users write with AI
- [SOPs](../../9-ai-sessions/sops.md) - Standard Operating Procedures that AI agents read and obey

## Usage

You can use hive records in these ways:

- Reference them in D&R rules with the `hive://` prefix
- Manage them with the web app, the CLI, or the API
- Put them under version control with the Git Sync extension

!!! warning "New records are disabled by default"
    The cloud creates every new Hive record **disabled**, unless the request sets `usr_mtd.enabled: true`. This applies to D&R rules, FP rules, secrets, lookups, YARA sources, cloud sensors, AI skills, playbooks, and other record types. The cloud stores a disabled record normally, but every consumer that obeys the flag skips it. Rules do not fire, lookups are not queried, and AI skills are not enumerated. If a record exists but nothing happens, check `usr_mtd.enabled` first.

    To enable a record when you create it, do one of these:

    1. Pass `--enabled` on the CLI `set` command, for example `limacharlie secret set --key … --input-file … --enabled`.
    2. Include `usr_mtd.enabled: true` in the request body or the input file.
    3. Set `enabled=True` (Python SDK) or `Enabled: &enabled` (Go SDK) on the record before you call `set` or `Add`.

    You can also call the matching `enable` subcommand after you create the record (`limacharlie <hive> enable --key …`).

---

## See Also

- [D&R Rules](dr-rules.md)
- [Secrets Manager](secrets.md)
- [Lookups](lookups.md)
