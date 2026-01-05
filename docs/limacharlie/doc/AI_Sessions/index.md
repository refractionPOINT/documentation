# AI Sessions

LimaCharlie AI Sessions brings the power of Claude, Anthropic's advanced AI assistant, directly into your security operations. AI Sessions enables you to leverage AI for automated incident investigation, threat hunting, and response actions—all within the context of your LimaCharlie organization.

## Overview

AI Sessions provides two complementary ways to use Claude AI:

### D&R-Driven Sessions

Automatically spawn AI sessions in response to detections, events, or any condition matched by a Detection & Response rule. Use cases include:

- **Automated incident triage**: When a detection fires, have Claude investigate the alert, gather context, and produce a summary report
- **Threat hunting**: Automatically investigate suspicious activity patterns
- **Enrichment**: Use Claude to correlate data from multiple sources via MCP servers
- **Response automation**: Generate recommendations or take automated actions

[Learn more about D&R-Driven Sessions](dr-sessions.md)

### User Sessions

Interactive AI sessions accessed through the web interface or API. Use cases include:

- **Ad-hoc investigation**: Interactively investigate incidents with Claude's help
- **Learning and exploration**: Explore your environment and learn about security concepts
- **Custom analysis**: Perform complex analysis tasks with full Claude Code capabilities

[Learn more about User Sessions](user-sessions.md)

## Key Features

| Feature | D&R-Driven Sessions | User Sessions |
|---------|---------------------|---------------|
| **Trigger** | Automatic (D&R rules) | Manual (UI/API) |
| **Authentication** | Org API key + Anthropic secret | User JWT + stored credentials |
| **Interaction** | Fire-and-forget | Real-time WebSocket |
| **Use case** | Automation | Investigation |
| **Idempotency** | Supported | N/A |

## How It Works

AI Sessions runs fully-managed Claude Code instances in isolated cloud environments. Each session:

1. **Receives a prompt** with context (event data, detection details, or user input)
2. **Executes autonomously** using Claude's tool capabilities (Bash, file operations, web fetch, etc.)
3. **Connects to external data** via MCP servers (LimaCharlie API, threat intel, etc.)
4. **Returns results** either as a final summary or streamed in real-time

## Getting Started

### For D&R-Driven Sessions

1. Store your Anthropic API key in a [Hive Secret](../Platform_Management/Config_Hive/config-hive-secrets.md)
2. Create a D&R rule with the `start ai session` action
3. Configure the prompt and optional profile settings

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: mimikatz

respond:
  - action: report
    name: suspicious-process-detected
  - action: start ai session
    prompt: |
      Investigate this suspicious process detection.
      Analyze the process tree, network connections, and file activity.
      Provide a summary of findings and recommended actions.
    anthropic_secret: hive://secret/anthropic-key
    lc_api_key_secret: hive://secret/lc-api-key
```

### For User Sessions

1. [Register](user-sessions.md#registration) for AI Sessions
2. Store your Anthropic credentials (API key or OAuth)
3. Create a session and start interacting

## Documentation

- [D&R-Driven Sessions](dr-sessions.md) - Automated sessions triggered by D&R rules
- [User Sessions](user-sessions.md) - Interactive sessions via web UI or API
- [API Reference](api-reference.md) - REST API and WebSocket protocol
- [TypeScript SDK](sdk.md) - SDK for programmatic access

## Billing

AI Sessions usage is billed based on:

- **Session runtime**: Per-minute charges for active sessions
- **Claude API usage**: Passed through from your Anthropic account (Bring Your Own Key model)

Since you provide your own Anthropic API key, Claude API costs are billed directly by Anthropic to your account.

## Privacy & Security

- **Bring Your Own Key**: You provide your own Anthropic API key; LimaCharlie never has access to your Claude conversations
- **Isolated execution**: Each session runs in an isolated container
- **Encrypted storage**: Credentials are encrypted at rest using AES-256-GCM
- **No training**: Neither LimaCharlie nor Anthropic uses your data for model training
