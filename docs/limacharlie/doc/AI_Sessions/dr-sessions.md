# D&R-Driven AI Sessions

D&R-Driven AI Sessions allow you to automatically spawn Claude AI sessions in response to detections, events, or any condition matched by a Detection & Response rule. This enables powerful automated investigation, triage, and response workflows.

## Overview

When a D&R rule matches, the `start ai session` response action launches a Claude session with:

- A prompt containing the context you specify
- Access to tools and MCP servers you configure
- Optional event data extracted and included automatically

The session runs autonomously, performing the investigation or analysis you've defined, and the results can be captured via outputs or stored for later review.

## The `start ai session` Action

### Basic Syntax

```yaml
respond:
  - action: start ai session
    prompt: "Your instructions to Claude..."
    anthropic_secret: hive://secret/my-anthropic-key
```

### Required Parameters

| Parameter | Description |
|-----------|-------------|
| `prompt` | The instructions for Claude. Supports [template strings](../Events/template-strings-and-transforms.md) to include event data. |
| `anthropic_secret` | Your Anthropic API key. Use `hive://secret/<name>` to reference a [Hive Secret](../Platform_Management/Config_Hive/config-hive-secrets.md). |

### Optional Parameters

| Parameter | Description |
|-----------|-------------|
| `name` | Session name. Supports template strings. Useful for identifying sessions in logs. |
| `lc_api_key_secret` | LimaCharlie API key for org-level API access. Use `hive://secret/<name>`. |
| `idempotent_key` | Unique key to prevent duplicate sessions. Supports template strings. |
| `data` | Extract event data fields to include in the prompt as JSON. |
| `profile` | Inline session configuration (tools, model, limits, etc.). |
| `profile_name` | Reference a saved profile by name. |

> Note: You can specify either `profile` (inline) or `profile_name` (reference), but not both.

## Configuration Options

### Prompt Templating

The `prompt` parameter supports LimaCharlie's template syntax. You can include event data directly in your instructions:

```yaml
- action: start ai session
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
- action: start ai session
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

Prevent duplicate sessions for the same event using `idempotent_key`:

```yaml
- action: start ai session
  prompt: "Investigate this detection..."
  anthropic_secret: hive://secret/anthropic-key
  idempotent_key: "{{ .detect.detect_id }}"
```

If a session with the same idempotent key was recently created, the action is skipped.

### Session Profiles

Profiles let you configure Claude's behavior, available tools, and resource limits.

#### Inline Profile

```yaml
- action: start ai session
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
    one_shot: true  # Complete initial task then terminate
    ttl_seconds: 1800

    # Environment variables
    environment:
      LOG_LEVEL: debug
      API_KEY: hive://secret/external-api-key

    # MCP servers
    mcp_servers:
      limacharlie:
        type: http
        url: https://mcp.limacharlie.io
        headers:
          Authorization: hive://secret/lc-mcp-token
```

#### Profile Options

| Option | Type | Description |
|--------|------|-------------|
| `allowed_tools` | list | Tools Claude can use. If empty, all tools are allowed. |
| `denied_tools` | list | Tools Claude cannot use. Takes precedence over `allowed_tools`. |
| `permission_mode` | string | `acceptEdits` (default), `plan`, or `bypassPermissions` |
| `model` | string | Claude model to use (e.g., `claude-sonnet-4-20250514`) |
| `max_turns` | integer | Maximum conversation turns before auto-termination |
| `max_budget_usd` | float | Maximum spend limit in USD |
| `one_shot` | boolean | When `true`, session completes all work for the initial prompt (including tools, skills, and subagents) then terminates automatically. Recommended for D&R-triggered sessions. Default: `false` |
| `ttl_seconds` | integer | Maximum session lifetime in seconds |
| `environment` | map | Environment variables. Values can use `hive://secret/` |
| `mcp_servers` | map | MCP server configurations (see below) |

### MCP Server Configuration

MCP (Model Context Protocol) servers extend Claude's capabilities by providing additional data sources and tools.

#### HTTP MCP Server

```yaml
mcp_servers:
  limacharlie:
    type: http
    url: https://mcp.limacharlie.io
    headers:
      Authorization: hive://secret/lc-mcp-token
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

Automatically investigate when a suspicious process is detected:

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: -encodedcommand

respond:
  - action: report
    name: encoded-powershell-command
  - action: start ai session
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

### Example 2: Automated Triage with LimaCharlie MCP

Use the LimaCharlie MCP server to query additional context:

```yaml
detect:
  target: detection
  event: "*"
  op: is greater than
  path: priority
  value: 3

respond:
  - action: start ai session
    prompt: |
      A high-priority detection was triggered. Use the LimaCharlie MCP tools to:

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
      mcp_servers:
        limacharlie:
          type: http
          url: https://mcp.limacharlie.io
          headers:
            Authorization: hive://secret/lc-mcp-token
```

### Example 3: Threat Hunting Automation

Automatically investigate IoC matches from threat intelligence:

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: lookup/threat-domains

respond:
  - action: report
    name: threat-intel-domain-match
  - action: start ai session
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

Use external tools via MCP for enrichment:

```yaml
respond:
  - action: start ai session
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

## Best Practices

### Prompt Design

- **Be specific**: Tell Claude exactly what you want it to investigate and how to report findings
- **Provide context**: Include relevant event data in the prompt
- **Define outputs**: Specify the format you want for results (markdown, JSON, etc.)
- **Set boundaries**: Clearly state what actions Claude should NOT take

### Resource Limits

- **Set max_turns**: Prevent runaway sessions that consume excessive resources
- **Set max_budget_usd**: Cap costs for each session
- **Use ttl_seconds**: Automatically terminate long-running sessions

### Security

- **Store secrets in Hive**: Never hardcode API keys in D&R rules
- **Limit tools**: Only allow tools Claude needs for the task
- **Use denied_tools**: Explicitly block dangerous tools for sensitive operations
- **Restrict MCP access**: Only configure MCP servers that are necessary

### Deduplication

- **Use idempotent_key**: Prevent duplicate sessions for the same event
- **Include unique identifiers**: Use `detect_id`, `this` atom, or similar unique values
- **Combine with suppression**: Use D&R suppression to limit how often sessions are spawned

## Troubleshooting

### Session Not Starting

- Verify the Anthropic API key is valid and stored correctly in Hive Secrets
- Check that the D&R rule is enabled and matching events
- Review D&R rule syntax for errors

### Session Failing

- Check `max_turns` isn't too low for the task
- Verify MCP server URLs and authentication
- Review session logs for error messages

### Unexpected Behavior

- Review the prompt for ambiguity
- Check that `allowed_tools` includes necessary tools
- Verify `denied_tools` isn't blocking required capabilities
