
# Create API Key

Generate a new API key for a LimaCharlie organization with optional permission restrictions for secure programmatic access.

## When to Use

Use this skill when the user needs to:
- Create API credentials for integrations or automation
- Generate keys for third-party tool access
- Set up restricted access keys following least-privilege principle
- Create keys for different environments (dev, staging, production)
- Provide API access to external partners or services

Common scenarios:
- Setting up SIEM integrations
- Configuring automation workflows
- Granting limited access to contractors
- Creating environment-specific credentials
- Implementing security best practices with restricted permissions

## What This Skill Does

This skill creates a new API key for a LimaCharlie organization. It calls the LimaCharlie API to generate a key with an optional description and permission restrictions. The API returns the actual key value (only shown once) and a key hash for future management. Keys can have full organization access or be restricted to specific operations.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **key_name**: Description or name for the API key (required)

Optional parameters:
- **permissions**: List of specific permissions to grant (omit for full access)
  - Examples: ["sensor.get", "sensor.list", "sensor.task"]
  - Empty or omitted = full organization access
  - Specify permissions for least-privilege access

Common permissions:
- `sensor.get`, `sensor.list` - Read sensor information
- `sensor.task` - Send tasks to sensors
- `rule.get`, `rule.set`, `rule.delete` - Manage D&R rules
- `output.get`, `output.set`, `output.delete` - Manage outputs
- `insight.evt.get`, `insight.det.get` - Query historical data

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Descriptive key name (helps identify purpose later)
3. Optional: List of specific permissions (recommended for security)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/v1/orgs/[oid]/keys",
  body={
    "key_name": "[description]",
    "perms": "[permission1,permission2,...]"  # Optional, comma-separated
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/v1/orgs/{oid}/keys`
- Query parameters: None
- Body fields:
  - `key_name` (string, required): Description/name for the key
  - `perms` (string, optional): Comma-separated list of permissions

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "key": "lc://api/1a2b3c4d-5e6f-7890-abcd-ef1234567890",
    "key_hash": "a1b2c3d4e5f6"
  }
}
```

**Success (200-299):**
- Response contains the actual API key value (only shown once!)
- Key hash is provided for future management (deletion, identification)
- Store the key value securely immediately
- The key is immediately active and can be used for API calls
- Key hash appears in list-api-keys output for management

**Common Errors:**
- **400 Bad Request**: Invalid parameters (missing key_name, invalid permissions)
- **403 Forbidden**: Insufficient permissions to create API keys - requires admin or owner access
- **404 Not Found**: Organization does not exist
- **409 Conflict**: Key name conflicts with existing key (though duplicates are usually allowed)
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- **CRITICAL**: Display the API key value prominently with a security warning
- Emphasize that the key value cannot be retrieved again
- Provide the key hash for reference
- Include instructions to store the key securely
- Suggest adding the key to a secret manager or vault
- Warn against committing the key to version control

## Example Usage

### Example 1: Create a full-access API key

User request: "Create an API key for our SIEM integration"

Steps:
1. Extract organization ID
2. Create key with descriptive name:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/orgs/c7e8f940-1234-5678-abcd-1234567890ab/keys",
  body={
    "key_name": "SIEM Integration Key"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "key": "lc://api/a1b2c3d4-5e6f-7890-1234-567890abcdef",
    "key_hash": "f1e2d3c4b5a6"
  }
}
```

Present to user:
```
✅ API Key Created Successfully

⚠️ IMPORTANT: Save this key immediately - it cannot be retrieved again!

API Key: lc://api/a1b2c3d4-5e6f-7890-1234-567890abcdef
Key Hash: f1e2d3c4b5a6
Name: SIEM Integration Key
Permissions: Full access (unrestricted)

Security recommendations:
- Store this key in a secure secret manager
- Never commit this key to version control
- Rotate this key every 90 days
- Consider using restricted permissions if possible
```

### Example 2: Create a restricted read-only API key

User request: "Create a read-only API key for a contractor to view sensor data"

Steps:
1. Identify appropriate read-only permissions
2. Create key with restrictions:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/orgs/c7e8f940-1234-5678-abcd-1234567890ab/keys",
  body={
    "key_name": "Contractor Read-Only Access",
    "perms": "sensor.get,sensor.list,insight.evt.get"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "key": "lc://api/9z8y7x6w-5v4u-3t2s-1r0q-ponmlkjihgf",
    "key_hash": "9a8b7c6d5e4f"
  }
}
```

Present to user:
```
✅ Restricted API Key Created

⚠️ Save this key now - it will not be shown again!

API Key: lc://api/9z8y7x6w-5v4u-3t2s-1r0q-ponmlkjihgf
Key Hash: 9a8b7c6d5e4f
Name: Contractor Read-Only Access
Permissions: sensor.get, sensor.list, insight.evt.get (Read-only)

This key has restricted access and can only:
✓ View sensor information
✓ List sensors
✓ Query historical event data

This key CANNOT:
✗ Send tasks to sensors
✗ Modify rules or configurations
✗ Delete data or resources

This follows security best practices (principle of least privilege).
```

## Additional Notes

- **The API key value is only displayed once** - there is no way to retrieve it later
- Store keys immediately in a secure location (secret manager, vault, password manager)
- Key hashes are stable identifiers used for management (deletion, listing)
- Full access keys (no permissions) have complete organization access
- Restricted keys improve security by limiting potential damage from key compromise
- Consider creating separate keys for different purposes/environments
- Implement key rotation policies (90-180 days recommended)
- Never hardcode keys in source code or commit to version control
- Use environment variables or secret managers for key storage
- Revoke contractor/temporary keys promptly when no longer needed

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/organization_ext.go` (CreateAPIKey function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/admin/admin.go` (RegisterCreateAPIKey)
