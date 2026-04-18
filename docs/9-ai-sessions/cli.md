# Command Line Interface

The [LimaCharlie Python SDK](../6-developer-guide/sdks/python-sdk.md) ships a `limacharlie ai` command group that covers the full AI Sessions lifecycle from the terminal: creating sessions from an `ai_agent` Hive template with per-run overrides, listing and inspecting sessions, attaching to a live session over WebSocket, and terminating.

These commands are available in the `cli-v2` release line of the CLI and talk to the same endpoints documented on the [API Reference](api-reference.md) page. Authentication reuses your existing LimaCharlie credentials — no separate AI Sessions token is required.

!!! note
    The CLI is complementary to the [web console](user-sessions.md) and the [TypeScript SDK](sdk.md). Anything you can do from the console (other than file upload/download, which is not yet wired into the CLI) you can do from the CLI.

## Installation

```bash
pip install limacharlie
```

Then authenticate as described in the [CLI overview](../6-developer-guide/sdk-overview.md#authentication).

## `limacharlie ai session list`

List AI sessions for the current organization.

```bash
limacharlie ai session list
limacharlie ai session list --status running
limacharlie ai session list --status ended --limit 10
```

Options:

| Flag | Description |
|---|---|
| `--status` | Filter by status: `running`, `starting`, `ended`. |
| `--limit` | Maximum results per page (1 – 200, default 50). |
| `--cursor` | Pagination cursor from a previous response. |

The `initial_prompt` field is truncated in the list view. Use `ai session get --id <SESSION_ID> --full-prompt` to see the full prompt.

## `limacharlie ai session get`

Fetch a single session's metadata (status, model, token usage, cost, trigger info, end reason).

```bash
limacharlie ai session get --id <SESSION_ID>
limacharlie ai session get --id <SESSION_ID> --full-prompt
```

## `limacharlie ai session history`

Retrieve the full conversation log of a session (user prompts, assistant responses, tool calls, tool results).

```bash
limacharlie ai session history --id <SESSION_ID>
limacharlie ai session history --id <SESSION_ID> --raw
```

Internal system bootstrap messages (credential diagnostics, `claude_md_loaded`, MCP config debug, etc.) are filtered out by default. Pass `--raw` to include them.

## `limacharlie ai session terminate`

Terminate a running session. Requires the `ai_agent.set` permission.

```bash
limacharlie ai session terminate --id <SESSION_ID>
```

## `limacharlie ai session attach`

Open a WebSocket to a running session and stream its messages live. With `--interactive` the terminal becomes a chat: stdin lines are sent to the agent as prompts and approval requests are surfaced as y/n prompts.

```bash
# Tail a running session (pretty output).
limacharlie ai session attach --id <SESSION_ID>

# Interactive chat with the agent.
limacharlie ai session attach --id <SESSION_ID> --interactive

# Read-only view of an org session you did not start.
limacharlie ai session attach --id <SESSION_ID> --read-only

# Raw JSON frames, one per line — pipe-friendly.
limacharlie ai session attach --id <SESSION_ID> --raw | jq .
```

### Flags

| Flag | Description |
|---|---|
| `--id` | **Required.** Session ID to attach to. |
| `--interactive`, `-i` | Send stdin lines as prompts; surface approval/question messages interactively. |
| `--read-only` | Use the org-scoped read-only WebSocket (`/v1/org/sessions/{id}/ws`). Requires `ai_agent.get` on the session's owning org. Send operations are blocked client-side. |
| `--no-history` | Don't render the history block on connect; just show new messages. |
| `--raw` | Print each WebSocket frame as a single JSON line instead of colour-coded formatting. |

### Endpoint selection and fallback

Two WebSocket endpoints exist on the AI Sessions service:

- `/v1/sessions/{id}/ws` — owner-interactive. The authenticated user must own the session; write messages (prompts, approvals, interrupts) are accepted.
- `/v1/org/sessions/{id}/ws` — org-scoped, read-only. Requires `ai_agent.get` on the session's owning org. No write messages accepted.

By default the CLI connects to the owner endpoint. If the server returns 403 (the session belongs to another user), the CLI transparently falls back to the org-scoped read-only endpoint and prints a notice. Pass `--read-only` to connect directly to the org endpoint and skip the 403 round trip.

### Interactive controls

When `--interactive` is set:

- **Typed line + Enter** → sent as a `prompt` message.
- `/interrupt` → sends a WebSocket `interrupt` message, cancelling the agent's current turn.
- `/quit` → closes the WebSocket and exits.
- **Ctrl+C** → clean disconnect.
- **Tool approval requests** → interactive `Approve? [y/n/session]` prompt. Choosing `session` auto-approves matching invocations for the rest of the session.
- **`ask_user_question` messages** → if the question has options, you get a numbered menu; otherwise a free-text prompt.

### Output format

Notices (connection status, read-only fallback, errors) go to **stderr**; session messages go to **stdout**. When stdout is a TTY, messages are colour-coded by type:

| Type | Colour | Form |
|---|---|---|
| `user` | green bold | `user:` + indented text |
| `assistant` | cyan bold | `assistant:` + indented text |
| `tool_use` | yellow | `tool_use NAME (id): {input}` |
| `tool_result` | dim yellow | `tool_result (id):` + content (truncated at 4 KB) |
| `system` | dim | `system[subtype]: ...` |
| `result` | blue | `result: <summary>` |
| `error` | red bold (stderr) | `error [code]: message` |
| `session_end` | red bold | `session ended: <reason>` — stream then exits |
| `tool_approval_request` (non-interactive) | yellow bold | `approval requested for NAME: {input}` |
| `ask_user_question` (non-interactive) | magenta bold | `question: <text>` |

With `--raw` each frame is a single JSON object per line, making it easy to post-process:

```bash
limacharlie ai session attach --id $SID --raw \
  | jq -c 'select(.type=="tool_use") | .payload'
```

## `limacharlie ai start-session`

Start a new AI session by reusing an `ai_agent` Hive record as a **template** and overriding individual fields for this run.

The Hive record named by `--definition` supplies the default session configuration: prompt, model, credentials (as `hive://secret/` references), tool permissions, MCP servers, environment, budgets, and so on. Any `--option` flag listed below replaces the matching field from the template; everything else is used as-is.

This lets you reuse one `ai_agent` definition as a starting point and vary only the parts you need per-run — swap the prompt, cap the budget, change the model, add an environment variable, restrict tools — without maintaining a copy of the definition per variant.

### Override semantics

- **Scalars and lists** — replace the template value when the flag is passed. Omitted flags leave the template intact.
- **Environment** — merges the template's `environment` with `--env KEY=VALUE` flags. On key collision the CLI value wins.
- **MCP servers** — always come from the template (not overridable from the CLI).
- **`hive://secret/<name>` references** — valid in any override value, not just in the template. They are resolved before the request is sent, so secrets never appear in `argv`.

### Examples

Start a session from a definition with no overrides:

```bash
limacharlie ai start-session --definition my-security-analyst
```

Reuse the template but swap the prompt and tag the session for auditing:

```bash
limacharlie ai start-session --definition my-agent \
  --prompt "Investigate this specific alert" \
  --name "Alert investigation"
```

Cap budget and pick a specific model on top of the template:

```bash
limacharlie ai start-session --definition my-agent \
  --model claude-sonnet-4-6 \
  --max-budget-usd 2.50
```

Add an env var (merged with the template's environment):

```bash
limacharlie ai start-session --definition my-agent \
  --env SLACK_WEBHOOK=hive://secret/slack-webhook
```

Restrict tools and force `one_shot` off for this run only:

```bash
limacharlie ai start-session --definition my-agent \
  --allowed-tools Read,Grep --denied-tools Bash,Write --no-one-shot
```

Pipe the result into `jq` to grab the new session ID and attach to it:

```bash
SID=$(limacharlie ai start-session --definition my-agent \
        --output json | jq -r '.session_id')
limacharlie ai session attach --id "$SID" --interactive
```

### Flags

**Session metadata**

| Flag | Description |
|---|---|
| `--definition` | **Required.** Name of the `ai_agent` Hive record to use as template. |
| `--prompt` | Replace the prompt from the definition. |
| `--name` | Replace the session name. |
| `--idempotent-key` | Deduplication key — if an active session for this key exists, it is returned instead of creating a new one. |
| `--data` | JSON dictionary appended to the prompt as YAML event data (for standalone runs that have no D&R event). |

**Profile fields** — scalars and lists replace the template value when provided:

| Flag | Maps to `ProfileContent` field |
|---|---|
| `--model` | `model` |
| `--max-turns` | `max_turns` |
| `--max-budget-usd` | `max_budget_usd` |
| `--task-budget-tokens` | `task_budget_tokens` |
| `--ttl-seconds` | `ttl_seconds` |
| `--one-shot` / `--no-one-shot` | `one_shot` |
| `--permission-mode` | `permission_mode` (`acceptEdits`, `plan`, `bypassPermissions`) |
| `--allowed-tools` | `allowed_tools` (comma-separated) |
| `--denied-tools` | `denied_tools` (comma-separated) |
| `--plugin` (repeatable) | `plugins` |

**Environment** — merged with the template's environment (override wins on key collisions):

| Flag | Description |
|---|---|
| `--env KEY=VALUE` (repeatable) | Environment variable for the session. `VALUE` may be a literal or `hive://secret/<name>`. |

**Credentials** — replace the corresponding `*_secret` field on the template:

| Flag | Description |
|---|---|
| `--anthropic-key` | Literal Anthropic API key or `hive://secret/<name>`. |
| `--lc-api-key` | Literal LimaCharlie API key or `hive://secret/<name>`. |
| `--lc-uid` | Literal User ID or `hive://secret/<name>`. |

### Output

The command prints the server's session-creation response. With `--output json`:

```json
{
  "session_id": "abc-123",
  "status": "starting",
  "created_at": "2026-04-17T18:05:02Z"
}
```

Use the returned `session_id` with `ai session attach`, `ai session get`, or `ai session terminate`.

## Related pages

- [User Sessions](user-sessions.md) — concepts, session states, profiles, the web UI.
- [D&R-Driven Sessions](dr-sessions.md) — triggering the same `ai_agent` records automatically from Detection & Response rules.
- [API Reference](api-reference.md) — the REST and WebSocket endpoints the CLI wraps.
