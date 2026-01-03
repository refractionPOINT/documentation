# API Reference

This document provides a complete reference for the AI Sessions REST API and WebSocket protocol.

## Base URL

| Environment | URL |
|-------------|-----|
| Production | `https://ai-sessions.limacharlie.io` |
| Staging | `https://ai-sessions-staging.limacharlie.io` |

## Authentication

All API requests require a valid LimaCharlie JWT token in the Authorization header:

```
Authorization: Bearer <LC-JWT>
```

For WebSocket connections, you can also pass the token as a query parameter:

```
wss://ai-sessions.limacharlie.io/v1/sessions/{sessionId}/ws?token=<LC-JWT>
```

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Registration | 10 requests/minute per user |
| Session creation | 10 requests/minute per user |
| WebSocket messages | 100 messages/second per connection |

---

## REST API Endpoints

### Registration

#### Register User

```
POST /v1/register
```

Register the authenticated user for the AI Sessions platform.

**Response: 200 OK**
```json
{
  "registered": true,
  "registered_at": "2025-01-15T10:30:00Z"
}
```

**Error Responses:**
- `401`: Invalid or missing JWT token
- `403`: Email domain not in allowed list
- `409`: User already registered

#### Deregister User

```
DELETE /v1/register
```

Deregister the user and delete all associated data. This terminates all active sessions and deletes stored credentials.

**Response: 200 OK**
```json
{
  "deregistered": true
}
```

---

### Sessions

#### List Sessions

