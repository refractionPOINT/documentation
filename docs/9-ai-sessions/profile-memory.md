title: Profile Memory Bank · LimaCharlie AI Sessions

# Profile Memory Bank

User-scoped AI Sessions are not associated with any specific organisation, so they cannot use the org-scoped [`ai_memory` Hive](memory.md). To give Claude durable context across user sessions, each [Session Profile](user-sessions.md#session-profiles) carries a **memory bank**: a small set of markdown files mounted into the runner's workspace at `/workspace/.memory/` whenever a session is launched from that profile.

The memory bank is the user-side analog of `ai_memory`, scoped per profile rather than per org. Use it for things like:

- preferences ("always run terraform plans against `staging` first"),
- recurring projects (a running plan, status notes, decision logs),
- learned facts about your environment (host inventories, compliance constraints, runbook pointers).

Each profile gets its own bank, so you can keep an "investigations" profile, a "reporting" profile, and a "research" profile with independent memories.

## How memories are mounted

When a session starts from a profile that has memories:

1. The session manager loads the bank, decrypts it, and ships it inside the encrypted session config.
2. The runner writes each memory to `/workspace/.memory/<path>` before Claude starts.
3. While the session runs, the runner watches `/workspace/.memory/`. Whenever Claude writes, edits, or deletes a file there, the change is debounced and synced back to the bank — so anything the model "learns" persists for the next session that uses this profile.

The directory belongs entirely to the bank: do not store transient files in `.memory/`, they will be wiped on the next session start.

## Layout and limits

Memory paths use the same shape as the `ai_memory` Hive:

- relative path, forward slashes only,
- characters limited to `A–Z`, `a–z`, `0–9`, `.`, `_`, `-`, `/`,
- no leading-dot segments (so `.swp`/`~`/`.#…` editor temp files are easy to filter out),
- no `..` traversal,
- maximum depth: 5 segments,
- maximum path length: 256 characters.

Per-profile caps:

| Limit | Value |
|---|---|
| Entries per profile | 100 |
| Bytes per entry | 64 KiB |
| Aggregate bytes per profile | 5 MiB |

Bank entries are stored encrypted at rest using your user-specific key — the same scheme that protects environment variables and MCP server credentials in your profiles.

## Lifecycle

- The memory bank is **decoupled from session lifecycle**. Deleting a session has no effect on its profile's bank.
- The bank is **not part of session suspend archives**. When a session resumes, it remounts the *current* bank — so any edits you make through the API while a session was dormant take effect on resume.
- **Deleting a profile cascades** the deletion to every entry in its bank.

## Managing memories

### REST API

Authenticate with your LimaCharlie JWT (`Authorization: Bearer $LC_JWT`).

#### List entries

Returns metadata only — fetch bodies separately.

```bash
curl https://ai-sessions.limacharlie.io/v1/profiles/$PROFILE_ID/memories \
  -H "Authorization: Bearer $LC_JWT"
```

```json
{
  "memories": [
    {
      "path": "preferences.md",
      "size": 412,
      "content_hash": "9b2f…",
      "created_at": "2026-05-01T10:14:32Z",
      "updated_at": "2026-05-04T08:02:11Z"
    }
  ]
}
```

#### Read an entry

```bash
curl --get https://ai-sessions.limacharlie.io/v1/profiles/$PROFILE_ID/memories/content \
  --data-urlencode "path=projects/acme.md" \
  -H "Authorization: Bearer $LC_JWT"
```

#### Create or update an entry

The body is JSON; the markdown content goes inside the `content` field.

```bash
curl -X PUT https://ai-sessions.limacharlie.io/v1/profiles/$PROFILE_ID/memories/content \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  --data-urlencode "path=projects/acme.md" \
  -d '{"content": "## Acme Corp\n- single-tenant deployment\n- compliance: SOC2"}'
```

The response includes a `created` flag (true on first insert) and a `changed` flag (false when the supplied content matched the existing entry — in that case the call is a no-op).

#### Delete an entry

```bash
curl -X DELETE --get https://ai-sessions.limacharlie.io/v1/profiles/$PROFILE_ID/memories/content \
  --data-urlencode "path=projects/old-deal.md" \
  -H "Authorization: Bearer $LC_JWT"
```

### From inside a session

Claude can simply write to `/workspace/.memory/<path>.md` (or read from it) the same way it would any other file. Edits are synced back to the bank automatically — no special API call required from the model.

## Profile memory vs. AI Memory hive

Both stores share a "filesystem-style entry within an owner record" model, but they sit at different scopes:

|   | Profile memory bank | [AI Memory Hive](memory.md) |
|---|---|---|
| Scope | One bank per profile (per-user) | One record per agent (per-org) |
| Auth | LC user JWT | LC org/user creds with `ai_memory.{get,set,del}` |
| Mounted into runner | Yes, at `/workspace/.memory/` | No — accessed via `limacharlie ai-memory` CLI |
| Best for | Per-user durable context for interactive sessions | Cross-session agent state for D&R-driven sessions |

If your session has both an LC org binding *and* a profile memory bank, you can use them together: the bank for personal preferences and project notes, the hive for org-scoped operational state.

## Security

- The runner is treated as untrusted code. It cannot make privileged API calls to the session manager.
- Memory writes from inside the runner travel over the same authenticated WebSocket the runner uses to talk to the proxy. The proxy validates path/size limits at the trust boundary and forwards to the session manager, which authoritatively re-derives the (user, profile) target from the persisted session record. A compromised runner cannot redirect writes into another user's profile.
- Bodies are encrypted at rest with your user-specific key.
