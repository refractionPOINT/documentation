# User AI Sessions

User AI Sessions give you interactive access to Claude AI through the LimaCharlie web app or the API. D&R-driven sessions run automatically, but you start a user session manually. A user session gives real-time, bidirectional communication with Claude.

## Overview

User sessions give you:

- **Interactive Claude Code**: Full Claude Code capabilities in a cloud-hosted environment
- **Real-time communication**: WebSocket-based streaming of responses and tool usage
- **Session management**: Create, list, and manage many sessions
- **File transfer**: Upload files to session workspaces and download files from them
- **Profiles**: Save and reuse session configurations

## Getting Started

### Step 1: Registration

You must register before you use AI Sessions. LimaCharlie users with approved email domains can register.

**In the web app:**
Go to the AI Sessions section in the LimaCharlie web app. Click "Register".

**With the API:**

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/register \
  -H "Authorization: Bearer $LC_JWT"
```

### Step 2: Store Claude Credentials

AI Sessions uses a Bring Your Own Key (BYOK) model. You supply your Anthropic credentials: an API key, or Claude Max OAuth.

#### Option A: API Key

Store your Anthropic API key directly:

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/auth/claude/apikey \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-ant-api03-xxxxx"}'
```

> Note: API keys must start with `sk-ant-`.

#### Option B: Claude Max OAuth

If you have a Claude Max subscription, you can authenticate with OAuth:

1. Start the OAuth flow:

    ```bash
    curl -X POST https://ai-sessions.limacharlie.io/v1/auth/claude/start \
      -H "Authorization: Bearer $LC_JWT"
    ```

2. Poll for the authorization URL:

    ```bash
    curl https://ai-sessions.limacharlie.io/v1/auth/claude/url?session_id=<oauth_session_id> \
      -H "Authorization: Bearer $LC_JWT"
    ```

3. Open the URL in your browser and authorize.
4. Submit the authorization code:

    ```bash
    curl -X POST https://ai-sessions.limacharlie.io/v1/auth/claude/code \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/json" \
      -d '{"session_id": "<oauth_session_id>", "code": "<authorization_code>"}'
    ```

### Step 3: Create a Session

Create a session to start work with Claude:

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/sessions \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "allowed_tools": ["Bash", "Read", "Write", "Grep", "Glob"],
    "denied_tools": ["WebFetch"]
  }'
```

### Step 4: Connect via WebSocket

For real-time interaction, connect to the session with a WebSocket:

```javascript
const ws = new WebSocket(
  'wss://ai-sessions.limacharlie.io/v1/sessions/{sessionId}/ws?token={jwt}'
);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log(msg.type, msg.payload);
};

// Send a prompt
ws.send(JSON.stringify({
  type: 'prompt',
  payload: { text: 'List all files in the current directory' }
}));
```

!!! tip "Chat from the terminal"
    The `limacharlie ai chat` command in the LimaCharlie CLI starts a user session and opens the interactive chat. You do not send a manual `POST /v1/sessions` and you do not bring up a WebSocket. First, run `limacharlie ai auth claude login` (or `set-key`) one time to register your Anthropic credential. See [Command Line Interface](cli.md#limacharlie-ai-chat) for the full flag set. To attach again to a session that you started earlier, use `ai session attach --id <SESSION_ID> --interactive`.

## Session Profiles

Profiles let you save and reuse session configurations. You can have a maximum of 10 profiles, and one of them is the default.

### Creating a Profile

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/profiles \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Investigation",
    "description": "Profile for security investigations",
    "allowed_tools": ["Bash", "Read", "Grep", "Glob", "WebFetch"],
    "denied_tools": ["Write", "Edit"],
    "permission_mode": "acceptEdits",
    "max_turns": 100,
    "max_budget_usd": 10.0
  }'
```

### Profile Options

