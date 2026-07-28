# AI Skills

AI Skills let you store reusable [Claude Code skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) definitions in your LimaCharlie organization. A skill is a self-contained instruction set: a `SKILL.md` document and optional supporting files. Claude loads a skill on demand when the description of the skill matches the current work. When you store skills in LimaCharlie, every AI Session that your organization runs (D&R-driven, CLI-launched, or interactive) starts with the same library of operational knowledge. You do not need to add that knowledge to each prompt or session profile.

Each skill record maps one to one to an on-disk Claude Code skill directory. The `SKILL.md` body is in the `content` field of the record. The YAML frontmatter becomes typed fields with the same names as the official spec. Bundled scripts and reference documents go in a `files` map, keyed by their path relative to the skill root.

## When to use a skill

- **Codify operating procedures.** Record "how we triage lateral-movement detections" or "how we close a phishing case" one time. Every analyst session then loads it automatically.
- **Bundle helper scripts and reference material.** A skill can carry its own shell helpers, queries, or markdown notes with the instructions. The agent reads them when it loads the skill.
- **Keep prompts terse.** Prompts and `ai_agent` records state *what* to do. The skill states *how* to do it, and you can reuse the skill.

For the underlying skill model, see the upstream [Claude Code Skills documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview). It covers when Claude loads a skill, the trigger budget for `description` + `when_to_use`, the `allowed-tools` grammar, and more. The LimaCharlie store mirrors that schema exactly.

## Record format

A skill record has one required field, `content`, and the optional frontmatter fields below. The fields use the same names as the on-disk `SKILL.md` frontmatter. A skill can therefore move between a developer's filesystem and the LimaCharlie hive with no renamed field.

### Required

| Field | Type | Description |
|---|---|---|
| `content` | string | The `SKILL.md` body — the markdown instructions that Claude reads when the skill loads. |

### Frontmatter

| Field | Type | Description |
|---|---|---|
| `name` | string | Slug, `[a-z0-9-]{1,64}`. Optional — defaults to the record key. |
| `description` | string | Short summary that decides when to invoke the skill. |
| `when_to_use` | string | More trigger context. It counts against the same budget as `description` (combined ≤ 1536 characters). |
| `argument-hint` | string | Hint shown in slash-command autocomplete (e.g. `[issue-number]`). |
| `arguments` | list / string | Named positional arguments for `$name` substitution in `content`. Accepts a list or a space-separated string. |
| `disable-model-invocation` | boolean | When `true`, Claude does not auto-load the skill. You can still invoke the skill explicitly. |
| `user-invocable` | boolean | When `false`, the skill is background knowledge only and does not appear in the slash-command menu. |
| `allowed-tools` | list / string | Pre-approved tool list with the same grammar as session profiles (e.g. `Bash(git:*)`, `Read`). See [Tool Permissions & Profiles](tool-permissions.md). |
| `model` | string | Model override while the skill is active. The literal `inherit` keeps the model of the session. |
| `effort` | string | One of `low`, `medium`, `high`, `xhigh`, `max`. |
| `context` | string | Isolation mode. Only `fork` is accepted. |
| `agent` | string | Subagent type used when `context: fork`. Ignored in other cases. |
| `hooks` | object | Skill-lifecycle hooks. Pass-through to Claude Code — see its hooks documentation for the schema. |
| `paths` | list / string | Glob patterns that limit auto-invocation to matching file paths. Accepts a list or a comma-separated string. |
| `shell` | string | Shell used for `!` blocks. Either `bash` or `powershell`. |

### Bundled files

| Field | Type | Description |
|---|---|---|
| `files` | map | Supporting files keyed by path relative to the skill root (e.g. `scripts/helper.sh`, `reference/api.md`). Maximum 100 entries. The `SKILL.md` file does not appear here — its body is in `content`. |

File paths must be relative and canonical, with forward slashes and no `./` or `../` traversal. A path must not be `SKILL.md`, which is reserved for `content`.

