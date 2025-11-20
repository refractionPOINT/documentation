
# Delete API Key

Permanently delete an API key from a LimaCharlie organization, immediately revoking its access.

## When to Use

Use this skill when the user needs to:
- Revoke access for a compromised or exposed API key
- Remove API keys for departed team members or contractors
- Clean up unused or obsolete API keys
- Implement API key rotation policies
- Respond to security incidents involving API key exposure

Common scenarios:
- Key rotation as part of security best practices
- Decommissioning integrations or automation
- Responding to key exposure in logs or version control
- Auditing and removing old or unused keys
- Revoking third-party access

## What This Skill Does

This skill deletes an API key from a LimaCharlie organization. It calls the LimaCharlie API to permanently revoke the key using its key ID. Once deleted, the key immediately stops working and cannot be recovered. This is a security-critical operation that should be used carefully.

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required)
- **key_id**: The ID of the API key to delete (required)
  - Obtain from list-api-keys skill
  - Not the actual key value, but the key identifier

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Correct key ID from list-api-keys
3. Confirmation that the correct key is being deleted (verify key name/description)
4. Understanding that deletion is permanent and immediate

**IMPORTANT**: Always list keys first to confirm you're deleting the correct one!

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_api_key",
  parameters={
    "oid": "[organization-id]",
    "key_id": "[key-id]"
  }
)
```

**Tool Details:**
- Tool name: `delete_api_key`
- Required parameters:
  - `oid` (string): Organization ID
  - `key_id` (string): ID of the API key to delete

### Step 3: Handle the Response

The tool returns a response with:
```json
{}
```

**Success:**
- Empty or minimal response body indicates successful deletion
- The API key is immediately revoked and stops working
- Any applications using this key will fail authentication
- The key cannot be recovered - deletion is permanent
- The key will no longer appear in list-api-keys output

**Common Errors:**
- **400 Bad Request**: Invalid key_id format or missing parameter
- **403 Forbidden**: Insufficient permissions to delete API keys - requires admin or owner access
- **404 Not Found**: Key ID does not exist or organization not found
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm successful deletion
- Remind user that the key is immediately revoked
- Warn about potential impact on running integrations
- Suggest verifying that dependent systems have been updated
- Recommend creating a replacement key if needed

## Example Usage

### Example 1: Delete a compromised API key

User request: "Delete the API key that was accidentally committed to GitHub"

Steps:
1. First, list keys to identify the compromised one:
```
# Use list-api-keys to find the key ID
```
2. Confirm which key to delete (verify name/description)
3. Delete the key:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_api_key",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "key_id": "a1b2c3d4e5f6"
  }
)
```

Expected response:
```json
{}
```

Present to user:
```
API Key Deleted Successfully

The compromised API key has been permanently revoked.

Key ID: a1b2c3d4e5f6
Status: Deleted and immediately deactivated

Important next steps:
1. The old key will no longer work for API calls
2. Update any systems using this key with a new one
3. Review access logs for unauthorized usage
4. Consider rotating other keys as a precaution
5. Remove the key from any documentation or configs

Would you like me to create a replacement key?
```

### Example 2: Clean up old unused keys

User request: "Remove all API keys older than 1 year"

Steps:
1. List all API keys with creation dates
2. Identify keys older than 365 days
3. Confirm with user which keys to delete
4. Delete each identified key:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_api_key",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "key_id": "f1e2d3c4b5a6"
  }
)
```

Present summary:
```
API Key Cleanup Complete

Deleted 3 old API keys:

- "Old Integration Key" (created 2 years ago)
- "Test Key" (created 18 months ago)
- "Deprecated Automation" (created 14 months ago)

All keys have been permanently revoked.

Remaining active keys: 2
- "Production SIEM Key" (created 3 months ago)
- "Monitoring Service" (created 1 month ago)

Recommendation: Implement a 90-day key rotation policy.
```

### Example 3: Revoke contractor access

User request: "Remove API access for the contractor who finished last week"

Steps:
1. List keys to find contractor's key
2. Verify it's the correct key (check description)
3. Delete the key:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_api_key",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "key_id": "9a8b7c6d5e4f"
  }
)
```

Present to user:
```
Contractor Access Revoked

API key "Contractor Read-Only Access" has been deleted.

Key ID: 9a8b7c6d5e4f
Permissions: sensor.get, sensor.list (read-only)
Status: Permanently revoked

The contractor no longer has API access to your organization.

- Access properly terminated
- Least-privilege key removed
- No further cleanup needed
```

## Additional Notes

- **Deletion is immediate and permanent** - keys cannot be recovered
- Always list keys first to verify you're deleting the correct one
- Check key descriptions/names to avoid deleting wrong keys
- Consider the impact on running integrations before deletion
- Key deletion is a privileged operation requiring admin access
- Deleted keys immediately stop working for all API calls
- Use deletion as part of key rotation workflows
- When rotating keys: create new key -> update systems -> delete old key
- Monitor for authentication failures after deletion to catch missed dependencies
- Key IDs are unique - you cannot accidentally delete wrong org's keys
- Consider implementing automated key rotation with scheduled deletion

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/organization_ext.go` (DeleteAPIKey function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/admin/admin.go` (RegisterDeleteAPIKey)
