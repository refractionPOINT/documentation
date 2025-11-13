---
name: delete-rule
description: Delete a rule from a Hive in a LimaCharlie organization. Use this skill when users need to remove, delete, or clean up rules from any Hive like D&R rules (dr-general), false positive rules (fp), or other custom Hive types. Generic Hive operation that works with any Hive name. Permanently removes the rule. Use with caution as this action cannot be undone. Useful for decommissioning detection rules or removing obsolete filtering rules.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Delete Rule from Hive

Permanently deletes a rule from a Hive in a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- Delete a D&R rule permanently
- Remove a false positive rule
- Clean up obsolete rules from any Hive
- Decommission detection or response logic
- Fix issues by removing and recreating a rule

Common scenarios:
- "Delete the 'suspicious-dns' D&R rule from general namespace"
- "Remove the 'chrome-fp' false positive rule"
- "Delete the rule named 'old-detection' from dr-general"
- "Clean up the test rules from fp Hive"

## What This Skill Does

This skill permanently deletes a rule from a specified Hive in the LimaCharlie Hive system. It's a generic operation that works with any Hive name. The skill sends a DELETE request to the Hive API using the specified Hive name, "global" partition, and rule name. Once deleted, the rule and all its data are permanently removed and cannot be recovered.

**Warning:** This operation is permanent and cannot be undone. The rule will immediately stop executing. Consider getting the rule first if you might need to restore it later.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **hive_name**: The name of the Hive containing the rule (required)
  - Common values: `dr-general`, `fp`
- **rule_name**: The name of the rule to delete (required)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Hive name (string, determines which Hive to delete from)
3. Rule name (string, must be exact match)
4. Consider warning the user that this is permanent
5. Optionally, use get-rule first to confirm what will be deleted

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="DELETE",
  path="/hive/[hive-name]/global/[rule-name]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `DELETE`
- Path: `/hive/{hive_name}/global/{rule_name}`
  - Replace `{hive_name}` with the Hive name
  - Replace `{rule_name}` with the URL-encoded rule name
  - No `/data` or `/mtd` suffix - delete operates on the entire record
- Query parameters: None
- Body: None

### Step 3: Handle the Response

The API returns:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

**Success (200-299):**
- Rule has been permanently deleted
- Inform the user that the deletion was successful
- Note that this action cannot be undone

**Common Errors:**
- **400 Bad Request**: Invalid rule name format
- **403 Forbidden**: Insufficient permissions or read-only Hive
- **404 Not Found**: The rule doesn't exist - already deleted or never existed
- **500 Server Error**: Backend issue - advise retry

### Step 4: Format the Response

Present the result to the user:
- Confirm the rule was deleted
- Show the rule name and Hive that was removed from
- Warn that this action is permanent
- Note that the rule will no longer execute
- Suggest using list-rules to verify deletion if needed

## Example Usage

### Example 1: Delete a D&R rule

User request: "Delete the 'suspicious-dns' D&R rule from general namespace"

Steps:
1. Get the organization ID from context
2. Optionally warn user about permanent deletion
3. Use hive_name "dr-general" and rule_name "suspicious-dns"
4. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/hive/dr-general/global/suspicious-dns"
)
```

Expected response confirms deletion.

Inform user: "Successfully deleted the suspicious-dns rule from dr-general. This action is permanent and cannot be undone. The rule will no longer detect or respond to events."

### Example 2: Delete a false positive rule

User request: "Remove the 'chrome-fp' false positive rule"

Steps:
1. Get organization ID
2. Use hive_name "fp" and rule_name "chrome-fp"
3. Call API with path "/hive/fp/global/chrome-fp"

Expected response confirms the FP rule was deleted.

### Example 3: Handle non-existent rule

User request: "Delete the 'non-existent-rule' from dr-general"

Steps:
1. Attempt to delete the rule
2. Receive 404 error
3. Inform user: "The rule 'non-existent-rule' does not exist in dr-general. It may have already been deleted or was never created."

## Additional Notes

- **Permanent Action**: Deleted rules cannot be recovered - there is no "trash" or "undo"
- **Backup First**: Consider retrieving the rule with get-rule before deleting
- **Read-Only Hives**: Some Hives like `dr-managed` may not allow deletion
- **Immediate Effect**: The rule stops executing immediately upon deletion
- **Re-creation**: You can create a new rule with the same name after deletion
- **Name Sensitivity**: Rule names are case-sensitive - use exact name
- **Audit Trail**: The deletion is logged in organization audit logs
- **Alternative**: To temporarily disable, use set-rule with `enabled: false` instead
- **Related Operations**:
  - To temporarily disable: use set-rule with enabled: false
  - To view before deleting: use get-rule
  - To verify deletion: use list-rules

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go` (Remove method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/hive/generic_hive.go`