### Limits

- Combined `description` + `when_to_use`: 1536 characters
- Bundled files: 100 entries
- Total record size: 10 MB

## Example

A minimal skill that gives Claude a triage workflow and one helper script:

```yaml
data:
  content: |
    # Triage a lateral-movement detection

    1. Pull the process tree for the source host with `lc events`.
    2. Cross-reference the destination host against the asset inventory.
    3. Run `scripts/check_lateral.sh` to summarise authentication anomalies
       on both hosts.
    4. Open a case with the findings; link the original detection.

  description: Triage a lateral-movement detection end to end.
  when_to_use: >
    Use when a detection in the `lateral-movement` category fires and you
    need a single, repeatable workflow to investigate it.
  allowed-tools:
    - Bash(scripts/*:*)
    - Read
    - Grep
  files:
    scripts/check_lateral.sh: |
      #!/bin/bash
      set -euo pipefail
      # ... helper body ...

usr_mtd:
  enabled: true
```

Disabled skills (`enabled: false` in `usr_mtd`) stay in the store. The session skips them when it enumerates the available skills.

## Permissions

| Operation | Permission |
|---|---|
| List / get | `ai_skill.get` |
| Create / update | `ai_skill.set` |
| Delete | `ai_skill.del` |
| Read metadata | `ai_skill.get.mtd` |
| Update metadata | `ai_skill.set.mtd` |

## Managing skills

### CLI

```bash
# List every skill in the org.
limacharlie ai-skill list

# Get one skill (frontmatter, content, and any bundled files).
limacharlie ai-skill get --key triage-lateral

# Create or replace a skill from a YAML file. New hive records are
# disabled by default, so pass --enabled (or include usr_mtd.enabled:
# true in the file) if you want the skill picked up by AI sessions.
limacharlie ai-skill set --key triage-lateral --input-file triage.yaml --enabled

# Or pipe it in.
cat triage.yaml | limacharlie ai-skill set --key triage-lateral --enabled

# Toggle without deleting the record.
limacharlie ai-skill disable --key triage-lateral
limacharlie ai-skill enable  --key triage-lateral

# Remove the skill entirely.
limacharlie ai-skill delete  --key triage-lateral --confirm
```

The `set` payload uses the same `data` / `usr_mtd` envelope as any other Hive record. The format mirrors the on-disk Claude Code skill directory. The frontmatter keys go under `data`, next to `content` and `files`.

### REST API

Skills are in the `ai_skill` Hive, so the standard Hive endpoints apply:

```bash
# List
curl -s -X GET \
  "https://api.limacharlie.io/v1/hive/ai_skill/$OID" \
  -H "Authorization: Bearer $LC_JWT"

# Set
curl -s -X POST \
  "https://api.limacharlie.io/v1/hive/ai_skill/$OID/triage-lateral/data" \
  -H "Authorization: Bearer $LC_JWT" \
  --data-urlencode "data=$(cat triage.json)"
```

### Python SDK

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive, HiveRecord

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
hive = Hive(org, "ai_skill")

# enabled=True so the skill is picked up by AI sessions immediately —
# new hive records are disabled by default.
hive.set(HiveRecord("triage-lateral", data={
    "content": "...SKILL.md body...",
    "description": "Triage a lateral-movement detection end to end.",
    "allowed-tools": ["Read", "Grep", "Bash(scripts/*:*)"],
    "files": {
        "scripts/check_lateral.sh": "#!/bin/bash\n...\n",
    },
}, enabled=True))
```

## Related

- [User Sessions](user-sessions.md) — interactive sessions that load the skill library of the organization.
- [D&R-Driven Sessions](dr-sessions.md) — automated sessions; the same skills apply.
- [AI Memory](memory.md) — companion store for per-agent state that must persist across runs.
- [Tool Permissions & Profiles](tool-permissions.md) — grammar for `allowed-tools` entries.
