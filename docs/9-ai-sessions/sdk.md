# TypeScript SDK

The `@limacharlie/ai-sessions` package provides a TypeScript SDK for interacting with the AI Sessions Platform.

## Installation

```bash
npm install @limacharlie/ai-sessions
# or
yarn add @limacharlie/ai-sessions
# or
pnpm add @limacharlie/ai-sessions
```

For Node.js environments, you also need the `ws` package:

```bash
npm install ws
```

## Quick Start

```typescript
import { createClient, createSessionWebSocket } from '@limacharlie/ai-sessions';

// Create REST client
const client = createClient({
  baseUrl: 'https://ai-sessions.limacharlie.io',
  token: 'your-limacharlie-jwt-token',
});

// Register user (first time only)
await client.register();

// Store your Anthropic API key
await client.storeAPIKey('sk-ant-api03-xxxxx');

// Create a session
const { session } = await client.createSession({
  allowed_tools: ['Bash', 'Read', 'Write'],
});
console.log('Session created:', session.id);

// Connect via WebSocket for real-time communication
const ws = createSessionWebSocket(
  client.getWebSocketURL(session.id),
  {
    onAssistant: (msg) => {
      console.log('Claude:', msg.content);
    },
    onToolUse: (msg) => {
      console.log('Tool:', msg.data.tool_name, msg.data.input);
    },
    onError: (err) => {
      console.error('Error:', err);
    },
    onSessionEnd: (msg) => {
      console.log('Session ended:', msg.data.reason);
    },
    onConnectionChange: (state) => {
      console.log('Connection:', state);
    },
  }
);

await ws.connect();

// Send a prompt
ws.sendPrompt('Hello! List the files in the current directory.');

// Later, disconnect
ws.disconnect();
```

## Features

- **REST API Client**: Full coverage of the AI Sessions API
- **WebSocket Client**: Real-time communication with automatic reconnection
- **File Transfer**: Upload and download files to/from sessions
- **TypeScript Support**: Full type definitions included
- **Node.js & Browser**: Works in both environments

## REST Client

### Configuration

```typescript
import { createClient } from '@limacharlie/ai-sessions';

const client = createClient({
  baseUrl: 'https://ai-sessions.limacharlie.io',
  token: 'your-jwt-token',
  timeout: 30000, // optional, default 30s
  retry: {
    maxRetries: 3,
    retryDelay: 1000,
    retryOn: [429, 502, 503, 504],
  },
});
```

### Registration

```typescript
// Register for AI Sessions
await client.register();

// Deregister (deletes all data)
await client.deregister();
```

### Sessions

```typescript
// List all sessions
const { sessions } = await client.listSessions();

// List running sessions only
const { sessions } = await client.listSessions({ status: 'running' });

// Create a session
const { session } = await client.createSession({
  allowed_tools: ['Bash', 'Read', 'Write'],
  denied_tools: ['WebFetch'],
});

// Get session details
const { session } = await client.getSession(sessionId);

// Terminate a session
await client.terminateSession(sessionId);

// Delete session record (after termination)
await client.deleteSessionRecord(sessionId);
```

### Credentials

```typescript
// Store Anthropic API key
await client.storeAPIKey('sk-ant-api03-xxxxx');

// Check credential status
const status = await client.getCredentialStatus();
console.log(status.has_credentials); // true/false
console.log(status.credential_type); // 'api_key' or 'oauth_token'

// Delete stored credentials
await client.deleteCredentials();
```

### OAuth Flow

```typescript
// Start OAuth flow
const { oauth_session_id } = await client.startOAuth();

// Poll for OAuth URL
const response = await client.pollOAuthURL(oauth_session_id);
if (response.status === 'url_ready') {
  console.log('Visit:', response.url);
}

// After user authorizes, submit the code
await client.submitOAuthCode(oauth_session_id, authorizationCode);
```

### Profiles