```
GET /v1/sessions
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `pending`, `running`, `terminated`, `failed` |
| `limit` | integer | Max results (default 50, max 200) |
| `cursor` | string | Pagination cursor |

**Response: 200 OK**
```json
{
  "sessions": [
    {
      "id": "abc123",
      "status": "running",
      "region": "us-central1",
      "created_at": "2025-01-15T10:30:00Z",
      "started_at": "2025-01-15T10:30:05Z",
      "lc_auth_type": "jwt",
      "allowed_tools": ["Bash", "Read"],
      "denied_tools": ["Write"]
    }
  ],
  "next_cursor": "xyz789"
}
```

#### Create Session

```
POST /v1/sessions
```

**Request Body:**
```json
{
  "lc_credentials": {
    "type": "org_api_key",
    "org_api_key": "xxxxxxxx"
  },
  "allowed_tools": ["Bash", "Read", "Write"],
  "denied_tools": ["WebFetch"]
}
```

**Response: 201 Created**
```json
{
  "session": {
    "id": "abc123",
    "status": "pending",
    "region": "us-central1",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

**Error Responses:**
- `400`: Invalid request body
- `403`: Not registered or no Claude credentials
- `409`: Maximum concurrent sessions (10) reached

#### Get Session

```
GET /v1/sessions/{sessionId}
```

**Response: 200 OK**
```json
{
  "session": {
    "id": "abc123",
    "status": "running",
    "region": "us-central1",
    "created_at": "2025-01-15T10:30:00Z",
    "started_at": "2025-01-15T10:30:05Z",
    "terminated_at": null,
    "termination_reason": null,
    "exit_code": null,
    "error_message": null,
    "allowed_tools": ["Bash", "Read"],
    "denied_tools": ["Write"]
  }
}
```

#### Terminate Session

```
DELETE /v1/sessions/{sessionId}
```

**Response: 200 OK**
```json
{
  "terminated": true
}
```

#### Delete Session Record

```
DELETE /v1/sessions/{sessionId}/record
```

Delete a terminated session from history. Only terminated or failed sessions can be deleted.

**Response: 200 OK**
```json
{
  "deleted": true
}
```

---

### Profiles

#### List Profiles

```
GET /v1/profiles
```

**Response: 200 OK**
```json
{
  "profiles": [
    {
      "id": "profile123",
      "name": "Investigation",
      "description": "Profile for security investigations",
      "is_default": true,
      "allowed_tools": ["Bash", "Read"],
      "denied_tools": ["Write"],
      "permission_mode": "acceptEdits",
      "model": "claude-sonnet-4-20250514",
      "max_turns": 100,
      "max_budget_usd": 10.0,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

#### Create Profile

```
POST /v1/profiles
```

**Request Body:**
```json
{
  "name": "Investigation",
  "description": "Profile for security investigations",
  "allowed_tools": ["Bash", "Read", "Grep"],
  "denied_tools": ["Write", "Edit"],
  "permission_mode": "acceptEdits",
  "model": "claude-sonnet-4-20250514",
  "max_turns": 100,
  "max_budget_usd": 10.0,
  "mcp_servers": {
    "limacharlie": {
      "type": "http",
      "url": "https://mcp.limacharlie.io",
      "headers": {
        "Authorization": "Bearer token"
      }
    }
  },
  "is_default": false
}
```

**Response: 201 Created**
```json
{
  "profile": {
    "id": "profile123",
    "name": "Investigation",
    ...
  }
}
```

**Error Responses:**
- `400`: Invalid request body
- `409`: Maximum profiles (10) reached

#### Get Profile

```
GET /v1/profiles/{profileId}
```

#### Update Profile

```
PUT /v1/profiles/{profileId}
```

#### Delete Profile

```
DELETE /v1/profiles/{profileId}
```

> Note: The default profile cannot be deleted.

#### Set Default Profile

```
POST /v1/profiles/{profileId}/default
```

#### Capture Session as Profile

```
POST /v1/sessions/{sessionId}/capture-profile
```

**Request Body:**
```json
{
  "name": "My Session Config",
  "description": "Captured from session abc123"
}
```

---

### Claude Authentication

#### Start OAuth Flow

```
POST /v1/auth/claude/start
```

**Response: 200 OK**
```json
{
  "oauth_session_id": "oauth123",
  "expires_in": 300,
  "message": "Poll /auth/claude/url for the OAuth URL"
}
```

#### Get OAuth URL

```
GET /v1/auth/claude/url?session_id={oauth_session_id}
```

**Response: 200 OK (URL Ready)**
```json
{
  "status": "url_ready",
  "url": "https://console.anthropic.com/oauth/authorize?...",
  "message": "Visit the URL to authorize"
}
```

**Response: 200 OK (Pending)**
```json
{
  "status": "pending",
  "message": "Waiting for OAuth URL to be generated"
}
```

#### Submit OAuth Code

```
POST /v1/auth/claude/code
```

**Request Body:**
```json
{
  "session_id": "oauth123",
  "code": "authorization_code_from_anthropic"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "status": "completed",
  "message": "Claude credentials stored successfully"
}
```

#### Store API Key

```
POST /v1/auth/claude/apikey
```

**Request Body:**
```json
{
  "api_key": "sk-ant-api03-xxxxx"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "message": "API key stored successfully"
}
```

#### Get Credential Status

```
GET /v1/auth/claude/status
```

**Response: 200 OK**
```json
{
  "has_credentials": true,
  "credential_type": "api_key",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Delete Credentials

```
DELETE /v1/auth/claude
```

---

### File Transfer

#### Request Upload URL

```
POST /v1/io/sessions/{sessionId}/upload
```

**Request Body:**
```json
{
  "filename": "data.csv",
  "content_type": "text/csv",
  "size": 1024
}
```

**Response: 200 OK**
```json
{
  "upload_url": "https://storage.googleapis.com/...",
  "upload_id": "upload123",
  "target_path": "/workspace/uploads/data.csv",
  "expires_at": "2025-01-15T11:30:00Z"
}
```

**Error Responses:**
- `413`: File size exceeds limit (100 MB)

#### Notify Upload Complete

```
POST /v1/io/sessions/{sessionId}/upload/complete
```

**Request Body:**
```json
{
  "upload_id": "upload123"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "path": "/workspace/uploads/data.csv"
}
```

#### Request Download URL

```
POST /v1/io/sessions/{sessionId}/download
```

**Request Body:**
```json
{
  "path": "/workspace/output.txt"
}
```

**Response: 200 OK**
```json
{
  "download_url": "https://storage.googleapis.com/...",
  "expires_at": "2025-01-15T11:30:00Z"
}
```

---

## WebSocket Protocol

### Connection

**Endpoint:**
```
wss://ai-sessions.limacharlie.io/v1/sessions/{sessionId}/ws
```

**Authentication:**
- Header: `Authorization: Bearer <JWT>`
- Query parameter: `?token=<JWT>`

### Connection Errors

| Code | Description |
|------|-------------|
| 4001 | Invalid or missing authentication |
| 4003 | Session belongs to different user |
| 4004 | Session not found |
| 4009 | Session not running |
| 4100 | Session ended |
| 4101 | Connection reset |
| 4500 | Internal error |

### Message Format

All messages are JSON objects:

```json
{
  "type": "message_type",
  "timestamp": "2025-01-15T10:30:00Z",
  "session_id": "abc123",
  "payload": { ... }
}
```

---

### Client to Server Messages

#### prompt

Send a user prompt to Claude.

```json
{
  "type": "prompt",
  "payload": {
    "text": "List all files in the current directory"
  }
}
```

#### interrupt

Interrupt the current Claude operation.

```json
{
  "type": "interrupt"
}
```

#### heartbeat

Keep the connection alive (send every 30 seconds).

```json
{
  "type": "heartbeat"
}
```

#### upload_request

Request a signed URL for file upload.

```json
{
  "type": "upload_request",
  "payload": {
    "request_id": "req_123",
    "filename": "data.csv",
    "content_type": "text/csv",
    "size": 1024
  }
}
```

#### upload_complete

Notify that file upload has completed.

```json
{
  "type": "upload_complete",
  "payload": {
    "request_id": "req_123",
    "filename": "data.csv",
    "path": "/workspace/uploads/data.csv"
  }
}
```

#### download_request

Request a signed URL for file download.

```json
{
  "type": "download_request",
  "payload": {
    "request_id": "req_456",
    "path": "/workspace/output.txt"
  }
}
```

---

### Server to Client Messages

#### assistant

Claude's response content.

```json
{
  "type": "assistant",
  "timestamp": "2025-01-15T10:30:00Z",
  "payload": {
    "content": [
      {
        "type": "text",
        "text": "Here are the files in the current directory:\n\n- file1.txt\n- file2.py"
      }
    ],
    "model": "claude-sonnet-4-20250514"
  }
}
```

#### tool_use

Claude is invoking a tool.

```json
{
  "type": "tool_use",
  "timestamp": "2025-01-15T10:30:01Z",
  "payload": {
    "id": "tool_abc123",
    "name": "Bash",
    "input": {
      "command": "ls -la"
    }
  }
}
```

#### tool_result

Result of a tool execution.

```json
{
  "type": "tool_result",
  "timestamp": "2025-01-15T10:30:02Z",
  "payload": {
    "tool_use_id": "tool_abc123",
    "content": "total 16\ndrwxr-xr-x 2 user user 4096 Jan 15 10:00 .\n..."
  }
}
```

#### user

Echo of user input (for display purposes).

```json
{
  "type": "user",
  "timestamp": "2025-01-15T10:30:00Z",
  "payload": {
    "text": "List all files in the current directory"
  }
}
```

#### system

System messages from Claude.

```json
{
  "type": "system",
  "timestamp": "2025-01-15T10:30:00Z",
  "payload": {
    "message": "Working directory: /workspace"
  }
}
```

#### result

Final result of a Claude operation.

```json
{
  "type": "result",
  "timestamp": "2025-01-15T10:35:00Z",
  "payload": {
    "success": true,
    "summary": "Listed directory contents successfully"
  }
}
```

#### session_status

Session status update.

```json
{
  "type": "session_status",
  "timestamp": "2025-01-15T10:30:00Z",
  "payload": {
    "status": "running"
  }
}
```

#### session_end

Session has terminated.

```json
{
  "type": "session_end",
  "timestamp": "2025-01-15T10:35:00Z",
  "payload": {
    "reason": "completed",
    "exit_code": 0
  }
}
```

**Termination Reasons:**
- `completed`: Session completed normally
- `user_requested`: User terminated the session
- `timeout`: Session timed out
- `process_crashed`: Claude process crashed
- `cancelled`: Session was cancelled

#### session_error

An error occurred in the session.

```json
{
  "type": "session_error",
  "timestamp": "2025-01-15T10:35:00Z",
  "payload": {
    "error": "Claude process died unexpectedly",
    "details": "Exit code: 1"
  }
}
```

#### error

General error message.

```json
{
  "type": "error",
  "timestamp": "2025-01-15T10:35:00Z",
  "payload": {
    "message": "Rate limit exceeded",
    "code": "rate_limited"
  }
}
```

**Error Codes:**
- `session_not_found`: Session no longer exists
- `session_not_running`: Session is not in running state
- `session_crashed`: Session process crashed
- `invalid_message`: Malformed message received
- `rate_limited`: Too many messages sent

#### upload_url

Response to upload_request.

```json
{
  "type": "upload_url",
  "timestamp": "2025-01-15T10:30:00Z",
  "payload": {
    "request_id": "req_123",
    "upload_id": "upload_789",
    "url": "https://storage.googleapis.com/...",
    "target_path": "/workspace/uploads/data.csv",
    "expires_at": "2025-01-15T11:30:00Z"
  }
}
```

#### download_url

Response to download_request.

```json
{
  "type": "download_url",
  "timestamp": "2025-01-15T10:30:00Z",
  "payload": {
    "request_id": "req_456",
    "url": "https://storage.googleapis.com/...",
    "expires_at": "2025-01-15T11:30:00Z"
  }
}
```

---

## Connection Management

### Heartbeat

- **Client**: Send `heartbeat` message every 30 seconds
- **Server**: Sends WebSocket ping frames every 30 seconds
- **Timeout**: Connection closed after 60 seconds of inactivity

### Reconnection

If the connection is lost:

1. Reconnect using the same session ID
2. Server sends any buffered messages (up to 60 seconds old)
3. If session has ended, server sends `session_end` message

### Message Size

Maximum message size is 1 MB. Use file transfer for larger payloads.

---

## Example: Complete Session Flow

```javascript
const jwt = 'your-limacharlie-jwt';
const baseUrl = 'https://ai-sessions.limacharlie.io';

// 1. Create session
const createResp = await fetch(`${baseUrl}/v1/sessions`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwt}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    allowed_tools: ['Bash', 'Read', 'Write']
  })
});
const { session } = await createResp.json();

// 2. Wait for session to be running
let status = 'pending';
while (status === 'pending') {
  await new Promise(r => setTimeout(r, 1000));
  const resp = await fetch(`${baseUrl}/v1/sessions/${session.id}`, {
    headers: { 'Authorization': `Bearer ${jwt}` }
  });
  const data = await resp.json();
  status = data.session.status;
}

// 3. Connect via WebSocket
const ws = new WebSocket(
  `wss://ai-sessions.limacharlie.io/v1/sessions/${session.id}/ws?token=${jwt}`
);

// 4. Set up heartbeat
const heartbeat = setInterval(() => {
  ws.send(JSON.stringify({ type: 'heartbeat' }));
}, 30000);

// 5. Handle messages
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  switch (msg.type) {
    case 'assistant':
      console.log('Claude:', msg.payload.content);
      break;
    case 'tool_use':
      console.log('Using tool:', msg.payload.name);
      break;
    case 'tool_result':
      console.log('Tool result:', msg.payload.content);
      break;
    case 'session_end':
      console.log('Session ended:', msg.payload.reason);
      clearInterval(heartbeat);
      break;
    case 'error':
      console.error('Error:', msg.payload.message);
      break;
  }
};

// 6. Send a prompt
ws.send(JSON.stringify({
  type: 'prompt',
  payload: { text: 'Hello! List the files in the current directory.' }
}));

// 7. Later: interrupt if needed
// ws.send(JSON.stringify({ type: 'interrupt' }));

// 8. Cleanup
ws.onclose = () => {
  clearInterval(heartbeat);
};
```
