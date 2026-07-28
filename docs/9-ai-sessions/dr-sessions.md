# D&R-Driven AI Sessions

D&R-Driven AI Sessions start Claude AI sessions automatically in response to detections, events, or any condition that a Detection & Response rule matches. This gives you automated workflows for investigation, triage, and response.

## Overview

When a D&R rule matches, the `start ai agent` response action launches a Claude session with:

- A prompt that contains the context that you specify
- The auto-installed `limacharlie` CLI for LimaCharlie operations, authenticated by `lc_api_key_secret`, plus any built-in tools and external MCP servers that you configure
- Optional event data that the action extracts and includes automatically

The session runs autonomously and does the investigation or analysis that you defined. You can capture the results with outputs, or store them for later review.

## The `start ai agent` Action

There are two ways to configure the action: **inline mode** (all parameters in the rule) or **definition mode** (a reference to a pre-configured AI agent in the Hive).

### Inline Mode

Specify all session parameters directly in the D&R rule:

```yaml
respond:
  - action: start ai agent
    prompt: "Your instructions to Claude..."
    anthropic_secret: hive://secret/my-anthropic-key
```

#### Required Parameters (Inline Mode)

| Parameter | Description |
|-----------|-------------|
| `prompt` | The instructions for Claude. Supports [template strings](../4-data-queries/template-transforms.md) to include event data. |
| `anthropic_secret` | Your Anthropic API key. Use `hive://secret/<name>` to reference a [Hive Secret](../7-administration/config-hive/secrets.md). To route through AWS Bedrock or Google Cloud Vertex AI instead, use definition mode with the `bedrock:` / `vertex:` blocks on an `ai_agent` Hive record — see [Alternative AI Providers](alternative-providers.md). |

#### Optional Parameters (Inline Mode)

| Parameter | Description |
|-----------|-------------|
| `name` | Session name. Supports template strings. Useful to identify sessions in logs. |
| `lc_api_key_secret` | LimaCharlie API key for org-level API access. Use `hive://secret/<name>`. |
| `lc_uid_secret` | LimaCharlie User ID. Necessary when `lc_api_key_secret` is a user API key and not an org API key. Use `hive://secret/<name>`. |
| `idempotent_key` | Unique key that stops duplicate sessions. Supports template strings. |
| `debounce_key` | Serializes sessions: one active session for each key. New requests queue behind the active session and start again when it ends. Supports template strings. |
| `data` | Extract event data fields to include in the prompt as JSON. |
| `profile` | Inline session configuration (tools, model, limits, and more). |
| `profile_name` | Reference a saved profile by name. Supported only for user sessions at present. For D&R sessions, use inline `profile` instead. |

> You can specify `profile` (inline) or `profile_name` (reference), but not both.

### Definition Mode

Reference a pre-configured AI agent definition stored in the Hive:

```yaml
respond:
  - action: start ai agent
    definition: hive://ai_agent/my-triage-bot
```

In definition mode, all session configuration (prompt, anthropic key, profile, and more) comes from the referenced AI agent record. You need no other parameters.

#### Per-rule Augmentation

A rule that uses `definition:` can also supply its own `prompt:` and `data:` fields. LimaCharlie merges these with the values on the `ai_agent` record. One agent definition can therefore be reused across many rules, with task-specific augmentation for each rule:

- **`prompt`** — appended to the prompt of the `ai_agent` record, with a blank line between them. The prompt of the agent is the stable core. The prompt of the rule adds detail for that rule.
- **`data`** — extracted from the event on the rule side (templates, `secret://` and gjson callbacks resolve as usual) and merged with the data extraction of the `ai_agent` record. The merged dictionary is appended to the prompt as one JSON code block. **Rule keys override agent keys on collision**, so a rule can replace or add fields for its trigger.

```yaml
respond:
  - action: start ai agent
    definition: hive://ai_agent/detection-investigator
    debounce_key: "investigate-{{ .routing.sid }}"
    # Appended to the ai_agent record's prompt
    prompt: |
      Focus specifically on credential-theft TTPs for this trigger.
    # Merged with the ai_agent record's data: extraction; rule keys win
    data:
      trigger_rule: "credential-dumping-suspect"
      detection_name: "{{ .detect.cat }}"
```

You can also set `debounce_key` at the action level in definition mode. It overrides the value on the `ai_agent` record:

