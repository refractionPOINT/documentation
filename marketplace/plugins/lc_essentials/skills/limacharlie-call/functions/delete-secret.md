
# Delete Secret

This skill deletes a secret from LimaCharlie secure storage. Deletion is immediate and cannot be undone.

## When to Use

Use this skill when the user needs to:
- Remove a secret that is no longer needed
- Delete compromised or rotated credentials
- Clean up unused API keys or tokens
- Remove test or temporary secrets
- Prevent a secret from being used in configurations
- Security cleanup after credential rotation

Common scenarios:
- "Delete the webhook-api-key secret"
- "Remove the old Slack token"
- "I rotated the API key, delete the old one"
- "Clean up unused secrets"
- "The credential was compromised, remove it immediately"

## What This Skill Does

This skill calls the LimaCharlie API to permanently delete a secret. Any configurations (outputs, D&R rules) that reference the deleted secret will fail to authenticate. The deletion is immediate and cannot be reversed.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **secret_name**: Name of the secret to delete

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact secret name (case-sensitive)
3. Confirmation that the secret is not being used
4. Understanding that deletion is permanent

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="DELETE",
  path="/v1/hive/secret/[oid]/[secret-name]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `DELETE`
- Path: `/hive/secret/{oid}/{secret_name}` (replace placeholders with actual values)
- Query parameters: None
- Body: None (DELETE request)

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

**Success (200-299):**
- Secret is deleted immediately
- Response body is typically empty or contains confirmation
- Secret name is now available for reuse
- Configurations referencing this secret will fail

**Common Errors:**
- **404 Not Found**: Secret with this name doesn't exist - verify exact name
- **403 Forbidden**: Insufficient permissions - user needs write access to secrets
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- Confirm deletion with secret name
- Warn about impact:
  - Outputs using this secret will fail
  - D&R rules referencing it will error
  - Cannot be undone
- Suggest:
  - Verify no configurations are using the secret
  - Check org errors for any failures
  - Create replacement secret if credential was rotated

## Example Usage

### Example 1: Delete unused secret

User request: "Delete the old-webhook-key secret, we're not using it anymore"

Steps:
1. Confirm secret name: "old-webhook-key"
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/v1/hive/secret/c7e8f940-1234-5678-abcd-1234567890ab/old-webhook-key"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {}
}
```

Format output:
```
Successfully deleted secret "old-webhook-key"

The secret has been permanently removed from secure storage.
Any configurations referencing [secret:old-webhook-key] will no longer work.

The secret name is now available for reuse if needed.
```

### Example 2: Rotate credentials

User request: "I've rotated our API key. Delete the old secret 'api-key-v1' after I create the new one"

Steps:
1. User creates new secret 'api-key-v2' (use set-secret skill)
2. Update configurations to reference new secret
3. Delete old secret:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/v1/hive/secret/c7e8f940-1234-5678-abcd-1234567890ab/api-key-v1"
)
```

Format output:
```
Successfully deleted secret "api-key-v1"

Credential rotation complete:
1. New secret 'api-key-v2' is active
2. Configurations updated to use new secret
3. Old secret removed

Verify all integrations are working with the new credentials.
Monitor org errors for any authentication failures.
```

### Example 3: Secret not found

User request: "Delete the test-secret"

Steps:
1. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/v1/hive/secret/c7e8f940-1234-5678-abcd-1234567890ab/test-secret"
)
```

Expected response:
```json
{
  "status_code": 404,
  "error": "Secret not found"
}
```

Format output:
```
Error: Secret "test-secret" not found.

The secret may have already been deleted or the name might be incorrect.
Secret names are case-sensitive.

Would you like me to list all secrets to see what exists?
```

### Example 4: Check for usage before deletion

User request: "Can I safely delete the slack-token secret?"

Steps:
1. List outputs to check for references
2. Check D&R rules if possible
3. If safe, proceed with deletion
4. If in use:
```
Warning: The secret "slack-token" is currently being used by:
- Output: "slack-notifications" (module: slack)
- D&R Rule: "critical-alert-notification"

Deleting this secret will cause these configurations to fail.

Options:
1. Update configurations to use a different secret first
2. Delete anyway (will cause failures)
3. Cancel deletion

What would you like to do?
```

## Additional Notes

- Deletion is immediate and permanent
- Cannot undo secret deletion
- Configurations using deleted secrets will fail with authentication errors
- Check for secret usage before deleting:
  - List outputs and search for `[secret:secret-name]`
  - Review D&R rules for secret references
  - Check extension configurations
- Secret names are case-sensitive - must match exactly
- Best practices for secret rotation:
  1. Create new secret with rotated credential
  2. Update all configurations to reference new secret
  3. Verify new secret works
  4. Delete old secret
- After deletion, monitor org errors for any failures
- Secret name becomes available for reuse immediately
- Consider disabling instead of deleting if unsure (update with dummy value)
- Related skills: `list-secrets` to view names, `set-secret` to create replacements, `get-secret` to verify values before deletion

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/secrets.go`
