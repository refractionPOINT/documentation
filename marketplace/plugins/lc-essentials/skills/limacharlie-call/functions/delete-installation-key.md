
# Delete Installation Key

Remove an installation key from the LimaCharlie organization, preventing its use for new sensor deployments.

## When to Use

Use this skill when the user needs to:
- Delete an unused or obsolete installation key
- Revoke deployment credentials for security reasons
- Clean up installation keys after project completion
- Remove keys that may have been compromised
- Decommission keys associated with retired environments

Common scenarios:
- Security incident response - revoking potentially compromised keys
- Project cleanup after environment decommissioning
- Regular security hygiene - removing unused credentials
- Consolidating installation keys to reduce management overhead
- Rotating installation keys as part of security best practices

## What This Skill Does

This skill deletes a specified installation key from the organization. Once deleted, the key can no longer be used to deploy or enroll new sensors. Note that deleting an installation key does NOT affect sensors that were already deployed using that key - those sensors remain operational. This operation is permanent and cannot be undone, so it should be used carefully. The skill calls the LimaCharlie MCP tool to remove the key identified by its IID (installation key ID).

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **iid**: Installation key ID to delete (required)

To find the IID:
- Use the list-installation-keys skill to see all available keys and their IIDs
- The IID is the unique identifier for each installation key

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Correct installation key ID (iid) - verify this is the right key to delete
3. Confirmation that this key should be deleted (operation is permanent)
4. Understanding that existing sensors using this key will continue working

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_installation_key",
  parameters={
    "oid": "[organization-id]",
    "iid": "[installation-key-id]"
  }
)
```

**Tool Details:**
- Tool Name: `delete_installation_key`
- Required Parameters:
  - `oid`: Organization ID
  - `iid`: Installation key ID to delete

### Step 3: Handle the Response

The tool returns a response with:
```json
{}
```

**Success:**
- The installation key has been successfully deleted
- The key can no longer be used for new sensor deployments
- Existing sensors enrolled with this key continue to operate normally
- The deletion is permanent and cannot be undone

**Common Errors:**
- **Invalid IID**: Missing or invalid IID parameter
- **Unauthorized**: Authentication token is invalid or expired
- **Forbidden**: Insufficient permissions to delete installation keys (requires platform_admin role)
- **Not Found**: Installation key with the specified IID does not exist

### Step 4: Format the Response

Present the result to the user:
- Confirm successful deletion of the installation key
- Specify which key was deleted (by IID)
- Remind user that existing sensors are not affected
- Note that the operation is permanent
- Suggest creating a new key if replacement is needed

## Example Usage

### Example 1: Delete an obsolete installation key

User request: "Delete the installation key prod-old-key"

Steps:
1. Extract organization ID from context
2. Verify the IID to delete: "prod-old-key"
3. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_installation_key",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "iid": "prod-old-key"
  }
)
```

Expected response:
```json
{}
```

Present to user:
```
Successfully deleted installation key 'prod-old-key'.

This key can no longer be used to deploy new sensors.
Existing sensors that were enrolled with this key will continue to operate normally.
```

### Example 2: Delete compromised key after security incident

User request: "We had a security incident, remove the compromised installation key dev-test-123"

Steps:
1. Extract organization ID
2. Verify the key to revoke: "dev-test-123"
3. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_installation_key",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "iid": "dev-test-123"
  }
)
```

Expected response:
```json
{}
```

Present to user:
```
Installation key 'dev-test-123' has been revoked and deleted.

This key cannot be used to enroll new sensors.
Sensors already enrolled with this key remain connected.

Next steps:
1. Monitor sensors enrolled with this key for suspicious activity
2. Consider rotating to a new installation key
3. Review sensor list to identify which sensors used this key
```

### Example 3: Handle deletion of non-existent key

User request: "Delete the installation key old-key"

Steps:
1. Call tool with IID "old-key"
2. Tool returns not found error

Present to user:
```
Could not find installation key 'old-key'.

This key may have already been deleted or never existed.
Use the list-installation-keys skill to see all available keys.
```

## Additional Notes

- Deletion is permanent and cannot be undone - verify the IID before deleting
- Deleting a key does NOT affect sensors already enrolled with that key
- Sensors deployed with a deleted key will continue to function normally
- To find which sensors used a specific key, check sensor tags (keys automatically apply tags)
- After deleting a compromised key, consider:
  - Auditing sensors that used that key
  - Creating a replacement key with different credentials
  - Reviewing access logs for unauthorized usage
- Use the list-installation-keys skill to verify which keys exist before deletion
- If you need to prevent sensors from connecting, use sensor isolation or deletion instead
- Installation key deletion is a security-sensitive operation requiring platform_admin permissions
- Consider documenting why keys are deleted for audit purposes
- If rotating keys, create the new key before deleting the old one to ensure continuity

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/go-limacharlie/limacharlie/installation_keys.go`
For the MCP tool implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/lc-mcp-server/internal/tools/config/installation_keys.go`
