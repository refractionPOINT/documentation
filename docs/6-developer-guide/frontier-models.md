# Using the CLI with other Frontier Models

LimaCharlie's deepest AI integration is with Claude — [AI Sessions](../9-ai-sessions/index.md) in the browser and the [Claude Code plugin](mcp-server.md#option-1-claude-code-plugin-recommended) in the terminal. But the platform itself is API-first and model-agnostic: any agent that can run shell commands can operate it through the [`limacharlie` CLI](cli.md), whatever frontier model it runs on.

The CLI is the recommended integration for agents that aren't Claude Code. Two things make it work especially well:

- Every command supports `--ai-help` — help text written specifically for LLM consumption, so an agent can teach itself the platform as it goes
- It is scriptable: cron jobs, CI checks, and bulk operations work the same way for an agent as for a human

The [MCP server](mcp-server.md) can be added alongside the CLI when you want structured tools with typed results, or used on its own for clients that can't run shell commands.

## The CLI in 60 seconds

```bash
pip install limacharlie
limacharlie auth login --oid YOUR_ORG_ID --api-key YOUR_API_KEY
limacharlie auth whoami        # verify
```

Or via Docker, with no Python needed:

```bash
docker run -v ${HOME}/.limacharlie:/root/.limacharlie:ro refractionpoint/limacharlie:latest whoami
```

The CLI and SDK read, in order of precedence: environment variables, then `~/.limacharlie` (YAML).

```bash
export LC_OID="your-org-id"
export LC_API_KEY="your-api-key"
```

The credentials file supports named environments, selected with `LC_CURRENT_ENV`:

```yaml
oid: "default-org-id"
api_key: "default-key"
env:
  production:
    oid: "..."
    api_key: "..."
  staging:
    oid: "..."
    api_key: "..."
```

### Scoping the agent's key

