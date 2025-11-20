
# Get Secret

This skill retrieves a secret value from LimaCharlie secure storage. Use this cautiously as it exposes sensitive credentials.

## When to Use

Use this skill when the user needs to:
- Retrieve a stored API key or token for verification
- Get a password or credential for troubleshooting
- Verify the correct secret value is stored
- Migrate credentials to another system
- Debug integration issues related to authentication

**WARNING**: Use this skill sparingly and with caution. Secret values should remain hidden in most cases.

Common scenarios:
- "Show me the webhook API key secret"
- "What's the value of the slack-api-token secret?"
- "I need to verify the stored S3 access key"
- "Get the password stored in database-password secret"

## What This Skill Does

This skill calls the LimaCharlie API to retrieve a specific secret's value and metadata. The actual secret value is returned in plaintext, so handle with care.

## Required Information

Before calling this skill, gather:

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **name**: Name of the secret to retrieve

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact secret name (case-sensitive)
3. User confirmation that they need to see the secret value
4. Understanding that the value will be exposed

### Step 2: Call the API

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="get_secret",
  parameters={
    "oid": "[organization-id]",
    "name": "[secret-name]"
  }
)
```

**API Details:**
- Tool: `get_secret`
- Required parameters:
  - `oid`: Organization ID
  - `name`: Name of the secret to retrieve

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "data": {
    "value": "actual-secret-value-here"
  },
  "sys_mtd": {
    "created_at": 1234567890,
    "created_by": "user@example.com",
    "last_mod": 1234567890,
    "last_author": "user@example.com",
    "etag": "abc123",
    "guid": "def456"
  },
  "usr_mtd": {
    "enabled": true,
    "tags": [],
    "comment": ""
  }
}
```

**Success:**
- Secret value is in `data.value`
- Metadata includes creation time, creator, last modification
- Present value carefully (consider masking in logs)
- Include metadata for context

**Common Errors:**
- **404 Not Found**: Secret with this name doesn't exist - verify exact name
- **403 Forbidden**: Insufficient permissions - user needs read access to secrets
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- Show secret name and value
- Include creation and modification metadata
- Warn about handling sensitive data securely
- Suggest storing or copying securely
- Remind not to share or log the value

## Example Usage

### Example 1: Get API key secret

User request: "Show me the webhook-api-key secret value"

Steps:
1. Confirm secret name: "webhook-api-key"
2. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_secret",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "webhook-api-key"
  }
)
```

Expected response:
```json
{
  "data": {
    "value": "sk_live_abc123def456ghi789"
  },
  "sys_mtd": {
    "created_at": 1640000000,
    "created_by": "admin@example.com",
    "last_mod": 1640000000,
    "last_author": "admin@example.com"
  },
  "usr_mtd": {
    "enabled": true
  }
}
```

Format output:
```
Secret: webhook-api-key

Value: sk_live_abc123def456ghi789

Metadata:
- Created: 2021-12-20 by admin@example.com
- Last modified: 2021-12-20 by admin@example.com
- Status: Enabled

WARNING: This is sensitive data. Handle securely and do not share or log.
```

### Example 2: Secret not found

User request: "Get the value of prod-database-password"

Steps:
1. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_secret",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "prod-database-password"
  }
)
```

Expected response:
```json
{
  "error": "Secret not found"
}
```

Format output:
```
Error: Secret "prod-database-password" not found.

The secret may not exist or the name might be incorrect.
Secret names are case-sensitive.

Would you like me to list all secrets to see what's available?
```

## Additional Notes

- Use this skill sparingly - secrets should remain hidden
- Secret values are returned in plaintext - handle carefully
- Consider security implications before exposing values
- Secret values may include:
  - API keys and tokens
  - Passwords
  - Access keys and secrets
  - Webhook authentication tokens
  - TLS certificates and private keys
- Do not log or persist secret values unnecessarily
- Rotate secrets if they may have been compromised
- Secret names are case-sensitive
- The `data.value` field contains the actual secret
- Metadata provides audit trail (who created/modified, when)
- Related skills: `list-secrets` to see names, `set-secret` to store values, `delete-secret` to remove

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/secrets.go`
