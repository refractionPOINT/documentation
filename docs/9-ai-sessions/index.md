# AI Sessions

LimaCharlie AI Sessions brings Claude, the advanced AI assistant from Anthropic, directly into your security operations. With AI Sessions, you use AI for automated incident investigation, threat hunting, and response actions — all in the context of your LimaCharlie organization.

## Overview

AI Sessions gives you two complementary ways to use Claude AI:

### D&R-Driven Sessions

Start AI sessions automatically in response to detections, events, or any condition that a Detection & Response rule matches. Use cases include:

- **Automated incident triage**: When a detection fires, Claude investigates the alert, collects context, and produces a summary report
- **Threat hunting**: Investigate patterns of suspicious activity automatically
- **Enrichment**: Use Claude to correlate data from many sources
- **Response automation**: Generate recommendations or take automated actions
- **Compliance classification**: Classify in-scope cases against framework controls (PCI DSS, HIPAA, CMMC, SOC 2, NIST 800-53, ISO 27001, CIS v8) and write audit-grade documentation directly into the case record. See [Compliance](compliance/index.md).

[Learn more about D&R-Driven Sessions](dr-sessions.md)

### User Sessions

Interactive AI sessions that you access through the web app or the API. Use cases include:

- **Ad-hoc investigation**: Investigate incidents interactively with help from Claude
- **Learning and exploration**: Explore your environment and learn about security concepts
- **Custom analysis**: Do complex analysis tasks with the full capabilities of Claude Code

[Learn more about User Sessions](user-sessions.md)

## Key Features

| Feature | D&R-Driven Sessions | User Sessions |
|---------|---------------------|---------------|
| **Trigger** | Automatic (D&R rules) | Manual (UI/API) |
| **Authentication** | Org API key + Anthropic secret | User JWT + stored credentials |
| **Interaction** | Fire-and-forget | Real-time WebSocket |
| **Use case** | Automation | Investigation |
| **Idempotency** | Supported | N/A |
| **Debouncing** | Supported | N/A |

## How It Works

AI Sessions runs fully-managed Claude Code instances in isolated cloud environments. Each session:

1. **Receives a prompt** with context (event data, detection details, or user input)
2. **Runs autonomously** with the tool capabilities of Claude (Bash, file operations, web fetch, and more)
3. **Connects to external data** through the LimaCharlie CLI, MCP servers, or other configured tools
4. **Returns results** as a final summary or as a real-time stream

For the platform layers, the isolation model, and data residency, see [Architecture](architecture.md).

## Getting Started

### For D&R-Driven Sessions

1. Store your Anthropic API key in a [Hive Secret](../7-administration/config-hive/secrets.md)
2. Create a D&R rule with the `start ai agent` action
3. Configure the prompt and the optional profile settings

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: mimikatz

respond:
  - action: report
    name: suspicious-process-detected
  - action: start ai agent
    prompt: |
      Investigate this suspicious process detection.
      Analyze the process tree, network connections, and file activity.
      Provide a summary of findings and recommended actions.
    anthropic_secret: hive://secret/anthropic-key
    lc_api_key_secret: hive://secret/lc-api-key
```

### For User Sessions

1. [Register](user-sessions.md#step-1-registration) for AI Sessions
2. Store your Anthropic credentials (API key or OAuth)
3. Create a session and start to interact with it

## Documentation

- [Grid: Your AI Field Engineer](grid.md) - The guided, outcome-first way to use AI Sessions
- [Architecture](architecture.md) - How the platform is organized, the isolation model
- [D&R-Driven Sessions](dr-sessions.md) - Automated sessions that D&R rules trigger
- [User Sessions](user-sessions.md) - Interactive sessions through the web app or the API, including the session lifecycle
- [Tool Permissions & Profiles](tool-permissions.md) - How `allowed_tools`, `denied_tools`, and `permission_mode` work
- [Runner Environment](runner-environment.md) - CLI tools, language runtimes, and reference data pre-installed in the session container
- [Rich Cards & Slash Commands](rich-cards.md) - Interactive cards that the agent renders inline, and the `/` commands that call them
- [AI Skills](skills.md) - Reusable Claude Code skill definitions stored in your org
- [AI Memory](memory.md) - Per-agent persistent memory with partial-merge writes
- [API Reference](api-reference.md) - REST API and WebSocket protocol
- [Cost Tracking & Savings](cost-tracking.md) - AI spend, analyst-equivalent value, and net savings measured from your case resolution mix
- [Compliance](compliance/index.md) - The `lc-compliance` Claude Code plugin: case-reviewer agents for each framework (D&R-driven), plus four interactive skills for control lookups, gap analysis, and guided deploy

## Billing

LimaCharlie bills AI Sessions usage on:

- **Session runtime**: Per-minute charges for active sessions
- **Claude API usage**: Passed through from your Anthropic account (Bring Your Own Key model)

Because you supply your own Anthropic API key, Anthropic bills the Claude API costs directly to your account.

To track what your AI agents spend and the analyst work that they took on, see [Cost Tracking & Savings](cost-tracking.md). That page also gives the net savings against the cost to do the same investigations by hand. To set a hard limit on what one session can spend, set `max_budget_usd` (see [D&R-Driven Sessions](dr-sessions.md)).

## Privacy & Security

- **Bring Your Own Key**: You supply your own Anthropic API key. LimaCharlie never has access to your Claude conversations
- **Isolated execution**: Each session runs in an isolated container
- **Encrypted storage**: LimaCharlie encrypts credentials at rest with AES-256-GCM
- **No training**: Neither LimaCharlie nor Anthropic uses your data for model training
