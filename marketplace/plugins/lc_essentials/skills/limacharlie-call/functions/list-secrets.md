
# List Secrets

This skill retrieves all secret names (but not values) stored in a LimaCharlie organization. Secrets are used to securely store credentials that can be referenced in output configurations, D&R rules, and other places.

## When to Use

Use this skill when the user needs to:
- View all stored secret names
- Audit what credentials are stored
- Check if a secret exists before referencing it
- Verify secret naming before creating configurations
- Find the correct secret name to reference
- Review security credential inventory

Common scenarios:
- "What secrets are stored in the organization?"
- "List all API keys and credentials"
- "Show me secret names"
- "Does a secret named 'webhook-key' exist?"
- "What secrets can I reference in my output configuration?"

## What This Skill Does

This skill calls the LimaCharlie API to list all secret names in an organization. For security, only the names are returned - actual secret values are not included. Secret values can only be retrieved individually using the get-secret skill.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No other parameters are needed for listing secret names.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="GET",
  path="/hive/secret/[oid]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/hive/secret/{oid}` (replace `{oid}` with actual organization ID)
- Query parameters: None
- Body: None (GET request)

Note: Secrets are stored in the LimaCharlie Hive system, which is a key-value store.

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "api-key-prod": {
      "data": {},
      "sys_mtd": {
        "created_at": 1234567890,
        "created_by": "user@example.com",
        "last_mod": 1234567890,
        "last_author": "user@example.com"
      },
      "usr_mtd": {
        "enabled": true
      }
    },
    "webhook-token": {
      "data": {},
      "sys_mtd": {...},
      "usr_mtd": {...}
    }
  }
}
```

**Success (200-299):**
- Response body contains a dictionary where keys are secret names
- Each secret has metadata but the `data` field is empty (values not returned)
- Extract secret names from the dictionary keys
- Metadata includes creation time, creator, last modification
- Present as a list of secret names

**Common Errors:**
- **404 Not Found**: Organization doesn't exist or has no secrets (empty result)
- **403 Forbidden**: Insufficient permissions - user needs read access to secrets
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- List all secret names
- Include metadata if helpful (creation date, last modified)
- Note that actual values are not shown for security
- Explain how to reference secrets: `[secret:secret-name]`
- Note if no secrets are configured (empty result)
- Suggest creating secrets if needed for outputs or integrations

## Example Usage

### Example 1: List all secrets

User request: "What secrets are stored in the organization?"

Steps:
1. Obtain organization ID
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/hive/secret/c7e8f940-1234-5678-abcd-1234567890ab"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "slack-api-token": {
      "data": {},
      "sys_mtd": {
        "created_at": 1640000000,
        "created_by": "admin@example.com",
        "last_mod": 1640000000,
        "last_author": "admin@example.com"
      },
      "usr_mtd": {
        "enabled": true
      }
    },
    "webhook-api-key": {
      "data": {},
      "sys_mtd": {
        "created_at": 1641000000,
        "created_by": "admin@example.com",
        "last_mod": 1641000000,
        "last_author": "admin@example.com"
      },
      "usr_mtd": {
        "enabled": true
      }
    },
    "s3-access-key": {
      "data": {},
      "sys_mtd": {
        "created_at": 1642000000,
        "created_by": "admin@example.com",
        "last_mod": 1642000000,
        "last_author": "admin@example.com"
      },
      "usr_mtd": {
        "enabled": true
      }
    }
  }
}
```

Format output:
```
Stored Secrets (3 total):

1. slack-api-token
   - Created: 2021-12-20 by admin@example.com
   - Status: Enabled

2. webhook-api-key
   - Created: 2022-01-01 by admin@example.com
   - Status: Enabled

3. s3-access-key
   - Created: 2022-01-12 by admin@example.com
   - Status: Enabled

Note: Secret values are not shown for security. Use get-secret to retrieve specific values.

To reference secrets in configurations, use: [secret:secret-name]
For example: [secret:slack-api-token]
```

### Example 2: No secrets configured

User request: "List secrets"

Steps:
1. Call API as above
2. Receive empty response:
```json
{
  "status_code": 200,
  "body": {}
}
```

Format output:
```
No secrets are currently stored in this organization.

Secrets are used to securely store:
- API keys and tokens
- Passwords and credentials
- Webhook authentication tokens
- Cloud service access keys

You can create secrets using the set-secret skill.
Secrets can be referenced in outputs, D&R rules, and integrations using: [secret:secret-name]
```

### Example 3: Check if specific secret exists

User request: "Does a secret named 'prod-api-key' exist?"

Steps:
1. Call API to list all secrets
2. Check if 'prod-api-key' is in the response keys
3. Format output:
```
Yes, the secret "prod-api-key" exists in the organization.

Created: 2022-03-15 by admin@example.com
Last modified: 2022-03-15
Status: Enabled

To use this secret in a configuration, reference it as: [secret:prod-api-key]
```

Or if not found:
```
No, the secret "prod-api-key" does not exist.

Available secrets: slack-api-token, webhook-api-key, s3-access-key

To create this secret, use the set-secret skill.
```

## Additional Notes

- Secret values are never returned in list operations (security by design)
- Only secret names and metadata are visible
- Use get-secret skill to retrieve individual secret values (use cautiously)
- Secret names should be descriptive but not reveal sensitive information
- Common secret naming patterns:
  - `service-type-key` (e.g., slack-api-token, s3-access-key)
  - `environment-service-credential` (e.g., prod-webhook-key)
  - `integration-name-auth` (e.g., splunk-hec-token)
- Reference secrets in configurations: `[secret:secret-name]`
- Secret references work in:
  - Output configurations (auth headers, passwords, API keys)
  - D&R rule actions
  - Extension configurations
  - Webhook payloads
- Secrets are encrypted at rest
- Access to secrets requires proper permissions
- Related skills: `get-secret` to retrieve values, `set-secret` to create/update, `delete-secret` to remove

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/secrets.go`
