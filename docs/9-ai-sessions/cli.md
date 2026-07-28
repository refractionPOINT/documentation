# Command Line Interface

The [LimaCharlie Python SDK](../6-developer-guide/sdks/python-sdk.md) supplies a `limacharlie ai` command group that covers the full AI Sessions lifecycle from the terminal. With this group you create sessions from an `ai_agent` Hive template with overrides for each run, list and inspect sessions, attach to a live session over WebSocket, and terminate a session.

These commands are available in the `cli-v2` release line of the CLI. They use the same endpoints that the [API Reference](api-reference.md) page documents. Authentication reuses your LimaCharlie credentials. You do not need a separate AI Sessions token.

!!! note
    The CLI adds to the [web app](user-sessions.md). Everything that you can do from the web app you can also do from the CLI. The one exception is file upload and download, which the CLI does not support yet.

## Installation

```bash
pip install limacharlie
```

Then authenticate. The [CLI overview](../6-developer-guide/sdk-overview.md#authentication) gives the steps.

## Two session ownership models

The AI Sessions service has two kinds of session. Each kind has its own creation command, lifecycle group, and WebSocket authentication model. The two kinds are independent. The commands for one kind do not show a session that you created in the other kind.

| | **Org-owned session** | **User-owned session** |
|---|---|---|
| Started by | `ai start-session --definition <hive-record>` (or a D&R rule) | `ai chat [PROMPT]` |
| Owner | The organization (`OwnerOID`) | The authenticated user (`OwnerUID`) |
| Anthropic credential | `anthropic_secret` from the `ai_agent` Hive record | The stored credential of the user, set up with [`ai auth claude`](#limacharlie-ai-auth-claude) |
| Lifecycle commands | [`ai session list/get/history/terminate`](#limacharlie-ai-session-list) | [`ai chats list/get/history/terminate`](#limacharlie-ai-chats) |
| `ai session attach` mode | Read-only. The org WebSocket endpoint is the only one available, so `--interactive` falls back to read-only | Owner-interactive. `--interactive` sends prompts |

Use **org sessions** for automation: scheduled runs, D&R rule triggers, and single runs of an `ai_agent` Hive record. Use **user sessions** for an interactive Claude chat in your terminal. A user session bills against your own Claude credential.

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
| `--limit` | Maximum results for each page (1 – 200, default 50). |
| `--cursor` | Pagination cursor from a previous response. |

The list view truncates the `initial_prompt` field. Use `ai session get --id <SESSION_ID> --full-prompt` to see the full prompt.

## `limacharlie ai session get`

Get the metadata of one session: status, model, token usage, cost, trigger information, and end reason.

```bash
limacharlie ai session get --id <SESSION_ID>
limacharlie ai session get --id <SESSION_ID> --full-prompt
```

## `limacharlie ai session history`

Get the full conversation log of a session: user prompts, assistant responses, tool calls, and tool results.

```bash
limacharlie ai session history --id <SESSION_ID>
limacharlie ai session history --id <SESSION_ID> --raw
```

By default, the command hides internal system startup messages, such as credential diagnostics, `claude_md_loaded`, and MCP config debug messages. [`ai session attach`](#default-noise-filter) hides the same set from the live stream. Pass `--raw` to include them.

## `limacharlie ai session terminate`

Terminate a running session. This command needs the `ai_agent.set` permission.

```bash
limacharlie ai session terminate --id <SESSION_ID>
```

## `limacharlie ai session attach`

Open a WebSocket to a running session and stream its messages live. With `--interactive`, the terminal becomes a chat. The CLI sends each stdin line to the agent as a prompt and shows approval requests as y/n prompts.

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
| `--interactive`, `-i` | Send stdin lines as prompts. Show approval messages and question messages as prompts. |
| `--read-only` | Use the org-scoped read-only WebSocket (`/v1/ws/org/sessions/{id}`). Needs `ai_agent.get` on the organization that owns the session. The client blocks send operations. |
| `--no-history` | Do not show the history block on connect. Show only new messages. |
| `--raw` | Print each WebSocket frame as a single JSON line instead of colour-coded formatting. |
| `--verbose`, `-v` | Show every frame: plumbing `system[subtype]` messages (`init_received`, `model_set`, `hook_started`, …), `session_status` pings, `usage_delta` frames, and full ISO timestamps instead of the default `HH:MM:SS`. See [Default noise filter](#default-noise-filter). |

### Endpoint selection and fallback

The AI Sessions service has two WebSocket endpoints:

- `/v1/ws/sessions/{id}` — owner-interactive. The authenticated user must own the session. The endpoint accepts write messages: prompts, approvals, and interrupts.
- `/v1/ws/org/sessions/{id}` — org-scoped, read-only. Needs `ai_agent.get` on the organization that owns the session. The endpoint accepts no write messages.

By default, the CLI connects to the owner endpoint. If the server returns 403, the CLI falls back to the org-scoped read-only endpoint and prints a notice. The server returns 403 when your organization owns the session instead of you. Every session that `ai start-session` creates is an example. Pass `--read-only` to connect directly to the org endpoint and avoid the 403 response.

!!! tip "When `--interactive` actually accepts your input"
    `ai session attach --interactive` sends prompts only when the owner endpoint accepts you. The owner endpoint accepts you for **user-owned** sessions, which you create with [`ai chat`](#limacharlie-ai-chat) or in the web app under your identity. **Org-owned** sessions come from `ai start-session` and from any run that a D&R rule triggers. For these sessions the org endpoint is the only path that the AI Sessions service exposes, and it is read-only. The CLI falls back to that endpoint and prints a notice. Use [`ai chat`](#limacharlie-ai-chat) for a terminal chat.

### Interactive controls

When `--interactive` is set:

- **Typed line + Enter** → sent as a `prompt` message.
- `/interrupt` → sends a WebSocket `interrupt` message, cancelling the agent's current turn.
- `/quit` → closes the WebSocket and exits.
- **Ctrl+C** → clean disconnect.
- **Tool approval requests** → interactive `Approve? [y/n/session]` prompt. If you choose `session`, the CLI approves matching calls automatically for the rest of the session.
- **`ask_user_question` messages** → if the question has options, you get a numbered menu. If it has no options, you get a free-text prompt.

### Output format

Notices (connection status, read-only fallback, errors) go to **stderr**. Session messages go to **stdout**. When stdout is a TTY, the CLI colour-codes messages by type:

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

By default, timestamps are short: `HH:MM:SS`. Pass `--verbose` to keep the full ISO-8601 value that the server sent.

With `--raw`, each frame is one JSON object on its own line. This format is good for post-processing:

```bash
limacharlie ai session attach --id $SID --raw \
  | jq -c 'select(.type=="tool_use") | .payload'
```

### Default noise filter

The AI Sessions runner sends many housekeeping frames at the start of every session and between tool calls. Without a filter, these frames fill the live stream. The assistant turns are then hidden between dozens of `system[credential_diagnostics]:`, `system[model_set]:`, `session_status: {...}`, and empty `assistant:` headers. The pretty renderer therefore hides these frames by default:

- **Plumbing message types** — `session_status` (startup and status pings), `usage_delta` (token counts for each API call), `sdk_session_id`.
- **Plumbing `system` subtypes** — every startup event that the bridge sends (`credential_diagnostics`, `init_received`, `claude_md_loaded`, `mcp_config_debug`, `mcp_servers_set`, `model_set`, `max_turns_set`, `max_budget_set`, `task_budget_set`, `one_shot_mode_set`, `permission_mode_set`, `tools_configured`, `system_prompt_set`, `oid_added_to_system_prompt`, `ttl_added_to_system_prompt`, `plugins_resolved`, `autoinit_loaded`, `autoinit_error`, `resuming_sdk_session`, `user_mcp_servers_loaded`, `mcp_servers_loaded`, `session_patterns_loaded`, `unknown_plugin`, `claude_md_error`, …) and the Claude SDK hook events (`hook_started`, `hook_response`, `hook_matched`).
- **Empty frames** — `assistant` turns that carry only a `tool_use` block (the `tool_use` message already shows the call), `user` frames that wrap a `tool_result` (the `tool_result` message already shows the output), and `result` pings with no human-readable summary.

The filter applies to the initial history block and to the live stream. Pass `--verbose` or `-v` to disable the filter and see every frame. `--raw` skips the renderer and prints the JSON unchanged. [`ai session history`](#limacharlie-ai-session-history) and [`ai chats history`](#limacharlie-ai-chats) use the same noise set. `--raw` on those commands includes the filtered frames.

## `limacharlie ai start-session`

Start a new AI session. The command reuses an `ai_agent` Hive record as a **template** and overrides single fields for this run.

The Hive record that `--definition` names supplies the default session configuration: prompt, model, credentials (as `hive://secret/` references), tool permissions, MCP servers, environment, budgets, and other fields. Each `--option` flag below replaces the matching field from the template. The CLI uses the other fields without change.

You can therefore use one `ai_agent` definition as a start point and change only the parts that you need for each run. You can replace the prompt, cap the budget, change the model, add an environment variable, or restrict tools. You do not need a copy of the definition for each variant.

### Override semantics

- **Scalars and lists** — replace the template value when you pass the flag. If you omit the flag, the template value stays.
- **Environment** — merges the `environment` field of the template with the `--env KEY=VALUE` flags. On a key collision, the CLI value wins.
- **MCP servers** — always come from the template. You cannot override them from the CLI.
- **`hive://secret/<name>` references** — valid in any override value, not only in the template. The CLI resolves them before it sends the request, so secrets never appear in `argv`.

### Examples

Start a session from a definition with no overrides:

```bash
limacharlie ai start-session --definition my-security-analyst
```

Reuse the template, but replace the prompt and name the session for auditing:

```bash
limacharlie ai start-session --definition my-agent \
  --prompt "Investigate this specific alert" \
  --name "Alert investigation"
```

Cap the budget and select a model on top of the template:

```bash
limacharlie ai start-session --definition my-agent \
  --model claude-sonnet-4-6 \
  --max-budget-usd 2.50
```

Add an environment variable (merged with the environment of the template):

```bash
limacharlie ai start-session --definition my-agent \
  --env SLACK_WEBHOOK=hive://secret/slack-webhook
```

Restrict tools and set `one_shot` to off for this run only:

```bash
limacharlie ai start-session --definition my-agent \
  --allowed-tools Read,Grep --denied-tools Bash,Write --no-one-shot
```

Pipe the result into `jq` to get the new session ID, then attach to the session. The attach is read-only, because these are org-owned sessions. For an interactive terminal chat, use [`ai chat`](#limacharlie-ai-chat):

```bash
SID=$(limacharlie ai start-session --definition my-agent \
        --output json | jq -r '.session_id')
limacharlie ai session attach --id "$SID"
```

### Flags

#### Session metadata

| Flag | Description |
|---|---|
| `--definition` | **Required.** Name of the `ai_agent` Hive record to use as template. |
| `--prompt` | Replace the prompt from the definition. |
| `--name` | Replace the session name. |
| `--idempotent-key` | Deduplication key. If an active session for this key exists, the command returns that session and creates no new one. |
| `--data` | JSON dictionary that the CLI adds to the prompt as YAML event data. Use it for standalone runs that have no D&R event. |

**Profile fields** — scalars and lists replace the template value when you give them:

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

**Environment** — merged with the environment of the template (the override wins on a key collision):

| Flag | Description |
|---|---|
| `--env KEY=VALUE` (repeatable) | Environment variable for the session. `VALUE` can be a literal or `hive://secret/<name>`. |

**Credentials** — replace the related `*_secret` field on the template:

| Flag | Description |
|---|---|
| `--anthropic-key` | Literal Anthropic API key or `hive://secret/<name>`. |
| `--lc-api-key` | Literal LimaCharlie API key or `hive://secret/<name>`. |
| `--lc-uid` | Literal User ID or `hive://secret/<name>`. |

### Output

The command prints the session-creation response from the server. With `--output json`:

```json
{
  "session_id": "abc-123",
  "status": "starting",
  "created_at": "2026-04-17T18:05:02Z"
}
```

Use the returned `session_id` with `ai session attach`, `ai session get`, or `ai session terminate`.

## `limacharlie ai auth claude`

Manage the Anthropic credential of each user that [`ai chat`](#limacharlie-ai-chat) uses. Org-owned sessions that start with `ai start-session` ignore this credential. They use the `anthropic_secret` field from the `ai_agent` Hive record. You do not need to run `auth claude` for those sessions.

The credential is stored on the server and is bound to the authenticated UID. The credential is a Claude Max OAuth token (browser flow) or a raw Anthropic API key.

```bash
limacharlie ai auth claude status
limacharlie ai auth claude login
limacharlie ai auth claude set-key --key "$ANTHROPIC_API_KEY"
limacharlie ai auth claude set-key --key hive://secret/anthropic-key
echo "$ANTHROPIC_API_KEY" | limacharlie ai auth claude set-key --key-from-stdin
limacharlie ai auth claude logout
```

### Subcommands

| Command | Description |
|---|---|
| `status` | Returns `has_credentials`, `credential_type` (`oauth_token` or `apikey`), and `created_at`. |
| `login` | Runs the browser OAuth flow. It starts an OAuth session on the server, polls until Claude returns the URL, prints the URL to the terminal, and asks for the authorization code. |
| `set-key` | Stores a raw Anthropic API key. Accepts `--key <VALUE>` (literal or `hive://secret/<name>`) or `--key-from-stdin` for piped input. The two flags are mutually exclusive. |
| `logout` | Deletes the stored credential. |

Errors:

- *"No Claude credentials registered for this user"* — `ai chat` gives this error when `status.has_credentials` is `false`. Run `auth claude login` or `auth claude set-key`, then try again.
- The browser OAuth flow has a TTL of 5 minutes on the server. If you need more time to paste the code back, start again with `auth claude login`.

## `limacharlie ai chat`

Start a new **user-owned** AI session and open an interactive WebSocket chat. The authenticated user owns the session. The session bills against the credential that [`ai auth claude`](#limacharlie-ai-auth-claude) stores. It attaches over the owner endpoint, so prompts move in both directions.

The opening prompt comes from the optional `PROMPT` argument. Later turns come from interactive stdin after the session attaches. The command does **not** read stdin for the opening prompt. Give the opening prompt in the argument, so that piped multi-line input does not become one message.

```bash
# Start a chat with an opening prompt.
limacharlie ai chat "What sensors pinged in the last hour?"

# Start a chat with overrides — caps and a specific model.
limacharlie ai chat --model claude-sonnet-4-6 --max-budget-usd 0.50

# Start a chat with no opening prompt; first message comes from stdin in the
# interactive loop that runs after attach.
limacharlie ai chat
```

`ai chat` does three steps before it gives the terminal to the chat loop:

1. Calls [`ai auth claude status`](#limacharlie-ai-auth-claude). If no credential is stored, the command exits with a non-zero code and shows instructions.
2. Calls `POST /v1/register`. This call is idempotent and is safe to run every time.
3. Calls `POST /v1/sessions` with the override flags below, then attaches with [`ai session attach`](#limacharlie-ai-session-attach) in interactive mode.

### Flags

| Flag | Description |
|---|---|
| *(positional)* `PROMPT` | Optional opening prompt sent as the first message after attach. |
| `--name` | Session name (display only). |
| `--model` | Anthropic model (for example, `claude-sonnet-4-6`). |
| `--max-turns` | Maximum agent turns before auto-stop. |
| `--max-budget-usd` | Hard USD cost cap for the session. |
| `--task-budget-tokens` | Token budget for each task. |
| `--permission-mode` | `acceptEdits`, `plan`, or `bypassPermissions`. |
| `--allowed-tools` | Comma-separated list of allowed tool names. |
| `--denied-tools` | Comma-separated list of denied tool names. |
| `--plugin` (repeatable) | Plugin names to enable. |
| `--idempotent-key` | Deduplication key for session creation. |
| `--verbose`, `-v` | Disable the [default noise filter](#default-noise-filter) and use full ISO timestamps — same flag as on `ai session attach`. |

The flag set is smaller than the flag set of [`ai start-session`](#limacharlie-ai-start-session). There is no `--definition`, because chat sessions are blank and do not come from a template. There is no environment merge. There are no flags to override credentials (`--anthropic-key`, `--lc-api-key`, `--lc-uid`), because the session uses the per-user credential from `auth claude` and runs without an attached LC service identity.

### Interactive controls

The controls are the same as for [`ai session attach --interactive`](#interactive-controls). Stdin lines become prompts, `/interrupt` cancels the agent's current turn, `/quit` detaches, and Ctrl+C disconnects. The CLI shows tool approval requests and `ask_user_question` messages as in-line prompts.

### Re-attaching to an in-progress chat

`ai chat` always creates a new session. To reconnect to a session that you started, use [`ai session attach --interactive --id <SESSION_ID>`](#limacharlie-ai-session-attach). It works on user-owned sessions in the same way as the attach loop inside `ai chat`, because you own them and the owner endpoint accepts you.

## `limacharlie ai chats`

Manage the lifecycle of user-owned sessions. This group is the counterpart of the [`ai session`](#limacharlie-ai-session-list) group. It has the same subcommands (`list`, `get`, `history`, `terminate`), but it uses the user-scoped REST endpoints (`/v1/sessions/*`) instead of the org-scoped endpoints (`/v1/org/sessions/*`).

```bash
limacharlie ai chats list
limacharlie ai chats list --status running
limacharlie ai chats get --id <SESSION_ID>
limacharlie ai chats get --id <SESSION_ID> --full-prompt
limacharlie ai chats history --id <SESSION_ID>
limacharlie ai chats history --id <SESSION_ID> --raw
limacharlie ai chats terminate --id <SESSION_ID>
```

| Subcommand | Org equivalent | Notes |
|---|---|---|
| `chats list` | `session list` | Lists the sessions where you are the owning UID. Same `--status`, `--limit`, and `--cursor` flags. |
| `chats get` | `session get` | Same `--full-prompt` toggle. |
| `chats history` | `session history` | Same filter for internal system messages. Same `--raw` to disable it. |
| `chats terminate` | `session terminate` | Calls `DELETE /v1/sessions/{id}` (user-scoped). |

The sessions that you create with `ai chat` appear in `chats list`. The sessions that you create with `ai start-session`, and the sessions that D&R rules trigger, appear in `session list`. The two sets do not overlap. `chats get --id <org-session-id>` returns "not found" instead of the org session, and `session get` with a user-owned session ID does the same.

## Related pages

- [User Sessions](user-sessions.md) — concepts, session states, profiles, and the web app.
- [D&R-Driven Sessions](dr-sessions.md) — how Detection & Response rules trigger the same `ai_agent` records automatically.
- [Tool Permissions & Profiles](tool-permissions.md) — reference for `--allowed-tools`, `--denied-tools`, and `--permission-mode`.
- [API Reference](api-reference.md) — the REST and WebSocket endpoints that the CLI wraps.
