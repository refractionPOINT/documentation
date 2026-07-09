# Using the CLI with other Frontier Models

LimaCharlie's deepest AI integration is with Claude — [AI Sessions](../9-ai-sessions/index.md) in the browser and the [Claude Code plugin](mcp-server.md#option-1-claude-code-plugin-recommended) in the terminal. But the platform itself is API-first and model-agnostic: any agent that can run shell commands can operate it through the [`limacharlie` CLI](cli.md), whatever frontier model it runs on.

The CLI is the recommended integration for agents that aren't Claude Code (and Claude Code itself uses it under the hood). Two things make it work especially well:

- Every command supports `--ai-help` — help text written specifically for LLM consumption, so an agent can teach itself the platform as it goes
- It is scriptable: cron jobs, CI checks, and bulk operations work the same way for an agent as for a human

```bash
pip install limacharlie
limacharlie auth login --oid YOUR_ORG_ID --api-key YOUR_API_KEY
limacharlie auth whoami        # verify
```

The [MCP server](mcp-server.md) can be added alongside the CLI when you want structured tools with typed results, or used on its own for clients that can't run shell commands.

## The Frontier Labs guides

Complete, maintained setup guides live in the [Frontier Labs repository on GitHub](https://github.com/tekgrunt/frontier-labs). They cover tool-by-tool setup, a drop-in context file that teaches any model the platform, copy-paste prompts, and helper scripts.

### Setup guides

- [Getting started: LimaCharlie access](https://github.com/tekgrunt/frontier-labs/blob/main/docs/getting-started.md) — org, API key with least-privilege permission sets, credentials, and CLI install; model-agnostic and the prerequisite for the tool guides
- [Gemini CLI](https://github.com/tekgrunt/frontier-labs/blob/main/docs/gemini-cli.md) — Google's Gemini CLI: CLI access, optional MCP connection, `GEMINI.md` context, custom `/lc:` slash commands, and headless usage
- [OpenAI Codex](https://github.com/tekgrunt/frontier-labs/blob/main/docs/codex-cli.md) — Codex CLI: sandbox networking caveats, MCP via `config.toml`, per-tool approval guardrails, and `codex exec` for scripted runs
- [Claude Code](https://github.com/tekgrunt/frontier-labs/blob/main/docs/claude-code.md) — pointer back to the native plugin, which is the better path for Claude Code users

### Working with the platform

- [Common tasks cookbook](https://github.com/tekgrunt/frontier-labs/blob/main/docs/common-tasks.md) — SOC workflows with the prompt to give your agent and the CLI/MCP calls underneath: fleet visibility, LCQL hunting, detection triage, IOC sweeps, D&R rule authoring and replay, response actions, and Infrastructure-as-Code
- [Prompt library](https://github.com/tekgrunt/frontier-labs/blob/main/examples/prompts.md) — copy-paste starting points organized by workflow; they work identically across Gemini CLI, Codex, and Claude Code
- [Agent context file (AGENTS.md)](https://github.com/tekgrunt/frontier-labs/blob/main/context/AGENTS.md) — a drop-in file that teaches any model the platform: key concepts, an LCQL primer, a CLI/MCP quick reference, and standing safety rules (never take response actions without human confirmation)
- [Troubleshooting](https://github.com/tekgrunt/frontier-labs/blob/main/docs/troubleshooting.md) — MCP connection failures, permission 401s, JWT expiry, offline-sensor timeouts, and sandbox networking

### Configs and scripts

- [Example configurations](https://github.com/tekgrunt/frontier-labs/tree/main/examples) — sample `settings.json` (Gemini) and `config.toml` (Codex) with destructive tools disabled and read-only tool allowlists
- [Helper scripts](https://github.com/tekgrunt/frontier-labs/tree/main/scripts) — one-shot setup for Gemini/Codex, a setup checker, JWT exchange, and non-interactive LCQL runs

## Safety notes

Whatever the model, the same rules apply:

- Scope the agent's API key to what it needs — see [Permission Requirements](mcp-server.md#permission-requirements). A good pattern is two keys: `ai-readonly` for daily work and `ai-responder` exported only during active response work.
- Keep response actions (isolation, rule deployment, endpoint tasking) behind approval prompts; the tool guides show how for each client.
- Never run auto-approval modes with a key that holds write permissions like `sensor.task` or `dr.set`.
