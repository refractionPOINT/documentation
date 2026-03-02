# User AI Sessions

User AI Sessions provide interactive access to Claude AI through the LimaCharlie web interface or API. Unlike D&R-driven sessions that run automatically, user sessions are manually initiated and allow real-time, bidirectional communication with Claude.

## Overview

User sessions give you:

- **Interactive Claude Code**: Full Claude Code capabilities in a cloud-hosted environment
- **Real-time communication**: WebSocket-based streaming of responses and tool usage
- **Session management**: Create, list, and manage multiple sessions
- **File transfer**: Upload and download files to/from session workspaces
- **Profiles**: Save and reuse session configurations

## Getting Started

### Step 1: Registration

Before using AI Sessions, you must register. Registration is available to LimaCharlie users with approved email domains.

**Via Web UI:**
Navigate to the AI Sessions section in the LimaCharlie web console and click "Register".

**Via API:**
```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/register \
  -H "Authorization: Bearer $LC_JWT"
```

### Step 2: Store Claude Credentials

AI Sessions uses a Bring Your Own Key (BYOK) model. You provide your Anthropic credentials—either an API key or via Claude Max OAuth.

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

If you have a Claude Max subscription, you can authenticate via OAuth:

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

3. Visit the URL in your browser and authorize
4. Submit the authorization code:
```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/auth/claude/code \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<oauth_session_id>", "code": "<authorization_code>"}'
```

### Step 3: Create a Session

Create a new session to start working with Claude:

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

For real-time interaction, connect to the session via WebSocket:

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

## Session Profiles

Profiles let you save and reuse session configurations. You can have up to 10 profiles, with one designated as the default.

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
| `allowed_tools` | list | Tools Claude can use |
| `denied_tools` | list | Tools Claude cannot use |
| `permission_mode` | string | `acceptEdits`, `plan`, or `bypassPermissions` |
| `model` | string | Claude model to use |
| `max_turns` | integer | Maximum conversation turns |
| `max_budget_usd` | float | Maximum spend limit in USD |
| `mcp_servers` | map | MCP server configurations |

### Setting a Default Profile

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/profiles/{profileId}/default \
  -H "Authorization: Bearer $LC_JWT"
```

### Capturing Settings from a Session

You can create a new profile from an existing session's settings:

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/sessions/{sessionId}/capture-profile \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Session Config"}'
```

## Session Lifecycle

### Session States

| State | Description |
|-------|-------------|
| `pending` | Session is being created and provisioned |
| `running` | Session is active and accepting prompts |
| `terminated` | Session ended normally or was terminated by user |
| `failed` | Session encountered an error |

### Termination Reasons

| Reason | Description |
|--------|-------------|
| `user_requested` | User terminated the session |
| `completed` | Session completed its task |
| `process_crashed` | Claude process crashed unexpectedly |
| `timeout` | Session exceeded time limit |
| `cancelled` | Session was cancelled by the system |

### Terminating a Session

```bash
curl -X DELETE https://ai-sessions.limacharlie.io/v1/sessions/{sessionId} \
  -H "Authorization: Bearer $LC_JWT"
```

### Deleting Session Records

After a session is terminated, you can delete its record:

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

3. Notify that upload is complete:
```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/io/sessions/{sessionId}/upload/complete \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"upload_id": "{upload_id}"}'
```

The file will be available in the session at the `target_path` returned in step 1.

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

```
You: I need to investigate suspicious activity on sensor abc123.
     The user reported strange popup windows.

Claude: I'll investigate this sensor. Let me start by gathering some
        context about the sensor and recent events.

        [Uses LimaCharlie MCP to query sensor info and events]

        I found several suspicious indicators:
        1. A new process "update.exe" started from a temp directory
        2. Multiple outbound connections to an unknown IP
        3. Registry modifications for persistence

        Would you like me to investigate any of these in more detail?
```

### Ad-hoc Analysis

Perform quick analysis tasks:

```
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

```
You: Show me how to create a D&R rule that detects PowerShell
     downloading files from the internet.

Claude: Here's how to create a D&R rule for detecting PowerShell
        web downloads:

        [Provides detailed explanation with examples]
```

## Best Practices

### Session Management

- **Terminate idle sessions**: Sessions consume resources; terminate when done
- **Use profiles**: Save common configurations for quick session creation
- **Set resource limits**: Use `max_turns` and `max_budget_usd` to control costs

### Security

- **Limit tool access**: Only enable tools needed for your task
- **Review tool usage**: Monitor what actions Claude is taking
- **Be careful with Write/Edit**: These tools can modify files

### Performance

- **Keep prompts focused**: Specific, clear prompts get better results
- **Upload files for large data**: Use file transfer instead of pasting into prompts
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

- Verify your email domain is in the allowed list
- Check that your JWT token is valid
- Contact support if the issue persists

### Cannot Create Session

- Ensure you have Claude credentials stored
- Check you haven't exceeded the maximum session limit (10)
- Verify your profile configuration is valid

### WebSocket Connection Issues

- Use the query parameter for JWT if header doesn't work
- Send heartbeats every 30 seconds to keep connection alive
- Check session status—connection only works for `running` sessions

### Session Crashes

- Check `max_turns` isn't being exceeded
- Review the error message in session details
- Ensure MCP server configurations are correct
