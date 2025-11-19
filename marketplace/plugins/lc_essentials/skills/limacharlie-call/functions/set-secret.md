
# Set Secret

This skill stores a secret securely in LimaCharlie. Secrets can be referenced in output configurations, D&R rules, and integrations.

## When to Use

Use this skill when the user needs to:
- Store an API key or token securely
- Save passwords or credentials
- Store webhook authentication tokens
- Save cloud service access keys
- Store TLS certificates or private keys
- Update an existing secret value
- Create secrets for use in outputs or D&R rules

Common scenarios:
- "Store this API key as a secret named webhook-key"
- "Save my Slack token securely"
- "Create a secret for the S3 access key"
- "Update the database password secret"
- "I need to store credentials for the output configuration"

## What This Skill Does

This skill calls the LimaCharlie API to store a secret securely. The secret is encrypted at rest and can be referenced in configurations using `[secret:secret-name]` syntax. If a secret with the same name exists, it will be updated.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **secret_name**: Name for the secret (alphanumeric, hyphens, underscores)
- **secret_value**: The actual secret value to store

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Descriptive secret name (should indicate purpose)
3. Secret value (the actual credential to store)
4. Confirmation that the value is correct (updating overwrites)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/v1/hive/secret/[oid]/[secret-name]/data",
  body={
    "data": "{\"value\": \"secret-value-here\"}",
    "usr_mtd": "{\"enabled\": true}"
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/v1/hive/secret/{oid}/{secret_name}/data` (replace `{oid}` with organization ID and `{secret_name}` with the secret name)
- Query parameters: None
- Body structure (Hive record format):
  - `data`: JSON-encoded string containing the secret data (e.g., `{"value": "secret-value"}`)
  - `usr_mtd`: JSON-encoded string containing user metadata (e.g., `{"enabled": true}`)

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "guid": "abc123...",
    "hive": {
      "name": "secret",
      "partition": "oid"
    },
    "name": "secret-name"
  }
}
```

**Success (200-299):**
- Secret is stored and immediately available
- Response includes GUID and confirmation
- Secret can be referenced as `[secret:secret-name]`
- If updating, the old value is replaced

**Common Errors:**
- **400 Bad Request**: Invalid parameters (missing fields, malformed body)
- **403 Forbidden**: Insufficient permissions - user needs write access to secrets
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- Confirm secret storage with name
- Explain how to reference: `[secret:secret-name]`
- Provide examples of usage (outputs, D&R rules)
- Remind about security best practices
- Note if this updated an existing secret

## Example Usage

### Example 1: Store webhook API key

User request: "Store this API key as a secret: sk_live_abc123def456"

Steps:
1. Choose descriptive name: "webhook-api-key"
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/hive/secret/c7e8f940-1234-5678-abcd-1234567890ab/webhook-api-key/data",
  body={
    "data": "{\"value\": \"sk_live_abc123def456\"}",
    "usr_mtd": "{\"enabled\": true}"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "guid": "abc123-def456-ghi789"
  }
}
```

Format output:
```
Successfully stored secret "webhook-api-key"

The API key has been securely encrypted and stored.

To reference this secret in configurations, use:
  [secret:webhook-api-key]

Example usage in webhook output:
  auth_header_value: [secret:webhook-api-key]

The secret value is now hidden and can only be retrieved using get-secret.
```

### Example 2: Store Slack token

User request: "Save my Slack token securely: xoxb-1234567890-abcdefghijk"

Steps:
1. Use descriptive name: "slack-api-token"
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/hive/secret/c7e8f940-1234-5678-abcd-1234567890ab/slack-api-token/data",
  body={
    "data": "{\"value\": \"xoxb-1234567890-abcdefghijk\"}",
    "usr_mtd": "{\"enabled\": true}"
  }
)
```

Format output:
```
Successfully stored secret "slack-api-token"

Your Slack token is now securely stored and encrypted.

To use in a Slack output:
  slack_api_token: [secret:slack-api-token]

To use in a D&R rule action:
  - action: report
    metadata:
      slack_token: '[secret:slack-api-token]'
```

### Example 3: Update existing secret

User request: "Update the database-password secret with the new password"

Steps:
1. Confirm this will replace the old value
2. Call API with new value
3. Format output:
```
Successfully updated secret "database-password"

The secret value has been replaced with the new password.
Any configurations referencing [secret:database-password] will now use the new value.

Note: The change takes effect immediately. Ensure any services using this secret can handle the update.
```

## Additional Notes

- Secrets are encrypted at rest
- Secret names should be descriptive but not reveal sensitive info
- Good naming patterns:
  - `service-type-credential` (e.g., slack-api-token)
  - `environment-service-key` (e.g., prod-webhook-key)
  - `system-auth-type` (e.g., database-password)
- Reference secrets in configs: `[secret:secret-name]`
- Secrets work in:
  - Output configurations (API keys, passwords, tokens)
  - D&R rule actions (webhooks, notifications)
  - Extension configurations
- Setting an existing secret name updates the value
- No confirmation prompt for updates - be careful
- Secret values are never logged or displayed after storage
- Rotate secrets regularly for security
- Delete secrets that are no longer needed
- Related skills: `list-secrets` to view names, `get-secret` to retrieve values, `delete-secret` to remove

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/secrets.go`
