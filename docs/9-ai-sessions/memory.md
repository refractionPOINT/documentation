# AI Memory

AI Memory is a key/value store for each agent. It holds content that must outlive one AI Session. [Skills](skills.md) record *how* an agent works. Memory records *what the agent learned*: facts about the environment, earlier decisions, open investigations, and anything else the agent must recall on its next run.

Each agent owns one record. You pick the agent identifier that keys the record. Inside the record, names in a filesystem style address each memory (`notes/today`, `cases/INC-123/timeline`, `runtime/last-seen-host`, …). Writes are partial. To set one named memory, you do not need to read the rest of the record. Parallel writes to different memory names on the same agent do not need to coordinate.

## How writes merge

Memory uses a partial-merge model on the server. An agent can update one entry at a time and does not send the whole record:

- **Set** with `{"<name>": "<content>"}` replaces that one entry. The other memories on the agent stay unchanged.
- **Set** with `{"<name>": null}` deletes that one entry. The other memories stay unchanged.
- **Delete the whole record** to remove all memories for an agent in one call.

An agent can therefore add notes step by step during a session — `progress/step-1`, `progress/step-2` — and never fetch the full record. Two agents, or two parallel turns, that write to different memory names do not overwrite each other.

## Naming rules

Memory names obey filesystem conventions:

- Relative paths only — no leading `/`.
- Forward slashes only — no `\`.
- Canonical form — `./` and `../` segments are rejected.
- No traversal above the record root.
- Maximum 256 characters for each name.

Use the path structure to organize memories (`runtime/`, `notes/`, `cases/<id>/…`). The store ignores the segments, but a consistent layout makes it easier to list or delete a subset.

## Limits

- Memories per agent record: 1024
- Memory name length: 256 characters
- Total record size: 10 MB

## Permissions

| Operation | Permission |
|---|---|
| List / get | `ai_memory.get` |
| Create / update / drop | `ai_memory.set` |
| Delete a whole agent record | `ai_memory.del` |
| Read metadata | `ai_memory.get.mtd` |
| Update metadata | `ai_memory.set.mtd` |

## Managing memory

### CLI

The `ai-memory` command group separates two sets of commands. `get`, `set`, and `delete` operate on one memory entry and take both `--key` and `--memory-name`. `list-records` and `delete-record` operate on the whole agent record.

```bash
# Enumerate every agent that has memory stored.
limacharlie ai-memory list-records

# List the memory entries on one agent.
limacharlie ai-memory list --key triage-bot

# Read one memory entry.
limacharlie ai-memory get --key triage-bot --memory-name notes/today

# Write or replace one memory entry (other memories preserved).
limacharlie ai-memory set --key triage-bot \
    --memory-name notes/today --content "wrote the cli wrapper"

# Pipe content from a file or another command.
cat findings.md | limacharlie ai-memory set \
    --key triage-bot --memory-name cases/INC-123/timeline

# Drop one memory entry (other memories preserved).
limacharlie ai-memory delete --key triage-bot \
    --memory-name notes/today --confirm

# Drop every memory the agent has stored.
limacharlie ai-memory delete-record --key triage-bot --confirm
```

### REST API

Memory is in the `ai_memory` Hive. To set or delete one entry and keep the others, send only that entry in the `memories` field. The server does the merge.

```bash
# Set one memory (other memories preserved).
curl -s -X POST \
  "https://api.limacharlie.io/v1/hive/ai_memory/$OID/triage-bot/data" \
  -H "Authorization: Bearer $LC_JWT" \
  --data-urlencode 'data={"memories":{"notes/today":"wrote the cli wrapper"}}'

# Drop one memory (other memories preserved).
curl -s -X POST \
  "https://api.limacharlie.io/v1/hive/ai_memory/$OID/triage-bot/data" \
  -H "Authorization: Bearer $LC_JWT" \
  --data-urlencode 'data={"memories":{"notes/today":null}}'
```

A read of the record returns every memory under `data.memories`.

### Python SDK

The `AiMemory` client wraps the partial-merge behavior. A caller can operate on one entry at a time:

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.ai_memory import AiMemory

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
am = AiMemory(org)

# Write or replace one memory.
am.set("triage-bot", "notes/today", "wrote the cli wrapper")

# Read one memory.
content = am.get("triage-bot", "notes/today")

# Update many entries in one call (None drops the entry).
am.set_many("triage-bot", {
    "progress/step-1": "done",
    "progress/step-2": "in flight",
    "notes/today": None,
})

# Drop one memory; everything else on the agent is preserved.
am.delete("triage-bot", "progress/step-1")

# Wipe the agent record entirely.
am.delete_record("triage-bot")
```

## Profile memory bank

AI Memory (above) is an **org-scoped, per-agent** store in the
`ai_memory` Hive. A second and different kind of memory exists: the **profile memory
bank**. The bank is **per user, and its lifecycle is tied to a [session profile](user-sessions.md#session-profiles)**.

When you start a session from a profile, the markdown files of the bank are mounted
into the session workspace at `/workspace/.memory/<path>`. The edits that the agent makes
there during the session are synced back to the profile. Use the bank for notes,
runbooks, and reference material that you need in every session with a given
profile. You and the agent can both edit these files.

| | AI Memory (`ai_memory`) | Profile memory bank |
|---|---|---|
| Scope | Organization, per agent | A single user's profile |
| Managed with | CLI / API / SDK (Hive) | Profile management, mounted into the session |
| Mounted in session | No (the agent reads and writes with tools) | Yes, at `/workspace/.memory/` |
| Limits | 1024 entries, 256-char names, 10 MB total | 100 entries, 64 KiB per entry, 5 MiB total |

The bank is excluded from hibernation archives and mounted again on every start.
Changes that you make with profile management during a dormant session take effect on
the next resume.

## Related

- [AI Skills](skills.md) — companion store for reusable instruction sets.
- [User Sessions](user-sessions.md) — interactive sessions that can read and write memory.
- [D&R-Driven Sessions](dr-sessions.md) — automated sessions that can persist findings across runs.
