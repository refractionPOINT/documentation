---
name: list-api-keys
description: List all API keys for a LimaCharlie organization. Use this skill when you need to view API keys, check key permissions, audit API access, or manage organization authentication credentials. Shows key metadata including creation time, permissions, and usage but does not return actual key values for security.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# List API Keys

Retrieve all API keys configured for a LimaCharlie organization, including their metadata, permissions, and configuration details.

## When to Use

Use this skill when the user needs to:
- View all API keys in an organization
- Audit API key permissions and access levels
- Check when API keys were created or last used
- Identify API keys for rotation or deletion
- Review organization authentication credentials

Common scenarios:
- Security audits of API access
- Troubleshooting authentication issues
- API key management and cleanup
- Preparing for key rotation
- Documenting organization access patterns

## What This Skill Does

This skill lists all API keys for a LimaCharlie organization. It calls the LimaCharlie API to retrieve API key metadata including key hashes, creation timestamps, permissions, and usage information. For security reasons, actual API key values are never returned - only the key hashes and metadata.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No additional parameters are required for listing API keys.

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
  path="/orgs/[oid]/keys"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/orgs/{oid}/keys`
- Query parameters: None
- Body fields: None

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "api_keys": {
      "key_hash_1": {
        "created": 1234567890,
        "perms": ["sensor.get", "sensor.task"],
        "key_name": "Production API Key"
      },
      "key_hash_2": {
        "created": 1234567899,
        "perms": [],
        "key_name": "Development Key"
      }
    }
  }
}
```

**Success (200-299):**
- Response contains a map of key hashes to API key metadata
- Each key entry includes creation timestamp, permissions list, and description
- Empty permissions array means the key has full organization access
- Key hashes can be used to delete specific keys

**Common Errors:**
- **400 Bad Request**: Invalid organization ID format
- **403 Forbidden**: Insufficient permissions to view API keys - requires admin or owner access
- **404 Not Found**: Organization does not exist
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Display each API key with its name/description
- Show the key hash (needed for deletion)
- List the permissions for each key (or indicate full access)
- Include creation timestamps in human-readable format
- Highlight keys with no permissions (full access) as these are high-privilege
- Consider suggesting rotation for very old keys

## Example Usage

### Example 1: List all API keys in an organization

User request: "Show me all API keys for my organization"

Steps:
1. Extract organization ID from context
2. Call API to retrieve all keys:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/orgs/c7e8f940-1234-5678-abcd-1234567890ab/keys"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "api_keys": {
      "a1b2c3d4e5f6": {
        "created": 1609459200,
        "perms": [],
        "key_name": "Main API Key"
      },
      "f6e5d4c3b2a1": {
        "created": 1640995200,
        "perms": ["sensor.get", "sensor.list"],
        "key_name": "Read-only Key"
      }
    }
  }
}
```

Present to user:
```
Found 2 API keys:

1. Main API Key (Hash: a1b2c3d4e5f6)
   - Created: January 1, 2021
   - Permissions: Full access (no restrictions)
   - ⚠️ High-privilege key

2. Read-only Key (Hash: f6e5d4c3b2a1)
   - Created: January 1, 2022
   - Permissions: sensor.get, sensor.list
   - Limited to sensor read operations
```

### Example 2: Audit API keys for security review

User request: "I need to audit all API keys and their permissions"

Steps:
1. List all API keys using the API call
2. Analyze permissions for each key
3. Identify high-risk keys (full access, old keys)
4. Provide security recommendations

Present findings with:
- Keys with full organization access highlighted
- Keys older than 90 days flagged for rotation
- Keys with minimal permissions marked as least-privilege
- Recommendations for improving API key security

## Additional Notes

- API key values are only shown once during creation - they cannot be retrieved later
- Key hashes are stable identifiers used for management operations
- Empty permissions array indicates full organization access (highest privilege)
- Keys with specific permissions follow principle of least privilege
- Consider implementing key rotation policies (90-180 days)
- Always use restricted permissions when possible
- This is a read-only operation - no keys are modified

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/organization_ext.go` (GetAPIKeys function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/admin/admin.go` (RegisterListAPIKeys)