```typescript
// List profiles
const { profiles } = await client.listProfiles();

// Create a profile
const { profile } = await client.createProfile({
  name: 'Investigation',
  description: 'Profile for security investigations',
  allowed_tools: ['Bash', 'Read', 'Grep'],
  denied_tools: ['Write', 'Edit'],
  max_turns: 100,
  max_budget_usd: 10.0,
});

// Get profile
const { profile } = await client.getProfile(profileId);

// Update profile
await client.updateProfile(profileId, {
  name: 'Updated Investigation',
  max_turns: 150,
});

// Delete profile
await client.deleteProfile(profileId);

// Set as default
await client.setDefaultProfile(profileId);

// Capture session settings as profile
await client.captureProfile(sessionId, {
  name: 'My Session Config',
});
```

### File Transfer (REST)

```typescript
// Request upload URL
const { upload_url, upload_id, target_path } = await client.requestUploadURL(
  sessionId,
  {
    filename: 'data.csv',
    content_type: 'text/csv',
    size: 1024,
  }
);

// Upload using the URL (use fetch or your preferred HTTP client)
await fetch(upload_url, {
  method: 'PUT',
  body: fileContent,
  headers: { 'Content-Type': 'text/csv' },
});

// Notify upload complete
await client.notifyUploadComplete(sessionId, upload_id);

// Request download URL
const { download_url } = await client.requestDownloadURL(sessionId, {
  path: '/workspace/output.txt',
});

// Download using the URL
const response = await fetch(download_url);
const content = await response.text();
```

## WebSocket Client

### Configuration

```typescript
import { createSessionWebSocket } from '@limacharlie/ai-sessions';

const ws = createSessionWebSocket(
  client.getWebSocketURL(sessionId),
  {
    // Message handlers
    onMessage: (msg) => { /* any message */ },
    onAssistant: (msg) => { /* Claude response */ },
    onToolUse: (msg) => { /* tool being used */ },
    onToolResult: (msg) => { /* tool result */ },
    onUser: (msg) => { /* user message echo */ },
    onSystem: (msg) => { /* system message */ },
    onResult: (msg) => { /* final result */ },
    onError: (err) => { /* error */ },
    onSessionEnd: (msg) => { /* session ended */ },
    onConnectionChange: (state) => { /* connection state changed */ },
  },
  {
    // Options
    autoReconnect: true,
    maxReconnectAttempts: 5,
    reconnectDelay: 1000,
    heartbeatInterval: 30000,
  }
);
```

### Connection

```typescript
// Connect
await ws.connect();

// Check connection state
console.log(ws.getState()); // 'connecting', 'connected', 'disconnected'

// Disconnect
ws.disconnect();
```

### Sending Messages

```typescript
// Send a prompt
ws.sendPrompt('Write a hello world in Python');

// Interrupt current operation
ws.sendInterrupt();

// Send heartbeat (usually handled automatically)
ws.sendHeartbeat();
```

### File Transfer (WebSocket)

```typescript
// Request upload URL
ws.requestUpload({
  request_id: 'req_123',
  filename: 'data.csv',
  content_type: 'text/csv',
  size: 1024,
});

// Listen for upload_url response in onMessage handler

// Notify upload complete
ws.notifyUploadComplete({
  request_id: 'req_123',
  filename: 'data.csv',
  path: '/workspace/uploads/data.csv',
});

// Request download URL
ws.requestDownload({
  request_id: 'req_456',
  path: '/workspace/output.txt',
});
```

## File Transfer Helper

The SDK provides a convenience wrapper for file transfers:

```typescript
import { createFileTransfer, createWebSocketFileTransfer } from '@limacharlie/ai-sessions';

// REST-based file transfer
const fileTransfer = createFileTransfer(client);

// Upload a file
const path = await fileTransfer.uploadFile(
  sessionId,
  file, // File or Blob
  'document.pdf',
  {
    onProgress: (progress) => console.log(`${progress}%`),
  }
);

// Download a file
const blob = await fileTransfer.downloadFromURL(downloadUrl);

// WebSocket-based file transfer
const wsFileTransfer = createWebSocketFileTransfer(ws);
await wsFileTransfer.uploadFile(file, 'data.csv');
const blob = await wsFileTransfer.downloadFile('/output/result.txt');
```

## Node.js Usage

For Node.js, provide WebSocket implementation:

```typescript
import { createClient, createSessionWebSocket } from '@limacharlie/ai-sessions';
import WebSocket from 'ws';

const client = createClient({
  baseUrl: 'https://ai-sessions.limacharlie.io',
  token: 'your-jwt-token',
  fetch: globalThis.fetch, // Node 18+ has native fetch
});

const ws = createSessionWebSocket(
  client.getWebSocketURL(sessionId),
  handlers,
  options,
  WebSocket as unknown as typeof globalThis.WebSocket
);
```

## Types

All types are exported from the main package:

```typescript
import type {
  // Client types
  AISessionsClient,
  AISessionsConfig,

  // Session types
  Session,
  SessionStatus,
  CreateSessionRequest,
  LCCredentials,

  // Profile types
  Profile,
  CreateProfileRequest,
  MCPServerConfig,

  // WebSocket types
  WebSocketMessage,
  AssistantMessage,
  ToolUseMessage,
  ToolResultMessage,
  WebSocketOptions,
  ConnectionState,

  // File transfer types
  UploadRequest,
  UploadResponse,
  DownloadRequest,
  DownloadResponse,
} from '@limacharlie/ai-sessions';
```

## Error Handling

```typescript
import { APIError } from '@limacharlie/ai-sessions';

try {
  await client.createSession({});
} catch (error) {
  if ('error' in error && 'message' in error) {
    const apiError = error as APIError;
    console.error(`API Error: ${apiError.error} - ${apiError.message}`);

    // Handle specific errors
    switch (apiError.status) {
      case 401:
        console.error('Authentication failed');
        break;
      case 403:
        console.error('Not registered or no credentials');
        break;
      case 409:
        console.error('Max sessions reached');
        break;
      case 429:
        console.error('Rate limited');
        break;
    }
  }
}
```

## Complete Example

Here's a complete example showing a typical workflow:

```typescript
import { createClient, createSessionWebSocket } from '@limacharlie/ai-sessions';
import WebSocket from 'ws';

async function main() {
  // Create client
  const client = createClient({
    baseUrl: 'https://ai-sessions.limacharlie.io',
    token: process.env.LC_JWT!,
  });

  // Check if registered, register if not
  try {
    await client.getCredentialStatus();
  } catch (e) {
    console.log('Registering...');
    await client.register();
    await client.storeAPIKey(process.env.ANTHROPIC_KEY!);
  }

  // Create session
  console.log('Creating session...');
  const { session } = await client.createSession({
    allowed_tools: ['Bash', 'Read', 'Grep', 'Glob'],
    denied_tools: ['Write', 'Edit'],
  });
  console.log('Session ID:', session.id);

  // Wait for session to be running
  let status = session.status;
  while (status === 'pending') {
    await new Promise(r => setTimeout(r, 1000));
    const resp = await client.getSession(session.id);
    status = resp.session.status;
  }

  if (status !== 'running') {
    throw new Error(`Session failed to start: ${status}`);
  }

  // Connect via WebSocket
  console.log('Connecting...');
  const ws = createSessionWebSocket(
    client.getWebSocketURL(session.id),
    {
      onAssistant: (msg) => {
        for (const content of msg.payload.content) {
          if (content.type === 'text') {
            process.stdout.write(content.text);
          }
        }
      },
      onToolUse: (msg) => {
        console.log(`\n[Using ${msg.payload.name}]`);
      },
      onToolResult: (msg) => {
        console.log(`[Result: ${msg.payload.content.substring(0, 100)}...]`);
      },
      onSessionEnd: (msg) => {
        console.log(`\nSession ended: ${msg.payload.reason}`);
        process.exit(0);
      },
      onError: (err) => {
        console.error('Error:', err);
      },
    },
    { autoReconnect: true },
    WebSocket as unknown as typeof globalThis.WebSocket
  );

  await ws.connect();
  console.log('Connected!');

  // Send prompt
  ws.sendPrompt('Find all Python files in /workspace and show their first 10 lines');

  // Keep alive
  process.on('SIGINT', async () => {
    console.log('\nTerminating session...');
    ws.disconnect();
    await client.terminateSession(session.id);
    process.exit(0);
  });
}

main().catch(console.error);
```

## License

MIT