```yaml
respond:
  - action: start ai agent
    definition: hive://ai_agent/my-triage-bot
    debounce_key: "investigate-{{ .routing.sid }}"
```

## Configuration Options

### Prompt Templating

The `prompt` parameter supports the template syntax of LimaCharlie. You can include event data directly in your instructions:

```yaml
- action: start ai agent
  prompt: |
    A suspicious process was detected on {{ .routing.hostname }}.

    Process: {{ .event.FILE_PATH }}
    Command Line: {{ .event.COMMAND_LINE }}
    User: {{ .event.USER_NAME }}

    Please investigate this activity and determine if it's malicious.
  anthropic_secret: hive://secret/anthropic-key
```

### Data Extraction

Use the `data` parameter to extract specific fields and include them as structured JSON:

```yaml
- action: start ai agent
  prompt: "Analyze this detection and provide a severity assessment."
  anthropic_secret: hive://secret/anthropic-key
  data:
    hostname: "{{ .routing.hostname }}"
    sensor_id: "{{ .routing.sid }}"
    process_path: "{{ .event.FILE_PATH }}"
    command_line: "{{ .event.COMMAND_LINE }}"
    parent_process: "{{ .event.PARENT/FILE_PATH }}"
    detection_name: "{{ .detect.cat }}"
```

The extracted data is appended to the prompt as a JSON code block.

### Idempotent Sessions

Use `idempotent_key` to stop duplicate sessions for the same event:

```yaml
- action: start ai agent
  prompt: "Investigate this detection..."
  anthropic_secret: hive://secret/anthropic-key
  idempotent_key: "{{ .detect.detect_id }}"
```

If a session with the same idempotent key was created in the last 24 hours, LimaCharlie skips the action.

### Debounced Sessions

Use `debounce_key` to serialize sessions, so that only one session runs at a time for each key. If a session is already active for a debounce key, LimaCharlie queues the new requests. When the active session ends, LimaCharlie starts the most recent queued request automatically.

This is useful for workflows where many detections can fire quickly but one agent must handle them in sequence (for example, a triage bot that works cases one at a time).

```yaml
- action: start ai agent
  prompt: "Investigate this case..."
  anthropic_secret: hive://secret/anthropic-key
  debounce_key: "triage-bot"
```

`idempotent_key` drops duplicates silently. `debounce_key` instead makes sure that the latest request is processed, but it waits for the current session to finish first. LimaCharlie keeps only the most recent pending request for each key. The key supports template strings for dynamic serialization:

```yaml
# Serialize per sensor — one active investigation per endpoint
debounce_key: "investigate-{{ .routing.sid }}"
```

> **Debounce vs Idempotent**: Use `idempotent_key` when the same event must never create more than one session. Use `debounce_key` when each event must be processed, but in sequence and not in parallel.

### Session Profiles

Profiles let you configure the behavior of Claude, the available tools, and the resource limits.

#### Inline Profile

```yaml
- action: start ai agent
  prompt: "Investigate this activity..."
  anthropic_secret: hive://secret/anthropic-key
  profile:
    # Tool access
    allowed_tools:
      - Bash
      - Read
      - Grep
      - Glob
      - WebFetch
    denied_tools:
      - Write
      - Edit

    # Permission mode
    permission_mode: acceptEdits

    # Model configuration
    model: claude-sonnet-4-20250514
    max_turns: 50
    max_budget_usd: 5.0
    one_shot: true  # Complete initial task then terminate (this is the default for D&R sessions)
    ttl_seconds: 1800

    # Environment variables
    environment:
      LOG_LEVEL: debug
      API_KEY: hive://secret/external-api-key
```

> LimaCharlie itself does **not** need an `mcp_servers` entry. The session reaches LimaCharlie through the auto-installed `limacharlie` CLI, authenticated by the `lc_api_key_secret` that you supply. The `mcp_servers` map below is only for *external/third-party* tools (threat-intel, ticketing, and similar).

#### Profile Options

> The dedicated [Tool Permissions & Profiles](tool-permissions.md) page holds the full pattern grammar for `allowed_tools` and `denied_tools` (built-in Claude Code tool names, `Bash(prefix:*)` scoping, and MCP `mcp__server__tool` names). It also holds the precedence rules and the semantics of `permission_mode`. Unattended D&R agents usually need `permission_mode: bypassPermissions`, so that tool calls do not stop for approval prompts.