| Option | Type | Description |
|--------|------|-------------|
| `name` | string | Profile name (max 100 characters) |
| `description` | string | Profile description (max 500 characters) |
| `allowed_tools` | list | Tools that Claude can use. See [Tool Permissions & Profiles](tool-permissions.md) for the full pattern grammar. |
| `denied_tools` | list | Tools that Claude cannot use. Always wins over `allowed_tools`. See [Tool Permissions & Profiles](tool-permissions.md). |
| `permission_mode` | string | `acceptEdits`, `plan`, or `bypassPermissions`. See [Tool Permissions & Profiles](tool-permissions.md#permission_mode). |
| `model` | string | Claude model to use |
| `max_turns` | integer | Maximum conversation turns |
| `max_budget_usd` | float | Maximum spend limit in USD |
| `one_shot` | boolean | When `true`, the session ends after its initial work. Default: `false` for user sessions. |
| `ttl_seconds` | integer | Maximum session lifetime in seconds |
| `environment` | map | Environment variables passed to the session |
| `mcp_servers` | map | Configurations for external MCP servers. The auto-installed `limacharlie` CLI gives LimaCharlie access, so it needs no entry here. |

### Setting a Default Profile

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/profiles/{profileId}/default \
  -H "Authorization: Bearer $LC_JWT"
```

### Capturing Settings from a Session

You can create a profile from the settings of an existing session:

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/sessions/{sessionId}/capture-profile \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Session Config"}'
```

## Session Lifecycle

### What you see: Running / Waiting / Ended

In the web app — the sidebar, session lists, the live grid, and the chat header — a
session shows one of three states, with an optional **needs-attention** flag:

| State | Meaning |
|-------|---------|
| **Running** | The agent works: it thinks, runs tools, or recovers. |
| **Waiting** | The session is alive but idle. It waits for your next prompt, is asleep but resumable, or is blocked on a tool approval or question with no answer. |
| **Ended** | The session is finished. The `end_reason` says why — see [End Reasons](#end-reasons) below. |

**Needs attention** — when a Running or Waiting session is blocked on a tool approval
or on a question with no answer, the badge shows a trailing alert marker. If you
send a prompt to a blocked session, the chat shows a "message queued" notice with a
button that scrolls the pending request into view.

### Hibernation

Idle sessions are **hibernated** automatically. The workspace is archived and the
session becomes **dormant**. A dormant session has a storage cost but **zero
compute** cost until you send a new message, and it then resumes. For you, the
session stays "Waiting" the whole time and continues from the same point, because
the conversation and the working files are restored on resume.

### Forking

You can **fork** a dormant or ended session into a new session inside its retention
window. The fork inherits the **conversation context** of the source, but it starts
with the **profile of the user who forks it**, and with the tools and capabilities of
that profile. A fork preflight reports if the source is forkable, and which MCP
servers of the source your profiles do not have, so you can acknowledge them before
you fork.

### Resource limits

Some [Profile Options](#profile-options) end a session automatically. `max_turns`
ends the session after a count of turns. `max_budget_usd` ends it when the total
Claude cost goes above the cap. `one_shot` ends it after the initial task.
`ttl_seconds` sets the session lifetime, with a maximum of 24 hours. A platform
maximum for session duration, set by the tier of your organization, also applies.
When the session reaches one of these limits, it moves to `ended` with the matching
`end_reason` below.

### End Reasons

When a session enters the `ended` state, the `end_reason` field shows why:

| Reason | Description |
|--------|-------------|
| `completed` | Session completed its task normally |
| `failed` | Session encountered an execution error |
| `job_completed` | Session runner process exited |
| `user_requested` | User terminated the session |
| `org_api_requested` | The org API terminated the session |
| `max_duration_exceeded` | Session exceeded its maximum duration |
| `startup_timeout` | Session failed to start within the allowed time |
| `heartbeat_stale` | Lost connection to the session runner |

### Terminating a Session

```bash
curl -X DELETE https://ai-sessions.limacharlie.io/v1/sessions/{sessionId} \
  -H "Authorization: Bearer $LC_JWT"
```

### Deleting Session Records

After you terminate a session, you can delete its record:

```bash
curl -X DELETE https://ai-sessions.limacharlie.io/v1/sessions/{sessionId}/record \
  -H "Authorization: Bearer $LC_JWT"
```

## File Transfer

### Uploading Files

1. Request an upload URL:

    ```bash
    curl -X POST https://ai-sessions.limacharlie.io/v1/io/sessions/{sessionId}/upload \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/json" \
      -d '{
        "filename": "data.csv",
        "content_type": "text/csv",
        "size": 1024
      }'
    ```

2. Upload the file to the signed URL:

    ```bash
    curl -X PUT "{upload_url}" \
      -H "Content-Type: text/csv" \
      --data-binary @data.csv
    ```

3. Report that the upload is complete:

    ```bash
    curl -X POST https://ai-sessions.limacharlie.io/v1/io/sessions/{sessionId}/upload/complete \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/json" \
      -d '{"upload_id": "{upload_id}"}'
    ```

The file is then available in the session at the `target_path` from step 1.

### Downloading Files

1. Request a download URL:

    ```bash
    curl -X POST https://ai-sessions.limacharlie.io/v1/io/sessions/{sessionId}/download \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/json" \
      -d '{"path": "/workspace/output.txt"}'
    ```

2. Download the file from the signed URL:

    ```bash
    curl -o output.txt "{download_url}"
    ```

### File Size Limits

- Maximum file size: 100 MB
- Maximum message size (WebSocket): 1 MB

## Use Cases

### Interactive Threat Investigation

Use Claude to investigate a security incident step by step:

```text
You: I need to investigate suspicious activity on sensor abc123.
     The user reported strange popup windows.

Claude: I'll investigate this sensor. Let me start by gathering some
        context about the sensor and recent events.

        [Uses LimaCharlie tools to query sensor info and events]

        I found several suspicious indicators:
        1. A new process "update.exe" started from a temp directory
        2. Multiple outbound connections to an unknown IP
        3. Registry modifications for persistence

        Would you like me to investigate any of these in more detail?
```

### Ad-hoc Analysis

Do quick analysis tasks:

```text
You: Analyze this list of IP addresses and tell me which ones
     appear in threat intelligence feeds.

Claude: I'll analyze each IP address against available threat
        intelligence sources.

        [Checks each IP against VirusTotal, AbuseIPDB, etc.]

        Results:
        - 192.168.1.1: Clean (internal)
        - 45.33.32.156: Malicious - Known C2 server
        - 8.8.8.8: Clean (Google DNS)
```

### Learning and Exploration

Explore your LimaCharlie environment:

```text
You: Show me how to create a D&R rule that detects PowerShell
     downloading files from the internet.

Claude: Here's how to create a D&R rule for detecting PowerShell
        web downloads:

        [Provides detailed explanation with examples]
```

## Best Practices

### Session Management

- **Terminate when done**: Idle sessions are hibernated automatically to save resources, but terminate the sessions that you no longer need
- **Use profiles**: Save common configurations for quick session creation
- **Set resource limits**: Use `max_turns` and `max_budget_usd` to control costs
- **Expect resume latency**: After a period with no activity, your session can be hibernated. The first message after hibernation can take longer, because the session resumes first

### Security

- **Limit tool access**: Enable only the tools that your task needs
- **Review tool usage**: Monitor which actions Claude does
- **Be careful with Write/Edit**: These tools can change files

### Performance

- **Keep prompts focused**: Specific, clear prompts get better results
- **Upload files for large data**: Use file transfer instead of a paste into a prompt
- **Use heartbeats**: Keep WebSocket connections alive with regular heartbeats

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Registration requests | 10/minute per user |
| Session creation | 10/minute per user |
| Maximum concurrent sessions | 10 per user |
| WebSocket messages | 100/second per connection |
| Prompts | 60/minute per session |
| File uploads | 10/minute per session |

## Troubleshooting

### Cannot Register

- Check that your email domain is in the allowed list
- Check that your JWT token is valid
- Contact support if the problem continues

### Cannot Create Session

- Make sure that you stored Claude credentials
- Check that you are below the maximum session limit (10)
- Check that your profile configuration is valid

### WebSocket Connection Issues

- Use the query parameter for the JWT if the header does not work
- Send heartbeats every 30 seconds to keep the connection alive
- Check the session status—the connection works only for `running` sessions

### Session Crashes

- Check that the session is below `max_turns`
- Read the error message in the session details
- Make sure that the MCP server configurations are correct
