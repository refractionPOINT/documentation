# Tool Permissions & Profiles

Every AI Session runs a Claude Agent SDK process inside a managed sandbox. Three fields control what that agent can do: which built-in Claude Code tools it can call, which shell commands it can run, and which MCP servers it can reach. These fields appear in both **user Profiles** and **`ai_agent` Hive records**:

- `allowed_tools`
- `denied_tools`
- `permission_mode`

These three settings map to the matching options on `ClaudeAgentOptions` in the Claude Agent SDK. The matching behaviour is the behaviour in the upstream [Claude Code permissions reference](https://code.claude.com/docs/en/permissions). This page explains how LimaCharlie shows these fields, the full grammar for tool names, and how the bridge evaluates patterns at the time of a tool call.

## Where these fields live

The same three fields appear in every place where you configure an AI Session:

| Location | Who owns it | Used by |
|---|---|---|
| **User Profile** (`POST /v1/profiles`) | The authenticated LimaCharlie user | [User Sessions](user-sessions.md) that you create in the web app or with `ai chat` in the [CLI](cli.md). |
| **`ai_agent` Hive record** | The organization | [D&R-driven sessions](dr-sessions.md) and CLI `ai start-session --definition <name>` runs. |
| **Inline `profile:` block** in a D&R `start ai agent` action | The organization | One-off overrides inside a specific D&R rule. |
| **Per-session `allowed_tools` / `denied_tools`** in `POST /v1/sessions` | The authenticated user | Per-session override on top of the chosen Profile. |

The field names and behaviour are the same on all four surfaces. A `denied_tools: [Write]` rule has the same meaning in the default Profile of a user and in an `ai_agent` record that a detection triggers.

## Tool-name grammar

Entries in `allowed_tools` and `denied_tools` are **tool-name patterns**, not free-form strings. The matcher recognises three shapes.

### 1. Bare built-in tool name

A bare identifier matches the entire Claude Code tool of that name. Common built-ins are:

| Name | What it does |
|---|---|
| `Read` | Read a file from the session workspace. |
| `Write` | Create or overwrite a file. |
| `Edit` | Apply a targeted edit to an existing file. |
| `Bash` | Run a shell command. |
| `Grep` | Search file contents. |
| `Glob` | Match files by pattern. |
| `WebFetch` | Fetch an HTTP(S) URL. |
| `WebSearch` | Run a web search. |
| `TodoWrite` | Update the in-session task list. |
| `Task` | Spawn a subagent. |
| `AskUserQuestion` | Ask the human-in-the-loop a structured question. In interactive sessions, the attached client shows the question (the browser chat or `ai session attach --interactive`). In `one_shot` or unattended sessions, these questions time out after five minutes. |

!!! note
    The Claude Code CLI publishes the authoritative list of built-in tools. LimaCharlie does not add tools to that set or remove tools from it. Bare names are case-sensitive.

### 2. Scoped Bash pattern — `Bash(prefix:*)`

The `Bash` tool accepts a scoping specifier that limits which commands the pattern covers. Only the `prefix:*` form is recognised. It mirrors the official Claude Code CLI syntax:

```text
Bash(git:*)            # any command starting with "git "
Bash(npm install:*)    # any command starting with "npm install "
Bash(kubectl get:*)    # read-only kubectl verbs
```

**Common pre-processing.** The hardened matcher of LimaCharlie evaluates every pattern in `allowed_tools` and in `denied_tools`, not the upstream Claude Code literal-prefix matcher. Before any match, the bridge normalises every Bash command in the same way:

- The bridge splits the command on shell stage operators (`|`, `||`, `&`, `&&`, `;`, `|&`) and on real newlines.
- The bridge strips process wrappers (`timeout`, `time`, `nice`, `nohup`, `stdbuf`, bare `xargs`) and leading `VAR=value` env assignments from the front of each stage. It repeats this step, so `nohup timeout 30 DEBUG=1 npm test` becomes `npm test` before the match.
- Redirection operators (`>`, `>>`, `<`, `>&`, `&>`, fd-duplications) stay attached to their command — they are **not** stage separators.
- The match is a literal prefix on the stripped stage: the stage equals the prefix exactly, or it starts with `prefix + " "`. There is no allowlist for flag values and no resolution of aliases.

**Allow semantics.** An `allowed_tools` match fires only when an allow pattern covers **every** pipeline stage. `Bash(git:*)` alone does **not** approve `git status && rm -rf /`. No pattern covers the `rm -rf /` stage, so the command falls through to `permission_mode`.

**Deny semantics.** A `denied_tools` match fires when **any** pipeline stage matches **any** deny pattern, and one matching stage blocks the whole call. `Bash(rm:*)` in `denied_tools` catches both `rm -rf /` and the mixed-case `ls && rm -rf /`. Deny is the mirror of allow, so you cannot play the two sides against each other with spliced wrappers and compound operators.

**Dangerous constructs fall through to `permission_mode`.** Command substitution, process substitution, backticks, and subshell or brace grouping (`` ` ``, `$(...)`, `<(...)`, `>(...)`, `(...)`, `{...}`) can hide commands from both sides of the matcher. On a stage that contains one of them, neither allow nor deny fires automatically. The call takes the `permission_mode` fallback path, which is a new prompt in interactive sessions. For example, `Bash(cat:*)` does **not** auto-approve `cat $(rm -rf /)`, and `Bash(rm:*)` does **not** auto-deny it; the call prompts.

**Bare tool name.** A bare `Bash` entry, with no `(prefix:*)` specifier, means every Bash invocation. In `allowed_tools`, it auto-approves all shell commands. In `denied_tools`, it blocks all of them. Every other tool name works the same way: a bare `Read` or `WebFetch` matches every invocation of that tool.

**Deny wins.** When a call matches both lists, the bridge checks deny first and blocks the call.

**Shared with session-scoped approvals.** The `session` answer in the interactive approval prompt adds patterns to the same allow-pattern set, so all the rules above apply to those runtime rules too. Autonomous org-owned sessions and interactive user sessions use one matcher implementation.

### 3. MCP tool pattern

Claude sees MCP server tools under a mangled name in the form `mcp__<server_name>__<tool_name>`. You can allow or deny them with the full name or with a scoped pattern.

```yaml
# Allow every tool exposed by the VirusTotal MCP server
allowed_tools:
  - mcp__virustotal

# Deny one specific tool from the VirusTotal MCP server
denied_tools:
  - mcp__virustotal__upload_file
```

The `<server_name>` segment is the name that the MCP server registers at the start of the session. It is the same identifier that is the key in the `mcp_servers` map of the Profile or the `ai_agent` record. Use that exact name in your pattern.

## `allowed_tools` vs `denied_tools`

At the start of a session, the bridge loads both lists into its own pattern sets, and the same hardened matcher above evaluates them. For every tool call:

1. **Deny check first.** If any `denied_tools` pattern matches under the deny semantics, the bridge blocks the call and Claude receives a deny result. Deny always wins.
2. **Allow check second.** If an `allowed_tools` pattern fully covers the call under the allow semantics, the bridge auto-approves it with no prompt.
3. **Fallback on no match.** If neither list matches, `permission_mode` decides what happens: `acceptEdits` auto-approves file-edit tools and prompts the user for every other tool, `plan` keeps the session read-only, and `bypassPermissions` auto-approves the call.
4. **Both lists empty.** Nothing is pre-authorised and nothing is pre-blocked; every tool call falls through to `permission_mode`.

> Use this model: `allowed_tools` is the positive intent ("the agent can do these things without a question"), and `denied_tools` is the backstop ("never let the agent do this, even when a wider allow rule covers it"). For unattended D&R-driven agents, a narrow `allowed_tools` and `permission_mode: bypassPermissions` replace the interactive approval flow.

## `permission_mode`

`permission_mode` controls what happens **when a tool call is not auto-approved by the lists above**. Three values are valid:

| Value | Behaviour |
|---|---|
| `acceptEdits` (default) | File-editing tools (`Write`, `Edit`, `NotebookEdit`, `MultiEdit`) are auto-approved; every other tool call triggers an approval prompt. Best for human-in-the-loop user sessions. |
| `plan` | Claude stays in plan-only mode: it can read and reason, but it cannot run a tool that changes data without explicit approval. Use it for review and preview flows. |
| `bypassPermissions` | All tool calls are auto-approved, but `denied_tools` still applies. Unattended D&R-driven agents need this value. Without it, a tool call with no user to answer the prompt times out after 5 minutes and the session fails. |

When you omit the field, the runner sets `permission_mode` to `acceptEdits`. For D&R agents that must run tools without a human, set `permission_mode: bypassPermissions` in the `ai_agent` record or in the inline profile.

## Session-scoped approvals (interactive sessions)

In user sessions with the approval prompt, the operator can answer `session` instead of `y` or `n`. That answer stores a **session-scoped pattern** from the tool call — a `Bash(<prefix>:*)` for shell commands, or the plain tool name for other tools. The session then auto-approves later calls that match, with no more questions.

Session-scoped patterns and the `allowed_tools` from the Profile use one pattern store, so they use the same hardened matcher and all its guarantees. These patterns are ephemeral: they disappear at the end of the session, and nothing copies them into the Profile automatically. To keep the configuration of a session, snapshot it with `POST /v1/sessions/{sessionId}/capture-profile` (see the [capture-profile endpoint](api-reference.md#profiles)).

## Defaults shipped to new users

When a user registers for AI Sessions the first time, LimaCharlie provisions two profiles automatically:

- **Default** — a read-only safe baseline. `permission_mode: acceptEdits`, no `denied_tools`, and `allowed_tools` limited to:

    ```text
    Read
    Bash(cat:*) Bash(head:*) Bash(tail:*) Bash(less:*)
    Bash(grep:*) Bash(sed:*) Bash(awk:*) Bash(jq:*)
    Bash(ls:*)  Bash(find:*) Bash(wc:*)
    ```

- **Full Permissions** — `permission_mode: bypassPermissions`, both lists empty. Claude can use any tool with no prompt. Use this profile only when you accept that level of access.

The Default profile has `is_default: true`, and the web app uses it until the user selects another one. You cannot delete the Default profile. You can edit it, make another profile the default, or create more profiles up to the limit of 10 for each user.

## Examples

### Read-only investigation profile

This profile is a good baseline for interactive triage. Claude can read workspace files and run common read-only shell utilities. It never writes or edits files, and every tool that is not a read tool still needs an approval prompt.

```json
{
  "name": "Investigation (read-only)",
  "permission_mode": "acceptEdits",
  "allowed_tools": [
    "Read", "Grep", "Glob",
    "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)",
    "Bash(grep:*)", "Bash(jq:*)", "Bash(ls:*)", "Bash(find:*)"
  ],
  "denied_tools": ["Write", "Edit", "NotebookEdit"]
}
```

### Unattended D&R triage agent

This `ai_agent` Hive record runs without a human. `bypassPermissions` stops tool calls from waiting for approval. `allowed_tools` is empty, but `denied_tools` still stops the agent from writing files or from reaching arbitrary URLs.

```yaml
ai_agent:
  triage-agent:
    data:
      prompt: |
        Investigate the triggering detection and produce a structured report.
      anthropic_secret: hive://secret/anthropic-key
      lc_api_key_secret: hive://secret/lc-api-key
      permission_mode: bypassPermissions
      one_shot: true
      denied_tools:
        - Write
        - Edit
        - WebFetch
```

### Scoping MCP tools to a single server

The agent can call the VirusTotal MCP server for enrichment and no other server. The patterns also block the one tool that submits local files to the service. Every other MCP server that the session inherits keeps the normal approval flow, or is denied under `permission_mode: plan`.

```yaml
allowed_tools:
  - mcp__virustotal
denied_tools:
  - mcp__virustotal__upload_file
```

### Blocking destructive Bash verbs

Deny a specific prefix even when the rest of Bash is open. The deny matcher strips wrappers and splits pipelines in the same way as the allow matcher, so one pattern catches both bare and compound forms.

```yaml
allowed_tools: ["Bash"]
denied_tools:
  - "Bash(rm:*)"
  - "Bash(mv:*)"
  - "Bash(kubectl delete:*)"
```

- `rm -rf /` → blocked by `Bash(rm:*)`.
- `ls && rm -rf /` → blocked too: the `rm -rf /` stage matches `Bash(rm:*)`, and deny fires on any matching stage.
- `timeout 30 kubectl delete pod xyz` → blocked: the bridge strips the `timeout 30` wrapper before the match.
- `cat $(rm file)` → no auto-deny, and no auto-approve either; the dangerous construct sends the call back through `permission_mode` (a new prompt in interactive sessions).

## Where to go next

- [User Sessions](user-sessions.md#session-profiles) — how to create and manage Profiles with the API and the web app.
- [D&R-Driven Sessions](dr-sessions.md#session-profiles) — how to attach these fields to an `ai_agent` Hive record or to an inline `profile:` block on a `start ai agent` action.
- [Command Line Interface](cli.md#limacharlie-ai-start-session) — per-run overrides for `--allowed-tools`, `--denied-tools`, and `--permission-mode` when you start a session from a Hive template.
- [API Reference](api-reference.md#profiles) — the REST shape of the Profile resource.
- [Claude Code permissions (upstream)](https://code.claude.com/docs/en/permissions) — the source of truth for the pattern grammar.