| Option | Type | Description |
|--------|------|-------------|
| `allowed_tools` | list | Tools Claude can use. If empty, all tools are allowed. See [Tool Permissions & Profiles](tool-permissions.md#tool-name-grammar). |
| `denied_tools` | list | Tools Claude cannot use. Takes precedence over `allowed_tools`. See [Tool Permissions & Profiles](tool-permissions.md#allowed_tools-vs-denied_tools). |
| `permission_mode` | string | `acceptEdits` (default), `plan`, or `bypassPermissions`. See [Tool Permissions & Profiles](tool-permissions.md#permission_mode). |
| `model` | string | Claude model to use (e.g., `claude-sonnet-4-20250514`) |
| `max_turns` | integer | Maximum conversation turns before the session stops automatically |
| `max_budget_usd` | float | Maximum spend limit in USD |
| `one_shot` | boolean | When `true`, the session completes all work for the initial prompt (including tools, skills, and subagents), then stops automatically. Default: `true` for D&R-triggered sessions. |
| `ttl_seconds` | integer | Maximum session lifetime in seconds. Capped at 24 hours. |
| `environment` | map | Environment variables. Values can use `hive://secret/` |
| `mcp_servers` | map | External/third-party MCP server configurations (see below). Not needed for LimaCharlie access. |

### MCP Server Configuration

MCP (Model Context Protocol) servers extend the capabilities of Claude with *external/third-party* data sources and tools.

> You do **not** configure LimaCharlie here. The session already has the auto-installed `limacharlie` CLI for all LimaCharlie operations (authenticated by `lc_api_key_secret`). Reserve `mcp_servers` for outside services such as threat-intel, ticketing, or custom enrichment tools.

#### HTTP MCP Server

```yaml
mcp_servers:
  virustotal:
    type: http
    url: https://vt-mcp.example.com
    headers:
      x-apikey: hive://secret/vt-api-key
```

#### Stdio MCP Server

```yaml
mcp_servers:
  custom-tool:
    type: stdio
    command: /usr/bin/my-tool
    args:
      - --config
      - /etc/my-tool.conf
    env:
      API_KEY: hive://secret/tool-api-key
```

## Examples

### Example 1: Basic Detection Investigation

Investigate automatically when a rule detects a suspicious process:

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: -encodedcommand

respond:
  - action: report
    name: encoded-powershell-command
  - action: start ai agent
    prompt: |
      A PowerShell process with an encoded command was detected.

      Decode the command and analyze what it does.
      Check for persistence mechanisms, lateral movement, or data exfiltration.
      Provide a severity assessment and recommended response actions.
    anthropic_secret: hive://secret/anthropic-key
    data:
      command_line: "{{ .event.COMMAND_LINE }}"
      hostname: "{{ .routing.hostname }}"
      user: "{{ .event.USER_NAME }}"
```

### Example 2: Automated Triage with the LimaCharlie CLI

The session reaches LimaCharlie through the auto-installed `limacharlie` CLI. Supply `lc_api_key_secret` to authenticate the CLI. LimaCharlie itself needs no `mcp_servers` entry:

```yaml
detect:
  target: detection
  event: "*"
  op: is greater than
  path: priority
  value: 3

respond:
  - action: start ai agent
    prompt: |
      A high-priority detection was triggered. Use the `limacharlie` CLI to:

      1. Get information about the sensor where this occurred
      2. Query recent events from the same sensor
      3. Check if the same detection occurred on other sensors
      4. Look up any relevant threat intelligence

      Produce a summary report with:
      - What happened
      - Scope of impact
      - Recommended immediate actions
      - Suggested long-term mitigations
    anthropic_secret: hive://secret/anthropic-key
    lc_api_key_secret: hive://secret/lc-api-key
    idempotent_key: "{{ .detect.detect_id }}"
    profile:
      max_turns: 100
      max_budget_usd: 10.0
```

### Example 3: Threat Hunting Automation

Investigate IoC matches from threat intelligence automatically:

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: lookup/threat-domains

respond:
  - action: report
    name: threat-intel-domain-match
  - action: start ai agent
    name: "threat-hunt-{{ .routing.sid }}"
    prompt: |
      A DNS request to a known malicious domain was detected.

      Using the available tools:
      1. Identify the process that made the DNS request
      2. Examine the process's network connections
      3. Check for any files written by the process
      4. Look for persistence mechanisms
      5. Identify if other sensors communicated with this domain

      Document all findings and provide a detailed incident report.
    anthropic_secret: hive://secret/anthropic-key
    lc_api_key_secret: hive://secret/lc-api-key
    profile:
      allowed_tools:
        - Bash
        - Read
        - Grep
        - Glob
        - WebFetch
      denied_tools:
        - Write
        - Edit
      max_turns: 150
      ttl_seconds: 3600
```

### Example 4: Custom Enrichment

Use external tools through MCP for enrichment:

```yaml
respond:
  - action: start ai agent
    prompt: |
      Enrich this alert with external threat intelligence.

      Check the file hash against VirusTotal.
      Look up the IP address geolocation and reputation.
      Cross-reference with MITRE ATT&CK techniques.
    anthropic_secret: hive://secret/anthropic-key
    data:
      file_hash: "{{ .event.HASH }}"
      ip_address: "{{ .event.IP_ADDRESS }}"
    profile:
      mcp_servers:
        virustotal:
          type: http
          url: https://vt-mcp.example.com
          headers:
            x-apikey: hive://secret/vt-api-key
        mitre:
          type: http
          url: https://mitre-mcp.example.com
```

### Example 5: Definition Mode with Hive AI Agent

You can store a reusable AI agent definition in the `ai_agent` hive and reference it by name. You then do not need all the session configuration inline in every D&R rule.

#### Step 1: Create the AI Agent Record

Store the agent definition in the `ai_agent` hive with the API, the CLI, or infrastructure-as-code:

```yaml
ai_agent:
  detection-investigator:
    data:
      # Credentials (use hive://secret/ references)
      anthropic_secret: hive://secret/anthropic-key
      lc_api_key_secret: hive://secret/lc-api-key

      # Prompt with instructions
      prompt: |
        You are a detection investigator. A detection has fired and you need to
        investigate it and document your findings.

        Using the provided event data:
        1. Get details about the sensor where this occurred
        2. Check the process tree and parent/child relationships
        3. Look for related network connections and file operations
        4. Check if similar activity exists on other sensors
        5. Assess severity and provide a recommendation

        Document all findings in a structured report.

      # Session name (supports template strings)
      name: "investigate-{{ .routing.hostname }}"

      # Extract event data fields to include in the prompt
      data:
        hostname: routing.hostname
        sensor_id: routing.sid
        detection_name: detect.cat

      # Session configuration
      model: claude-sonnet-4-20250514
      max_turns: 50
      max_budget_usd: 5.0
      ttl_seconds: 1800
      one_shot: true
      permission_mode: bypassPermissions

      # Tool restrictions
      allowed_tools:
        - Bash
        - Read
        - Grep
        - Glob
        - WebFetch
      denied_tools:
        - Write
        - Edit

      # No mcp_servers entry is needed for LimaCharlie access — the
      # auto-installed `limacharlie` CLI uses lc_api_key_secret above.
      # Add mcp_servers only for external/third-party tools.

    usr_mtd:
      enabled: true
```

#### Step 2: Reference It from D&R Rules

The D&R rule becomes minimal. It holds only a reference to the agent definition:

```yaml
detect:
  target: detection
  event: "*"
  op: is greater than
  path: priority
  value: 3

respond:
  - action: start ai agent
    definition: hive://ai_agent/detection-investigator
    debounce_key: "investigate-{{ .routing.sid }}"
```

This approach keeps D&R rules small. You update the behavior of the agent (prompt, model, tools, and more) in one place, and you do not change every rule that uses it. You can override the `debounce_key` at the action level in definition mode.

!!! tip "Per-rule prompt and data augmentation"
    Rules that use `definition:` can also supply `prompt:` and `data:` to augment the referenced agent. LimaCharlie appends the prompt of the rule to the prompt of the agent, with a blank line between them. It merges the extracted data of the rule into the data extraction of the agent, and rule keys override agent keys. See [Per-rule Augmentation](#per-rule-augmentation).

!!! tip "Reuse the same definition from the CLI"
    You can use the same `ai_agent` Hive record as a template from the CLI with `limacharlie ai start-session --definition <name>`. You can override single fields for each run (prompt, model, budget, tool list, environment, credentials). One definition is therefore both a D&R-driven agent and an ad-hoc CLI template. See [Command Line Interface](cli.md#limacharlie-ai-start-session) for the full list of override flags.

#### AI Agent Record Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | Yes | Instructions for Claude. |
| `anthropic_secret` | string | Conditional | Anthropic API key or `hive://secret/` reference. Necessary unless `bedrock:` or `vertex:` is set. See [Alternative AI Providers](alternative-providers.md). |
| `bedrock` | object | Conditional | AWS Bedrock provider block (`region`, `access_key_id_secret`, `secret_access_key_secret`, `session_token_secret`, `bearer_token_secret`). Mutually exclusive with `anthropic_secret` and `vertex`. See [Alternative AI Providers](alternative-providers.md#amazon-bedrock). |
| `vertex` | object | Conditional | Google Cloud Vertex AI provider block (`project_id`, `region`, `service_account_json_secret`). Mutually exclusive with `anthropic_secret` and `bedrock`. See [Alternative AI Providers](alternative-providers.md#google-cloud-vertex-ai). |
| `lc_api_key_secret` | string | No | LimaCharlie API key or `hive://secret/` reference. |
| `lc_uid_secret` | string | No | LimaCharlie User ID or `hive://secret/` reference. Necessary when `lc_api_key_secret` is a user API key. |
| `name` | string | No | Session name. Supports template strings. |
| `data` | map | No | Event data extraction mapping. |
| `allowed_tools` | list | No | Tools Claude can use. |
| `denied_tools` | list | No | Tools Claude cannot use. |
| `permission_mode` | string | No | `acceptEdits`, `plan`, or `bypassPermissions`. |
| `model` | string | No | Claude model identifier. With Bedrock or Vertex, use the model ID format of that provider (see [Alternative AI Providers](alternative-providers.md)). |
| `max_turns` | integer | No | Maximum conversation turns. |
| `max_budget_usd` | float | No | Maximum spend limit in USD. |
| `ttl_seconds` | integer | No | Maximum session lifetime in seconds. |
| `one_shot` | boolean | No | Stop automatically after the initial task. |
| `environment` | map | No | Environment variables (values can use `hive://secret/`). |
| `mcp_servers` | map | No | External/third-party MCP server configurations. Not needed for LimaCharlie access (the auto-installed CLI handles it). |

## Best Practices

### Prompt Design

- **Be specific**: Tell Claude exactly what to investigate and how to report the findings
- **Give context**: Include the relevant event data in the prompt
- **Define outputs**: Specify the format you want for results (markdown, JSON, and similar)
- **Set boundaries**: State clearly which actions Claude must NOT take

### Resource Limits

- **Set max_turns**: Stop sessions that run away and use too many resources
- **Set max_budget_usd**: Cap costs for each session
- **Use ttl_seconds**: Stop long sessions automatically

### Security

- **Store secrets in Hive**: Never hardcode API keys in D&R rules
- **Limit tools**: Allow only the tools that Claude needs for the task
- **Use denied_tools**: Block dangerous tools explicitly for sensitive operations
- **Restrict MCP access**: Configure only the MCP servers that you need

### Deduplication and Serialization

- **Use idempotent_key**: Stop duplicate sessions for the same event
- **Use debounce_key**: Serialize sessions so that only one runs at a time for each key. Queued requests start again when the active session completes
- **Include unique identifiers**: Use `detect_id`, `this` atom, or similar unique values
- **Combine with suppression**: Use D&R suppression to limit how often LimaCharlie starts sessions

## Troubleshooting

### Session Not Starting

- Check that the Anthropic API key is valid and stored correctly in Hive Secrets
- Check that the D&R rule is enabled and matches events
- Review the D&R rule syntax for errors

### Session Failing

- Check that `max_turns` is not too low for the task
- Check the MCP server URLs and the authentication
- Review the session logs for error messages

### Unexpected Behavior

- Review the prompt for ambiguity
- Check that `allowed_tools` includes the necessary tools
- Check that `denied_tools` does not block a necessary capability

## See Also

- [Compliance Case-Reviewer Agent](compliance/case-reviewer-agent.md) -- A production example of a D&R-driven session. It classifies every new case against framework control citations on `case_created` events. Use it as a reference for prompt structure, scope-check patterns, debounce keys, and case-write workflows.
- [Tool Permissions & Profiles](tool-permissions.md) -- Configure `allowed_tools` / `denied_tools` for D&R sessions.
- [Runner Environment](runner-environment.md) -- What is pre-installed in the session container.
- [Alternative AI Providers](alternative-providers.md) -- Route through AWS Bedrock or Google Cloud Vertex AI instead of Anthropic direct.