Grant only what the agent needs — see [Permission Requirements](mcp-server.md#permission-requirements) for permission sets by use case, and [API Keys](../7-administration/access/api-keys.md) for creating keys.

> **Tip:** make two keys — `ai-readonly` and `ai-responder` — and only export the responder key into your shell when you're actively doing response work. Never run an agent's auto-approval mode with a key that holds write permissions like `sensor.task` or `dr.set`.

## Teach the model the platform

Regardless of tool, agents perform dramatically better with standing context about the platform: what the key concepts are, how LCQL works, and what the safety rules are. Save the following as a context file your agent loads automatically — `AGENTS.md` is a widely-supported convention (Codex, and Gemini CLI when configured; Claude Code reads `CLAUDE.md`).

??? example "LimaCharlie agent context file (click to expand, copy into AGENTS.md)"

    ````markdown
    # LimaCharlie Platform Context

    You are working with **LimaCharlie**, an Agentic SecOps Workspace: EDR
    sensors on endpoints, a telemetry data lake, detection & response (D&R)
    rules, and response capabilities — all API-first and built to be operated
    by agents. You interact with it through the `limacharlie` CLI and/or the
    LimaCharlie MCP tools (if connected).

    ## Ground rules (non-negotiable)

    1. **Never take response actions without explicit human confirmation in
       this session.** Response actions include: isolating a host
       (`isolate_network` / `segregate_network`), rejoining, deleting sensors,
       deleting or modifying D&R rules, killing processes, and any endpoint
       tasking that changes state. Read the sensor ID and hostname back to the
       human and get a yes before acting.
    2. **Prefer reads over writes.** Investigate with queries and detections
       first; propose changes rather than making them.
    3. **Validate before deploying.** D&R rules: validate
       (`validate_dr_rule_components`) and, when possible, replay against
       history (`limacharlie replay`) before enabling. LCQL: validate/estimate
       before running broad queries — they scan a data lake and have real cost.
    4. **Never print API keys, JWTs, or installation keys** into output, logs,
       or files.

    ## Discovering how to do things

    - Prefer the `limacharlie` CLI — it covers the full platform, and it is
      the only path for streaming (`limacharlie stream detections`),
      Infrastructure-as-Code (`limacharlie sync`), and replay.
    - Every `limacharlie` CLI command supports `--ai-help` — help text written
      specifically for you. When unsure of usage, run e.g.
      `limacharlie search --ai-help` before guessing flags.
    - If MCP tools are connected, they are a good alternative for structured
      operations (they return JSON and handle auth), and some live-sensor
      operations are MCP-only.
    - To check identity/auth: `limacharlie auth whoami` or MCP `who_am_i`.

    ## Key concepts

    - **Organization (org)**: a tenant, identified by an OID (UUID). All
      resources live in an org.
    - **Sensor**: an endpoint agent (Windows/macOS/Linux/Chrome/edge) or cloud
      adapter, identified by a SID (UUID). Sensors have platforms, hostnames,
      tags, and online/offline state.
    - **Events**: telemetry (e.g. `NEW_PROCESS`, `DNS_REQUEST`,
      `NETWORK_CONNECTIONS`, `CODE_IDENTITY`, `WEL` for Windows Event Logs).
      Stored ~1 year in the data lake.
    - **Detections**: outputs of D&R rules; have a category, severity, and the
      triggering event.
    - **D&R rules**: YAML with a `detect` block (event matching logic) and a
      `respond` block (actions: `report`, `task`, `add tag`,
      `isolate network`, ...). Stored in Hive; managed via `limacharlie dr ...`
      or MCP rule tools.
    - **LCQL**: the query language for the data lake (see below).
    - **Artifacts**: collected files/forensic data (memory dumps, logs,
      Velociraptor collections).

    ## LCQL in 60 seconds

    Pipe-separated:
    `<timeframe> | <sensor selector> | <event type(s)> | <filter> [ | <projection> ]`

    - Timeframe: `-10m`, `-1h`, `-24h`, or absolute epochs.
    - Sensor selector: `*` (all), `plat == windows`,
      `hostname contains "web"`, tag selectors.
    - Event types: one or more, space-separated: `NEW_PROCESS DNS_REQUEST`.
    - Filter: paths into the event, e.g.
      `event/DOMAIN_NAME contains 'example'`, operators: `==`, `!=`,
      `contains`, `ends with`, `>`, `is`.
    - Projection: `event/X as Alias`, `COUNT()`, `COUNT_UNIQUE()`,
      `GROUP BY()`, `ORDER BY(x desc)`, `LIMIT n`.

    Examples:

    ```text
    -24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)
    -1h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as SrcIP event/EVENT/EventData/TargetUserName as User
    -24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as Path event/HASH as Hash COUNT_UNIQUE(Hash) as Count GROUP BY(Path Hash)
    ```

    Validate before running broad queries: `dryrun` in `limacharlie search`
    gives a cost estimate. If MCP is available,
    `generate_lcql_query` → `validate_lcql_query` → `run_lcql_query` is a
    reliable alternative to free-handing syntax, and `get_event_schema` checks
    field paths for an event type.

    CLI caveat: `limacharlie search run --query '...'` takes the query WITHOUT
    the timeframe part (`[selector] | [event types] | filter [| projection]`);
    the time range goes in `--start`/`--end` as unix epoch seconds. String
    values use single quotes. Run `limacharlie search run --ai-help` for the
    full reference.

    ## Common operations quick reference

    | Task | CLI | MCP tool(s) |
    |---|---|---|
    | Who am I / auth check | `limacharlie auth whoami` | `who_am_i` |
    | List sensors | `limacharlie sensor list [--selector '...']` | `list_sensors`, `get_online_sensors` |
    | Sensor details | `limacharlie sensor --help` | `get_sensor_info`, `is_online` |
    | Query telemetry | `limacharlie search run --query '...'` | `run_lcql_query` |
    | Recent detections | (REST/SDK) | `get_historic_detections` |
    | Live detection stream | `limacharlie stream detections` | — |
    | IOC search (data lake) | `limacharlie ioc --help` | `search_iocs`, `batch_search_iocs` |
    | Live org-wide sweep | `limacharlie spotcheck --help` | — |
    | List / set D&R rules | `limacharlie dr list`, `dr set` ⚠️ | `get_detection_rules`, `set_rule` ⚠️ |
    | Replay rule vs history | `limacharlie replay --help` | — |
    | Live process listing | — | `get_processes` (sensor must be online) |
    | Network connections | — | `get_network_connections` |
    | Autoruns / services / drivers | — | `get_autoruns`, `get_services`, `get_drivers` |
    | Isolate / rejoin host ⚠️ | — | `isolate_network`, `rejoin_network`, `is_isolated` |
    | Artifacts | `limacharlie artifact --help` | `list_artifacts`, `get_artifact` |
    | Org config as code | `limacharlie sync pull` / `sync push --dry-run` | — |

    ⚠️ = requires explicit human confirmation first (ground rule 1). Also note
    live-sensor tools fail on offline sensors — check `is_online` first, and
    use `reliable_tasking` to queue for offline hosts.

    ## Auth environment

    The CLI/SDK reads `LC_OID` + `LC_API_KEY` env vars, or `~/.limacharlie`
    (YAML, supports named environments via `LC_CURRENT_ENV`). REST calls use a
    JWT from `https://jwt.limacharlie.io` (valid 1 hour):
    `curl -X POST https://jwt.limacharlie.io -d "oid=$LC_OID&secret=$LC_API_KEY"`
    → use as `Authorization: Bearer <jwt>` against
    `https://api.limacharlie.io`. If an operation returns 401, the API key
    lacks that permission — report which permission is likely missing (format
    `category.action`, e.g. `sensor.task`, `insight.evt.get`) rather than
    retrying.
    ````

## Gemini CLI

Setup for [Google's Gemini CLI](https://github.com/google-gemini/gemini-cli).

### Install and authenticate

```bash
npm install -g @google/gemini-cli    # or: brew install gemini-cli, or: npx @google/gemini-cli
```

Authenticate by running `gemini` and signing in with Google, or export a `GEMINI_API_KEY` from AI Studio, or use Vertex AI.

Install the `limacharlie` CLI as shown above — Gemini CLI can run shell commands, so this alone gives the agent access to the full platform.

### (Optional) Connect the MCP server

One command:

```bash
gemini mcp add limacharlie https://mcp.limacharlie.io/mcp --transport http \
  --header "Authorization: Bearer YOUR_API_KEY:YOUR_ORG_ID"
```

Or edit `~/.gemini/settings.json` (user-wide) / `<project>/.gemini/settings.json` (project-scoped, wins on conflict) directly:

```json
{
  "mcpServers": {
    "limacharlie": {
      "httpUrl": "https://mcp.limacharlie.io/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY:YOUR_ORG_ID"
      },
      "timeout": 30000
    }
  }
}
```

Notes:

- `httpUrl` selects the streamable HTTP transport, which is what the LimaCharlie server uses. Don't confuse it with `url`, which is SSE.
- The token format is `API_KEY` + colon + `ORG_ID` for an organization key. For multi-org access, exchange a *user* API key for a JWT (see [Connecting AI Assistants](mcp-server.md#option-3-http-mcp-with-keys)) and use `Bearer YOUR_JWT` instead — but JWTs expire after 1 hour, so the static `key:oid` form is more practical for a config file.
- If you keep the token in the user-scoped file, `chmod 600 ~/.gemini/settings.json`. Avoid putting it in a project-scoped settings file that might get committed.

Verify: start `gemini` and run `/mcp` — you should see `limacharlie` as `CONNECTED` with its tool list.

The full server exposes a large number of tools, which costs context. Use `includeTools` to allowlist what you need, or `excludeTools` to cut what you don't (for example `"excludeTools": ["delete_sensor", "delete_org_note", "remove_org_user"]`).

> **Warning:** do not set `"trust": true` for the LimaCharlie server. Keeping trust off means Gemini asks before each tool call — exactly what you want when tools can isolate machines from the network.

### Context file

Gemini CLI automatically loads context files named `GEMINI.md` from `~/.gemini/GEMINI.md`, the project root, and directories it works in. Save the [agent context file](#teach-the-model-the-platform) into your working directory as `GEMINI.md`. Or, to share one context file across tools, configure Gemini to also read `AGENTS.md` — in settings.json:

```json
{
  "context": { "fileName": ["AGENTS.md", "GEMINI.md"] }
}
```

Confirm it loaded with `/memory show`.

### Custom slash commands

Gemini CLI supports custom commands as TOML files in `~/.gemini/commands/` (global) or `<project>/.gemini/commands/`. For example, `~/.gemini/commands/lc/triage.toml`:

```toml
description = "Pull and triage the last 24h of LimaCharlie detections"
prompt = """
Pull LimaCharlie detections from the last 24 hours, group them by rule and
severity, and triage each group: true positive, noise, or needs investigation
— with reasoning. Read-only: do not take any response actions.
"""
```

And `~/.gemini/commands/lc/hunt.toml`, which takes an argument:

```toml
description = "Hunt an IOC (hash, domain, or IP) across the fleet"
prompt = """
Hunt this indicator across the LimaCharlie org for the last 30 days: {{args}}
Tell me which hosts touched it and when, as a timeline. Read-only: do not
take any response actions.
"""
```

Then inside Gemini, run `/lc:triage` or `/lc:hunt 8.8.8.8`.

### Headless / scripted usage

Gemini CLI runs non-interactively with `-p`:

```bash
gemini -p "Use LimaCharlie tools to summarize the last 24h of detections by category and severity. Output markdown." \
  --output-format text > /tmp/lc-daily-report.md
```

`--output-format json` gives you `{response, stats}` for piping into other tools; `stream-json` emits NDJSON events. The default approval mode requires confirmation for tool calls, which blocks headless runs — for unattended read-only jobs, either allowlist just the read tools you need (`tools.allowed` in settings, or `includeTools` on the MCP server) or — only with a read-only API key — `--approval-mode yolo`. Never combine yolo mode with a key that has `sensor.task` or `dr.set`.

## OpenAI Codex

Setup for [OpenAI's Codex CLI](https://github.com/openai/codex).

### Install and authenticate

```bash
npm install -g @openai/codex     # or: brew install --cask codex
```

Authenticate with `codex login` (ChatGPT account, browser OAuth; `--device-auth` for headless boxes) or an API key: `echo $OPENAI_API_KEY | codex login --with-api-key`.

Install the `limacharlie` CLI as shown above. One caveat: Codex's default sandbox blocks outbound network, so for `limacharlie` CLI calls to work you'll either approve escalations as they come, or set:

```toml
[sandbox_workspace_write]
network_access = true
```

(MCP tools, if you add them below, are unaffected — they run outside the sandbox.)

### (Optional) Connect the MCP server

Codex configures MCP servers in `~/.codex/config.toml`. The LimaCharlie hosted server is a remote streamable-HTTP server, configured with `url`:

```toml
[mcp_servers.limacharlie]
url = "https://mcp.limacharlie.io/mcp"
bearer_token_env_var = "LC_MCP_TOKEN"
startup_timeout_sec = 20
tool_timeout_sec = 120
```

Then in your shell profile:

```bash
export LC_MCP_TOKEN="YOUR_API_KEY:YOUR_ORG_ID"
```

`bearer_token_env_var` tells Codex to read the token from the environment and send `Authorization: Bearer <value>` — your secret stays out of the config file. The token format is `API_KEY` + colon + `ORG_ID` for an organization API key; for multi-org access, exchange a *user* API key for a JWT instead (see [Connecting AI Assistants](mcp-server.md#option-3-http-mcp-with-keys)).

Verify: start `codex` and type `/mcp` — you should see `limacharlie` connected with its tools. Outside a session: `codex mcp list`.

### Guardrails

Codex lets you gate MCP tools per server and per tool. Auto-approve reads, prompt on everything else:

```toml
[mcp_servers.limacharlie]
url = "https://mcp.limacharlie.io/mcp"
bearer_token_env_var = "LC_MCP_TOKEN"
default_tools_approval_mode = "prompt"

# Reads the agent may call freely:
[mcp_servers.limacharlie.tools.list_sensors]
approval_mode = "approve"
[mcp_servers.limacharlie.tools.get_sensor_info]
approval_mode = "approve"
[mcp_servers.limacharlie.tools.get_historic_detections]
approval_mode = "approve"
[mcp_servers.limacharlie.tools.run_lcql_query]
approval_mode = "approve"
```

Or hard-disable destructive tools entirely:

```toml
disabled_tools = ["delete_sensor", "delete_org_note", "remove_org_user"]
```

If the tool count is heavy on context, allowlist with `enabled_tools = [...]`.

### Context file

Codex automatically loads `AGENTS.md` from `~/.codex/AGENTS.md` (global), your repo root, and the working directory — later files win. Save the [agent context file](#teach-the-model-the-platform) as `AGENTS.md` in your working directory.

### Headless / scripted usage

```bash
codex exec -a never --sandbox read-only \
  "Use LimaCharlie tools to summarize the last 24h of detections by category and severity. Output markdown." \
  -o /tmp/lc-daily-report.md
```

Useful flags: `--json` (NDJSON event stream), `-o report.md` (write the final message to a file), `--sandbox read-only`, `-a never` (no approval prompts — only safe with a read-only LimaCharlie key). For finer command-level control (for example, allow `limacharlie search` unprompted but gate everything else), see Codex [execpolicy rules](https://developers.openai.com/codex/rules) in `~/.codex/rules/`.

## Common tasks

Each task below shows the **prompt** you'd give your agent, and **what's underneath** — the CLI commands and/or MCP tools the agent will (or should) reach for. Knowing the underlying calls helps you verify the agent did the right thing. Prompts work identically in Claude Code, Gemini CLI, and Codex.

### Fleet visibility

> "List my online sensors grouped by platform, and flag anything that hasn't checked in for more than 7 days."

Underneath:

```bash
limacharlie sensor list
limacharlie sensor list --selector 'plat == windows'
```

Or MCP `list_sensors` / `get_online_sensors`. For a sensor deep-dive (processes, network connections, autoruns), the MCP live-tasking tools `get_processes`, `get_network_connections`, and `get_autoruns` need the sensor online and a key with `sensor.task`.

### Querying telemetry (LCQL)

LCQL queries have four pipe-separated parts (plus optional projection) — see [Data & Queries](../4-data-queries/index.md) for the full reference and [LCQL Examples](../4-data-queries/lcql-examples.md) for more queries:

```text
<timeframe> | <sensor selector> | <event type(s)> | <filter> [ | <projection> ]
```

> "Query the last 24 hours of DNS requests on Windows sensors and show me the 20 least-common domains."

```text
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME != "" | event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)
```

> "Show me failed Windows logons in the last hour with source IP, logon type, and target user."

```text
-1h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as SrcIP event/EVENT/EventData/LogonType as LogonType event/EVENT/EventData/TargetUserName as Username
```

> "Find unsigned executables that ran across the fleet in the last 24 hours, grouped by path and hash."

```text
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as Path event/HASH as Hash COUNT_UNIQUE(Hash) as Count GROUP BY(Path Hash)
```

Run these with `limacharlie search run` or MCP `run_lcql_query`; `generate_lcql_query` has the platform build the query for you.

> **Cost tip:** LCQL queries scan the data lake. Have the agent use `dryrun` in `limacharlie search` (or MCP `validate_lcql_query` / `estimate_lcql_query`) before running broad queries.

### Detections

> "Pull detections from the last 24 hours, group them by rule and severity, and tell me which ones look like real incidents vs noise. For anything interesting, pull the surrounding telemetry."

Underneath: MCP `get_historic_detections` → `get_historic_events` for context. The key needs `insight.det.get` / `insight.evt.get`. To watch live instead:

```bash
limacharlie stream detections     # also: stream events --tag vip, stream audit
```

For an IOC sweep ("search the whole org for this hash / domain / IP over the last 30 days"): `limacharlie ioc --help` (data-lake search), `limacharlie spotcheck --help` (live org-wide sweep), or MCP `search_iocs` / `batch_search_iocs`.

### Detection engineering (D&R rules)

> "Write a D&R rule that detects certutil.exe being used to download files, tags the sensor, and reports the detection. Validate it before showing me."

Underneath — the agent drafts the YAML and manages it with the CLI:

```bash
limacharlie dr list
limacharlie dr set --key my-rule --input-file rule.yaml --enabled
limacharlie dr disable --key my-rule
```

With MCP connected, it can also use `generate_dr_rule_detection` + `generate_dr_rule_respond`, then `validate_dr_rule_components`, and deploy with `set_rule` (needs `dr.set`). Either way, keep deployment behind an approval prompt. Before deploying, test against history: `limacharlie replay --help` replays historical telemetry through a rule.

### Response actions ⚠️

These change endpoint state. Keep them behind approval prompts (see the Gemini and Codex guardrail sections above), use a key with `sensor.task` only when needed, and have the agent confirm the exact sensor ID with you first.

> "FINANCE-03 looks compromised. Confirm its sensor ID with me, then isolate it from the network."

Underneath: MCP `isolate_network` (verify with `is_isolated`, undo with `rejoin_network`). Isolation blocks all traffic except to the LimaCharlie cloud and persists across reboots. For evidence collection first: `get_processes`, `get_network_connections`, `get_autoruns`; for deeper forensics, `collect_velociraptor_artifact` and the artifacts API (`list_artifacts` / `get_artifact`, or `limacharlie artifact --help`).

### Infrastructure-as-Code

> "Pull this org's full config and commit it to git so we can track changes."

```bash
limacharlie sync pull --oid $LC_OID
limacharlie sync push --dry-run --oid $LC_OID --config lc-config.yaml   # always dry-run first
```

This pairs well with a coding agent: keep your org config in a repo, let the agent edit the YAML, review the diff, `sync push --dry-run`, then apply.

## Prompt library

Copy-paste starting points for the workflows above.

### Orientation (start here on a new org)

```text
Use the LimaCharlie tools to orient me: who am I authenticated as, what org is this, how many sensors are there and on what platforms, and what D&R rules are currently active? Output a short briefing.
```

### Fleet

```text
List sensors that haven't checked in for more than 7 days. Table: hostname, platform, last seen.
```

```text
Which of my sensors are missing the `vip` tag but have hostnames matching our executive naming convention (EXEC-*)?
```

### Hunting

```text
Query the last 24h of DNS requests on Windows sensors and show me the 20 least-common domains with the hosts that resolved them.
```

```text
Find unsigned executables that ran in the last 24 hours, grouped by path and hash. Then check the top 5 hashes against the IOC search for the last 30 days.
```

```text
Hunt this indicator across the org for the last 30 days and build a timeline of every host that touched it: 8.8.8.8
```

```text
Show me processes that made network connections to non-standard ports (>1024) in the last hour, excluding browsers.
```

### Detections & triage

```text
Pull the last 24h of detections, group by rule and severity, and triage: true positive, noise, or needs investigation — with reasoning. Prioritize what I should look at first.
```

```text
This detection looks interesting: <paste detection JSON or ID>. Pull the surrounding 30 minutes of telemetry from that sensor and reconstruct what happened.
```

### Detection engineering

```text
Write a D&R rule that detects PowerShell with an encoded command line spawned by an Office application. Validate the rule components, explain each part, and show me the YAML — but do not deploy it.
```

```text
Here's a threat report: <paste/link>. Extract the IOCs and behaviors, check whether we have any matching activity in the last 30 days, and propose D&R rules for the behaviors we can't already detect.
```

```text
Replay my rule `suspicious-certutil` against last week's telemetry and estimate the false-positive rate.
```

### Incident response (approval prompts on!)

```text
HOST-042 triggered a credential-theft detection. Before anything else: pull its process list, network connections, and autoruns, and save them to ./evidence/. Then walk me through what you see. Do not isolate anything yet.
```

```text
I've reviewed the evidence — isolate HOST-042 now. Confirm the sensor ID with me first, then verify isolation took effect.
```

```text
The incident is resolved. Rejoin HOST-042 to the network and confirm it's back online.
```

### Reporting

```text
Generate a weekly SOC report: detection volume by day and category, top 10 noisiest rules, sensors added/removed, and any coverage gaps. Markdown.
```

```text
Produce a MITRE ATT&CK coverage summary for this org based on the current detection rules.
```

### Infrastructure-as-Code prompts

```text
Run `limacharlie sync pull` for this org, then explain the org's configuration to me like I'm a new SOC hire: what's being collected, what rules exist, where outputs go.
```

```text
Edit the pulled config to add a new D&R rule (file: rules/encoded-powershell.yaml), show me the diff, run `sync push --dry-run`, and stop for my review before applying.
```

## Troubleshooting

### Gemini CLI: `/mcp` shows `DISCONNECTED`

- Check the header format. It must be exactly `Authorization: Bearer YOUR_API_KEY:YOUR_ORG_ID` — API key first, then a colon, then the org ID (a UUID). Swapping them is the most common mistake.
- Make sure you used `httpUrl` (streamable HTTP), not `url` (SSE), in settings.json.
- Confirm the key still exists in **Access Management → REST API** and wasn't revoked.
- Run `gemini` with `-d` (debug) for connection details.

### Codex: server missing from `/mcp`

- `codex mcp get limacharlie` — does the config parse and show what you expect?
- If you used `bearer_token_env_var`, the env var must be exported in the shell that launched Codex. Check with `echo $LC_MCP_TOKEN` — it should print `key:oid`.
- Raise `startup_timeout_sec` (default 10) if you're on a slow link.

### HTTP 401 on specific tool calls / REST endpoints

The key authenticated fine but lacks a permission. Match the failing operation to the permission tables in [Permission Requirements](mcp-server.md#permission-requirements) — for example, LCQL queries need `insight.evt.get` and live sensor commands need `sensor.task` — and add it to the key in the web app. Changes take effect immediately; reconnect the MCP server (or restart the CLI session) if results seem stale.

### JWT calls suddenly failing after working

JWTs expire after **one hour**. Re-exchange the API key for a fresh JWT (see [API Keys](../7-administration/access/api-keys.md)) or switch to the static `key:oid` bearer format for MCP, which doesn't expire.

### `limacharlie` CLI says unauthenticated

- `limacharlie auth whoami` — what identity does it think you have?
- Precedence: `LC_OID`/`LC_API_KEY` env vars override `~/.limacharlie`. A stale env var in your profile silently wins over a fresh `auth login`.
- Multiple orgs: `limacharlie auth list-orgs` then `limacharlie auth use-org <name>`, or set `LC_CURRENT_ENV` to a named environment from the credentials file.

### Live-sensor tools return nothing / time out

Tools like `get_processes`, `get_network_connections`, and `yara_scan_process` task the actual endpoint — the sensor must be **online**. Check with `is_online` (MCP) or `limacharlie sensor list`. For offline sensors, queue commands via the Reliable Tasking extension (`reliable_tasking` MCP tool) instead. Historic-data tools (`run_lcql_query`, `get_historic_detections`, `get_historic_events`) work regardless of sensor state — they hit the data lake.

### The agent picks wrong tools or writes bad LCQL

- Make sure the [context file](#teach-the-model-the-platform) loaded: `/memory show` in Gemini; for Codex, verify `AGENTS.md` is in the repo root or `~/.codex/`.
- LCQL help: the platform can write queries for the agent — tell it to use `generate_lcql_query` and `validate_lcql_query` rather than free-handing syntax.
- CLI usage: remind the agent that every `limacharlie` command supports `--ai-help`.
